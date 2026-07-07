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

exec "$@"
