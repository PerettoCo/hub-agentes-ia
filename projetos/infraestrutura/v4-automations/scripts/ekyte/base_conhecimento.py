"""
base_conhecimento.py — Popula a Base de Conhecimento do Ekyte automaticamente.

Usos:
  1. Salvar atas de rituais (Comitê, Growth, Working Backwards)
  2. Salvar análises de performance como notas
  3. Salvar account planning gerado pelo agente AM
  4. Listar e consultar notas existentes

Uso:
  python scripts/ekyte/base_conhecimento.py --acao listar
  python scripts/ekyte/base_conhecimento.py --acao salvar-ata --ritual comite --cliente "Nome"
"""
import sys
import argparse
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.ekyte.connector import EkyteClient
from scripts.connectors import load_clientes, claude

SYSTEM_AM = """
Você é o Agente Account Manager V4.
Formate atas e análises de forma estruturada, clara e pronta para ser salva
na Base de Conhecimento do Ekyte.
"""

# IDs dos quadros no Ekyte — preencha após criar os quadros lá
# Ekyte → Base de Conhecimento → URL contém o ID do quadro
QUADROS_EKYTE = {
    "atas_comite": None,       # Quadro: Atas Comitê P&EG
    "atas_growth": None,       # Quadro: Atas Growth
    "atas_wb": None,           # Quadro: Atas Working Backwards
    "account_planning": None,  # Quadro: Account Planning
    "analises": None,          # Quadro: Análises de Performance
    "okrs": None,              # Quadro: OKRs e Plano Tático
}


def listar_base(workspace_id: int = None) -> list:
    """Lista quadros e notas existentes na base de conhecimento."""
    ekyte = EkyteClient()
    quadros = ekyte.get_base_conhecimento(workspace_id=workspace_id)
    print(f"\nBase de Conhecimento — {len(quadros)} quadros encontrados:")
    for q in quadros:
        print(f"  ID: {q.get('id')} — {q.get('name') or q.get('title', '?')}")
    return quadros


def salvar_ata_comite(
    cliente_nome: str,
    decisoes: str,
    fcas_abertas: str,
    priorizacao: str,
    acoes: str,
    quadro_id: int = None,
) -> dict:
    """
    Salva ata do Comitê P&EG na Base de Conhecimento.
    CONFIRMAR com suporte Ekyte se POST /boards/notes está disponível.
    """
    ekyte = EkyteClient()
    qid = quadro_id or QUADROS_EKYTE.get("atas_comite")

    if not qid:
        print("  AVISO: quadro_id não configurado para atas_comite.")
        print("  Configure QUADROS_EKYTE['atas_comite'] com o ID do quadro no Ekyte.")
        return {"criado": False, "motivo": "quadro_id não configurado"}

    titulo = f"Ata Comitê P&EG — {cliente_nome} — {date.today().strftime('%d/%m/%Y')}"
    conteudo = f"""
Data: {date.today().strftime('%d/%m/%Y')}
Cliente: {cliente_nome}

DECISÕES TOMADAS:
{decisoes}

FCAs ABERTAS/FECHADAS:
{fcas_abertas}

PRIORIZAÇÃO DE CLIENTES:
{priorizacao}

AÇÕES + DONOS + PRAZOS:
{acoes}
""".strip()

    return ekyte.criar_nota_base(
        titulo=titulo,
        conteudo=conteudo,
        quadro_id=qid,
        categoria="Atas",
    )


def salvar_ata_growth(
    cliente_nome: str,
    diagnostico: str,
    sprint_acao: str,
    dono_prazo: str,
    quadro_id: int = None,
) -> dict:
    """Salva ata de Growth na Base de Conhecimento."""
    ekyte = EkyteClient()
    qid = quadro_id or QUADROS_EKYTE.get("atas_growth")

    if not qid:
        print("  AVISO: quadro_id não configurado para atas_growth.")
        return {"criado": False}

    titulo = f"Growth — {cliente_nome} — {date.today().strftime('%d/%m/%Y')}"
    conteudo = f"""
Data: {date.today().strftime('%d/%m/%Y')}
Cliente discutido: {cliente_nome}

DIAGNÓSTICO DO DESVIO:
{diagnostico}

SPRINT / AÇÃO DEFINIDA:
{sprint_acao}

DONO DA EXECUÇÃO + PRAZO:
{dono_prazo}
""".strip()

    return ekyte.criar_nota_base(
        titulo=titulo,
        conteudo=conteudo,
        quadro_id=qid,
        categoria="Atas Growth",
    )


