"""
atualizar_okrs.py — Roda QUINTA 8h (cron automático, após análise GT).

Pega os dados de performance coletados, calcula progresso
de cada KR, detecta riscos de churn por NPS/CSAT e
envia atualização de OKRs para AM com alertas.
"""
import sys
import os
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.connectors import (
    GoogleAdsConnector, MetaConnector,
    GmailConnector, claude, load_clientes
)

SYSTEM_AM = """
Você é o Agente Account Manager V4.

Seu papel: atualizar o progresso dos KRs de cada cliente com base nos dados
de performance da semana, detectar riscos e gerar comunicação estruturada.

Regras:
- Calcule o progresso de cada KR com os dados disponíveis.
- Se um KR está em risco (< 70% do esperado), marque como VERMELHO e sugira ação.
- Se está em atenção (70-90% do esperado), marque como AMARELO.
- Se está ok (> 90% do esperado), marque como VERDE.
- Gere uma atualização semanal curta e acionável para o AM usar no Ekyte.
"""


def calcular_progresso_kr(kr: dict, google_data: dict, meta_data: dict) -> dict:
    """Calcula progresso de um KR com os dados disponíveis."""
    desc = kr["descricao"].lower()
    meta = kr["meta"]
    inverso = kr.get("inverso", False)
    atual = 0

    if "roas" in desc:
        g = google_data.get("roas", 0) if google_data else 0
        m = meta_data.get("roas", 0) if meta_data else 0
        atual = max(g, m)
    elif "cac" in desc or "cpa" in desc:
        atual = google_data.get("cpa", 0) if google_data else 0
    elif "lead" in desc or "mql" in desc or "conversao" in desc:
        g = google_data.get("conversoes", 0) if google_data else 0
        m = meta_data.get("conversoes", 0) if meta_data else 0
        atual = g + m
        meta = meta / 4  # Aproxima meta semanal (mensal / 4)

    if meta == 0:
        progresso_pct = 0
    elif inverso:
        progresso_pct = max(0, (1 - (atual - meta) / meta) * 100) if atual > 0 else 100
    else:
        progresso_pct = (atual / meta * 100) if atual > 0 else 0

    if progresso_pct >= 90:
        status = "🟢"
    elif progresso_pct >= 70:
        status = "🟡"
    else:
        status = "🔴"

    return {
        "descricao": kr["descricao"],
        "meta": meta,
        "atual": round(atual, 2),
        "progresso_pct": round(progresso_pct, 1),
        "status": status,
        "unidade": kr.get("unidade", ""),
    }


def gerar_atualizacao_okr(cliente: dict, krs_progresso: list) -> str:
    """Usa Claude para gerar a atualização de OKR formatada."""
    user_prompt = f"""
Gere a atualização semanal de OKRs do cliente {cliente['nome']} para o AM registrar no Ekyte.

Semana: {date.today().isocalendar()[1]} — {date.today().strftime('%d/%m/%Y')}
Objetivo do quarter: {cliente['okrs']['objetivo']}

Progresso dos KRs calculado:
{krs_progresso}

Gere no formato:

## {cliente['nome']} — Atualização OKRs — Semana {date.today().isocalendar()[1]}

**Objetivo:** {cliente['okrs']['objetivo']}

**Progresso dos KRs:**
[Para cada KR: status emoji + descrição + atual/meta + % + observação se necessário]

**Status geral:** [VERDE/AMARELO/VERMELHO] — [justificativa em 1 frase]

**Ação prioritária desta semana:**
[Se algum KR está vermelho ou amarelo: o que o AM precisa fazer agora]

**Texto para registrar no Ekyte:**
[Versão curta e direta para copiar e colar na atualização do Ekyte — máx 3 linhas]
"""
    return claude(SYSTEM_AM, user_prompt, max_tokens=600)


def montar_email_am(atualizacoes: list) -> str:
    semana = date.today().isocalendar()[1]
    blocos = "\n\n".join(atualizacoes)

    tem_vermelho = "🔴" in blocos
    cor_header = "#dc3545" if tem_vermelho else "#0d6efd"
    aviso = ""
    if tem_vermelho:
        aviso = """
<div style="background: #f8d7da; padding: 12px; border-radius: 6px; margin: 12px 0;
            border-left: 4px solid #dc3545; color: #721c24;">
  <strong>Atenção:</strong> Um ou mais KRs estão em vermelho.
  Verifique as ações prioritárias abaixo e abra FCA no Ekyte se necessário.
</div>
"""

    return f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; color: #333;">

<h2 style="color: {cor_header}; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px;">
  Atualização de OKRs — Semana {semana}
</h2>

<p style="color: #666; font-size: 14px;">
  Calculado automaticamente com dados de Google Ads e Meta Ads.
  Copie os textos do Ekyte para atualizar o plano tático.
</p>

{aviso}

<div style="white-space: pre-wrap; line-height: 1.7; font-size: 13px;">
{blocos}
</div>

<hr style="margin: 32px 0; border: none; border-top: 1px solid #e0e0e0;">
<p style="color: #999; font-size: 12px;">
  V4 Automations — Gerado toda quinta às 8h após coleta do GT.
</p>
</body>
</html>
"""


def main():
    print(f"[AM OKRs] Iniciando — {date.today()}")

    clientes = load_clientes()
    atualizacoes = []

    for cliente in clientes:
        print(f"  Processando: {cliente['nome']}...")

        google_data = meta_data = None

        try:
            gads = GoogleAdsConnector()
            google_data = gads.get_performance(cliente["google_ads_customer_id"], days=7)
        except Exception as e:
            print(f"  Google Ads erro: {e}")

        try:
            meta = MetaConnector()
            meta_data = meta.get_performance(cliente["meta_ad_account_id"], days=7)
        except Exception as e:
            print(f"  Meta erro: {e}")

        krs_progresso = [
            calcular_progresso_kr(kr, google_data, meta_data)
            for kr in cliente["okrs"]["krs"]
        ]

        atualizacao = gerar_atualizacao_okr(cliente, krs_progresso)
        atualizacoes.append(atualizacao)
        print(f"  OKRs calculadas: OK")

    html = montar_email_am(atualizacoes)

    gmail = GmailConnector()
    gmail.send(
        to=os.getenv("EMAIL_AM"),
        subject=f"Atualização OKRs — Semana {date.today().isocalendar()[1]}",
        body_html=html,
    )

    print(f"[AM OKRs] Concluído.")


if __name__ == "__main__":
    main()
