"""
connectors.py — Conectores de API compartilhados por todos os scripts.
Importar com: from scripts.connectors import GoogleAdsClient, MetaClient, GA4Client, GmailClient
"""
import os
import json
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Metric, Dimension
)
from google.ads.googleads.client import GoogleAdsClient as GAdsClient
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

BASE = Path(__file__).parent.parent
load_dotenv(BASE / "config" / ".env")
_ROOT_ENV = BASE.parent / ".env"
if _ROOT_ENV.exists():
    load_dotenv(_ROOT_ENV, override=False)

TOKEN_FILE = BASE / "config" / "token.json"
CREDS_FILE = BASE / "config" / "credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/adwords",
]


def _get_google_creds():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
    return creds


# ── GOOGLE ADS ──────────────────────────────────────────────────────────────

class GoogleAdsConnector:
    def __init__(self):
        self.client = GAdsClient.load_from_dict({
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "use_proto_plus": True,
        })

    def get_performance(self, customer_id: str, days: int = 7) -> dict:
        """Pega performance dos últimos N dias para uma conta."""
        customer_id = customer_id.replace("-", "")
        ga_service = self.client.get_service("GoogleAdsService")

        query = f"""
            SELECT
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversion_value,
                metrics.clicks,
                metrics.impressions,
                metrics.ctr,
                metrics.average_cpc
            FROM campaign
            WHERE segments.date DURING LAST_{days}_DAYS
            AND campaign.status = 'ENABLED'
        """

        response = ga_service.search(customer_id=customer_id, query=query)

        total_cost = 0
        total_conversions = 0
        total_conversion_value = 0
        total_clicks = 0

        for row in response:
            total_cost += row.metrics.cost_micros / 1_000_000
            total_conversions += row.metrics.conversions
            total_conversion_value += row.metrics.conversion_value
            total_clicks += row.metrics.clicks

        roas = total_conversion_value / total_cost if total_cost > 0 else 0
        cpc = total_cost / total_clicks if total_clicks > 0 else 0
        cpa = total_cost / total_conversions if total_conversions > 0 else 0

        return {
            "canal": "Google Ads",
            "investimento": round(total_cost, 2),
            "conversoes": round(total_conversions, 1),
            "receita_atribuida": round(total_conversion_value, 2),
            "roas": round(roas, 2),
            "cpc": round(cpc, 2),
            "cpa": round(cpa, 2),
            "cliques": total_clicks,
        }

    def get_pace(self, customer_id: str, verba_mensal: float) -> dict:
        """Calcula pace de verba: quanto gastou vs quanto deveria ter gasto até hoje."""
        from datetime import date
        hoje = date.today()
        dias_no_mes = 30
        dias_passados = hoje.day
        pace_esperado = verba_mensal * (dias_passados / dias_no_mes)

        perf = self.get_performance(customer_id, days=dias_passados)
        gasto_atual = perf["investimento"]

        diferenca = gasto_atual - pace_esperado
        status = "ok" if abs(diferenca / pace_esperado) < 0.1 else ("acima" if diferenca > 0 else "abaixo")

        return {
            "verba_mensal": verba_mensal,
            "gasto_ate_hoje": round(gasto_atual, 2),
            "pace_esperado": round(pace_esperado, 2),
            "diferenca": round(diferenca, 2),
            "percentual_diferenca": round((diferenca / pace_esperado) * 100, 1),
            "status": status,
        }


# ── META ADS ────────────────────────────────────────────────────────────────

class MetaConnector:
    def __init__(self):
        FacebookAdsApi.init(
            app_id=os.getenv("META_APP_ID"),
            app_secret=os.getenv("META_APP_SECRET"),
            access_token=os.getenv("META_ACCESS_TOKEN"),
        )

    def get_performance(self, ad_account_id: str, days: int = 7) -> dict:
        """Pega performance dos últimos N dias para uma conta Meta."""
        from datetime import date, timedelta
        hoje = date.today()
        inicio = (hoje - timedelta(days=days)).strftime("%Y-%m-%d")
        fim = hoje.strftime("%Y-%m-%d")

        account = AdAccount(ad_account_id)
        insights = account.get_insights(params={
            "time_range": {"since": inicio, "until": fim},
            "fields": ["spend", "actions", "action_values", "clicks", "impressions", "ctr", "cpm", "frequency"],
            "level": "account",
        })

        if not insights:
            return {"canal": "Meta Ads", "erro": "sem dados"}

        data = insights[0]
        spend = float(data.get("spend", 0))
        clicks = int(data.get("clicks", 0))
        impressions = int(data.get("impressions", 0))
        ctr = float(data.get("ctr", 0))
        cpm = float(data.get("cpm", 0))
        frequency = float(data.get("frequency", 0))

        conversions = 0
        conversion_value = 0
        for action in data.get("actions", []):
            if action["action_type"] in ["purchase", "lead", "complete_registration"]:
                conversions += float(action["value"])
        for av in data.get("action_values", []):
            if av["action_type"] == "purchase":
                conversion_value += float(av["value"])

        roas = conversion_value / spend if spend > 0 else 0
        cpa = spend / conversions if conversions > 0 else 0

        return {
            "canal": "Meta Ads",
            "investimento": round(spend, 2),
            "conversoes": round(conversions, 1),
            "receita_atribuida": round(conversion_value, 2),
            "roas": round(roas, 2),
            "cpa": round(cpa, 2),
            "ctr": round(ctr, 2),
            "cpm": round(cpm, 2),
            "frequencia": round(frequency, 2),
            "cliques": clicks,
            "impressoes": impressions,
        }


