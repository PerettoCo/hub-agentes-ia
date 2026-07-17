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
echo "Y29uc3QgaHR0cCA9IHJlcXVpcmUoJ2h0dHAnKTsKY29uc3QgZnMgPSByZXF1aXJlKCdmcycpOwoKY29uc3QgQkFDS0VORF9QT1JUID0gcGFyc2VJbnQocHJvY2Vzcy5lbnYuT1BFTkNPREVfQkFDS0VORF9QT1JUIHx8ICc0MDk3Jyk7CmNvbnN0IFBST1hZX1BPUlQgPSBwYXJzZUludChwcm9jZXNzLmVudi5PUEVOQ09ERV9QUk9YWV9QT1JUIHx8ICc0MDk2Jyk7CmNvbnN0IENPTkZJR19QQVRIID0gcHJvY2Vzcy5lbnYuT1BFTkNPREVfQ09ORklHX1BBVEggfHwgJy93b3Jrc3BhY2UvLmNvbmZpZy9vcGVuY29kZS9vcGVuY29kZS5qc29uJzsKCmNvbnN0IEFVVEggPSBwcm9jZXNzLmVudi5PUEVOQ09ERV9TRVJWRVJfUEFTU1dPUkQKICA/ICdCYXNpYyAnICsgQnVmZmVyLmZyb20ocHJvY2Vzcy5lbnYuT1BFTkNPREVfU0VSVkVSX1VTRVJOQU1FICsgJzonICsgcHJvY2Vzcy5lbnYuT1BFTkNPREVfU0VSVkVSX1BBU1NXT1JEKS50b1N0cmluZygnYmFzZTY0JykKICA6IG51bGw7CgpmdW5jdGlvbiBiYWNrZW5kRmV0Y2gocGF0aCkgewogIHJldHVybiBuZXcgUHJvbWlzZShmdW5jdGlvbihyZXNvbHZlLCByZWplY3QpIHsKICAgIHZhciBvcHRzID0geyBob3N0bmFtZTogJzEyNy4wLjAuMScsIHBvcnQ6IEJBQ0tFTkRfUE9SVCwgcGF0aDogcGF0aCwgbWV0aG9kOiAnR0VUJywgaGVhZGVyczoge30gfTsKICAgIGlmIChBVVRIKSBvcHRzLmhlYWRlcnMuYXV0aG9yaXphdGlvbiA9IEFVVEg7CiAgICB2YXIgcmVxID0gaHR0cC5nZXQob3B0cywgZnVuY3Rpb24ocmVzKSB7CiAgICAgIHZhciBkID0gJyc7CiAgICAgIHJlcy5vbignZGF0YScsIGZ1bmN0aW9uKGMpIHsgZCArPSBjOyB9KTsKICAgICAgcmVzLm9uKCdlbmQnLCBmdW5jdGlvbigpIHsgcmVzb2x2ZShkKTsgfSk7CiAgICB9KTsKICAgIHJlcS5vbignZXJyb3InLCByZWplY3QpOwogIH0pOwp9CgpmdW5jdGlvbiBsb2FkQ3VzdG9tQWdlbnRzKCkgewogIHRyeSB7CiAgICBpZiAoIWZzLmV4aXN0c1N5bmMoQ09ORklHX1BBVEgpKSByZXR1cm4gW107CiAgICB2YXIgY29uZmlnID0gSlNPTi5wYXJzZShmcy5yZWFkRmlsZVN5bmMoQ09ORklHX1BBVEgsICd1dGYtOCcpKTsKICAgIHZhciBhZ2VudHMgPSBjb25maWcuYWdlbnQgfHwge307CiAgICByZXR1cm4gT2JqZWN0LmtleXMoYWdlbnRzKS5tYXAoZnVuY3Rpb24obmFtZSkgewogICAgICByZXR1cm4geyBuYW1lOiBuYW1lLCBkZXNjcmlwdGlvbjogYWdlbnRzW25hbWVdLmRlc2NyaXB0aW9uIHx8ICcnLCBtb2RlOiBhZ2VudHNbbmFtZV0ubW9kZSB8fCAnc3ViYWdlbnQnLCBuYXRpdmU6IGZhbHNlLCBwZXJtaXNzaW9uOiBbXSwgb3B0aW9uczoge30gfTsKICAgIH0pOwogIH0gY2F0Y2ggKGUpIHsgcmV0dXJuIFtdOyB9Cn0KCmZ1bmN0aW9uIGxvYWRDdXN0b21BcGlBZ2VudHMoKSB7CiAgdHJ5IHsKICAgIGlmICghZnMuZXhpc3RzU3luYyhDT05GSUdfUEFUSCkpIHJldHVybiBbXTsKICAgIHZhciBjb25maWcgPSBKU09OLnBhcnNlKGZzLnJlYWRGaWxlU3luYyhDT05GSUdfUEFUSCwgJ3V0Zi04JykpOwogICAgdmFyIGFnZW50cyA9IGNvbmZpZy5hZ2VudCB8fCB7fTsKICAgIHJldHVybiBPYmplY3Qua2V5cyhhZ2VudHMpLm1hcChmdW5jdGlvbihuYW1lKSB7CiAgICAgIHJldHVybiB7IGlkOiBuYW1lLCBkZXNjcmlwdGlvbjogYWdlbnRzW25hbWVdLmRlc2NyaXB0aW9uIHx8ICcnLCBtb2RlOiBhZ2VudHNbbmFtZV0ubW9kZSB8fCAnc3ViYWdlbnQnLCBoaWRkZW46IGZhbHNlLCBwZXJtaXNzaW9uczogW10sIHJlcXVlc3Q6IHt9LCBzeXN0ZW06ICcnIH07CiAgICB9KTsKICB9IGNhdGNoIChlKSB7IHJldHVybiBbXTsgfQp9Cgp2YXIgc2VydmVyID0gaHR0cC5jcmVhdGVTZXJ2ZXIoZnVuY3Rpb24ocmVxLCByZXMpIHsKICB2YXIgdXJsUGF0aCA9IHJlcS51cmwuc3BsaXQoJz8nKVswXTsKICB2YXIgaXNBZ2VudCA9ICh1cmxQYXRoID09PSAnL2FnZW50JyB8fCB1cmxQYXRoID09PSAnL2FwaS9hZ2VudCcpICYmIHJlcS5tZXRob2QgPT09ICdHRVQnOwogIHZhciBpc1NraWxsID0gdXJsUGF0aCA9PT0gJy9hcGkvc2tpbGwnICYmIHJlcS5tZXRob2QgPT09ICdHRVQnOwoKICB2YXIgb3B0cyA9IHsgaG9zdG5hbWU6ICcxMjcuMC4wLjEnLCBwb3J0OiBCQUNLRU5EX1BPUlQsIHBhdGg6IHJlcS51cmwsIG1ldGhvZDogcmVxLm1ldGhvZCwgaGVhZGVyczoge30gfTsKICBmb3IgKHZhciBrIGluIHJlcS5oZWFkZXJzKSBvcHRzLmhlYWRlcnNba10gPSByZXEuaGVhZGVyc1trXTsKICBpZiAoQVVUSCAmJiAhb3B0cy5oZWFkZXJzLmF1dGhvcml6YXRpb24pIG9wdHMuaGVhZGVycy5hdXRob3JpemF0aW9uID0gQVVUSDsKCiAgdmFyIGJyZXEgPSBodHRwLnJlcXVlc3Qob3B0cywgZnVuY3Rpb24oYnJlcykgewogICAgZnVuY3Rpb24gcGFzc1Rocm91Z2goKSB7IHJlcy53cml0ZUhlYWQoYnJlcy5zdGF0dXNDb2RlLCBicmVzLmhlYWRlcnMpOyBicmVzLnBpcGUocmVzKTsgfQoKICAgIGlmICgoaXNBZ2VudCB8fCBpc1NraWxsKSAmJiBicmVzLnN0YXR1c0NvZGUgPT09IDIwMCAmJiByZXEubWV0aG9kID09PSAnR0VUJykgewogICAgICB2YXIgYm9keSA9ICcnOwogICAgICBicmVzLm9uKCdkYXRhJywgZnVuY3Rpb24oYykgeyBib2R5ICs9IGM7IH0pOwogICAgICBicmVzLm9uKCdlbmQnLCBmdW5jdGlvbigpIHsKICAgICAgICB0cnkgewogICAgICAgICAgaWYgKGlzU2tpbGwpIHsKICAgICAgICAgICAgdmFyIG9yaWcgPSBKU09OLnBhcnNlKGJvZHkpOwogICAgICAgICAgICB2YXIgZXhpc3RpbmcgPSBvcmlnLmRhdGEgfHwgW107CiAgICAgICAgICAgIGJhY2tlbmRGZXRjaCgnL3NraWxsP2RpcmVjdG9yeT0vd29ya3NwYWNlJykudGhlbihmdW5jdGlvbih3c0JvZHkpIHsKICAgICAgICAgICAgICB0cnkgewogICAgICAgICAgICAgICAgdmFyIHdzU2tpbGxzID0gSlNPTi5wYXJzZSh3c0JvZHkpOwogICAgICAgICAgICAgICAgdmFyIHNlZW4gPSB7fTsKICAgICAgICAgICAgICAgIGV4aXN0aW5nLmZvckVhY2goZnVuY3Rpb24ocykgeyBzZWVuW3MubmFtZV0gPSB0cnVlOyB9KTsKICAgICAgICAgICAgICAgIHdzU2tpbGxzLmZvckVhY2goZnVuY3Rpb24ocykgewogICAgICAgICAgICAgICAgICBpZiAoIXNlZW5bcy5uYW1lXSkgeyBzZWVuW3MubmFtZV0gPSB0cnVlOyBleGlzdGluZy5wdXNoKHsgbmFtZTogcy5uYW1lLCBkZXNjcmlwdGlvbjogcy5kZXNjcmlwdGlvbiB8fCAnJywgbG9jYXRpb246IHMubG9jYXRpb24gfHwgJycsIGNvbnRlbnQ6IHMuY29udGVudCB8fCAnJyB9KTsgfQogICAgICAgICAgICAgICAgfSk7CiAgICAgICAgICAgICAgICB2YXIgbWVyZ2VkID0geyBsb2NhdGlvbjogb3JpZy5sb2NhdGlvbiwgZGF0YTogZXhpc3RpbmcgfTsKICAgICAgICAgICAgICAgIHJlcy53cml0ZUhlYWQoMjAwLCB7ICdjb250ZW50LXR5cGUnOiAnYXBwbGljYXRpb24vanNvbicsICdhY2Nlc3MtY29udHJvbC1hbGxvdy1vcmlnaW4nOiAnKicgfSk7CiAgICAgICAgICAgICAgICByZXMuZW5kKEpTT04uc3RyaW5naWZ5KG1lcmdlZCkpOwogICAgICAgICAgICAgIH0gY2F0Y2ggKGUpIHsgcGFzc1Rocm91Z2goKTsgfQogICAgICAgICAgICB9LCBmdW5jdGlvbigpIHsgcGFzc1Rocm91Z2goKTsgfSk7CiAgICAgICAgICB9IGVsc2UgewogICAgICAgICAgICB2YXIgbWVyZ2VkOwogICAgICAgICAgICBpZiAodXJsUGF0aCA9PT0gJy9hcGkvYWdlbnQnKSB7CiAgICAgICAgICAgICAgdmFyIG9yaWcgPSBKU09OLnBhcnNlKGJvZHkpOwogICAgICAgICAgICAgIHZhciBleGlzdGluZ0lkcyA9IHt9OwogICAgICAgICAgICAgIChvcmlnLmRhdGEgfHwgW10pLmZvckVhY2goZnVuY3Rpb24oYSkgeyBpZiAoYS5pZCkgZXhpc3RpbmdJZHNbYS5pZF0gPSB0cnVlOyB9KTsKICAgICAgICAgICAgICB2YXIgY3VzdG9tQXBpID0gbG9hZEN1c3RvbUFwaUFnZW50cygpLmZpbHRlcihmdW5jdGlvbihhKSB7IHJldHVybiAhZXhpc3RpbmdJZHNbYS5pZF07IH0pOwogICAgICAgICAgICAgIG1lcmdlZCA9IHsgbG9jYXRpb246IG9yaWcubG9jYXRpb24sIGRhdGE6IChvcmlnLmRhdGEgfHwgW10pLmNvbmNhdChjdXN0b21BcGkpIH07CiAgICAgICAgICAgIH0gZWxzZSB7CiAgICAgICAgICAgICAgdmFyIGJhc2UgPSBKU09OLnBhcnNlKGJvZHkpOwogICAgICAgICAgICAgIHZhciBleGlzdGluZ05hbWVzID0ge307CiAgICAgICAgICAgICAgYmFzZS5mb3JFYWNoKGZ1bmN0aW9uKGEpIHsgaWYgKGEubmFtZSkgZXhpc3RpbmdOYW1lc1thLm5hbWVdID0gdHJ1ZTsgfSk7CiAgICAgICAgICAgICAgdmFyIGN1c3RvbSA9IGxvYWRDdXN0b21BZ2VudHMoKS5maWx0ZXIoZnVuY3Rpb24oYSkgeyByZXR1cm4gIWV4aXN0aW5nTmFtZXNbYS5uYW1lXTsgfSk7CiAgICAgICAgICAgICAgbWVyZ2VkID0gYmFzZS5jb25jYXQoY3VzdG9tKTsKICAgICAgICAgICAgfQogICAgICAgICAgICByZXMud3JpdGVIZWFkKDIwMCwgeyAnY29udGVudC10eXBlJzogJ2FwcGxpY2F0aW9uL2pzb24nLCAnYWNjZXNzLWNvbnRyb2wtYWxsb3ctb3JpZ2luJzogJyonIH0pOwogICAgICAgICAgICByZXMuZW5kKEpTT04uc3RyaW5naWZ5KG1lcmdlZCkpOwogICAgICAgICAgfQogICAgICAgIH0gY2F0Y2ggKGUpIHsKICAgICAgICAgIGNvbnNvbGUuZXJyb3IoJ1twcm94eV0gbWVyZ2UgZXJyb3I6JywgZS5tZXNzYWdlKTsKICAgICAgICAgIHBhc3NUaHJvdWdoKCk7CiAgICAgICAgfQogICAgICB9KTsKICAgIH0gZWxzZSB7CiAgICAgIHBhc3NUaHJvdWdoKCk7CiAgICB9CiAgfSk7CgogIGJyZXEub24oJ2Vycm9yJywgZnVuY3Rpb24oZSkgewogICAgcmVzLndyaXRlSGVhZCg1MDIsIHsgJ2NvbnRlbnQtdHlwZSc6ICd0ZXh0L3BsYWluJyB9KTsKICAgIHJlcy5lbmQoJ3Byb3h5IGVycm9yOiAnICsgZS5tZXNzYWdlKTsKICB9KTsKCiAgcmVxLnBpcGUoYnJlcSk7Cn0pOwoKc2VydmVyLm9uKCdlcnJvcicsIGZ1bmN0aW9uKGUpIHsKICBjb25zb2xlLmVycm9yKCdbcHJveHldIEZBVEFMOicsIGUubWVzc2FnZSk7CiAgcHJvY2Vzcy5leGl0KDEpOwp9KTsKCnNlcnZlci5saXN0ZW4oUFJPWFlfUE9SVCwgJzAuMC4wLjAnLCBmdW5jdGlvbigpIHsKICBjb25zb2xlLmxvZygnW3Byb3h5XSBsaXN0ZW5pbmcgb24gOicgKyBQUk9YWV9QT1JUICsgJyAtPiA6JyArIEJBQ0tFTkRfUE9SVCk7Cn0pOwo=" | base64 -d > /workspace/scripts/opencode-proxy.js
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
