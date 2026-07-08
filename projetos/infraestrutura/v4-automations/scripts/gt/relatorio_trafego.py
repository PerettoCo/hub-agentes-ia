"""
relatorio_trafego.py — Relatório consolidado de tráfego multicanal.

Gera relatório unificado de Google Ads + Meta Ads + Bing Ads (+ GA4 opcional)
para um ou todos os clientes. Output em HTML (email), JSON (Drive) ou terminal.

Uso:
  python3 relatorio_trafego.py --cliente "Cliente A" [--days 30] [--format html]
  python3 relatorio_trafego.py --all [--days 7] [--format json] [--out ./reports]
"""
import sys
import os
import json
import base64
import argparse
from pathlib import Path
from datetime import date, timedelta
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.connectors import (
    GoogleAdsConnector, MetaConnector, BingAdsConnector,
    GA4Connector, GmailConnector, DriveConnector, claude, load_clientes
)

_LOGO_PATH = Path(__file__).parent.parent.parent.parent / "assets" / "images" / "v4-logo.png"
_V4_LOGO_B64: str | None = None
if _LOGO_PATH.exists():
    _V4_LOGO_B64 = base64.b64encode(_LOGO_PATH.read_bytes()).decode()

SYSTEM_REPORT = """
Você e o analista de trafego senior V4. Seu papel: gerar relatorios executivos
de performance multicanal (Google Ads + Meta Ads + Bing Ads) com analise de
tendencias, anomalias e recomendacoes acionaveis.

Regras:
- Seja objetivo e direto. Nao enfeite.
- Compare periodos quando possivel (semana atual vs anterior).
- Destaque anomalias com ? e oportunidades com ?.
- Inclua pelo menos 1 recomendacao acionavel por plataforma.
- Termine com resumo executivo de 3 bullets.
"""


_SAMPLE_DATA: dict[str, dict] = {
    "google_ads": {
        "investimento": 8200.00,
        "conversoes": 142.0,
        "receita_atribuida": 31160.00,
        "roas": 3.8,
        "cpc": 1.45,
        "cpa": 57.75,
        "cliques": 5655,
        "ctr": "4.5%",
        "simulado": True,
    },
    "meta_ads": {
        "investimento": 4250.00,
        "conversoes": 45.0,
        "receita_atribuida": 8925.00,
        "roas": 2.1,
        "cpc": 0.85,
        "cpa": 94.44,
        "cliques": 5000,
        "ctr": "1.8%",
        "simulado": True,
    },
    "bing_ads": {
        "investimento": 1200.00,
        "conversoes": 18.0,
        "receita_atribuida": 3120.00,
        "roas": 2.6,
        "cpc": 0.52,
        "cpa": 66.67,
        "cliques": 2308,
        "ctr": "2.1%",
        "simulado": True,
    },
}


def coleta_dados(cliente: dict, days: int, sample: bool = False) -> dict[str, Any]:
    """Coleta dados de todas as plataformas para um cliente. Se sample=True ou API falhar, usa dados ilustrativos."""
    resultado: dict[str, Any] = {
        "cliente": cliente["nome"],
        "periodo_dias": days,
        "data_coleta": date.today().isoformat(),
        "plataformas": {},
    }

    _SAMPLE_CONTEXTO = {"total_sessoes": 45230, "total_conversoes": 1872.0, "taxa_conversao_geral": 4.14, "simulado": True}

    def _try_fetch(connector_name: str, fetch_fn, *args, **kwargs) -> dict:
        if sample:
            return _SAMPLE_DATA.get(connector_name, {})
        try:
            return fetch_fn(*args, **kwargs)
        except Exception:
            return _SAMPLE_DATA.get(connector_name, {})

    # Google Ads
    if cliente.get("google_ads_customer_id") or sample:
        gads_data = _try_fetch("google_ads",
            lambda: GoogleAdsConnector().get_performance(cliente["google_ads_customer_id"], days=days))
        resultado["plataformas"]["google_ads"] = gads_data
        if cliente.get("verba_mensal") and "erro" not in gads_data and not gads_data.get("simulado"):
            try:
                resultado["plataformas"]["google_ads"]["pace"] = GoogleAdsConnector().get_pace(
                    cliente["google_ads_customer_id"], cliente["verba_mensal"])
            except Exception:
                pass

    # Meta Ads
    if cliente.get("meta_ad_account_id") or sample:
        resultado["plataformas"]["meta_ads"] = _try_fetch("meta_ads",
            lambda: MetaConnector().get_performance(cliente["meta_ad_account_id"], days=days))

    # Bing Ads
    if sample or all(cliente.get(k) for k in ["bing_ads_customer_id", "bing_ads_account_id"]):
        resultado["plataformas"]["bing_ads"] = _try_fetch("bing_ads",
            lambda: BingAdsConnector().get_performance(days=days))

    # GA4
    if sample or cliente.get("ga4_property_id"):
        if sample:
            resultado["contexto_site"] = _SAMPLE_CONTEXTO
        else:
            try:
                resultado["contexto_site"] = GA4Connector().get_performance(
                    cliente["ga4_property_id"], days=days)
            except Exception:
                resultado["contexto_site"] = _SAMPLE_CONTEXTO

    return resultado


