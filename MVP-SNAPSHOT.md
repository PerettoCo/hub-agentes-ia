# MVP Snapshot — Hub de Agentes Infra Unify

## 1. Data/Hora

2026-07-19 00:37:37

## 2. Git Commit Hashes

```
e7aed33 feat: MCP servers (google-drive, ekyte) for 1.17.20
638cad7 fix: mcp.servers object format (not array) for 1.17.20
ead85d9 fix: pin opencode 1.17.20, agente mode:subagent, MCP servers, consulta banco SQL
a8553ed fix: entrypoint repo URL + configs 1.18.3 format (singular keys)
e5d828b dashboard: logo 200px, Sofia avatar na card
```

## 3. Directory Tree

```
hub-agentes-infra-unify/
├── .agents/
│   └── skills/                          (94 skills)
├── .claude/
│   └── skills/                          (68 skills, subset)
├── .env.example
├── .github/
│   └── agents/
│       └── n8n-architect.agent.md
├── .gitignore
├── .nojekyll
├── bases/
│   └── projetos-de-seo/
│       └── docs/
│           ├── auditoria-seo-r1grupo-Q2-2026.html
│           └── auditoria-seo-r1grupo-Q2-2026.md
├── data/
│   └── .gitkeep
├── docker-compose.agentes.yml
├── docs/
│   ├── 2026-07-14.md
│   ├── AGENTS.md
│   ├── acesso-hub-agentes.md
│   ├── agent-hub/
│   │   ├── documentacao-completa.html
│   │   ├── hub-agentes-v1.html
│   │   ├── hub-agentes-v1.md
│   │   ├── hub-de-agentes.html
│   │   ├── infra-skills-completa.html
│   │   ├── manual-operacional-times.html
│   │   └── skills-export.zip
│   ├── Ajuda Rede V4/
│   │   ├── Palavras-chave(2024.05.13-2026.07.08).csv
│   │   ├── Relatorio de campanha (5) (1).csv
│   │   ├── Relatorio de campanha (5).csv
│   │   ├── Relatorio de locais.csv
│   │   ├── Relatorio de palavras-chave da rede de pesquisa (3).csv
│   │   └── Relatorio de programacao de anuncios.csv
│   ├── biblioteca-skills.md
│   ├── boas-vindas-usuarios.md
│   ├── catalogo-skills-v1.html
│   ├── docker-compose.agentes.yml
│   ├── hub-agentes-v1.html
│   ├── hub-agentes-v1.md
│   ├── index2.html
│   ├── litellm-config.yaml
│   ├── opencode-hub-auditoria.html
│   ├── opencode-hub-documentacao.md
│   ├── opencode.server.json
│   ├── opencodelogo.png
│   └── titles-e-metadesc-r1.pdf
├── infra/
│   ├── agents/                          (35 agent .md files)
│   ├── auth/
│   │   ├── Dockerfile
│   │   ├── opencode-config/             (7 config .json files)
│   │   ├── package.json
│   │   ├── package-lock.json
│   │   ├── public/
│   │   │   ├── dashboard.html
│   │   │   ├── login.html
│   │   │   ├── logo.png
│   │   │   ├── logout.html
│   │   │   ├── sofia.png
│   │   │   └── v4bg.png
│   │   └── server.js
│   ├── Dockerfile.opencode
│   ├── entrypoint.sh
│   ├── entrypoint.sh.bak
│   ├── gateway/
│   │   ├── Dockerfile
│   │   ├── nginx.conf
│   │   └── run.sh
│   └── scripts/
│       ├── file-reader.py
│       ├── hash-password.js
│       ├── manage-users.js
│       ├── memory-cli.py
│       ├── opencode-proxy.js
│       ├── rag-ingest.py
│       ├── requirements.txt
│       ├── seed-mission-control.py
│       ├── seed-mission-control.sql
│       ├── seed-users.sql
│       └── setup.sh
├── litellm-config.yaml
├── opencode.server.json
├── PLANO DE ACAO HUB DE AGENTES/
│   ├── LOG_SESSAO_10-07-2026.md
│   └── PLANO.md
├── projetos/
│   └── infraestrutura/
│       ├── ai-ops/                      (2 api key files)
│       ├── authelia/
│       │   ├── configuration.yml
│       │   ├── docker-compose.yml
│       │   ├── Dockerfile
│       │   └── users_database.yml
│       ├── docker-compose.agentes.yml
│       ├── docker-compose.yml
│       ├── Dockerfile.opencode
│       ├── dokploy-app-litellm.yml
│       ├── dokploy-app-opencode-web.yml
│       ├── ia.fvmarketing.com.br.har
│       ├── litellm.config.yaml
│       ├── memoria-agentes/
│       │   └── README.md
│       ├── n8n/
│       ├── n8n-skills/
│       ├── OPENAUTH-DOC.md
│       ├── opencode-gateway/
│       │   ├── Dockerfile
│       │   ├── nginx.conf
│       │   └── run.sh
│       ├── opencode-login/
│       │   ├── Dockerfile
│       │   ├── entrypoint.sh
│       │   ├── .env.example
│       │   ├── gerar-keys-litellm.sh
│       │   ├── gerar-senha.js
│       │   ├── .gitignore
│       │   ├── opencode-config/
│       │   │   ├── csm1.json
│       │   │   ├── csm2.json
│       │   │   ├── csm3.json
│       │   │   ├── fhelipe.json
│       │   │   ├── lucasnunes.json
│       │   │   ├── marcos.json
│       │   │   ├── paolo.json
│       │   │   └── template.json
│       │   ├── package.json
│       │   ├── package-lock.json
│       │   ├── public/
│       │   │   ├── dashboard.html
│       │   │   ├── login.html
│       │   │   ├── logo-peretto-red.png
│       │   │   ├── logo.png
│       │   │   ├── logo-v4.png
│       │   │   ├── logo-white.png
│       │   │   ├── logout-confirm.html
│       │   │   ├── logout.html
│       │   │   ├── sofia.png
│       │   │   └── v4bg.png
│       │   ├── scripts/entrypoint.sh
│       │   ├── server.js
│       │   ├── setup.sh
│       │   ├── users.example.json
│       │   └── users.json
│       └── v4-automations/
│           ├── (scripts, config, cron, documentacao, setup)
├── scripts/
│   ├── authelia-deploy.sh
│   ├── consultar-supabase.py
│   ├── file-reader.py
│   ├── memory-cli.py
│   ├── migrar-volumes.sh
│   ├── opencode-entrypoint.sh
│   ├── opencode-proxy.js
│   ├── rag-ingest.py
│   ├── requirements.txt
│   └── setup-authelia.sh
├── Screenshot from 2026-07-16 00-10-12.png
├── sofia.png
├── Untitled 1.base
└── [V4 PERETTO INTERNO] Form Monitoramento LP Site...json
```

