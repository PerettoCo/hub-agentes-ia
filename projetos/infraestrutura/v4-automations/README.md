# V4 Automations — Squad Mata Leão

Sistema de agentes automatizados por função. Roda em cron, coleta dados, processa com Claude API e entrega outputs no Gmail/Drive sem intervenção humana.

---

## Passo a passo completo para colocar no ar

### ETAPA 1 — Pré-requisitos (30 min)

```bash
# Python 3.9+
python3 --version

# Instalar dependências
pip install -r setup/requirements.txt
```

### ETAPA 2 — Credenciais Google (45 min)

1. Acesse https://console.cloud.google.com
2. Crie um projeto novo: "v4-automations"
3. Ative as APIs:
   - Google Ads API
   - Google Analytics Data API (GA4)
   - Gmail API
   - Google Drive API
4. Crie credenciais OAuth2 (tipo: Desktop App)
5. Baixe o arquivo JSON → renomeie para `credentials.json`
6. Mova para `config/credentials.json`
7. Rode o setup de autenticação:

```bash
python setup/auth_google.py
```

Isso abre o browser uma vez, você faz login, e salva o token. Nunca mais precisa fazer isso.

### ETAPA 3 — Credenciais Meta (20 min)

1. Acesse https://developers.facebook.com
2. Crie um App (tipo: Business)
3. Adicione o produto "Marketing API"
4. Gere um User Access Token com permissões:
   - `ads_read`
   - `ads_management`
   - `business_management`
5. Gere um token de longa duração (60 dias):
   - https://developers.facebook.com/tools/explorer
6. Copie o token → coloque em `config/.env`

### ETAPA 4 — Chave Anthropic (5 min)

1. Acesse https://console.anthropic.com
2. Gere uma API Key
3. Coloque em `config/.env`

### ETAPA 5 — Google Ads Developer Token (30 min)

1. Acesse https://ads.google.com/home/tools/manager-accounts
2. Crie ou acesse sua conta MCC (Manager)
3. Menu: Ferramentas → Centro de API
4. Solicite acesso (aprovação automática para test account)
5. Copie o Developer Token → coloque em `config/.env`

### ETAPA 6 — Configurar clientes (10 min)

Edite `config/clientes.json` com os dados reais dos clientes.

### ETAPA 7 — Ativar o cron (5 min)

```bash
# Instala os crons automaticamente
python setup/install_cron.py
```

Isso configura:
- Domingo 20h → briefing do Coordenador para o Comitê de segunda
- Quinta 7h → análise de performance do GT
- Dia 1 de cada mês 8h → envio de NPS/CSAT pelo AM
- Sexta 16h → checklist de conformidade do Coordenador

---

## Estrutura de arquivos

```
v4-automations/
├── README.md
├── config/
│   ├── .env                    ← suas chaves (nunca commitar)
│   ├── credentials.json        ← OAuth Google (nunca commitar)
│   ├── token.json              ← gerado automaticamente
│   └── clientes.json           ← dados dos seus clientes
├── setup/
│   ├── requirements.txt
│   ├── auth_google.py          ← autenticação OAuth (roda 1x)
│   └── install_cron.py         ← instala os crons
├── scripts/
│   ├── coordenador/
│   │   ├── briefing_comite.py  ← domingo 20h
│   │   └── checklist.py        ← sexta 16h
│   ├── gt/
│   │   └── analise_performance.py  ← quinta 7h
│   ├── am/
│   │   ├── atualizar_okrs.py   ← após análise GT
│   │   └── enviar_nps.py       ← dia 1 de cada mês
│   └── copy/
│       └── briefing_criativo.py ← sob demanda
└── cron/
    └── crontab.txt             ← referência dos crons
```
