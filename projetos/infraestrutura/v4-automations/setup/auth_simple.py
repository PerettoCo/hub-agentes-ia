"""Gera refresh_token do Google Ads via console (sem servidor local)."""
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CONFIG_DIR = Path(__file__).parent.parent / "config"
CREDS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.json"
ENV_FILE = CONFIG_DIR / ".env"

SCOPES = [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
]

if not CREDS_FILE.exists():
    print("ERRO: credentials.json não encontrado em", CREDS_FILE)
    exit(1)

flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
flow.redirect_uri = "http://localhost:18080"

url, _ = flow.authorization_url(prompt="consent")
print("\n" + "="*60)
print("  ABRA ESTE LINK no navegador e AUTORIZE:")
print("="*60)
print(f"\n{url}\n")
print("  Após autorizar, a pagina vai redirecionar para localhost:18080")
print("  (vai dar erro de conexao — é NORMAL).")
print("  Copie a URL COMPLETA da barra de endereco e cole abaixo.\n")

resp = input("  URL: ").strip()

code = parse_qs(urlparse(resp).query).get("code", [None])[0]
if not code:
    print("  Nao foi possivel extrair o codigo. Copie a URL inteira.")
    exit(1)

flow.fetch_token(code=code)
creds = flow.credentials

with open(TOKEN_FILE, "w") as f:
    f.write(creds.to_json())

rt = creds.refresh_token
if rt:
    env = ENV_FILE.read_text()
    lines = env.split("\n")
    for i, l in enumerate(lines):
        if l.strip().startswith("GOOGLE_ADS_REFRESH_TOKEN"):
            lines[i] = f"GOOGLE_ADS_REFRESH_TOKEN={rt}"
            break
    ENV_FILE.write_text("\n".join(lines))
    print(f"\n  OK! Refresh token salvo no .env")
    print(f"\n  Rode: python3 squads/prime/clientes/gset/consultar-campanhas.py")
else:
    print("  Sem refresh_token. Revogue o acesso em myaccount.google.com/permissions e tente de novo.")
