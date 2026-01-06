FROM debian:12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN wget -O tonutils-reverse-proxy \
    https://github.com/tonutils/reverse-proxy/releases/latest/download/tonutils-reverse-proxy-linux-amd64 \
    && chmod +x tonutils-reverse-proxy

EXPOSE 80

ENTRYPOINT ["./tonutils-reverse-proxy", "--domain", "quantumforge.ton", "-allow-insecure-https"]
