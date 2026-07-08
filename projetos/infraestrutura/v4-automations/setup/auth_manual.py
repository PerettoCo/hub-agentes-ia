"""
auth_manual.py — Autenticação Google manual.
Sem servidor local. Você cola o código de autorização.
"""
import os
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CONFIG_DIR = Path(__file__).parent.parent / "config"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.json"
DOTENV_FILE = CONFIG_DIR / ".env"

SCOPES = [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]


def salvar_refresh_token(refresh_token):
    if refresh_token and DOTENV_FILE.exists():
        content = DOTENV_FILE.read_text()
        if "GOOGLE_ADS_REFRESH_TOKEN" in content:
            lines = content.split("\n")
            new_lines = []
            for line in lines:
                if line.strip().startswith("GOOGLE_ADS_REFRESH_TOKEN"):
                    new_lines.append(f"GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")
                else:
                    new_lines.append(line)
            DOTENV_FILE.write_text("\n".join(new_lines))
        else:
            with open(DOTENV_FILE, "a") as f:
                f.write(f"\nGOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n")
        print(f"  ✓ Salvo no .env!")


def run():
    print("=" * 60)
    print("  AUTENTICAÇÃO GOOGLE ADS — MANUAL")
    print("=" * 60)

    if not CREDENTIALS_FILE.exists():
        print(f"\n  ERRO: {CREDENTIALS_FILE} não encontrado.\n")
        print(f"  Crie uma credencial Desktop App em:")
        print(f"  https://console.cloud.google.com/apis/credentials")
        print(f"  Baixe o JSON e salve em {CREDENTIALS_FILE}")
        return

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)

    # Gera URL de autorização
    auth_url, _ = flow.authorization_url(prompt="consent")

    print(f"\n  PASSO 1 — Abra este link no navegador:\n")
    print(f"  {auth_url}")
    print(f"\n  Faça login com a conta que gerencia o Google Ads da GSET")
    print(f"  e autorize as permissões.")
    print(f"\n  Após autorizar, o navegador vai redirecionar para")
    print(f"  http://localhost:18080 (vai dar erro de página não encontrada —")
    print(f"  é normal!).")
    print(f"\n  PASSO 2 — Copie a URL COMPLETA da barra de endereço")
    print(f"  (começa com http://localhost:18080/...)")
    print(f"  e cole abaixo:\n")

    redirect_response = input("  URL redirecionada: ").strip()

    # Extrai o código da URL
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(redirect_response)
    params = parse_qs(parsed.query)
    code = params.get("code", [None])[0]

    if not code:
        print(f"\n  ✗ Não foi possível extrair o código da URL.")
        print(f"  Certifique-se de copiar a URL completa.\n")
        return

    flow.fetch_token(code=code)
    creds = flow.credentials

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    print(f"\n  ✓ Token salvo em {TOKEN_FILE}")

    if creds.refresh_token:
        print(f"\n  ✓ Refresh Token:")
        print(f"  {creds.refresh_token}")
        salvar_refresh_token(creds.refresh_token)
    else:
        print(f"\n  ⚠ Sem refresh_token. Tente de novo revogando o acesso primeiro.")
        print(f"  Acesse: https://myaccount.google.com/permissions")
        print(f"  Remova o acesso do app e tente novamente.\n")
        return

    print(f"\n  ✓ Pronto! Agora rode:")
    print(f"  python3 squads/prime/clientes/gset/consultar-campanhas.py\n")


if __name__ == "__main__":
    run()
