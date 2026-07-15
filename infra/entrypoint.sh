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

if [ -n "$GITHUB_TOKEN" ]; then
  REPO_URL="https://marcoslrvusa:${GITHUB_TOKEN}@github.com/PerettoCo/hub-agentes.git"
  if [ ! -d /workspace/.git ]; then
    echo "[entrypoint] Setting up workspace (infra-v2)..."
    rm -rf /workspace
    git clone -b infra-v2 --single-branch "$REPO_URL" /workspace
    git -C /workspace remote set-url origin https://github.com/PerettoCo/hub-agentes.git
  else
    echo "[entrypoint] Updating workspace..."
    git -C /workspace remote set-url origin "$REPO_URL"
    git -C /workspace pull --ff-only
  fi
fi

mkdir -p /workspace/outputs

rm -f /workspace/opencode.json

exec "$@"
