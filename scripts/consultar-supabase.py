#!/usr/bin/env python3
"""consultar-supabase — Executa consultas SQL (PostgREST) no Supabase DADOS.

O agente traduz a pergunta em linguagem natural para SQL e este script apenas
executa e devolve os dados. Suporta: SELECT simples, count(*), WHERE (AND/OR),
ORDER BY e LIMIT.

Tabela fato principal: DBClientes (clientes).
Demais: DBSquads, DBPessoas, 11Service, 121Kickoff, 121KickoffEE,
50TranscricaoCheckin, f_gerenciador_* (campanhas Meta/Google).
"""
import os
import sys
import json
import urllib.request
import urllib.parse
import re

SUPABASE_URL = os.environ.get("SUPABASE_DADOS_URL", "https://mhntycubvywjszweeuxs.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_DADOS_KEY")

# Schema (tabelas e colunas principais) para validacao/ajuda.
SCHEMA = {
    "DBClientes": ["cardid", "title", "nomedaempresa", "cnpj", "cidade", "uf", "nomedoprincipalstakeholder",
                  "contatodostakeholder", "emaildostakeholder", "razaosocial", "corretagem", "faturamentoanual",
                  "tier", "etiquetastatus", "currentphasename", "setor", "subsetor", "segmento", "canaldevendas",
                  "modelodevendas", "modelodenegocio", "nomedocloser", "moeda", "poderfinanceiro", "portfolio",
                  "nivelconsciencia", "inadimplencia", "situacao", "contrato_url", "datadeinicio",
                  "datadoprimeiropagamento", "data_churn", "motivo_churn", "google_drive_folder", "ekyte_id"],
    "DBSquads": ["cardid", "title", "departamento", "headdri", "emaildohead", "match_keywords", "is_apoio", "space_id_squads", "id_pipefy"],
    "DBPessoas": ["cardid", "title", "funcao", "equipe", "datadeinicio", "senioridade", "status", "nomecompleto",
                  "emailv4company", "cpf", "cnpj", "whatsappbusiness", "razaosocial", "remuneracaoinicial",
                  "remuneracaovigente", "chavepix", "space_id", "meet_recordings_id"],
    "11Service": ["cardid", "title", "cliente12", "datadeiniciopagamento", "categoriavendida", "juros", "valorjuros",
                  "pessoalenvolvido", "squads", "quantotempoduraraesseprojeto", "clientedatabase", "modelodecobranca",
                  "produtosgestaodemidia", "valorgestaodemidia", "produtoscriativos", "valorcriativos",
                  "produtoscrmmarketing", "valorcrmmarketing", "produtoscomerciais", "valorcomerciais",
                  "produtostech", "valortech", "produtoscontent", "valorcontent", "produtoswebdesing", "valorwebdesing",
                  "produtosassessoria", "valorassessoria", "datadechurn", "squad", "squad1", "squad2", "squad3", "datainicio"],
    "121Kickoff": ["cardid", "title", "empresacompany", "cidadeestado", "segmentodonegocio", "nome", "cargo",
                   "qualofaturamentomensalmedio", "qualeoticketmedio", "margem_contribuicao_pct", "categoria",
                   "icp", "percepcaomarca", "tomdevoz", "website", "whoareyourmaincompetitors"],
    "121KickoffEE": ["id", "created_at", "faturamento_mensal", "segmento_negocio", "objetivos", "modelo_vendas",
                    "produto_servico", "descricao_clientes", "concorrentes", "margem_contribuicao_pct",
                    "investimento_midia_paga_brl", "qtd_leads_mes", "qtd_oportunidades_mes", "qtd_pedidos_mes",
                    "data_envio", "nome_cliente", "dbcliente_id"],
    "50TranscricaoCheckin": ["codigo", "titulo", "criado_em", "atualizado_em", "squad", "cliente",
                             "indice_aderencia_ao_roteiro_metodo", "indice_rigor_analitico_dados_conteudo",
                             "indice_lideranca_gestao_de_expectativa_futuro", "check_in", "dores_latentes",
                             "visao_sobre_o_projeto", "avaliacao_positiva_do_projeto", "sugestao_de_melhoria",
                             "oportunidades_de_upsell", "riscos_e_obstaculos", "recomendacoes_finais", "resumo",
                             "indice_atendimento", "indice_satisfacao_do_cliente", "indice_tecnico",
                             "space_id_cliente", "funcionario_email"],
    "f_gerenciador_meta": ["id", "ad_id", "adset_id", "campaign_id", "account_id", "data_semana", "data_fim",
                           "custo", "impressoes", "cliques", "reach", "ctr", "cpc", "leads", "omni_purchase",
                           "value_omni_purchase", "resultados", "resultado_indicador", "cpm", "cpp", "frequency"],
    "f_gerenciador_google_ad": ["id", "customer_id", "campaign_id", "ad_group_id", "ad_id", "data_semana",
                                "campaign_name", "ad_group_name", "ad_status", "custo", "impressoes", "cliques",
                                "ctr", "average_cpc", "conversions", "conversions_value", "cost_per_conversion",
                                "roas", "all_conversions"],
    "f_gerenciador_google_campanha": ["id", "customer_id", "campaign_id", "data_semana", "campaign_name",
                                     "channel_type", "campaign_status", "bidding_strategy_type", "custo",
                                     "impressoes", "cliques", "ctr", "average_cpc", "conversions",
                                     "conversions_value", "cost_per_conversion", "roas"],
    "f_gerenciador_google_pmax": ["id", "customer_id", "campaign_id", "asset_group_id", "data_semana",
                                  "campaign_name", "asset_group_name", "asset_group_status", "custo", "impressoes",
                                  "cliques", "ctr", "conversions", "conversions_value", "roas"],
}

