#!/usr/bin/env python3
"""
memory-cli.py — CLI de Memoria por Similaridade com pgvector + Supabase

Uso:
  python memory-cli.py store          "texto"              --type fact --importance 4
  python memory-cli.py search         "query semantica"    --limit 5 --threshold 0.7
  python memory-cli.py delete         <uuid>
  python memory-cli.py list                                  --type decision
  python memory-cli.py consolidate                           --dry-run
  python memory-cli.py export         output.json           --format json
  python memory-cli.py import         input.json
  python memory-cli.py inject-context "contexto da sessao"  --session-id abc-123
  python memory-cli.py stats
  python memory-cli.py cleanup
  python memory-cli.py migrate-sql                           --print-only

Dependencias:
  pip install openai httpx python-dotenv typer rich

Variaveis de ambiente:
  SUPABASE_URL, SUPABASE_SERVICE_KEY, OPENAI_API_KEY
"""

import os, sys, json, hashlib, uuid, logging, argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("memory-cli")

# ============================================================
# Tipos
# ============================================================

MEMORY_TYPES = ("fact", "decision", "learned", "context", "preference", "general", "session_summary")
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536


@dataclass
class Memory:
    id: str = ""
    content: str = ""
    content_tokens: int = 0
    agent_id: str = "opencode"
    session_id: Optional[str] = None
    parent_session: Optional[str] = None
    memory_type: str = "general"
    importance: int = 1
    ttl: Optional[str] = None
    consolidated: bool = False
    consolidated_from: Optional[list] = None
    access_count: int = 0
    last_accessed: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    checksum: str = ""
    created_at: str = ""
    updated_at: str = ""

    @property
    def embedding_text(self) -> str:
        return f"{self.memory_type}: {self.content[:100]}..."

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_row(cls, row: dict) -> "Memory":
        return cls(
            id=row.get("id", ""),
            content=row.get("content", ""),
            content_tokens=row.get("content_tokens", 0),
            agent_id=row.get("agent_id", "opencode"),
            session_id=row.get("session_id"),
            parent_session=row.get("parent_session"),
            memory_type=row.get("memory_type", "general"),
            importance=row.get("importance", 1),
            ttl=row.get("ttl"),
            consolidated=row.get("consolidated", False),
            consolidated_from=row.get("consolidated_from"),
            access_count=row.get("access_count", 0),
            last_accessed=row.get("last_accessed"),
            metadata=row.get("metadata", {}),
            checksum=row.get("checksum", ""),
            created_at=row.get("created_at", ""),
            updated_at=row.get("updated_at", ""),
        )


# ============================================================
# Config
# ============================================================

def load_env():
    """Carrega .env do diretorio corrente ou pai."""
    for p in [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]:
        env_file = p / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
            break


class Config:
    def __init__(self):
        load_env()
        self.supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        self.supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")
        self.embedding_base_url = os.environ.get(
            "EMBEDDING_BASE_URL",
            "https://api.openai.com/v1",
        ).rstrip("/")
        self.embedding_model = os.environ.get(
            "EMBEDDING_MODEL",
            "text-embedding-3-small",
        )
        self.embedding_api_key = os.environ.get(
            "EMBEDDING_API_KEY",
            os.environ.get("OPENAI_API_KEY", ""),
        )
        self.embedding_dims = int(os.environ.get("EMBEDDING_DIMS", "1536"))
        self.agent_id = os.environ.get("MEMORY_AGENT_ID", "opencode")
        self.default_threshold = float(os.environ.get("MEMORY_THRESHOLD", "0.7"))
        self.default_limit = int(os.environ.get("MEMORY_LIMIT", "5"))

    def validate(self):
        missing = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_key:
            missing.append("SUPABASE_SERVICE_KEY")
        if not self.embedding_api_key:
            missing.append("EMBEDDING_API_KEY ou OPENAI_API_KEY")
        if missing:
            log.error(
                "Variaveis obrigatorias faltando: %s\n"
                "Crie um .env ou exporte as variaveis.",
                ", ".join(missing),
            )
            sys.exit(1)

    @property
    def supabase_headers(self) -> dict:
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
        }


