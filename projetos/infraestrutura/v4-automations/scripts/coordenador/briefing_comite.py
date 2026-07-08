"""
briefing_comite.py — Roda DOMINGO 20h (cron automático).

Coleta dados de todos os clientes, cruza pace vs OKR,
gera hipóteses com Claude e envia briefing por email para
AM e Coordenador antes do Comitê de segunda.
"""
import sys
import os
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.connectors import (
    GoogleAdsConnector, MetaConnector, GA4Connector,
    GmailConnector, claude, load_clientes
)

SYSTEM_COORDENADOR = """
Você é o Agente Coordenador da Squad Mata Leão V4.

Seu papel: analisar dados de performance e pace de verba de cada cliente,
cruzar com as OKRs do quarter, identificar desvios e gerar hipóteses acionáveis
para o Comitê de P&EG de segunda-feira.

Regras:
- Seja direto. Coordenador não precisa de introdução, só de diagnóstico.
- Para cada cliente: status (verde/amarelo/vermelho), desvio principal, hipótese, ação sugerida.
- Se estiver tudo ok, diga isso com os dados que confirmam.
- Formato: estruturado, escaneável, pronto para o AM facilitar a reunião.
- Máximo 3 ações por cliente — foco no que mais importa.
- Use FCA quando houver desvio (Fato → Causa → Ação).
"""


def coletar_dados_cliente(cliente: dict) -> dict:
    """Coleta dados de todas as fontes para um cliente."""
    print(f"  Coletando dados: {cliente['nome']}...")

    dados = {"nome": cliente["nome"], "okrs": cliente["okrs"], "erros": []}

    try:
        gads = GoogleAdsConnector()
        dados["google_ads_semana"] = gads.get_performance(cliente["google_ads_customer_id"], days=7)
        dados["google_ads_pace"] = gads.get_pace(cliente["google_ads_customer_id"], cliente["verba_mensal"] * 0.5)
    except Exception as e:
        dados["erros"].append(f"Google Ads: {e}")
        dados["google_ads_semana"] = None
        dados["google_ads_pace"] = None

    try:
        meta = MetaConnector()
        dados["meta_semana"] = meta.get_performance(cliente["meta_ad_account_id"], days=7)
    except Exception as e:
        dados["erros"].append(f"Meta Ads: {e}")
        dados["meta_semana"] = None

    try:
        ga4 = GA4Connector()
        dados["ga4_semana"] = ga4.get_performance(cliente["ga4_property_id"], days=7)
    except Exception as e:
        dados["erros"].append(f"GA4: {e}")
        dados["ga4_semana"] = None

    return dados


def gerar_analise_cliente(dados: dict) -> str:
    """Usa Claude para gerar análise de um cliente."""
    user_prompt = f"""
Analise os dados abaixo do cliente {dados['nome']} e gere o bloco de briefing para o Comitê de segunda.

OKRs do quarter:
{dados['okrs']}

Performance Google Ads (últimos 7 dias):
{dados.get('google_ads_semana') or 'Dados indisponíveis'}

Pace de verba Google Ads:
{dados.get('google_ads_pace') or 'Dados indisponíveis'}

Performance Meta Ads (últimos 7 dias):
{dados.get('meta_semana') or 'Dados indisponíveis'}

GA4 — Sessões e conversão (últimos 7 dias):
{dados.get('ga4_semana') or 'Dados indisponíveis'}

Erros de coleta (se houver):
{dados['erros'] if dados['erros'] else 'Nenhum'}

Gere o bloco de briefing seguindo este formato exato:

## [NOME DO CLIENTE] — [VERDE/AMARELO/VERMELHO]

**Status geral:** [uma frase com o diagnóstico principal]

**KRs em progresso:**
- KR1: [valor atual] / meta [valor meta] → [%] — [status]
- KR2: [valor atual] / meta [valor meta] → [%] — [status]

**Pace de verba:** [gasto atual] / [esperado] ([diferença em %]) — [ok/acima/abaixo]

**Principal desvio identificado:**
FATO: [dado objetivo]
CAUSA: [análise — 1-2 frases]
AÇÃO: [o que fazer, quem, quando]

**Outras ações para a semana:**
1. [ação]
2. [ação]
"""
    return claude(SYSTEM_COORDENADOR, user_prompt, max_tokens=800)


def montar_email(analises: list[str], data_comite: str) -> str:
    """Monta o HTML do email de briefing."""
    blocos = "\n\n".join(analises)

    return f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; color: #333;">

<h2 style="color: #1a1a1a; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px;">
  Briefing Comitê P&EG — {data_comite}
</h2>

<p style="color: #666; font-size: 14px;">
  Gerado automaticamente na noite de domingo. Dados coletados de Google Ads, Meta Ads e GA4.
  Revise, ajuste e use como base para facilitar o Comitê.
</p>

<div style="background: #f9f9f9; padding: 16px; border-radius: 8px; margin: 16px 0;">
  <strong>Legenda de status:</strong>
  🟢 KRs on track, pace ok &nbsp;|&nbsp;
  🟡 Atenção — desvio identificado &nbsp;|&nbsp;
  🔴 Crítico — ação imediata necessária
</div>

<div style="white-space: pre-wrap; line-height: 1.6;">
{blocos}
</div>

<hr style="margin: 32px 0; border: none; border-top: 1px solid #e0e0e0;">
<p style="color: #999; font-size: 12px;">
  V4 Automations — Squad Mata Leão &nbsp;|&nbsp;
  Este email é gerado automaticamente todo domingo às 20h.
</p>

</body>
</html>
"""


def main():
    print(f"[Briefing Comitê] Iniciando — {date.today()}")

    clientes = load_clientes()
    analises = []

    for cliente in clientes:
        try:
            dados = coletar_dados_cliente(cliente)
            analise = gerar_analise_cliente(dados)
            analises.append(analise)
            print(f"  Análise concluída: {cliente['nome']}")
        except Exception as e:
            analises.append(f"## {cliente['nome']} — ERRO\n\nFalha na coleta: {e}")
            print(f"  ERRO em {cliente['nome']}: {e}")

    # Monta e envia o email
    data_comite = "Segunda-feira"
    html = montar_email(analises, data_comite)

    gmail = GmailConnector()
    destinatarios = [
        os.getenv("EMAIL_COORDENADOR"),
        os.getenv("EMAIL_AM"),
    ]
    gmail.send(
        to=destinatarios,
        subject=f"Briefing Comitê P&EG — {date.today().strftime('%d/%m')}",
        body_html=html,
    )

    print(f"[Briefing Comitê] Concluído. Email enviado para {destinatarios}")


if __name__ == "__main__":
    main()
