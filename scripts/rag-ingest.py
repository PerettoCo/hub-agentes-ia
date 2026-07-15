#!/usr/bin/env python3
"""
rag-ingest.py — Pipeline robusto de ingestao RAG

Extrai texto de qualquer arquivo, chunkifica com overlap,
gera embeddings e armazena no Supabase (pgvector).

Uso:
  python scripts/rag-ingest.py documento.pdf
  python scripts/rag-ingest.py documento.pdf --chunk-size 1500 --overlap 200 --type fact --importance 4
  python scripts/rag-ingest.py diretorio/          # ingere todos os arquivos
  python scripts/rag-ingest.py documento.pdf --dry-run  # so mostra o que faria

Dependencias:
  pip install -r scripts/requirements.txt
"""
import os, sys, json, hashlib, uuid, argparse, logging, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("rag-ingest")

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "text-embedding-3-small"

# ============================================================
# Config
# ============================================================

def load_env():
    for p in [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]:
        env_file = p / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            break

load_env()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
EMBEDDING_API_KEY = os.environ.get(
    "EMBEDDING_API_KEY",
    os.environ.get("OPENAI_API_KEY", ""),
)
EMBEDDING_BASE_URL = os.environ.get(
    "EMBEDDING_BASE_URL",
    "https://api.openai.com/v1",
).rstrip("/")

# ============================================================
# Utils
# ============================================================

