"""
sprints.py — Gestão de sprints no Ekyte.

Funções:
  - Resumo de sprint atual (% conclusão, tarefas, atrasos)
  - Criação automática da próxima sprint com tarefas padrão
  - Relatório de sprint para o briefing do Comitê

Uso:
  python scripts/ekyte/sprints.py --cliente "Nome do Cliente"
"""
import sys
import argparse
from pathlib import Path
from datetime import date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.ekyte.connector import EkyteClient
from scripts.connectors import load_clientes, claude


SYSTEM_AM = """
Você é o Agente Account Manager V4.
Gere resumos de sprint claros, acionáveis e no formato padrão da operação.
Foque em: o que foi entregue, o que está em risco, qual a ação imediata.
"""

# Tarefas padrão por tipo de sprint — adapte conforme sua operação
TAREFAS_PADRAO_SPRINT = {
    "onboarding": [
        {"titulo": "Pesquisa de keywords e benchmarks", "executor_role": "gt", "dias": 3},
        {"titulo": "Briefing de campanha Meta Ads", "executor_role": "gt", "dias": 4},
        {"titulo": "Copy dos primeiros 3 anúncios", "executor_role": "copy", "dias": 5},
        {"titulo": "Criação dos assets visuais (2 estáticos + 1 vídeo)", "executor_role": "design", "dias": 7},
        {"titulo": "Ativação das campanhas", "executor_role": "gt", "dias": 10},
    ],
    "ongoing": [
        {"titulo": "Análise de performance semanal", "executor_role": "gt", "dias": 2},
        {"titulo": "Atualização de OKRs no plano tático", "executor_role": "am", "dias": 2},
        {"titulo": "Otimizações de campanhas", "executor_role": "gt", "dias": 3},
        {"titulo": "Rotação de criativos", "executor_role": "copy", "dias": 5},
    ],
    "replanejamento": [
        {"titulo": "Análise do quarter anterior", "executor_role": "am", "dias": 2},
        {"titulo": "Novo planejamento de mídia", "executor_role": "gt", "dias": 4},
        {"titulo": "Atualização de OKRs para o próximo quarter", "executor_role": "am", "dias": 5},
        {"titulo": "Apresentação do replanejamento para o cliente", "executor_role": "am", "dias": 7},
    ],
}


def resumo_sprint(cliente: dict) -> dict:
    """Gera resumo completo da sprint atual do cliente."""
    ekyte = EkyteClient()
    workspace_id = cliente.get("ekyte_workspace_id")
    squad_id = cliente.get("ekyte_squad_id")
    project_id = cliente.get("ekyte_sprint_project_id")

    resumo = {"cliente": cliente["nome"], "sprints": [], "tarefas_atrasadas": [], "fcas": []}

    # Sprints ativas
    sprints = ekyte.get_sprints_ativas(workspace_id=workspace_id)
    for sprint in sprints:
        status = ekyte.get_status_sprint(sprint["id"])
        resumo["sprints"].append(status)

    # Tarefas atrasadas
    resumo["tarefas_atrasadas"] = ekyte.get_tarefas_atrasadas(
        workspace_id=workspace_id, squad_id=squad_id
    )

    # FCAs abertas
    resumo["fcas"] = ekyte.get_fcas_abertas(
        workspace_id=workspace_id, squad_id=squad_id
    )

    return resumo


def gerar_relatorio_sprint_claude(resumo: dict) -> str:
    """Usa Claude para gerar relatório narrativo da sprint."""
    user_prompt = f"""
Gere o relatório de sprint do cliente {resumo['cliente']} para o briefing do Comitê.

Sprints ativas:
{resumo['sprints'] if resumo['sprints'] else 'Nenhuma sprint ativa'}

Tarefas atrasadas ({len(resumo['tarefas_atrasadas'])}):
{[{'titulo': t.get('title'), 'prazo': t.get('currentDueDate', '')[:10]} for t in resumo['tarefas_atrasadas'][:10]]}

FCAs abertas ({len(resumo['fcas'])}):
{[f.get('subject') for f in resumo['fcas'][:5]]}

Gere no formato:

## {resumo['cliente']} — Status Sprint

**Sprints em andamento:**
[Para cada sprint: nome, %, status emoji, prazo]

**Tarefas em risco:**
[Liste as atrasadas com título e prazo]

**FCAs abertas:**
[Liste os assuntos]

**Diagnóstico:** [1 frase — qual o risco principal desta semana]

**Ação prioritária:** [o que o AM precisa fazer agora]
"""
    return claude(SYSTEM_AM, user_prompt, max_tokens=600)


