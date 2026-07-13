# Padrao Universal de Tratamento de Erros — n8n Enterprise V4

> **Versao:** 2.0 | **Status:** Homologado | **Ultima revisao:** 2026-07-08

## Indice

1. [Arquitetura em 3 Camadas](#1-arquitetura-em-3-camadas)
2. [Taxonomia de Erros](#2-taxonomia-de-erros)
3. [Envelope Padrao de Erro](#3-envelope-padrao-de-erro)
4. [Retry Policies](#4-retry-policies)
5. [Error Handler Central](#5-error-handler-central)
6. [Circuit Breaker](#6-circuit-breaker)
7. [Dead Letter Queue](#7-dead-letter-queue)
8. [Node-Level Error Handling](#8-node-level-error-handling)
9. [Workflow-Level Error Workflow](#9-workflow-level-error-workflow)
10. [Notificacoes e Escalation](#10-notificacoes-e-escalation)
11. [Anti-Patterns](#11-anti-patterns)
12. [Checklist de Implementacao](#12-checklist-de-implementacao)
13. [Plano de Retrofit](#13-plano-de-retrofit)

---

## 1. Arquitetura em 3 Camadas

O tratamento de erro enterprise V4 e composto por **tres camadas obrigatorias e complementares**:

```
┌─────────────────────────────────────────────────────────┐
│  CAMADA 1: Node-Level (auto-cura)                       │
│  ─────────────────────────────────────────────────────── │
│  retryOnFail + continueOnError em cada no fallivel      │
│  Captura ~73% das falhas transientes (429, 503, timeout)│
├─────────────────────────────────────────────────────────┤
│  CAMADA 2: Error Workflow (rede de seguranca)           │
│  ─────────────────────────────────────────────────────── │
│  [CC] Error Handler Central captura o que escapar       │
│  Classifica severidade, notifica, persiste na DLQ       │
├─────────────────────────────────────────────────────────┤
│  CAMADA 3: Circuit Breaker + Dead Letter Queue          │
│  ─────────────────────────────────────────────────────── │
│  Circuit breaker evita sobrecarga em APIs fragilizadas  │
│  DLQ preserva payload completo para replay manual       │
└─────────────────────────────────────────────────────────┘
```

**Regra de ouro:** as tres camadas NAO sao alternativas. Um workflow enterprise TEM que ter as tres.

---

## 2. Taxonomia de Erros

Todo erro deve ser classificado em exatamente uma destas categorias no momento da captura:

| Classe | Codigo | Retentavel? | Severidade Default | Exemplos |
|--------|--------|-------------|-------------------|----------|
| `server_error` | 5xx | Sim (3x) | critical | 500, 502, 503, 504 |
| `rate_limit` | 429 | Sim (c/ backoff) | warning | Too Many Requests |
| `timeout` | ETIMEDOUT | Sim (3x) | critical | Conexao expirou, upstream timeout |
| `client_error` | 4xx (exceto 429) | **Nunca** | warning | 400, 401, 403, 404, 422 |
| `data_validation` | custom | **Nunca** | warning | toDateTime undefined, null constraint |
| `network_dns` | ENOTFOUND | Sim (3x) | critical | DNS resolve fail, Redis off |
| `runtime` | custom | **Nunca** | critical | Task runner desconectado, OOM |
| `resource_exhaustion` | OOM/CPU | **Nunca** | critical | Memory heap, event loop blocked |
| `unknown` | ? | **Nunca** | info | Nao classificado |

### Matriz de decisoes

```
Erro capturado
  ├── 4xx? (exceto 408/409/425/429)
  │     → NAO retentar. Registrar na DLQ + notificar.
  │     → 401/403 = alerta imediato (credencial expirou)
  │     → 404 = verificar se endpoint mudou
  │
  ├── 429 / rate limit?
  │     → Retentar com backoff exponencial + jitter
  │     → Respeitar header Retry-After se presente
  │     → Max 3 tentativas, depois DLQ
  │
  ├── 5xx / timeout / DNS?
  │     → Retentar com backoff exponencial (1s, 2s, 4s)
  │     → Max 3 tentativas, depois DLQ
  │
  ├── Data validation?
  │     → NAO retentar. Payload corrompido.
  │     → Registrar + notificar equipe
  │
  └── Runtime / OOM?
        → NAO retentar. Problema de infraestrutura.
        → Alarmar imediatamente (PagerDuty/Slack critical)
```

---

## 3. Envelope Padrao de Erro

Todo workflow que captura um erro DEVE produzir este envelope JSON padrao:

```json
{
  "severity": "critical",
  "errorClass": "server_error",
  "workflowName": "CRM Sync: Attio to Notion",
  "workflowId": "abc123",
  "failedNode": "HTTP Request — Attio",
  "errorMessage": "Request failed with status code 502",
  "errorDescription": "Upstream API returned Bad Gateway",
  "executionId": "12345",
  "executionUrl": "https://n8n.fvmarketing.com.br/workflow/abc123/executions/12345",
  "executionMode": "trigger",
  "correlationId": "abc123-12345",
  "timestamp": "2026-07-08T10:30:00.000Z",
  "_raw": {}
}
```

### Campos obrigatorios

| Campo | Tipo | Origem | Descricao |
|-------|------|--------|-----------|
| `severity` | enum | Classificacao | `critical`, `warning`, `info` |
| `errorClass` | enum | Classificacao | Vide taxonomia acima |
| `workflowName` | string | Error Trigger | Nome do workflow que falhou |
| `workflowId` | string | Error Trigger | ID interno do n8n |
| `failedNode` | string | Error Trigger | Nome do no que lancou o erro |
| `errorMessage` | string | Error Trigger | Mensagem de erro (sanitizada) |
| `executionId` | string | Error Trigger | ID da execucao |
| `executionUrl` | string | Error Trigger | Link direto para a execucao |
| `correlationId` | string | Gerado | `workflowId-executionId` — estavel entre retries |
| `timestamp` | string | Error Trigger | ISO 8601 |

---

## 4. Retry Policies

### 4.1 Node-Level Nativo (para transientes rapidos)

Configurar em **todo no HTTP Request, API third-party e Database**:

| Parametro | Valor | Motivo |
|-----------|-------|--------|
| `retryOnFail` | `true` | Habilita retry automatico |
| `maxTries` | `3` | Evita loop infinito (cap n8n: 5) |
| `waitBetweenTries` | `5000` | 5s entre tentativas (cap n8n: 5000ms) |

```typescript
{
  retryOnFail: true,
  maxTries: 3,
  waitBetweenTries: 5000,
}
```

**Limitação:** n8n nativo nao permite backoff exponencial nem classificar erro. Para 429 e 5xx persistentes, usar loop customizado.

### 4.2 Loop Customizado com Backoff (para 429 e 5xx)

Para cenarios que exigem controle fino:

```
HTTP Request
  → IF (status retryavel?)
    ├── true  → Wait (backoff exponencial + jitter)
    │            → IF (attempt < maxTries?)
    │              ├── true → HTTP Request (loop)
    │              └── false → DLQ + notificar
    └── false → DLQ + notificar
```

**Formula de backoff com jitter:**

```
waitSeconds = min(maxDelay, baseDelay * 2^(attempt-1)) ± 25%
```

- Base delay: 1-30s para APIs, 30-60s para rate limits
- Max delay: 300s (5 min)

**Code node de classificacao:**

```javascript
const code = $json.statusCode;
const transient = [408, 409, 425, 429, 500, 502, 503, 504].includes(code);
return [{
  json: {
    ...$input.first().json,
    _retryable: transient,
    _classifiedAs: transient ? 'transient' : 'permanent',
  }
}];
```

### 4.3 Tabela de Configuracao por Tipo de Node

| Tipo de Node | retryOnFail | maxTries | waitBetweenTries | Observacao |
|-------------|-------------|----------|------------------|------------|
| HTTP Request | true | 3 | 5000 | Sempre configurar |
| Supabase | true | 2 | 3000 | Falhas de rede raras |
| Slack | true | 3 | 5000 | Rate limit 429 frequente |
| Google Sheets | true | 2 | 5000 | 429 em pico |
| Redis | true | 2 | 2000 | Conexao local, rapido |
| WhatsApp/API externa | true | 3 | 5000 | Instabilidade comum |
| Code node | false | - | - | Retry nao ajuda erro de logica |
| Postgres | true | 2 | 3000 | Timeout de query |
| n8n node (API) | true | 3 | 5000 | Pode rate limitar |

### 4.4 Nunca Retentar

- **4xx (exceto 408/409/425/429):** erro e do cliente/payload
- **Data validation errors:** payload corrompido, precisa de revisao manual
- **Runtime errors:** infraestrutura, retry nao adianta
- **Auth failures (401/403):** credencial expirou, alertar equipe

---

## 5. Error Handler Central

### 5.1 Proposito

Workflow unico que captura erros de **todos** os workflows de producao. Evita N workflows de erro duplicados.

**Workflow:** `[CC] Error Handler Central` em `Orquestracao/Error Handler Central.workflow.ts`

### 5.2 Estrutura

```
Error Trigger
  → Code: Parse and Classify
    → IF: Severity Critical?
      ├── YES (critical)
      │     → Slack #incidents (mensagem detalhada)
      │     → Supabase: INSERT into error_dlq (payload completo)
      │     → Code: Circuit Breaker Check (incrementa falha)
      │       → Supabase: log circuit state
      │       → Email: report para equipe
      │
      └── NO (warning/info)
            → Slack #alerts (mensagem resumida)
            → Supabase: INSERT into error_dlq
```

### 5.3 Regras de Severidade

| Condicao | Severidade |
|----------|-----------|
| 5xx, timeout, DNS, OOM, runtime | critical |
| 429, 4xx, data_validation | warning |
| Qualquer erro sem classificacao | info |
| Workflow contem "pagamento", "auth", "billing" no nome | critical (override) |

### 5.4 Configuracao

1. **Criar** o workflow Error Handler Central (ja pronto em `.workflow.ts`)
2. **Configurar** credentials (Slack, Supabase)
3. **Vincular** manualmente em cada workflow producao:
   - Abrir workflow → **Settings** → **Error Workflow** → selecionar `[CC] Error Handler Central`
4. **Publicar** o Error Handler (Shift+P) apos qualquer alteracao

> **Importante:** O Error Workflow precisa estar **publicado** (nao em draft) para aparecer no dropdown.

---

## 6. Circuit Breaker

### 6.1 Proposito

Proteger integracoes fragilizadas contra cascata de falhas. Quando um workflow falha N vezes consecutivas, o circuit breaker "abre" e o Error Handler Central recomenda pausa.

### 6.2 Parametros

| Parametro | Valor | Descricao |
|-----------|-------|-----------|
| `FAILURE_THRESHOLD` | 5 | Falhas consecutivas para abrir |
| `COOLDOWN_MS` | 300000 (5 min) | Tempo minimo antes de half-open |
| Escopo | por workflow | Estado isolado por nome |

### 6.3 Estados

```
closed ──(5 falhas consecutivas)──→ open ──(5 min)──→ half-open
  ↑                                                      │
  └──────────────(sucesso no half-open)──────────────────┘
```

- **closed:** operando normalmente
- **open:** falhas consecutivas excederam threshold. Pular chamadas.
- **half-open:** apos cooldown. Tentar 1 chamada. Se sucesso, volta pra closed. Se falha, volta pra open.

### 6.4 Tabela de Estado

```sql
error_circuit_breaker (
  workflow_name,
  circuit_status,    -- 'closed' | 'open' | 'half-open'
  failures_consecutive,
  opened_at,
  last_failure_at,
  last_recovered_at,
  cooldown_ms
)
```

### 6.5 View de Circuitos Abertos

```sql
SELECT * FROM vw_circuits_open_now;
-- Retorna workflows com circuit breaker aberto no momento
```

---

## 7. Dead Letter Queue (DLQ)

### 7.1 Proposito

Persistencia permanente de TODAS as falhas nao-recuperaveis. Ao contrario do prune de execucoes do n8n (que apaga dados antigos), a DLQ preserva para auditoria.

### 7.2 Tabela

```sql
error_dlq (
  id, correlation_id, workflow_name, workflow_id,
  execution_id, failed_node, error_class, error_message,
  severity, payload, status, attempt, max_attempts,
  acknowledged_at, acknowledged_by, resolved_at,
  resolution_notes, created_at
)
```

### 7.3 Ciclo de Vida de um Item na DLQ

```
pending_review
  → investigating
    → resolved     (corrigido)
    → wont_fix     (decidiu nao corrigir)
    → recovered_auto (retry eventualmente funcionou)
```

### 7.4 Views Uteis

```sql
-- Erros das ultimas 24h agrupados por workflow
SELECT * FROM vw_error_summary_24h;

-- Health score geral
SELECT * FROM vw_error_health_score;
```

---

## 8. Node-Level Error Handling

### 8.1 Regra: `onError` + `main[1]`

**Todo** no fallivel (API, DB, rede, file I/O) DEVE ter:

1. `onError: "continueErrorOutput"` — cria o segundo output
2. Conexao `sourceIndex: 1` para um handler de erro

**Nao faca metade.** Um sem o outro e PIOR que nenhum — falha silenciosa.

### 8.2 Padrao de Conexao

```typescript
// Node config
{
  onError: 'continueErrorOutput',
  retryOnFail: true,
  maxTries: 3,
  waitBetweenTries: 5000,
}

// Conexao do erro
this.HttpRequest.out(1).to(this.HandleError.in(0));

// Fan-in: varios nos → mesmo handler
this.FetchUser.out(1).to(this.HandleError.in(0));
this.CallExternal.out(1).to(this.HandleError.in(0));
this.WriteDb.out(1).to(this.HandleError.in(0));
```

### 8.3 Nos que DEVEM ter error output

- HTTP Request
- Supabase / Postgres
- Slack / Email / Qualquer notificacao
- Redis
- WhatsApp / API externa
- Google Sheets / Drive
- Code nodes com logica que pode lancar excecao

### 8.4 Nos que NAO precisam

- Set / Edit Fields (validacao ja feita)
- IF / Switch (expressoes simples)
- NoOp
- Wait

---

## 9. Workflow-Level Error Workflow

### 9.1 Configuracao Obrigatoria

**TODO workflow de producao** DEVE ter um Error Workflow vinculado:

| Tipo de Workflow | Error Workflow Obrigatorio? |
|-----------------|---------------------------|
| Webhook / API | Sim |
| Schedule (cron) | Sim |
| Queue worker | Sim |
| Agent tool | Sim |
| Internal one-off | Opcional |

### 9.2 Como Configurar

1. Abrir o workflow no n8n
2. **Settings** (engrenagem ao lado do nome)
3. **Error Workflow** → selecionar `[CC] Error Handler Central`
4. Salvar
5. Publicar (`Shift + P`)

### 9.3 Recursion Trap

O Error Handler Central NAO deve notificar no mesmo canal que os workflows monitorados. Se tudo notifica Slack e o Slack cai:

- Workflow falha → Error Handler tenta notificar Slack → Slack down → Error Handler falha → ERRO PERDIDO

**Mitigacao:** Error Handler usa email como fallback principal e escreve na DLQ (Supabase) antes de qualquer notificacao. A DLQ e o registro de ultima instancia.

---

## 10. Notificacoes e Escalation

### 10.1 Canais

| Severidade | Canal Primario | Canal Fallback | Acao |
|-----------|---------------|----------------|------|
| critical | Slack #incidents | Email + DLQ | Alertar time imediatamente |
| warning | Slack #alerts | DLQ | Revisar em horario comercial |
| info | DLQ apenas | - | Apenas registro |

### 10.2 Formato Slack Critical

```
🚨 *CRITICO* — Workflow Failure
*Workflow:* CRM Sync
*Node:* HTTP Request — Attio
*Error:* Request failed with status code 502
*Class:* server_error
*Correlation:* abc123-12345
*Exec:* <URL|#12345>
*Time:* 2026-07-08T10:30:00Z
```

### 10.3 Formato Slack Warning

```
⚠️ *ALERTA* — Workflow Failure
*Workflow:* CRM Sync
*Node:* Code — Validate Data
*Error:* toDateTime can't be used on undefined value
*Class:* data_validation
*Correlation:* abc123-12345
*Time:* 2026-07-08T10:30:00Z
```

### 10.4 Escalation Chain

Tier 1: Slack (imediato)
Tier 2: SMS Twilio (15 min sem ack) — *opcional, configurar por workflow*
Tier 3: Voice call Twilio (+30 min) — *opcional, somente workflows criticos*

O ack e registrado na coluna `acknowledged_at` da `error_dlq`. Cada tier checa se ja houve ack antes de disparar.

---

## 11. Anti-Patterns

| Anti-pattern | Problema | Correcao |
|-------------|----------|---------|
| `onError` set mas `main[1]` nao conectado | Erro descartado silenciosamente; execucao mostra sucesso | Conectar handler OU voltar `onError` para `stopWorkflow` |
| Error output conectado mas `onError` nao setado | Handler nunca dispara; workflow haltado | Setar `onError: "continueErrorOutput"` |
| Unico error handler para todos os workflows | Um handler que falha = todos os erros perdidos | Usar [CC] Error Handler Central + fallback DLQ |
| Retry como unica estrategia | Payloads invalidos sao retentados sem motivo | Classificar erro antes: retry so em transiente |
| Retentar 4xx | Queima API credits e quota a toa | So retentar 408/409/425/429/5xx |
| Continue on Error sem logging | Falha silenciosa pior que crash | Sempre logar no error output |
| Error workflow notifica mesmo canal que workflows | Recursion trap: canal cai, erro desaparece | Usar canal diferente + fallback |
| Levar stack trace no response body | Vaza detalhes internos para caller | Logar privadamente, retornar mensagem sanitizada |
| Nao publicar alteracao no error handler | Codigo antigo roda em producao | Sempre Shift+P apos mudar Error Handler |
| responseCode = 200 no error branch | Caller interpreta como sucesso | Setar 4xx/5xx explicitamente |

---

## 12. Checklist de Implementacao

### Para CADA workflow de producao

#### Node-Level
- [ ] Todo HTTP Request tem `retryOnFail: true, maxTries: 3, waitBetweenTries: 5000`
- [ ] Todo Supabase/Postgres tem `retryOnFail: true, maxTries: 2`
- [ ] Todo no fallivel tem `onError: "continueErrorOutput"` E `main[1]` conectado
- [ ] Code nodes com logica complexa tem try/catch + error output
- [ ] Validacao de entrada feita UPSTREAM (antes do processamento)
- [ ] SplitInBatches em loops que processam datasets > 100 registros

#### Workflow-Level
- [ ] Error Workflow configurado em Settings (aponta para `[CC] Error Handler Central`)
- [ ] Workflow publicado (nao em draft)
- [ ] Dados de execucao salvos (`saveDataErrorExecution: 'ALL'`)
- [ ] Timezone configurada (`America/Sao_Paulo`)

#### Error Handler Central
- [ ] Credencial Slack configurada e testada
- [ ] Credencial Supabase configurada
- [ ] Dead Letter Queue populando corretamente
- [ ] Circuit breaker state sendo registrado
- [ ] Error handler publicado apos configuracao

### Para NOVOS workflows (template)

- [ ] Usar template padrao com error handling embutido
- [ ] Envelope de erro padrao implementado
- [ ] Todos os nos falliveis configurados conforme secao 8
- [ ] Error Workflow vinculado antes do deploy
- [ ] Testado com falha provocada (ex: URL invalida)

---

## 13. Plano de Retrofit

### Workflows SDR IA (prioridade maxima)

7 workflows com erro recorrente — aplicar correcoes + padrao universal:

| Workflow | Erro | Correcao ja aplicada? | Push pendente? | Retrofit necessario |
|----------|------|----------------------|---------------|-------------------|
| ADPLAN | JS timeout 25min | Sim (JSON) | Sim | + Error Workflow + DLQ + retry config |
| SIGNOR | Task runner disconnect | Server tuning | - | + Error Workflow + DLQ |
| Genics | Redis DNS | Server tuning | - | + Error Workflow + DLQ |
| SOFIA | Rate limit Chatwoot | Sim (Wait) | Sim | + Error Workflow + DLQ + retry |
| PRO ANALISES | toDateTime undefined | Sim (try/catch) | Sim | + Error Workflow + DLQ |
| Schwalm | Null constraint telefone | Sim (validation) | Sim | + Error Workflow + DLQ |
| V4 INTERNO | 404 Ekyte | Sim (validation) | Sim | + Error Workflow + DLQ |

### Workflows Command Center

| Workflow | Erro | Retrofit necessario |
|----------|------|-------------------|
| Collector | Sem tratamento de erro | + `onError` + retry + Error Workflow + DLQ |
| Heartbeat | Sem tratamento de erro | + `onError` + retry + Error Workflow + DLQ |
| Metrics | Sem tratamento de erro | + `onError` + retry + Error Workflow + DLQ |

### Passos do Retrofit

1. **Aplicar correcoes pendentes** (push dos JSONs ja corrigidos)
2. **Configurar Error Workflow** em cada workflow producao
3. **Adicionar retryOnFail** em todos os nos HTTP/DB/API
4. **Adicionar onError + main[1]** nos nos falliveis sem tratamento
5. **Subir schema v2.1** no Supabase (tabelas DLQ + circuit breaker + retry log)
6. **Testar** com falha provocada em cada workflow
7. **Validar** DLQ populando e notificacoes chegando

---

## Anexo: Referencia Rapida

### Comandos Uteis

```bash
# Listar workflows
npx n8nac list

# Status do ambiente
npx n8nac env status --json

# Validar workflow
npx n8nac verify <workflowId>

# Push de workflow
npx n8nac push caminho/workflow.workflow.ts --verify

# Credenciais necessarias
npx n8nac workflow credential-required <workflowId> --json
```

### Credenciais Necessarias

| Credencial | Uso | Onde cadastrar |
|-----------|-----|---------------|
| Slack API | Notificacoes de erro | Error Handler Central |
| Supabase API | DLQ, Circuit Breaker, Retry Log | Error Handler Central + todos SDR IA |
| SMTP | Email fallback | Error Handler Central |

### Arquivos do Padrao

| Arquivo | Descricao |
|---------|-----------|
| `Orquestracao/Error Handler Central.workflow.ts` | Workflow central de erro |
| `supabase-schema-v2.1.sql` | Schema DLQ + circuit breaker + retry log |
| `STANDARD-ERROR-HANDLING.md` | Este documento |
| `AGENTS.md` | Contexto para IA |
| `CLAUDE.md` | Contexto detalhado |

---

> **Proxima revisao:** 2026-10-08
> **Responsavel:** Equipe de Automacao / Infraestrutura