# ============================================================
# Embedding
# ============================================================

def compute_checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_embedding(text: str, config: Config) -> list[float]:
    """Gera embedding via LiteLLM ou OpenAI (compatível com API OpenAI)."""
    import httpx

    if not text.strip():
        log.warning("Texto vazio, retornando embedding zero")
        return [0.0] * EMBEDDING_DIMS

    url = f"{config.embedding_base_url}/embeddings"
    for attempt in range(3):
        try:
            resp = httpx.post(
                url,
                headers={
                    "Authorization": f"Bearer {config.embedding_api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": config.embedding_model, "input": text},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]
        except httpx.HTTPStatusError as e:
            log.warning("Embedding attempt %d/3 failed: %s", attempt + 1, e)
            if attempt == 2:
                log.error("Embedding esgotou tentativas para: %.80s", text)
                raise
        except httpx.TimeoutException:
            log.warning("Embedding timeout attempt %d/3", attempt + 1)
            if attempt == 2:
                raise
    return [0.0] * EMBEDDING_DIMS  # never reached


# ============================================================
# Supabase Client
# ============================================================

class SupabaseClient:
    """Cliente HTTP para Supabase REST + RPC com retry e backoff."""

    def __init__(self, config: Config):
        self.config = config
        self.base = config.supabase_url
        self.headers = config.supabase_headers

    def _request(self, method: str, path: str, **kwargs):
        import httpx
        import time

        url = f"{self.base}{path}"
        last_error = None
        for attempt in range(3):
            try:
                resp = httpx.request(
                    method, url, headers=self.headers,
                    timeout=30, **kwargs,
                )
                resp.raise_for_status()
                if resp.status_code == 204:
                    return None
                return resp.json()
            except httpx.HTTPStatusError as e:
                last_error = e
                log.warning("Supabase %s %s attempt %d/3: %s", method, path, attempt + 1, e)
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    log.error("Supabase request failed: %s", e)
                    raise
            except httpx.TimeoutException as e:
                last_error = e
                log.warning("Supabase timeout %s %s attempt %d/3", method, path, attempt + 1)
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    raise
        raise last_error or RuntimeError("Supabase request failed")

    def get(self, path: str, params: dict = None):
        return self._request("GET", path, params=params)

    def post(self, path: str, json: dict = None):
        return self._request("POST", path, json=json)

    def rpc(self, fn: str, params: dict = None):
        return self._request("POST", f"/rest/v1/rpc/{fn}", json=params or {})

    def insert(self, table: str, data: dict):
        return self._request(
            "POST", f"/rest/v1/{table}",
            json=data,
            headers={**self.headers, "Prefer": "return=minimal"},
        )

    def delete(self, table: str, query: str):
        return self._request("DELETE", f"/rest/v1/{table}?{query}")


# ============================================================
# Comandos
# ============================================================

def cmd_store(config: Config, content: str, memory_type: str = "general",
              importance: int = 1, session_id: str = None, metadata: str = None,
              ttl_days: int = None, agent_id: str = None):
    """Armazena uma memoria."""
    agent_id = agent_id or config.agent_id
    checksum = compute_checksum(content)
    meta = json.loads(metadata) if metadata else {}
    tokens = len(content.split())

    log.info("Gerando embedding...")
    embedding = generate_embedding(content, config)

    client = SupabaseClient(config)

    # Verificar checksum (dedup)
    existing = client.get(
        "/rest/v1/agent_memories",
        params={"checksum": f"eq.{checksum}", "agent_id": f"eq.{agent_id}", "select": "id"},
    )
    if existing and len(existing) > 0:
        log.info("Dedup: memoria identica ja existe (id=%s)", existing[0]["id"])
        return existing[0]["id"]

    ttl = None
    if ttl_days:
        ttl = (datetime.now(timezone.utc) + timedelta(days=ttl_days)).isoformat()

    record = {
        "content": content,
        "content_tokens": tokens,
        "embedding": embedding,
        "agent_id": agent_id,
        "session_id": session_id,
        "memory_type": memory_type,
        "importance": importance,
        "metadata": meta,
        "checksum": checksum,
    }
    if ttl:
        record["ttl"] = ttl

    log.info("Inserindo no Supabase...")
    client.insert("agent_memories", record)
    log.info("Memoria armazenada: type=%s importance=%d tokens=%d", memory_type, importance, tokens)
    return None