def criar_proxima_sprint(
    cliente: dict,
    tipo: str = "ongoing",
    executor_ids: dict = None,
) -> dict:
    """
    Cria a próxima sprint no Ekyte com tarefas padrão.

    Args:
        cliente: dict do cliente em clientes.json
        tipo: "onboarding" | "ongoing" | "replanejamento"
        executor_ids: dict mapeando role → ekyte_user_id
                     ex: {"gt": "uuid-gt", "am": "uuid-am", "copy": "uuid-copy"}

    ATENÇÃO: requer confirmação de POST /projects com suporte Ekyte.
    """
    ekyte = EkyteClient()
    workspace_id = cliente.get("ekyte_workspace_id")
    executor_ids = executor_ids or {}

    hoje = date.today()
    inicio = hoje.strftime("%Y-%m-%d")
    fim = (hoje + timedelta(days=14)).strftime("%Y-%m-%d")

    # Identifica número da próxima sprint
    sprints_existentes = ekyte.get_projetos(workspace_id=workspace_id)
    num_sprint = len(sprints_existentes) + 1
    nome_sprint = f"Sprint #{num_sprint} — {cliente['nome']} — {hoje.strftime('%d/%m')}"

    print(f"  Criando sprint: {nome_sprint}")

    # Cria o projeto/sprint
    sprint = ekyte.criar_sprint(
        nome=nome_sprint,
        workspace_id=workspace_id,
        inicio=inicio,
        fim=fim,
        descricao=f"Sprint automática — tipo: {tipo} — criada por V4 Automations",
    )

    sprint_id = sprint.get("id")
    tarefas_criadas = []

    if sprint_id:
        tarefas_padrao = TAREFAS_PADRAO_SPRINT.get(tipo, [])
        for tarefa_def in tarefas_padrao:
            role = tarefa_def["executor_role"]
            executor_id = executor_ids.get(role)
            if not executor_id:
                print(f"    Pulando '{tarefa_def['titulo']}' — executor_id para '{role}' não configurado")
                continue

            prazo = (hoje + timedelta(days=tarefa_def["dias"])).strftime("%Y-%m-%d")

            try:
                tarefa = ekyte.criar_tarefa(
                    titulo=tarefa_def["titulo"],
                    descricao=f"Tarefa automática — Sprint {nome_sprint}",
                    workspace_id=workspace_id,
                    executor_id=executor_id,
                    project_id=sprint_id,
                    prazo=prazo,
                    prioridade=200,
                )
                tarefas_criadas.append(tarefa_def["titulo"])
                print(f"    Tarefa criada: {tarefa_def['titulo']}")
            except Exception as e:
                print(f"    Erro ao criar '{tarefa_def['titulo']}': {e}")

    return {
        "sprint_criada": nome_sprint,
        "sprint_id": sprint_id,
        "tarefas_criadas": tarefas_criadas,
        "periodo": f"{inicio} → {fim}",
    }


def main():
    parser = argparse.ArgumentParser(description="Gestão de sprints Ekyte")
    parser.add_argument("--cliente", help="Nome do cliente")
    parser.add_argument("--acao", default="resumo",
                        choices=["resumo", "criar"],
                        help="resumo = relatório da sprint atual | criar = nova sprint")
    parser.add_argument("--tipo", default="ongoing",
                        choices=["onboarding", "ongoing", "replanejamento"],
                        help="Tipo de sprint para criação")
    args = parser.parse_args()

    clientes = load_clientes()

    if args.cliente:
        clientes = [c for c in clientes if c["nome"] == args.cliente]

    clientes_ekyte = [c for c in clientes if c.get("ekyte_workspace_id")]

    if not clientes_ekyte:
        print("Nenhum cliente com ekyte_workspace_id configurado.")
        return

    for cliente in clientes_ekyte:
        print(f"\n{'='*60}")
        print(f"Cliente: {cliente['nome']}")

        if args.acao == "resumo":
            resumo = resumo_sprint(cliente)
            relatorio = gerar_relatorio_sprint_claude(resumo)
            print(relatorio)

        elif args.acao == "criar":
            resultado = criar_proxima_sprint(cliente, tipo=args.tipo)
            print(f"Sprint criada: {resultado['sprint_criada']}")
            print(f"Período: {resultado['periodo']}")
            print(f"Tarefas: {len(resultado['tarefas_criadas'])}")


if __name__ == "__main__":
    main()
