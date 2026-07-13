---
name: geral-memoria-pgvector
description: Sistema de memoria persistente por similaridade semantica com pgvector + Supabase. Inclui CLI completa (`scripts/memory-cli.py`) com store, search (vector + FTS hibrido), delete, list, consolidate (fusao de memorias similares), export/import, inject-context (formata contexto pra LLM), stats e cleanup (TTL). Usa OpenAI embeddings (text-embedding-3-small, 1536d) com connection pooling via REST, checksum dedup, importance scoring, access tracking e consolidacao automatica. Use quando o usuario falar em "memoria", "lembrar", "nao esquecer", "salva esse contexto", "busca o que ja foi dito sobre", "historico de sessoes", "memoria persistente", "pgvector", "busca semantica", "quero que o agente tenha memoria entre sessoes", "injetar contexto", ou "contexto da sessao passada". Tambem acione ao perceber informacao repetida que deveria estar persistida.
aliases: [memoria-pgvector, memory-pgvector]
tags: [skill, geral]
---

# Memoria por Similaridade com pgvector + Supabase

Sistema completo de memoria persistente para agentes usando **pgvector** no **Supabase** com embeddings **OpenAI** (`text-embedding-3-small`, 1536 dimensoes). Inclui CLI em `scripts/memory-cli.py` com todos os comandos de operacao.

Usa **LiteLLM** como provider de embedding (configurável via `EMBEDDING_BASE_URL`) — você define o modelo e gerencia consumo por lá. Compatível com OpenAI, Ollama, Anthropic, e qualquer provider que o LiteLLM suporta.

Diferente de memoria de conversa (buffer window), este sistema guarda informacao **pelo significado** — busque "o que discutimos sobre precos" e encontre o contexto mesmo com palavras diferentes.

## Arquitetura

```
┌─────────────────────────────────────────────────────┐
│  Agente / Terminal                                  │
│  $ python memory-cli.py store "texto" --type fact   │
│  $ python memory-cli.py search "query" --threshold 0.7│
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  memory-cli.py                                       │
│  ├─ generate_embedding() → LiteLLM (qualquer modelo)│
│  ├─ SupabaseClient() → REST + RPC com retry/backoff  │
│  ├─ cmd_consolidate() → funde memorias similares     │
│  └─ cmd_inject_context() → formata bloco pra LLM    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  LiteLLM Proxy                                       │
│  (OpenAI, Ollama, Claude, qualquer provider)         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Supabase (opencode-memoria)                        │
│  ├─ agent_memories (tabela com vector(N))           │
│  ├─ match_agent_memories() → busca hibrida (vec+FTS)│
│  ├─ consolidate_similar_memories() → fusao por sim  │
│  └─ cleanup_expired_memories() → TTL + lixo         │
└─────────────────────────────────────────────────────┘
```

## Setup Rapido

### 1. SQL no Supabase

Cole o conteudo de `references/supabase-migration.sql` no SQL Editor do Supabase (`bkenzsvexfayjcrqnmpx`). Isso cria:

- Tabela `agent_memories` com `vector(1536)`, `checksum` (dedup), `ttl` (expiracao), `consolidated` e `consolidated_from`
- Indice HNSW (`m=16, ef_construction=200`) para busca em ~1M registros
- Indice GIN para full-text search em portugues (fallback quando nao ha embedding)
- Funcao `match_agent_memories()` com filtros por tipo, sessao, importancia + hybrid search
- Funcao `search_memories_fts()` para busca textual pura
- Funcao `consolidate_similar_memories()` que funde memorias com similaridade > 85%
- Funcao `cleanup_expired_memories()` que expurga TTL vencido + consolidados velhos
- Trigger `update_updated_at`

```bash
# Para ver o SQL sem abrir o arquivo:
python scripts/memory-cli.py migrate-sql --print-only
```

### 2. Credenciais

