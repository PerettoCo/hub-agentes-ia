"""
fca.py — Automação de FCAs no Ekyte.

Fluxo:
  1. GT detecta anomalia de performance (via analise_performance.py)
  2. Este script cria o FCA no Ekyte automaticamente
  3. FCA aparece na fila do AM para revisar e comunicar ao cliente

Uso standalone:
  python scripts/ekyte/fca.py \\
    --cliente "Nome do Cliente" \\
    --fato "CAC subiu 40% na última semana" \\
    --causa "Fadiga de criativo + aumento de CPM" \\
    --acao "Pausar criativos com CTR < 1% e ativar novos até quinta"

Uso integrado (via analise_performance.py automático):
  from scripts.ekyte.fca import criar_fca_automatica
  criar_fca_automatica(cliente, desvio)
"""
import sys
import argparse
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.ekyte.connector import EkyteClient
from scripts.connectors import load_clientes, claude, GmailConnector
import os


SYSTEM_GT = """
Você é o Agente Gestor de Tráfego Senior V4.
Gere FCAs precisas, baseadas em dados, com causa provável e ação específica.
Formato: FATO (dado objetivo) → CAUSA (análise) → AÇÃO (quem faz, o que faz, quando).
"""


def gerar_fca_com_claude(cliente_nome: str, desvio: dict, dados_performance: dict) -> dict:
    """
    Usa Claude para gerar a FCA estruturada a partir de um desvio detectado.
    Retorna dict com fato, causa, acao.
    """
    user_prompt = f"""
Gere uma FCA estruturada para o cliente {cliente_nome}.

Desvio detectado:
{desvio}

Dados de performance relevantes:
{dados_performance}

Gere exatamente neste formato (apenas o conteúdo, sem títulos extras):

FATO:
[Dado objetivo e específico — número, percentual, período]

CAUSA:
[Análise da causa mais provável — 2-3 frases baseadas nos dados]

AÇÃO:
[O que será feito — quem (GT/Copy/Design/AM), o quê, quando]
"""
    resposta = claude(SYSTEM_GT, user_prompt, max_tokens=400)

    fato = causa = acao = ""
    secao_atual = None

    for linha in resposta.split("\n"):
        linha = linha.strip()
        if linha.startswith("FATO:"):
            secao_atual = "fato"
            resto = linha.replace("FATO:", "").strip()
            if resto: fato += resto + " "
        elif linha.startswith("CAUSA:"):
            secao_atual = "causa"
            resto = linha.replace("CAUSA:", "").strip()
            if resto: causa += resto + " "
        elif linha.startswith("AÇÃO:") or linha.startswith("ACAO:"):
            secao_atual = "acao"
            resto = linha.replace("AÇÃO:", "").replace("ACAO:", "").strip()
            if resto: acao += resto + " "
        elif linha and secao_atual:
            if secao_atual == "fato": fato += linha + " "
            elif secao_atual == "causa": causa += linha + " "
            elif secao_atual == "acao": acao += linha + " "

    return {
        "fato": fato.strip(),
        "causa": causa.strip(),
        "acao": acao.strip(),
    }


def criar_fca_automatica(
    cliente: dict,
    desvio: dict,
    dados_performance: dict = None,
    notificar_am: bool = True,
) -> dict:
    """
    Cria FCA automaticamente no Ekyte quando anomalia é detectada.

    Args:
        cliente: dict do cliente em clientes.json
        desvio: dict com kr, meta, atual, desvio_pct, critico
        dados_performance: dados coletados de Google Ads / Meta
        notificar_am: se True, envia email para o AM

    Returns:
        dict com resultado da criação
    """
    workspace_id = cliente.get("ekyte_workspace_id")
    executor_id = cliente.get("ekyte_executor_id_gt")

    if not workspace_id:
        print(f"  {cliente['nome']}: ekyte_workspace_id não configurado — pulando FCA")
        return {"criado": False, "motivo": "workspace_id não configurado"}

    # Gera FCA com Claude
    fca_data = gerar_fca_com_claude(
        cliente["nome"],
        desvio,
        dados_performance or {},
    )

    resultado = {
        "cliente": cliente["nome"],
        "desvio": desvio,
        "fca": fca_data,
        "criado_ekyte": False,
        "notificado": False,
    }

    # Cria no Ekyte
    try:
        ekyte = EkyteClient()
        ticket = ekyte.criar_fca(
            fato=fca_data["fato"],
            causa=fca_data["causa"],
            acao=fca_data["acao"],
            workspace_id=workspace_id,
            executor_id=executor_id or "",
            cliente_nome=cliente["nome"],
        )
        resultado["criado_ekyte"] = True
        resultado["ticket_id"] = ticket.get("id")
        print(f"  FCA criada no Ekyte: #{ticket.get('id')} — {cliente['nome']}")
    except Exception as e:
        resultado["erro_ekyte"] = str(e)
        print(f"  Erro ao criar FCA no Ekyte: {e}")
        print(f"  (POST /tickets pode não estar disponível — confirme com suporte Ekyte)")

    # Notifica AM por email com a FCA gerada
    if notificar_am:
        try:
            gmail = GmailConnector()
            criticidade = "🔴 CRÍTICO" if desvio.get("critico") else "🟡 Atenção"
            html = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333; padding: 20px;">

