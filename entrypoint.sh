#!/bin/sh

if [ ! -f /app/config.toml ] || [ -d /app/config.toml ]; then
  rm -rf /app/config.toml
  cp /app/config_sample.toml /app/config.toml

  if [ -n "$PLEX_URL" ]; then
    sed -i "s|plex_url = .*|plex_url = \"$PLEX_URL\"|" /app/config.toml
  fi
  if [ -n "$PLEX_TOKEN" ]; then
    sed -i "s|plex_token = .*|plex_token = \"$PLEX_TOKEN\"|" /app/config.toml
  fi
  if [ -n "$PLEX_LIBRARIES" ]; then
    sed -i "s|libraries = .*|libraries = $PLEX_LIBRARIES|" /app/config.toml
  fi
fi

if [ "$SCAN_ON_STARTUP" = "true" ]; then
  python3 /app/plex-hide-spoilers.py --quiet
fi

exec "$@"