def compute_checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """Divide texto em chunks com overlap."""
    if not text.strip():
        return []
    chunks = []
    start = 0
    text_len = len(text)
    idx = 0
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk_text_content = text[start:end]
        chunks.append({
            "index": idx,
            "start_char": start,
            "end_char": end,
            "text": chunk_text_content,
            "size_chars": len(chunk_text_content),
        })
        idx += 1
        if end >= text_len:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def generate_embedding(text: str) -> list[float]:
    import httpx
    if not text.strip():
        return [0.0] * 1536
    url = f"{EMBEDDING_BASE_URL}/embeddings"
    for attempt in range(3):
        try:
            resp = httpx.post(
                url,
                headers={
                    "Authorization": f"Bearer {EMBEDDING_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={"model": EMBEDDING_MODEL, "input": text},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            log.warning("Embedding attempt %d/3: %s", attempt + 1, e)
            if attempt == 2:
                raise
    return [0.0] * 1536

def extract_text(filepath: str, max_chars: int = 100000) -> dict:
    """Usa file-reader.py para extrair texto."""
    result = subprocess.run(
        ["python3", "scripts/file-reader.py", filepath, str(max_chars)],
        capture_output=True, text=True, timeout=60,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": f"file-reader falhou: {result.stderr[:500]}", "text": ""}

# ============================================================
# Supabase
# ============================================================

def supabase_insert(data: dict):
    import httpx
    url = f"{SUPABASE_URL}/rest/v1/agent_memories"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    resp = httpx.post(url, headers=headers, json=data, timeout=10)
    resp.raise_for_status()

def check_duplicate(checksum: str, agent_id: str) -> bool:
    import httpx
    url = f"{SUPABASE_URL}/rest/v1/agent_memories?checksum=eq.{checksum}&agent_id=eq.{agent_id}&select=id"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    resp = httpx.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return len(data) > 0

# ============================================================
# Ingestao
# ============================================================

def ingest_file(
    filepath: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    memory_type: str = "fact",
    importance: int = 3,
    agent_id: str = "opencode",
    session_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    dry_run: bool = False,
):
    path = Path(filepath)
    if not path.exists():
        log.error("Arquivo nao encontrado: %s", filepath)
        return False

    log.info("Extraindo texto: %s", path.name)
    doc = extract_text(str(path))

    if doc.get("error"):
        log.error("Erro ao extrair: %s", doc["error"])
        return False

    text = doc.get("text", "")
    if not text.strip():
        log.warning("Texto vazio: %s", path.name)
        return False

    # Chunkificar
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    log.info("Documento: %s — %d chars em %d chunks", path.name, doc["size_chars"], len(chunks))

    if not chunks:
        log.warning("Nenhum chunk gerado para: %s", path.name)
        return False

    meta = metadata or {}
    meta["source_file"] = path.name
    meta["source_path"] = str(path.absolute())
    meta["source_ext"] = path.suffix.lower()

    if dry_run:
        log.info("DRY RUN — Pulando armazenamento.")
        print(json.dumps({
            "file": path.name,
            "total_chars": doc["size_chars"],
            "chunks": len(chunks),
            "first_chunk": chunks[0]["text"][:200] if chunks else "",
        }, ensure_ascii=False, indent=2))
        return True

    # Armazenar cada chunk
    success_count = 0
    skip_count = 0
    try:
        from tqdm import tqdm
        iterator = tqdm(chunks, desc=f"Ingerindo {path.name}")
    except ImportError:
        iterator = chunks

    for chunk in iterator:
        chunk_text_content = chunk["text"]
        if not chunk_text_content.strip():
            continue

        checksum = compute_checksum(chunk_text_content)

        # Dedup
        try:
            if check_duplicate(checksum, agent_id):
                skip_count += 1
                continue
        except Exception as e:
            log.debug("Dedup check falhou (continua mesmo assim): %s", e)

        # Embedding
        try:
            embedding = generate_embedding(chunk_text_content)
        except Exception as e:
            log.error("Embedding falhou no chunk %d: %s", chunk["index"], e)
            continue

        # Inserir
        record = {
            "content": chunk_text_content,
            "content_tokens": len(chunk_text_content.split()),
            "embedding": embedding,
            "agent_id": agent_id,
            "session_id": session_id,
            "memory_type": memory_type,
            "importance": importance,
            "metadata": meta,
            "checksum": checksum,
        }

        try:
            supabase_insert(record)
            success_count += 1
        except Exception as e:
            log.error("Falha ao inserir chunk %d: %s", chunk["index"], e)

    log.info(
        "Concluido: %s — %d inseridos, %d ignorados (dedup), %d chunks",
        path.name, success_count, skip_count, len(chunks),
    )
    return success_count > 0


def ingest_directory(
    directory: str,
    recursive: bool = True,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    memory_type: str = "fact",
    importance: int = 3,
    agent_id: str = "opencode",
    dry_run: bool = False,
    max_files: int = 50,
):
    path = Path(directory)
    if not path.is_dir():
        log.error("Diretorio nao encontrado: %s", directory)
        return

    SUPPORTED_EXTS = {
        ".pdf", ".docx", ".doc", ".pptx", ".xlsx", ".xls",
        ".odt", ".ods", ".odp", ".rtf",
        ".csv", ".html", ".htm",
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp",
        ".md", ".txt", ".json", ".xml", ".yaml", ".yml", ".log",
        ".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".svelte",
        ".sh", ".bash", ".css", ".scss", ".rb", ".go", ".rs", ".java",
        ".cpp", ".c", ".h", ".swift", ".kt", ".php", ".lua",
    }

    files = []
    if recursive:
        for f in path.rglob("*"):
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS:
                files.append(f)
    else:
        for f in path.iterdir():
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS:
                files.append(f)

    files.sort()
    if len(files) > max_files:
        log.warning("Limitando a %d arquivos (encontrados %d)", max_files, len(files))
        files = files[:max_files]

    log.info("Encontrados %d arquivos para ingestao em: %s", len(files), directory)

    total_ok = 0
    total_fail = 0
    for f in files:
        try:
            ok = ingest_file(
                str(f),
                chunk_size=chunk_size,
                overlap=overlap,
                memory_type=memory_type,
                importance=importance,
                agent_id=agent_id,
                dry_run=dry_run,
            )
            if ok:
                total_ok += 1
            else:
                total_fail += 1
        except Exception as e:
            log.error("Erro ao ingerir %s: %s", f.name, e)
            total_fail += 1

    log.info("=== Resumo: %d ok, %d falha (total %d arquivos) ===", total_ok, total_fail, len(files))


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="RAG Ingest — Pipeline robusto de ingestao de documentos no pgvector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("path", help="Arquivo ou diretorio para ingerir")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE, help="Tamanho do chunk em chars")
    parser.add_argument("--overlap", type=int, default=CHUNK_OVERLAP, help="Overlap entre chunks")
    parser.add_argument("--type", default="fact", help="Tipo de memoria (fact, decision, learned, etc)")
    parser.add_argument("--importance", type=int, default=3, help="Importancia 1-5")
    parser.add_argument("--agent-id", default="opencode", help="Agent ID")
    parser.add_argument("--session-id", default=None, help="Session ID")
    parser.add_argument("--dry-run", action="store_true", help="So mostrar o que faria")
    parser.add_argument("--no-recursive", action="store_true", help="Nao recursivo (so arquivos na raiz)")

    args = parser.parse_args()

    # Validar env
    missing = []
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_KEY:
        missing.append("SUPABASE_SERVICE_KEY")
    if not EMBEDDING_API_KEY:
        missing.append("EMBEDDING_API_KEY ou OPENAI_API_KEY")
    if missing:
        log.error("Variaveis obrigatorias faltando: %s", ", ".join(missing))
        log.error("Crie um .env ou exporte as variaveis.")
        sys.exit(1)

    path = Path(args.path)
    if path.is_dir():
        ingest_directory(
            args.path,
            recursive=not args.no_recursive,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            memory_type=args.type,
            importance=args.importance,
            agent_id=args.agent_id,
            dry_run=args.dry_run,
        )
    else:
        ingest_file(
            args.path,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            memory_type=args.type,
            importance=args.importance,
            agent_id=args.agent_id,
            session_id=args.session_id,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
