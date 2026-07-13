import { workflow, node, links } from '@n8n-as-code/transformer';

// <workflow-map>
// Workflow : [CC] Error Handler Central
// Nodes   : 10  |  Connections: 11
//
// NODE INDEX
// ──────────────────────────────────────────────────────────────────────────
// Property name                      Node type (short)         Flags
// ErrorTrigger                         errorTrigger
// ParseAndClassify                     code
// ClassifySeverity                     if
// SlackCritical                        slack                      [creds]
// SlackWarning                         slack                      [creds]
// DqInsert                             supabase                   [creds]
// SendReportEmail                      httpRequest                [creds]
// StopAndError                         noOp
// LogToSupabase                        supabase                   [creds]
// CircuitBreakerCheck                  code
//
// ROUTING MAP
// ──────────────────────────────────────────────────────────────────────────
// ErrorTrigger
//   → ParseAndClassify
//     → ClassifySeverity
//       ├── true (critical)  → SlackCritical     → StopAndError
//       │                    → DqInsert           → StopAndError
//       │                    → CircuitBreakerCheck
//       │                      → LogToSupabase
//       │                      → SendReportEmail
//       └── false (warning)  → SlackWarning       → DqInsert
//                          .out(1) (info) → LogToSupabase
// </workflow-map>

// =====================================================================
// [CC] Error Handler Central
// =====================================================================
// Proposito: Captura e trata erros de todos os workflows de producao.
//            Classifica por severidade, notifica canal correto, persiste
//            na Dead Letter Queue e avalia circuit breaker.
//
// CONFIGURE: Apos criar, vincular manualmente em Settings > Error Workflow
//            de cada workflow de producao (UI do n8n).
// =====================================================================

@workflow({
  name: '[CC] Error Handler Central',
  active: true,
  settings: {
    executionOrder: 'v1',
    errorWorkflow: '',
    timezone: 'America/Sao_Paulo',
    saveDataErrorExecution: 'ALL',
    saveDataSuccessExecution: 'ALL',
  },
})
export class ErrorHandlerCentralWorkflow {
  @node({
    name: 'Error Trigger',
    type: 'n8n-nodes-base.errorTrigger',
    version: 1,
    position: [250, 300],
  })
  ErrorTrigger = {};

  @node({
    name: 'Parse and Classify',
    type: 'n8n-nodes-base.code',
    version: 2,
    position: [500, 300],
  })
  ParseAndClassify = {
    mode: 'runOnceForAllItems',
    language: 'javaScript',
    jsCode: `
// =====================================================================
// Parse and Classify — Error Handler Central
// =====================================================================
// Recebe payload do Error Trigger e produz envelope padrao V4:
// { severity, workflowName, workflowId, failedNode, errorMessage,
//   errorClass, executionId, executionUrl, correlationId, timestamp }
// =====================================================================

const input = $input.first().json;
const execution = input.execution || {};
const workflow = input.workflow || {};
const trigger = input.trigger || {};

const workflowName = workflow.name || 'Unknown';
const workflowId = workflow.id || 'unknown';
const executionId = execution.id || 'N/A';
const executionMode = execution.mode || trigger.mode || 'unknown';
const failedNode = execution.lastNodeExecuted || (trigger.error && trigger.error.node ? trigger.error.node.name : 'Trigger');

const error = execution.error || trigger.error || {};
const errorMessageRaw = error.message || 'No error message';
const errorDescription = error.description || '';
const errorTimestamp = error.timestamp || Date.now();

// --- Correlation ID (estavel entre retries) ---
const correlationId = [workflowId, executionId].join('-');

// --- Classificacao do erro ---
const msg = errorMessageRaw.toLowerCase();
const combinedMsg = [msg, errorDescription.toLowerCase()].join(' ');

let errorClass = 'unknown';
let severity = 'info';

// Codigos HTTP
if (/5\d{2}|internal server error|upstream/i.test(combinedMsg)) {
  errorClass = 'server_error';
  severity = 'critical';
} else if (/429|rate limit|too many requests|try again later/i.test(combinedMsg)) {
  errorClass = 'rate_limit';
  severity = 'warning';
} else if (/timeout|timed out|etimedout|econnrefused/i.test(combinedMsg)) {
  errorClass = 'timeout';
  severity = 'critical';
} else if (/4\d{2}/.test(combinedMsg) && !/429/.test(combinedMsg)) {
  errorClass = 'client_error';
  severity = 'warning';
} else if (/undefined|cannot read property|null|not-null constraint/i.test(combinedMsg)) {
  errorClass = 'data_validation';
  severity = 'warning';
} else if (/dns|enotfound|getaddrinfo|resolve/i.test(combinedMsg)) {
  errorClass = 'network_dns';
  severity = 'critical';
} else if (/workflow could not be activated|activation|task runner|disconnect/i.test(combinedMsg)) {
  errorClass = 'runtime';
  severity = 'critical';
} else if (/memory|oom|heap/i.test(combinedMsg)) {
  errorClass = 'resource_exhaustion';
  severity = 'critical';
}

// Workflows critical por nome (pagamento, auth, infra)
const CRITICAL_WF_PATTERNS = [/pagamento/i, /payment/i, /auth/i, /cobranca/i, /billing/i, /order/i];
if (severity === 'info' && CRITICAL_WF_PATTERNS.some(p => p.test(workflowName))) {
  severity = 'critical';
}

return [{
  json: {
    severity,
    errorClass,
    workflowName,
    workflowId,
    failedNode,
    errorMessage: errorMessageRaw.substring(0, 500),
    errorDescription: errorDescription.substring(0, 500),
    executionId,
    executionUrl: execution.url || '',
    executionMode,
    correlationId,
    timestamp: new Date(errorTimestamp).toISOString(),
    _raw: input,
  },
}];
`,
  };

