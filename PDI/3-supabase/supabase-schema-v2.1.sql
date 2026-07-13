-- ============================================================
-- N8N ENTERPRISE — Supabase Schema Extension v2.1
-- Error Handling + Retry + Circuit Breaker + DLQ
-- ============================================================
-- Uso: Rodar no SQL Editor do Supabase (projeto: gswzuzetverulcgzhynb)
-- Compativel com schema v2.0 existente (adiciona tabelas, nao altera)
-- ============================================================

-- ============================================================
-- 8. DEAD LETTER QUEUE (DLQ)
-- ============================================================
-- Persiste TODOS os erros que escapam para o Error Handler Central.
-- Cada linha = uma falha nao-recuperavel.
-- Usado para: auditoria, replay manual, analise de tendencia, SLA.
-- ============================================================
CREATE TABLE IF NOT EXISTS error_dlq (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  correlation_id    TEXT NOT NULL,
  workflow_name     TEXT NOT NULL,
  workflow_id       TEXT,
  execution_id      TEXT,
  failed_node       TEXT,
  error_class       TEXT NOT NULL
    CHECK (error_class IN (
      'server_error', 'rate_limit', 'timeout', 'client_error',
      'data_validation', 'network_dns', 'runtime', 'resource_exhaustion',
      'unknown'
    )),
  error_message     TEXT,
  severity          TEXT NOT NULL DEFAULT 'warning'
    CHECK (severity IN ('critical', 'warning', 'info')),
  payload           JSONB DEFAULT '{}',
  status            TEXT DEFAULT 'pending_review'
    CHECK (status IN (
      'pending_review', 'investigating', 'resolved',
      'wont_fix', 'recovered_auto'
    )),
  attempt           INTEGER DEFAULT 1,
  max_attempts      INTEGER DEFAULT 3,
  acknowledged_at   TIMESTAMPTZ,
  acknowledged_by   TEXT,
  resolved_at       TIMESTAMPTZ,
  resolution_notes  TEXT,
  created_at        TIMESTAMPTZ DEFAULT now()
);

