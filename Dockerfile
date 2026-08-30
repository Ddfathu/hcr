FROM --platform=linux/amd64 ubuntu:22.04

RUN apt update && apt install -y openssh-server python3 python3-flask && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY hcr-server /app/hcr-server
COPY entrypoint.sh /app/entrypoint.sh
COPY web_ui.py /app/web_ui.py

RUN chmod +x /app/hcr-server /app/entrypoint.sh

EXPOSE 8080 8081 22

CMD ["/app/entrypoint.sh"]