## 4. Agents in infra/agents/

| File | Size |
|------|------|
| account-orchestrator.md | 3.5K |
| analista-dados.md | 3.1K |
| automacao-analytics.md | 2.0K |
| cmoorch.md | 2.9K |
| content-studio.md | 2.5K |
| copy-content.md | 1.8K |
| criacao-design.md | 1.7K |
| cro-lab.md | 2.9K |
| cro-otimizacao.md | 2.1K |
| csm-orquestrador.md | 2.8K |
| estrategia-lideranca.md | 2.0K |
| estrategia-marketing.md | 1.9K |
| evolucao-checkins.md | 2.4K |
| executor-comite.md | 2.0K |
| flag-churn.md | 3.1K |
| flag-okr.md | 3.1K |
| flag-operacao.md | 3.1K |
| flag-roi.md | 2.9K |
| gerar-doc.md | 1.6K |
| gerar-html.md | 1.4K |
| gerar-pdf.md | 1.4K |
| gerar-ppt.md | 1.5K |
| growth-team.md | 2.2K |
| launch-pad.md | 3.0K |
| media-buyer.md | 2.9K |
| midia-paga.md | 1.9K |
| n8n-automator.md | 2.7K |
| pesquisador.md | 2.8K |
| pipeline-conteudo.md | 2.4K |
| receita-crescimento.md | 2.2K |
| relatorios-trafego.md | 3.4K |
| revenue-ops.md | 2.4K |
| revisor.md | 2.2K |
| seo-visibilidade.md | 1.9K |
| vendas-account.md | 1.9K |