```bash
export SUPABASE_URL=https://bkenzsvexfayjcrqnmpx.supabase.co
export SUPABASE_SERVICE_KEY=<service_role_key>
export EMBEDDING_API_KEY=<sua_chave_litellm>
export EMBEDDING_BASE_URL=http://localhost:4000/v1

# Opcionais:
export EMBEDDING_MODEL=text-embedding-3-small
export EMBEDDING_DIMS=1536
export MEMORY_AGENT_ID=opencode
export MEMORY_THRESHOLD=0.7
export MEMORY_LIMIT=5
```

Ou crie um `.env` na raiz do projeto com essas variaveis.

### 3. Dependencias

```bash
pip install httpx python-dotenv
```

## CLI — Comandos

### `store` — Armazenar memoria

```bash
# Armazenar um fato importante
python scripts/memory-cli.py store \
  "Decidimos usar pgvector em vez de Pinecone porque ja temos Supabase." \
  --type decision --importance 4 \
  --metadata '{"context":"infra-escolha","date":"2026-07-07"}'

# Com TTL de 7 dias (contexto temporario)
python scripts/memory-cli.py store \
  "Reuniao de alinhamento quinta 14h" \
  --type context --importance 2 --ttl-days 7

# Vinculado a uma sessao
python scripts/memory-cli.py store \
  "Cliente pediu priorizar canal do WhatsApp" \
  --type fact --importance 5 --session-id "ses_abc123"
```

O CLI faz **dedup por checksum** automaticamente — se o mesmo texto exato ja existir, nao duplica.

### `search` — Busca semantica (vector)

```bash
# Busca basica
python scripts/memory-cli.py search "qual banco vetorial escolhemos?" --limit 3

# Com threshold mais baixo (resultados menos similares)
python scripts/memory-cli.py search "decisoes de infra" --threshold 0.5

# Filtrando por tipo
python scripts/memory-cli.py search "oque o cliente pediu" --type fact

# Output JSON para processamento
python scripts/memory-cli.py search "preferencias do usuario" --json
```

### `search` com `--fts` — Full-text search (fallback)

```bash
# Busca textual exata (nao usa embedding — util quando a query e muito especifica)
python scripts/memory-cli.py search "WhatsApp" --fts
python scripts/memory-cli.py search "ADPLAN SDR" --fts --type fact
```

### `inject-context` — Contexto formatado pra LLM

```bash
# Busca e ja formata como bloco de contexto para injetar no prompt
python scripts/memory-cli.py inject-context "oque estamos fazendo com SDR IA" \
  --limit 5 --threshold 0.6
```

Output pronto pra colar em qualquer prompt de LLM:
```
## Contexto Recuperado da Memoria (pgvector)

### 1. [fact] importancia=5 similaridade=0.82 (2026-07-07)
ADPLAN: SDR IA com JS timeout corrigido, pendente push no n8n.

### 2. [decision] importancia=4 similaridade=0.78 (2026-06-22)
Decidimos usar pgvector em vez de Pinecone porque ja temos Supabase.
```

### `list` — Listar memorias

```bash
python scripts/memory-cli.py list                          # todas
python scripts/memory-cli.py list --type decision          # so decisoes
python scripts/memory-cli.py list --limit 50               # mais resultados
python scripts/memory-cli.py list --json                   # pra processar
```

### `consolidate` — Fundir memorias similares

```bash
# Dry-run: mostra o que seria fundido sem modificar
python scripts/memory-cli.py consolidate --dry-run

# Executa consolidacao: funde memorias com >85% similaridade
python scripts/memory-cli.py consolidate

# Com threshold customizado
python scripts/memory-cli.py consolidate --threshold 0.9
```

A consolidacao funde ate 10 memorias similares em uma so, marcando as originais como consolidadas. A nova memoria ganha importancia +1.

### `stats` — Dashboard

```bash
python scripts/memory-cli.py stats
```

