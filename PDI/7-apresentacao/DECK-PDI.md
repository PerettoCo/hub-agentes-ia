# PDI — Apresentacao: Padrao Universal de Tratamento de Erros n8n

> **Formato:** 15-20 slides | **Tempo:** 20-25 min
> **Audiencia:** Tech Lead + Squad de Automacao

---

## Slide 1: Titulo

```
PDI: PADRAO UNIVERSAL DE TRATAMENTO DE ERROS
              N8N ENTERPRISE

        Marcos Perettoco — Tech Lead
        Julho 2026 | FV Marketing / V4
```

---

## Slide 2: O Problema

**7 workflows SDR IA com erro recorrente**

- ADPLAN: JS timeout 25min (event loop bloqueado)
- SIGNOR: Task runner desconectado
- Genics: Redis Cloud inacessivel
- SOFIA: Rate limit Chatwoot
- PRO ANALISES: toDateTime undefined
- Schwalm: Null constraint telefone
- V4 INTERNO: 404 no Ekyte

**E o pior:** nenhum notificava ninguem. Falhas passavam dias sem deteccao.

---

## Slide 3: Diagnostico

3 Command Centers tambem sem tratamento de erro:

| Workflow | Trigger | Risco |
|----------|---------|-------|
| Collector | 2min | Dashboard desatualizado |
| Heartbeat | 5min | Falso positivo de saude |
| Metrics | 1h | Lacuna historica |

**Causa raiz:** Cada workflow tratava erro do seu jeito (ou nao tratava).

---

## Slide 4: A Solucao — Arquitetura em 3 Camadas

```
┌─────────────────────────────────────────────┐
│  CAMADA 1: Node-Level (retry + continue)    │
│  Captura ~73% das falhas transientes        │
├─────────────────────────────────────────────┤
│  CAMADA 2: Error Handler Central            │
│  Classifica, notifica, persiste na DLQ      │
├─────────────────────────────────────────────┤
│  CAMADA 3: Circuit Breaker + Dead Letter    │
│  Protege APIs fragilizadas, permite replay  │
└─────────────────────────────────────────────┘
```

---

## Slide 5: Antes vs Depois

| Antes | Depois |
|-------|--------|
| Cada workflow seu proprio jeito | Padrao unificado |
| Falha silenciosa | Notificacao em < 1 min |
| Sem retry | Retry com backoff exponencial |
| Sem persistencia | Dead Letter Queue no Supabase |
| Sem protecao | Circuit breaker integrado |
| Debug manual | Correlation ID + payload completo |

---

## Slide 6: Taxonomia de Erros

| Classe | Severidade | Retentavel? | Exemplo |
|--------|-----------|-------------|---------|
| server_error | critical | Sim (3x) | 502, 503 |
| rate_limit | warning | Sim (c/ backoff) | 429 |
| timeout | critical | Sim (3x) | ETIMEDOUT |
| client_error | warning | Nunca | 400, 401, 403 |
| data_validation | warning | Nunca | null constraint |
| network_dns | critical | Sim (3x) | ENOTFOUND |
| runtime | critical | Nunca | Task runner |
| resource_exhaustion | critical | Nunca | OOM |

---

## Slide 7: Retry Matrix

Cada tipo de node tem configuracao especifica:

```
HTTP Request  → 3 tries, 5s wait
Supabase      → 2 tries, 3s wait
Slack         → 3 tries, 5s wait
WhatsApp      → 3 tries, 5s wait
Code node     → NUNCA retentar
```

Backoff exponencial com jitter para 429 e 5xx.

---

## Slide 8: Entregas Concretas

```
PDI/
├── 1-standards/        → Documentacao, taxonomia, retry matrix
├── 2-workflows/        → 2 workflows .workflow.ts (validados)
├── 3-supabase/         → Schema v2.1 + guia de migracao
├── 4-retrofit/         → Planos de retrofit SDR IA + CC
├── 5-monitoring/       → Dashboards + queries de alerta
├── 6-automation/       → Scripts de deploy automatizado
└── 7-apresentacao/     → Este deck
```

---

## Slide 9: Error Handler Central (Camada 2)

Workflow unico que captura erros de TODOS os workflows.

```
Error Trigger
  → Code: Parse and Classify
    → IF: Severity Critical?
      ├── YES → Slack #incidents → DLQ → Circuit Breaker
      └── NO  → Slack #alerts → DLQ
```

- 10 nodes
- Validado com n8nac skills
- Notifica Slack, persiste no Supabase

---

## Slide 10: Circuit Breaker (Camada 3)

Protege integracoes contra cascata de falhas.

```
closed ──(5 falhas)──→ open ──(5 min)──→ half-open
  ↑                                            │
  └──────────(sucesso)─────────────────────────┘
```

- Monitor a cada 5 min
- Recovery automatico via PATCH na API n8n
- Log de todos os estados no Supabase

---

## Slide 11: Dead Letter Queue

Persistencia PERMANENTE de todas as falhas.

```
error_dlq (
  id, correlation_id, workflow_name,
  failed_node, error_class, severity,
  payload (JSONB), status,
  acknowledged_at, resolved_at
)
```

- 4 novas views de monitoramento
- Payload completo preservado para replay
- Ciclo de vida: pending → investigating → resolved

---

## Slide 12: Retrofit SDR IA

5 workflows com correcoes aplicadas mas nunca pushed.

| Workflow | Correcao | Esforco |
|----------|---------|---------|
| ADPLAN | SplitInBatches + Code otimizado | 20 min |
| SOFIA | Wait 500ms + Error Workflow | 10 min |
| PRO ANALISES | try/catch toDateTime | 10 min |
| Schwalm | Validacao telefone + IF | 10 min |
| V4 INTERNO | Board ID map + IF | 10 min |

Fase 1: Push (1 dia)
Fase 2: Configurar error handling (2 dias)
Fase 3: Validacao (1 dia)

---

## Slide 13: Metricas de Sucesso

| Metrica | Antes | Meta | Como Medir |
|---------|-------|------|-----------|
| Deteccao de falha | Dias | < 1 min | Tempo entre erro e notificacao |
| Auto-cura (retry) | 0% | > 70% | `vw_retry_success_rate` |
| Circuitos abertos sem alerta | 100% | 0% | `vw_circuits_open_now` |
| Workflows com error handling | 0 | 100% | `error_dlq` populando |
| Tempo de retrofit | - | 5 dias | Milestone tracking |

---

## Slide 14: Proximos Passos

```
Semana 1:
  Seg: Subir schema v2.1 no Supabase
  Ter: Push Error Handler Central + Circuit Monitor
  Qua: Configurar credenciais (Slack, Supabase)
  Qui: Vincular Error Workflow nos SDR IA
  Sex: Vincular Error Workflow nos Command Center

Semana 2:
  Seg: Validar com falha provocada
  Ter: Dashboard + alertas
  Qua: Documentar e apresentar resultados
```

---

## Slide 15: Perguntas?

```
"O que era silencioso agora grita.
O que quebrava sem rastro agora deixa DNA.
O que era 7 jeitos diferentes agora e um padrao."
```

---

## Slide 16: Anexo — Anti-Patterns

| Anti-pattern | Problema |
|-------------|----------|
| `onError` sem `main[1]` | Erro descartado silenciosamente |
| Retentar 4xx | Queima API credits a toa |
| Error workflow mesmo canal | Recursion trap |
| responseCode 200 no erro | Caller nunca ve a falha |
| Nao publicar error handler | Codigo antigo rodando |
