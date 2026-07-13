#!/bin/bash
# =========================================================
# Authelia Autoinstaller — V4 Agents Hub
# Uso: bash authelia-deploy.sh
# Cria configs, compose e deploya no Dokploy automaticamente
# =========================================================
set -e

DOMPLOY_URL="http://2.25.148.214:3000/api/deploy/compose/kzFVYo6tQOuOGEgmuxYuw"
DOMAIN="auth.fvmarketing.com.br"
# Muda pra sslip.io se DNS nao tiver apontando:
# DOMAIN="${DOKPLOY_PROJECT}-${DOKPLOY_SERVICE}-2-25-148-214.sslip.io"

echo "=========================================="
echo " Authelia Autoinstaller — V4 Hub"
echo "=========================================="
echo ""

# --- Cria pastas ---
echo "[1/4] Criando /etc/authelia/ ..."
sudo mkdir -p /etc/authelia

# --- Gera secrets seguros ---
JWT_SECRET=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)

# --- Cria configuration.yml ---
echo "[2/4] Gerando configuration.yml ..."
sudo tee /etc/authelia/configuration.yml > /dev/null << CONFIG
####################################################
# Authelia config — gerado por autoinstaller
# altere senhas em /etc/authelia/users_database.yml
####################################################
theme: dark
jwt_secret: ${JWT_SECRET}
server:
  host: 0.0.0.0
  port: 9091
log:
  level: info
authentication_backend:
  file:
    path: /config/users_database.yml
access_control:
  default_policy: deny
  rules:
    - domain: "${DOMAIN}"
      resources:
        - "^/api/health$"
      policy: bypass
    - domain: "${DOMAIN}"
      policy: one_factor
session:
  name: authelia_session
  secret: ${SESSION_SECRET}
  expiration: 24h
  inactivity: 30m
  remember_me: 30d
storage:
  local:
    path: /config/db.sqlite3
regulation:
  max_retries: 5
  find_time: 10m
  ban_time: 30m
notifier:
  filesystem:
    filename: /config/notifications.yml
CONFIG
echo "  ✅ configuration.yml criado"

# --- Cria users_database.yml ---
echo "[3/4] Gerando users_database.yml ..."
sudo tee /etc/authelia/users_database.yml > /dev/null << 'USERS'
users:
  marcos.luciano:
    displayname: Marcos Luciano
    password: "$argon2id$v=19$m=65536,t=3,p=4$NLhKHecej4BW765POOwD1g$5e3S4ieTNIrcaOHtPrqGXzVSlAJkvk+U3qKMbiwIhks"
    email: marcosluciano.rodrigues@v4company.com
    groups:
      - admin
  fhelipe.aranha:
    displayname: Fhelipe Aranha
    password: "$argon2id$v=19$m=65536,t=3,p=4$RpphIY6pDT0rNuMjcJvjKg$4E94yyK0ICS3XENpgQnzsnWkhML2aYEgQmbgLz4YYjc"
    email: fhelipe.aranha@v4company.com
    groups:
      - csm
  csm.2:
    displayname: CSM 2
    password: "$argon2id$v=19$m=65536,t=3,p=4$cT9wpQNn3NRcwfXnDSSwlg$dyDRzELzj1OR5IseFmF//hWKF92jsNCitynX0o+nmmc"
    email: csm2@v4company.com
    groups:
      - csm
  csm.3:
    displayname: CSM 3
    password: "$argon2id$v=19$m=65536,t=3,p=4$pkWuNDteWAssoTHaMVS1Wg$iKOPsB2960ZVGi7RgQc+Y/eW6rUloFP1/i/GpJgwNm8"
    email: csm3@v4company.com
    groups:
      - csm
USERS
echo "  ✅ users_database.yml criado (4 usuários)"

# --- Cria docker-compose.yml ---
echo "[4/4] Gerando docker-compose.yml ..."
cat > /tmp/docker-compose.yml << COMPOSE
services:
  authelia:
    image: authelia/authelia:latest
    container_name: authelia
    restart: unless-stopped
    volumes:
      - /etc/authelia/configuration.yml:/config/configuration.yml:ro
      - /etc/authelia/users_database.yml:/config/users_database.yml:ro
    networks:
      - dokploy-network
    labels:
      - "traefik.enable=true"
      - "traefik.docker.network=dokploy-network"
      - "traefik.http.routers.authelia.rule=Host(\`${DOMAIN}\`)"
      - "traefik.http.services.authelia.loadbalancer.server.port=9091"
      - "traefik.http.routers.authelia.tls=true"
      - "traefik.http.routers.authelia.tls.certresolver=letsencrypt"

networks:
  dokploy-network:
    external: true
COMPOSE

echo "  ✅ docker-compose.yml criado em /tmp/docker-compose.yml"
echo ""

# --- Deploy via Dokploy ---
echo "=========================================="
echo " Enviando compose pro Dokploy..."
echo "=========================================="

RESPONSE=$(curl -s -X POST "${DOMPLOY_URL}" \
  -H "Content-Type: multipart/form-data" \
  -F "composeFile=@/tmp/docker-compose.yml")

echo ""
echo "Resposta do Dokploy:"
echo "${RESPONSE}"
echo ""

# --- FIM ---
echo ""
echo "=========================================="
echo " ✅ DEPLOY ENVIADO!"
echo "=========================================="
echo ""
echo "Se o DNS estiver apontando:"
echo "   https://${DOMAIN}"
echo ""
echo "Se não estiver, substitua por:"
echo "   https://authelia-XXXXXXXX-2-25-148-214.sslip.io"
echo "   (O Dokploy mostra a URL depois do deploy)"
echo ""
echo "Login: marcos.luciano"
echo "Senha: P3r3tt0@Marcostech"
echo "=========================================="
