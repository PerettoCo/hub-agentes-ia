"""
auth_device.py — Autenticação Google via Device Code Flow (sem redirect URI).
Roda 100% no terminal, sem precisar de servidor local.

Uso: python3 v4-automations/setup/auth_device.py
"""
import os
import json
import time
from pathlib import Path
import requests

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


def auth_device():
    if not CREDENTIALS_FILE.exists():
        print(f"ERRO: {CREDENTIALS_FILE} não encontrado.")
        return

    with open(CREDENTIALS_FILE) as f:
        config = json.load(f)

    client_id = config.get("installed", {}).get("client_id") or config.get("web", {}).get("client_id")
    client_secret = config.get("installed", {}).get("client_secret") or config.get("web", {}).get("client_secret")

    if not client_id:
        print("ERRO: client_id não encontrado no credentials.json")
        return

    # ── Passo 1: Solicitar device code ─────────────────────────────────────
    print("\n" + "=" * 60)
    print("  AUTENTICAÇÃO GOOGLE")
    print("=" * 60)

    resp = requests.post("https://oauth2.googleapis.com/device/code", data={
        "client_id": client_id,
        "scope": " ".join(SCOPES),
    })
    device = resp.json()

    if "error" in device:
        print(f"ERRO: {device.get('error_description', device['error'])}")
        return

    print(f"\n  1. Acesse: {device['verification_url']}")
    print(f"\n  2. Digite o código: {device['user_code']}")
    print(f"\n  3. Faça login com a conta que gerencia o Google Ads")
    print(f"  4. Autorize as permissões")
    print(f"\n  Aguardando autorização...\n")

    # ── Passo 2: Poll até o usuário autorizar ──────────────────────────────
    interval = device.get("interval", 5)
    device_code = device["device_code"]

    for _ in range(60):  # timeout ~5 min
        time.sleep(interval)
        resp = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": client_id,
            "client_secret": client_secret,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        })
        token_data = resp.json()

        if "access_token" in token_data:
            break
        if token_data.get("error") not in ("authorization_pending", "slow_down"):
            print(f"ERRO: {token_data.get('error_description', token_data.get('error', 'desconhecido'))}")
            return
    else:
        print("Timeout: autorização não concluída.")
        return

    # ── Passo 3: Salvar tokens ────────────────────────────────────────────
    token_json = {
        "token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token", ""),
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": client_id,
        "client_secret": client_secret,
        "scopes": SCOPES,
        "expiry": None,
    }

    with open(TOKEN_FILE, "w") as f:
        json.dump(token_json, f, indent=2)
    print(f"\n  ✓ Token salvo em {TOKEN_FILE}")

    refresh_token = token_data.get("refresh_token", "")
    if refresh_token:
        print(f"\n  ✓ Refresh Token gerado!")
        print(f"\n  {refresh_token}")
        print(f"\n  Copie esse valor acima para GOOGLE_ADS_REFRESH_TOKEN no {DOTENV_FILE}")

        # Oferece já salvar no .env
        if input("\n  Quer que eu salve automaticamente no .env? (s/N): ").strip().lower() == "s":
            env_path = DOTENV_FILE
            if env_path.exists():
                content = env_path.read_text()
                if "GOOGLE_ADS_REFRESH_TOKEN" in content:
                    lines = content.split("\n")
                    new_lines = []
                    for line in lines:
                        if line.startswith("GOOGLE_ADS_REFRESH_TOKEN"):
                            new_lines.append(f"GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")
                        else:
                            new_lines.append(line)
                    env_path.write_text("\n".join(new_lines))
                else:
                    env_path.write_text(content.strip() + f"\nGOOGLE_ADS_REFRESH_TOKEN={refresh_token}\n")
                print("  ✓ Salvo no .env!")
            else:
                print(f"  .env não encontrado em {env_path}")
    else:
        print("\n  ⚠ Nenhum refresh_token retornado. Pode ser necessário revogar e tentar de novo.")

    print("\n  Pronto! Agora rode: python3 squads/prime/clientes/gset/consultar-campanhas.py\n")
    return token_data


if __name__ == "__main__":
    auth_device()
