#!/bin/bash

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

# Comentado: resetar estado força reindexação lenta a cada restart
# echo "[entrypoint] Resetting workspace preference..."
# rm -f /home/node/.local/share/opencode/state.json /home/node/.local/share/opencode/projects.json /home/node/.local/share/opencode/workspace* 2>/dev/null || true

exec "$@"
