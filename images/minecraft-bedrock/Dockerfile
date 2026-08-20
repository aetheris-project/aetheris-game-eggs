# Aetheris runtime image - generated from the shared SteamCMD pattern.
# Published as ghcr.io/aetheris-project/minecraft-bedrock:latest
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        curl ca-certificates tzdata lib32gcc-s1 lib32stdc++6 \
        libcurl4-gnutls-dev \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -d /home/container container

USER container
WORKDIR /home/container

CMD ["bash"]