def cmd_search(config: Config, query: str, limit: int = 5, threshold: float = 0.7,
               memory_type: str = None, session_id: str = None, agent_id: str = None,
               fts: bool = False, json_output: bool = False):
    """Busca memorias por similaridade semantica."""
    agent_id = agent_id or config.agent_id

    client = SupabaseClient(config)
    results = []

    if fts:
        log.info("Full-text search: %s", query)
        params = {
            "p_query": query,
            "p_match_count": limit,
            "p_agent_id": agent_id,
        }
        if memory_type:
            params["p_memory_type"] = memory_type
        results = client.rpc("search_memories_fts", params)
    else:
        log.info("Gerando embedding para query...")
        embedding = generate_embedding(query, config)

        params = {
            "query_embedding": embedding,
            "match_threshold": threshold,
            "match_count": limit,
            "p_agent_id": agent_id,
        }
        if memory_type:
            params["p_memory_type"] = memory_type
        if session_id:
            params["p_session_id"] = session_id

        results = client.rpc("match_agent_memories", params)

        # Atualizar access_count
        for r in results:
            try:
                client.rpc("update_access_count", {"p_id": r["id"]})
            except Exception:
                pass

    if json_output:
        print(json.dumps(results, indent=2, default=str))
        return results

    if not results:
        log.info("Nenhuma memoria encontrada.")
        return results

    print(f"\n{'='*60}")
    print(f"  {len(results)} memorias encontradas (threshold={threshold})")
    print(f"{'='*60}\n")
    for i, r in enumerate(results, 1):
        sim = r.get("similarity", 0)
        impr = r.get("importance", 1)
        mtype = r.get("memory_type", "?")
        created = r.get("created_at", "")[:10]
        tid = r.get("id", "")[:8]
        content = r.get("content", "")
        print(f"  [{i}] sim={sim:.3f} imp={impr} type={mtype} date={created} id={tid}")
        print(f"       {content[:200]}")
        print()
    return results


def cmd_delete(config: Config, memory_id: str):
    """Deleta uma memoria pelo ID."""
    client = SupabaseClient(config)
    client.delete("agent_memories", f"id=eq.{memory_id}")
    log.info("Memoria %s deletada.", memory_id)


def cmd_list(config: Config, memory_type: str = None, agent_id: str = None,
             limit: int = 20, json_output: bool = False):
    """Lista memorias recentes."""
    agent_id = agent_id or config.agent_id

    filters = [f"agent_id=eq.{agent_id}", f"order=created_at.desc", f"limit={limit}"]
    if memory_type:
        filters.append(f"memory_type=eq.{memory_type}")

    client = SupabaseClient(config)
    results = client.get(f"/rest/v1/agent_memories?{'&'.join(filters)}")

    if not results:
        log.info("Nenhuma memoria encontrada.")
        return

    mems = [Memory.from_row(r) for r in results]

    if json_output:
        print(json.dumps([m.to_dict() for m in mems], indent=2, default=str))
        return

    print(f"\n{'='*80}")
    print(f"  Memorias recentes (agent={agent_id}, type={memory_type or 'todos'})")
    print(f"{'='*80}\n")
    for m in mems:
        print(f"  [{m.id[:8]}] {m.memory_type:15s} imp={m.importance} "
              f"{m.created_at[:10]} access={m.access_count}")
        print(f"       {m.content[:120]}")
        print()


