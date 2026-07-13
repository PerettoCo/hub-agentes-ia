# Envelope Padrao de Erro — Referencia Rapida

## Schema

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

## Campos

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| `severity` | `critical | warning | info` | Sim | Nivel de impacto |
| `errorClass` | `server_error | rate_limit | timeout | client_error | data_validation | network_dns | runtime | resource_exhaustion | unknown` | Sim | Taxonomia do erro |
| `workflowName` | string | Sim | Nome do workflow que falhou |
| `workflowId` | string | Sim | ID interno n8n |
| `failedNode` | string | Sim | Nome do no que lancou a excecao |
| `errorMessage` | string | Sim | Mensagem (sanitizada, max 500 chars) |
| `executionId` | string | Sim | ID da execucao |
| `executionUrl` | string | Nao | Link direto para a execucao |
| `correlationId` | string | Sim | `{workflowId}-{executionId}` — estavel entre retries |
| `timestamp` | string (ISO 8601) | Sim | Momento do erro |

## Codigo de Referencia (Code node)

```javascript
const input = $input.first().json;
const execution = input.execution || {};
const workflow = input.workflow || {};
const error = execution.error || {};
const msg = (error.message || '').toLowerCase();

let errorClass = 'unknown';
let severity = 'info';

if (/5\d{2}|internal server error|upstream/i.test(msg)) {
  errorClass = 'server_error'; severity = 'critical';
} else if (/429|rate limit|too many/i.test(msg)) {
  errorClass = 'rate_limit'; severity = 'warning';
} else if (/timeout|etimedout|econnrefused/i.test(msg)) {
  errorClass = 'timeout'; severity = 'critical';
} else if (/undefined|cannot read|null|not-null/i.test(msg)) {
  errorClass = 'data_validation'; severity = 'warning';
} else if (/dns|enotfound|getaddrinfo/i.test(msg)) {
  errorClass = 'network_dns'; severity = 'critical';
} else if (/task runner|disconnect|activation/i.test(msg)) {
  errorClass = 'runtime'; severity = 'critical';
} else if (/memory|oom|heap/i.test(msg)) {
  errorClass = 'resource_exhaustion'; severity = 'critical';
}

return [{
  json: {
    correlationId: [workflow.id, execution.id].join('-'),
    severity,
    errorClass,
    workflowName: workflow.name || 'Unknown',
    workflowId: workflow.id,
    failedNode: execution.lastNodeExecuted || 'Trigger',
    errorMessage: (error.message || '').substring(0, 500),
    executionId: execution.id,
    executionUrl: execution.url || '',
    timestamp: new Date().toISOString(),
  }
}];
```
