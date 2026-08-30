FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install OpenSSH Server dan dependencies esensial
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Siapkan direktori kerja dan sshd
RUN mkdir -p /var/run/sshd /app

# Environment Variables Default (Bisa di-override di Railway Dashboard)
ENV SSH_USER=root
ENV SSH_PASS=PasswordHCR123
ENV PORT=8880
ENV TRANSPORT=plain
ENV MAX_DOWNLOAD_FRAME=1024
ENV DOWNLOAD_POLL_TIMEOUT=10s

# Konfigurasi SSH Daemon
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

WORKDIR /app

# Salin binary hcr-server dan entrypoint
COPY hcr-server /app/hcr-server
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/hcr-server /app/entrypoint.sh

EXPOSE 8880 22

ENTRYPOINT ["/app/entrypoint.sh"]
