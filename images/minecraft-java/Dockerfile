# Aetheris Minecraft Java runtime image.
# Published as ghcr.io/aetheris-project/minecraft-java:latest
FROM eclipse-temurin:21-jre-jammy

ENV DEBIAN_FRONTEND=noninteractive \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl ca-certificates tzdata bash \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -d /home/container container

USER container
WORKDIR /home/container

EXPOSE 25565/tcp

CMD ["bash"]