Output:
```
==================================================
  Estatisticas da Memoria (agent=opencode)
==================================================
  Total: 47
  fact          : 18 ██████████████████
  decision      : 12 ████████████
  context       : 10 ██████████
  learned       :  5 █████
  general       :  2 ██
```

### `export` / `import` — Backup / restore

```bash
python scripts/memory-cli.py export backup-2026-07-07.json
python scripts/memory-cli.py import backup-2026-07-07.json
```

### `delete` / `cleanup`

```bash
python scripts/memory-cli.py delete <uuid>
python scripts/memory-cli.py cleanup   # expurga TTL vencido + consolidados >90 dias
```

## Tipos de Memoria

| Tipo | Uso | Importancia | TTL sugestao |
|---|---|---|---|
| `fact` | Fatos objetivos sobre cliente/projeto | 4-5 | eterno |
| `decision` | Decisoes e justificativas | 3-4 | eterno |
| `learned` | Aprendizados (o que funcionou ou nao) | 3-5 | eterno |
| `context` | Contexto de sessao reutilizavel | 2-3 | 30 dias |
| `preference` | Preferencias do usuario | 3-4 | eterno |
| `session_summary` | Resumo automatico de sessao | 2-3 | 60 dias |
| `general` | Qualquer outra coisa | 1-2 | 7 dias |

## Estrategia de Uso

### O que salvar
- Decisoes e o raciocinio por tras ("escolhemos X porque Y")
- Fatos sobre clientes: prazos, combinados, metricas, contatos
- Preferencias explicitas do usuario
- Aprendizados de sessoes anteriores ("tentamos X, nao funcionou porque Y")
- Resumos de sessoes longas (rode no final da sessao)

### O que NAO salvar
- Conversa banal ("bom dia", "obrigado")
- Informacao que ja existe em arquivos (CLAUDE.md, AGENTS.md)
- Dados sensiveis (senhas, tokens) — NUNCA
- Contexto que so vale para a sessao atual

### Pipeline recomendado

```
1. Durante a sessao: store() em momentos-chave (decisoes, fatos)
2. No fim da sessao: inject-context() para revisar, store() um resumo
3. Semanalmente: consolidate() para fundir similares
4. Mensalmente: cleanup() para expurgar expirados
5. Ao comecar sessao: inject-context() com o tema do trabalho
```

## Integracao com o Ecossistema V4

### `geral-log-sessoes`
Log salva JSONs de sessoes em disco. Esta skill e complementar: log preserva a conversa exata; pgvector permite buscar "o que foi dito sobre X" em qualquer sessao.

### `contexto` (Mission Control)
Gera contexto estatico (CLAUDE.md, AGENTS.md). Use pgvector para memoria **dinamica** — o que muda entre sessoes.

### `geral-leitura-contexto`
Le contexto do diretorio atual. Use `inject-context` do pgvector para complementar com memorias de sessoes anteriores.

### `n8n-architect`
Workflows SDR no n8n usam o mesmo `vectorStoreSupabase` com OpenAI key `0gfrMoNokOXtnvLg`. A tabela `agent_memories` e separada de `documents`.

## Troubleshooting

| Problema | Causa | Solucao |
|---|---|---|
| Nenhum resultado | Threshold alto | Baixe para 0.5 |
| Resultados ruins | Embedding mismatch | Sempre `text-embedding-3-small` nos dois lados |
| Timeout | Rede | O CLI ja faz retry com backoff (3x) |
| 401 Supabase | Service key errada | Verifique `SUPABASE_SERVICE_KEY` |
| Dedup falso positivo | Raro em texto grande | O `checksum` e SHA256 do content exato |
| Consolidacao lenta | Muitas memorias | Rode `consolidate --dry-run` primeiro |

## Referencia

- `scripts/memory-cli.py` — CLI completa (430 linhas)
- `references/supabase-migration.sql` — Migration SQL com tudo (tabela, indices, funcoes, triggers)
