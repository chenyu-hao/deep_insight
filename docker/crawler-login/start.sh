#!/bin/sh
set -eu

DISPLAY_NUM="${DISPLAY_NUM:-99}"
DISPLAY=":${DISPLAY_NUM}"
SCREEN_WIDTH="${SCREEN_WIDTH:-1440}"
SCREEN_HEIGHT="${SCREEN_HEIGHT:-900}"
SCREEN_DEPTH="${SCREEN_DEPTH:-24}"
VNC_PORT="${VNC_PORT:-5900}"
NOVNC_PORT="${NOVNC_PORT:-6080}"
LOGIN_PLATFORM="${LOGIN_PLATFORM:-xhs}"
USER_DATA_ROOT="${USER_DATA_ROOT:-/app/browser_data}"
COOKIE_FILE_PATH="${COOKIE_FILE_PATH:-/app/runtime/cookies.json}"

case "${LOGIN_PLATFORM}" in
  xhs)
    LOGIN_URL="${LOGIN_URL:-https://www.xiaohongshu.com/explore}"
    ;;
  dy)
    LOGIN_URL="${LOGIN_URL:-https://www.douyin.com/}"
    ;;
  ks)
    LOGIN_URL="${LOGIN_URL:-https://www.kuaishou.com/}"
    ;;
  wb)
    LOGIN_URL="${LOGIN_URL:-https://weibo.com/}"
    ;;
  bili)
    LOGIN_URL="${LOGIN_URL:-https://www.bilibili.com/}"
    ;;
  tieba)
    LOGIN_URL="${LOGIN_URL:-https://tieba.baidu.com/}"
    ;;
  zhihu)
    LOGIN_URL="${LOGIN_URL:-https://www.zhihu.com/}"
    ;;
  *)
    echo "[login] Unsupported LOGIN_PLATFORM: ${LOGIN_PLATFORM}" >&2
    exit 1
    ;;
esac

USER_DATA_DIR="${USER_DATA_ROOT}/${LOGIN_PLATFORM}_user_data_dir"
mkdir -p "${USER_DATA_DIR}" "$(dirname "${COOKIE_FILE_PATH}")"

if [ ! -f "${COOKIE_FILE_PATH}" ]; then
  printf '{}\n' > "${COOKIE_FILE_PATH}"
fi

echo "[login] Platform: ${LOGIN_PLATFORM}"
echo "[login] URL: ${LOGIN_URL}"
echo "[login] User data dir: ${USER_DATA_DIR}"
echo "[login] noVNC: http://localhost:${NOVNC_PORT}/vnc.html"

Xvfb "${DISPLAY}" -screen 0 "${SCREEN_WIDTH}x${SCREEN_HEIGHT}x${SCREEN_DEPTH}" &
XVFB_PID=$!

export DISPLAY
fluxbox >/tmp/fluxbox.log 2>&1 &
FLUXBOX_PID=$!

x11vnc -display "${DISPLAY}" -rfbport "${VNC_PORT}" -forever -shared -nopw >/tmp/x11vnc.log 2>&1 &
X11VNC_PID=$!

websockify --web=/usr/share/novnc/ "${NOVNC_PORT}" "localhost:${VNC_PORT}" >/tmp/novnc.log 2>&1 &
WEBSOCKIFY_PID=$!

cleanup() {
  kill "${WEBSOCKIFY_PID}" "${X11VNC_PID}" "${FLUXBOX_PID}" "${XVFB_PID}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

sleep 2

chromium \
  --display="${DISPLAY}" \
  --no-sandbox \
  --disable-dev-shm-usage \
  --disable-gpu \
  --password-store=basic \
  --user-data-dir="${USER_DATA_DIR}" \
  --new-window \
  "${LOGIN_URL}" >/tmp/chromium.log 2>&1 &

wait "${WEBSOCKIFY_PID}"
