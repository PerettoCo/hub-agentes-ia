# V4 Automations — Guia de Instalação e Configuração

## Sobre

O **V4 Automations** é o sistema de agentes automatizados da V4 Company. Coleta dados de plataformas de anúncios (Google Ads, Meta Ads, Bing Ads), processa com IA (Claude) e entrega relatórios por e-mail e Google Drive — sem intervenção humana.

---

## 1. Pré-requisitos

- Python 3.9+
- Acesso ao Google Cloud Console
- Conta no Facebook Developers
- Chave API Anthropic (Claude)
- Acesso ao Google Ads (conta MCC)

---

## 2. Estrutura de Diretórios

```
v4-automations/
├── config/
│   ├── .env                  ← Chaves de API (NUNCA commitar)
│   ├── credentials.json      ← OAuth Google (NUNCA commitar)
│   ├── token.json            ← Gerado automaticamente na autenticação
│   └── clientes.json         ← Dados dos clientes (contas, OKRs)
├── setup/
│   ├── requirements.txt      ← Dependências Python
│   ├── auth_google.py        ← Autenticação OAuth (roda 1x)
│   └── install_cron.py       ← Instala crons automáticos
├── scripts/
│   ├── connectors.py         ← Biblioteca compartilhada de APIs
│   ├── gt/
│   │   ├── relatorio_trafego.py   ← Relatório consolidado multicanal
│   │   └── analise_performance.py ← Análise semanal GT
│   ├── am/
│   │   ├── atualizar_okrs.py      ← Atualização de OKRs
│   │   └── enviar_nps.py          ← Pesquisa NPS/CSAT
│   ├── copy/
│   │   ├── pipeline_conteudo.py   ← Pipeline editorial
│   │   └── briefing_criativo.py   ← Briefing criativo
│   ├── coordenador/
│   │   ├── briefing_comite.py     ← Briefing do comitê
│   │   └── checklist.py           ← Checklist de conformidade
│   └── ekyte/
│       ├── connector.py           ← Conector Ekyte
│       ├── sprints.py             ← Gestão de sprints
│       └── fca.py                 ← Criação de FCAs
└── cron/
    └── crontab.txt           ← Agenda de referência
```

---

## 3. Instalação Passo a Passo

### 3.1. Dependências Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r setup/requirements.txt
```

### 3.2. Credenciais Google (OAuth2)

1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. Crie um projeto: **v4-automations**
3. Ative as APIs:
   - Google Ads API
   - Google Analytics Data API (GA4)
   - Gmail API
   - Google Drive API
4. Vá em **APIs e Serviços → Credenciais**
5. Crie credenciais **OAuth 2.0** (tipo: Aplicativo para desktop)
6. Baixe o JSON → renomeie para `credentials.json`
7. Coloque em `config/credentials.json`
8. Rode a autenticação:

```bash
python setup/auth_google.py
```

Isso abre o navegador uma vez. Faça login com a conta Google da V4. Um `token.json` será salvo automaticamente.

### 3.3. Meta Ads (Facebook)

1. Acesse [developers.facebook.com](https://developers.facebook.com)
2. Crie um App (tipo: **Business**)
3. Adicione o produto **Marketing API**
4. Gere um **User Access Token** com permissões:
   - `ads_read`
   - `ads_management`
   - `business_management`
5. Converta para token de longa duração (60 dias)
6. Adicione no `config/.env`:

```env
META_APP_ID=seu_app_id
META_APP_SECRET=seu_app_secret
META_ACCESS_TOKEN=seu_token_de_longa_duracao
```

### 3.4. Chave Anthropic (Claude)

1. Acesse [console.anthropic.com](https://console.anthropic.com)
2. Gere uma API Key
3. Adicione no `config/.env`:

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

### 3.5. Google Ads (Developer Token)

1. Acesse [ads.google.com](https://ads.google.com/home/tools/manager-accounts)
2. Crie ou acesse sua conta MCC (Manager)
3. Menu: **Ferramentas → Centro de API**
4. Solicite acesso ao Developer Token
5. Adicione no `config/.env`:

```env
GOOGLE_ADS_DEVELOPER_TOKEN=seu_token
GOOGLE_ADS_CLIENT_ID=seu_client_id
GOOGLE_ADS_CLIENT_SECRET=seu_client_secret
GOOGLE_ADS_REFRESH_TOKEN=seu_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID= (opicional, se usar MCC)
```

### 3.6. Gmail (Remetente)

```env
GMAIL_SENDER=seu-email@v4company.com
```

### 3.7. Bing Ads (Opcional)

```env
BING_ADS_DEVELOPER_TOKEN=
BING_ADS_CLIENT_ID=
BING_ADS_CLIENT_SECRET=
BING_ADS_REFRESH_TOKEN=
BING_ADS_CUSTOMER_ID=
BING_ADS_ACCOUNT_ID=
```

---

## 4. Configurar Clientes

Edite `config/clientes.json`. Schema completo:

```json
{
  "clientes": [
    {
      "nome": "Cliente X",
      "google_ads_customer_id": "123-456-7890",
      "meta_ad_account_id": "act_123456789",
      "bing_ads_customer_id": null,
      "bing_ads_account_id": null,
      "ga4_property_id": "properties/123456789",
      "email_cliente": "contato@cliente.com",
      "verba_mensal": 5000,
      "vertical": "ecommerce",
      "drive_root_folder_id": null,
      "okrs": {
        "objetivo": "Descrição do objetivo",
        "krs": [
          { "descricao": "ROAS médio", "meta": 3.2, "unidade": "x", "atual": 0 },
          { "descricao": "Leads mensais", "meta": 150, "unidade": "leads", "atual": 0 }
        ]
      }
    }
  ]
}
```

---

## 5. Testar o Pipeline

### 5.1. Teste de envio de e-mail

```bash
python3 -c "
import sys
sys.path.insert(0, '.')
from scripts.connectors import GmailConnector
gmail = GmailConnector()
gmail.send(
    to='seu-email@v4company.com',
    subject='Teste — Pipeline OK',
    body_html='<h1>v4-automations funciona!</h1>'
)
"
```

### 5.2. Relatório de tráfego (dados sample)

```bash
python3 scripts/gt/relatorio_trafego.py \
    --cliente "Cliente A" \
    --days 7 \
    --format html \
    --sample \
    --email seu-email@v4company.com
