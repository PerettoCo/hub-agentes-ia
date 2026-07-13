# Script de Demonstracao — Error Handling n8n Enterprise

## Setup

```bash
# 1. Mostrar ambiente
npx n8nac env status --json

# 2. Mostrar workflows atuais
npx n8nac list

# 3. Mostrar estrutura PDI
tree PDI/
```

## Passo 1: Validar Workflows

```bash
npx n8nac skills validate "PDI/2-workflows/Error Handler Central.workflow.ts"
# Deve retornar: ✅ Workflow is valid!

npx n8nac skills validate "PDI/2-workflows/Circuit Breaker Monitor.workflow.ts"
# Deve retornar: ✅ Workflow is valid!
```

## Passo 2: Schema Supabase

```bash
# Abrir no SQL Editor
cat PDI/3-supabase/supabase-schema-v2.1.sql

# Mostrar as novas tabelas:
# - error_dlq (dead letter queue)
# - error_circuit_breaker
# - error_retry_log
# - error_alert_config
# - 4 views de monitoramento
```

## Passo 3: Push Error Handler Central

```bash
npx n8nac push "PDI/2-workflows/Error Handler Central.workflow.ts" --verify
```

## Passo 4: Vincular Error Workflow

```
No n8n UI:
  1. Abrir workflow SDR IA (ex: ADPLAN)
  2. Settings → Error Workflow
  3. Selecionar "[CC] Error Handler Central"
  4. Salvar
  5. Publicar (Shift+P)
```

## Passo 5: Provocar Falha (Teste)

```bash
# Workflow temporario de teste:
# Webhook (qualquer path)
#   → HTTP Request (URL: https://api.exemplo.com/invalida)
#     → Respond to Webhook

# Importante: NAO conectar error output.
# O erro escapa para o Error Handler Central.

# Rodar e verificar:
# 1. Slack notificou?
# 2. DLQ populou? (SELECT * FROM error_dlq ORDER BY created_at DESC LIMIT 5)
# 3. Circuit breaker registrou?
```

## Passo 6: Verificar Metricas

```sql
-- Health score geral
SELECT * FROM vw_error_health_score;

-- Top errors 24h
SELECT * FROM vw_error_summary_24h;
```

## Passo 7: Circuit Breaker Recovery

```bash
# Se circuit breaker abriu durante o teste:
# Aguardar 5 min (cooldown)
# Circuit Breaker Monitor tenta recovery automatico

# Verificar:
SELECT * FROM vw_circuits_open_now;
# Deve estar vazio apos recovery
```

## Sucesso

- ✅ Notificacao Slack chegou em < 30s
- ✅ DLQ com payload completo
- ✅ Circuit breaker registrou estado
- ✅ Recovery automatico funcionou
