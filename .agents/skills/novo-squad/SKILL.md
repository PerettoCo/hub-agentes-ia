---
name: novo-squad
description: Cria uma nova pasta de squad em squads/ com entry point e estrutura padrao. Pergunta nome do squad e quem e quem. Use quando o usuario rodar /novo-squad ou disser que quer criar um squad novo.
aliases: [novo-squad]
tags: [skill, area-base]
---
Voce vai criar a pasta de um novo squad com a estrutura padrao, um entry point com os membros e CLAUDE.md/AGENTS.md iniciais.

## Contexto

Squads sao times fixos de pessoas (gestor, account, trafego, criativo, CS, etc.) que atendem varios clientes. Um cliente pertence a um squad so. **Padrao obrigatorio:** `squads/{squad}/clientes/{cliente}/`. A estrutura final do squad e:

```
squads/{squad}/
├── CLAUDE.md          ← contexto do squad
├── AGENTS.md          ← espelho do contexto para outros agentes
├── {squad}.md         ← entry point com membros
├── docs/              ← docs gerais do squad
└── clientes/          ← clientes do squad (criados via /novo-cliente)
```

## Processo

### Passo 1 — Nome do squad

Pergunte:
> "Qual o nome do squad?"

Guarde duas versoes do nome:
- **Nome digitado** (com capitalizacao original): ex: "Squad Performance"
- **Nome formatado** pra pasta: lowercase + hifens, ex: "squad-performance"

### Passo 2 — Criar a estrutura

```bash
cp -r bases/_template/_template-squad "squads/[nome-formatado]"
```

Substitua `{NOME}` no `CLAUDE.md` e `AGENTS.md` da nova pasta pelo **nome digitado** (com capitalizacao preservada — nao pela versao em hifens).

### Passo 3 — Coletar membros

Em loop, pergunte:
> "Adiciona um membro do squad: nome + funcao (ex: 'Joao Silva — Gestor de Trafego'). Aperta Enter sem digitar nada quando terminar."

A cada resposta nao-vazia, guarde a entrada na lista de membros.
Quando o usuario apertar Enter sem digitar nada, encerra o loop.

Se a lista ficar vazia (usuario pulou tudo), crie o entry point sem membros.

### Passo 4 — Criar entry point do grafo

Crie `squads/[nome-formatado]/[nome-formatado].md` (entry point para o grafo do Obsidian — nome visivel ao inves de "README"):

```markdown
---
aliases: ["[Nome digitado]"]
tags: [squad]
---
# [Nome digitado]

## Membros
[lista de membros ou "- (a preencher)"]

## Clientes
(Lista criada por `/novo-cliente`)
```

Substitua `[lista de membros ou "- (a preencher)"]` pelos bullets coletados no passo 3, ou deixe `- (a preencher)` se vazio.

### Passo 5 — Confirmar

Mostre a estrutura criada:
```
squads/[nome-formatado]/
├── [nome-formatado].md  ← entry point do grafo Obsidian
├── CLAUDE.md
├── AGENTS.md
├── docs/
└── clientes/          ← vazio, pronto pra receber clientes
```

Diga:
> "Squad criado. Roda `/novo-cliente` pra adicionar um cliente neste squad."

## Regras

- Nome formatado da pasta e SEMPRE lowercase + hifens. Sem espacos, sem acentos.
- Se ja existir uma pasta com o nome formatado, avise o usuario e pergunte se quer escolher outro nome.
- Squad e gitignored por padrao (so os templates `_template-*` sobem pro repo).
- Membros tem formato livre — aceite qualquer string que o usuario digitar.
