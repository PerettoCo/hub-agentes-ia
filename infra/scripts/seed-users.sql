-- Tabela de usuários para sync com Supabase (opcional)
-- Esta SQL é para o banco de MEMÓRIA
-- A fonte primária de usuários é o arquivo /data/users.json

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT,
  squad TEXT,
  role TEXT DEFAULT 'user'
);

-- Senha padrão para todos: v4@2025
-- A senha é alterada via: node infra/scripts/manage-users.js passwd <username> <senha>
-- Ou pelo dashboard no /api/users

-- Gere hashes atualizados com: node infra/scripts/hash-password.js "v4@2025" username
INSERT INTO users (username, password_hash, name, email, squad, role) VALUES
  ('marcos.luciano',  '$2b$10$hbKezvHhmyqx4kkmlS2E8.EmORDg4Fwmm5ZQt4WIPrK7O4k2SmDWi', 'Marcos Luciano',   'marcos@fvmarketing.com.br', 'Growth', 'admin'),
  ('fhelipe.aranha',  '$2b$10$hbKezvHhmyqx4kkmlS2E8.EmORDg4Fwmm5ZQt4WIPrK7O4k2SmDWi', 'Fhelipe Aranha',   'fhelipe@fvmarketing.com.br', 'Growth', 'user'),
  ('lucas.nunes',     '$2b$10$hbKezvHhmyqx4kkmlS2E8.EmORDg4Fwmm5ZQt4WIPrK7O4k2SmDWi', 'Lucas Nunes',      'lucas@fvmarketing.com.br', 'Growth', 'user'),
  ('paolo.carmine',   '$2b$10$hbKezvHhmyqx4kkmlS2E8.EmORDg4Fwmm5ZQt4WIPrK7O4k2SmDWi', 'Paolo Carmine',    'paolo@fvmarketing.com.br', 'Design', 'user'),
  ('bruno.lindenmeyer', '$2b$10$hbKezvHhmyqx4kkmlS2E8.EmORDg4Fwmm5ZQt4WIPrK7O4k2SmDWi', 'Bruno Lindenmeyer', 'bruno@fvmarketing.com.br', 'Tech', 'user'),
  ('italo.rossi',     '$2b$10$hbKezvHhmyqx4kkmlS2E8.EmORDg4Fwmm5ZQt4WIPrK7O4k2SmDWi', 'Ítalo Rossi',      'italo@fvmarketing.com.br', 'Design', 'user')
ON CONFLICT (username) DO NOTHING;