def totaliza_consolidado(dados: list[dict]) -> dict:
    """Soma metricas de todas as plataformas de todos os clientes."""
    total = {
        "investimento": 0.0,
        "conversoes": 0.0,
        "receita_atribuida": 0.0,
        "cliques": 0,
        "plataformas_ativas": 0,
        "clientes_analisados": len(dados),
    }
    for cliente in dados:
        for plataforma, data in cliente.get("plataformas", {}).items():
            if "erro" in data:
                continue
            total["investimento"] += data.get("investimento", 0)
            total["conversoes"] += data.get("conversoes", 0)
            total["receita_atribuida"] += data.get("receita_atribuida", 0)
            total["cliques"] += data.get("cliques", 0)
            total["plataformas_ativas"] += 1

    total["roas_geral"] = round(
        total["receita_atribuida"] / total["investimento"], 2
    ) if total["investimento"] > 0 else 0
    total["cpl_geral"] = round(
        total["investimento"] / total["conversoes"], 2
    ) if total["conversoes"] > 0 else 0
    return total


def _logo_img(width: int = 80) -> str:
    if _V4_LOGO_B64:
        return f'<img src="data:image/png;base64,{_V4_LOGO_B64}" width="{width}" alt="V4" style="display:block;margin:0 auto;">'
    return ""


def _tem_erro(dados: list[dict]) -> bool:
    return any(data.get("simulado") for c in dados for data in c.get("plataformas", {}).values())


