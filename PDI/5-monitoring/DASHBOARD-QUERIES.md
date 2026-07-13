# Dashboard de Monitoramento — Queries Supabase

## 1. Health Score Geral

```sql
SELECT * FROM vw_error_health_score;
```

Retorna:
| total_errors_24h | critical_24h | warning_24h | open_circuits | health_score |
|-----------------|-------------|-------------|---------------|--------------|
| 47 | 3 | 12 | 0 | 0.936 |

Health score > 0.95 = saudavel
Health score 0.80-0.95 = atencao
Health score < 0.80 = critico

## 2. Circuitos Abertos Agora

```sql
SELECT * FROM vw_circuits_open_now;
```

Se retornar alguma linha, um workflow esta com circuit breaker aberto.

## 3. Top 10 Workflows com Mais Erros (7 dias)

```sql
SELECT
  workflow_name,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE severity = 'critical') as critical,
  COUNT(*) FILTER (WHERE severity = 'warning') as warning,
  MAX(created_at) as ultimo_erro
FROM error_dlq
WHERE created_at > now() - INTERVAL '7 days'
GROUP BY workflow_name
ORDER BY total DESC
LIMIT 10;
```

## 4. Erros Nao Revisados

```sql
SELECT * FROM error_dlq
WHERE status = 'pending_review'
  AND created_at > now() - INTERVAL '7 days'
ORDER BY severity DESC, created_at DESC
LIMIT 50;
```

## 5. Taxa de Sucesso de Retry por Workflow

```sql
SELECT
  r.workflow_name,
  COUNT(*) as total_attempts,
  COUNT(*) FILTER (WHERE r.success = true) as successes,
  ROUND(COUNT(*) FILTER (WHERE r.success = true)::DECIMAL / GREATEST(COUNT(*), 1) * 100, 1) as success_pct
FROM error_retry_log r
WHERE r.created_at > now() - INTERVAL '7 days'
GROUP BY r.workflow_name
ORDER BY total_attempts DESC;
```

## 6. Timeline de Eventos (ultimas 24h)

```sql
SELECT
  date_trunc('hour', created_at) as hora,
  error_class,
  COUNT(*) as total
FROM error_dlq
WHERE created_at > now() - INTERVAL '24 hours'
GROUP BY hora, error_class
ORDER BY hora DESC, total DESC;
```

## 7. Top 10 Nodes que Mais Falham

```sql
SELECT
  failed_node,
  COUNT(*) as total,
  COUNT(DISTINCT workflow_name) as workflows_afetados,
  COUNT(*) FILTER (WHERE severity = 'critical') as critical
FROM error_dlq
WHERE created_at > now() - INTERVAL '7 days'
GROUP BY failed_node
ORDER BY total DESC
LIMIT 10;
```

## Sugestoes de Alertas (Cron + Webhook)

| Condicao | Query | Acao |
|----------|-------|------|
| Circuito aberto | `SELECT COUNT(*) FROM vw_circuits_open_now` > 0 | Slack #incidents |
| Health score < 0.80 | `SELECT health_score FROM vw_error_health_score` < 0.80 | Slack #incidents + email |
| 5+ erros criticos em 1h | Query #6 com filtro critical | Slack #incidents |
| Pendentes > 20 | Query #4 com COUNT > 20 | Slack #alerts |
