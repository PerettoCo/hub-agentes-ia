#!/bin/bash
set -e

# Suppress xdg-open in headless container
mkdir -p /home/node/.local/bin
cat > /home/node/.local/bin/xdg-open << 'XDGEOF'
#!/bin/bash
echo "[xdg-open] suppressed (headless container)"
XDGEOF
chmod +x /home/node/.local/bin/xdg-open
export PATH="/home/node/.local/bin:$PATH"
export BROWSER=/home/node/.local/bin/xdg-open

mkdir -p /workspace/outputs

if [ -n "$GITHUB_TOKEN" ]; then
  REPO_URL="https://marcoslrvusa:${GITHUB_TOKEN}@github.com/PerettoCo/hub-agentes.git"
  if [ ! -d /workspace/.git ]; then
    echo "[entrypoint] Cloning hub-agentes (infra-v2) into /workspace..."
    git clone -b infra-v2 --single-branch "$REPO_URL" /workspace
    git -C /workspace remote set-url origin https://github.com/PerettoCo/hub-agentes.git
  else
    echo "[entrypoint] Updating workspace..."
    git -C /workspace remote set-url origin "$REPO_URL"
    git -C /workspace pull --ff-only
  fi
fi

# Remove project-level opencode.json — each user has their own via Docker bind mount
rm -f /workspace/opencode.json

exec "$@"
