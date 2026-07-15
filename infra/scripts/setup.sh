#!/bin/bash
# setup.sh — Configuração inicial do Hub de Agentes
# Uso: bash infra/scripts/setup.sh
#
# Isso configura:
#   1. Cria .env a partir de .env.example (se não existir)
#   2. Gera SESSION_SECRET aleatório
#   3. Cria diretórios de dados persistentes
#   4. Verifica Docker e Docker Compose
#   5. Cria usuário admin inicial bootstrap

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[setup]${NC} $1"; }
warn()  { echo -e "${YELLOW}[setup]${NC} $1"; }
error() { echo -e "${RED}[setup]${NC} $1"; }

info "=== Hub de Agentes — Setup ==="

# 1. Verificar Docker
if ! command -v docker &>/dev/null; then
  error "Docker não encontrado. Instale Docker primeiro: https://docs.docker.com/engine/install/"
  exit 1
fi
info "Docker encontrado: $(docker --version)"

if ! docker compose version &>/dev/null; then
  error "Docker Compose não encontrado."
  exit 1
fi
info "Docker Compose encontrado: $(docker compose version)"

# 2. Criar .env
ENV_FILE=".env"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f "$ENV_FILE" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example "$ENV_FILE"
    info "$ENV_FILE criado a partir de .env.example"
  else
    warn ".env.example não encontrado. Criando .env básico..."
    cat > "$ENV_FILE" << EOF
SESSION_SECRET=
PUBLIC_URL=https://ia.fvmarketing.com.br
OPENCODE_SERVER_PASSWORD=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
SUPABASE_DADOS_URL=
SUPABASE_DADOS_KEY=
GITHUB_TOKEN=
LITELLM_KEY_MARCOS=
LITELLM_KEY_FHELIPE=
LITELLM_KEY_LUCASNUNES=
LITELLM_KEY_PAOLO=
LITELLM_KEY_BRUNO=
LITELLM_KEY_ITALO=
EOF
  fi
fi

# 3. Gerar SESSION_SECRET se vazio
if grep -q "SESSION_SECRET=$" "$ENV_FILE"; then
  NEW_SECRET=$(openssl rand -hex 32)
  sed -i "s/SESSION_SECRET=$/SESSION_SECRET=$NEW_SECRET/" "$ENV_FILE"
  info "SESSION_SECRET gerado automaticamente"
fi

# 4. Criar diretórios de dados persistentes
DATA_DIR="./data"
mkdir -p "$DATA_DIR/sessions" "$DATA_DIR/certs"
info "Diretórios de dados criados: $DATA_DIR/sessions, $DATA_DIR/certs"

# 5. Verificar usuários
USERS_FILE="$DATA_DIR/users.json"
if [ ! -f "$USERS_FILE" ]; then
  warn "Arquivo de usuários não encontrado."
  warn "O bootstrap criará um admin automaticamente na primeira execução."
  warn "Defina BOOTSTRAP_ADMIN no .env (ex: marcos.luciano) para criar o admin inicial."
  echo ""
  read -p "Deseja criar um admin agora? (s/N): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Ss]$ ]]; then
    read -p "Username (ex: marcos.luciano): " ADMIN_USER
    if [ -n "$ADMIN_USER" ]; then
      sed -i "s/^BOOTSTRAP_ADMIN=.*/BOOTSTRAP_ADMIN=${ADMIN_USER}:v4@2025/" "$ENV_FILE"
      info "BOOTSTRAP_ADMIN definido. O admin será criado na primeira execução."
    fi
  fi
fi

# 6. Verificar Cloudflare Origin CA certs
CERTS_DIR="$DATA_DIR/certs"
if [ ! -f "$CERTS_DIR/cert.pem" ] || [ ! -f "$CERTS_DIR/key.pem" ]; then
  warn "Cloudflare Origin CA não encontrado em $CERTS_DIR"
  warn "O gateway usará um certificado auto-assinado para teste."
  warn ""
  warn "Para produção, gere um certificado em:"
  warn "  Cloudflare Dashboard → SSL/TLS → Origin Server → Create Certificate"
  warn "  Salve cert.pem e key.pem em: $CERTS_DIR"
fi

# 7. Resumo final
echo ""
info "=== Setup concluído ==="
echo ""
echo "  .env              → $ENV_FILE"
echo "  Dados persistentes → $DATA_DIR"
echo "  Iniciar:          docker compose -f docker-compose.agentes.yml up -d"
echo "  Logs:             docker compose -f docker-compose.agentes.yml logs -f"
echo "  Parar:            docker compose -f docker-compose.agentes.yml down"
echo ""
echo "  Portal:           https://ia.fvmarketing.com.br"
echo "  Admin inicial:    Usuário: admin / Senha: v4@2025"
echo ""

if [ ! -f "$CERTS_DIR/cert.pem" ]; then
  echo "  ⚠  Configure o Cloudflare Origin CA antes de publicar o gateway."
fi
