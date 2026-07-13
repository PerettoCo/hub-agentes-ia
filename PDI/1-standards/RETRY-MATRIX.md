# Retry Matrix — Configuracao por Tipo de Node

## Configuracao Nativa (node-level)

| Tipo de Node | retryOnFail | maxTries | waitBetweenTries | Observacao |
|-------------|-------------|----------|------------------|------------|
| HTTP Request | true | 3 | 5000 | Sempre configurar |
| Supabase API | true | 2 | 3000 | Rede interna, falhas raras |
| Slack | true | 3 | 5000 | 429 frequente em pico |
| Google Sheets | true | 2 | 5000 | Rate limit em batch |
| Redis | true | 2 | 2000 | Conexao local, rapido |
| WhatsApp / API externa | true | 3 | 5000 | Instabilidade comum |
| Postgres | true | 2 | 3000 | Timeout de query |
| n8n node (API interna) | true | 3 | 5000 | Pode rate limitar |
| Code (JavaScript/Python) | false | - | - | Retry nao ajuda erro de logica |
| Set / Edit Fields | false | - | - | Dados ja validados |
| IF / Switch | false | - | - | Expressoes simples |

## Configuracao Customizada (loop com backoff)

Para cenarios que exigem controle fino (429, 5xx persistentes):

```typescript
// Parametros do loop customizado
{
  baseDelay: 1000,       // 1s inicial
  maxDelay: 300000,      // 5s maximo
  maxTries: 3,
  multiplier: 2,          // Exponencial: 1s, 2s, 4s
  jitterPercent: 25,      // Mais ou menos 25% aleatorio
}
```

### Codigo de Backoff

```javascript
// Code node - calcular wait com jitter
const attempt = $input.first().json._attempt || 1;
const baseDelay = 1000;   // 1s
const maxDelay = 300000;  // 5min
const multiplier = 2;

const waitMs = Math.min(
  maxDelay,
  baseDelay * Math.pow(multiplier, attempt - 1)
);
const jitter = waitMs * (0.25 * (Math.random() * 2 - 1));
const finalWait = Math.round(waitMs + jitter);

return [{ json: { _waitMs: finalWait, _attempt: attempt + 1 } }];
```

## Codigos HTTP: Retentar ou Nao?

| Status | Retentar? | Acao |
|--------|-----------|------|
| 400 | Nao | Payload invalido — revisar manualmente |
| 401 | Nao | Credencial expirou — alertar equipe imediatamente |
| 403 | Nao | Permissao negada — alertar equipe |
| 404 | Nao | Endpoint/URL mudou — revisar |
| 408 | Sim (3x) | Timeout do servidor — backoff |
| 409 | Sim (3x) | Conflito — retentar com backoff |
| 422 | Nao | Dado mal formatado — revisar payload |
| 425 | Sim (3x) | Very Early — retentar |
| 429 | Sim (3x) | Rate limit — respeitar Retry-After se presente |
| 500 | Sim (3x) | Erro interno do servidor |
| 502 | Sim (3x) | Upstream com problema |
| 503 | Sim (3x) | Servico indisponivel |
| 504 | Sim (3x) | Timeout do upstream |
