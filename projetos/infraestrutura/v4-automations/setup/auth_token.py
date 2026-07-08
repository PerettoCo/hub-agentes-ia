"""Gera refresh token do Google Ads em 2 passos."""
import json, sys, time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import InstalledAppFlow

CONFIG = Path(__file__).parent.parent / "config"
STATE_FILE = CONFIG / "auth_state.json"
ENV_FILE = CONFIG / ".env"
SCOPES = ["https://www.googleapis.com/auth/adwords",
          "https://www.googleapis.com/auth/analytics.readonly",
          "https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/drive"]

def step1():
    flow = InstalledAppFlow.from_client_secrets_file(str(CONFIG / "credentials.json"), SCOPES)
    flow.redirect_uri = "http://localhost"
    url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="false")
    STATE_FILE.write_text(json.dumps({"url": url, "redirect_uri": "http://localhost"}))
    print(url)

def step2(code):
    flow = InstalledAppFlow.from_client_secrets_file(str(CONFIG / "credentials.json"), SCOPES)
    flow.redirect_uri = "http://localhost"
    flow.fetch_token(code=code)
    creds = flow.credentials
    CONFIG.joinpath("token.json").write_text(creds.to_json())
    rt = creds.refresh_token
    if rt:
        env = ENV_FILE.read_text()
        lines = env.split("\n")
        for i, l in enumerate(lines):
            if l.strip().startswith("GOOGLE_ADS_REFRESH_TOKEN"):
                lines[i] = f"GOOGLE_ADS_REFRESH_TOKEN={rt}"
                break
        ENV_FILE.write_text("\n".join(lines))
        print(f"REFRESH_TOKEN={rt}")
        print("Salvo no .env!")
    else:
        print("ERRO: sem refresh_token")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--code":
        step2(sys.argv[2])
    else:
        step1()
