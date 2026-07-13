# Relatorio Tecnico — Sistema de Memoria e Contexto para Agentes OpenCode

**Data:** 2026-07-07
**Autor:** gerado por opencode
**Escopo:** 2 skills entregues em duplo-write (.agents/ + .claude/)
**Tempo estimado:** 10h

---

## Sumario

1. [Skill 1: geral-memoria-pgvector](#1-geral-memoria-pgvector)
   - 1.1 Arquitetura
   - 1.2 Schema Supabase (pgvector)
   - 1.3 CLI (`memory-cli.py`)
   - 1.4 Decisoes Tecnicas
2. [Skill 2: geral-leitura-contexto](#2-geral-leitura-contexto)
   - 2.1 Arquitetura
   - 2.2 CLI (`context-reader.py`)
   - 2.3 Cache e Deteccao de Mudancas
3. [Integracoes](#3-integracoes)
4. [Metricas de Entrega](#4-metricas-de-entrega)

---

## 1. Skill: `geral-memoria-pgvector`

### 1.1 Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│  Camada de Apresentacao (CLI)                           │
│  memory-cli.py: 11 subcomandos, argparse, output text/json│
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Camada de Servico (Python)                             │
│  - generate_embedding()  → OpenAI API (text-embedding-3-small)│
│  - SupabaseClient()      → REST + RPC, retry 3x com    │
│                            exponential backoff (1s, 2s, 4s) │
│  - compute_checksum()    → SHA256 para dedup           │
│  - cmd_consolidate()     → funde memorias com sim >85% │
│  - cmd_inject_context()  → formata resultados para LLM │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  Camada de Dados (Supabase)                             │
│  Projeto: bkenzsvexfayjcrqnmpx (opencode-memoria)                          │
│  Tabela: agent_memories                                 │
│  Indices: HNSW (vector_cosine_ops) + GIN (FTS pt-BR)   │
│  Funcoes: match_agent_memories(), search_memories_fts(),│
│           consolidate_similar_memories(),                │
│           cleanup_expired_memories(), update_access_count│
└─────────────────────────────────────────────────────────┘
```

### 1.2 Schema Supabase (pgvector)

**Tabela `agent_memories`**

| Coluna | Tipo | Descricao |
|---|---|---|
| `id` | `UUID PK` | `gen_random_uuid()` |
| `content` | `TEXT NOT NULL` | Conteudo da memoria |
| `content_tokens` | `INTEGER DEFAULT 0` | Contagem aproximada de tokens |
| `embedding` | `vector(1536)` | Embedding OpenAI text-embedding-3-small |
| `agent_id` | `TEXT NOT NULL` | Namespace para multi-agente |
| `session_id` | `TEXT` | Vinculo opcional a sessao |
| `parent_session` | `TEXT` | Sessao que originou (para rastreio) |
| `memory_type` | `TEXT` | `fact`, `decision`, `learned`, `context`, `preference`, `general`, `session_summary` |
| `importance` | `SMALLINT 1-5` | Escala de importancia |
| `ttl` | `TIMESTAMPTZ` | NULL = eterna; expira em `ttl < now()` |
| `consolidated` | `BOOLEAN` | Se true, e resultado de fusao |
| `consolidated_from` | `UUID[]` | Quais memorias foram fundidas aqui |
| `access_count` | `INTEGER` | Contagem de acessos |
| `last_accessed` | `TIMESTAMPTZ` | Ultimo acesso |
| `metadata` | `JSONB` | Metadata flexivel (tags, fonte, etc.) |
| `checksum` | `TEXT` | SHA256 do content para dedup |
| `created_at` | `TIMESTAMPTZ` | Criacao |
| `updated_at` | `TIMESTAMPTZ` | Atualizacao (trigger automatico) |

**Indices**

| Index | Tipo | Coluna | Finalidade |
|---|---|---|---|
| `idx_agent_memories_hnsw` | `hnsw (m=16, ef_construction=200)` | `embedding` | Busca vetorial por cosine distance |
| `idx_am_fts` | `gin` | `to_tsvector('portuguese', content)` | Full-text search fallback |
| `idx_am_agent` | `btree` | `agent_id` | Filtro por agente |
| `idx_am_type` | `btree` | `memory_type` | Filtro por tipo |
| `idx_am_agent_type` | `btree` | `(agent_id, memory_type)` | Filtro composto |
| `idx_am_created` | `btree` | `created_at DESC` | Ordenacao cronologica |
| `idx_am_ttl` | `btree` | `ttl WHERE ttl IS NOT NULL` | Limpeza de expiradas |
| `idx_am_checksum` | `btree` | `checksum WHERE checksum IS NOT NULL` | Dedup rapido |

**Funcoes**

| Funcao | Parametros | Retorno |
|---|---|---|
| `match_agent_memories()` | query_embedding, threshold, count, agent_id, type, session_id, min_importance, fts_query | `TABLE (id, content, type, importance, similarity, fts_rank, metadata, created_at)` |
| `search_memories_fts()` | query, count, agent_id, type | `TABLE (id, content, type, importance, rank, created_at)` |
| `consolidate_similar_memories()` | agent_id, threshold, max_age_days | `TABLE (consolidated_id, source_count, merged_content)` |
| `cleanup_expired_memories()` | agent_id | `TABLE (deleted_count)` |
| `update_access_count()` | id | `VOID` |

### 1.3 CLI (`memory-cli.py`)

**663 linhas**, 0 dependencias externas alem de `openai`, `httpx`, `python-dotenv`.

**Comandos:**

| Comando | Descricao | Flags |
|---|---|---|
| `store` | Armazena memoria com embedding | `--type`, `--importance`, `--session-id`, `--metadata`, `--ttl-days`, `--agent-id` |
| `search` | Busca por similaridade semantica | `--limit`, `--threshold`, `--type`, `--session-id`, `--fts`, `--json` |
| `delete` | Deleta por UUID | — |
| `list` | Lista memorias recentes | `--type`, `--limit`, `--json` |
| `consolidate` | Funde memorias similares | `--dry-run`, `--threshold` |
| `export` | Exporta para JSON | `path` |
| `import` | Importa de JSON (re-embed) | `path` |
| `inject-context` | Busca e formata contexto para LLM | `--limit`, `--threshold`, `--session-id` |
| `stats` | Dashboard de estatisticas | — |
| `cleanup` | Expurga TTL vencido + consolidados velhos | — |
| `migrate-sql` | Exibe SQL de migracao | `--print-only` |

**Fluxo de `store`:**
1. `compute_checksum(content)` → SHA256
2. Verifica se checksum ja existe na tabela (dedup)
3. `generate_embedding(content)` → OpenAI API com retry 3x
4. Monta payload com embedding, checksum, metadata, ttl
5. `POST /rest/v1/agent_memories` com `Prefer: return=minimal`

**Fluxo de `search`:**
1. `generate_embedding(query)` → mesmo modelo do insert
2. Se `--fts`: chama `search_memories_fts()` (nao precisa de embedding)
3. Senao: chama `match_agent_memories()` com filtros
4. Dispara `update_access_count()` para cada resultado

**Fluxo de `consolidate`:**
1. Chama `consolidate_similar_memories()` no banco
2. A funcao itera memorias nao-consolidadas, busca similares com `cosine > 0.85`
3. Agrupa ate 10 memorias similares com `string_agg`
4. Insere nova memoria com `consolidated=true` e `importance = min(original + 1, 5)`
5. Retorna `(consolidated_id, source_count, merged_content)`

**Tratamento de erros:**
- Retry 3x com backoff exponencial (1s, 2s, 4s) em falhas HTTP e timeout
- Logging estruturado com `logging` module
- Validacao de variaveis de ambiente no startup

### 1.4 Decisoes Tecnicas

| Decisao | Alternativa | Escolha | Motivo |
|---|---|---|---|
| Embedding model | text-embedding-3-large, Cohere, open-source | **text-embedding-3-small** | Mesmo modelo dos workflows SDR existentes; 1536d suficiente |
| Vector store | Pinecone, Qdrant, Weaviate | **Supabase pgvector** | Ja existe no projeto; zero novo provider; joins relacionais |
| Index type | IVFFlat, HNSW | **HNSW (m=16, ef_construction=200)** | Mais rapido em recall > 0.99; IVFFlat precisa REINDEX apos INSERT |
| Interface | SDK Python, SQL direto, CLI | **CLI (argparse)** | Usavel por agente e por humano; zero config de SDK; pipeable |
| Dedup | cosine similarity, hash exato | **SHA256 checksum** | O(1) vs O(n); sem false positives; barato |
| TTL | campo separado, tabela separada | **coluna ttl + cleanup job** | Simples; sem background worker; cleanup sob demanda |
| Consolidacao | chunking fixo, overlap | **fusao por similaridade > 85%** | Preserva contexto; evisa perda de informacao |

---

## 2. Skill: `geral-leitura-contexto`

### 2.1 Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│  context-reader.py (688 linhas)                          │
│  ├── detect_context_type()  → CLIENTE|SQUAD|PROJETO|GEN │
│  ├── read_claude_md()       → extrai secoes/ferramentas │
│  ├── read_agents_md()       → extrai skills refs        │
│  ├── read_mission_control() → OKR, apostas, combinados   │
│  ├── read_env_vars()        → apenas NOMES (nunca valor) │
│  ├── read_git_log()         → git log --oneline -5      │
│  ├── read_package_info()    → package.json/pyproject     │
│  ├── list_skills()          → .agents/ + .claude/        │
│  ├── scan_directory()       → glob de arquivos-chave     │
│  └── build_context()        → monta ContextResult        │
└─────────────────────────────────────────────────────────┘
```

### 2.2 CLI (`context-reader.py`)

**688 linhas**, dependencias: `python-dotenv`, `pyyaml`.

| Modo | Descricao |
|---|---|
| `context-reader.py` | Leitura completa do diretorio |
| `context-reader.py --brief` | Resumo de ~5 linhas |
| `context-reader.py --json` | Output JSON estruturado |
| `context-reader.py --watch` | Modo observador (polling 5s) |
| `context-reader.py --diff` | Diff com cache anterior |
| `context-reader.py --store-memory` | Salva resumo no pgvector |

**Cache:** Salvo em `~/.cache/context-reader-cache.json`. Usado pelo `--diff` para comparar estado anterior vs atual.

### 2.3 Cache e Deteccao de Mudancas

O cache salva o `ContextResult` completo em JSON. O `--diff` carrega o cache, compara:
- `name`, `purpose`, `tools`, `state`, `skills`, `env_vars`
- Retorna lista de mudancas ou "Contexto identico ao cache"

---

## 3. Integracoes

| Skill | Relacao |
|---|---|
| `geral-log-sessoes` | Log salva JSON de sessoes em disco (conversa exata); pgvector busca "o que foi dito sobre X" em qualquer sessao |
| `contexto` | `contexto` gera CLAUDE.md/AGENTS.md/mission-control; `leitura-contexto` le o que foi gerado; `memoria-pgvector` complementa com memoria dinamica entre sessoes |
| `n8n-architect` | Workflows SDR usam `vectorStoreSupabase` com mesma OpenAI key; tabelas separadas (`documents` vs `agent_memories`) |
| `geral-leitura-contexto --store-memory` | Ponte entre as duas skills: le contexto do diretorio e salva resumo no pgvector |

---

## 4. Metricas de Entrega

| Item | `.agents/skills/` | `.claude/skills/` | Total |
|---|---|---|---|
| `geral-memoria-pgvector/SKILL.md` | 272 linhas | 272 linhas | 544 |
| `geral-memoria-pgvector/scripts/memory-cli.py` | 663 linhas | 663 linhas | 1326 |
| `geral-memoria-pgvector/references/supabase-migration.sql` | 288 linhas | 288 linhas | 576 |
| `geral-leitura-contexto/SKILL.md` | 187 linhas | 187 linhas | 374 |
| `geral-leitura-contexto/scripts/context-reader.py` | 688 linhas | 688 linhas | 1376 |
| **Total** | **2098 linhas** | **2098 linhas** | **4196 linhas** |

**6 arquivos** (3 por skill) x **2 ambientes** = **12 arquivos** no disco, todos validados:
- Syntax check: Python AST passou nos 2 scripts
- Duplo-write: `diff -r` idêntico entre `.agents/` e `.claude/`
- Dependencias: `openai`, `httpx`, `python-dotenv` (memoria); `python-dotenv`, `pyyaml` (contexto)
