"""
install_all.py — Setup completo do V4 Automations em um comando.

Uso:
  python3 setup/install_all.py

Faz:
  1. Verifica pré-requisitos (Python, git, pip)
  2. Cria virtual environment (.venv)
  3. Instala dependências
  4. Guia configuração de credenciais interativamente
  5. Gera .env com valores fornecidos
  6. Cria/atualiza clientes.json
  7. Roda autenticação Google OAuth
  8. Testa pipeline de email
  9. Gera relatório sample
  10. Instala crons
  11. Exibe resumo final
"""
import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import date

BASE = Path(__file__).parent.parent.resolve()
CONFIG = BASE / "config"
SETUP = BASE / "setup"
SCRIPTS = BASE / "scripts"
PYTHON = sys.executable


# ─── UTILITIES ───────────────────────────────────────────────────────────────

def step(n: int, title: str):
    print(f"\n{'='*60}")
    print(f"  PASSO {n}: {title}")
    print(f"{'='*60}")


def ok(msg: str):
    print(f"  ✅ {msg}")


def warn(msg: str):
    print(f"  ⚠️  {msg}")


def fail(msg: str):
    print(f"  ❌ {msg}")
    return False


def ask(prompt: str, default: str = "") -> str:
    if default:
        val = input(f"  {prompt} [{default}]: ").strip()
        return val if val else default
    return input(f"  {prompt}: ").strip()


def run(cmd: list[str], cwd=None) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or BASE)
        return r.returncode, r.stdout.strip()
    except FileNotFoundError:
        return -1, ""


def check_command(name: str) -> bool:
    rc, _ = run(["which", name])
    return rc == 0


# ─── MAIN SETUP ──────────────────────────────────────────────────────────────

