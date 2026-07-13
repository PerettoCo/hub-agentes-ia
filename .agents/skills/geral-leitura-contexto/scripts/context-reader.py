#!/usr/bin/env python3
"""
context-reader.py — Leitura Profunda de Contexto do OpenCode

Uso:
  python context-reader.py                         # Le contexto do diretorio atual
  python context-reader.py /caminho/para/pasta     # Le contexto de outra pasta
  python context-reader.py --json                  # Output JSON estruturado
  python context-reader.py --watch                 # Fica observando mudancas
  python context-reader.py --brief                 # So resumo de 5 linhas
  python context-reader.py --diff                  # Mostra o que mudou desde a ultima leitura
  python context-reader.py --store-memory          # Salva o contexto no Supabase (se memory-cli disponivel)

Dependencias:
  pip install python-dotenv pyyaml
"""

import os, sys, json, hashlib, re, time, logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("context-reader")

# ============================================================
# Dataclasses
# ============================================================

@dataclass
class FileInfo:
    path: str
    name: str
    size: int
    modified: str
    lines: int
    summary: str = ""


@dataclass
class ContextResult:
    root: str
    context_type: str  # CLIENTE | SQUAD | PROJETO | GENERICO
    name: str
    last_updated: str = ""
    purpose: str = ""
    tools: list = field(default_factory=list)
    commands: list = field(default_factory=list)
    skills: list = field(default_factory=list)
    env_vars: list = field(default_factory=list)
    state: dict = field(default_factory=dict)
    files: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)
    git_log: list = field(default_factory=list)
    mission_control: dict = field(default_factory=dict)
    read_at: str = ""


# ============================================================
# Detectores
# ============================================================

def detect_context_type(root: Path) -> tuple[str, str]:
    """Retorna (tipo, nome)."""
    name = root.name

    # CLIENTE
    has_calls = (root / "calls").is_dir()
    has_docs = (root / "docs").is_dir()
    has_campanhas = (root / "campanhas").is_dir()
    has_mission = (root / "mission-control").is_dir()
    has_clientes_sub = (root / "clientes").is_dir()

    if has_clientes_sub:
        return "SQUAD", name
    if (has_calls or has_mission) and not has_clientes_sub:
        return "CLIENTE", name
    if has_docs and (root.parent.name == "bases"):
        return "PROJETO", name
    if has_docs or has_campanhas:
        return "PROJETO", name

    return "GENERICO", name


def detect_name_from_context(root: Path) -> str:
    """Tenta extrair nome de CLAUDE.md ou AGENTS.md."""
    for fname in ["CLAUDE.md", "AGENTS.md"]:
        f = root / fname
        if f.exists():
            content = f.read_text(encoding="utf-8", errors="replace")
            # Procura titulo: # Nome
            m = re.search(r"^# (.+)$", content, re.MULTILINE)
            if m:
                return m.group(1).strip()
    return root.name


# ============================================================
# Leitores
# ============================================================

def read_file_preview(path: Path, max_lines: int = 50) -> str:
    """Le as primeiras linhas de um arquivo."""
    if not path.exists():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        preview = lines[:max_lines]
        if len(lines) > max_lines:
            preview.append(f"... ({len(lines) - max_lines} linhas a mais)")
        return "\n".join(preview)
    except Exception as e:
        return f"[erro ao ler: {e}]"


def read_claude_md(root: Path) -> Optional[dict]:
    """Le e extrai informacao do CLAUDE.md."""
    path = root / "CLAUDE.md"
    if not path.exists():
        return None

    content = path.read_text(encoding="utf-8", errors="replace")
    result = {
        "title": "",
        "purpose": "",
        "tools_found": [],
        "commands_found": [],
        "has_env_refs": False,
        "raw_preview": content[:500],
    }

    m = re.search(r"^# (.+)$", content, re.MULTILINE)
    if m:
        result["title"] = m.group(1)

    # Extrair secoes
    sections = re.findall(r"^## (.+)$", content, re.MULTILINE)
    result["sections"] = sections

    # Detectar ferramentas
    tool_patterns = [
        (r"n8n[-_ ]?ac?as?c?|n8nac", "n8n-as-code (n8nac)"),
        (r"npx", "npx (Node)"),
        (r"pip|poetry|uv", "Python (pip/poetry)"),
        (r"npm|yarn|pnpm", "Node (npm/yarn)"),
        (r"docker[- ]?compose|docker", "Docker"),
        (r"supabase", "Supabase"),
        (r"notion|notionapi", "Notion API"),
    ]
    for pattern, name in tool_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            result["tools_found"].append(name)

    # Detectar comandos
    cmd_patterns = [
        (r"`npx[^`]+`", "npx"),
        (r"`python[^`]+`", "python"),
        (r"`npm[^`]+`", "npm"),
        (r"`docker[^`]+`", "docker"),
    ]
    for pattern, _ in cmd_patterns:
        cmds = re.findall(pattern, content)
        result["commands_found"].extend(c.strip("`") for c in cmds[:5])

    result["has_env_refs"] = ".env" in content or "environ" in content or "SUPABASE_" in content

    return result


