#!/bin/bash
# Save session to log/
set -e
DIR="$(dirname "$0")/../log"
mkdir -p "$DIR"
TS=$(date +%Y-%m-%d_%H-%M-%S)
echo "$TS"
