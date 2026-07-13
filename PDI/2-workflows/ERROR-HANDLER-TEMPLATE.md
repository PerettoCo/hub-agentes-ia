# Template de Error Handling para Novos Workflows

Use este template ao criar um NOVO workflow para garantir conformidade com o padrao.

## Estrutura Minima

```typescript
// Em cada no fallivel (HTTP Request, Supabase, etc), adicionar:
{
  onError: 'continueErrorOutput',
  retryOnFail: true,
  maxTries: 3,
  waitBetweenTries: 5000,
}

// Roteamento:
this.NohFallivel.out(0).to(this.ProximoNo.in(0));   // sucesso
this.NohFallivel.out(1).to(this.HandleError.in(0));  // erro
```

## Workflow Completo (Webhook API)

```
Webhook (responseMode: "responseNode")
  → Set: Validate Schema
    → IF: valid?
      ├── NO → Respond 400 (validation_error)
      └── YES → HTTP Request (retryOnFail + onError)
                  ├── success → Respond 200 (dados)
                  └── error → Respond 502 (upstream_error)
```

## Checklist Rapido para Novos Workflows

- [ ] `retryOnFail: true` em todo HTTP Request, Supabase, API externa
- [ ] `onError: "continueErrorOutput"` nos nos falliveis
- [ ] `main[1]` conectado para cada no com `onError`
- [ ] Error Workflow vinculado em Settings (aponta para `[CC] Error Handler Central`)
- [ ] Workflow publicado (Shift+P)
- [ ] Testado com falha provocada (ex: URL invalida)