OPS = {"eq", "neq", "gt", "gte", "lt", "lte", "like", "ilike", "in", "is"}


def err(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False))
    sys.exit(1)


def parse_sql(sql):
    sql = sql.strip().rstrip(";").strip()
    m = re.match(r"select\s+(.*?)\s+from\s+(\w+)", sql, re.IGNORECASE)
    if not m:
        err("Formato nao suportado. Exemplo: SELECT * FROM DBClientes WHERE uf='SP' LIMIT 5  |  SELECT count(*) FROM DBClientes WHERE etiquetastatus='Ativo'")
    sel, table = m.group(1).strip(), m.group(2)
    rest = sql[m.end():].strip()

    aggregate = None
    cm = re.match(r"count\s*\(\s*\*?\s*\)|count\s*\(\s*(\w+)\s*\)", sel, re.IGNORECASE)
    if cm:
        aggregate = "count"
        counted = cm.group(1) or "cardid"
        sel = counted
    elif sel.strip() == "*":
        sel = "*"
    else:
        sel = ", ".join(c.strip() for c in sel.split(","))

    where = None
    om = re.search(r"\bwhere\b\s+(.*?)(?:\s+order\s+by\s+|\s+limit\s+|$)", rest, re.IGNORECASE | re.DOTALL)
    if om:
        where = om.group(1).strip()

    order = None
    om2 = re.search(r"\border\s+by\s+(\w+)\s*(asc|desc)?", rest, re.IGNORECASE)
    if om2:
        order = om2.group(1) + ("." + (om2.group(2) or "asc").lower())

    limit = None
    lm = re.search(r"\blimit\s+(\d+)", rest, re.IGNORECASE)
    if lm:
        limit = int(lm.group(1))

    filters = []
    if where:
        for part in re.split(r"\s+(?:and|or)\s+", where, flags=re.IGNORECASE):
            part = part.strip()
            if not part:
                continue
            fm = re.match(r"(\w+)\s*(>=|<=|<>|!=|=|>|<|like|ilike|in|is)\s*(.+)$", part, re.IGNORECASE)
            if not fm:
                continue
            col, op, val = fm.group(1), fm.group(2).lower(), fm.group(3).strip().strip("'").strip('"')
            opmap = {"=": "eq", ">=": "gte", "<=": "lte", ">": "gt", "<": "lt", "<>": "neq", "!=": "neq"}
            op = opmap.get(op, op)
            if op not in OPS:
                continue
            filters.append({"column": col, "op": op, "value": val})

    return {
        "table": table,
        "select": sel,
        "filters": filters,
        "order": order,
        "limit": limit or 20,
        "aggregate": aggregate,
    }


