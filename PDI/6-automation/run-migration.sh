#!/bin/bash
# ============================================================
# Run Migration - Schema v2.0 → v2.1 Supabase
# ============================================================
# Uso: bash run-migration.sh
#
# Executa o schema v2.1 no Supabase via psql.
# Necessario: Supabase project URL + service_role key configurados
# em variaveis de ambiente ou .env
# ============================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCHEMA_FILE="$ROOT_DIR/3-supabase/supabase-schema-v2.1.sql"

# Carregar .env se existir
ENV_FILE="$ROOT_DIR/../projetos/infraestrutura/n8n/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_SERVICE_KEY="${SUPABASE_SERVICE_KEY:-}"

# Verificar se temos URL e Service Key
echo "============================================"
echo " Migracao Supabase — Schema v2.1"
echo "============================================"
echo ""

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo "❌ SUPABASE_URL ou SUPABASE_SERVICE_KEY nao configurados."
    echo ""
    echo "Configure no .env ou exporte as variaveis:"
    echo "  export SUPABASE_URL=https://seuprojeto.supabase.co"
    echo "  export SUPABASE_SERVICE_KEY=sua_service_role_key"
    echo ""
    echo "Ou rode manualmente no SQL Editor do Supabase:"
    echo "  Abrir https://supabase.com/dashboard/project/gswzuzetverulcgzhynb"
    echo "  → SQL Editor → colar conteudo de:"
    echo "    $SCHEMA_FILE"
    exit 1
fi

# Rodar via psql
echo "Executando schema v2.1..."
echo "URL: $SUPABASE_URL"
echo ""

# Extrair o host do projeto da URL
PGHOST=$(echo "$SUPABASE_URL" | sed 's|https://||' | sed 's|\.supabase\.co.*||').supabase.co
PGPASSWORD="$SUPABASE_SERVICE_KEY"

PGPASSWORD="$PGPASSWORD" psql \
    -h "$PGHOST" \
    -p 5432 \
    -d postgres \
    -U postgres \
    -f "$SCHEMA_FILE" 2>&1

echo ""
echo "✅ Migracao concluida."
echo ""
echo "Verificar tabelas criadas:"
echo "  SELECT table_name FROM information_schema.tables"
echo "  WHERE table_schema = 'public'"
echo "    AND table_name IN ('error_dlq','error_circuit_breaker','error_retry_log','error_alert_config');"
