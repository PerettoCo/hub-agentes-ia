# Memória Semântica de Agentes (geral-memoria-agentes)

## 1. O Problema

Hoje, quando um agente OpenCode vai trabalhar em uma tarefa, ele começa do zero. Não importa se já fez algo muito parecido para o mesmo cliente ou nicho — a experiência anterior se perde entre sessões.

Isso significa que:
- O agente não aprende com acertos passados
- Estratégias que funcionaram são reinventadas a cada execução
- O histórico de "o que deu certo" fica na cabeça do humano, não na base compartilhada
- Cada agente opera isolado, sem memória coletiva

## 2. A Solução: pgvector como Cérebro Coletivo dos Agentes

A skill `geral-memoria-agentes` implementa uma base vetorial (pgvector no Supabase) que funciona como um cérebro coletivo: agentes consultam "o que já funcionou parecido com isso" e registram "o que acabei de fazer e deu certo".

O fluxo é simples:

```
         ┌─────────────────────────────────────────────────┐
         │            Supabase + pgvector                   │
         │  ┌───────────────────────────────────────────┐   │
         │  │  agent_memories                            │   │
         │  │  ┌─────┬──────────┬──────────┬──────────┐ │   │
         │  │  │ id  │embedding │ content  │ strategy │...│   │
         │  │  ├─────┼──────────┼──────────┼──────────┤ │   │
         │  │  │ u1  │ [0.02... │ "Audit..."│ "Crawler"│ │   │
         │  │  │ u2  │ [0.01... │ "Camp... │ "Meta..."│ │   │
         │  │  └─────┴──────────┴──────────┴──────────┘ │   │
         │  └───────────────────────────────────────────┘   │
         └─────────────────────────────────────────────────┘
                        ▲                     │
                        │ search              │ record
                        │ (antes)             │ (depois)
                        │                     ▼
               ┌─────────────────────────────────────┐
               │        Agente OpenCode               │
               │                                      │
               │  1. ANTES: busca memórias similares  │
               │  2. USA o contexto pra planejar      │
               │  3. FAZ o trabalho                   │
               │  4. DEPOIS: registra nova memória    │
               └─────────────────────────────────────┘
```

## 3. Como Funciona Tecnicamente

### 3.1 Storage — Supabase + pgvector

A tabela central chama-se `agent_memories` e fica no schema `public` do Supabase:

```sql
CREATE TABLE agent_memories (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  embedding     VECTOR(1536) NOT NULL,    -- ← o vetor que permite busca semântica
  content       TEXT NOT NULL,             -- descrição completa do trabalho
  summary       TEXT,                      -- título resumido
  client        TEXT,                      -- fips-nautica, atlas-copco, etc
  niche         TEXT,                      -- moda, saúde, construção, etc
  agent_role    TEXT,                      -- seo-visibilidade, sdr-tech, etc
  task_type     TEXT,                      -- seo-audit, copy, checkin, etc
  strategy      TEXT,                      -- QUAL A ESTRATÉGIA QUE FUNCIONOU
  result        TEXT,                      -- QUAL FOI O RESULTADO
  success_score INTEGER CHECK (1-10),      -- nota de sucesso
  tags          JSONB,                     -- ["seo","audit","ecommerce"]
  metadata      JSONB,                     -- {"paginas":47,"criticos":12}
  created_at    TIMESTAMPTZ DEFAULT now(),
  updated_at    TIMESTAMPTZ DEFAULT now()
);
```

Índice IVFFlat com distance cosine para busca em lote — cada query de similaridade escaneia ~100 listas (configurável) em vez de tabela inteira.

### 3.2 Embeddings — OpenAI text-embedding-3-small

Cada memória carrega um vetor de 1536 dimensões gerado pelo modelo `text-embedding-3-small` da OpenAI.

O embedding é gerado a partir da **concatenação** dos campos mais relevantes:

```
texto_para_embedding = summary + "\n" + content + "\n" +
                       "Cliente: " + client + "\n" +
                       "Nicho: " + niche + "\n" +
                       "Estratégia: " + strategy + "\n" +
                       "Resultado: " + result
```

Isso garante que a busca por similaridade capture tanto o contexto (cliente, nicho) quanto o conteúdo técnico (estratégia, resultado).