def build_params(spec):
    params = {}
    if spec.get("aggregate") == "count":
        params["select"] = spec.get("select") or "cardid"
        params["limit"] = "1"
    elif spec.get("select") and spec["select"] != "*":
        params["select"] = spec["select"]
    for f in spec.get("filters", []):
        col, op, val = f.get("column"), f.get("op"), f.get("value")
        if not col or op not in OPS:
            continue
        if op == "in":
            params[col] = "in.(" + str(val) + ")"
        elif op == "is":
            params[col] = "is." + str(val)
        else:
            params[col] = f"{op}.{val}"
    if spec.get("order"):
        params["order"] = spec["order"]
    params["limit"] = str(min(int(spec.get("limit", 20) or 20), 100))
    return params


def execute(spec):
    table = spec["table"]
    if table not in SCHEMA:
        err(f"Tabela '{table}' nao esta no schema. Tabelas: {', '.join(SCHEMA.keys())}")
    if not SUPABASE_KEY:
        err("SUPABASE_DADOS_KEY nao definida no ambiente")
    url = f"{SUPABASE_URL}/rest/v1/{urllib.parse.quote(table, safe='')}?{urllib.parse.urlencode(build_params(spec))}"
    req = urllib.request.Request(url)
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", "Bearer " + SUPABASE_KEY)
    req.add_header("Accept", "application/json")
    if spec.get("aggregate") == "count":
        req.add_header("Prefer", "count=exact")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 404:
            err(f"Tabela '{table}' nao encontrada. Verifique o nome exato.")
        elif e.code == 406:
            err(f"Coluna/parametro invalido em '{table}': {body[:300]}")
        else:
            err(f"HTTP {e.code}: {body[:500]}")
    except Exception as e:
        err(f"Erro de execucao: {e}")
    if spec.get("aggregate") == "count":
        crange = resp.headers.get("content-range", "")
        mm = re.search(r"/(\d+)\s*$", crange)
        total = int(mm.group(1)) if mm else len(data)
        return {"count": total}
    return data


def clean(rows):
    if isinstance(rows, list):
        for r in rows:
            if isinstance(r, dict):
                for k, v in list(r.items()):
                    if isinstance(v, str) and len(v) > 200:
                        r[k] = v[:200] + "...[truncado]"
                    elif isinstance(v, (dict, list)):
                        r[k] = json.dumps(v, ensure_ascii=False)[:200] + "...[truncado]"
    return rows


def main():
    q = " ".join(sys.argv[1:]).strip() or sys.stdin.read().strip()
    if not q:
        err("Forneca uma consulta SQL (o agente traduz a pergunta do usuario para SQL).")
    if not re.match(r"^\s*select\b", q, re.IGNORECASE):
        err("Envie uma consulta SQL. Ex: SELECT * FROM DBClientes WHERE uf='SP' LIMIT 5  |  SELECT count(*) FROM DBClientes WHERE etiquetastatus='Ativo'")
    spec = parse_sql(q)
    data = execute(spec)
    data = clean(data)
    registros = data.get("count") if isinstance(data, dict) and "count" in data else (len(data) if isinstance(data, list) else 1)
    print(json.dumps({
        "tabela": spec["table"],
        "registros": registros,
        "dados": data,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
