"""
enviar_nps.py — Roda DIA 1 DE CADA MÊS às 8h (cron automático).

Envia pesquisa de NPS e CSAT para cada cliente ativo
via Gmail com link personalizado e registra o envio.
"""
import sys
import os
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.connectors import GmailConnector, claude, load_clientes

SYSTEM_AM = """
Você é o Agente Account Manager V4.
Escreva emails de pesquisa NPS/CSAT humanizados, diretos e que gerem alta taxa de resposta.
Tom: próximo, não corporativo. Curto. Claro. Fácil de responder.
"""

# URL base da pesquisa — substitua pelo seu formulário Google Forms ou Typeform
# Use {cliente_nome} como placeholder que será substituído
NPS_FORM_URL = "https://forms.gle/SEU_FORM_ID_AQUI"
CSAT_FORM_URL = "https://forms.gle/SEU_FORM_ID_AQUI"


def gerar_email_nps(cliente: dict, am_nome: str = "Time V4") -> tuple[str, str]:
    """Gera assunto e corpo do email NPS para o cliente."""
    mes = date.today().strftime("%B/%Y")

    user_prompt = f"""
Escreva um email curto de pesquisa NPS + CSAT para o cliente {cliente['nome']}.

Contexto:
- Somos a agência de marketing digital deles
- Estamos pedindo avaliação mensal de satisfação
- Mês de referência: {mes}
- NPS: "De 0 a 10, qual a probabilidade de indicar nossa agência?"
- CSAT: "De 1 a 5, como avalia a qualidade das entregas deste mês?"

Links:
- Pesquisa NPS: {NPS_FORM_URL}
- Pesquisa CSAT: {CSAT_FORM_URL}

Regras:
- Máximo 5 linhas no corpo
- Tom próximo, não formal
- Deixe claro que leva menos de 2 minutos
- Assine como {am_nome}

Gere:
ASSUNTO: [linha de assunto]
CORPO: [email completo em HTML simples]
"""

    resposta = claude(SYSTEM_AM, user_prompt, max_tokens=400)

    # Extrai assunto e corpo
    linhas = resposta.strip().split("\n")
    assunto = ""
    corpo_linhas = []
    modo_corpo = False

    for linha in linhas:
        if linha.startswith("ASSUNTO:"):
            assunto = linha.replace("ASSUNTO:", "").strip()
        elif linha.startswith("CORPO:"):
            modo_corpo = True
        elif modo_corpo:
            corpo_linhas.append(linha)

    corpo = "\n".join(corpo_linhas).strip()

    if not assunto:
        assunto = f"Sua opinião importa — {mes}"
    if not corpo:
        corpo = f"""
<p>Olá!</p>
<p>Gostaríamos de saber como foi nossa parceria em {mes}.</p>
<p>
  <a href="{NPS_FORM_URL}">Pesquisa NPS (1 pergunta)</a> — leva 30 segundos.<br>
  <a href="{CSAT_FORM_URL}">Pesquisa CSAT (1 pergunta)</a> — leva 30 segundos.
</p>
<p>Obrigado!<br>{am_nome}</p>
"""

    return assunto, corpo


def montar_email_html(corpo: str, cliente_nome: str) -> str:
    return f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;
             color: #333; line-height: 1.6; padding: 20px;">
{corpo}
<hr style="margin: 24px 0; border: none; border-top: 1px solid #e0e0e0;">
<p style="color: #999; font-size: 11px;">
  Você recebe este email pois é cliente da V4 Company — Squad Mata Leão.<br>
  Suas respostas são anônimas e usadas apenas para melhorar nosso serviço.
</p>
</body>
</html>
"""


def main():
    print(f"[NPS/CSAT] Iniciando envio — {date.today()}")

    clientes = load_clientes()
    gmail = GmailConnector()

    enviados = 0
    erros = 0

    for cliente in clientes:
        if not cliente.get("email_cliente"):
            print(f"  {cliente['nome']}: sem email configurado — pulando")
            continue

        try:
            assunto, corpo = gerar_email_nps(cliente)
            html = montar_email_html(corpo, cliente["nome"])

            gmail.send(
                to=cliente["email_cliente"],
                subject=assunto,
                body_html=html,
            )

            enviados += 1
            print(f"  {cliente['nome']}: enviado para {cliente['email_cliente']}")

        except Exception as e:
            erros += 1
            print(f"  {cliente['nome']}: ERRO — {e}")

    # Notifica AM sobre os envios
    gmail.send(
        to=os.getenv("EMAIL_AM"),
        subject=f"NPS/CSAT enviados — {date.today().strftime('%B/%Y')}",
        body_html=f"""
<html><body style="font-family: Arial, sans-serif; color: #333; padding: 20px;">
<h3>Pesquisas NPS/CSAT enviadas</h3>
<p>Mês: {date.today().strftime('%B/%Y')}</p>
<p>Enviados: <strong>{enviados}</strong> | Erros: <strong>{erros}</strong></p>
<p>Acompanhe as respostas nos formulários e atualize o checklist de conformidade.</p>
<p style="color: #999; font-size: 12px;">V4 Automations — gerado automaticamente dia 1 de cada mês.</p>
</body></html>
""",
    )

    print(f"[NPS/CSAT] Concluído. Enviados: {enviados} | Erros: {erros}")


if __name__ == "__main__":
    main()
