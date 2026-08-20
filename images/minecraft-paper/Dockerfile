# Aetheris Minecraft Paper runtime image.
# Published as ghcr.io/aetheris-project/minecraft-paper:latest
FROM eclipse-temurin:21-jre-jammy

ENV DEBIAN_FRONTEND=noninteractive \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -d /home/container container

USER container
WORKDIR /home/container

EXPOSE 25565

CMD ["bash"]
