#!/usr/bin/env bash
set -e

# Update password SSH dari Environment Variable saat container start
echo "${SSH_USER}:${SSH_PASS}" | chpasswd

# Buat host key SSH jika belum ada
ssh-keygen -A >/dev/null 2>&1

# Jalankan SSH Daemon di background (port 22 internal)
echo "[+] Starting SSH daemon..."
/usr/sbin/sshd

# Parameter tuning
LISTEN_PORT="${PORT:-8880}"
TRANSPORT_MODE="${TRANSPORT:-plain}"
MAX_FRAME="${MAX_DOWNLOAD_FRAME:-1024}"
POLL_TIMEOUT="${DOWNLOAD_POLL_TIMEOUT:-10s}"

echo "[+] Starting HCR Server on :${LISTEN_PORT} (Transport: ${TRANSPORT_MODE})..."
exec /app/hcr-server \
  --listen ":${LISTEN_PORT}" \
  --target "127.0.0.1:22" \
  --transport "${TRANSPORT_MODE}" \
  --max-download-frame "${MAX_FRAME}" \
  --download-poll-timeout "${POLL_TIMEOUT}"
