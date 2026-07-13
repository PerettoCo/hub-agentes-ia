-- ============================================================
-- MEMORIA PGVECTOR — Supabase Migration v2.0
-- Projeto: bkenzsvexfayjcrqnmpx (opencode-memoria)
-- Uso: Rodar no SQL Editor do Supabase (uma vez)
-- ============================================================

-- 0. Extensoes
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- fuzzy string match pra fallback

-- 1. Tabela principal de memorias
CREATE TABLE IF NOT EXISTS agent_memories (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content         TEXT NOT NULL,
  content_tokens  INTEGER DEFAULT 0,
  embedding       vector(1536),
  agent_id        TEXT NOT NULL DEFAULT 'opencode',
  session_id      TEXT,
  parent_session  TEXT,                  -- sessao que originou
  memory_type     TEXT NOT NULL DEFAULT 'general'
    CHECK (memory_type IN ('fact','decision','learned','context','preference','general','session_summary')),
  importance      SMALLINT NOT NULL DEFAULT 1
    CHECK (importance BETWEEN 1 AND 5),
  ttl             TIMESTAMPTZ,           -- NULL = eterna, senao expira em
  consolidated    BOOLEAN DEFAULT false, -- true = resultado de consolidacao
  consolidated_from UUID[],              -- quais memorias foram consolidadas aqui
  access_count    INTEGER DEFAULT 0,
  last_accessed   TIMESTAMPTZ,
  metadata        JSONB DEFAULT '{}',
  checksum        TEXT,                  -- hash SHA256 do content pra dedup rapido
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- 2. Indices
-- HNSW para busca vetorial (cosine distance)
CREATE INDEX IF NOT EXISTS idx_agent_memories_hnsw
  ON agent_memories
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 200);

