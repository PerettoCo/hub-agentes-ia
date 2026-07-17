#!/bin/bash
set -e

mkdir -p /home/node/.local/bin
cat > /home/node/.local/bin/xdg-open << 'XDGEOF'
#!/bin/bash
echo "[xdg-open] suppressed (headless container)"
XDGEOF
chmod +x /home/node/.local/bin/xdg-open
export PATH="/home/node/.local/bin:/home/marcos/.nvm/versions/node/v22.22.2/bin:/home/marcos/.opencode/bin:/usr/bin:/home/marcos/.npm-global/bin:/home/marcos/.local/bin:/home/marcos/.nvm/versions/node/v22.22.2/bin:/home/marcos/.opencode/bin:/usr/bin:/home/marcos/.npm-global/bin:/home/marcos/.local/bin:/usr/bin:/home/marcos/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin"
export BROWSER=/home/node/.local/bin/xdg-open

mkdir -p /home/node/.npm /home/node/.cache /home/node/.config/opencode
git config --global safe.directory '*'

GIT_REPO="${HUB_REPO:-PerettoCo/hub-agentes}"
GIT_BRANCH="${HUB_BRANCH:-infra-v2-clean}"
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
    git -C /workspace checkout -B "$GIT_BRANCH" "origin/$GIT_BRANCH"
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

# Copy opencode config to home dir so the opencode backend reads it
cp /workspace/.config/opencode/opencode.json /home/node/.config/opencode/opencode.json 2>/dev/null || true
chown node:node /home/node/.config/opencode/opencode.json 2>/dev/null || true

# Copy agent definitions (.md) to home dir so subagents work (model, permissions, system prompt)
mkdir -p /home/node/.config/opencode/agents/
if [ -d /workspace/infra/agents ]; then
  cp /workspace/infra/agents/*.md /home/node/.config/opencode/agents/ 2>/dev/null || true
  chown -R node:node /home/node/.config/opencode/agents/ 2>/dev/null || true
fi

# Symlink workspace skills to home so opencode auto-discovers from home too
if [ -d /workspace/.agents/skills ]; then
  rm -rf /home/node/.config/opencode/skills 2>/dev/null
  ln -sf /workspace/.agents/skills /home/node/.config/opencode/skills 2>/dev/null || true
  chown -h node:node /home/node/.config/opencode/skills 2>/dev/null || true
fi

# Create agent proxy script  
# Copy agent proxy script from repo (replaces base64-embedded version)
cp /workspace/infra/scripts/opencode-proxy.js /workspace/scripts/opencode-proxy.js 2>/dev/null || true
chown node:node /workspace/scripts/opencode-proxy.js 2>/dev/null || true

# Latest opencode (auto-discovery de modelos do LiteLLM via /v1/models)
npm install -g opencode-ai@latest 2>&1 | tail -1

echo "[entrypoint] Starting opencode on 127.0.0.1:4097..."
su node -c "cd /workspace && NODE_PATH=/usr/local/lib/node_modules nohup /usr/local/bin/opencode web --hostname 127.0.0.1 --port 4097 --print-logs > /tmp/opencode/opencode.log 2>&1 &"

for i in $(seq 1 30); do
  if curl -s http://127.0.0.1:4097/global/health > /dev/null 2>&1; then
    echo "[entrypoint] opencode ready"
    break
  fi
  sleep 1
done

echo "[entrypoint] Starting agent proxy on 0.0.0.0:4096..."
exec su node -c "cd /workspace && NODE_PATH=/usr/local/lib/node_modules node scripts/opencode-proxy.js"
