#!/bin/bash

# Mata o xdg-open pra evitar crash do opencode web ao tentar abrir browser
mkdir -p /home/node/.local/bin
cat > /home/node/.local/bin/xdg-open << 'XDGEOF'
#!/bin/bash
echo "[xdg-open] suppressed (headless container)"
XDGEOF
chmod +x /home/node/.local/bin/xdg-open
export PATH="/home/node/.local/bin:$PATH"
export BROWSER=/home/node/.local/bin/xdg-open

# Garante que o Python venv esteja no PATH
if [ -d /opt/venv ]; then
  export PATH="/opt/venv/bin:$PATH"
  export VIRTUAL_ENV="/opt/venv"
fi

# Clone/update do workspace
if [ -n "$GITHUB_TOKEN" ]; then
  if [ ! -d /workspace/.git ]; then
    echo "[entrypoint] Cloning hub-agentes into /workspace..."
    git clone "https://marcoslrvusa:${GITHUB_TOKEN}@github.com/PerettoCo/hub-agentes.git" /workspace
    git -C /workspace remote set-url origin https://github.com/PerettoCo/hub-agentes.git
  else
    echo "[entrypoint] Updating workspace..."
    git -C /workspace remote set-url origin "https://marcoslrvusa:${GITHUB_TOKEN}@github.com/PerettoCo/hub-agentes.git"
    git -C /workspace pull --ff-only
  fi
fi

# Remove opencode.json do workspace (project-level) para evitar conflito com o bind mount do usuário
rm -f /workspace/opencode.json

exec "$@"