```

### 5.3. Relatório com dados reais

```bash
python3 scripts/gt/relatorio_trafego.py \
    --cliente "Cliente X" \
    --days 7 \
    --format html \
    --email seu-email@v4company.com
```

### 5.4. Relatório para todos os clientes

```bash
python3 scripts/gt/relatorio_trafego.py \
    --all \
    --days 30 \
    --format html \
    --email seu-email@v4company.com
```

---

## 6. Relatório de Tráfego — Flags

| Flag                            | Descrição                            |
| ------------------------------- | ------------------------------------ |
| `--cliente "Nome"`              | Cliente específico                   |
| `--all`                         | Todos os clientes                    |
| `--days N`                      | Janela em dias (padrão: 7)           |
| `--format html\|json\|terminal` | Formato de saída                     |
| `--sample`                      | Usa dados ilustrativos (ignora APIs) |
| `--email email@com`             | Envia por e-mail                     |
| `--drive`                       | Salva no Google Drive                |
| `--claude`                      | Inclui análise via IA                |
| `--out ./pasta`                 | Diretório de saída                   |

---

## 7. Agendar Crons

```bash
python setup/install_cron.py
```

Agenda gerada:

| Dia | Horário | Tarefa |
|---|---|---|
| Domingo | 20:00 | Briefing do Comitê P&EG |
| Quinta | 07:00 | Análise de performance GT |
| Quinta | 08:00 | Atualização de OKRs |
| Sexta | 16:00 | Checklist de conformidade |
| Dia 1 do mês | 08:00 | Pesquisa NPS/CSAT |

---

## 8. Troubleshooting

| Problema | Causa | Solução |
|---|---|---|
| `ModuleNotFoundError` | Dependências não instaladas | `pip install -r setup/requirements.txt` |
| `Gmail API not enabled` | API não ativada no projeto GCP | Ativar em console.cloud.google.com |
| `CUSTOMER_NOT_FOUND` | Customer ID errado no clientes.json | Verificar ID no Google Ads |
| `(#200) Provide valid app ID` | Meta sem credentials no .env | Preencher META_APP_ID/SECRET/ACCESS_TOKEN |
| `OAuth token expired` | Token Google expirado | Rodar `python setup/auth_google.py` |
| Dados de hoje incompletos | Latência Facebook + sync V4mos | Usar `--days` com margem de 3 dias |
| Cache V4mos | Dados repetidos em 30min | Aguardar ou variar período |

---

## 9. Conectores Disponíveis

| Conector | Classe | APIs |
|---|---|---|
| Google Ads | `GoogleAdsConnector` | Investimento, ROAS, CPC, CPA, cliques |
| Meta Ads | `MetaConnector` | Investimento, ROAS, CTR, CPM, frequência |
| Bing Ads | `BingAdsConnector` | Investimento, ROAS, CPC, cliques |
| GA4 | `GA4Connector` | Sessões, conversões, taxa por canal |
| Gmail | `GmailConnector` | Envio de e-mail HTML |
| Google Drive | `DriveConnector` | Upload JSON/Markdown, criar pastas |
| Claude | `claude()` | Análise via IA Anthropic |

---

## 10. Referência

- `connectors.py` — Biblioteca central de APIs (444 linhas)
- `relatorio_trafego.py` — Relatório multicanal com template V4
- `clientes.json` — Cadastro de clientes com OKRs
- Documentação completa: `docs/ARQUITETURA_RELATORIOS.md`