# ── GA4 ─────────────────────────────────────────────────────────────────────

class GA4Connector:
    def __init__(self):
        creds = _get_google_creds()
        self.client = BetaAnalyticsDataClient(credentials=creds)

    def get_performance(self, property_id: str, days: int = 7) -> dict:
        """Pega sessões, conversões e taxa de conversão dos últimos N dias."""
        request = RunReportRequest(
            property=property_id,
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="conversions"),
                Metric(name="sessionConversionRate"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
            ],
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        )

        response = self.client.run_report(request)

        canais = {}
        total_sessions = 0
        total_conversions = 0

        for row in response.rows:
            canal = row.dimension_values[0].value
            sessions = int(row.metric_values[0].value)
            convs = float(row.metric_values[1].value)
            total_sessions += sessions
            total_conversions += convs
            canais[canal] = {
                "sessoes": sessions,
                "conversoes": round(convs, 1),
                "taxa_conversao": round(float(row.metric_values[2].value) * 100, 2),
            }

        taxa_geral = (total_conversions / total_sessions * 100) if total_sessions > 0 else 0

        return {
            "total_sessoes": total_sessions,
            "total_conversoes": round(total_conversions, 1),
            "taxa_conversao_geral": round(taxa_geral, 2),
            "por_canal": canais,
        }


# ── GMAIL ───────────────────────────────────────────────────────────────────

class GmailConnector:
    def __init__(self):
        creds = _get_google_creds()
        self.service = build("gmail", "v1", credentials=creds)
        self.sender = os.getenv("GMAIL_SENDER")

    def send(self, to: str | list, subject: str, body_html: str):
        """Envia email HTML. to pode ser string ou lista de emails."""
        if isinstance(to, list):
            to = ", ".join(to)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = to
        msg.attach(MIMEText(body_html, "html"))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        self.service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        print(f"Email enviado para {to}: {subject}")


# ── ANTHROPIC ───────────────────────────────────────────────────────────────

import anthropic as _anthropic

def claude(system: str, user: str, max_tokens: int = 2000) -> str:
    """Chama API LLM com system + user prompt. Retorna texto.
    Tenta: OpenRouter → Anthropic Claude → Google Gemini, nessa ordem.
    Cada fallback só é ativado se a API key correspondente existir.
    """
    errors = []

    or_key = os.getenv("OPENROUTER_API_KEY")
    if or_key:
        try:
            from openai import OpenAI
            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=or_key)
            messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content
        except Exception as e:
            errors.append(f"OpenRouter: {e}")

    anthro_key = os.getenv("ANTHROPIC_API_KEY")
    if anthro_key:
        try:
            client = _anthropic.Anthropic(api_key=anthro_key)
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return msg.content[0].text
        except Exception as e:
            errors.append(f"Anthropic: {e}")

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                system_instruction=system,
            )
            resp = model.generate_content(user, generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens))
            return resp.text
        except Exception as e:
            errors.append(f"Gemini: {e}")

    raise RuntimeError(f"Nenhuma API LLM respondeu. Erros: {'; '.join(errors)}")


# ── BING ADS ────────────────────────────────────────────────────────────────