### 3.3 Busca — Função `match_agent_memories`

A função RPC (PostgreSQL) recebe um vetor de consulta e devolve as N memórias mais similares que passam do limiar:

```sql
SELECT ... FROM agent_memories
WHERE 1 - (embedding <=> query_embedding) > threshold
  AND (filtros opcionais: cliente, nicho, papel, tipo)
ORDER BY embedding <=> query_embedding
LIMIT match_count;
```

O operador `<=>` é o cosine distance do pgvector. A subtração `1 - distance` converte em similaridade (0 a 1).

Filtros opcionais por cliente, nicho, papel de agente e tipo de tarefa permitem refinar a busca.

### 3.4 Scripts Python

#### `search.py` — antes de trabalhar

```
1. Recebe: --query "descrição do trabalho" --client "X"
2. Chama OpenAI: gera embedding da query
3. Chama Supabase: POST /rest/v1/rpc/match_agent_memories
4. Retorna: JSON com as top-N memórias similares
5. Agente usa strategy + result de cada memória como contexto
```

#### `record.py` — depois de concluir

```
1. Recebe: --content, --summary, --client, --strategy, --result, etc
2. Concatena campos relevantes
3. Chama OpenAI: gera embedding
4. Chama Supabase: POST /rest/v1/agent_memories
5. Retorna: confirmação de sucesso
```

## 4. Como os Agentes Usam (Comportamento Automático)

A skill instrui o agente a **sempre** executar dois passos em toda tarefa:

### Passo 1: ANTES — Buscar memórias

Sempre que o agente recebe uma tarefa, ele monta o contexto atual e busca memórias similares:

```bash
python search.py \
  --query "auditoria SEO para e-commerce de moda masculina" \
  --client "fips-nautica" \
  --niche "moda" \
  --role "seo-visibilidade" \
  --task-type "seo-audit" \
  --threshold 0.7 \
  --limit 5
```

O retorno é JSON com as memórias mais similares. Cada memória contém:
- `content`: descrição completa do que foi feito antes
- `strategy`: a estratégia usada (reaproveitável)
- `result`: o resultado obtido
- `success_score`: nota do quão bem funcionou
- `similarity`: grau de similaridade (0-1)

O agente incorpora essas memórias como contexto no planejamento.

### Passo 2: DEPOIS — Registrar aprendizado

Após concluir, o agente registra o que fez:

```bash
python record.py \
  --summary "SEO audit — e-commerce moda masculina" \
  --content "Auditoria completa de 47 páginas..." \
  --client "fips-nautica" \
  --niche "moda" \
  --agent-role "seo-visibilidade" \
  --task-type "seo-audit" \
  --strategy "Crawler Screaming Frog + Google Rich Results Test + revisão manual" \
  --result "47 páginas auditadas, 12 críticos encontrados" \
  --success-score 8 \
  --tags '["seo","audit","ecommerce"]'
```

## 5. Setup no Supabase

### 5.1 O que precisa ser feito

1. Habilitar a extensão pgvector no projeto Supabase
2. Criar a tabela `agent_memories`
3. Criar índices e a função `match_agent_memories`
4. Configurar RLS e grants para a Data API

### 5.2 Como fazer

**Opção A — Manual (recomendado na primeira vez):**
1. Acessar o SQL Editor do Supabase Dashboard
   - URL: `https://supabase.com/dashboard/project/gswzuzetverulcgzhynb/sql/new`
2. Copiar e colar o conteúdo de:
   - `.agents/skills/geral-memoria-agentes/scripts/setup/supabase-schema.sql`
3. Executar

**Opção B — Automatizado via Management API:**
```bash
export SUPABASE_URL="https://gswzuzetverulcgzhynb.supabase.co"
export SUPABASE_SERVICE_KEY="<service_role_key>"
export SUPABASE_PAT="<personal_access_token_da_supabase>"
python .agents/skills/geral-memoria-agentes/scripts/setup.py
```

### 5.3 Pré-requisitos

| Recurso | Onde obter |
|---|---|
| Service Role Key | Dashboard → Project Settings → API → service_role key |
| Personal Access Token (opcional) | Dashboard → Account → Access Tokens |
| OpenAI API Key | platform.openai.com/api-keys |