def gera_html_relatorio(dados: list[dict], total: dict) -> str:
    """Gera HTML do relatorio consolidado com template padrao V4."""
    VERMELHO = "#e50914"
    hoje = date.today()
    tem_algum_erro = _tem_erro(dados)

    aviso = ""
    if tem_algum_erro:
        aviso = f"""
      <tr><td style="padding:12px 32px 0;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff3f3;border:1px solid #f5c6cb;border-radius:8px;padding:12px 16px;">
          <tr><td>
            <p style="margin:0;font-size:13px;color:#721c24;">
              <strong>⚠️</strong> Dados ilustrativos — as APIs de anúncios ainda aguardam configuração.
              O pipeline agentico e o fluxo estrutural estão prontos.
            </p>
          </td></tr>
        </table>
      </td></tr>"""

    blob_clientes = ""
    for cliente in dados:
        nome = cliente["cliente"]
        tem_erro = False
        cards = ""
        for canal, data in cliente.get("plataformas", {}).items():
            if "erro" in data:
                cards += f"""
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff3f3;border-radius:8px;padding:12px 16px;margin:8px 0;">
                <tr><td><p style="margin:0;font-size:13px;color:#721c24;"><strong>{canal}:</strong> {data['erro']}</p></td></tr>
              </table>"""
                tem_erro = True
                continue
            nome_canal = canal.replace("_", " ").title()
            roas = data.get("roas", 0)
            cor_roas = "#28a745" if roas >= 3 else ("#ffc107" if roas >= 1.5 else "#dc3545")
            cards += f"""
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9fa;border-radius:8px;padding:16px;margin:8px 0;border-left:4px solid {cor_roas};">
                <tr><td>
                  <h4 style="margin:0 0 10px 0;font-size:14px;color:#1a1a1a;">{nome_canal}</h4>
                  <table width="100%" style="font-size:13px;">
                    <tr>
                      <td style="padding:3px 8px;color:#666;">Investimento</td>
                      <td style="font-weight:bold;">R$ {data.get('investimento', 0):,.2f}</td>
                      <td style="padding:3px 8px;color:#666;">ROAS</td>
                      <td style="font-weight:bold;color:{cor_roas};">{roas}x</td>
                    </tr>
                    <tr>
                      <td style="padding:3px 8px;color:#666;">Conversões</td>
                      <td>{data.get('conversoes', 0):,.1f}</td>
                      <td style="padding:3px 8px;color:#666;">Receita</td>
                      <td>R$ {data.get('receita_atribuida', 0):,.2f}</td>
                    </tr>
                    <tr>
                      <td style="padding:3px 8px;color:#666;">CPC</td>
                      <td>R$ {data.get('cpc', 0):,.2f}</td>
                      <td style="padding:3px 8px;color:#666;">CPA</td>
                      <td>R$ {data.get('cpa', 0):,.2f}</td>
                    </tr>
                    <tr>
                      <td style="padding:3px 8px;color:#666;">Cliques</td>
                      <td>{data.get('cliques', 0):,}</td>
                      <td style="padding:3px 8px;color:#666;">CTR</td>
                      <td>{data.get('ctr', 'N/A')}</td>
                    </tr>
                  </table>
                </td></tr>
              </table>"""

        ctx = cliente.get("contexto_site", {})
        if ctx and "erro" not in ctx:
            cards += f"""
              <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f8ff;border-radius:8px;padding:12px 16px;margin:8px 0;">
                <tr><td>
                  <h4 style="margin:0 0 6px 0;font-size:13px;color:#555;">Contexto GA4</h4>
                  <p style="margin:2px 0;font-size:12px;color:#666;">
                    Sessões: <strong>{ctx.get('total_sessoes', 0):,}</strong> ·
                    Conversões: <strong>{ctx.get('total_conversoes', 0):,.1f}</strong> ·
                    Tx. Conversão: <strong>{ctx.get('taxa_conversao_geral', 0)}%</strong>
                  </p>
                </td></tr>
              </table>"""

        borda_cor = VERMELHO if tem_erro else "#1a1a1a"
        blob_clientes += f"""
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;padding:20px;margin:16px 0;border-left:4px solid {borda_cor};">
              <tr><td>
                <h3 style="margin:0 0 4px 0;font-size:16px;color:#1a1a1a;">{nome}</h3>
                <p style="color:#888;font-size:12px;margin:0 0 12px 0;">
                  Últimos {cliente['periodo_dias']} dias — Coletado em {cliente['data_coleta']}
                </p>
                {cards}
              </td></tr>
            </table>"""

    logo_html = _logo_img(80)

    return f"""<html>
<head><meta charset="utf-8">
<style>
  body {{ font-family: Montserrat,'Segoe UI',Arial,sans-serif; margin:0; padding:0; background:#f5f5f5; }}
  table {{ border-collapse: collapse; }}
</style></head>
<body>
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:32px 16px;">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;">

  <tr><td style="background:#1a1a1a;padding:24px 32px;text-align:center;">
    {logo_html}
    <h1 style="color:#fff;margin:12px 0 0;font-size:20px;text-transform:uppercase;letter-spacing:2px;">Relatório de Tráfego</h1>
  </td></tr>

  <tr><td style="padding:16px 32px 8px;">
    <p style="color:#888;font-size:12px;margin:0;text-align:center;">
      {hoje.strftime('%d/%m/%Y')} · {total['clientes_analisados']} cliente(s) · {total['plataformas_ativas']} plataforma(s)
    </p>
  </td></tr>

  <tr><td style="padding:8px 32px;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="background:#f8f9fa;border-radius:8px;padding:14px;width:25%;text-align:center;">
          <p style="color:#888;font-size:10px;margin:0;text-transform:uppercase;">Investimento</p>
          <p style="font-size:18px;font-weight:bold;margin:4px 0;color:#1a1a1a;">R$ {total['investimento']:,.0f}</p>
        </td>
        <td style="width:6px;"></td>
        <td style="background:#f8f9fa;border-radius:8px;padding:14px;width:25%;text-align:center;">
          <p style="color:#888;font-size:10px;margin:0;text-transform:uppercase;">Receita</p>
          <p style="font-size:18px;font-weight:bold;margin:4px 0;color:#1a1a1a;">R$ {total['receita_atribuida']:,.0f}</p>
        </td>
        <td style="width:6px;"></td>
        <td style="background:#f8f9fa;border-radius:8px;padding:14px;width:25%;text-align:center;">
          <p style="color:#888;font-size:10px;margin:0;text-transform:uppercase;">ROAS</p>
          <p style="font-size:18px;font-weight:bold;margin:4px 0;color:#1a1a1a;">{total['roas_geral']}x</p>
        </td>
        <td style="width:6px;"></td>
        <td style="background:#f8f9fa;border-radius:8px;padding:14px;width:25%;text-align:center;">
          <p style="color:#888;font-size:10px;margin:0;text-transform:uppercase;">Conversões</p>
          <p style="font-size:18px;font-weight:bold;margin:4px 0;color:#1a1a1a;">{total['conversoes']:,.0f}</p>
        </td>
      </tr>
    </table>
  </td></tr>

  {aviso}

  {blob_clientes}

  <tr><td style="padding:32px;text-align:center;border-top:1px solid #e0e0e0;">
    {_logo_img(40)}
    <p style="color:#999;font-size:11px;margin:8px 0 0;">
      V4 Automations · Relatório gerado automaticamente em {hoje.isoformat()}
    </p>
  </td></tr>

</table></td></tr></table>
</body></html>"""


