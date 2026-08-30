FROM --platform=linux/amd64 ubuntu:22.04

RUN apt update && apt install -y openssh-server python3 python3-flask && rm -rf /var/lib/apt/lists/*

# Konfigurasi agar SSH mengizinkan login root via password
RUN mkdir -p /var/run/sshd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config

WORKDIR /app
COPY hcr-server /app/hcr-server
COPY entrypoint.sh /app/entrypoint.sh
COPY web_ui.py /app/web_ui.py

RUN chmod +x /app/hcr-server /app/entrypoint.sh

EXPOSE 8080 8081 22

CMD ["/app/entrypoint.sh"]
