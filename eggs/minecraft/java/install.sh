#!/bin/bash
# @author Aetheris Project
# @description Minecraft Java install script with version + build resolution
# Runs inside the Pterodactyl install container; idempotent.

set -euo pipefail

apt-get update -y
apt-get install -y curl unzip jq

SERVER_JARFILE="${SERVER_JARFILE:-server.jar}"

case "${SERVER_TYPE:-paper}" in
  vanilla)
    MANIFEST="$(curl -fsSL https://launchermeta.mojang.com/mc/game/version_manifest_v2.json)"
    if [ -z "${MC_VERSION:-}" ] || [ "${MC_VERSION}" = "latest" ]; then
      MC_VERSION="$(echo "${MANIFEST}" | jq -r .latest.release)"
    fi
    VERSION_URL="$(echo "${MANIFEST}" | jq -r --arg v "${MC_VERSION}" '.versions[] | select(.id==$v) | .url')"
    SERVER_URL="$(curl -fsSL "${VERSION_URL}" | jq -r .downloads.server.url)"
    echo "Downloading vanilla ${MC_VERSION}..."
    curl -fsSL -o "${SERVER_JARFILE}" "${SERVER_URL}"
    ;;
  paper)
    VERSION="${MC_VERSION:-latest}"
    [ "${VERSION}" = "latest" ] && VERSION="$(curl -fsSL https://api.papermc.io/v2/projects/paper | jq -r '.versions[-1]')"
    BUILD="$(curl -fsSL "https://api.papermc.io/v2/projects/paper/versions/${VERSION}/builds" | jq -r '.builds[-1].build')"
    echo "Downloading Paper ${VERSION} build ${BUILD}..."
    curl -fsSL -o "${SERVER_JARFILE}" "https://api.papermc.io/v2/projects/paper/versions/${VERSION}/builds/${BUILD}/downloads/paper-${VERSION}-${BUILD}.jar"
    ;;
  purpur)
    VERSION="${MC_VERSION:-latest}"
    echo "Downloading Purpur ${VERSION}..."
    curl -fsSL -o "${SERVER_JARFILE}" "https://api.purpurmc.org/v2/purpur/${VERSION}/latest/download"
    ;;
  fabric)
    VERSION="${MC_VERSION:-latest}"
    LOADER="$(curl -fsSL https://meta.fabricmc.net/v2/versions/loader | jq -r '.[0].loader.version')"
    INSTALLER="$(curl -fsSL https://meta.fabricmc.net/v2/versions/installer | jq -r '.[0].version')"
    echo "Downloading Fabric ${VERSION} loader ${LOADER}..."
    curl -fsSL -o fabric-installer.jar "https://meta.fabricmc.net/v2/versions/loader/${VERSION}/${LOADER}/${INSTALLER}/server/jar"
    java -jar fabric-installer.jar server -mcversion "${VERSION}" -loader "${LOADER}" -downloadMinecraft
    mv server.jar "${SERVER_JARFILE}"
    rm -f fabric-installer.jar
    ;;
  *)
    echo "Unknown server type: ${SERVER_TYPE}. Supported: vanilla, paper, purpur, fabric." >&2
    exit 1
    ;;
esac

chmod +x "${SERVER_JARFILE}"

if [ "${ACCEPT_EULA:-1}" = "1" ]; then
  echo "eula=true" > eula.txt
else
  echo "eula=false" > eula.txt
fi

if [ ! -f server.properties ]; then
  cat > server.properties <<EOF
motd=${MOTD:-Aetheris Minecraft Server}
max-players=${MAX_PLAYERS:-20}
server-port=${SERVER_PORT:-25565}
online-mode=${ONLINE_MODE:-true}
EOF
fi

echo "Install complete. Server jar: ${SERVER_JARFILE}"
