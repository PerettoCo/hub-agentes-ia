"""
checklist.py — Roda SEXTA 16h (cron automático).

Gera o checklist de conformidade semanal S/N, identifica
itens N, e envia por email para o Coordenador com pautas
já priorizadas para o Comitê de segunda.

Nota: os itens de onboarding e ongoing dependem de uma planilha
ou doc no Drive com o status de cada cliente. Configure o
DRIVE_STATUS_DOC_ID no .env para integração automática.
Sem o doc, o checklist é gerado com campos para preenchimento manual.
"""
import sys
import os
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.connectors import GmailConnector, claude, load_clientes

# Integração Ekyte — opcional
# Se EKYTE_API_KEY estiver configurada, enriquece o checklist com dados reais
try:
    from scripts.ekyte.checklist_ekyte import verificar_conformidade_ekyte, formatar_checklist_texto
    EKYTE_DISPONIVEL = True
except ImportError:
    EKYTE_DISPONIVEL = False

SYSTEM_COORDENADOR = """
Você é o Agente Coordenador da Squad Mata Leão V4.
Gere o checklist de conformidade semanal no formato padrão da operação.
Seja direto e binário: S ou N. Itens N viram pauta do Comitê.
"""


def gerar_checklist(clientes: list) -> tuple[str, str]:
    """Gera o checklist e as pautas para o Comitê."""

    nomes = [c["nome"] for c in clientes]

    user_prompt = f"""
Gere o checklist de conformidade semanal para a Squad Mata Leão.

Clientes ativos: {', '.join(nomes)}
Data: {date.today().strftime('%d/%m/%Y')} — Semana {date.today().isocalendar()[1]}

Gere o checklist completo no formato abaixo.
Para cada item use [ S ] ou [ N ] — deixe como [ ? ] se não for possível verificar automaticamente.

Depois gere a seção de PAUTAS PARA O COMITÊ com os itens N priorizados.

Formato:

CHECKLIST SEMANAL — Semana {date.today().isocalendar()[1]} — {date.today().strftime('%d/%m/%Y')}

─── RITUAIS ───
[ ? ] Comitê P&EG realizado com ata preenchida?
[ ? ] Growths realizados com atas preenchidas? (3x na semana)
[ ? ] Working Backwards realizado com ata preenchida?

─── ONGOING — {' / '.join(nomes)} ───
(Para cada cliente:)
[ ? ] Replanejamento trimestral em dia?
[ ? ] CSAT/NPS mensal coletado?
[ ? ] OKRs atualizadas no plano tático?
[ ? ] Sprint atual documentada no Ekyte?
[ ? ] Quality Check atualizado?
[ ? ] ROI atualizado no sistema interno?

─── PAUTAS PARA O COMITÊ DE SEGUNDA ───
(Liste os itens críticos que precisam de atenção)

─── STATUS GERAL ───
(Avaliação geral: VERDE / AMARELO / VERMELHO com justificativa)
"""

    checklist_text = claude(SYSTEM_COORDENADOR, user_prompt, max_tokens=1200)

    return checklist_text


def montar_email_checklist(checklist: str) -> str:
    semana = date.today().isocalendar()[1]
    return f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; color: #333;">

<h2 style="color: #1a1a1a; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px;">
  Checklist de Conformidade — Semana {semana}
</h2>

<p style="color: #666; font-size: 14px;">
  Preencha os itens marcados com [ ? ] e atualize os N identificados.
  Qualquer N vira pauta do Comitê de segunda automaticamente.
</p>

<div style="background: #f5f5f5; padding: 20px; border-radius: 8px;
            font-family: monospace; font-size: 13px; white-space: pre-wrap; line-height: 1.8;">
{checklist}
</div>

<div style="background: #fff3cd; padding: 12px; border-radius: 6px; margin-top: 16px;
            border-left: 4px solid #ffc107;">
  <strong>Lembrete:</strong> Preencher o checklist é parte do Working Backwards de hoje.
  Não é tarefa para depois — é parte do ritual.
</div>

<hr style="margin: 32px 0; border: none; border-top: 1px solid #e0e0e0;">
<p style="color: #999; font-size: 12px;">
  V4 Automations — Squad Mata Leão &nbsp;|&nbsp;
  Gerado automaticamente toda sexta às 16h.
</p>

</body>
</html>
"""


def main():
    print(f"[Checklist] Iniciando — {date.today()}")

    clientes = load_clientes()
    checklist = gerar_checklist(clientes)

    html = montar_email_checklist(checklist)

    gmail = GmailConnector()
    gmail.send(
        to=os.getenv("EMAIL_COORDENADOR"),
        subject=f"Checklist Semanal S/N — Semana {date.today().isocalendar()[1]}",
        body_html=html,
    )

    print(f"[Checklist] Concluído. Email enviado para Coordenador.")


if __name__ == "__main__":
    main()
