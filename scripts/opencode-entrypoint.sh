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

mkdir -p /home/node/.npm /home/node/.cache /home/node/.config/opencode
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
mkdir -p /workspace/outputs /workspace/.local/state /tmp/opencode
chown node:node /workspace/outputs /workspace/.local/state /tmp/opencode 2>/dev/null || true

rm -f /workspace/opencode.json

# Upgrade opencode on every restart
npm install -g opencode-ai@latest 2>&1 | tail -1

# Start opencode on internal port (not exposed to gateway)
echo "[entrypoint] Starting opencode on 127.0.0.1:4097..."
su node -c "cd /workspace && NODE_PATH=/usr/local/lib/node_modules nohup /usr/local/bin/opencode web --hostname 127.0.0.1 --port 4097 --print-logs > /tmp/opencode/opencode.log 2>&1 &"
OPENCODE_PID=$!

# Wait for opencode to be ready
for i in $(seq 1 30); do
  if curl -s http://127.0.0.1:4097/global/health > /dev/null 2>&1; then
    echo "[entrypoint] opencode ready"
    break
  fi
  sleep 1
done

# Start the agent proxy on port 4096 (the port gateway expects)
echo "[entrypoint] Starting agent proxy on 0.0.0.0:4096..."
exec su node -c "cd /workspace && node scripts/opencode-proxy.js"
