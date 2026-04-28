#!/usr/bin/env bash
set -euo pipefail

platform="${1:-xhs}"

case "${platform}" in
  xhs|dy|ks|wb|bili|tieba|zhihu)
    ;;
  *)
    echo "Unsupported platform: ${platform}" >&2
    echo "Usage: $0 [xhs|dy|ks|wb|bili|tieba|zhihu]" >&2
    exit 1
    ;;
esac

mkdir -p browser_data runtime

if [[ ! -f runtime/cookies.json ]]; then
  printf '{}\n' > runtime/cookies.json
fi

echo "Starting crawler-login for platform: ${platform}"
LOGIN_PLATFORM="${platform}" docker compose --profile login up -d --build crawler-login

cat <<EOF

Open the browser desktop at:
  http://localhost:6080/vnc.html

After QR login succeeds:
  1. Close the crawler-login browser tab/window if you want
  2. Stop the login container:
     docker compose --profile login stop crawler-login
  3. Start or resume the main stack:
     docker compose up -d api mcp renderer

Shared state is persisted in:
  ./browser_data
  ./runtime/cookies.json
EOF