**Total: 35 agent files**

## 5. Configs in infra/auth/opencode-config/

| File | Size |
|------|------|
| bruno.lindenmeyer.json | 8.0K |
| fhelipe.aranha.json | 8.0K |
| italo.rossi.json | 8.0K |
| lucas.nunes.json | 8.0K |
| marcos.luciano.json | 8.0K |
| paolo.carmine.json | 8.0K |
| template.json | 8.0K |

**Total: 7 config files (6 users + 1 template)**

## 6. docker-compose.agentes.yml

```yaml
volumes:
  opencode-data-marcos:
  opencode-data-fhelipe:
  opencode-data-lucasnunes:
  opencode-data-paolo:
  opencode-data-bruno:
  opencode-data-italo:
  opencode-auth-data:

services:
  # ─── Gateway (roteado via Dokploy/Traefik, sem porta no host) ───
  opencode-gateway:
    build:
      context: infra/gateway
      dockerfile: Dockerfile
    restart: unless-stopped
    depends_on:
      opencode-auth:
        condition: service_started
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ─── Auth ───
  opencode-auth:
    build:
      context: infra/auth
      dockerfile: Dockerfile
    volumes:
      - opencode-auth-data:/data
    environment:
      SESSION_SECRET: ${SESSION_SECRET:?SESSION_SECRET é obrigatório}
      COOKIE_DOMAIN: ${COOKIE_DOMAIN:-.fvmarketing.com.br}
      PUBLIC_URL: ${PUBLIC_URL:-https://ia.fvmarketing.com.br}
      SUPABASE_URL: ${SUPABASE_URL:-}
      SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY:-}
      BOOTSTRAP_ADMIN: ${BOOTSTRAP_ADMIN:-}
      DEFAULT_PASSWORD: ${DEFAULT_PASSWORD:-v4@2025}
      USERS_PATH: /data/users.json
      NODE_ENV: production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/api/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 10s

  # ─── OpenCode — Marcos Luciano ───
  opencode-marcos:
    build:
      context: .
      dockerfile: infra/Dockerfile.opencode
    environment:
      OPENCODE_SERVER_USERNAME: opencode
      OPENCODE_SERVER_PASSWORD: ${OPENCODE_SERVER_PASSWORD:?OPENCODE_SERVER_PASSWORD é obrigatório}
      OPENAI_API_KEY: ${LITELLM_KEY_MARCOS:?LITELLM_KEY_MARCOS é obrigatório}
      OPENAI_BASE_URL: https://litellm.fvmarketing.com.br/v1
      OPENCODE_DISABLE_MODELS_FETCH: "false"
      GITHUB_TOKEN: ${GITHUB_TOKEN:-}
      SUPABASE_URL: ${SUPABASE_URL:-}
      SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY:-}
      SUPABASE_DADOS_URL: ${SUPABASE_DADOS_URL:-}
      SUPABASE_DADOS_KEY: ${SUPABASE_DADOS_KEY:-}
      HUB_USERNAME: marcos.luciano
    volumes:
      - opencode-data-marcos:/home/node/.local/share/opencode
      - ./infra/auth/opencode-config/marcos.luciano.json:/home/node/.config/opencode/opencode.json:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:4096/global/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # ─── OpenCode — Fhelipe Aranha ───
  opencode-fhelipe:
    build:
      context: .
      dockerfile: infra/Dockerfile.opencode
    environment:
      OPENCODE_SERVER_USERNAME: opencode
      OPENCODE_SERVER_PASSWORD: ${OPENCODE_SERVER_PASSWORD:?}
      OPENAI_API_KEY: ${LITELLM_KEY_FHELIPE:?}
      OPENAI_BASE_URL: https://litellm.fvmarketing.com.br/v1
      OPENCODE_DISABLE_MODELS_FETCH: "false"
      GITHUB_TOKEN: ${GITHUB_TOKEN:-}
      SUPABASE_URL: ${SUPABASE_URL:-}
      SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY:-}
      SUPABASE_DADOS_URL: ${SUPABASE_DADOS_URL:-}
      SUPABASE_DADOS_KEY: ${SUPABASE_DADOS_KEY:-}
      HUB_USERNAME: fhelipe.aranha
    volumes:
      - opencode-data-fhelipe:/home/node/.local/share/opencode
      - ./infra/auth/opencode-config/fhelipe.aranha.json:/home/node/.config/opencode/opencode.json:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:4096/global/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # ─── OpenCode — Lucas Nunes ───
  opencode-lucasnunes:
    build:
      context: .
      dockerfile: infra/Dockerfile.opencode
    environment:
      OPENCODE_SERVER_USERNAME: opencode
      OPENCODE_SERVER_PASSWORD: ${OPENCODE_SERVER_PASSWORD:?}
      OPENAI_API_KEY: ${LITELLM_KEY_LUCASNUNES:?}
      OPENAI_BASE_URL: https://litellm.fvmarketing.com.br/v1
      OPENCODE_DISABLE_MODELS_FETCH: "false"
      GITHUB_TOKEN: ${GITHUB_TOKEN:-}
      SUPABASE_URL: ${SUPABASE_URL:-}
      SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY:-}
      SUPABASE_DADOS_URL: ${SUPABASE_DADOS_URL:-}
      SUPABASE_DADOS_KEY: ${SUPABASE_DADOS_KEY:-}
      HUB_USERNAME: lucas.nunes
    volumes:
      - opencode-data-lucasnunes:/home/node/.local/share/opencode
      - ./infra/auth/opencode-config/lucas.nunes.json:/home/node/.config/opencode/opencode.json:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:4096/global/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # ─── OpenCode — Paolo Carmine ───
  opencode-paolo:
    build:
      context: .
      dockerfile: infra/Dockerfile.opencode
    environment:
      OPENCODE_SERVER_USERNAME: opencode
      OPENCODE_SERVER_PASSWORD: ${OPENCODE_SERVER_PASSWORD:?}
      OPENAI_API_KEY: ${LITELLM_KEY_PAOLO:?}
      OPENAI_BASE_URL: https://litellm.fvmarketing.com.br/v1
      OPENCODE_DISABLE_MODELS_FETCH: "false"
      GITHUB_TOKEN: ${GITHUB_TOKEN:-}
      SUPABASE_URL: ${SUPABASE_URL:-}
      SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY:-}
      SUPABASE_DADOS_URL: ${SUPABASE_DADOS_URL:-}
      SUPABASE_DADOS_KEY: ${SUPABASE_DADOS_KEY:-}
      HUB_USERNAME: paolo.carmine
    volumes:
      - opencode-data-paolo:/home/node/.local/share/opencode
      - ./infra/auth/opencode-config/paolo.carmine.json:/home/node/.config/opencode/opencode.json:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:4096/global/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # ─── OpenCode — Bruno Lindenmeyer ───
  opencode-bruno:
    build:
      context: .
      dockerfile: infra/Dockerfile.opencode
    environment:
      OPENCODE_SERVER_USERNAME: opencode
      OPENCODE_SERVER_PASSWORD: ${OPENCODE_SERVER_PASSWORD:?}
      OPENAI_API_KEY: ${LITELLM_KEY_BRUNO:?}
      OPENAI_BASE_URL: https://litellm.fvmarketing.com.br/v1
      OPENCODE_DISABLE_MODELS_FETCH: "false"
      GITHUB_TOKEN: ${GITHUB_TOKEN:-}
      SUPABASE_URL: ${SUPABASE_URL:-}
      SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY:-}
      SUPABASE_DADOS_URL: ${SUPABASE_DADOS_URL:-}
      SUPABASE_DADOS_KEY: ${SUPABASE_DADOS_KEY:-}
      HUB_USERNAME: bruno.lindenmeyer
    volumes:
      - opencode-data-bruno:/home/node/.local/share/opencode
      - ./infra/auth/opencode-config/bruno.lindenmeyer.json:/home/node/.config/opencode/opencode.json:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:4096/global/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # ─── OpenCode — Ítalo Rossi ───
  opencode-italo:
    build:
      context: .
      dockerfile: infra/Dockerfile.opencode
    environment:
      OPENCODE_SERVER_USERNAME: opencode
      OPENCODE_SERVER_PASSWORD: ${OPENCODE_SERVER_PASSWORD:?}
      OPENAI_API_KEY: ${LITELLM_KEY_ITALO:?}
      OPENAI_BASE_URL: https://litellm.fvmarketing.com.br/v1
      OPENCODE_DISABLE_MODELS_FETCH: "false"
      GITHUB_TOKEN: ${GITHUB_TOKEN:-}
      SUPABASE_URL: ${SUPABASE_URL:-}
      SUPABASE_SERVICE_KEY: ${SUPABASE_SERVICE_KEY:-}
      SUPABASE_DADOS_URL: ${SUPABASE_DADOS_URL:-}
      SUPABASE_DADOS_KEY: ${SUPABASE_DADOS_KEY:-}
      HUB_USERNAME: italo.rossi
    volumes:
      - opencode-data-italo:/home/node/.local/share/opencode
      - ./infra/auth/opencode-config/italo.rossi.json:/home/node/.config/opencode/opencode.json:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:4096/global/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

## 7. Dockerfile.opencode

```dockerfile
FROM node:20-bookworm-slim