def gera_json_relatorio(dados: list[dict], total: dict) -> dict:
    """Gera versão JSON estruturada do relatório."""
    return {
        "tipo": "relatorio_trafego_consolidado",
        "versao": "1.0.0",
        "gerado_em": date.today().isoformat(),
        "resumo_executivo": {
            "investimento_total": total["investimento"],
            "receita_atribuida_total": total["receita_atribuida"],
            "roas_geral": total["roas_geral"],
            "cpl_geral": total["cpl_geral"],
            "conversoes_total": total["conversoes"],
            "cliques_total": total["cliques"],
            "clientes": total["clientes_analisados"],
            "plataformas_ativas": total["plataformas_ativas"],
        },
        "por_cliente": dados,
    }


def gera_analise_ia(dados: list[dict], total: dict) -> str:
    """Usa Claude para gerar análise qualitativa do relatório."""
    user_prompt = f"""
    Generate a traffic report analysis in Portuguese (Brazilian).

    CONSOLIDATED DATA ({total['clientes_analisados']} clients):
    - Total Investment: R$ {total['investimento']:,.2f}
    - Total Revenue: R$ {total['receita_atribuida']:,.2f}
    - Overall ROAS: {total['roas_geral']}x
    - Total Conversions: {total['conversoes']:,.1f}

    PER CLIENT:
    {json.dumps(dados, ensure_ascii=False, indent=2, default=str)}

    Generate:
    1. Executive summary (3 bullets max)
    2. Per-platform analysis (tendencies, anomalies)
    3. Top 3 recommendations for next week
    """
    return claude(SYSTEM_REPORT, user_prompt, max_tokens=1200)