class BingAdsConnector:
    """Microsoft Advertising (Bing Ads) — usa Microsoft Advertising SDK."""

    def __init__(self):
        from bingads.service_client import ServiceClient
        self.developer_token = os.getenv("BING_ADS_DEVELOPER_TOKEN")
        self.client_id = os.getenv("BING_ADS_CLIENT_ID")
        self.client_secret = os.getenv("BING_ADS_CLIENT_SECRET")
        self.refresh_token = os.getenv("BING_ADS_REFRESH_TOKEN")
        self.customer_id = os.getenv("BING_ADS_CUSTOMER_ID")
        self.account_id = os.getenv("BING_ADS_ACCOUNT_ID")

        authentication = {
            "DeveloperToken": self.developer_token,
            "ClientId": self.client_id,
            "ClientSecret": self.client_secret,
            "RefreshToken": self.refresh_token,
        }
        self.service = ServiceClient(
            service="ReportingService",
            version=13,
            authentication=authentication,
            environment="production",
            customer_id=self.customer_id,
            account_id=self.account_id,
        )

    def get_performance(self, days: int = 7) -> dict:
        """Pega performance dos últimos N dias para a conta Bing."""
        from bingads.v13.reporting import (
            ReportAggregation, CampaignPerformanceReportRequest, ReportTime
        )
        from datetime import date, timedelta
        hoje = date.today()
        inicio = (hoje - timedelta(days=days))

        report_request = CampaignPerformanceReportRequest(
            format="Csv",
            report_name="Bing Ads Performance",
            return_only_complete_data=True,
            aggregation=ReportAggregation.SUMMARY,
            time=ReportTime(
                custom_date_range_start=inicio.strftime("%Y-%m-%d"),
                custom_date_range_end=hoje.strftime("%Y-%m-%d"),
            ),
            columns=[
                "Spend", "Conversions", "Revenue", "Clicks",
                "Impressions", "Ctr", "Cpc", "ReturnOnAdSpend",
            ],
        )
        try:
            result = self.service.download_report(report_request)
            rows = result.strip().split("\n")[1:]  # Skip header
            total_spend = 0.0
            total_conversions = 0.0
            total_revenue = 0.0
            total_clicks = 0

            for row in rows:
                cols = row.split(",")
                if len(cols) >= 8:
                    total_spend += float(cols[0] or 0)
                    total_conversions += float(cols[1] or 0)
                    total_revenue += float(cols[2] or 0)
                    total_clicks += int(float(cols[3] or 0))

            roas = total_revenue / total_spend if total_spend > 0 else 0
            cpc = total_spend / total_clicks if total_clicks > 0 else 0
            cpa = total_spend / total_conversions if total_conversions > 0 else 0

            return {
                "canal": "Bing Ads",
                "investimento": round(total_spend, 2),
                "conversoes": round(total_conversions, 1),
                "receita_atribuida": round(total_revenue, 2),
                "roas": round(roas, 2),
                "cpc": round(cpc, 2),
                "cpa": round(cpa, 2),
                "cliques": total_clicks,
            }
        except Exception as e:
            return {"canal": "Bing Ads", "erro": str(e)}


# ── GOOGLE DRIVE ────────────────────────────────────────────────────────────

class DriveConnector:
    """Google Drive — upload, create folders, list files."""

    def __init__(self):
        creds = _get_google_creds()
        self.service = build("drive", "v1", credentials=creds)

    def create_folder(self, name: str, parent_id: str | None = None) -> str:
        """Cria uma pasta no Drive. Retorna o ID."""
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]
        folder = self.service.files().create(body=metadata, fields="id").execute()
        return folder["id"]

    def upload_json(self, content: dict, filename: str, parent_id: str | None = None) -> str:
        """Faz upload de um JSON para o Drive. Retorna o fileId."""
        from googleapiclient.http import MediaIoBaseUpload
        import io
        json_bytes = json.dumps(content, ensure_ascii=False, indent=2, default=str).encode("utf-8")
        media = MediaIoBaseUpload(io.BytesIO(json_bytes), mimetype="application/json", resumable=True)
        metadata = {"name": filename, "mimeType": "application/json"}
        if parent_id:
            metadata["parents"] = [parent_id]
        file = self.service.files().create(body=metadata, media_body=media, fields="id").execute()
        return file["id"]

    def upload_markdown(self, content: str, filename: str, parent_id: str | None = None) -> str:
        """Faz upload de markdown como Google Doc."""
        import io
        from googleapiclient.http import MediaIoBaseUpload
        md_bytes = content.encode("utf-8")
        media = MediaIoBaseUpload(io.BytesIO(md_bytes), mimetype="text/markdown", resumable=True)
        metadata = {"name": filename, "mimeType": "text/markdown"}
        if parent_id:
            metadata["parents"] = [parent_id]
        file = self.service.files().create(body=metadata, media_body=media, fields="id").execute()
        return file["id"]

    def find_folder(self, name: str, parent_id: str | None = None) -> str | None:
        """Busca uma pasta por nome. Retorna o ID ou None."""
        q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            q += f" and '{parent_id}' in parents"
        results = self.service.files().list(q=q, fields="files(id,name)", pageSize=10).execute()
        files = results.get("files", [])
        return files[0]["id"] if files else None

    def ensure_folder(self, path: list[str], root_id: str | None = None) -> str:
        """Garante que uma hierarquia de pastas existe. Cria o que faltar. Ex: ['Clientes', 'Cliente X', 'Relatorios']"""
        current_id = root_id
        for part in path:
            found = self.find_folder(part, parent_id=current_id)
            if found:
                current_id = found
            else:
                current_id = self.create_folder(part, parent_id=current_id)
        return current_id


# ── CLIENTES ────────────────────────────────────────────────────────────────

def load_clientes() -> list:
    path = BASE / "config" / "clientes.json"
    with open(path) as f:
        return json.load(f)["clientes"]
