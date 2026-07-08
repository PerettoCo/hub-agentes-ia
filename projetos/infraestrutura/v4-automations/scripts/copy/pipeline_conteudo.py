"""
pipeline_conteudo.py — Pipeline de conteúdo editorial com aprovação e Google Drive.

Gerencia o ciclo completo:
1. Criação de calendário editorial
2. Produção de blog posts + email marketing (via Claude)
3. Envio para aprovação (pasta no Drive)
4. Geração de JSONs finais + push para Drive

Uso:
  python3 pipeline_conteudo.py --calendario --cliente "Cliente A"
  python3 pipeline_conteudo.py --semana 2026-W22 --cliente "Cliente A"
"""
import sys
import os
import json
import argparse
from pathlib import Path
from datetime import date, timedelta, datetime
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.connectors import (
    DriveConnector, GmailConnector, claude
)

SYSTEM_CALENDARIO = """
Voce e o editor-chefe de conteudo V4. Seu papel: criar calendarios editoriais
estruturados para clientes, definindo topicos, formatos, deadlines e estado de
aprovacao.

Formato de output: JSON array com objetos.
Cada objeto tem: titulo, formato (blog_post|email_marketing|social|lead_magnet),
semana, dia_semana, keyword_principal, objetivo, status (rascunho|aprovado|publicado).
"""

SYSTEM_BLOG = """
Voce e um copywriter senior V4 especialista em blog posts e email marketing.
Escreva conteudo persuasivo, bem estruturado e otimizado para conversao.

Blog post: titulo, introducao, subtitulos (h2/h3), corpo, CTA, meta description.
Email marketing: subject line, preheader, corpo, CTA button, PS.
Tudo em portugues brasileiro do cliente.
"""


def gerar_calendario(cliente: str, semanas: int = 4) -> list[dict]:
    """Gera calendário editorial via Claude."""
    user_prompt = f"""
    Crie um calendario editorial de {semanas} semanas para o cliente "{cliente}".
    Inclua uma mistura de blog posts e email marketing.
    Para cada item: titulo, formato, semana, dia_semana, keyword_principal,
    objetivo (ex: Topo de Funil, Nutricao, Conversao), status: "rascunho".

    Retorne APENAS o JSON array, sem markdown.
    """
    result = claude(SYSTEM_CALENDARIO, user_prompt, max_tokens=2000)
    result = result.strip()
    if result.startswith("```"):
        result = result.split("\n", 1)[1]
    if result.endswith("```"):
        result = result.rsplit("\n", 1)[0]
    result = result.strip()
    return json.loads(result)


def gerar_blog_post(item: dict, cliente: str) -> dict:
    """Gera blog post completo via Claude."""
    user_prompt = f"""
    Escreva um blog post completo para o cliente "{cliente}".

    Titulo: {item['titulo']}
    Keyword principal: {item.get('keyword_principal', '')}
    Objetivo: {item.get('objetivo', '')}

    Inclua:
    - Meta description (ate 160 chars)
    - Introducao (2-3 paragrafos)
    3-4 subtitulos H2 com conteudo
    - Conclusao com CTA
    - Estimativa de leitura (minutos)

    Retorne APENAS JSON com: titulo, meta_description, introducao, secoes (array
    de {subtitulo, conteudo}), conclusao, cta, tempo_leitura, formato: "blog_post",
    status: "para_aprovacao".
    """
    result = claude(SYSTEM_BLOG, user_prompt, max_tokens=3000)
    result = result.strip()
    if result.startswith("```"):
        result = result.split("\n", 1)[1]
    if result.endswith("```"):
        result = result.rsplit("\n", 1)[0]
    return json.loads(result.strip())


def gerar_email_marketing(item: dict, cliente: str) -> dict:
    """Gera email marketing via Claude."""
    user_prompt = f"""
    Escreva um email marketing completo para o cliente "{cliente}".

    Titulo: {item['titulo']}
    Keyword principal: {item.get('keyword_principal', '')}
    Objetivo: {item.get('objetivo', '')}

    Inclua:
    - Subject line (3 opcoes)
    - Preheader text
    - Corpo do email (2-3 paragrafos)
    - CTA button (texto + hint de destino)
    - PS line

    Retorne APENAS JSON com: titulo, subject_lines (array), preheader, corpo,
    cta {texto, hint}, ps, formato: "email_marketing", status: "para_aprovacao".
    """
    result = claude(SYSTEM_BLOG, user_prompt, max_tokens=2500)
    result = result.strip()
    if result.startswith("```"):
        result = result.split("\n", 1)[1]
    if result.endswith("```"):
        result = result.rsplit("\n", 1)[0]
    return json.loads(result.strip())


def salvar_json_drive(
    drive: DriveConnector,
    conteudo: dict,
    cliente: str,
    pasta_raiz_id: str | None,
) -> str:
    """Salva JSON de conteúdo no Google Drive."""
    pasta_cliente = drive.ensure_folder(
        ["Conteudo V4", cliente, date.today().strftime("%Y-%m")],
        root_id=pasta_raiz_id,
    )
    filename = f"{conteudo['formato']}-{conteudo['titulo'][:40]}-{date.today().isoformat()}.json"
    filename = filename.replace(" ", "-").lower()
    file_id = drive.upload_json(conteudo, filename, parent_id=pasta_cliente)
    return file_id


