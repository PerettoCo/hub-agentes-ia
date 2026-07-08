"""
auth_setup.py — Autenticação Google passo a passo para Desktop App.
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


def run():
    print("=" * 60)
    print("  AUTENTICAÇÃO GOOGLE ADS")
    print("=" * 60)

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.valid:
        print("\n  ✓ Já autenticado!")
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print("Token renovado automaticamente.")
        return creds

    if not CREDENTIALS_FILE.exists():
        print(f"\n  ERRO: {CREDENTIALS_FILE} não encontrado.")

        # Link direto pra criar Desktop App credential
        print(f"""
  PASSO A PASSO:

  1. Abra: https://console.cloud.google.com/apis/credentials

  2. Clique em "+ CREATE CREDENTIALS" → "OAuth client ID"

  3. Application type: escolha "Desktop app"

  4. Nome: "V4 Automations Desktop"

  5. Clique em "CREATE"

  6. No popup, clique em "DOWNLOAD JSON"

  7. Salve o arquivo como:
     {CREDENTIALS_FILE}
""")
        return

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)

    print(f"\n  Vou tentar autenticar...")
    print(f"  (Se falhar com redirect_uri_mismatch, siga as instruções abaixo)")
    print(f"\n  Se der erro, acesse este link e adicione 'http://localhost:8080'")
    print(f"  como Authorized redirect URI:")
    print(f"\n  https://console.cloud.google.com/apis/credentials")
    print(f"\n  Depois volte e rode de novo.\n")

    PORT = 18080
    print(f"  Usando porta: {PORT}")
    print(f"\n  ⚠ SE FALHAR COM redirect_uri_mismatch:")
    print(f"  1. Abra: https://console.cloud.google.com/apis/credentials")
    print(f"  2. Edite sua credencial (lápis)")
    print(f"  3. Em 'Authorized redirect URIs' → ADD URI:")
    print(f"     http://localhost:{PORT}")
    print(f"  4. Salve e rode de novo\n")

    try:
        creds = flow.run_local_server(
            port=PORT,
            authorization_prompt_message="",
            success_message="Autenticado! Volte ao terminal.",
        )
    except Exception as e:
        if "redirect_uri_mismatch" in str(e):
            print(f"\n  ✗ redirect_uri_mismatch.")
            print(f"\n  Faça isso rápido:")
            print(f"  1. Abra: https://console.cloud.google.com/apis/credentials")
            print(f"  2. Clique no lápis da sua credencial (editar)")
            print(f"  3. Em 'Authorized redirect URIs', clique 'ADD URI'")
            print(f"  4. Digite: http://localhost:8080")
            print(f"  5. Clique 'Save' no final")
            print(f"  6. Rode este script de novo\n")
        else:
            print(f"Erro: {e}")
        return

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    print(f"\n  ✓ Token salvo!")

    if creds.refresh_token:
        print(f"\n  ✓ Refresh Token:")
        print(f"  {creds.refresh_token}")
        if DOTENV_FILE.exists():
            content = DOTENV_FILE.read_text()
            if "GOOGLE_ADS_REFRESH_TOKEN" in content:
                lines = content.split("\n")
                new_lines = []
                for line in lines:
                    if line.startswith("GOOGLE_ADS_REFRESH_TOKEN"):
                        new_lines.append(f"GOOGLE_ADS_REFRESH_TOKEN={creds.refresh_token}")
                    else:
                        new_lines.append(line)
                DOTENV_FILE.write_text("\n".join(new_lines))
                print(f"  ✓ Salvo automaticamente no .env!")
            else:
                with open(DOTENV_FILE, "a") as f:
                    f.write(f"\nGOOGLE_ADS_REFRESH_TOKEN={creds.refresh_token}\n")
                print(f"  ✓ Salvo no .env!")
        print(f"\n  Pronto! Rode: python3 squads/prime/clientes/gset/consultar-campanhas.py")
    else:
        print("  ⚠ Sem refresh_token. Pode precisar revogar acesso e tentar de novo.")

    return creds


if __name__ == "__main__":
    run()
