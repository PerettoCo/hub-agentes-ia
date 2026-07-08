"""
briefing_criativo.py — Sob demanda (não é cron).

Gera briefing criativo completo para Copy e Design
baseado nos dados de performance do cliente.

Uso:
  python scripts/copy/briefing_criativo.py --cliente "Nome do Cliente" --objetivo "conversao" --canal "meta"

Ou via código:
  from scripts.copy.briefing_criativo import gerar_briefing
  briefing = gerar_briefing("Nome do Cliente", objetivo="conversao", canal="meta")
"""
import sys
import os
import argparse
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.connectors import (
    GoogleAdsConnector, MetaConnector,
    GmailConnector, claude, load_clientes
)

SYSTEM_COPY = """
Você é o Agente Copywriter Senior V4.

Seu papel: gerar briefings criativos completos baseados em dados reais de performance,
prontos para Copy escrever e Design produzir os assets.

Regras:
- Todo briefing tem hipótese: "esta copy vai funcionar porque [razão baseada nos dados]"
- Variações A/B obrigatórias com hipóteses DIFERENTES (não só tons diferentes)
- Use dados de performance para informar o ângulo: se CTR está baixo, o hook precisa mudar; se CPA alto, o público ou a oferta é o problema
- Seja específico: "headline de 5 palavras sobre o benefício X" é melhor que "headline impactante"
- Sempre inclua: formato, dimensões, prazo sugerido
"""


def gerar_briefing(
    nome_cliente: str,
    objetivo: str = "conversao",
    canal: str = "meta",
    enviar_email: bool = True,
) -> str:
    """
    Gera briefing criativo com dados de performance.

    Args:
        nome_cliente: nome exato do cliente em clientes.json
        objetivo: awareness | consideracao | conversao
        canal: meta | google | ambos
        enviar_email: se True, envia por Gmail para o time
    """
    clientes = load_clientes()
    cliente = next((c for c in clientes if c["nome"] == nome_cliente), None)

    if not cliente:
        raise ValueError(f"Cliente '{nome_cliente}' não encontrado em clientes.json")

    print(f"[Briefing Criativo] {nome_cliente} — {objetivo} — {canal}")

    # Coleta dados de performance
    google_data = meta_data = None

    if canal in ("google", "ambos"):
        try:
            gads = GoogleAdsConnector()
            google_data = gads.get_performance(cliente["google_ads_customer_id"], days=14)
        except Exception as e:
            print(f"  Google Ads: {e}")

    if canal in ("meta", "ambos"):
        try:
            meta_conn = MetaConnector()
            meta_data = meta_conn.get_performance(cliente["meta_ad_account_id"], days=14)
        except Exception as e:
            print(f"  Meta: {e}")

    user_prompt = f"""
Gere o briefing criativo completo para o cliente {cliente['nome']}.

Objetivo da campanha: {objetivo}
Canal: {canal}
Data: {date.today().strftime('%d/%m/%Y')}

Performance dos últimos 14 dias:
Google Ads: {google_data or 'não disponível'}
Meta Ads: {meta_data or 'não disponível'}

OKRs do cliente: {cliente['okrs']}
Vertical: {cliente.get('vertical', 'não especificado')}

Gere o briefing COMPLETO no formato:

# BRIEFING CRIATIVO — {cliente['nome']} — {date.today().strftime('%d/%m')}

## Objetivo de comunicação
[O que queremos que o público PENSE, SINTA ou FAÇA]

## Diagnóstico de performance (informa o ângulo criativo)
[O que os dados dos últimos 14 dias dizem sobre o que está funcionando ou não]
[Seja específico: CTR X%, CPM R$Y, ROAS Z — e o que isso significa para o criativo]

## Público-alvo
- Quem é: [perfil]
- Dor principal: [dor]
- Objeção que precisa ser quebrada: [objeção]
- Linguagem: [formal/informal/técnico/emocional]

## Proposta de valor central
[Uma frase — o porquê de escolher este cliente]

## VARIAÇÃO A — [hipótese A]
**Ângulo:** [foco na dor / benefício / prova social / urgência]
**Hook/Headline:** [máx 6 palavras]
**Copy principal:** [2-4 linhas]
**CTA:** [ação específica]
**Por que vai funcionar:** [baseado nos dados de performance]

## VARIAÇÃO B — [hipótese B — ângulo diferente da A]
**Ângulo:** [ângulo diferente]
**Hook/Headline:** [máx 6 palavras]
**Copy principal:** [2-4 linhas]
**CTA:** [ação específica]
**Por que vai funcionar:** [baseado nos dados de performance]

## Entregáveis desta sprint
- [ ] 2 estáticos (1080x1080 + 1080x1920) — Prazo: [X dias úteis]
- [ ] 1 vídeo 15-30s — Prazo: [X dias úteis]
- [ ] Copy para conjunto de anúncios — Prazo: [X dias úteis]

## Critério de decisão A/B
Pausar variação com CTR < [X]% após [N] impressões.
"""

    briefing = claude(SYSTEM_COPY, user_prompt, max_tokens=1200)

    if enviar_email:
        gmail = GmailConnector()
        html = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto;
             color: #333; padding: 20px;">
<h2 style="color: #1a1a1a;">Briefing Criativo — {nome_cliente}</h2>
<p style="color: #666; font-size: 13px;">
  Gerado em {date.today().strftime('%d/%m/%Y')} com dados de performance dos últimos 14 dias.
</p>
<div style="background: #f9f9f9; padding: 20px; border-radius: 8px;
            white-space: pre-wrap; font-size: 13px; line-height: 1.7;">
{briefing}
</div>
<hr style="margin: 24px 0; border: none; border-top: 1px solid #e0e0e0;">
<p style="color: #999; font-size: 12px;">V4 Automations — Briefing sob demanda.</p>
</body>
</html>
"""
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent.parent / "config" / ".env")

        gmail.send(
            to=[os.getenv("EMAIL_AM"), os.getenv("EMAIL_GT")],
            subject=f"Briefing Criativo — {nome_cliente} — {date.today().strftime('%d/%m')}",
            body_html=html,
        )
        print(f"  Email enviado para AM e GT.")

    print(f"[Briefing Criativo] Concluído.")
    return briefing


def main():
    parser = argparse.ArgumentParser(description="Gera briefing criativo com dados de performance")
    parser.add_argument("--cliente", required=True, help="Nome do cliente (exato como em clientes.json)")
    parser.add_argument("--objetivo", default="conversao", choices=["awareness", "consideracao", "conversao"])
    parser.add_argument("--canal", default="meta", choices=["meta", "google", "ambos"])
    parser.add_argument("--no-email", action="store_true", help="Não envia email")

    args = parser.parse_args()

    briefing = gerar_briefing(
        nome_cliente=args.cliente,
        objetivo=args.objetivo,
        canal=args.canal,
        enviar_email=not args.no_email,
    )

    print("\n" + "="*60)
    print(briefing)


if __name__ == "__main__":
    main()