def cmd_consolidate(config: Config, dry_run: bool = False, threshold: float = 0.85,
                    agent_id: str = None):
    """Consolida memorias similares (funde as parecidas)."""
    agent_id = agent_id or config.agent_id
    client = SupabaseClient(config)

    if dry_run:
        log.info("DRY RUN: estimando consolidacao...")
        results = client.rpc("consolidate_similar_memories", {
            "p_agent_id": agent_id,
            "p_similarity_threshold": threshold,
            "p_max_age_days": 30,
        })
        for r in results:
            log.info("  Consolidaria %d memorias em %s", r.get("source_count", 0), r.get("consolidated_id"))
        log.info("Dry run: %d consolidacoes possiveis.", len(results))
        return results
    else:
        log.info("Consolidando memorias...")
        results = client.rpc("consolidate_similar_memories", {
            "p_agent_id": agent_id,
            "p_similarity_threshold": threshold,
            "p_max_age_days": 30,
        })
        log.info("Consolidacao concluida: %d grupos fundidos.", len(results))
        return results


def cmd_export(config: Config, output_path: str, agent_id: str = None):
    """Exporta todas as memorias para JSON."""
    agent_id = agent_id or config.agent_id
    client = SupabaseClient(config)

    results = client.get(
        f"/rest/v1/agent_memories?agent_id=eq.{agent_id}&order=created_at.desc"
    )
    mems = [Memory.from_row(r).to_dict() for r in results]

    Path(output_path).write_text(json.dumps(mems, indent=2, default=str))
    log.info("Exportadas %d memorias para %s", len(mems), output_path)


def cmd_import(config: Config, input_path: str, agent_id: str = None):
    """Importa memorias de um JSON."""
    agent_id = agent_id or config.agent_id
    data = json.loads(Path(input_path).read_text())
    client = SupabaseClient(config)

    count = 0
    for item in data:
        item.pop("id", None)
        item["agent_id"] = agent_id
        # Re-embed se nao tiver embedding
        if "embedding" not in item or not item.get("embedding"):
            log.info("Gerando embedding para: %.60s", item.get("content", ""))
            item["embedding"] = generate_embedding(item["content"], config)
        client.insert("agent_memories", item)
        count += 1

    log.info("Importadas %d memorias de %s", count, input_path)


def cmd_inject_context(config: Config, context_text: str, session_id: str = None,
                       limit: int = 5, threshold: float = 0.6, agent_id: str = None):
    """Busca memorias e injeta como contexto formatado para LLM."""
    agent_id = agent_id or config.agent_id

    if not context_text.strip():
        log.info("Contexto vazio, pulando busca.")
        return

    results = cmd_search(
        config, context_text, limit=limit, threshold=threshold,
        agent_id=agent_id, json_output=True,
    )
    if not results:
        print("Nenhum contexto relevante encontrado.")
        return

    # Formatar como bloco de contexto para LLM
    lines = [
        "## Contexto Recuperado da Memoria (pgvector)",
        "",
    ]
    for i, r in enumerate(results, 1):
        sim = r.get("similarity", 0)
        impr = r.get("importance", 1)
        mtype = r.get("memory_type", "?")
        created = r.get("created_at", "")[:10]
        content = r.get("content", "")
        lines.append(f"### {i}. [{mtype}] importancia={impr} similaridade={sim:.2f} ({created})")
        lines.append(content)
        lines.append("")

    output = "\n".join(lines)
    print(output)
    return output


def cmd_stats(config: Config, agent_id: str = None):
    """Estatisticas do banco de memorias."""
    agent_id = agent_id or config.agent_id
    client = SupabaseClient(config)

    total = client.get(f"/rest/v1/agent_memories?agent_id=eq.{agent_id}&select=id")
    by_type = {}
    for t in MEMORY_TYPES:
        q = f"/rest/v1/agent_memories?agent_id=eq.{agent_id}&memory_type=eq.{t}&select=id"
        res = client.get(q)
        if res:
            by_type[t] = len(res)

    print(f"\n{'='*50}")
    print(f"  Estatisticas da Memoria (agent={agent_id})")
    print(f"{'='*50}")
    print(f"  Total: {len(total) if total else 0}")
    for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
        bar = "█" * min(c, 40)
        print(f"  {t:20s}: {c:4d} {bar}")
    print()


