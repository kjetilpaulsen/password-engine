#!/usr/bin/env bash
set -euo pipefail

if [[ -f .env ]]; then
  set -a
  . ./.env
  set +a
elif [[ -f .env.example ]]; then
  set -a
  . ./.env.example
  set +a
fi

: "${APP_NAME:?APP_NAME must be set}"

mkdir -p \
  "${HOME}/.local/share/docker" \
  "${HOME}/.local/state/docker" \
  "${HOME}/.cache/docker" \
  "${HOME}/.config/docker" \
  "${HOME}/.local/state/docker/postgresql" \
  "${HOME}/.local/state/docker/postgresql/${APP_NAME}"

chmod 755 \
  "${HOME}/.local/share/docker" \
  "${HOME}/.local/state/docker" \
  "${HOME}/.cache/docker" \
  "${HOME}/.config/docker" \
  "${HOME}/.local/state/docker/postgresql" \
  "${HOME}/.local/state/docker/postgresql/${APP_NAME}"

echo "Initialized Docker directories for ${APP_NAME}"
