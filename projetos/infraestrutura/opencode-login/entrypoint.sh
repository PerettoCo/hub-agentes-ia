#!/bin/bash
set -e

# ─── OpenCode Web Entrypoint ───
# Gera opencode.json apontando pro LiteLLM com a chave virtual do usuário
# e inicia o servidor web.

LITELLM_VIRTUAL_KEY="${LITELLM_VIRTUAL_KEY:-}"
LITELLM_BASE_URL="${LITELLM_BASE_URL:-http://litellm:4000/v1}"
OPENCODE_PORT="${OPENCODE_PORT:-4096}"

OPENCODE_CONFIG_DIR="${OPENCODE_CONFIG_DIR:-/root/.config/opencode}"

apt-get update && apt-get install -y git curl sudo
npm install -g opencode-ai

mkdir -p "$OPENCODE_CONFIG_DIR"

if [ -n "$LITELLM_VIRTUAL_KEY" ]; then
  cat > "$OPENCODE_CONFIG_DIR/opencode.json" << EOF
{
  "modelProvider": "litellm",
  "model": "deepseek-v4-flash-free",
  "customProviders": {
    "litellm": {
      "type": "openai-compatible",
      "apiKey": "${LITELLM_VIRTUAL_KEY}",
      "baseURL": "${LITELLM_BASE_URL}"
    }
  }
}
EOF
  echo "[opencode] LiteLLM configurado com chave virtual"
else
  echo "[opencode] AVISO: LITELLM_VIRTUAL_KEY não definida — rodando sem gateway"
fi

opencode web --hostname 0.0.0.0 --port "$OPENCODE_PORT"
