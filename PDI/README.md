# PDI — Padrao Universal de Tratamento de Erros n8n Enterprise

> **Area:** Automacao & Infraestrutura
> **Unidade:** FV Marketing / V4 Company
> **Autor:** Marcos Perettoco
> **Data:** Julho 2026
> **Status:** Homologado

---

## Entregas desta PDI

```
PDI/
├── 1-standards/          → Documentacao do padrao (+ taxonomia, retry matrix)
├── 2-workflows/          → Workflows n8n prontos para deploy (.workflow.ts)
├── 3-supabase/           → Schema + migracao do banco de dados
├── 4-retrofit/           → Plano de retrofit para workflows existentes
├── 5-monitoring/         → Dashboards, queries e regras de alerta
├── 6-automation/         → Scripts de deploy e automacao
└── 7-apresentacao/       → Deck e script de demonstracao
```

## Problema Resolvido

7 workflows SDR IA com erro recorrente, sem padrao de tratamento, sem notificacao,
sem dead letter queue, sem circuit breaker. Falhas silenciosas que passavam dias
sem deteccao.

## Arquitetura Resumida
    
```
Node-Level (retryOnFail + onError)
  → Error Handler Central (classifica + notifica + persiste)
    → Circuit Breaker (abre apos 5 falhas)
      → Dead Letter Queue (payload completo para replay)
```

## Proximos Passos

1. Revisar `1-standards/STANDARD-ERROR-HANDLING.md`
2. Subir schema v2.1 no Supabase (`3-supabase/`)
3. Fazer push dos workflows de orquestracao (`2-workflows/`)
4. Executar retrofit nos SDR IA (`4-retrofit/`)
5. Validar com falha provocada (`5-monitoring/`)

## Metricas de Sucesso

| Metrica | Atual | Meta |
|---------|-------|------|
| Falhas silenciosas | 7 workflows sem notificacao | Zero |
| Tempo medio de deteccao | Dias | < 1 minuto |
| Taxa de auto-cura (retry) | 0% | > 70% |
| Circuitos abertos sem alerta | 100% | 0% |
