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
  REPO_URL="https://marcoslrvusa:${GITHUB_TOKEN}@github.com/PerettoCo/hub-agentes-ia.git"
  if [ ! -d /workspace/.git ]; then
    echo "[entrypoint] Setting up workspace..."
    rm -rf /workspace/* /workspace/.[!.]* /workspace/.??* 2>/dev/null || true
    git clone -b main --single-branch "$REPO_URL" /workspace || echo "[entrypoint] Git clone failed (non-fatal)"
    git -C /workspace remote set-url origin https://github.com/PerettoCo/hub-agentes-ia.git 2>/dev/null || true
  else
    echo "[entrypoint] Updating workspace..."
    git -C /workspace remote set-url origin "$REPO_URL" 2>/dev/null || true
    git -C /workspace pull --ff-only 2>/dev/null || echo "[entrypoint] Git pull failed (non-fatal)"
  fi
fi

# Per-user workspace directories (any agent can use)
HUB_USER="${HUB_USERNAME:-unknown}"
for u in marcos.luciano fhelipe.aranha lucas.nunes paolo.carmine bruno.lindenmeyer italo.rossi; do
  u_safe="${u//./-}"
  mkdir -p /workspace/input/"$u_safe"
  mkdir -p /workspace/output/"$u_safe"/{handoff,reports,queries,shared,temp}
done

# Input dir for file uploads (user saves files here, agent reads with file-reader.py)
for u in bruno-lindenmeyer fhelipe-aranha italo-rossi lucas-nunes marcos-luciano paolo-carmine; do
  mkdir -p /workspace/input/"$u"
done

rm -f /workspace/opencode.json

exec "$@"