def salvar_calendario_drive(
    drive: DriveConnector,
    calendario: list[dict],
    cliente: str,
    pasta_raiz_id: str | None,
) -> str:
    """Salva calendário no Drive."""
    pasta = drive.ensure_folder(
        ["Conteudo V4", cliente, "Calendarios"],
        root_id=pasta_raiz_id,
    )
    filename = f"calendario-editorial-{cliente}-{date.today().isoformat()}.json"
    filename = filename.replace(" ", "-").lower()
    data = {
        "cliente": cliente,
        "gerado_em": date.today().isoformat(),
        "semanas": calendario,
    }
    return drive.upload_json(data, filename, parent_id=pasta)


def aprovar_item(item_path: str, drive: DriveConnector) -> bool:
    """Marca item como aprovado (lê JSON, muda status, re-salva)."""
    import tempfile
    import shutil
    # Baixar JSON do Drive
    request = drive.service.files().export_media(
        fileId=item_path, mimeType="application/json"
    )
    content = request.execute().decode("utf-8")
    data = json.loads(content)
    if data.get("status") == "para_aprovacao":
        data["status"] = "aprovado"
        data["aprovado_em"] = date.today().isoformat()
        drive.service.files().update(
            fileId=item_path,
            media_body=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
        ).execute()
        return True
    return False


def main():
    p = argparse.ArgumentParser(description="Pipeline de Conteudo Editorial")
    p.add_argument("--calendario", action="store_true", help="Gerar calendario editorial")
    p.add_argument("--semana", help="Semana especifica (ex: 2026-W22)")
    p.add_argument("--cliente", required=True, help="Nome do cliente")
    p.add_argument("--semanas", type=int, default=4, help="Quantas semanas de calendario")
    p.add_argument("--drive", action="store_true", help="Salvar no Google Drive")
    p.add_argument("--drive-folder", help="ID da pasta raiz no Drive", default=None)
    p.add_argument("--email", help="Notificar por email", default=None)
    p.add_argument("--aprovar", help="ID do arquivo no Drive para aprovar")
    p.add_argument("--produzir", help="Produzir item especifico do calendario (indice)")
    args = p.parse_args()

    drive = DriveConnector() if (args.drive or args.aprovar) else None

    # Aprovação
    if args.aprovar and drive:
        if aprovar_item(args.aprovar, drive):
            print(f"Item {args.aprovar} aprovado com sucesso.")
        else:
            print(f"Item {args.aprovar} ja esta aprovado ou nao encontrado.")
        return

    # Calendário
    if args.calendario:
        print(f"Gerando calendario editorial para {args.cliente} ({args.semanas} semanas)...")
        calendario = gerar_calendario(args.cliente, semanas=args.semanas)
        print(f"Calendario gerado: {len(calendario)} itens")

        output = {"cliente": args.cliente, "data": date.today().isoformat(), "itens": calendario}
        print(json.dumps(output, ensure_ascii=False, indent=2))

        if drive:
            file_id = salvar_calendario_drive(drive, calendario, args.cliente, args.drive_folder)
            print(f"Calendario salvo no Drive (fileId: {file_id})")

        if args.email:
            gmail = GmailConnector()
            body = f"<h2>Calendário Editorial — {args.cliente}</h2><pre>{json.dumps(output, ensure_ascii=False, indent=2)}</pre>"
            gmail.send(to=args.email, subject=f"Calendário Editorial {args.cliente}", body_html=body)
            print(f"Calendário enviado para {args.email}")

        # Perguntar se quer produzir
        print(f"\nPara produzir um item: python3 pipeline_conteudo.py --cliente '{args.cliente}' --produzir <indice>")

    # Produção de item específico
    if args.produzir is not None:
        idx = int(args.produzir)
        if args.calendario:
            # Se gerou calendário agora, usa ele
            if not calendario:
                print("Erro: gere o calendario primeiro com --calendario")
                return
            if idx >= len(calendario):
                print(f"Indice {idx} fora do range (0-{len(calendario)-1})")
                return
            item = calendario[idx]
        else:
            print("Use --calendario primeiro para gerar o calendario, depois --produzir")
            return

        print(f"Produzindo: {item['titulo']} ({item['formato']})...")

        if item["formato"] == "blog_post":
            conteudo = gerar_blog_post(item, args.cliente)
        elif item["formato"] == "email_marketing":
            conteudo = gerar_email_marketing(item, args.cliente)
        else:
            print(f"Formato nao suportado: {item['formato']}")
            return

        print(json.dumps(conteudo, ensure_ascii=False, indent=2))

        # Salvar no Drive
        if drive:
            file_id = salvar_json_drive(drive, conteudo, args.cliente, args.drive_folder)
            print(f"Conteudo salvo no Drive (fileId: {file_id}) — status: para_aprovacao")

        # Notificar
        if args.email:
            gmail = GmailConnector()
            preview = json.dumps(conteudo, ensure_ascii=False, indent=2)
            body = f"""
            <h2>Novo Conteudo para Aprovacao — {args.cliente}</h2>
            <p><strong>{conteudo['titulo']}</strong> ({conteudo['formato']})</p>
            <p><strong>Status:</strong> Para Aprovacao</p>
            <p><strong>Link Drive:</strong> https://drive.google.com/file/d/{file_id}</p>
            <hr>
            <pre style="font-size:12px;">{preview[:2000]}...</pre>
            """
            gmail.send(
                to=args.email,
                subject=f"[Aprovacao] {conteudo['titulo']} — {args.cliente}",
                body_html=body,
            )
            print(f"Notificacao de aprovacao enviada para {args.email}")


if __name__ == "__main__":
    main()
