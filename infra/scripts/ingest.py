#!/usr/bin/env python3
"""
Ingestor universal — detecta novos arquivos no input do usuário e processa.
Usa /workspace/input/ (symlink para volume persistente) e /workspace/output/.
"""
import os, sys, json, shutil, subprocess, re, glob
from pathlib import Path

INPUT_DIR = Path("/workspace/input")
OUTPUT_DIR = Path("/workspace/output")

def get_user() -> str:
    user = os.environ.get("HUB_USERNAME", "unknown")
    return user.replace(".", "-")

def ensure_dirs(user: str = None):
    """Cria subpastas de output."""
    for d in [
        INPUT_DIR,
        OUTPUT_DIR / "handoff",
        OUTPUT_DIR / "reports",
        OUTPUT_DIR / "queries",
        OUTPUT_DIR / "shared",
        OUTPUT_DIR / "temp",
    ]:
        d.mkdir(parents=True, exist_ok=True)
    return INPUT_DIR, OUTPUT_DIR

def scan_input(input_dir: Path) -> list:
    """Retorna arquivos novos no input (não processados)."""
    files = []
    for f in input_dir.glob("*"):
        if f.is_file() and not f.name.startswith(".") and not f.name.endswith(".done"):
            files.append(f)
    return sorted(files, key=lambda x: x.stat().st_mtime)

def process_file(filepath: Path, output_dir: Path) -> dict:
    """Processa um arquivo usando file-reader.py e salva resultado."""
    filepath = Path(filepath)
    ext = filepath.suffix.lower()
    result = {
        "file": filepath.name,
        "path": str(filepath),
        "status": "processed",
        "text": "",
        "output_path": "",
    }

    # Try file-reader.py
    reader = Path(__file__).parent / "file-reader.py"
    if reader.exists():
        try:
            r = subprocess.run(
                ["python3", str(reader), str(filepath)],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode == 0:
                text = r.stdout
            else:
                text = f"[ERRO] file-reader: {r.stderr[:500]}"
        except Exception as e:
            text = f"[ERRO] file-reader exception: {e}"
    else:
        # Fallback: read as text if possible
        try:
            text = filepath.read_text(errors="replace")
        except:
            text = f"[format not readable: {ext}]"

    result["text"] = text

    # Save processed output
    stem = filepath.stem
    output_path = output_dir / "handoff" / f"{stem}_processed.json"
    output_path.write_text(json.dumps({
        "source": filepath.name,
        "type": ext,
        "content": text,
        "word_count": len(text.split()),
    }, indent=2, ensure_ascii=False))

    result["output_path"] = str(output_path)
    return result

def ingest(user: str = None, filespec: str = None):
    """Main ingest function."""
    if not user:
        user = get_user()
    input_dir, output_dir = ensure_dirs(user)

    if filespec:
        # Process specific file pattern
        import glob as gb
        matching = []
        for f in gb.glob(filespec, recursive=True):
            matching.append(Path(f))
    else:
        # Scan input directory
        matching = scan_input(input_dir)

    if not matching:
        print(json.dumps({
            "user": user,
            "input_dir": str(input_dir),
            "output_dir": str(output_dir),
            "status": "no_files",
            "message": "Nenhum arquivo encontrado. Salve os arquivos em /workspace/input/ e rode /ingest novamente."
        }, indent=2, ensure_ascii=False))
        return

    results = []
    for f in matching:
        r = process_file(f, output_dir)
        results.append(r)
        # Mark as done
        f.rename(f.with_name(f.name + ".done"))
        # Also move to temp
        shutil.copy2(f, output_dir / "temp" / f.name)

    print(json.dumps({
        "user": user,
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "input_processed": len(results),
        "files": [
            {
                "file": r["file"],
                "status": r["status"],
                "word_count": len(r["text"].split()),
                "output": r["output_path"],
                "preview": r["text"][:200] + "..." if len(r["text"]) > 200 else r["text"]
            }
            for r in results
        ]
    }, indent=2, ensure_ascii=False))

def list_output(user: str = None):
    if not user:
        user = get_user()
    input_dir, output_dir = ensure_dirs(user)
    files = []
    for subdir in ["handoff", "reports", "queries", "shared"]:
        d = output_dir / subdir
        if d.exists():
            for f in sorted(d.iterdir()):
                if f.is_file():
                    files.append({
                        "dir": subdir,
                        "file": f.name,
                        "size": f.stat().st_size
                    })
    print(json.dumps({"user": user, "output_dir": str(output_dir), "files": files}, indent=2))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ingest"
    if cmd == "ingest":
        user = sys.argv[2] if len(sys.argv) > 2 else None
        filespec = sys.argv[3] if len(sys.argv) > 3 else None
        ingest(user, filespec)
    elif cmd == "list":
        user = sys.argv[2] if len(sys.argv) > 2 else None
        list_output(user)
    else:
        print(json.dumps({"error": f"Comando desconhecido: {cmd}. Use: ingest, list"}))