-- Indices para consulta frequente
CREATE INDEX IF NOT EXISTS idx_error_dlq_status ON error_dlq(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_error_dlq_correlation ON error_dlq(correlation_id);
CREATE INDEX IF NOT EXISTS idx_error_dlq_workflow ON error_dlq(workflow_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_error_dlq_class ON error_dlq(error_class, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_error_dlq_severity ON error_dlq(severity, created_at DESC);

-- ============================================================
-- 9. CIRCUIT BREAKER STATE
-- ============================================================
-- Registro de estado do circuit breaker por workflow.
-- O Error Handler Central atualiza esta tabela a cada falha.
-- Workflows de health-check consultam para decidir se reativam.
-- ============================================================
CREATE TABLE IF NOT EXISTS error_circuit_breaker (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_name         TEXT NOT NULL,
  workflow_id           TEXT,
  circuit_status        TEXT NOT NULL DEFAULT 'closed'
    CHECK (circuit_status IN ('closed', 'open', 'half-open')),
  circuit_action        TEXT DEFAULT 'none'
    CHECK (circuit_action IN ('none', 'OPENED', 'half-open', 'skip', 'closed_recovered')),
  failures_consecutive  INTEGER DEFAULT 0,
  opened_at             TIMESTAMPTZ,
  last_failure_at       TIMESTAMPTZ DEFAULT now(),
  last_recovered_at     TIMESTAMPTZ,
  cooldown_ms           INTEGER DEFAULT 300000,
  execution_id          TEXT,
  correlation_id        TEXT,
  metadata              JSONB DEFAULT '{}',
  created_at            TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_circuit_wf_name ON error_circuit_breaker(workflow_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_circuit_status ON error_circuit_breaker(circuit_status);

-- ============================================================
-- 10. RETRY LOG
-- ============================================================
-- Auditoria de retentativas automaticas.
-- Cada linha = uma tentativa de retry em um no HTTP.
-- Permite diagnosticar: taxa de sucesso pos-retry, backoff ideal,
-- codigos que nunca recuperam, tendencias de falha.
-- ============================================================
CREATE TABLE IF NOT EXISTS error_retry_log (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  correlation_id    TEXT NOT NULL,
  workflow_name     TEXT NOT NULL,
  workflow_id       TEXT,
  execution_id      TEXT,
  node_name         TEXT NOT NULL,
  attempt           INTEGER NOT NULL,
  max_attempts      INTEGER DEFAULT 3,
  http_method       TEXT,
  http_url          TEXT,
  http_status       INTEGER,
  error_class       TEXT,
  error_message     TEXT,
  wait_before_ms    INTEGER,
  success           BOOLEAN DEFAULT false,
  created_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_retry_log_wf ON error_retry_log(workflow_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_retry_log_corr ON error_retry_log(correlation_id);
CREATE INDEX IF NOT EXISTS idx_retry_log_node ON error_retry_log(node_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_retry_log_status ON error_retry_log(http_status, success);

-- ============================================================
-- 11. ALERT CONFIG
-- ============================================================
-- Configuracoes de alerta por workflow: canal, severidade minima,
-- escalation delay, time de plantao.
-- Populado manualmente ou via dashboard.
-- ============================================================
CREATE TABLE IF NOT EXISTS error_alert_config (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_name       TEXT NOT NULL UNIQUE,
  workflow_id         TEXT,
  min_severity        TEXT DEFAULT 'warning'
    CHECK (min_severity IN ('critical', 'warning', 'info')),
  slack_channel       TEXT,
  email_to            TEXT[] DEFAULT '{}',
  escalation_tier     INTEGER DEFAULT 1
    CHECK (escalation_tier BETWEEN 1 AND 3),
  escalation_minutes  INTEGER[] DEFAULT '{0, 15, 45}',
  pagerduty_enabled   BOOLEAN DEFAULT false,
  on_call_team        TEXT,
  active              BOOLEAN DEFAULT true,
  created_at          TIMESTAMPTZ DEFAULT now(),
  updated_at          TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_alert_config_active ON error_alert_config(active);

-- ============================================================
-- VIEWS DE MONITORAMENTO
-- ============================================================

-- 1. Resumo de falhas por workflow (ultimas 24h)
CREATE OR REPLACE VIEW vw_error_summary_24h AS
SELECT
  workflow_name,
  COUNT(*) as total_errors,
  COUNT(*) FILTER (WHERE severity = 'critical') as critical_errors,
  COUNT(*) FILTER (WHERE severity = 'warning') as warning_errors,
  COUNT(*) FILTER (WHERE error_class = 'rate_limit') as rate_limits,
  COUNT(*) FILTER (WHERE error_class = 'timeout') as timeouts,
  COUNT(*) FILTER (WHERE error_class = 'data_validation') as validation_errors,
  COUNT(*) FILTER (WHERE status = 'pending_review') as pending_review,
  MAX(created_at) as last_error_at
FROM error_dlq
WHERE created_at > now() - INTERVAL '24 hours'
GROUP BY workflow_name
ORDER BY total_errors DESC;

-- 2. Circuitos abertos no momento
CREATE OR REPLACE VIEW vw_circuits_open_now AS
SELECT
  workflow_name,
  failures_consecutive,
  opened_at,
  EXTRACT(EPOCH FROM (now() - opened_at))::INTEGER / 60 as minutes_open,
  metadata
FROM (
  SELECT DISTINCT ON (workflow_name) *
  FROM error_circuit_breaker
  ORDER BY workflow_name, created_at DESC
) latest
WHERE circuit_status = 'open';

-- 3. Taxa de sucesso de retry por node
CREATE OR REPLACE VIEW vw_retry_success_rate AS
SELECT
  node_name,
  COUNT(*) as total_attempts,
  COUNT(*) FILTER (WHERE success = true) as successes,
  CASE
    WHEN COUNT(*) > 0
    THEN ROUND(COUNT(*) FILTER (WHERE success = true)::DECIMAL / COUNT(*) * 100, 1)
    ELSE 0
  END as success_rate_pct,
  COUNT(*) FILTER (WHERE http_status = 429) as rate_limited,
  COUNT(*) FILTER (WHERE http_status = 503) as unavailable
FROM error_retry_log
WHERE created_at > now() - INTERVAL '7 days'
GROUP BY node_name
ORDER BY total_attempts DESC;

-- 4. Dashboard consolidado de saude
CREATE OR REPLACE VIEW vw_error_health_score AS
WITH
dlq_stats AS (
  SELECT
    COUNT(*) as total_errors_24h,
    COUNT(*) FILTER (WHERE severity = 'critical') as critical_24h,
    COUNT(*) FILTER (WHERE severity = 'warning') as warning_24h
  FROM error_dlq
  WHERE created_at > now() - INTERVAL '24 hours'
),
circuit_stats AS (
  SELECT COUNT(*) as open_circuits
  FROM vw_circuits_open_now
)
SELECT
  COALESCE(dlq_stats.total_errors_24h, 0) as total_errors_24h,
  COALESCE(dlq_stats.critical_24h, 0) as critical_24h,
  COALESCE(dlq_stats.warning_24h, 0) as warning_24h,
  COALESCE(circuit_stats.open_circuits, 0) as open_circuits,
  CASE
    WHEN dlq_stats.total_errors_24h = 0 THEN 1.0
    ELSE GREATEST(0, 1.0 - (dlq_stats.critical_24h::DECIMAL / GREATEST(dlq_stats.total_errors_24h, 1)))
  END as health_score
FROM dlq_stats, circuit_stats;

-- ============================================================
-- REALTIME (novas tabelas)
-- ============================================================
DO $$ BEGIN ALTER PUBLICATION supabase_realtime ADD TABLE error_dlq; EXCEPTION WHEN SQLSTATE '42710' THEN NULL; END $$;
DO $$ BEGIN ALTER PUBLICATION supabase_realtime ADD TABLE error_circuit_breaker; EXCEPTION WHEN SQLSTATE '42710' THEN NULL; END $$;
DO $$ BEGIN ALTER PUBLICATION supabase_realtime ADD TABLE error_retry_log; EXCEPTION WHEN SQLSTATE '42710' THEN NULL; END $$;
DO $$ BEGIN ALTER PUBLICATION supabase_realtime ADD TABLE error_alert_config; EXCEPTION WHEN SQLSTATE '42710' THEN NULL; END $$;
