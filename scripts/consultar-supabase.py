#!/usr/bin/env python3
"""Consulta dados no Supabase DADOS via REST API.
Uso: consultar-supabase "SELECT * FROM DBClientes LIMIT 5"

Tabelas principais da operacao:
  DBClientes             Clientes (tabela principal)
  DBSquads               Squads
  DBPessoas              Pessoas
  11Service              Servicos
  121KickoffEE           Kickoff EE
  121Kickoff             Kickoff
  50TranscricaoCheckin   Transcricoes de check-in (combinados)
  f_gerenciador_google   Contas Google Ads
  f_gerenciador_meta     Contas Meta Ads
  f_gerenciador_*        Demais contas de campanha
"""
import os, sys, json, urllib.request, urllib.parse, re

SUPABASE_URL = os.environ.get("SUPABASE_DADOS_URL",
    "https://mhntycubvywjszweeuxs.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_DADOS_KEY")

if not SUPABASE_KEY:
    print('{"error": "SUPABASE_DADOS_KEY nao definida no ambiente"}')
    sys.exit(1)

query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
if not query:
    query = sys.stdin.read().strip()
if not query:
    print('{"error": "forneca uma consulta SQL: SELECT * FROM Tabela"}')
    sys.exit(1)

# Parse minimalist SQL
m = re.match(r"SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*?))?(?:\s+LIMIT\s+(\d+))?(?:\s+OFFSET\s+(\d+))?\s*$", query, re.IGNORECASE)
if not m:
    print(json.dumps({"error": "Formato: SELECT colunas FROM Tabela [WHERE cond] [LIMIT N] [OFFSET N]"}, ensure_ascii=False))
    sys.exit(1)

cols_raw, table, where, limit, offset = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
cols_raw = cols_raw.strip()
limit = int(limit) if limit else 20
offset = int(offset) if offset else 0

# Build URL
params = {"limit": str(min(limit, 100)), "offset": str(offset)}
if cols_raw != "*":
    params["select"] = cols_raw
if where:
    # Simple filter: col=val
    for part in where.split("AND"):
        part = part.strip()
        fm = re.match(r"(\w+)\s*=\s*'([^']*)'", part)
        if fm:
            params[f"{fm.group(1)}"] = f"eq.{fm.group(2)}"

url = f"{SUPABASE_URL}/rest/v1/{urllib.parse.quote(table, safe='')}?{urllib.parse.urlencode(params)}"

req = urllib.request.Request(url)
req.add_header("apikey", SUPABASE_KEY)
req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
req.add_header("Accept", "application/json")

try:
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read().decode())
    # Pretty print
    print(json.dumps({
        "tabela": table,
        "registros": len(data),
        "dados": data
    }, indent=2, ensure_ascii=False))
except urllib.error.HTTPError as e:
    err = e.read().decode()
    if e.code == 404:
        print(json.dumps({"error": f"Tabela '{table}' nao encontrada. Verifique o nome exato."}, ensure_ascii=False))
    elif e.code == 406:
        print(json.dumps({"error": f"Tabela '{table}' existe mas coluna especificada nao encontrada. Colunas disponiveis: {err[:300]}"}, ensure_ascii=False))
    else:
        print(json.dumps({"error": f"HTTP {e.code}: {err[:500]}"}, ensure_ascii=False))
except Exception as e:
    print(json.dumps({"error": str(e)}, ensure_ascii=False))
