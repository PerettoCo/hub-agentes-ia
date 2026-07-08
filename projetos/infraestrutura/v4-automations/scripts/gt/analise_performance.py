"""
analise_performance.py — Roda QUINTA 7h (cron automático).

Coleta dados de todos os clientes, detecta anomalias vs metas,
gera CHAS automaticamente para cada desvio e envia relatório
para GT e AM antes dos Growths da semana.
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

SYSTEM_GT = """
Você é o Agente Gestor de Tráfego Senior V4.

Seu papel: analisar dados de performance de mídia, detectar desvios vs metas,
e gerar diagnósticos CHAS prontos para o GT revisar e usar nos Growths da semana.

Regras:
- Seja técnico e preciso. O GT precisa de dados, não de narrativa.
- Para cada desvio: gere um CHAS completo (Context, Hypothesis, Action, Success).
- Priorize desvios por impacto no ROI do cliente.
- Se a performance está ok, confirme com os dados e aponte o que monitorar.
- Cada ação deve ter um responsável (GT, Copy, Design, AM) e prazo em dias.
"""


def detectar_desvios(cliente: dict, google_data: dict, meta_data: dict, ga4_data: dict) -> list:
    """Detecta desvios vs metas dos KRs do cliente."""
    desvios = []
    okrs = cliente["okrs"]["krs"]

    for kr in okrs:
        meta = kr["meta"]
        inverso = kr.get("inverso", False)

        # Tenta mapear KR para métrica coletada
        desc = kr["descricao"].lower()

        if "roas" in desc:
            valor = None
            if google_data: valor = google_data.get("roas", 0)
            if meta_data and (valor is None or valor == 0):
                valor = meta_data.get("roas", 0)
            if valor is not None:
                desvio_pct = ((valor - meta) / meta) * 100
                if abs(desvio_pct) > 10:
                    desvios.append({
                        "kr": kr["descricao"],
                        "meta": meta,
                        "atual": valor,
                        "desvio_pct": round(desvio_pct, 1),
                        "critico": abs(desvio_pct) > 25,
                    })

        elif "cac" in desc or "cpa" in desc:
            valor = None
            if google_data: valor = google_data.get("cpa", 0)
            if valor and valor > 0:
                desvio_pct = ((valor - meta) / meta) * 100
                if inverso and desvio_pct > 10:
                    desvios.append({
                        "kr": kr["descricao"],
                        "meta": meta,
                        "atual": valor,
                        "desvio_pct": round(desvio_pct, 1),
                        "critico": desvio_pct > 25,
                    })

        elif "lead" in desc or "mql" in desc:
            if google_data and meta_data:
                total_conv = (google_data.get("conversoes", 0) or 0) + (meta_data.get("conversoes", 0) or 0)
                meta_semanal = meta / 4
                desvio_pct = ((total_conv - meta_semanal) / meta_semanal) * 100
                if abs(desvio_pct) > 15:
                    desvios.append({
                        "kr": kr["descricao"],
                        "meta": round(meta_semanal, 0),
                        "atual": round(total_conv, 1),
                        "desvio_pct": round(desvio_pct, 1),
                        "critico": abs(desvio_pct) > 30,
                    })

    return desvios


def gerar_chas(cliente: dict, desvios: list, google_data: dict, meta_data: dict, ga4_data: dict) -> str:
    """Usa Claude para gerar análise CHAS completa."""

    user_prompt = f"""
Analise os dados de performance do cliente {cliente['nome']} e gere o relatório de GT para os Growths desta semana.

DADOS COLETADOS (últimos 7 dias):

Google Ads: {google_data or 'indisponível'}
Meta Ads: {meta_data or 'indisponível'}
GA4: {ga4_data or 'indisponível'}

DESVIOS DETECTADOS VS METAS:
{desvios if desvios else 'Nenhum desvio significativo detectado.'}

OKRs do cliente:
{cliente['okrs']}

Gere o relatório seguindo este formato:

## {cliente['nome']} — Performance da Semana

**Resumo executivo:** [1 frase com o diagnóstico principal]

**KPIs da semana:**
| Métrica | Valor | Meta | Status |
|---------|-------|------|--------|
[preencha com os dados disponíveis]

{'**CHAS — Análise de Desvio:**' if desvios else '**Situação:** Performance dentro do esperado.'}

{'''Para cada desvio identificado, gere um CHAS:

CONTEXT: [o que está acontecendo com dados específicos]
HYPOTHESIS: "[métrica] está assim porque [causa provável baseada nos dados]" — Confiança: High/Medium/Low
ACTION: [ação específica] — Responsável: [GT/Copy/Design/AM] — Prazo: [X dias]
SUCCESS: "Se conseguir [X], confirmamos que [conclusão]"''' if desvios else ''}

**O que monitorar esta semana:**
1. [métrica + threshold de alerta]
2. [métrica + threshold de alerta]

**Preparação para os Growths:**
[qual cliente priorizar, qual dado levar, qual hipótese apresentar]
"""

    return claude(SYSTEM_GT, user_prompt, max_tokens=1000)


def montar_email_gt(analises: list[tuple]) -> str:
    """Monta HTML do email de performance."""
    semana = date.today().isocalendar()[1]
    blocos_html = ""

    for nome, analise, tem_desvio in analises:
        cor_borda = "#dc3545" if tem_desvio else "#28a745"
        blocos_html += f"""
<div style="border-left: 4px solid {cor_borda}; padding: 16px; margin: 16px 0;
            background: #fafafa; border-radius: 0 8px 8px 0;">
<pre style="white-space: pre-wrap; font-family: Arial, sans-serif; font-size: 13px; margin: 0;">
{analise}
</pre>
</div>
"""

    return f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; color: #333;">

<h2 style="color: #1a1a1a; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px;">
  Análise de Performance — Semana {semana}
</h2>

<p style="color: #666; font-size: 14px;">
  Relatório automático gerado toda quinta às 7h.
  Revise os CHA(S) antes dos Growths de hoje, amanhã e sexta.
</p>

{blocos_html}

<hr style="margin: 32px 0; border: none; border-top: 1px solid #e0e0e0;">
<p style="color: #999; font-size: 12px;">
  V4 Automations — Squad Mata Leão &nbsp;|&nbsp;
  Gerado automaticamente toda quinta às 7h.
</p>
</body>
</html>
"""


def main():
    print(f"[GT Análise] Iniciando — {date.today()}")

    clientes = load_clientes()
    analises = []

    for cliente in clientes:
        print(f"  Processando: {cliente['nome']}...")

        google_data = meta_data = ga4_data = None

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

        try:
            ga4 = GA4Connector()
            ga4_data = ga4.get_performance(cliente["ga4_property_id"], days=7)
        except Exception as e:
            print(f"  GA4 erro: {e}")

        desvios = detectar_desvios(cliente, google_data, meta_data, ga4_data)
        analise = gerar_chas(cliente, desvios, google_data, meta_data, ga4_data)
        analises.append((cliente["nome"], analise, len(desvios) > 0))

        print(f"  Desvios: {len(desvios)} | Análise: OK")

    html = montar_email_gt(analises)

    gmail = GmailConnector()
    gmail.send(
        to=[os.getenv("EMAIL_GT"), os.getenv("EMAIL_AM")],
        subject=f"Análise de Performance — Semana {date.today().isocalendar()[1]}",
        body_html=html,
    )

    print(f"[GT Análise] Concluído.")


if __name__ == "__main__":
    main()
