FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    ca-certificates \
    chromium \
    fluxbox \
    novnc \
    websockify \
    x11vnc \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY docker/crawler-login/start.sh /usr/local/bin/start-crawler-login
RUN chmod +x /usr/local/bin/start-crawler-login

EXPOSE 5900 6080

CMD ["/usr/local/bin/start-crawler-login"]
