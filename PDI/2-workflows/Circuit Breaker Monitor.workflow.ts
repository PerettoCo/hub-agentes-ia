import { workflow, node, links } from '@n8n-as-code/transformer';

// <workflow-map>
// Workflow : [CC] Circuit Breaker Monitor
// Nodes   : 6  |  Connections: 6
//
// NODE INDEX
// ──────────────────────────────────────────────────────────────────────────
// Property name                      Node type (short)         Flags
// ScheduleTrigger                      scheduleTrigger
// QueryOpenCircuits                    supabase                   [creds]
// HasOpenCircuits                      if
// SlackAlert                           slack                      [creds]
// AttemptRecovery                      httpRequest                [creds]
// LogRecovery                          supabase                   [creds]
//
// ROUTING MAP
// ──────────────────────────────────────────────────────────────────────────
// ScheduleTrigger
//   → QueryOpenCircuits
//     → HasOpenCircuits
//       ├── true  → SlackAlert → AttemptRecovery → LogRecovery
//       └── false → (fim, sem acao)
// </workflow-map>

// =====================================================================
// [CC] Circuit Breaker Monitor
// =====================================================================
// Proposito: Consulta a view vw_circuits_open_now a cada 5 min.
//            Se houver circuitos abertos, notifica o squad e tenta
//            recovery (PATCH no workflow para reativa-lo).
// =====================================================================

@workflow({
  name: '[CC] Circuit Breaker Monitor',
  active: true,
  settings: {
    executionOrder: 'v1',
    timezone: 'America/Sao_Paulo',
    saveDataErrorExecution: 'ALL',
    saveDataSuccessExecution: 'ALL',
  },
})
export class CircuitBreakerMonitorWorkflow {
  @node({
    name: 'Schedule Trigger',
    type: 'n8n-nodes-base.scheduleTrigger',
    version: 1,
    position: [250, 300],
  })
  ScheduleTrigger = {
    rule: {
      interval: [
        {
          field: 'minutes',
          minutesInterval: 5,
        },
      ],
    },
  };

  @node({
    name: 'Query Open Circuits',
    type: 'n8n-nodes-base.supabase',
    version: 1,
    position: [500, 300],
    credentials: {
      supabaseApi: {
        id: 'COLOQUE_ID_CREDENCIAL_SUPABASE',
        name: 'Supabase API',
      },
    },
  })
  QueryOpenCircuits = {
    resource: 'row',
    operation: 'getAll',
    tableId: 'vw_circuits_open_now',
    returnAll: true,
  };

  @node({
    name: 'Has Open Circuits?',
    type: 'n8n-nodes-base.if',
    version: 2.3,
    position: [750, 300],
  })
  HasOpenCircuits = {
    conditions: {
      conditions: [
        {
          id: 'circuit-check',
          leftValue: "={{ $json.workflow_name }}",
          rightValue: '',
          operator: {
            type: 'string',
            operation: 'notEmpty',
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

  @node({
    name: 'Slack Circuit Alert',
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
  SlackAlert = {
    resource: 'message',
    operation: 'post',
    channelId: {
      mode: 'list',
      value: 'C00000000',
    },
    select: 'channel',
    text: `🔴 *Circuit Breaker OPEN*
*Workflow:* {{ $json.workflow_name }}
*Falhas consecutivas:* {{ $json.failures_consecutive }}
*Aberto ha:* {{ $json.minutes_open }} min
*Timestamp:* {{ $json.opened_at }}`,
    otherOptions: {
      unfurl_links: false,
      mrkdwn: true,
    },
  };

  @node({
    name: 'Attempt Recovery',
    type: 'n8n-nodes-base.httpRequest',
    version: 4.4,
    position: [1250, 200],
  })
  AttemptRecovery = {
    method: 'PATCH',
    url: "={{ 'https://n8n-oja8.srv1666908.hstgr.cloud/api/v1/workflows/' + $json.workflow_id }}",
    authentication: 'predefinedCredentialType',
    nodeCredentialType: 'n8nApi',
    sendBody: true,
    contentType: 'json',
    specifyBody: 'json',
    jsonBody: "={ \"active\": true }",
    options: {
      retryOnFail: true,
      maxTries: 2,
      waitBetweenTries: 5000,
    },
  };

  @node({
    name: 'Log Recovery',
    type: 'n8n-nodes-base.supabase',
    version: 1,
    position: [1500, 200],
    credentials: {
      supabaseApi: {
        id: 'COLOQUE_ID_CREDENCIAL_SUPABASE',
        name: 'Supabase API',
      },
    },
  })
  LogRecovery = {
    resource: 'row',
    operation: 'create',
    tableId: 'error_circuit_breaker',
    useCustomSchema: false,
    schema: 'public',
    dataToSend: 'defineBelow',
    fieldsUi: {
      fieldValues: [
        { fieldId: 'workflow_name', fieldValue: "={{ $json.workflow_name }}" },
        { fieldId: 'workflow_id', fieldValue: '' },
        { fieldId: 'circuit_status', fieldValue: 'closed' },
        { fieldId: 'circuit_action', fieldValue: 'closed_recovered' },
        { fieldId: 'failures_consecutive', fieldValue: '0' },
        { fieldId: 'last_recovered_at', fieldValue: "={{ new Date().toISOString() }}" },
      ],
    },
  };

  @links()
  defineRouting() {
    this.ScheduleTrigger.out(0).to(this.QueryOpenCircuits.in(0));
    this.QueryOpenCircuits.out(0).to(this.HasOpenCircuits.in(0));

    this.HasOpenCircuits.out(0).to(this.SlackAlert.in(0));
    this.SlackAlert.out(0).to(this.AttemptRecovery.in(0));
    this.AttemptRecovery.out(0).to(this.LogRecovery.in(0));
  }
}