<h3 style="color: {'#dc3545' if desvio.get('critico') else '#ffc107'};">
  {criticidade} — FCA Gerada — {cliente['nome']}
</h3>

<p style="color: #666; font-size: 13px;">
  Desvio detectado automaticamente em {date.today().strftime('%d/%m/%Y')}.
  {'FCA registrada no Ekyte.' if resultado['criado_ekyte'] else 'Registre manualmente no Ekyte.'}
</p>

<div style="background: #f8f9fa; padding: 16px; border-radius: 8px; margin: 12px 0;">
  <strong>KR afetado:</strong> {desvio.get('kr', '?')}<br>
  <strong>Meta:</strong> {desvio.get('meta')} | <strong>Atual:</strong> {desvio.get('atual')} |
  <strong>Desvio:</strong> {desvio.get('desvio_pct', 0):+.1f}%
</div>

<div style="border-left: 4px solid #dc3545; padding: 12px; margin: 12px 0; background: #fff5f5;">
  <strong>FATO:</strong><br>{fca_data['fato']}
</div>

<div style="border-left: 4px solid #ffc107; padding: 12px; margin: 12px 0; background: #fffbf0;">
  <strong>CAUSA:</strong><br>{fca_data['causa']}
</div>

<div style="border-left: 4px solid #28a745; padding: 12px; margin: 12px 0; background: #f0fff4;">
  <strong>AÇÃO:</strong><br>{fca_data['acao']}
</div>

<p style="color: #999; font-size: 12px; margin-top: 24px;">
  V4 Automations — FCA gerada automaticamente pelo Agente GT.
  {'ID no Ekyte: #' + str(resultado.get('ticket_id', '')) if resultado['criado_ekyte'] else ''}
</p>
</body>
</html>
"""
            gmail.send(
                to=os.getenv("EMAIL_AM"),
                subject=f"{criticidade} — FCA {cliente['nome']} — {date.today().strftime('%d/%m')}",
                body_html=html,
            )
            resultado["notificado"] = True
        except Exception as e:
            resultado["erro_notificacao"] = str(e)

    return resultado


def main():
    parser = argparse.ArgumentParser(description="Cria FCA no Ekyte")
    parser.add_argument("--cliente", required=True, help="Nome do cliente")
    parser.add_argument("--fato", required=True)
    parser.add_argument("--causa", required=True)
    parser.add_argument("--acao", required=True)
    parser.add_argument("--kr", default="Performance geral", help="KR afetado")
    parser.add_argument("--critico", action="store_true")
    args = parser.parse_args()

    clientes = load_clientes()
    cliente = next((c for c in clientes if c["nome"] == args.cliente), None)
    if not cliente:
        print(f"Cliente '{args.cliente}' não encontrado em clientes.json")
        return

    workspace_id = cliente.get("ekyte_workspace_id")
    executor_id = cliente.get("ekyte_executor_id_gt", "")

    if not workspace_id:
        print(f"Adicione 'ekyte_workspace_id' em clientes.json para {args.cliente}")
        return

    ekyte = EkyteClient()
    resultado = ekyte.criar_fca(
        fato=args.fato,
        causa=args.causa,
        acao=args.acao,
        workspace_id=workspace_id,
        executor_id=executor_id,
        cliente_nome=args.cliente,
    )

    print(f"FCA criada: {resultado}")


if __name__ == "__main__":
    main()
