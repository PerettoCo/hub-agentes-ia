---
name: novo-projeto
description: Cria uma nova pasta de projeto com estrutura padrao em bases/. Use quando o usuario rodar /novo-projeto ou disser que quer adicionar um projeto novo, uma area de trabalho ou qualquer base que nao seja cliente.
aliases: [novo-projeto]
tags: [skill, area-base]
---
Voce vai criar a pasta de um novo projeto com a estrutura padrao.

## Processo

### Passo 1 — Nome do projeto

Pergunte:
> "Qual o nome do projeto ou area de trabalho?"

Use o nome para criar a pasta. Converta para lowercase-com-hifens (ex: "Conciliação Bancária" → "conciliacao-bancaria").

### Passo 2 — Criar a estrutura

```bash
cp -r bases/_template "bases/[nome-formatado]"
cp "bases/[nome-formatado]/.env.example" "bases/[nome-formatado]/.env"
```

`.env` fica local (bases/ inteiro e gitignored, so `_template/` sobe). Preenche credenciais conforme usar.

### Passo 3 — Criar entry point do grafo

Crie `bases/[nome-formatado]/[nome-formatado].md` (entry point para o grafo do Obsidian — nome visivel ao inves de "README"):

```markdown
---
aliases: ["[Nome do Projeto]"]
tags: [projeto]
---
# [Nome do Projeto]

[Descricao que o usuario der]

## Pastas
- `docs/` — Documentacao
- `dados/` — Dados e planilhas
- `referencias/` — Referencias e pesquisas
```

### Passo 4 — Contexto inicial

Pergunte:
> "Me conta em 1-2 frases o que e esse projeto. Pra que ele serve?"

Crie `bases/[nome-formatado]/CLAUDE.md`:
```markdown
# [Nome do Projeto]

## Resumo
[Descricao que o usuario deu]

## Contexto
Rode `/contexto` apos adicionar dados nesta pasta para gerar o contexto completo.
```

### Passo 5 — Confirmar

Mostre a estrutura criada:
```
bases/[nome-formatado]/
├── [nome-formatado].md  ← entry point do grafo Obsidian
├── CLAUDE.md
├── .env            # credenciais locais (gitignored)
├── .env.example    # template
├── docs/
├── dados/
└── referencias/
```

Diga:
> "Projeto criado. Jogue seus dados nas pastas (docs, dados, referencias) e rode `/contexto` quando tiver pronto."