def read_agents_md(root: Path) -> Optional[dict]:
    """Le AGENTS.md."""
    path = root / "AGENTS.md"
    if not path.exists():
        return None

    content = path.read_text(encoding="utf-8", errors="replace")
    return {
        "title": re.search(r"^# (.+)$", content, re.MULTILINE).group(1) if re.search(r"^# (.+)$", content, re.MULTILINE) else "",
        "skills_refs": re.findall(r"`?([\w-]+(?:skill|hub|agent)[\w-]*)`?", content, re.IGNORECASE),
        "preview": content[:300],
    }


def read_mission_control(root: Path) -> dict:
    """Le pasta mission-control/."""
    mc_dir = root / "mission-control"
    if not mc_dir.is_dir():
        return {}

    result = {}
    for fname in ["okr-quarter.md", "apostas-vivas.md", "combinados.md",
                   "personas-call.md", "historico-checkins.md"]:
        f = mc_dir / fname
        if f.exists():
            content = f.read_text(encoding="utf-8", errors="replace")
            # Extrair apenas a primeira secao (resumo)
            lines = content.splitlines()
            preview = [l for l in lines if l.strip()][:20]
            result[fname.replace(".md", "")] = "\n".join(preview)

    return result


def read_env_vars(root: Path) -> list[str]:
    """Le .env e retorna apenas nomes (NUNCA valores)."""
    env_file = root / ".env"
    if not env_file.exists():
        # Tentar pai
        env_file = root.parent / ".env"
    if not env_file.exists():
        return []

    names = []
    try:
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name = line.split("=", 1)[0].strip()
                if name and not name.startswith("#"):
                    names.append(name)
    except Exception:
        pass
    return sorted(set(names))


def read_git_log(root: Path, count: int = 5) -> list[dict]:
    """Le git log recente."""
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={count}",
             "--format=%h|%ai|%s"],
            capture_output=True, text=True, cwd=root, timeout=5,
        )
        entries = []
        for line in result.stdout.strip().splitlines():
            if "|" in line:
                parts = line.split("|", 2)
                entries.append({
                    "hash": parts[0],
                    "date": parts[1][:10],
                    "message": parts[2] if len(parts) > 2 else "",
                })
        return entries
    except Exception:
        return []


def read_package_info(root: Path) -> dict:
    """Le informacoes basicas de config do projeto."""
    info = {}
    for fname in ["package.json", "pyproject.toml", "Cargo.toml"]:
        f = root / fname
        if f.exists():
            try:
                if fname == "package.json":
                    data = json.loads(f.read_text())
                    info["type"] = "node"
                    info["name"] = data.get("name", "")
                    info["version"] = data.get("version", "")
                    info["scripts"] = list(data.get("scripts", {}).keys())[:8]
                elif fname == "pyproject.toml":
                    content = f.read_text()
                    m = re.search(r'^name\s*=\s*"([^"]+)"', content, re.MULTILINE)
                    if m:
                        info["name"] = m.group(1)
                    m = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
                    if m:
                        info["version"] = m.group(1)
                    info["type"] = "python"
            except Exception:
                pass
        if info:
            break
    return info


def list_skills(root: Path) -> list[str]:
    """Lista skills instaladas."""
    skills = []
    for skills_dir in [root / ".agents" / "skills", root / ".claude" / "skills"]:
        if skills_dir.is_dir():
            for d in sorted(skills_dir.iterdir()):
                if d.is_dir() and (d / "SKILL.md").exists():
                    skills.append(d.name)
    return skills


