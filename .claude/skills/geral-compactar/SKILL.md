---
name: geral-compactar
description: >-
  Economia de contexto e tokens. Analisa o uso atual de contexto, identifica
  desperdícios, comprime prompts longos, resume histórico de conversas e sugere
  estratégias para maximizar o token budget. Use quando o usuário disser
  "contexto cheio", "token estourando", "resume essa conversa", "comprime isso",
  "economia de token", "otimizar contexto", "prompt muito longo", "resumir
  histórico" ou "/compactar".
area: geral
author: V4 Company
version: 1.0.0
---

Analisa e otimiza o uso de contexto/tokens na sessão atual.

## Estratégias de compressão

### 1. Análise de uso
- Estima tokens usados no contexto atual (entrada + saída acumulada)
- Identifica mensagens grandes ou冗余
- Aponta attachments/imagens que consomem muito

### 2. Compressão de prompt
Recebe um prompt longo e o reescreve mantendo 100% do significado com 40-60% menos tokens:
- Remove redundâncias e reformulações
- Condensa instruções multi-parágrafo em uma
- Elimina preâmbulos desnecessários ("como assistente IA...")
- Unifica exemplos duplicados
- Usa termos precisos no lugar de circumlóquios

### 3. Resumo de histórico
Quando o contexto está próximo do limite:
- Gera resumo estruturado da conversa até agora
- Preserva decisões tomadas, arquivos criados, comandos executados
- Mantém referências a arquivos e linhas específicas
- Descarta apenas iterações/explorações que não agregam

### 4. Estratégia de continuidade
Recomenda:
- Salvar sessão atual (`/session-save`) antes de limpar
- Usar `small_model` para tarefas simples
- Separar em skills o que for reutilizável
- Iniciar sessão nova com resumo carregado

## Modos de uso

| Comando | Descrição |
|---------|-----------|
| `/compact` | Executa análise completa e sugere compressão |
| `/compact analyze` | Só analisa, não comprime |
| `/compact compress <texto>` | Comprime um prompt específico |
| `/compact resume` | Gera resumo do histórico pra continuar depois |
