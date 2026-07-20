/**
 * attachment-reader — faz o anexo NATIVO do chat funcionar com modelos de texto.
 *
 * Quando o usuário anexa um arquivo (PDF, DOCX, XLSX, imagem, etc.) direto no
 * chat (clipe nativo do OpenCode):
 *   1. Salva o arquivo em /workspace/input/ (persistente, aparece no dashboard).
 *   2. Extrai o conteúdo em texto via scripts/file-reader.py
 *      (PDF->pdftotext, DOCX/XLSX, imagem->modelo de visão gratuito, OCR, etc.).
 *   3. Injeta o texto extraído na conversa para o modelo de texto "ler" o arquivo.
 *   4. Remove o file part do payload enviado ao LLM (modelos de texto não os
 *      leem e chegam a dar erro) — o conteúdo já vai como texto.
 *
 * Estratégia robusta em 2 hooks:
 *   - chat.message: salva + extrai (uma vez por anexo) e guarda em cache por
 *     part.id; também injeta um text part sintético (histórico/exibição).
 *   - experimental.chat.messages.transform: no payload final para o LLM, troca
 *     cada file part pelo texto extraído (do cache). É a fonte de verdade do que
 *     o modelo recebe, então garante a leitura mesmo se o push acima não persistir.
 */
import fs from "fs";
import path from "path";

const INPUT_DIR = "/workspace/input";
const READER = "/workspace/scripts/file-reader.py";
const MAX_BYTES = 25 * 1024 * 1024; // 25MB por anexo

// Cache por part.id -> texto extraído (vive enquanto o servidor roda).
const extractedCache = new Map();

function sanitize(name) {
  return (name || "anexo").replace(/[^\w.\- ]/g, "_").slice(0, 120);
}

async function bytesFromUrl(url, serverUrl) {
  if (!url) return null;
  if (url.startsWith("data:")) {
    const comma = url.indexOf(",");
    if (comma === -1) return null;
    const meta = url.slice(5, comma);
    const data = url.slice(comma + 1);
    if (/;base64/i.test(meta)) return Buffer.from(data, "base64");
    return Buffer.from(decodeURIComponent(data), "utf8");
  }
  let full = url;
  if (url.startsWith("/")) {
    try { full = new URL(url, serverUrl).toString(); } catch { /* noop */ }
  }
  const res = await fetch(full);
  if (!res.ok) throw new Error("fetch " + res.status);
  return Buffer.from(await res.arrayBuffer());
}

export const AttachmentReader = async ({ $, serverUrl, client }) => {
  const log = async (level, message, extra) => {
    try {
      await client.app.log({ body: { service: "attachment-reader", level, message, extra } });
    } catch { /* noop */ }
  };

  // Salva o arquivo e extrai o texto (uma única vez por part.id).
  async function processFilePart(part) {
    if (extractedCache.has(part.id)) return extractedCache.get(part.id);
    const fname = sanitize(part.filename);
    let block;
    try {
      const buf = await bytesFromUrl(part.url, serverUrl);
      if (!buf) {
        block = `[Anexo "${fname}": não foi possível obter o conteúdo.]`;
      } else if (buf.length > MAX_BYTES) {
        block = `[Anexo "${fname}" ignorado: maior que 25MB.]`;
      } else {
        fs.mkdirSync(INPUT_DIR, { recursive: true });
        const dest = path.join(INPUT_DIR, `${Date.now()}-${fname}`);
        fs.writeFileSync(dest, buf);

        const res = await $`python3 ${READER} ${dest}`.quiet().nothrow();
        let text = "";
        try {
          const j = JSON.parse(res.stdout.toString());
          text = j && j.text ? j.text : "";
        } catch {
          text = res.stdout ? res.stdout.toString() : "";
        }

        if (text && text.trim()) {
          block = `[Conteúdo do arquivo anexado "${fname}" — salvo em /workspace/input/]\n${text.trim()}`;
          await log("info", "anexo lido", { fname, chars: text.length });
        } else {
          block = `[Anexo "${fname}" salvo em /workspace/input/, mas não foi possível extrair texto.]`;
          await log("warn", "anexo sem texto", { fname });
        }
      }
    } catch (e) {
      block = `[Falha ao ler o anexo "${fname}": ${String(e).slice(0, 200)}]`;
      await log("error", "falha no anexo", { fname, error: String(e) });
    }
    extractedCache.set(part.id, block);
    return block;
  }

  function textPartFrom(ref, text) {
    return {
      id: "prt_att_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8),
      sessionID: ref.sessionID,
      messageID: ref.messageID,
      type: "text",
      text,
      synthetic: true,
      metadata: { attachmentReader: true },
    };
  }

  return {
    // Dispara quando a mensagem do usuário chega — salva + extrai + injeta texto.
    "chat.message": async (_input, output) => {
      const parts = output.parts || [];
      const fileParts = parts.filter((p) => p && p.type === "file");
      if (!fileParts.length) return;

      const ref = parts.find((p) => p.type === "text") || parts[0] || {};
      const blocks = [];
      for (const part of fileParts) {
        const block = await processFilePart(part);
        if (block) blocks.push(block);
      }
      if (blocks.length) {
        output.parts.push(textPartFrom(ref, "\n\n" + blocks.join("\n\n")));
      }
    },

    // Payload final para o LLM: troca cada file part pelo texto extraído.
    // Fonte de verdade — garante que o modelo de texto receba o conteúdo e
    // nunca receba um file part cru.
    "experimental.chat.messages.transform": async (_input, output) => {
      for (const m of output.messages || []) {
        if (!m.parts || !m.parts.some((p) => p.type === "file")) continue;
        // Se chat.message já injetou o texto do anexo nesta mensagem, apenas
        // removemos os file parts (evita duplicar o conteúdo).
        const alreadyInjected = m.parts.some((p) => p.metadata && p.metadata.attachmentReader);
        const rebuilt = [];
        for (const p of m.parts) {
          if (p.type !== "file") { rebuilt.push(p); continue; }
          if (alreadyInjected) continue; // texto já presente; só descarta o file
          const block = extractedCache.has(p.id)
            ? extractedCache.get(p.id)
            : await processFilePart(p);
          if (block) rebuilt.push(textPartFrom(p, block));
          // file part é descartado (não vai para o LLM de texto)
        }
        m.parts = rebuilt;
      }
    },
  };
};