def scan_directory(root: Path, max_depth: int = 2) -> list[FileInfo]:
    """Escaneia diretorio e retorna arquivos importantes."""
    important_patterns = [
        "*.md", "*.py", "*.ts", "*.js", "*.json", "*.yaml", "*.yml",
        "*.toml", "*.cfg", "*.ini", "Dockerfile", "docker-compose*.yml",
        ".env*", "Makefile", "*.sql",
    ]
    ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv",
                   ".opencode", "calls", "checkins", ".claude", ".agents"}
    # calls e checkins sao ignorados para nao poluir

    files = []
    for pattern in important_patterns:
        for f in root.glob(pattern):
            if any(ign in f.parts for ign in ignore_dirs):
                continue
            rel = f.relative_to(root)
            depth = len(rel.parts)
            if depth > max_depth:
                continue
            try:
                stat = f.stat()
                content = f.read_text(encoding="utf-8", errors="replace")
                lines = len(content.splitlines())
                # Sumario: primeiras linhas nao vazias
                non_empty = [l.strip() for l in content.splitlines() if l.strip()]
                summary = non_empty[0] if non_empty else ""
                if len(summary) > 120:
                    summary = summary[:117] + "..."
                files.append(FileInfo(
                    path=str(rel),
                    name=f.name,
                    size=stat.st_size,
                    modified=datetime.fromtimestamp(stat.st_mtime).isoformat()[:19],
                    lines=lines,
                    summary=summary,
                ))
            except Exception:
                pass

    return sorted(files, key=lambda x: x.path)


# ============================================================
# Context Builder
# ============================================================

def build_context(root_path: str | Path, brief: bool = False) -> ContextResult:
    """Constroi o contexto completo de um diretorio."""
    root = Path(root_path).resolve()
    if not root.is_dir():
        log.error("Diretorio nao encontrado: %s", root)
        sys.exit(1)

    ctx_type, ctx_name = detect_context_type(root)
    name_from_file = detect_name_from_context(root)
    name = name_from_file or ctx_name

    result = ContextResult(
        root=str(root),
        context_type=ctx_type,
        name=name,
        read_at=datetime.now().isoformat()[:19],
    )

    # Propósito
    claude = read_claude_md(root)
    if claude:
        result.purpose = claude.get("title", "")
        result.tools = claude.get("tools_found", [])
        result.commands = claude.get("commands_found", [])

    # AGENTS.md
    agents = read_agents_md(root)
    if agents:
        result.notes.append(f"AGENTS.md references skills: {', '.join(agents.get('skills_refs', []))}")

    # Skills instaladas
    result.skills = list_skills(root)

    # Variaveis de ambiente
    result.env_vars = read_env_vars(root)

    # Mission Control
    result.mission_control = read_mission_control(root)

    # Estado resumido do Mission Control
    mc = result.mission_control
    if mc:
        state = {}
        if "okr-quarter" in mc:
            first_line = mc["okr-quarter"].split("\n")[0] if mc["okr-quarter"] else ""
            state["okr"] = first_line[:80] if first_line else "presente"
        if "apostas-vivas" in mc:
            lines = [l for l in mc["apostas-vivas"].split("\n") if l.strip().startswith("|") and "Aposta" not in l]
            state["apostas"] = f"{len(lines)} ativas"
        if "combinados" in mc:
            pends = len(re.findall(r"\[ \]", mc["combinados"]))
            state["combinados_pendentes"] = pends
        if "historico-checkins" in mc:
            dates = re.findall(r"## (\d{4}-\d{2}-\d{2})", mc["historico-checkins"])
            state["ultimo_checkin"] = dates[-1] if dates else "N/A"
        result.state = state

    # Git log
    result.git_log = read_git_log(root)

    # Package info
    pkg = read_package_info(root)
    if pkg:
        result.notes.append(f"Projeto: {pkg.get('type', '?')} | {pkg.get('name', '')} v{pkg.get('version', '?')}")

    # Ultima atualizacao
    if result.git_log:
        result.last_updated = result.git_log[0]["date"]
    elif claude:
        pass  # poderia extrair data

    # Scaneamento de arquivos (so em modo nao-brief)
    if not brief:
        result.files = scan_directory(root)

    # Sugestoes
    if not claude:
        result.suggestions.append("Nao encontrei CLAUDE.md — considere rodar /contexto para gerar um.")

    if not (root / ".agents" / "skills").is_dir() and not (root / ".claude" / "skills").is_dir():
        result.suggestions.append("Nenhuma skill de agente encontrada. Considere configurar skills.")

    if result.env_vars:
        result.notes.append(f"{len(result.env_vars)} variaveis de ambiente definidas.")

    return result