-- Indices auxiliares
CREATE INDEX IF NOT EXISTS idx_am_agent     ON agent_memories(agent_id);
CREATE INDEX IF NOT EXISTS idx_am_type      ON agent_memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_am_agent_type ON agent_memories(agent_id, memory_type);
CREATE INDEX IF NOT EXISTS idx_am_created   ON agent_memories(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_am_ttl       ON agent_memories(ttl) WHERE ttl IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_am_checksum  ON agent_memories(checksum) WHERE checksum IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_am_consolidated ON agent_memories(consolidated);

-- Full-text search (hybrid search)
CREATE INDEX IF NOT EXISTS idx_am_fts
  ON agent_memories
  USING gin(to_tsvector('portuguese', content));

-- 3. Funcao match com hybrid search (vector + FTS + filtros)
CREATE OR REPLACE FUNCTION match_agent_memories(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 5,
  p_agent_id TEXT DEFAULT 'opencode',
  p_memory_type TEXT DEFAULT NULL,
  p_session_id TEXT DEFAULT NULL,
  p_min_importance INT DEFAULT 1,
  p_fts_query TEXT DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  memory_type TEXT,
  importance SMALLINT,
  session_id TEXT,
  consolidated BOOLEAN,
  similarity float,
  fts_rank float,
  metadata JSONB,
  created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    am.id,
    am.content,
    am.memory_type,
    am.importance,
    am.session_id,
    am.consolidated,
    1 - (am.embedding <=> query_embedding) AS similarity,
    CASE
      WHEN p_fts_query IS NOT NULL
      THEN ts_rank(to_tsvector('portuguese', am.content), plainto_tsquery('portuguese', p_fts_query))
      ELSE 0
    END AS fts_rank,
    am.metadata,
    am.created_at
  FROM agent_memories am
  WHERE am.agent_id = p_agent_id
    AND (p_memory_type IS NULL OR am.memory_type = p_memory_type)
    AND (p_session_id IS NULL OR am.session_id = p_session_id)
    AND am.importance >= p_min_importance
    AND (am.ttl IS NULL OR am.ttl > now())
    AND 1 - (am.embedding <=> query_embedding) > match_threshold
  ORDER BY
    (1 - (am.embedding <=> query_embedding)) DESC,
    am.importance DESC,
    am.created_at DESC
  LIMIT match_count;
END;
$$;

-- 4. Funcao de busca APENAS full-text (fallback quando nao tem embedding)
CREATE OR REPLACE FUNCTION search_memories_fts(
  p_query TEXT,
  p_match_count int DEFAULT 5,
  p_agent_id TEXT DEFAULT 'opencode',
  p_memory_type TEXT DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  memory_type TEXT,
  importance SMALLINT,
  rank float,
  created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    am.id, am.content, am.memory_type, am.importance,
    ts_rank(to_tsvector('portuguese', am.content), plainto_tsquery('portuguese', p_query)) AS rank,
    am.created_at
  FROM agent_memories am
  WHERE am.agent_id = p_agent_id
    AND (p_memory_type IS NULL OR am.memory_type = p_memory_type)
    AND (am.ttl IS NULL OR am.ttl > now())
    AND to_tsvector('portuguese', am.content) @@ plainto_tsquery('portuguese', p_query)
  ORDER BY rank DESC, am.importance DESC
  LIMIT p_match_count;
END;
$$;

-- 5. Funcao de consolidacao: busca memorias similares e funde
CREATE OR REPLACE FUNCTION consolidate_similar_memories(
  p_agent_id TEXT DEFAULT 'opencode',
  p_similarity_threshold float DEFAULT 0.85,
  p_max_age_days int DEFAULT 30
)
RETURNS TABLE (
  consolidated_id UUID,
  source_count INT,
  merged_content TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
  rec RECORD;
  similar RECORD;
  new_id UUID;
  merged_text TEXT;
  source_ids UUID[];
  count_sources INT;
BEGIN
  FOR rec IN
    SELECT * FROM agent_memories
    WHERE agent_id = p_agent_id
      AND consolidated = false
      AND memory_type != 'session_summary'
      AND created_at > now() - (p_max_age_days || ' days')::INTERVAL
    ORDER BY created_at DESC
  LOOP
    -- Pular se ja foi consolidado como parte de outro grupo
    IF rec.id = ANY(source_ids) THEN
      CONTINUE;
    END IF;

    -- Buscar similares nao consolidadas
    SELECT array_agg(m.id), string_agg(m.content, E'\n\n---\n\n' ORDER BY m.created_at)
    INTO source_ids, merged_text
    FROM (
      SELECT m.id, m.content, m.created_at
      FROM agent_memories m
      WHERE m.agent_id = p_agent_id
        AND m.consolidated = false
        AND m.id != rec.id
        AND m.memory_type != 'session_summary'
        AND 1 - (m.embedding <=> rec.embedding) > p_similarity_threshold
        AND m.created_at > now() - (p_max_age_days || ' days')::INTERVAL
      ORDER BY m.created_at DESC
      LIMIT 10
    ) m;

    count_sources := array_length(source_ids, 1);

    IF count_sources > 0 THEN
      -- Incluir a propria rec
      source_ids := array_prepend(rec.id, source_ids);
      merged_text := rec.content || E'\n\n---\n\n' || merged_text;

      -- Inserir memoria consolidada
      INSERT INTO agent_memories (
        content, content_tokens, agent_id, memory_type,
        importance, consolidated, consolidated_from, metadata
      ) VALUES (
        merged_text,
        0,
        p_agent_id,
        rec.memory_type,
        LEAST(rec.importance + 1, 5),
        true,
        source_ids,
        jsonb_build_object(
          'consolidated_at', now(),
          'source_count', count_sources + 1,
          'original_types', (SELECT array_agg(DISTINCT memory_type) FROM agent_memories WHERE id = ANY(source_ids))
        )
      )
      RETURNING id INTO new_id;

      consolidated_id := new_id;
      source_count := count_sources + 1;
      merged_content := merged_text;
      RETURN NEXT;
    END IF;
  END LOOP;
END;
$$;

-- 6. Funcao de limpeza (expurga TTL expirado + consolidado velho)
CREATE OR REPLACE FUNCTION cleanup_expired_memories(
  p_agent_id TEXT DEFAULT 'opencode'
)
RETURNS TABLE (deleted_count INT)
LANGUAGE plpgsql
AS $$
DECLARE
  v_count INT;
BEGIN
  DELETE FROM agent_memories
  WHERE agent_id = p_agent_id
    AND (
      (ttl IS NOT NULL AND ttl < now())
      OR
      (consolidated = true AND created_at < now() - INTERVAL '90 days')
    );
  GET DIAGNOSTICS v_count = ROW_COUNT;
  deleted_count := v_count;
  RETURN NEXT;
END;
$$;

-- 7. Trigger: atualiza updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_agent_memories_updated_at ON agent_memories;
CREATE TRIGGER trg_agent_memories_updated_at
  BEFORE UPDATE ON agent_memories
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at();

-- 8. Trigger: atualiza access_count e last_accessed (chamado via RPC ou manual)
-- NOTA: nao e trigger automatico — chame update_access_count(id) quando ler
CREATE OR REPLACE FUNCTION update_access_count(p_id UUID)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE agent_memories
  SET access_count = access_count + 1,
      last_accessed = now()
  WHERE id = p_id;
END;
$$;

-- ============================================================
-- FIM DA MIGRATION
-- ============================================================
