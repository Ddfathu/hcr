#!/bin/bash
set -e

SSH_PASS=${SSH_PASS:-"PasswordHCR123"}
echo "root:${SSH_PASS}" | chpasswd
mkdir -p /var/run/sshd
/usr/sbin/sshd

# Jalankan Cloudflare Zero Trust jika CF_TOKEN diisi di Railway
if [ -n "$CF_TOKEN" ]; then
    echo "Starting Cloudflare Zero Trust Tunnel..."
    cloudflared tunnel --no-autoupdate run --token "$CF_TOKEN" &
fi

echo "Starting Web Control Panel on port 8081..."
exec python3 /app/web_ui.py