def format_markdown(ctx: ContextResult, brief: bool = False) -> str:
    """Formata resultado como markdown."""
    lines = [
        f"## Resumo de Contexto",
        f"",
        f"**Tipo:** {ctx.context_type}",
        f"**Nome:** {ctx.name}",
        f"**Raiz:** `{ctx.root}`",
    ]
    if ctx.last_updated:
        lines.append(f"**Ultima atualizacao:** {ctx.last_updated}")
    lines.append(f"**Lido em:** {ctx.read_at}")
    lines.append("")

    if ctx.purpose:
        lines.append(f"### Proposito")
        lines.append(f"{ctx.purpose}")
        lines.append("")

    if ctx.tools:
        lines.append(f"### Ferramentas Detectadas")
        for t in ctx.tools:
            lines.append(f"- {t}")
        lines.append("")

    if ctx.commands:
        lines.append(f"### Comandos")
        for c in ctx.commands[:5]:
            lines.append(f"- `{c}`")
        lines.append("")

    if ctx.skills:
        lines.append(f"### Skills Instaladas ({len(ctx.skills)})")
        for s in ctx.skills:
            lines.append(f"- `{s}`")
        lines.append("")

    if ctx.state:
        lines.append(f"### Estado Atual (Mission Control)")
        for k, v in ctx.state.items():
            lines.append(f"- **{k}:** {v}")
        lines.append("")

    if ctx.git_log and not brief:
        lines.append(f"### Git Log (recente)")
        for entry in ctx.git_log:
            lines.append(f"- `{entry['hash']}` {entry['date']} {entry['message']}")
        lines.append("")

    if ctx.env_vars:
        lines.append(f"### Variaveis de Ambiente ({len(ctx.env_vars)})")
        lines.append(f"Definidas: {', '.join(sorted(ctx.env_vars)[:10])}")
        if len(ctx.env_vars) > 10:
            lines.append(f"... e mais {len(ctx.env_vars) - 10}")
        lines.append("")

    if ctx.notes:
        lines.append(f"### Notas")
        for n in ctx.notes:
            lines.append(f"- {n}")
        lines.append("")

    if ctx.suggestions:
        lines.append(f"### Sugestoes")
        for s in ctx.suggestions:
            lines.append(f"- {s}")
        lines.append("")

    if not brief and ctx.files:
        lines.append(f"### Arquivos ({len(ctx.files)})")
        for f in ctx.files:
            icon = "📄"
            if f.name == "CLAUDE.md":
                icon = "📋"
            elif f.name == "AGENTS.md":
                icon = "🤖"
            elif f.name.endswith(".py"):
                icon = "🐍"
            elif f.name.endswith((".ts", ".js")):
                icon = "🟦"
            lines.append(f"- {icon} `{f.path}` ({f.lines} linhas, {_fmt_size(f.size)})")
        lines.append("")

    return "\n".join(lines)


def _fmt_size(bytes: int) -> str:
    if bytes < 1024:
        return f"{bytes}B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.1f}KB"
    return f"{bytes / (1024 * 1024):.1f}MB"


def format_json(ctx: ContextResult) -> str:
    """Formata resultado como JSON."""
    return json.dumps(asdict(ctx), indent=2, default=str, ensure_ascii=False)


# ============================================================
# Memoization (cache do ultimo contexto)
# ============================================================

CACHE_FILE = Path.home() / ".cache" / "context-reader-cache.json"

def cache_load(root: str) -> Optional[ContextResult]:
    if CACHE_FILE.exists():
        try:
            data = json.loads(CACHE_FILE.read_text())
            if data.get("root") == root:
                return ContextResult(**data)
        except Exception:
            pass
    return None


def cache_save(ctx: ContextResult):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(asdict(ctx), default=str))


# ============================================================
# Watch mode
# ============================================================

