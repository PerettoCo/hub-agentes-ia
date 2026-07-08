#!/bin/bash
set -euo pipefail

# ─── Gerar Virtual Keys no LiteLLM ───
# Lê users.json, cria/atualiza chaves virtuais no LiteLLM pra cada usuário,
# e salva as chaves de volta no users.json.
#
# Uso: ./gerar-keys-litellm.sh
# Requer: LITELLM_MASTER_KEY e LITELLM_URL configurados

LITELLM_URL="${LITELLM_URL:-http://localhost:4000}"
LITELLM_MASTER_KEY="${LITELLM_MASTER_KEY:-}"
USERS_FILE="${USERS_FILE:-users.json}"

if [ -z "$LITELLM_MASTER_KEY" ]; then
  echo "[ERRO] LITELLM_MASTER_KEY não definida"
  echo "  Exporte a variável ou defina no .env"
  exit 1
fi

if [ ! -f "$USERS_FILE" ]; then
  echo "[ERRO] $USERS_FILE não encontrado"
  exit 1
fi

echo "=== Gerando Virtual Keys no LiteLLM ==="
echo "LiteLLM URL: $LITELLM_URL"
echo "Users file:  $USERS_FILE"
echo ""

# Mapa de squad → modelos liberados + rate limit
declare -A SQUAD_MODELS
SQUAD_MODELS["tech"]='["deepseek-v4-flash-free","gemini-2.5-flash-free","gpt-4o-mini","gpt-4o"]'
SQUAD_MODELS["account"]='["deepseek-v4-flash-free","gemini-2.5-flash-free","gpt-4o-mini"]'
SQUAD_MODELS["copy"]='["deepseek-v4-flash-free","gemini-2.5-flash-free","gpt-4o-mini"]'
SQUAD_MODELS["gt"]='["deepseek-v4-flash-free","gemini-2.5-flash-free","gpt-4o-mini"]'
SQUAD_MODELS["design"]='["deepseek-v4-flash-free","gpt-4o-mini","gpt-4o"]'
SQUAD_MODELS["csm"]='["deepseek-v4-flash-free","gemini-2.5-flash-free","gpt-4o-mini"]'
SQUAD_MODELS["coord"]='["deepseek-v4-flash-free","gemini-2.5-flash-free","gpt-4o-mini","gpt-4o"]'

# Lê users.json
USERS=$(cat "$USERS_FILE")
UPDATED_USERS=$(echo "$USERS" | jq '.users = []')
UPDATED=false

while read -r user; do
  USERNAME=$(echo "$user" | jq -r '.username')
  SQUAD=$(echo "$user" | jq -r '.squad')
  NAME=$(echo "$user" | jq -r '.name')
  EXISTING_KEY=$(echo "$user" | jq -r '.litellmKey // empty')

  MODELS="${SQUAD_MODELS[$SQUAD]:-[\"deepseek-v4-flash-free\"]}"

  echo "[$USERNAME] ($SQUAD) Gerando chave..."

  # Define rate limit por squad
  RPM=100
  case "$SQUAD" in
    tech) RPM=200 ;;
    coord) RPM=200 ;;
    design) RPM=100 ;;
    csm) RPM=150 ;;
  esac

  # Cria a chave virtual no LiteLLM
  RESPONSE=$(curl -s -X POST "$LITELLM_URL/virtual_keys" \
    -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"models\": $MODELS,
      \"rpm\": $RPM,
      \"metadata\": {
        \"user\": \"$USERNAME\",
        \"squad\": \"$SQUAD\",
        \"name\": \"$NAME\"
      }
    }")

  NEW_KEY=$(echo "$RESPONSE" | jq -r '.token // empty')

  if [ -z "$NEW_KEY" ]; then
    echo "  [ERRO] Falha ao gerar chave: $(echo "$RESPONSE" | jq -r '.error // "resposta vazia"')"
    if [ -n "$EXISTING_KEY" ]; then
      echo "  [INFO] Mantendo chave existente: ${EXISTING_KEY:0:20}..."
    fi
    continue
  fi

  echo "  ✓ Chave gerada: ${NEW_KEY:0:20}..."

  # Atualiza users.json com a nova chave
  TMP=$(mktemp)
  cat "$USERS_FILE" | jq \
    --arg u "$USERNAME" \
    --arg k "$NEW_KEY" \
    '(.users[] | select(.username == $u) | .litellmKey) = $k' \
    > "$TMP" && mv "$TMP" "$USERS_FILE"

  echo ""
done < <(echo "$USERS" | jq -c '.users[]')

echo ""
echo "=== Todas as chaves geradas ==="
echo "Arquivo atualizado: $USERS_FILE"
echo ""
echo "Chaves geradas:"
cat "$USERS_FILE" | jq -r '.users[] | "  \(.username) → \(.litellmKey[0:20])..."'
