#!/bin/bash
set -e

REPO_URL="https://github.com/PerettoCo/hub-agentes.git"

if [ -n "$GITHUB_TOKEN" ]; then
  REPO_URL="https://marcoslrvusa:${GITHUB_TOKEN}@github.com/PerettoCo/hub-agentes.git"
fi

if [ ! -d /workspace/.git ]; then
  echo "[entrypoint] Cloning hub-agentes into /workspace..."
  git clone "$REPO_URL" /workspace
  git -C /workspace remote set-url origin https://github.com/PerettoCo/hub-agentes.git
else
  echo "[entrypoint] Workspace already cloned, pulling latest..."
  git -C /workspace pull --ff-only
fi

exec "$@"