def main():
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║        V4 Automations — Setup Completo              ║")
    print("║  Instala tudo que precisa em um único comando       ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  Repositório: {BASE}")
    print(f"  Data: {date.today().isoformat()}")
    print(f"  Python: {sys.version}")
    print()

    tudo_ok = True

    # ── PASSO 1: Pré-requisitos ────────────────────────────────────────────
    step(1, "Pré-requisitos")

    # Python 3.9+
    v = sys.version_info
    if v.major >= 3 and v.minor >= 9:
        ok(f"Python {v.major}.{v.minor}.{v.micro}")
    else:
        tudo_ok = fail(f"Python 3.9+ necessário (atual: {v.major}.{v.minor})")

    # git
    if check_command("git"):
        ok("git instalado")
    else:
        warn("git não encontrado — opcional para instalação")

    # pip
    rc, pip_ver = run([PYTHON, "-m", "pip", "--version"])
    if rc == 0:
        ok(f"pip: {pip_ver.split()[1]}")
    else:
        tudo_ok = fail("pip não encontrado")

    if not tudo_ok:
        print("\n  Corrija os erros acima e rode novamente.")
        sys.exit(1)

    # ── PASSO 2: Virtual Environment ───────────────────────────────────────
    step(2, "Virtual Environment")

    venv_path = BASE / ".venv"
    if venv_path.exists():
        ok(".venv já existe")
        venv_python = venv_path / "bin" / "python3"
        venv_pip = venv_path / "bin" / "pip"
    else:
        print("  Criando .venv...")
        rc, out = run([PYTHON, "-m", "venv", str(venv_path)])
        if rc == 0:
            ok(".venv criado")
        else:
            # Fallback: tenta criar sem ensurepip
            rc2, _ = run([PYTHON, "-m", "venv", "--without-pip", str(venv_path)])
            if rc2 == 0:
                warn("venv criado sem pip — use python3 -m pip install --user")
                print("  Instalando dependências globalmente...")
            else:
                fail("Não foi possível criar .venv")
                print("  Instalando dependências globalmente...")
        venv_python = venv_path / "bin" / "python3"
        venv_pip = venv_path / "bin" / "pip"

    # ── PASSO 3: Dependências ─────────────────────────────────────────────
    step(3, "Dependências")

    req_file = SETUP / "requirements.txt"
    if req_file.exists():
        # Tenta venv pip primeiro, depois global
        if venv_pip.exists():
            rc, out = run([str(venv_pip), "install", "-r", str(req_file)])
        else:
            rc, out = run([PYTHON, "-m", "pip", "install", "--user", "--break-system-packages", "-r", str(req_file)])

        if rc == 0:
            ok("Dependências instaladas")
        else:
            # Último fallback
            rc, out = run([PYTHON, "-m", "pip", "install", "--user", "--break-system-packages", "-r", str(req_file)])
            if rc == 0:
                ok("Dependências instaladas (modo --user)")
            else:
                tudo_ok = fail(f"Falha ao instalar dependências:\n{out}")
    else:
        fail(f"requirements.txt não encontrado em {req_file}")

    if not tudo_ok:
        print("\n  Corrija os erros acima e rode novamente.")
        sys.exit(1)

    # ── PASSO 4: Credenciais ───────────────────────────────────────────────
    step(4, "Credenciais")

    print()
    print("  Vamos configurar as credenciais passo a passo.")
    print("  Pressione Enter para pular campos que não tem agora.")
    print("  (Você pode editar manualmente o .env depois)")
    print()

    # Carrega .env existente se houver
    env_path = CONFIG / ".env"
    env_atual = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env_atual[k.strip()] = v.strip()

    env_novo = {}

    # Google
    print("  ── Google (Console Cloud) ──")
    print("  https://console.cloud.google.com → APIs → Credenciais")
    env_novo["GOOGLE_ADS_DEVELOPER_TOKEN"] = ask("Developer Token", env_atual.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""))
    env_novo["GOOGLE_ADS_CLIENT_ID"] = ask("Client ID", env_atual.get("GOOGLE_ADS_CLIENT_ID", ""))
    env_novo["GOOGLE_ADS_CLIENT_SECRET"] = ask("Client Secret", env_atual.get("GOOGLE_ADS_CLIENT_SECRET", ""))
    env_novo["GOOGLE_ADS_REFRESH_TOKEN"] = ask("Refresh Token (deixe vazio pra gerar no passo 7)", env_atual.get("GOOGLE_ADS_REFRESH_TOKEN", ""))
    env_novo["GOOGLE_ADS_LOGIN_CUSTOMER_ID"] = ask("Login Customer ID (MCC, opcional)", env_atual.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", ""))

    # Gmail
    print("  ── Gmail ──")
    env_novo["GMAIL_SENDER"] = ask("Email remetente (ex: marcos@v4company.com)", env_atual.get("GMAIL_SENDER", ""))

    # Meta
    print("  ── Meta Ads (Facebook) ──")
    print("  https://developers.facebook.com → App Business → Marketing API")
    env_novo["META_APP_ID"] = ask("App ID", env_atual.get("META_APP_ID", ""))
    env_novo["META_APP_SECRET"] = ask("App Secret", env_atual.get("META_APP_SECRET", ""))
    env_novo["META_ACCESS_TOKEN"] = ask("Access Token (longa duração)", env_atual.get("META_ACCESS_TOKEN", ""))

    # Anthropic
    print("  ── Anthropic (Claude) ──")
    print("  https://console.anthropic.com")
    env_novo["ANTHROPIC_API_KEY"] = ask("API Key", env_atual.get("ANTHROPIC_API_KEY", ""))

    # Bing (opcional)
    print("  ── Bing Ads (opcional) ──")
    env_novo["BING_ADS_DEVELOPER_TOKEN"] = ask("Developer Token", env_atual.get("BING_ADS_DEVELOPER_TOKEN", ""))
    env_novo["BING_ADS_CLIENT_ID"] = ask("Client ID", env_atual.get("BING_ADS_CLIENT_ID", ""))
    env_novo["BING_ADS_CLIENT_SECRET"] = ask("Client Secret", env_atual.get("BING_ADS_CLIENT_SECRET", ""))
    env_novo["BING_ADS_REFRESH_TOKEN"] = ask("Refresh Token", env_atual.get("BING_ADS_REFRESH_TOKEN", ""))
    env_novo["BING_ADS_CUSTOMER_ID"] = ask("Customer ID", env_atual.get("BING_ADS_CUSTOMER_ID", ""))
    env_novo["BING_ADS_ACCOUNT_ID"] = ask("Account ID", env_atual.get("BING_ADS_ACCOUNT_ID", ""))

    # NotebookLM
    print("  ── NotebookLM (opcional) ──")
    env_novo["NOTEBOOKLM_URL"] = ask("URL do NotebookLM", env_atual.get("NOTEBOOKLM_URL", ""))

    # Escreve .env
    linhas = [
        "# V4 Automations — Credenciais",
        f"# Gerado automaticamente em {date.today().isoformat()}",
        "# ATENCAO: NAO commitar este arquivo",
        "",
    ]
    for k, v in env_novo.items():
        if v:
            linhas.append(f"{k}={v}")
        else:
            linhas.append(f"#{k}=")

    CONFIG.mkdir(exist_ok=True)
    env_path.write_text("\n".join(linhas) + "\n")
    ok(f".env salvo em {env_path}")

    # ── PASSO 5: Clientes ─────────────────────────────────────────────────
    step(5, "Configuração de Clientes")

    clientes_path = CONFIG / "clientes.json"
    if clientes_path.exists():
        try:
            clientes_data = json.loads(clientes_path.read_text())
            ok(f"clientes.json encontrado ({len(clientes_data.get('clientes', []))} cliente(s))")
        except json.JSONDecodeError:
            clientes_data = {"clientes": []}
            warn("clientes.json inválido — recriando")
    else:
        clientes_data = {"clientes": []}
        warn("clientes.json não encontrado — criando")

    add = input("\n  Deseja adicionar/editar um cliente agora? (s/N): ").strip().lower()
    if add == "s":
        nome = ask("Nome do cliente")
        if nome:
            # Procura se já existe
            existente = None
            for c in clientes_data["clientes"]:
                if c["nome"].lower() == nome.lower():
                    existente = c
                    break

            if existente:
                print(f"  Cliente '{nome}' já existe — atualizando campos em branco")
                cliente = existente
            else:
                cliente = {
                    "nome": nome,
                    "google_ads_customer_id": "",
                    "meta_ad_account_id": "",
                    "bing_ads_customer_id": "",
                    "bing_ads_account_id": "",
                    "ga4_property_id": "",
                    "email_cliente": "",
                    "verba_mensal": 0,
                    "vertical": "",
                    "drive_root_folder_id": "",
                    "okrs": {
                        "objetivo": "",
                        "krs": [],
                    },
                }
                clientes_data["clientes"].append(cliente)

            cliente["google_ads_customer_id"] = ask("Google Ads Customer ID (ex: 123-456-7890)", cliente.get("google_ads_customer_id", ""))
            cliente["meta_ad_account_id"] = ask("Meta Ads Account ID (ex: act_123456789)", cliente.get("meta_ad_account_id", ""))
            cliente["ga4_property_id"] = ask("GA4 Property ID (ex: properties/123456789)", cliente.get("ga4_property_id", ""))
            cliente["email_cliente"] = ask("Email do cliente para relatórios", cliente.get("email_cliente", ""))
            cliente["verba_mensal"] = int(ask("Verba mensal (R$)", str(cliente.get("verba_mensal", 0))) or 0)
            cliente["vertical"] = ask("Vertical (ecommerce, b2b_saas, etc)", cliente.get("vertical", ""))

            clientes_path.write_text(json.dumps(clientes_data, indent=2, ensure_ascii=False) + "\n")
            ok(f"Cliente '{nome}' salvo em clientes.json")

    # ── PASSO 6: Google OAuth ──────────────────────────────────────────────
    step(6, "Autenticação Google OAuth")

    if (CONFIG / "token.json").exists():
        ok("token.json já existe")
        renovar = input("  Renovar mesmo assim? (s/N): ").strip().lower()
        if renovar == "s":
            rc, _ = run([PYTHON, str(SETUP / "auth_google.py")])
            if rc == 0:
                ok("Autenticação Google renovada")
            else:
                warn("Falha na autenticação — rode manualmente: python setup/auth_google.py")
    else:
        print("  Rodando autenticação Google...")
        rc, _ = run([PYTHON, str(SETUP / "auth_google.py")])
        if rc == 0:
            ok("Autenticação Google concluída")
        else:
            warn("Autenticação falhou — verifique se credentials.json está em config/")

    # ── PASSO 7: Teste de Email ─────────────────────────────────────────────
    step(7, "Teste de Pipeline")

    if env_novo.get("GMAIL_SENDER"):
        print("  Enviando email de teste...")
        test_script = """
import sys
sys.path.insert(0, '{base}')
from scripts.connectors import GmailConnector
gmail = GmailConnector()
gmail.send(
    to='{email}',
    subject='V4 Automations — Setup concluído',
    body_html='<h1>V4 Automations</h1><p>Setup concluído com sucesso em {data}!</p>'
)
print('Email enviado!')
""".format(base=BASE, email=env_novo["GMAIL_SENDER"], data=date.today().isoformat())

        test_file = BASE / "setup" / "_test_email.py"
        test_file.write_text(test_script)
        rc, out = run([PYTHON, str(test_file)])
        test_file.unlink()

        if rc == 0:
            ok(f"Email de teste enviado para {env_novo['GMAIL_SENDER']}")
        else:
            warn(f"Falha no email de teste: ative a Gmail API no Google Cloud Console")
    else:
        warn("GMAIL_SENDER não configurado — pulando teste de email")

    # ── PASSO 8: Relatório Sample ──────────────────────────────────────────
    step(8, "Relatório Sample (ilustrativo)")

    rc, out = run([PYTHON, str(SCRIPTS / "gt" / "relatorio_trafego.py"),
                   "--cliente", clientes_data["clientes"][0]["nome"] if clientes_data["clientes"] else "Cliente A",
                   "--days", "7", "--format", "html",
                   "--sample", "--out", str(BASE / "relatorios")])

    if rc == 0:
        ok("Relatório sample gerado em relatorios/")
    else:
        warn("Falha ao gerar relatório sample")

    # ── PASSO 9: Crons ─────────────────────────────────────────────────────
    step(9, "Instalação de Crons")

    instalar = input("\n  Instalar crons automáticos? (s/N): ").strip().lower()
    if instalar == "s":
        rc, out = run([PYTHON, str(SETUP / "install_cron.py")])
        if rc == 0:
            ok("Crons instalados")
        else:
            warn("Falha ao instalar crons")
    else:
        print("  Pulando — rode depois: python setup/install_cron.py")

    # ── RESUMO FINAL ───────────────────────────────────────────────────────
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║           SETUP CONCLUÍDO — RESUMO                   ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    checks = [
        (".venv criado", venv_path.exists()),
        ("Dependências instaladas", req_file.exists()),
        (".env configurado", env_path.exists()),
        ("clientes.json configurado", clientes_path.exists()),
        ("token.json (OAuth)", (CONFIG / "token.json").exists()),
        ("credentials.json pronto", (CONFIG / "credentials.json").exists()),
    ]
    for label, status in checks:
        print(f"  {'✅' if status else '⬜'} {label}")

    print()
    print("  Próximos passos:")
    print()
    print("  • Relatório com dados reais:")
    print(f"    python3 scripts/gt/relatorio_trafego.py \\")
    print(f"      --cliente \"{clientes_data['clientes'][0]['nome'] if clientes_data['clientes'] else '<nome>'}\" \\")
    print(f"      --days 7 --format html --email {env_novo.get('GMAIL_SENDER', '<seu-email>')}")
    print()
    print("  • Relatório ilustrativo (sem API):")
    print(f"    python3 scripts/gt/relatorio_trafego.py \\")
    print(f"      --cliente \"{clientes_data['clientes'][0]['nome'] if clientes_data['clientes'] else '<nome>'}\" \\")
    print(f"      --days 7 --format html --sample")
    print()
    if env_novo.get("NOTEBOOKLM_URL"):
        print("  • NotebookLM configurado:")
        print(f"    {env_novo['NOTEBOOKLM_URL']}")
        print()
    print("  • Documentação completa:")
    print("    docs/v4-automations-guia-instalacao.md")
    print("    documentação/")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Setup interrompido pelo usuário.")
        sys.exit(0)