RUN apt-get update && apt-get install -y \
  git \
  xdg-utils \
  python3 \
  python3-pip \
  wget \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g opencode-ai@1.17.20 @ai-sdk/openai-compatible

COPY infra/scripts/requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt --break-system-packages && rm -f /tmp/requirements.txt

RUN mkdir -p \
  /home/node/.config/opencode \
  /home/node/.local/share/opencode \
  /workspace \
  /home/node/.agents \
  && chown -R node:node /home/node/.config /home/node/.local /workspace /home/node/.agents

ENV OPENCODE_HOSTNAME=0.0.0.0
ENV OPENCODE_PORT=4096
ENV NODE_PATH=/usr/local/lib/node_modules

COPY --chown=node:node infra/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER node
WORKDIR /workspace

EXPOSE 4096

ENTRYPOINT ["/entrypoint.sh"]
CMD ["opencode", "web", "--hostname", "0.0.0.0", "--port", "4096", "--print-logs"]
```

## 8. entrypoint.sh

```bash
#!/bin/bash
set -e

mkdir -p /home/node/.local/bin
cat > /home/node/.local/bin/xdg-open << 'XDGEOF'
#!/bin/bash
echo "[xdg-open] suppressed (headless container)"
XDGEOF
chmod +x /home/node/.local/bin/xdg-open
export PATH="/home/node/.local/bin:$PATH"
export BROWSER=/home/node/.local/bin/xdg-open

