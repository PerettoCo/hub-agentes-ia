---
name: account-checkin-review
description: Pos-call de check-in. Le o transcript do Gemini Notes (ou texto colado) da call que acabou e atualiza o Mission Control do cliente — registra combinados, atualiza apostas vivas (vivas/mortas/novas), refina personas com base nas provocacoes da call, e adiciona entrada no historico de check-ins. Tambem entrega diagnostico ROPRE-by-ROPRE da call e 3 ataques que o account defendeu mal pra alimentar o proximo roleplay. Use sempre que o usuario terminar uma reuniao de check-in com cliente, mencionar transcript de call, fechar uma reuniao, ou quiser revisar como uma call saiu — mesmo que nao fale "review" explicitamente.
area: account
author: guilhermelippert
version: 1.0.0
aliases: [account-checkin-review]
tags: [skill, area-account]
---
# Account — Check-in Review

Skill que fecha o ciclo do check-in. Pega o transcript da call que acabou, atualiza o Mission Control do cliente, entrega diagnóstico ROPRE-by-ROPRE da call e lista 3 ataques mal defendidos pra alimentar o próximo `account-checkin-roleplay`.

## O que essa skill produz

1. **Mission Control atualizado** — `combinados.md`, `apostas-vivas.md`, `personas-call.md`, `historico-checkins.md` recebem updates atômicos (Edit, não Write — preserva histórico).
2. **Diagnóstico ROPRE-by-ROPRE** da call que acabou — bloco a bloco, classificado como Forte / Médio / Fraco / Ausente, com nota do que falhou.
3. **3 ataques mal defendidos** extraídos da call — viram input direto pra próxima execução de `account-checkin-roleplay`.
4. **Arquivo em `checkins/`** — salva a review em `checkins/{YYYY-MM-DD}-review.md`.

## Pré-requisitos

- Transcript da call (idealmente o `.md` do Gemini Notes em `calls/`, ou texto colado pelo account).
- Mission Control existente em `squads/{squad}/clientes/{cliente}/mission-control/`. Se não existir, recomende rodar `/contexto` primeiro.

## Quando triggera

- "Acabei o check-in com {cliente}, vamos revisar"
- "Aqui o transcript da call de hoje, faz a review"
- "Como foi a call do {cliente}? Pega o transcript em /calls/"
- "Atualiza o mission-control do {cliente} com o que rolou"
- "Quero treinar pra próxima — o que o cliente atacou hoje?"

## Fluxo

### Passo 1 — Localizar transcript e cliente

Pergunte qual cliente se o usuário não disser. Localize a pasta `squads/{squad}/clientes/{cliente}/`.

Procure o transcript mais recente em `calls/` (mais recente por data no nome de arquivo ou mtime). Confirme: *"É essa call: {nome}? Sim/não?"*

Se o account colou texto direto na conversa (não tem arquivo), use o texto colado e ofereça salvar em `calls/{YYYY-MM-DD}-checkin.md` no fim.

### Passo 2 — Ler transcript inteiro

Leia o transcript completo. Se for muito longo (>20k tokens), use Read com offset/limit em chunks ou despache subagente pra extração estruturada. Foque nas seções "Resumo", "Detalhes", "Próximas etapas" do Gemini Notes — são onde mora o que importa.

### Passo 3 — Extrair os 4 elementos do MC

**A. Combinados novos** — toda decisão "{dono} faz {X} até {prazo}" vira entrada Pendente em `combinados.md`. Quando o transcript indica explicitamente que combinado anterior foi cumprido, mover de Pendentes pra Feitos com data de conclusão.

**B. Apostas vivas — mudanças** — comparar com `apostas-vivas.md` atual:
- **Confirmada** (sinal positivo + prazo cumprido) → marcar status "CONFIRMADA — escalar conforme plano". Aposta continua viva, não some.
- **Morta** (sinal negativo + prazo cumprido) → mover pra "Histórico de apostas" no fim do arquivo, com data e aprendizado.
- **Aposta nova nasceu** (cliente ou time propôs nova tese na call) → adicionar em "Apostas vivas" com schema completo (4 colunas).
- **Em curso** (prazo ainda não atingido) → continua como está.

**C. Persona — gatilhos novos** — ler o transcript com lente de persona:
- Provocações novas que o stakeholder fez → adicionar em "Padrões de provocação" do arquivo dele em `personas-call.md`.
- Frases marcantes → adicionar em "Frases típicas" (citação literal preferível).
- Mudança de comportamento (passivo virou ativo, agressivo amaciou) → nota datada na seção da pessoa.

**D. Histórico — entrada nova** — append em `historico-checkins.md`. Esse arquivo e apenas para calls reais/transcripts. Preparacoes e ensaios ficam em `historico-preparacoes.md`. Schema obrigatório:
```
## YYYY-MM-DD — {Tipo da call}
**Modo:** TEM | SEM | ND (anterior ao framework V2)
**Resumo (1 linha):** {...}
**Transcript:** [link relativo](../calls/{nome}.md)
**Pontos críticos:**
- {1-3 bullets}
**Treinar próximo:** ver os 3 ataques mal defendidos abaixo
```

### Passo 4 — Diagnóstico ROPRE-by-ROPRE

