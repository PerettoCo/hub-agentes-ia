---
name: account-evolucao-checkins
description: Relatorio de evolucao entre check-ins. Le o historico de check-ins, combinados e apostas do Mission Control e gera um relatorio de progressao — quais combinados foram cumpridos, quais apostas morreram/nasceram, como as personas evoluíram, e o ritmo de resolucao de combinados ao longo do tempo.
area: account
author: guilhermelippert
version: 1.0.0
aliases: [account-evolucao-checkins]
tags: [skill, area-account]
---
# Account — Evolucao entre Check-ins

Skill que responde: **"Estamos melhorando entre as calls?"**

Le o historico completo de check-ins de um cliente e gera um relatorio de evolucao ao longo do tempo. Nao e sobre uma call isolada — e sobre a **trajetoria** da relacao.

Criada a partir da visao de **Guilherme Lippert** de que cada check-in deve construir sobre o anterior, e que o valor real esta na serie historica, nao no ponto isolado.

## Arvore de Decisao

```
USUARIO PEDE EVOLUCAO DE CHECK-INS
│
├─ Qual cliente?
│  └─ Localiza em squads/{squad}/clientes/{cliente}/mission-control/
│
├─ O que analisar?
│  ├─ Combinados → taxa de cumprimento, tempo medio de resolucao, top devedores
│  ├─ Apostas → quantas viveram/morreram/nasceram, aprendizado acumulado
│  ├─ Personas → como os stakeholders mudaram, novos gatilhos
│  ├─ ROPRE → qualidade das calls ao longo do tempo (forte/medio/fraco)
│  └─ Todas (recomendado)
│
├─ Qual periodo?
│  ├─ Ultimo mes
│  ├─ Ultimo quarter
│  └─ Todo historico
│
└─ Formato de saida
   ├─ Relatorio em markdown (pra KB do cliente)
   ├─ HTML visual (pra apresentar ao time)
   └─ JSON (pra alimentar outros sistemas)
```

## O que produz

1. **Taxa de cumprimento de combinados** — % feitos vs pendentes, tempo medio pra resolver
2. **Ciclo de vida das apostas** — quantas nasceram, viveram, morreram no periodo; aprendizado acumulado
3. **Evolucao de personas** — novos gatilhos detectados, mudanca de comportamento dos stakeholders
4. **Qualidade ROPRE** — grafico de evolucao dos diagnosticos ao longo das calls (forte/medio/fraco)
5. **Ritmo de check-ins** — frequencia real vs esperada, gaps entre calls
6. **Score de saude da relacao** — metricas compostas que indicam se a relacao esta saudavel ou deteriorando

## Pre-requisitos

- Mission Control do cliente existente em `squads/{squad}/clientes/{cliente}/mission-control/`
- `historico-checkins.md` com pelo menos 2 entradas (para ter comparacao)
- Ideal: `apostas-vivas.md`, `combinados.md`, `personas-call.md` preenchidos
- Opcional: `checkins/` com os arquivos de review (para diagnostico ROPRE detalhado)

Se o historico tiver menos de 2 entradas, a skill avisa: "Historico insuficiente — preciso de pelo menos 2 check-ins para comparar."

## Quando triggerar

- "Como esta evoluindo o relacionamento com {cliente}?"
- "Relatorio de evolucao dos check-ins do {cliente}"
- "Estamos melhorando entre as calls?"
- "Quero ver a taxa de cumprimento de combinados do {cliente}"
- "Faz um retrospecto dos check-ins desse quarter"
- "Quais apostas viveram e morreram nos ultimos meses?"

## Fluxo

### Passo 1 — Identificar cliente e localizar Mission Control

Pergunte qual cliente se o usuario nao disser. Localize em `squads/{squad}/clientes/{cliente}/mission-control/`.

### Passo 2 — Ler todo o historico

Leia **todos** os arquivos do Mission Control. Nao so o `historico-checkins.md`:
- `combinados.md` — veja o que estava pendente, o que foi feito, em que ordem
- `apostas-vivas.md` — veja a secao de historico no final, alem das apostas atuais
- `personas-call.md` — veja as entradas com data, nao so o estado atual
- `historico-checkins.md` — o registro cronologico das calls

Se existirem arquivos de review em `checkins/`, leia-os para extrair diagnostico ROPRE.

### Passo 3 — Calcular metricas de evolucao

