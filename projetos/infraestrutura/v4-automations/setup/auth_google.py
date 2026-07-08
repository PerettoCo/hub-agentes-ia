"""
auth_google.py — Roda UMA VEZ para autenticar com Google.
Depois disso o token.json é renovado automaticamente.

Uso: python setup/auth_google.py
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

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/adwords",
]

def authenticate():
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Token renovado automaticamente.")
        else:
            if not CREDENTIALS_FILE.exists():
                print(f"ERRO: {CREDENTIALS_FILE} não encontrado.")
                print("Baixe o credentials.json do Google Cloud Console e coloque em config/")
                return

            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
            print("Autenticação concluída.")

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print(f"Token salvo em {TOKEN_FILE}")

    print("Google OAuth: OK")
    return creds

if __name__ == "__main__":
    authenticate()
