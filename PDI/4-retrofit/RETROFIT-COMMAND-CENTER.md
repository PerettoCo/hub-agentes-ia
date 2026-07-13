# Retrofit Command Center — Workflows de Infraestrutura

## Situacao Atual

3 workflows do Command Center operam SEM tratamento de erro algum.

| Workflow | Trigger | Funcao | Risco |
|----------|---------|--------|-------|
| `[CC] Collector` | Schedule 2min | Sincroniza workflows com Supabase | Falha silencia → dashboard desatualizado |
| `[CC] Heartbeat` | Schedule 5min | Saude da instancia n8n | Falha silencia → falso positivo de saude |
| `[CC] Metrics` | Schedule 1h | Snapshot de metricas | Falha silencia → lacuna historica |

## O que Implementar

### Em cada workflow

- [ ] `retryOnFail: true, maxTries: 3, waitBetweenTries: 5000` no HTTP Request
- [ ] `onError: "continueErrorOutput"` + `main[1]` conectado
- [ ] Error Workflow vinculado → `[CC] Error Handler Central`

### No Collector (critico)

O Collector faz GET `/api/v1/workflows` e UPSERT no Supabase. Se falha,
o dashboard fica desatualizado por ate 2 minutos (proximo ciclo).

Adicional:
- [ ] Log de ultima sync bem-sucedida no `error_dlq` (status = sucesso)
- [ ] Alerta se 3 ciclos consecutivos falharem (circuit breaker)

### No Heartbeat

Se o Heartbeat falha, podemos achar que a instancia caiu quando foi
só o workflow que quebrou.

Adicional:
- [ ] Diferenciar: falha do workflow vs falha da instancia
- [ ] Se workflow falha 3x seguidas: alertar squad

## Prioridade

| Workflow | Prioridade | Esforco | Impacto |
|----------|-----------|---------|---------|
| Collector | P1 | 30min | Medio (dashboard desatualizado) |
| Heartbeat | P2 | 20min | Baixo (falso positivo) |
| Metrics | P2 | 20min | Baixo (lacuna historica) |
