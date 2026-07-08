"""
checklist_ekyte.py — Enriquece o checklist semanal com dados reais do Ekyte.

Roda integrado ao coordenador/checklist.py.
Substitui os [ ? ] por [ S ] ou [ N ] reais
com base nos dados das sprints, tarefas e timesheet.

Uso standalone:
  python scripts/ekyte/checklist_ekyte.py

Uso integrado (importar):
  from scripts.ekyte.checklist_ekyte import verificar_conformidade_ekyte
  resultado = verificar_conformidade_ekyte(cliente)
"""
import sys
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.ekyte.connector import EkyteClient
from scripts.connectors import load_clientes


def verificar_conformidade_ekyte(cliente: dict) -> dict:
    """
    Verifica itens de conformidade de um cliente usando dados reais do Ekyte.
    Retorna dict com status S/N de cada item e observações.
    """
    ekyte = EkyteClient()
    workspace_id = cliente.get("ekyte_workspace_id")
    squad_id = cliente.get("ekyte_squad_id")
    project_id = cliente.get("ekyte_sprint_project_id")

    resultado = {
        "cliente": cliente["nome"],
        "data": date.today().strftime("%d/%m/%Y"),
        "itens": {},
        "erros": [],
    }

    # ── Sprint documentada no Ekyte ──────────────────────────────────────────
    try:
        sprints = ekyte.get_sprints_ativas(workspace_id=workspace_id)
        tem_sprint_ativa = len(sprints) > 0
        resultado["itens"]["sprint_documentada"] = {
            "status": "S" if tem_sprint_ativa else "N",
            "detalhe": f"{len(sprints)} sprint(s) ativa(s)" if tem_sprint_ativa
                       else "Nenhuma sprint ativa encontrada",
            "sprints": [{"nome": s["name"], "fim": s.get("endDate")} for s in sprints[:3]],
        }
    except Exception as e:
        resultado["itens"]["sprint_documentada"] = {"status": "?", "detalhe": str(e)}
        resultado["erros"].append(f"Sprints: {e}")

    # ── % de conclusão da sprint atual ───────────────────────────────────────
    try:
        if project_id:
            status_sprint = ekyte.get_status_sprint(project_id)
            pct = status_sprint.get("percentual", 0)
            resultado["itens"]["sprint_em_progresso"] = {
                "status": "S" if pct >= 50 else "N",
                "detalhe": f"{pct}% concluído ({status_sprint.get('concluidas')}/{status_sprint.get('total_tarefas')} tarefas)",
                "status_emoji": status_sprint.get("status", "?"),
            }
    except Exception as e:
        resultado["itens"]["sprint_em_progresso"] = {"status": "?", "detalhe": str(e)}

    # ── Tarefas atrasadas ────────────────────────────────────────────────────
    try:
        atrasadas = ekyte.get_tarefas_atrasadas(workspace_id=workspace_id, squad_id=squad_id)
        tem_atrasadas = len(atrasadas) > 0
        resultado["itens"]["tarefas_no_prazo"] = {
            "status": "N" if tem_atrasadas else "S",
            "detalhe": f"{len(atrasadas)} tarefa(s) atrasada(s)" if tem_atrasadas
                       else "Nenhuma tarefa atrasada",
            "atrasadas": [
                {"titulo": t.get("title", "?"), "prazo": t.get("currentDueDate", "?")}
                for t in atrasadas[:5]
            ],
        }
    except Exception as e:
        resultado["itens"]["tarefas_no_prazo"] = {"status": "?", "detalhe": str(e)}
        resultado["erros"].append(f"Tarefas: {e}")

    # ── FCAs abertas ─────────────────────────────────────────────────────────
    try:
        fcas = ekyte.get_fcas_abertas(workspace_id=workspace_id, squad_id=squad_id)
        resultado["itens"]["fcas_abertas"] = {
            "status": "S",
            "detalhe": f"{len(fcas)} FCA(s) em aberto" if fcas else "Nenhuma FCA aberta",
            "fcas": [{"assunto": f.get("subject", "?")} for f in fcas[:5]],
        }
    except Exception as e:
        resultado["itens"]["fcas_abertas"] = {"status": "?", "detalhe": str(e)}
        resultado["erros"].append(f"FCAs: {e}")

    # ── Timesheet atualizado ─────────────────────────────────────────────────
    try:
        ts = ekyte.get_timesheet_semana(squad_id=squad_id)
        resultado["itens"]["timesheet_atualizado"] = {
            "status": "S" if ts["atualizado"] else "N",
            "detalhe": f"{ts['total_registros']} apontamento(s) esta semana",
            "por_usuario": ts["por_usuario"],
        }
    except Exception as e:
        resultado["itens"]["timesheet_atualizado"] = {"status": "?", "detalhe": str(e)}
        resultado["erros"].append(f"Timesheet: {e}")

    # ── Calcula score geral ──────────────────────────────────────────────────
    itens = resultado["itens"].values()
    total = len(itens)
    verdes = sum(1 for i in itens if i["status"] == "S")
    pct_conformidade = round(verdes / total * 100) if total > 0 else 0

    resultado["score"] = f"{verdes}/{total}"
    resultado["percentual"] = pct_conformidade
    resultado["status_geral"] = (
        "🟢" if pct_conformidade >= 85 else
        "🟡" if pct_conformidade >= 60 else
        "🔴"
    )

    return resultado


def formatar_checklist_texto(resultado: dict) -> str:
    """Formata o resultado do checklist em texto legível para email."""
    itens = resultado["itens"]
    linhas = [
        f"── {resultado['cliente']} — {resultado['data']} ──",
        f"Score: {resultado['score']} itens ok {resultado['status_geral']}",
        "",
    ]

    mapa_labels = {
        "sprint_documentada": "Sprint documentada no Ekyte?",
        "sprint_em_progresso": "Sprint com progresso adequado (≥50%)?",
        "tarefas_no_prazo": "Tarefas dentro do prazo?",
        "fcas_abertas": "FCAs abertas registradas?",
        "timesheet_atualizado": "Timesheet atualizado esta semana?",
    }

    for chave, item in itens.items():
        label = mapa_labels.get(chave, chave)
        status = item["status"]
        detalhe = item.get("detalhe", "")
        linhas.append(f"[ {status} ] {label}")
        if detalhe:
            linhas.append(f"        → {detalhe}")

        # Detalha tarefas atrasadas se houver
        if chave == "tarefas_no_prazo" and item.get("atrasadas"):
            for t in item["atrasadas"][:3]:
                linhas.append(f"          • {t['titulo']} (prazo: {t['prazo'][:10] if t['prazo'] else '?'})")

        # Detalha FCAs se houver
        if chave == "fcas_abertas" and item.get("fcas"):
            for f in item["fcas"][:3]:
                linhas.append(f"          • {f['assunto']}")

    if resultado.get("erros"):
        linhas.append("")
        linhas.append(f"Erros de coleta: {', '.join(resultado['erros'])}")

    return "\n".join(linhas)


def main():
    """Roda checklist Ekyte para todos os clientes e imprime resultado."""
    clientes = load_clientes()
    clientes_ekyte = [c for c in clientes if c.get("ekyte_workspace_id")]

    if not clientes_ekyte:
        print("Nenhum cliente com ekyte_workspace_id em clientes.json")
        print("Adicione 'ekyte_workspace_id' e 'ekyte_squad_id' em cada cliente.")
        return

    for cliente in clientes_ekyte:
        print(f"\n{'='*60}")
        resultado = verificar_conformidade_ekyte(cliente)
        texto = formatar_checklist_texto(resultado)
        print(texto)


if __name__ == "__main__":
    main()
