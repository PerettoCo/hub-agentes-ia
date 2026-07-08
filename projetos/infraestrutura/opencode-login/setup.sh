#!/bin/bash
set -e

echo "=== OpenCode Login — Setup ==="
echo ""

# 1. Verificar se node está instalado
if ! command -v node &> /dev/null; then
  echo "[ERRO] Node.js não encontrado. Instale node 22+ primeiro."
  exit 1
fi

# 2. Instalar dependências
echo "[1/4] Instalando dependências..."
npm install --production

# 3. Gerar users.json a partir do example se não existir
if [ ! -f users.json ]; then
  echo "[2/4] Criando users.json a partir do example..."
  cp users.example.json users.json
  echo "  → users.json criado. Configure os usuários e senhas!"
  echo "  → Use: node gerar-senha.js <senha> para gerar hashes"
else
  echo "[2/4] users.json já existe — pulando"
fi

# 4. Verificar .env
if [ ! -f .env ]; then
  echo "[3/4] Copiando .env.example → .env"
  cp .env.example .env
  echo "  → Configure as chaves no .env antes de iniciar!"
else
  echo "[3/4] .env já existe — pulando"
fi

# 5. Testar saúde
echo "[4/4] Testando sintaxe do servidor..."
node -e "require('./server.js')" &
SERVER_PID=$!
sleep 2
kill $SERVER_PID 2>/dev/null || true

echo ""
echo "=== Setup concluído! ==="
echo ""
echo "Próximos passos:"
echo "  1. Edite users.json com os usuários reais"
echo "  2. Use 'node gerar-senha.js <senha>' pra cada senha"
echo "  3. Edite .env com as chaves reais"
echo "  4. Rode: node server.js"
echo ""
echo "Para deploy no Dockploy, use o docker-compose em Dockploy.md"