**A. Combinados**
- Total de combinados no periodo
- Quantos viram "Feitos" (cumprimento)
- Quantos continuam "Pendentes" (arrastados)
- Tempo medio entre "criado" e "feito" (se houver datas)
- Quem tem mais combinados pendentes (cliente vs time V4)
- Combinados que nunca sairam do lugar (arrastados por 2+ check-ins)

**B. Apostas**
- Quantas estavam vivas no inicio do periodo
- Quantas foram confirmadas
- Quantas morreram (com aprendizado)
- Quantas nasceram
- Qual o aprendizado acumulado (extraia das apostas mortas)

**C. Personas**
- Novos stakeholders identificados
- Novos padroes de provocacao registrados
- Mudanca de tom/atitude (ex: "passivo virou agressivo")
- Frases marcantes registradas

**D. Qualidade ROPRE (se disponivel)**
- Para cada review em `checkins/`, extraia a classificacao de cada bloco
- Monte uma serie temporal: call 1 → call 2 → call N
- Identifique padroes: "bloco R sempre cai", "combinados melhoraram"

### Passo 4 — Calcular Score de Saude

Com base nos dados acima, calcule:

| Componente | Peso | Formula |
|---|---|---|
| Cumprimento de combinados | 30% | % de combinados feitos no periodo |
| Vitalidade das apostas | 25% | apostas novas + confirmadas / total |
| Qualidade ROPRE media | 25% | media das notas (Forte=3, Medio=2, Fraco=1, Ausente=0) |
| Ritmo de check-ins | 20% | frequencia real / frequencia esperada (1x mes = ideal) |

**Score:**
- 80-100: Relacao saudavel
- 60-79: Atencao — monitorar
- < 60: Critico — intervencao necessaria

### Passo 5 — Identificar padroes e alertas

- **Combinado cronico**: mesma task aparece como pendente em 3+ check-ins seguidos
- **Aposta que nunca morre**: aposta viva ha mais de 2 quarters sem confirmacao
- **Persona silenciada**: stakeholder que aparecia e parou de aparecer nas calls
- **ROPRE em declinio**: qualidade caindo nas ultimas 3 calls

### Passo 6 — Montar relatorio

```markdown
# Evolucao de Check-ins — {Cliente}

**Periodo:** {inicio} a {fim} | **Check-ins no periodo:** {N} | **Score de Saude:** {X}/100 ({status})

## Resumo Executivo
{3-5 bullets com o essencial}

## 1. Combinados
| Metrica | Valor |
|---|---|
| Total de combinados | {N} |
| Cumpridos | {N} ({X}%) |
| Pendentes | {N} |
| Tempo medio de resolucao | {X} dias |
| Top arrastados | {lista} |

## 2. Apostas
| Metrica | Valor |
|---|---|
| Vivas no inicio | {N} |
| Confirmadas no periodo | {N} |
| Mortas no periodo | {N} |
| Novas | {N} |
| Aprendizado acumulado | {extracao} |

## 3. Personas
{Mudancas detectadas em cada stakeholder}

## 4. Qualidade ROPRE (serie)
| Data | Onde Paramos | R | O | P+R | E | Combinados |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

**Padrao identificado:** {ex: "bloco R sempre cai em modo SEM"}

## 5. Alertas
- ? {alerta 1}
- ? {alerta 2}

## Recomendacao
{proxima acao — ex: "aumentar frequencia de check-ins para quinzenal",
"cliente precisa de call extraordinaria sobre aposta X", "persona Y
precisa ser envolvida de novo"}
```

Salve o relatorio em `checkins/evolucao-{YYYY-MM-DD}.md`.

## Regras

- **Nunca invente dados** — se nao tem info, marque como "sem dados"
- **Preserve o historico** — append-only em tudo
- **Nao confunda ausencia de registro com ausencia de problema** — se nao tem review registrado, a call nao gerou aprendizado
- **Score de saude e termometro, nao diagnostico** — sempre contextualize com o que esta acontecendo no cliente
- **Portugues brasileiro**

## Conexao com outras skills

- **[[contexto]]** — pre-requisito, cria/atualiza Mission Control
- **[[account-checkin-review]]** — alimenta o historico que esta skill consome
- **[[account-checkin-roleplay]]** — os padroes identificados viram input pro roleplay
- **[[gt-relatorios-trafego]]** — dados de trafego contextualizam a evolucao (ex: "combinados caindo enquanto ROAS sobe — atencao")
