#!/bin/bash
set -e

# Setup Password SSH
SSH_PASS=${SSH_PASS:-"PasswordHCR123"}
echo "root:${SSH_PASS}" | chpasswd
mkdir -p /var/run/sshd
/usr/sbin/sshd

echo "Starting Web Control Panel on port 8081..."
exec python3 /app/web_ui.py