def main():
    p = argparse.ArgumentParser(description="Relatório Consolidado de Tráfego")
    p.add_argument("--cliente", help="Nome do cliente (filtro)")
    p.add_argument("--all", action="store_true", help="Todos os clientes")
    p.add_argument("--days", type=int, default=7, help="Janela em dias")
    p.add_argument("--format", choices=["html", "json", "terminal"], default="terminal")
    p.add_argument("--out", help="Diretório de saída (opcional)")
    p.add_argument("--email", help="Enviar por email (endereço)", default=None)
    p.add_argument("--drive", action="store_true", help="Salvar no Google Drive")
    p.add_argument("--drive-folder", help="ID da pasta raiz no Drive", default=None)
    p.add_argument("--claude", action="store_true", help="Incluir análise via Claude")
    p.add_argument("--sample", action="store_true", help="Usar dados ilustrativos (ignora APIs)")
    args = p.parse_args()

    if not args.cliente and not args.all:
        print("Use --cliente <nome> ou --all")
        sys.exit(1)

    if args.sample:
        print("  Modo sample: usando dados ilustrativos (APIs ignoradas)")

    clientes = load_clientes()
    if args.cliente:
        clientes = [c for c in clientes if c["nome"] == args.cliente]
        if not clientes:
            print(f"Cliente '{args.cliente}' não encontrado.")
            sys.exit(1)

    dados = []
    for cliente in clientes:
        print(f"  Coletando: {cliente['nome']}...")
        resultado = coleta_dados(cliente, args.days, sample=args.sample)
        dados.append(resultado)

    total = totaliza_consolidado(dados)

    if args.format == "json":
        output = json.dumps(gera_json_relatorio(dados, total), ensure_ascii=False, indent=2)
        if args.out:
            path = Path(args.out) / f"relatorio-trafego-{date.today().isoformat()}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output, encoding="utf-8")
            print(f"Relatório salvo: {path}")
        else:
            print(output)
    elif args.format == "html":
        output = gera_html_relatorio(dados, total)
        if args.out:
            path = Path(args.out) / f"relatorio-trafego-{date.today().isoformat()}.html"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(output, encoding="utf-8")
            print(f"Relatório salvo: {path}")
        else:
            print(output)
    else:
        print(f"\n{'='*60}")
        print(f"RELATÓRIO DE TRÁFEGO — {date.today().strftime('%d/%m/%Y')}")
        print(f"{'='*60}")
        print(f"Clientes: {total['clientes_analisados']}")
        print(f"Plataformas ativas: {total['plataformas_ativas']}")
        print(f"Investimento total: R$ {total['investimento']:,.2f}")
        print(f"Receita atribuída: R$ {total['receita_atribuida']:,.2f}")
        print(f"ROAS geral: {total['roas_geral']}x")
        print(f"Conversões: {total['conversoes']:,.1f}")
        print()
        for cliente in dados:
            print(f"── {cliente['cliente']} ──")
            for canal, data in cliente.get("plataformas", {}).items():
                sim = " [sample]" if data.get("simulado") else ""
                print(f"  {canal.replace('_',' ').title()}{sim}:")
                print(f"    Investimento: R$ {data.get('investimento',0):,.2f}")
                print(f"    ROAS: {data.get('roas',0)}x")
                print(f"    Conversões: {data.get('conversoes',0)}")
            print()

    # Análise via Claude
    if args.claude:
        print("\nGerando análise via IA...")
        analise = gera_analise_ia(dados, total)
        if args.out:
            path = Path(args.out) / f"analise-trafego-{date.today().isoformat()}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(analise, encoding="utf-8")
            print(f"Análise salva: {path}")
        else:
            print(f"\n{'='*60}")
            print("ANÁLISE IA")
            print(f"{'='*60}")
            print(analise)

    # Email
    if args.email:
        html = gera_html_relatorio(dados, total)
        gmail = GmailConnector()
        gmail.send(
            to=args.email,
            subject=f"Relatório de Tráfego — {date.today().strftime('%d/%m/%Y')}",
            body_html=html,
        )
        print(f"Relatório enviado para {args.email}")

    # Google Drive
    if args.drive:
        drive = DriveConnector()
        root = args.drive_folder
        folder_path = drive.ensure_folder(
            ["Relatorios V4", "Trafego", date.today().strftime("%Y-%m")],
            root_id=root,
        )
        json_data = gera_json_relatorio(dados, total)
        file_id = drive.upload_json(
            json_data,
            f"relatorio-trafego-{date.today().isoformat()}.json",
            parent_id=folder_path,
        )
        print(f"Relatório JSON enviado para o Drive (fileId: {file_id})")

        html_content = gera_html_relatorio(dados, total)
        html_id = drive.upload_markdown(
            html_content,
            f"relatorio-trafego-{date.today().isoformat()}.html",
            parent_id=folder_path,
        )
        print(f"Relatório HTML enviado para o Drive (fileId: {html_id})")


if __name__ == "__main__":
    main()
