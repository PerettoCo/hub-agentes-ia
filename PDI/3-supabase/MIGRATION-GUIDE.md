# Migracao Supabase — Schema v2.0 → v2.1

## O que muda

| Tabela | v2.0 | v2.1 | Descricao |
|--------|------|------|-----------|
| `n8n_workflows` | ✅ | ✅ | Inalterada |
| `n8n_events` | ✅ | ✅ | Inalterada |
| `n8n_heartbeat` | ✅ | ✅ | Inalterada |
| `n8n_metrics` | ✅ | ✅ | Inalterada |
| `workflow_reports` | ✅ | ✅ | Inalterada |
| `sdr_agents` | ✅ | ✅ | Inalterada |
| `sdr_events` | ✅ | ✅ | Inalterada |
| **`error_dlq`** | ❌ | **NOVA** | Dead Letter Queue |
| **`error_circuit_breaker`** | ❌ | **NOVA** | Circuit breaker state |
| **`error_retry_log`** | ❌ | **NOVA** | Auditoria de retentativas |
| **`error_alert_config`** | ❌ | **NOVA** | Config de alertas por workflow |
| View `vw_workflows_status` | ✅ | ✅ | Inalterada |
| View `vw_daily_summary` | ✅ | ✅ | Inalterada |
| View `vw_workflow_reports_count` | ✅ | ✅ | Inalterada |
| View **`vw_error_summary_24h`** | ❌ | **NOVA** | Resumo de falhas 24h |
| View **`vw_circuits_open_now`** | ❌ | **NOVA** | Circuitos abertos |
| View **`vw_retry_success_rate`** | ❌ | **NOVA** | Taxa de sucesso de retry |
| View **`vw_error_health_score`** | ❌ | **NOVA** | Health score geral |

## Como Rodar

```sql
-- 1. Conectar no Supabase (projeto: gswzuzetverulcgzhynb)
-- 2. Abrir SQL Editor
-- 3. Rodar o conteudo de supabase-schema-v2.1.sql
--    (As tabelas usam CREATE IF NOT EXISTS, seguro re-executar)
-- 4. Verificar com:
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('error_dlq','error_circuit_breaker','error_retry_log','error_alert_config');
```

> **Nota:** Nenhuma tabela existente e alterada. A migracao e 100% aditiva.
> Nao ha necessidade de downtime.