  @node({
    name: 'Severity: Critical?',
    type: 'n8n-nodes-base.if',
    version: 2.3,
    position: [750, 300],
  })
  ClassifySeverity = {
    conditions: {
      conditions: [
        {
          id: 'severity-check',
          leftValue: "={{ $json.severity }}",
          rightValue: 'critical',
          operator: {
            type: 'string',
            operation: 'equal',
          },
        },
      ],
      combinator: 'and',
      options: {
        caseSensitive: true,
        typeValidation: 'strict',
      },
    },
    options: [],
  };

  // --- CRITICAL PATH (severity = critical) ---

  @node({
    name: 'Slack Critical',
    type: 'n8n-nodes-base.slack',
    version: 2.5,
    position: [1000, 200],
    credentials: {
      slackApi: {
        id: 'COLOQUE_ID_CREDENCIAL_SLACK',
        name: 'Slack API',
      },
    },
  })
  SlackCritical = {
    resource: 'message',
    operation: 'post',
    channelId: {
      mode: 'list',
      value: 'C00000000',
    },
    select: 'channel',
    text: `🚨 *CRITICO* — Workflow Failure
*Workflow:* {{ $json.workflowName }}
*Node:* {{ $json.failedNode }}
*Error:* {{ $json.errorMessage }}
*Class:* {{ $json.errorClass }}
*Correlation:* {{ $json.correlationId }}
*Exec:* <{{ $json.executionUrl }}|#{{ $json.executionId }}>
*Time:* {{ $json.timestamp }}`,
    otherOptions: {
      unfurl_links: false,
      mrkdwn: true,
    },
  };

  @node({
    name: 'Dead Letter Insert',
    type: 'n8n-nodes-base.supabase',
    version: 1,
    position: [1250, 300],
    credentials: {
      supabaseApi: {
        id: 'COLOQUE_ID_CREDENCIAL_SUPABASE',
        name: 'Supabase API',
      },
    },
  })
  DqInsert = {
    resource: 'row',
    operation: 'create',
    tableId: 'error_dlq',
    useCustomSchema: false,
    schema: 'public',
    dataToSend: 'defineBelow',
    fieldsUi: {
      fieldValues: [
        { fieldId: 'workflow_name', fieldValue: "={{ $json.workflowName }}" },
        { fieldId: 'workflow_id', fieldValue: "={{ $json.workflowId }}" },
        { fieldId: 'execution_id', fieldValue: "={{ $json.executionId }}" },
        { fieldId: 'failed_node', fieldValue: "={{ $json.failedNode }}" },
        { fieldId: 'error_class', fieldValue: "={{ $json.errorClass }}" },
        { fieldId: 'error_message', fieldValue: "={{ $json.errorMessage }}" },
        { fieldId: 'severity', fieldValue: "={{ $json.severity }}" },
        { fieldId: 'correlation_id', fieldValue: "={{ $json.correlationId }}" },
        { fieldId: 'payload', fieldValue: "={{ JSON.stringify($json._raw) }}" },
        { fieldId: 'status', fieldValue: 'pending_review' },
      ],
    },
  };