def cmd_migrate_sql(config: Config, print_only: bool = False):
    """Exibe ou executa o SQL de migracao no Supabase."""
    sql_path = Path(__file__).parent.parent / "references" / "supabase-migration.sql"
    if not sql_path.exists():
        log.error("Arquivo SQL nao encontrado em %s", sql_path)
        sys.exit(1)

    sql = sql_path.read_text()

    if print_only:
        print(sql)
        return

    log.info("Enviando SQL para o Supabase...")
    client = SupabaseClient(config)
    # Usa o endpoint /rest/v1/rpc/ (nao ideal para DDL, mas funcional)
    # Idealmente cole no SQL Editor. Esta rota e informativa.
    print("\n⚠️  Copie e cole o SQL abaixo no SQL Editor do Supabase:\n")
    print(sql)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="CLI de Memoria por Similaridade (pgvector + Supabase)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandos:
  store <text>          Armazenar memoria
  search <query>        Buscar por similaridade
  delete <uuid>         Deletar memoria
  list                  Listar memorias
  consolidate           Consolidar memorias similares
  export <path>         Exportar para JSON
  import <path>         Importar de JSON
  inject-context <txt>  Buscar e formatar contexto para LLM
  stats                 Estatisticas
  cleanup               Limpar expiradas
  migrate-sql           Mostrar SQL de migracao
        """,
    )
    parser.add_argument("command", nargs="?", help="Comando")
    parser.add_argument("argument", nargs="?", help="Argumento do comando")
    parser.add_argument("--type", default=None, help="Tipo de memoria (fact, decision, learned, etc)")
    parser.add_argument("--importance", type=int, default=1, help="Importancia 1-5")
    parser.add_argument("--session-id", default=None, help="ID da sessao")
    parser.add_argument("--agent-id", default=None, help="Agent ID (namespace)")
    parser.add_argument("--limit", type=int, default=None, help="Limite de resultados")
    parser.add_argument("--threshold", type=float, default=None, help="Threshold de similaridade")
    parser.add_argument("--metadata", default=None, help="JSON metadata")
    parser.add_argument("--ttl-days", type=int, default=None, help="TTL em dias")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (consolidate)")
    parser.add_argument("--fts", action="store_true", help="Full-text search em vez de vetorial")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--print-only", action="store_true", help="So printar SQL")

    args = parser.parse_args()
    config = Config()
    config.validate()

    cmd = args.command
    arg = args.argument

    kwargs = {
        "config": config,
        "agent_id": args.agent_id,
        "json_output": args.json_output,
    }

    commands = {
        "store": lambda: cmd_store(
            config, arg,
            memory_type=args.type or "general",
            importance=args.importance,
            session_id=args.session_id,
            metadata=args.metadata,
            ttl_days=args.ttl_days,
            agent_id=args.agent_id,
        ),
        "search": lambda: cmd_search(
            config, arg,
            limit=args.limit or config.default_limit,
            threshold=args.threshold or config.default_threshold,
            memory_type=args.type,
            session_id=args.session_id,
            agent_id=args.agent_id,
            fts=args.fts,
            json_output=args.json_output,
        ),
        "delete": lambda: cmd_delete(config, arg),
        "list": lambda: cmd_list(
            config,
            memory_type=args.type,
            agent_id=args.agent_id,
            limit=args.limit or 20,
            json_output=args.json_output,
        ),
        "consolidate": lambda: cmd_consolidate(
            config,
            dry_run=args.dry_run,
            threshold=args.threshold or 0.85,
            agent_id=args.agent_id,
        ),
        "export": lambda: cmd_export(config, arg, agent_id=args.agent_id),
        "import": lambda: cmd_import(config, arg, agent_id=args.agent_id),
        "inject-context": lambda: cmd_inject_context(
            config, arg,
            session_id=args.session_id,
            limit=args.limit or 5,
            threshold=args.threshold or 0.6,
            agent_id=args.agent_id,
        ),
        "stats": lambda: cmd_stats(config, agent_id=args.agent_id),
        "cleanup": lambda: SupabaseClient(config).rpc("cleanup_expired_memories",
                                                        {"p_agent_id": args.agent_id or config.agent_id}),
        "migrate-sql": lambda: cmd_migrate_sql(config, print_only=args.print_only),
    }

    if not cmd or cmd not in commands:
        parser.print_help()
        sys.exit(1)

    commands[cmd]()


if __name__ == "__main__":
    main()