Leia o transcript com a lente do ROPRE V2: **Onde paramos / R / O / P+R(Apostas Vivas) / E / Combinados**.

Para cada bloco, classifique:
- **Forte** — bloco saiu com diagnose clara, decisão tomada, cliente engajado
- **Médio** — saiu mas raso, sem decisão clara, conversa fiada
- **Fraco** — virou garçom (lista de tarefas sem narrativa) ou foi pulado
- **Ausente** — bloco não foi feito

Para cada bloco fraco/médio, escreva 1 linha de "o que faltou". Esse diagnóstico é pra o account aprender o padrão dele, não pra penalizar.

### Passo 5 — Identificar 3 ataques mal defendidos

Encontre 3 momentos no transcript onde o cliente provocou e o account titubeou. **Sinais de defesa fraca:**
- Resposta longa demais (geralmente vergonha)
- Mudança de assunto rápida
- "Vou avaliar e te volto" usado pra escapar (não pra ganhar tempo legítimo)
- Contradição com call anterior (combinado anterior negado ou esquecido)
- Cliente repete a pergunta porque a resposta não fechou
- Concordância passiva sem argumentação

Para cada um dos 3:
- **Provocação literal do cliente** (citação)
- **Defesa que o account deu** (resumo curto)
- **Por que foi fraca** (qual sinal acima)
- **Script alternativo** ("ele deveria ter dito: ...") — propositivo, não defensivo

Esses 3 vão pra "Treinar próximo" no `historico-checkins.md` e alimentam diretamente `account-checkin-roleplay` na próxima preparação.

### Passo 6 — Aplicar updates

Use **`Edit` (não `Write`)** em cada arquivo do mission-control pra preservar histórico. Cada edição é atômica (1 arquivo, 1 update conceitual). Antes de editar, leia o arquivo se ainda não leu.

Após aplicar, mostre ao account um resumo:
- ✅ {N} combinados novos registrados | {M} marcados como feitos
- 🟢 {N} apostas confirmadas
- 🔴 {N} apostas mortas (com aprendizado registrado)
- 🆕 {N} apostas novas nascendo
- 👤 personas atualizadas: {nomes}
- 📝 entrada {YYYY-MM-DD} adicionada em historico-checkins.md

### Passo 7 — Entregar relatório final

Estrutura do output:

```markdown
# Review Check-in {Cliente} — {YYYY-MM-DD}

## Diagnóstico ROPRE
- **Onde paramos:** Forte | Médio | Fraco | Ausente — {nota se não Forte}
- **R Resultados:** ...
- **O Objetivos:** ...
- **P+R Apostas Vivas:** ...
- **E Entregas:** ...
- **Combinados:** ...

**Nota geral:** {síntese — call foi forte/média/fraca; ponto crítico foi X}

## 3 ataques mal defendidos (treinar próximo)

### Ataque 1
**Provocação ({stakeholder}):** "{citação literal}"
**Defesa do account:** {resumo}
**Por que foi fraca:** {sinal — ex: resposta longa demais, mudou assunto}
**Script alternativo:** "{...}"

### Ataque 2
[mesmo formato]

### Ataque 3
[mesmo formato]

## Updates aplicados ao Mission Control
{resumo do passo 6 com bullets}

## Recomendação
{próxima ação concreta — ex: "rode account-checkin-roleplay 1 semana antes da próxima call, com foco nos 3 ataques acima. Cliente em risco de churn? Sim/não."}
```

Salve o relatorio final em `checkins/{YYYY-MM-DD}-review.md`. Se `checkins/` nao existir, crie. O transcript bruto continua em `calls/`.

## Regras

- **Não invente** — se algo não está claro no transcript, marque com `[A CONFIRMAR]` em vez de chutar.
- **Append-only** em `personas-call.md` e `historico-checkins.md` — nunca sobrescreva entrada anterior. Use `Edit` adicionando ao fim das seções relevantes.
- **Nao misture preparacao com call real** — se o material analisado for ensaio/prep, nao rode esta skill; use `account-checkin-roleplay`, que escreve em `historico-preparacoes.md`.
- **Combinados feitos preservam** — quando mover de Pendentes pra Feitos, mantenha o registro completo (não apague).
- **Apostas mortas vão pro histórico**, não somem — o aprendizado é o ativo da relação ao longo do tempo.
- **Português brasileiro**.
- Se o transcript estiver vazio, corrompido ou for de outra call (não check-in), pare e avise o account.

## Princípio central

Esta skill existe pra transformar **call que aconteceu** em **input pra próxima call ser melhor**. Sem ela, cada check-in é isolado e o account repete os mesmos erros. Com ela, o time tem memória e cada call constrói sobre a anterior.

Se o output não dá pra alguém preparar a próxima call melhor, **a skill falhou**. Os 3 ataques + diagnóstico ROPRE são os ativos centrais — não pulem.

## Conexão com outras skills

- **[[contexto]]** — pré-requisito, cria mission-control inicial. Se não existir, recomende rodar antes.
- **[[account-checkin-roleplay]]** — consome a saída desta skill (os 3 ataques alimentam o roleplay da próxima call).
- **[[v4mos-dados-meta-ads]]** — opcional pra cruzar números do transcript com dados frescos da plataforma.
