-- Rodar no Supabase de memória (bkenzsvexfayjcrqnmpx)
-- NÃO rodar no banco de dados de produção

-- Tabela de Mission Control por cliente
CREATE TABLE IF NOT EXISTS mission_controls (
  id SERIAL PRIMARY KEY,
  cliente_id INTEGER UNIQUE,
  cliente_nome TEXT NOT NULL,
  dados_raiox JSONB DEFAULT '{}',
  regras_guardrails JSONB DEFAULT '[]',
  historico_resumo TEXT DEFAULT '',
  ultimo_checkin TIMESTAMPTZ,
  ultimo_checkin_resumo TEXT DEFAULT '',
  bets_ativas JSONB DEFAULT '[]',
  combinados_pendentes JSONB DEFAULT '[]',
  personas JSONB DEFAULT '[]',
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de outputs dos agentes
CREATE TABLE IF NOT EXISTS agent_outputs (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  modelo TEXT,
  cliente TEXT,
  query TEXT,
  resposta TEXT,
  fontes TEXT,
  arquivo_path TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela de trabalhos enviados para aprovação
CREATE TABLE IF NOT EXISTS pending_approvals (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  cliente TEXT,
  tipo TEXT DEFAULT 'output',
  conteudo TEXT,
  arquivo_path TEXT,
  status TEXT DEFAULT 'pending',
  reviewed_by TEXT,
  reviewed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