## 6. Variáveis de Ambiente

O agente precisa destas variáveis configuradas no ambiente OpenCode:

```bash
export SUPABASE_URL="https://gswzuzetverulcgzhynb.supabase.co"
export SUPABASE_SERVICE_KEY="<service_role_key>"
export OPENAI_API_KEY="<sua_chave>"
```

## 7. Exemplo End-to-End

### Cenário: Agente SEO vai auditar um novo cliente

```
QUERY DO USUÁRIO:
"Faz uma auditoria SEO para o site da fips-nautica, e-commerce de moda naval"

AGENTE ATIVA A SKILL:

[ANTES - busca memória]
$ python search.py \
  --query "auditoria SEO e-commerce moda naval fips-nautica" \
  --client "fips-nautica" \
  --niche "moda-naval" \
  --role "seo-visibilidade" \
  --task-type "seo-audit" \
  --limit 5

→ RETORNA 2 MEMÓRIAS:
  #1 (similaridade 0.92): Auditoria fips-nautica de 3 meses atrás
     - Estratégia: Screaming Frog + GSC + SEMrush
     - Achados principais: meta descriptions duplicadas, falta schema Product
     - Resultado: 47 páginas auditadas, 12 críticos, 8 melhorias implementadas
     
  #2 (similaridade 0.78): Auditoria para cc-shower-door (mesmo nicho e-commerce)
     - Estratégia: PageSpeed Insights + Core Web Vitals + Review de structured data
     - Resultado: Melhoria de 23% no LCP, 15% no CLS

[AGENTE USA O CONTEXTO]
O agente incorpora as estratégias que funcionaram antes:
- Inclui Screaming Frog + GSC + SEMrush (como na #1)
- Adiciona PageSpeed + Core Web Vitals (como na #2, que não tinha sido feito na #1)
- Planeja verificar os mesmos problemas críticos encontrados antes

[AGENTE FAZ O TRABALHO]
... executa a auditoria combinando as duas abordagens ...

[DEPOIS - registra novo aprendizado]
$ python record.py \
  --summary "SEO audit fips-nautica — 2a rodada com CWV" \
  --content "Auditoria completa incluindo ..." \
  --client "fips-nautica" \
  --niche "moda-naval" \
  --agent-role "seo-visibilidade" \
  --task-type "seo-audit" \
  --strategy "Screaming Frog + GSC + SEMrush + PageSpeed Insights + CWV" \
  --result "52 páginas auditadas, 15 críticos, 8 melhorias imediatas identificadas" \
  --success-score 9 \
  --tags '["seo","audit","ecommerce","CWV"]'

→ MEMÓRIA SALVA. Próxima vez que um agente fizer auditoria similar,
  ele encontra esta também — com a estratégia combinada que funcionou.
```

## 8. O Efeito de Longo Prazo

Com o tempo, a base `agent_memories` cresce e se torna o **cérebro coletivo** dos agentes:

**Semana 1:** Base vazia. Agentes trabalham sem contexto, mas já registram.
**Mês 1:** Dezenas de memórias. Agentes começam a encontrar estratégias relevantes.
**Mês 3:** Centenas de memórias. Cada nova tarefa já encontra 3-5 casos similares.
**Mês 6:** Milhares. O sistema começa a revelar padrões: "para e-commerce de moda, a estratégia X funciona melhor que Y".

Os agentes deixam de operar isoladamente e passam a ter uma **memória institucional compartilhada**.

## 9. Estrutura de Arquivos

```
.agents/skills/geral-memoria-agentes/     ← clone da skill
├── SKILL.md                              ← instruções pro agente
└── scripts/
    ├── setup.py                          ← setup automático
    ├── search.py                         ← busca similaridade
    ├── record.py                         ← registro de memória
    └── setup/
        └── supabase-schema.sql           ← DDL do banco

.claude/skills/geral-memoria-agentes/     ← duplo-write (idêntico)

projetos/infraestrutura/memoria-agentes/   ← ← ← VOCÊ ESTÁ AQUI
├── README.md                              ← este documento
└── task/                                  ← (crie aqui suas tasks)
```