def salvar_ata_working_backwards(
    alinhado: str,
    nao_alinhado: str,
    mudancas: str,
    quadro_id: int = None,
) -> dict:
    """Salva ata do Working Backwards na Base de Conhecimento."""
    ekyte = EkyteClient()
    qid = quadro_id or QUADROS_EKYTE.get("atas_wb")

    if not qid:
        print("  AVISO: quadro_id não configurado para atas_wb.")
        return {"criado": False}

    titulo = f"Working Backwards — {date.today().strftime('%d/%m/%Y')}"
    conteudo = f"""
Data: {date.today().strftime('%d/%m/%Y')}

O QUE FIZEMOS ALINHADO ÀS PREMISSAS:
{alinhado}

O QUE NÃO ESTAVA ALINHADO:
{nao_alinhado}

O QUE MUDA NA PRÓXIMA SEMANA:
{mudancas}
""".strip()

    return ekyte.criar_nota_base(
        titulo=titulo,
        conteudo=conteudo,
        quadro_id=qid,
        categoria="Retrospectiva",
    )


def salvar_analise_performance(
    cliente_nome: str,
    analise_texto: str,
    quadro_id: int = None,
) -> dict:
    """Salva análise de performance semanal na Base de Conhecimento."""
    ekyte = EkyteClient()
    qid = quadro_id or QUADROS_EKYTE.get("analises")

    if not qid:
        print("  AVISO: quadro_id não configurado para analises.")
        return {"criado": False}

    semana = date.today().isocalendar()[1]
    titulo = f"Performance Semana {semana} — {cliente_nome}"

    return ekyte.criar_nota_base(
        titulo=titulo,
        conteudo=analise_texto,
        quadro_id=qid,
        categoria=f"Semana {semana}",
    )


def salvar_okrs(
    cliente_nome: str,
    objetivo: str,
    krs: list,
    quadro_id: int = None,
) -> dict:
    """Salva atualização de OKRs na Base de Conhecimento."""
    ekyte = EkyteClient()
    qid = quadro_id or QUADROS_EKYTE.get("okrs")

    if not qid:
        print("  AVISO: quadro_id não configurado para okrs.")
        return {"criado": False}

    semana = date.today().isocalendar()[1]
    titulo = f"OKRs Semana {semana} — {cliente_nome}"

    linhas_krs = []
    for kr in krs:
        linhas_krs.append(
            f"KR: {kr.get('descricao')}\n"
            f"  Meta: {kr.get('meta')} | Atual: {kr.get('atual')} | "
            f"Progresso: {kr.get('progresso_pct', 0)}% {kr.get('status', '')}"
        )

    conteudo = f"""
Data: {date.today().strftime('%d/%m/%Y')} — Semana {semana}
Cliente: {cliente_nome}

OBJETIVO:
{objetivo}

KEY RESULTS:
{chr(10).join(linhas_krs)}
""".strip()

    return ekyte.criar_nota_base(
        titulo=titulo,
        conteudo=conteudo,
        quadro_id=qid,
        categoria="OKRs",
    )


def gerar_ata_com_claude(tipo_ritual: str, contexto: str) -> str:
    """Usa Claude para gerar ata estruturada a partir de notas brutas."""
    user_prompt = f"""
Formate a ata do ritual {tipo_ritual} com base nas notas abaixo.
Siga o formato padrão V4 — objetivo, direto, pronto para salvar no Ekyte.

Notas brutas:
{contexto}

Gere a ata completa e estruturada.
"""
    return claude(SYSTEM_AM, user_prompt, max_tokens=500)


def main():
    parser = argparse.ArgumentParser(description="Base de Conhecimento Ekyte")
    parser.add_argument("--acao", required=True,
                        choices=["listar", "salvar-ata", "salvar-analise"],
                        help="Ação a executar")
    parser.add_argument("--ritual", choices=["comite", "growth", "wb"],
                        help="Tipo de ritual (para salvar-ata)")
    parser.add_argument("--cliente", help="Nome do cliente")
    parser.add_argument("--workspace", type=int, help="ID do workspace no Ekyte")
    args = parser.parse_args()

    if args.acao == "listar":
        listar_base(workspace_id=args.workspace)

    elif args.acao == "salvar-ata":
        if not args.ritual:
            print("Informe --ritual: comite | growth | wb")
            return

        print(f"Digite as notas brutas do ritual (Ctrl+D para finalizar):")
        try:
            notas = sys.stdin.read()
        except KeyboardInterrupt:
            return

        ata = gerar_ata_com_claude(args.ritual, notas)
        print("\nAta gerada:")
        print(ata)
        print("\nSalvando no Ekyte...")

        if args.ritual == "comite":
            resultado = salvar_ata_comite(
                cliente_nome=args.cliente or "Squad Mata Leão",
                decisoes=ata,
                fcas_abertas="(ver conteúdo da ata)",
                priorizacao="(ver conteúdo da ata)",
                acoes="(ver conteúdo da ata)",
            )
        elif args.ritual == "growth":
            resultado = salvar_ata_growth(
                cliente_nome=args.cliente or "?",
                diagnostico=ata,
                sprint_acao="(ver conteúdo da ata)",
                dono_prazo="(ver conteúdo da ata)",
            )
        elif args.ritual == "wb":
            resultado = salvar_ata_working_backwards(
                alinhado=ata,
                nao_alinhado="(ver conteúdo da ata)",
                mudancas="(ver conteúdo da ata)",
            )

        print(f"Resultado: {resultado}")


if __name__ == "__main__":
    main()
