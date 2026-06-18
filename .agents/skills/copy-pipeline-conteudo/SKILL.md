---
name: copy-pipeline-conteudo
description: Pipeline completo de conteudo editorial — cria calendario, produz blog posts e email marketing via IA, envia para aprovacao no Google Drive e gera JSONs finais. Inclui fluxo de aprovacao com notificacao por email e publicacao automatica no Drive.
area: copy
author: v4team
version: 1.0.0
aliases: [copy-pipeline-conteudo]
tags: [skill, area-copy]
---
# Copy — Pipeline de Conteudo

Skill que gerencia o ciclo de vida completo de conteudo editorial: do calendario a publicacao. Inspirada nos workflows de producao de conteudo que ja rodam para clientes como Conversa e All Over.

## Arvore de Decisao

```
USUARIO QUER CONTEUDO
│
├─ Tem calendario editorial?
│  ├─ Nao → gerar calendario (--calendario)
│  │  ├─ Para quantas semanas? (default: 4)
│  │  ├─ Mix de formatos? (blog_post + email_marketing)
│  │  └─ Salvar no Drive? Sim/Nao
│  │
│  └─ Sim → qual item produzir?
│
├─ Produzir item
│  ├─ Blog post → Claude gera: titulo, meta, intro, secoes, CTA
│  ├─ Email marketing → Claude gera: subject lines, corpo, CTA, PS
│  └─ JSON salvo no Drive com status "para_aprovacao"
│
├─ Aprovacao
│  ├─ Colaborador recebe link do Drive
│  ├─ Abre, revisa, executa aprovacao
│  │  └─ Status muda para "aprovado"
│  └─ Notificacao automatica para o time
│
└─ Publicacao
   ├─ JSON final no Drive
   ├─ Pronto para consumir (site, email, API)
   └─ Historico mantido por mes
```

## O que produz

1. **Calendario Editorial** — JSON estruturado com N semanas de topicos, divididos entre blog posts e email marketing
2. **Blog Posts completos** — HTML/JSON com titulo, meta description, introducao, secoes, conclusao, CTA, tempo de leitura
3. **Email Marketing** — JSON com subject lines (3 opcoes), preheader, corpo, CTA, PS
4. **Fluxo de aprovacao** — conteudo salvo no Drive com status `para_aprovacao`, colaborador aprova mudando status para `aprovado`
5. **Arquivo no Drive** — estrutura por cliente/mes: `Conteudo V4/{cliente}/{YYYY-MM}/`
6. **Notificacao** — email automatico ao colaborador quando novo conteudo esta para aprovacao

## Pre-requisitos

- `v4-automations/config/.env` com ANTHROPIC_API_KEY
- `v4-automations/config/token.json` com OAuth Google (acesso ao Drive)
- Google Drive com permissao de escrita

## Quando triggerar

- "Precisamos de um calendario editorial para {cliente}"
- "Queremos blog posts para as proximas 4 semanas"
- "Cria uma sequencia de emails para a campanha de {cliente}"
- "Manda o proximo post do calendario para aprovacao"
- "Aprova o conteudo que esta no Drive"
- "Pipeline de conteudo para {cliente}"

## Fluxo

### Passo 1 — Calendario Editorial

```bash
python3 v4-automations/scripts/copy/pipeline_conteudo.py \
  --cliente "Cliente A" --calendario --semanas 4 --drive --email aprovador@email.com
```

O calendario e gerado por IA com topicos relevantes. Salvo no Drive em:
`Conteudo V4/{cliente}/Calendarios/calendario-editorial-{data}.json`

### Passo 2 — Escolher e Produzir

De posse do calendario, escolha o indice do item a produzir:

```bash
python3 v4-automations/scripts/copy/pipeline_conteudo.py \
  --cliente "Cliente A" --calendario --semanas 4 \
  --drive --drive-folder <ID> --email aprovador@email.com
```

Depois:
```bash
python3 v4-automations/scripts/copy/pipeline_conteudo.py \
  --cliente "Cliente A" --produzir 0 --drive --email aprovador@email.com
```

Isso gera o conteudo via Claude, salva o JSON no Drive com status `para_aprovacao`,
e envia notificacao por email com link direto.

### Passo 3 — Aprovacao

O colaborador recebe o email, clica no link do Drive, revisa o JSON.
Para aprovar:

```bash
python3 v4-automations/scripts/copy/pipeline_conteudo.py \
  --aprovar <fileId-do-Drive>
```

O status muda de `para_aprovacao` para `aprovado`.

### Passo 4 — JSON final no Drive

O JSON aprovado fica disponivel na estrutura:
```
Conteudo V4/{cliente}/{YYYY-MM}/
  blog-post-titulo-{data}.json
  email-marketing-titulo-{data}.json
```

### Formato dos JSONs

**Blog Post:**
```json
{
  "titulo": "Titulo do Post",
  "meta_description": "Descricao ate 160 caracteres",
  "introducao": "Texto introdutorio...",
  "secoes": [
    {"subtitulo": "...", "conteudo": "..."}
  ],
  "conclusao": "Texto final...",
  "cta": "Faca isso agora",
  "tempo_leitura": 5,
  "formato": "blog_post",
  "status": "aprovado",
  "aprovado_em": "2026-05-22"
}
```

**Email Marketing:**
```json
{
  "titulo": "Titulo do Email",
  "subject_lines": ["Linha 1", "Linha 2", "Linha 3"],
  "preheader": "Texto do preheader",
  "corpo": "Corpo do email...",
  "cta": {"texto": "Clique aqui", "hint": "/pagina-de-destino"},
  "ps": "Texto do PS",
  "formato": "email_marketing",
  "status": "aprovado",
  "aprovado_em": "2026-05-22"
}
```

## Regras

- **Blog posts:** minimo 800 palavras, CTA no final, meta description ate 160 caracteres
- **Email marketing:** 3 opcoes de subject line, preheader obrigatorio, CTA claro
- **Status tracking:** `rascunho` → `para_aprovacao` → `aprovado`
- **Drive sempre:** todo conteudo publicado tem uma copia JSON no Drive
- **Portugues brasileiro**
- Nao publique sem aprovacao

## Conexao com outras skills

- **[[copywriting]]** — escreve o texto final dos blog posts e emails
- **[[email-sequence]]** — consome os JSONs de email para montar sequencias
- **[[content-strategy]]** — alimenta o calendario com estrategia de topicos
- **[[geral-frontend-design]]** — transforma JSONs em HTML visual se precisar
- **[[analytics-tracking]]** — configura tracking para os conteudos publicados
