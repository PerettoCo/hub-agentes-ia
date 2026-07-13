# Workflows de Orquestracao

Dois workflows n8n-as-code (.workflow.ts) que implementam a Camada 2 e 3 do padrao.

## [CC] Error Handler Central

**Arquivo:** `Error Handler Central.workflow.ts`
**Trigger:** Error Trigger (captura erros de qualquer workflow vinculado)
**Nodes:** 10

### Fluxo

```
Error Trigger
  → Code: Parse and Classify
    → IF: Severity Critical?
      ├── YES → Slack #incidents → INSERT error_dlq → Circuit Breaker Check
      │                                      → Log circuit state
      └── NO  → Slack #alerts → INSERT error_dlq
```

### Credenciais Necessarias

| Credencial | Node | Finalidade |
|-----------|------|-----------|
| Slack API | Slack Critical, Slack Warning | Notificar canais |
| Supabase API | Dead Letter Insert, Log to Supabase | Persistir erro + circuit state |
| SMTP/Email | Send Report Email | Fallback de notificacao |

### Deploy

```bash
# 1. Validar
npx n8nac skills validate "Error Handler Central.workflow.ts"

# 2. Push para o n8n
npx n8nac push "Error Handler Central.workflow.ts" --verify

# 3. Vincular em cada workflow producao (UI do n8n)
#    Abrir workflow → Settings → Error Workflow → [CC] Error Handler Central

# 4. Publicar o Error Handler (Shift + P)
```

## [CC] Circuit Breaker Monitor

**Arquivo:** `Circuit Breaker Monitor.workflow.ts`
**Trigger:** ScheduleTrigger a cada 5 minutos
**Nodes:** 6

### Fluxo

```
Schedule (5min)
  → Supabase: query vw_circuits_open_now
    → IF: tem circuitos abertos?
      ├── YES → Slack alerta → PATCH workflow (reativar) → log recovery
      └── NO  → fim
```

### Credenciais

| Credencial | Node | Finalidade |
|-----------|------|-----------|
| Supabase API | Query Open Circuits, Log Recovery | Consultar e registrar |
| n8n API | Attempt Recovery | Reativar workflow via PATCH |
| Slack API | Slack Circuit Alert | Notificar squad |

### Deploy

```bash
npx n8nac skills validate "Circuit Breaker Monitor.workflow.ts"
npx n8nac push "Circuit Breaker Monitor.workflow.ts" --verify
```

## Notas

- Ambos workflows precisam estar **publicados** (nao draft) para funcionar
- Apos alterar o Error Handler, SEMPRE republicar (Shift+P)
- O Error Handler NAO deve notificar no mesmo canal que os workflows monitorados (recursion trap)
