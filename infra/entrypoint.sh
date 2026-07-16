#!/bin/bash
set -e

mkdir -p /home/node/.local/bin
cat > /home/node/.local/bin/xdg-open << 'XDGEOF'
#!/bin/bash
echo "[xdg-open] suppressed (headless container)"
XDGEOF
chmod +x /home/node/.local/bin/xdg-open
export PATH="/home/node/.local/bin:$PATH"
export BROWSER=/home/node/.local/bin/xdg-open

# Ensure home directories exist for persistence
mkdir -p /home/node/.npm /home/node/.cache /home/node/.config/opencode

# Trust all git repos (container-safe)
git config --global safe.directory '*'

GIT_REPO="${HUB_REPO:-PerettoCo/hub-agentes}"
GIT_BRANCH="${HUB_BRANCH:-infra-v2}"
GIT_USER="${HUB_GIT_USER:-marcoslrvusa}"

if [ -n "$GITHUB_TOKEN" ]; then
  REPO_URL="https://${GIT_USER}:${GITHUB_TOKEN}@github.com/${GIT_REPO}.git"
  PUBLIC_URL="https://github.com/${GIT_REPO}.git"

  if [ ! -d /workspace/.git ]; then
    echo "[entrypoint] Setting up workspace (${GIT_BRANCH})..."
    git init /workspace
    git -C /workspace remote add origin "$REPO_URL"
    git -C /workspace fetch origin "$GIT_BRANCH"
    git -C /workspace checkout -b "$GIT_BRANCH" "origin/$GIT_BRANCH"
    git -C /workspace remote set-url origin "$PUBLIC_URL"
  else
    echo "[entrypoint] Updating workspace..."
    git -C /workspace remote set-url origin "$REPO_URL"
    git -C /workspace fetch --all
    git -C /workspace reset --hard "origin/$GIT_BRANCH"
    git -C /workspace remote set-url origin "$PUBLIC_URL"
  fi

  echo "[entrypoint] Workspace ready (commit: $(git -C /workspace rev-parse --short HEAD 2>/dev/null || echo 'unknown'))"
else
    echo "[entrypoint] GITHUB_TOKEN not set — workspace will remain as-is"
fi

chown -R node:node /workspace 2>/dev/null || true
su node -c "git config --global safe.directory /workspace" 2>/dev/null || true
mkdir -p /workspace/outputs /workspace/.local/state
chown node:node /workspace/outputs /workspace/.local/state 2>/dev/null || true

rm -f /workspace/opencode.json

exec su node -c "cd /workspace && NODE_PATH=/usr/local/lib/node_modules exec /usr/local/bin/opencode web --hostname 0.0.0.0 --port 4096 --print-logs"
