"""
install_cron.py — Instala todos os crons automaticamente.

Uso: python setup/install_cron.py
"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent.resolve()
PYTHON = sys.executable

CRONS = [
    # Domingo 20h — Coordenador: briefing do Comitê de segunda
    f"0 20 * * 0 {PYTHON} {BASE}/scripts/coordenador/briefing_comite.py >> {BASE}/logs/coordenador.log 2>&1",

    # Quinta 7h — GT: análise de performance semanal
    f"0 7 * * 4 {PYTHON} {BASE}/scripts/gt/analise_performance.py >> {BASE}/logs/gt.log 2>&1",

    # Quinta 8h — AM: atualização de OKRs com dados do GT
    f"0 8 * * 4 {PYTHON} {BASE}/scripts/am/atualizar_okrs.py >> {BASE}/logs/am.log 2>&1",

    # Sexta 16h — Coordenador: checklist semanal S/N
    f"0 16 * * 5 {PYTHON} {BASE}/scripts/coordenador/checklist.py >> {BASE}/logs/coordenador.log 2>&1",

    # Dia 1 de cada mês, 8h — AM: envio de pesquisa NPS/CSAT
    f"0 8 1 * * {PYTHON} {BASE}/scripts/am/enviar_nps.py >> {BASE}/logs/am.log 2>&1",
]

def install():
    # Cria pasta de logs
    logs_dir = BASE / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Lê crontab atual
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    # Remove entradas antigas do v4-automations
    lines = [l for l in existing.splitlines() if str(BASE) not in l]

    # Adiciona as novas
    lines.append("")
    lines.append("# V4 Automations — Squad Mata Leão")
    lines.extend(CRONS)
    lines.append("")

    new_crontab = "\n".join(lines)

    proc = subprocess.run(["crontab", "-"], input=new_crontab, text=True, capture_output=True)

    if proc.returncode == 0:
        print("Crons instalados com sucesso!")
        print()
        print("Agenda:")
        print("  Domingo 20h    → Briefing do Comitê (Coordenador)")
        print("  Quinta  7h     → Análise de performance (GT)")
        print("  Quinta  8h     → Atualização de OKRs (AM)")
        print("  Sexta   16h    → Checklist semanal (Coordenador)")
        print("  Dia 1   8h     → Envio NPS/CSAT (AM)")
        print()
        print(f"Logs em: {logs_dir}")
    else:
        print(f"ERRO ao instalar crons: {proc.stderr}")

    # Salva referência
    cron_ref = BASE / "cron" / "crontab.txt"
    cron_ref.write_text("\n".join(CRONS))
    print(f"Referência salva em {cron_ref}")

if __name__ == "__main__":
    install()