def watch_mode(root_path: str, interval: int = 5):
    """Fica observando mudancas nos arquivos de contexto."""
    import time as time_module

    log.info("Watch mode ativo em: %s (intervalo=%ds)", root_path, interval)
    log.info("Pressione Ctrl+C para parar.")

    root = Path(root_path)
    seen = {}

    try:
        while True:
            # Checar arquivos-chave
            for fname in ["CLAUDE.md", "AGENTS.md", ".env"]:
                f = root / fname
                if f.exists():
                    mtime = f.stat().st_mtime
                    if fname in seen and seen[fname] != mtime:
                        log.info("Mudanca detectada em %s", fname)
                        ctx = build_context(root_path)
                        print(format_markdown(ctx, brief=True))
                    seen[fname] = mtime

            # Mission control
            mc_dir = root / "mission-control"
            if mc_dir.is_dir():
                for f in mc_dir.glob("*.md"):
                    mtime = f.stat().st_mtime
                    key = f"mc/{f.name}"
                    if key in seen and seen[key] != mtime:
                        log.info("Mudanca em mission-control/%s", f.name)
                    seen[key] = mtime

            time_module.sleep(interval)
    except KeyboardInterrupt:
        log.info("Watch mode encerrado.")


# ============================================================
# Diff mode
# ============================================================

def diff_context(root_path: str) -> str:
    """Compara contexto atual com o cache."""
    cached = cache_load(root_path)
    current = build_context(root_path)

    if not cached:
        log.info("Nenhum cache anterior. Salvando como baseline.")
        cache_save(current)
        return "Baseline salva. Rode novamente para ver diff."

    lines = []
    if cached.name != current.name:
        lines.append(f"- Nome: '{cached.name}' → '{current.name}'")
    if cached.purpose != current.purpose:
        lines.append("- Proposito mudou")
    if sorted(cached.tools) != sorted(current.tools):
        old_t = set(cached.tools)
        new_t = set(current.tools)
        added = new_t - old_t
        removed = old_t - new_t
        if added:
            lines.append(f"- Ferramentas adicionadas: {', '.join(added)}")
        if removed:
            lines.append(f"- Ferramentas removidas: {', '.join(removed)}")
    if cached.state != current.state:
        lines.append("- Estado do Mission Control mudou")
    if len(cached.skills) != len(current.skills):
        lines.append(f"- Skills: {len(cached.skills)} → {len(current.skills)}")

    cache_save(current)

    if not lines:
        return "Contexto identico ao cache. Sem mudancas."

    return "Mudancas detectadas:\n" + "\n".join(lines)


# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Leitor de Contexto do OpenCode")
    parser.add_argument("path", nargs="?", default=".", help="Diretorio para ler")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--brief", action="store_true", help="Resumo compacto")
    parser.add_argument("--watch", action="store_true", help="Modo observador")
    parser.add_argument("--diff", action="store_true", help="Comparar com cache")
    parser.add_argument("--store-memory", action="store_true",
                        help="Salvar contexto no Supabase (requer memory-cli.py)")

    args = parser.parse_args()
    root_path = str(Path(args.path).resolve())

    if args.diff:
        print(diff_context(root_path))
        return

    if args.watch:
        watch_mode(root_path)
        return

    ctx = build_context(root_path, brief=args.brief)
    cache_save(ctx)

    if args.json:
        print(format_json(ctx))
    else:
        print(format_markdown(ctx, brief=args.brief))

    # Salvar no Supabase se pediu
    if args.store_memory:
        try:
            mem_cli = Path(__file__).parent.parent.parent / "geral-memoria-pgvector" / "scripts" / "memory-cli.py"
            if mem_cli.exists():
                summary = f"Contexto de {ctx.name} ({ctx.context_type}): {ctx.purpose or 'sem proposito'}"
                subprocess.run(
                    [sys.executable, str(mem_cli), "store", summary,
                     "--type", "context", "--importance", "2",
                     "--metadata", json.dumps({"root": ctx.root, "type": ctx.context_type})],
                    capture_output=True, timeout=30,
                )
                log.info("Contexto salvo na memoria pgvector.")
            else:
                log.warning("memory-cli.py nao encontrado em %s", mem_cli)
        except Exception as e:
            log.warning("Falha ao salvar contexto no Supabase: %s", e)


if __name__ == "__main__":
    main()