if [ -n "$GITHUB_TOKEN" ]; then
  REPO_URL="https://marcoslrvusa:${GITHUB_TOKEN}@github.com/PerettoCo/hub-agentes-ia.git"
  if [ ! -d /workspace/.git ]; then
    echo "[entrypoint] Setting up workspace..."
    rm -rf /workspace/* /workspace/.[!.]* /workspace/.??* 2>/dev/null || true
    git clone -b main --single-branch "$REPO_URL" /workspace || echo "[entrypoint] Git clone failed (non-fatal)"
    git -C /workspace remote set-url origin https://github.com/PerettoCo/hub-agentes-ia.git 2>/dev/null || true
  else
    echo "[entrypoint] Updating workspace..."
    git -C /workspace remote set-url origin "$REPO_URL" 2>/dev/null || true
    git -C /workspace pull --ff-only 2>/dev/null || echo "[entrypoint] Git pull failed (non-fatal)"
  fi
fi

mkdir -p /workspace/outputs

rm -f /workspace/opencode.json

exec "$@"
```

## 9. Gateway nginx.conf

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events { worker_connections 1024; multi_accept on; }

http {
    log_format json escape=json
        '{"ts":"$time_iso8601","host":"$host","method":"$request_method",'
        '"uri":"$request_uri","status":$status,"upstream":"$upstream_addr",'
        '"rt":$request_time,"urt":"$upstream_response_time"}';

    access_log /var/log/nginx/access.json json;
    error_log /var/log/nginx/error.log warn;

    client_max_body_size 100m;
    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_cache off;
    chunked_transfer_encoding on;
    add_header X-Accel-Buffering no;

    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;

    # Cloudflare termina SSL — conexão com origin é HTTP mas o proto real é HTTPS
    proxy_set_header X-Forwarded-Proto https;

    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
    proxy_connect_timeout 10s;

    resolver 127.0.0.11 valid=10s;

    server {
        listen 80;
        server_name ia.fvmarketing.com.br;
        set $auth "http://opencode-auth:3000";

        location / {
            proxy_pass $auth;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location /static/ {
            proxy_pass $auth;
            expires 7d;
            add_header Cache-Control "public, immutable";
        }
    }

    server {
        listen 80;
        server_name ia.marcosluciano.fvmarketing.com.br;
        set $backend "http://opencode-marcos:4096";
        set $auth "http://opencode-auth:3000";

        auth_request /auth-check;
        error_page 401 =302 https://ia.fvmarketing.com.br/login?redirect=https://$host/;

        location / {
            proxy_pass $backend;
            proxy_set_header Authorization "Basic b3BlbmNvZGU6V213WnolaCFXXlJeYnBEeCF4QnQzNzNA";
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location = /auth-check {
            internal;
            proxy_pass $auth/auth-check;
            proxy_pass_request_body off;
            proxy_set_header Content-Length "";
            proxy_set_header Cookie $http_cookie;
        }

        location /health {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    server {
        listen 80;
        server_name ia.fhelipearanha.fvmarketing.com.br;
        set $backend "http://opencode-fhelipe:4096";
        set $auth "http://opencode-auth:3000";

        auth_request /auth-check;
        error_page 401 =302 https://ia.fvmarketing.com.br/login?redirect=https://$host/;

        location / {
            proxy_pass $backend;
            proxy_set_header Authorization "Basic b3BlbmNvZGU6V213WnolaCFXXlJeYnBEeCF4QnQzNzNA";
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location = /auth-check {
            internal;
            proxy_pass $auth/auth-check;
            proxy_pass_request_body off;
            proxy_set_header Content-Length "";
            proxy_set_header Cookie $http_cookie;
        }

        location /health {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    server {
        listen 80;
        server_name ia.lucasnunes.fvmarketing.com.br;
        set $backend "http://opencode-lucasnunes:4096";
        set $auth "http://opencode-auth:3000";

        auth_request /auth-check;
        error_page 401 =302 https://ia.fvmarketing.com.br/login?redirect=https://$host/;

        location / {
            proxy_pass $backend;
            proxy_set_header Authorization "Basic b3BlbmNvZGU6V213WnolaCFXXlJeYnBEeCF4QnQzNzNA";
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location = /auth-check {
            internal;
            proxy_pass $auth/auth-check;
            proxy_pass_request_body off;
            proxy_set_header Content-Length "";
            proxy_set_header Cookie $http_cookie;
        }

        location /health {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    server {
        listen 80;
        server_name ia.paolocarmine.fvmarketing.com.br;
        set $backend "http://opencode-paolo:4096";
        set $auth "http://opencode-auth:3000";

        auth_request /auth-check;
        error_page 401 =302 https://ia.fvmarketing.com.br/login?redirect=https://$host/;

        location / {
            proxy_pass $backend;
            proxy_set_header Authorization "Basic b3BlbmNvZGU6V213WnolaCFXXlJeYnBEeCF4QnQzNzNA";
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location = /auth-check {
            internal;
            proxy_pass $auth/auth-check;
            proxy_pass_request_body off;
            proxy_set_header Content-Length "";
            proxy_set_header Cookie $http_cookie;
        }

        location /health {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    server {
        listen 80;
        server_name ia.brunolindenmeyer.fvmarketing.com.br;
        set $backend "http://opencode-bruno:4096";
        set $auth "http://opencode-auth:3000";

        auth_request /auth-check;
        error_page 401 =302 https://ia.fvmarketing.com.br/login?redirect=https://$host/;

        location / {
            proxy_pass $backend;
            proxy_set_header Authorization "Basic b3BlbmNvZGU6V213WnolaCFXXlJeYnBEeCF4QnQzNzNA";
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location = /auth-check {
            internal;
            proxy_pass $auth/auth-check;
            proxy_pass_request_body off;
            proxy_set_header Content-Length "";
            proxy_set_header Cookie $http_cookie;
        }

        location /health {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    server {
        listen 80;
        server_name ia.italorossi.fvmarketing.com.br;
        set $backend "http://opencode-italo:4096";
        set $auth "http://opencode-auth:3000";

        auth_request /auth-check;
        error_page 401 =302 https://ia.fvmarketing.com.br/login?redirect=https://$host/;

        location / {
            proxy_pass $backend;
            proxy_set_header Authorization "Basic b3BlbmNvZGU6V213WnolaCFXXlJeYnBEeCF4QnQzNzNA";
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location = /auth-check {
            internal;
            proxy_pass $auth/auth-check;
            proxy_pass_request_body off;
            proxy_set_header Content-Length "";
            proxy_set_header Cookie $http_cookie;
        }

        location /health {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    server {
        listen 80 default_server;
        return 444;
    }
}
```

## 10. Auth server.js

(Servidor Express com sessão via FileStore, bcrypt, rate-limit, helmet, autenticação via formulário + API, gerenciamento de usuários CRUD, integração Supabase, healthcheck, targets de redirecionamento por usuário — 6 usuários cadastrados: marcos.luciano, fhelipe.aranha, lucas.nunes, paolo.carmine, bruno.lindenmeyer, italo.rossi)

- Porta: 3000
- Sessões: FileStore em /data/sessions, TTL 86400s
- Rate limit: 20 tentativas/15min no login, 100 req/min na API
- Usuários padrão: 6 (admin: marcos.luciano, resto role: user)
- Supabase sync a cada 5 minutos (opcional)
- Rotas: /login, /api/login, /api/logout, /api/me, /api/targets, /api/users (admin CRUD), /auth-check, /api/health, /, /logout

## 11. .env.example

```bash
# ─── Obrigatórias ───
SESSION_SECRET=CHAVE_SESSAO_32CARACTERES_AQUI
OPENCODE_SERVER_PASSWORD=SENHA_FORTE_OPencode

# ─── LiteLLM API Keys por usuário ───
LITELLM_KEY_MARCOS=
LITELLM_KEY_FHELIPE=
LITELLM_KEY_LUCASNUNES=
LITELLM_KEY_PAOLO=
LITELLM_KEY_BRUNO=
LITELLM_KEY_ITALO=

# ─── GitHub (para clonar repo no workspace) ───
GITHUB_TOKEN=

# ─── Supabase (opcional — fallback local se vazio) ───
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
SUPABASE_DADOS_URL=
SUPABASE_DADOS_KEY=

# ─── Domínio ───
PUBLIC_URL=https://ia.fvmarketing.com.br
COOKIE_DOMAIN=.fvmarketing.com.br

# ─── Cloudflare Tunnel (opcional — substitui portas expostas) ───
TUNNEL_TOKEN=

# ─── Bootstrap (primeira execução — cria admin) ───
BOOTSTRAP_ADMIN=
DEFAULT_PASSWORD=v4@2025
```

## Backup File Copy

Directories backed up to `backup-mvp/`:

- `backup-mvp/agents/` — 35 agent markdown files
- `backup-mvp/opencode-config/` — 7 JSON config files (6 users + template)