  @node({
    name: 'Circuit Breaker Check',
    type: 'n8n-nodes-base.code',
    version: 2,
    position: [1500, 400],
  })
  CircuitBreakerCheck = {
    mode: 'runOnceForAllItems',
    language: 'javaScript',
    jsCode: `
// =====================================================================
// Circuit Breaker Check
// =====================================================================
// Usa $getWorkflowStaticData('global') para manter estado do circuit
// breaker. Se N falhas consecutivas no mesmo workflow excederem o
// threshold, recomenda pausa.
// =====================================================================

const FAILURE_THRESHOLD = 5;
const COOLDOWN_MS = 5 * 60 * 1000; // 5 min

const input = $input.first().json;
const workflowName = input.workflowName || 'unknown';
const state = $getWorkflowStaticData('global');

if (!state.circuits) {
  state.circuits = {};
}

const now = Date.now();
let circuit = state.circuits[workflowName];

if (!circuit) {
  circuit = { status: 'closed', failures: 0, openedAt: null, lastFailureAt: null };
}

circuit.lastFailureAt = now;
circuit.failures = (circuit.failures || 0) + 1;
circuit.workflowName = workflowName;

let circuitAction = 'none';
let circuitStatus = circuit.status;

if (circuit.failures >= FAILURE_THRESHOLD && circuit.status !== 'open') {
  circuit.status = 'open';
  circuit.openedAt = now;
  circuitStatus = 'open';
  circuitAction = 'OPENED';
} else if (circuit.status === 'open') {
  const elapsed = now - circuit.openedAt;
  if (elapsed > COOLDOWN_MS) {
    circuit.status = 'half-open';
    circuitStatus = 'half-open';
    circuitAction = 'half-open';
  } else {
    circuitAction = 'skip';
    circuit.retryAfterMs = COOLDOWN_MS - elapsed;
  }
}

state.circuits[workflowName] = circuit;

return [{
  json: {
    ...input,
    circuitStatus,
    circuitAction,
    circuitFailures: circuit.failures,
    circuitRetryAfterMs: circuit.retryAfterMs || 0,
    circuitOpenedAt: circuit.openedAt ? new Date(circuit.openedAt).toISOString() : null,
  },
}];
`,
  };

  @node({
    name: 'Log Circuit to Supabase',
    type: 'n8n-nodes-base.supabase',
    version: 1,
    position: [1750, 400],
    credentials: {
      supabaseApi: {
        id: 'COLOQUE_ID_CREDENCIAL_SUPABASE',
        name: 'Supabase API',
      },
    },
  })
  LogToSupabase = {
    resource: 'row',
    operation: 'create',
    tableId: 'error_circuit_breaker',
    useCustomSchema: false,
    schema: 'public',
    dataToSend: 'defineBelow',
    fieldsUi: {
      fieldValues: [
        { fieldId: 'workflow_name', fieldValue: "={{ $json.workflowName }}" },
        { fieldId: 'circuit_status', fieldValue: "={{ $json.circuitStatus }}" },
        { fieldId: 'circuit_action', fieldValue: "={{ $json.circuitAction }}" },
        { fieldId: 'failures_consecutive', fieldValue: "={{ $json.circuitFailures }}" },
        { fieldId: 'execution_id', fieldValue: "={{ $json.executionId }}" },
        { fieldId: 'correlation_id', fieldValue: "={{ $json.correlationId }}" },
      ],
    },
  };

  @node({
    name: 'Send Report Email',
    type: 'n8n-nodes-base.httpRequest',
    version: 4.4,
    position: [1750, 200],
    credentials: {
      smtp: {
        id: 'COLOQUE_ID_CREDENCIAL_SMTP',
        name: 'SMTP',
      },
    },
  })
  SendReportEmail = {
    url: '', // Configurar via email node ou SMTP conforme disponivel
    method: 'POST',
    authentication: 'none',
    sendBody: false,
    options: {},
  };

  // --- WARNING PATH (severity = warning) ---

  @node({
    name: 'Slack Warning',
    type: 'n8n-nodes-base.slack',
    version: 2.5,
    position: [1000, 500],
    credentials: {
      slackApi: {
        id: 'COLOQUE_ID_CREDENCIAL_SLACK',
        name: 'Slack API',
      },
    },
  })
  SlackWarning = {
    resource: 'message',
    operation: 'post',
    channelId: {
      mode: 'list',
      value: 'C00000000',
    },
    select: 'channel',
    text: `⚠️ *ALERTA* — Workflow Failure
*Workflow:* {{ $json.workflowName }}
*Node:* {{ $json.failedNode }}
*Error:* {{ $json.errorMessage }}
*Class:* {{ $json.errorClass }}
*Correlation:* {{ $json.correlationId }}
*Time:* {{ $json.timestamp }}`,
    otherOptions: {
      unfurl_links: false,
      mrkdwn: true,
    },
  };

  @node({
    name: 'Stop and Error',
    type: 'n8n-nodes-base.noOp',
    version: 1,
    position: [2000, 300],
  })
  StopAndError = {};

  // =====================================================================
  // ROUTING
  // =====================================================================

  @links()
  defineRouting() {
    this.ErrorTrigger.out(0).to(this.ParseAndClassify.in(0));
    this.ParseAndClassify.out(0).to(this.ClassifySeverity.in(0));

    // Critical path
    this.ClassifySeverity.out(0).to(this.SlackCritical.in(0));
    this.ClassifySeverity.out(0).to(this.DqInsert.in(0));

    this.SlackCritical.out(0).to(this.CircuitBreakerCheck.in(0));
    this.CircuitBreakerCheck.out(0).to(this.LogToSupabase.in(0));
    this.CircuitBreakerCheck.out(0).to(this.SendReportEmail.in(0));
    this.CircuitBreakerCheck.out(0).to(this.StopAndError.in(0));

    // Warning/info path
    this.ClassifySeverity.out(1).to(this.SlackWarning.in(0));
    this.SlackWarning.out(0).to(this.DqInsert.in(0));
    this.DqInsert.out(0).to(this.StopAndError.in(0));
  }
}
