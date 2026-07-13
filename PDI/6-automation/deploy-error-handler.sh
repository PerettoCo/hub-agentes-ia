#!/bin/bash
# ============================================================
# Deploy Error Handler — Padrao Universal n8n Enterprise V4
# ============================================================
# Uso: bash deploy-error-handler.sh
#
# Este script:
#   1. Valida os workflows de orquestracao
#   2. Faz push para o n8n
#   3. Instrui sobre configuracao manual
# ============================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORKFLOWS_DIR="$ROOT_DIR/2-workflows"
ERROR_HANDLER="$WORKFLOWS_DIR/Error Handler Central.workflow.ts"
CIRCUIT_MONITOR="$WORKFLOWS_DIR/Circuit Breaker Monitor.workflow.ts"

echo "============================================"
echo " Deploy Error Handler - Padrao Enterprise V4"
echo "============================================"
echo ""

# Step 1: Validate
echo "[1/4] Validando Error Handler Central..."
if npx n8nac skills validate "$ERROR_HANDLER" 2>&1 | grep -q "Workflow is valid"; then
    echo "  ✅ Error Handler Central: valido"
else
    echo "  ❌ Error Handler Central: FALHA NA VALIDACAO"
    echo "     Revise o arquivo antes de continuar."
    exit 1
fi

echo "[2/4] Validando Circuit Breaker Monitor..."
if npx n8nac skills validate "$CIRCUIT_MONITOR" 2>&1 | grep -q "Workflow is valid"; then
    echo "  ✅ Circuit Breaker Monitor: valido"
else
    echo "  ❌ Circuit Breaker Monitor: FALHA NA VALIDACAO"
    exit 1
fi

# Step 2: Push
echo "[3/4] Fazendo push para o n8n..."
echo "  → Push Error Handler Central..."
npx n8nac push "$ERROR_HANDLER" --verify && echo "  ✅ Push OK" || echo "  ⚠️  Push falhou (continue manualmente)"

echo "  → Push Circuit Breaker Monitor..."
npx n8nac push "$CIRCUIT_MONITOR" --verify && echo "  ✅ Push OK" || echo "  ⚠️  Push falhou (continue manualmente)"

# Step 3: Instructions
echo ""
echo "[4/4] 🔧 CONFIGURACAO MANUAL NECESSARIA"
echo "============================================"
echo ""
echo "1. Credenciais (configurar no n8n UI):"
echo "   - Slack API (token com scope: chat:write)"
echo "   - Supabase API (service_role key)"
echo "   - n8n API (personal access token)"
echo "   - SMTP (para fallback de email)"
echo ""
echo "2. Vincular Error Workflow em cada workflow producao:"
echo "   Abrir workflow → Settings → Error Workflow"
echo "   → selecionar '[CC] Error Handler Central'"
echo ""
echo "3. Publicar ambos workflows (Shift+P)"
echo ""
echo "4. Testar com falha provocada:"
echo "   - Criar workflow temporario com HTTP Request para URL invalida"
echo "   - Rodar sem error output (deixa o erro escapar)"
echo "   - Confirmar: Slack notificou? DLQ populou?"
echo ""
echo "============================================"
echo " Deploy concluido (parcial)."
echo " Finalizacao manual necessaria (passos 1-4 acima)"
echo "============================================"
