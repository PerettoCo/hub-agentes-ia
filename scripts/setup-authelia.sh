#!/bin/bash
set -e

echo "=== Setup Authelia — V4 Agents Hub ==="

# 1) Cria pastas
mkdir -p /etc/authelia

# 2) Cria configuration.yml
cat > /etc/authelia/configuration.yml << 'CONFIG'
theme: dark
jwt_secret: 1c54dbe650522925920fd6a42bbf4f85aa83a3a9b71bcaa7c5c98811a80082b9
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
    - domain: "auth.fvmarketing.com.br"
      resources:
        - "^/api/health$"
      policy: bypass
    - domain: "auth.fvmarketing.com.br"
      policy: one_factor
session:
  name: authelia_session
  secret: 5c66e00ae774263ae6d314f3c8a89eaa7de1ce37e3421492ca434f1971e7c143
  expiration: 24h
  inactivity: 30m
storage:
  local:
    path: /config/db.sqlite3
regulation:
  max_retries: 3
  find_time: 5m
  ban_time: 15m
notifier:
  filesystem:
    filename: /config/notifications.yml
CONFIG

# 3) Cria users_database.yml com hashes prontas
cat > /etc/authelia/users_database.yml << 'USERS'
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

# 4) Verifica
echo ""
echo "✅ Arquivos criados:"
ls -la /etc/authelia/
echo ""
echo "==================== PRONTO ===================="
echo "Agora cola o compose abaixo no Dokploy e clica em Deploy:"
echo ""
echo "services:
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
      - \"traefik.enable=true\"
      - \"traefik.docker.network=dokploy-network\"
      - \"traefik.http.routers.authelia.rule=Host(\`auth.fvmarketing.com.br\`)\"
      - \"traefik.http.services.authelia.loadbalancer.server.port=9091\"
      - \"traefik.http.routers.authelia.tls=true\"
      - \"traefik.http.routers.authelia.tls.certresolver=letsencrypt\"

networks:
  dokploy-network:
    external: true"
echo ""
echo "Depois acesse: https://auth.fvmarketing.com.br"
echo "Login: marcos.luciano / P3r3tt0@Marcostech"
