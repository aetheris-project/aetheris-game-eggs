#!/usr/bin/env python3
"""Declarative generator for the Aetheris game egg catalog.

Each entry in GAMES produces, under `eggs/<slug>/`:

- `egg.json` - the Pterodactyl PTDL_v2 manifest (with embedded install script)
- `README.md` - game-specific quick start and variable reference
- `images/<slug>/Dockerfile` - the runtime container image

Run from the repository root:

    python tools/generate_eggs.py

The output is deterministic: re-running the generator over an entry rewrites
its files in place, so the generated catalog stays in sync with this file.
"""

from __future__ import annotations

import json
import pathlib
import textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPORTED_AT = "2026-08-20T00:00:00+00:00"
STEAMCMD_TARBALL = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"

STEAM_INSTALL_TEMPLATE = """\
# @author Aetheris Project
# @description {game} dedicated server install via SteamCMD
# @user-alpine

apt-get update -y
apt-get install -y curl tar

mkdir -p /home/container/steamcmd
cd /home/container

curl -sSL {tarball} | tar -xz -C steamcmd
./steamcmd/steamcmd.sh +force_install_dir /home/container +login anonymous +app_update {appid} {beta}validate +quit
{post}
"""

# --------------------------------------------------------------------------- #
# Common variable blocks
# --------------------------------------------------------------------------- #

def var(name: str, env: str, default: str, rules: str, description: str) -> dict:
    return {
        "name": name,
        "description": description,
        "env_variable": env,
        "default_value": default,
        "user_viewable": True,
        "user_editable": True,
        "rules": rules,
    }


def hostname_var(default: str) -> dict:
    return var("Hostname", "HOSTNAME", default, "required|string|max:64",
               "Server name shown in the server browser.")


def port_var(default: str, description: str = "Game port.") -> dict:
    return var("Server Port", "SERVER_PORT", default, "required|integer|min:1|max:65535", description)


def query_port_var(default: str) -> dict:
    return var("Query Port", "QUERY_PORT", default, "required|integer|min:1|max:65535",
               "Source query port used by the server browser.")


def rcon_var() -> dict:
    return var("RCON Password", "RCON_PASSWORD", "changeme", "string|max:64",
               "RCON password for remote administration.")


def password_var() -> dict:
    return var("Server Password", "SERVER_PASSWORD", "", "string|max:64",
               "Password required to join (leave empty for a public server).")


def max_players_var(default: str = "16") -> dict:
    return var("Max Players", "MAX_PLAYERS", default, "required|integer|min:1|max:500",
               "Maximum number of concurrent players.")


def tickrate_var() -> dict:
    return var("Tickrate", "TICKRATE", "64", "required|integer|min:10|max:128",
               "Server simulation tick rate.")


def game_port_var(default: str, description: str = "Game port (TCP).") -> dict:
    return var("Game Port", "GAME_PORT", default, "required|integer|min:1|max:65535", description)


# --------------------------------------------------------------------------- #
# Install scripts
# --------------------------------------------------------------------------- #

def steam_install(game: str, appid: str, beta: str = "", post: str = "") -> str:
    return STEAM_INSTALL_TEMPLATE.format(
        game=game,
        appid=appid,
        beta=f"-beta {beta} " if beta else "",
        post=post.strip("\n"),
        tarball=STEAMCMD_TARBALL,
    ).rstrip() + "\n"


def forge_install() -> str:
    return textwrap.dedent("""\
        # @author Aetheris Project
        # @description Minecraft Forge server install with version resolution
        # @user-alpine

        apt-get update -y
        apt-get install -y curl jq

        cd /home/container

        # Resolve the latest Forge version for the requested Minecraft version.
        MC=${MC_VERSION:-latest}
        FORGE_VERSION=$(curl -s "https://meta.forgecdn.net/minecraft/versions.json" | jq -r --arg mc "$MC" '.versions[] | select(.id==$mc) | .latest.release' | head -1)
        if [ -z "$FORGE_VERSION" ] || [ "$FORGE_VERSION" = "null" ]; then
          echo "Could not resolve Forge for Minecraft $MC"
          exit 1
        fi
        MC_FINAL=$(curl -s "https://meta.forgecdn.net/minecraft/versions.json" | jq -r --arg mc "$MC" '.versions[] | select(.id==$mc) | .id' | head -1)

        # Download the installer and run it headless.
        curl -s -o forge-installer.jar "https://maven.minecraftforge.net/net/minecraftforge/forge/${MC_FINAL}-${FORGE_VERSION}/forge-${MC_FINAL}-${FORGE_VERSION}-installer.jar"
        java -jar forge-installer.jar --installServer
        rm -f forge-installer.jar

        # Forge leaves run.sh / libraries; move the server jar to the expected name.
        if [ -f "run.sh" ]; then
          mv run.sh "${SERVER_JARFILE:-server.jar}.sh" 2>/dev/null || true
        fi
        if [ -f "libraries" ] && [ -d "libraries" ]; then
          echo "Forge libraries present" > /dev/null
        fi

        # EULA
        echo "eula=${ACCEPT_EULA:-true}" > eula.txt
        if [ ! -f server.properties ]; then
          cat > server.properties <<EOF
        motd=${MOTD:-Aetheris Forge Server}
        max-players=${MAX_PLAYERS:-20}
        server-port=${SERVER_PORT:-25565}
        online-mode=${ONLINE_MODE:-true}
        EOF
        fi
        """).strip() + "\n"


def paper_install() -> str:
    return textwrap.dedent("""\
        # @author Aetheris Project
        # @description Paper server install via the PaperMC API
        # @user-alpine

        apt-get update -y
        apt-get install -y curl jq

        cd /home/container

        VERSION=${MC_VERSION:-latest}
        if [ "$VERSION" = "latest" ]; then
          VERSION=$(curl -s https://api.papermc.io/v2/projects/paper | jq -r '.versions[-1]')
        fi
        BUILD=$(curl -s "https://api.papermc.io/v2/projects/paper/versions/${VERSION}/builds" | jq -r '.builds[-1].build')
        curl -s -o "${SERVER_JARFILE:-server.jar}" "https://api.papermc.io/v2/projects/paper/versions/${VERSION}/builds/${BUILD}/downloads/paper-${VERSION}-${BUILD}.jar"

        # EULA
        echo "eula=${ACCEPT_EULA:-true}" > eula.txt
        if [ ! -f server.properties ]; then
          cat > server.properties <<EOF
        motd=${MOTD:-Aetheris Paper Server}
        max-players=${MAX_PLAYERS:-20}
        server-port=${SERVER_PORT:-25565}
        online-mode=${ONLINE_MODE:-true}
        EOF
        fi
        """).strip() + "\n"


def velocity_install() -> str:
    return textwrap.dedent("""\
        # @author Aetheris Project
        # @description Velocity proxy install
        # @user-alpine

        apt-get update -y
        apt-get install -y curl jq

        cd /home/container

        # Resolve the latest Velocity build.
        PROJECT=$(curl -s https://api.papermc.io/v2/projects/velocity | jq -r '.versions[-1]')
        BUILD=$(curl -s "https://api.papermc.io/v2/projects/velocity/versions/${PROJECT}/builds" | jq -r '.builds[-1].build')
        curl -s -o velocity.jar "https://api.papermc.io/v2/projects/velocity/versions/${PROJECT}/builds/${BUILD}/downloads/velocity-${PROJECT}-${BUILD}.jar"

        if [ ! -f velocity.toml ]; then
          cat > velocity.toml <<EOF
        bind = "0.0.0.0:${SERVER_PORT:-25577}"
        motd = "${MOTD:-Aetheris Network}"
        show-max-players = ${MAX_PLAYERS:-500}
        online-mode = ${ONLINE_MODE:-true}
        EOF
        fi
        """).strip() + "\n"


# --------------------------------------------------------------------------- #
# Egg templates
# --------------------------------------------------------------------------- #

def make_egg(slug: str, name: str, description: str, image: str, startup: str,
             done: str, stop: str, install_script: str, variables: list[dict],
             config_files: dict | None = None, logs: dict | None = None,
             features: list[str] | None = None, ports: list[str] | None = None) -> dict:
    features = features or ["pid_limit", "fs_write"]
    config = {
        "files": config_files or {},
        "startup": {"done": done, "userInteraction": []},
        "stop": stop,
        "logs": logs or {"custom": False, "location": "logs/latest.log"},
        "extends": None,
    }
    egg = {
        "_comment": f"Aetheris {name} egg - Pterodactyl-compatible (PTDL_v2).",
        "meta": {
            "version": "PTDL_v2",
            "update_url": f"https://raw.githubusercontent.com/aetheris-project/aetheris-game-eggs/main/eggs/{slug}/egg.json",
        },
        "exported_at": EXPORTED_AT,
        "name": name,
        "author": "aetheris-project",
        "description": description,
        "features": features,
        "docker_images": {image: f"SteamCMD - {name}" if "steam" in image else name},
        "file_denylist": [],
        "startup": startup,
        "config": config,
        "scripts": {
            "installation": {
                "script": install_script,
                "container": "ghcr.io/pterodactyl/installers:alpine",
                "entrypoint": "bash",
            }
        },
        "variables": variables,
    }
    return egg


# --------------------------------------------------------------------------- #
# Game catalog
# --------------------------------------------------------------------------- #

GAMES = [
    # --- Minecraft ecosystem -------------------------------------------------
    {
        "slug": "minecraft/forge",
        "name": "Minecraft Forge",
        "description": "Minecraft Java Edition with the Forge mod loader, automatic version resolution and memory presets.",
        "image": "ghcr.io/aetheris-project/minecraft-forge:latest",
        "ports": ["25565"],
        "startup": "java -Xms${MEMORY}M -Xmx${MEMORY}M -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -jar ${SERVER_JARFILE} nogui",
        "done": "Done (",
        "stop": "stop",
        "install": forge_install,
        "java": True,
        "variables": [
            var("Minecraft Version", "MC_VERSION", "latest", "required|string|max:16", "Minecraft version to install."),
            var("Server Jarfile", "SERVER_JARFILE", "server.jar", "required|string|max:64", "The jarfile to run."),
            var("Memory (MB)", "MEMORY", "4096", "required|integer|min:512|max:131072", "Memory allocated to the server in MB."),
            var("Accept EULA", "ACCEPT_EULA", "true", "required|boolean", "Accept the Minecraft EULA."),
            var("Max Players", "MAX_PLAYERS", "20", "required|integer|min:1|max:500", "Maximum concurrent players."),
            port_var("25565", "Minecraft server port."),
            var("Online Mode", "ONLINE_MODE", "true", "required|boolean", "Verify client identities with Mojang."),
            var("MOTD", "MOTD", "Aetheris Forge Server", "string|max:60", "Server description shown in the server list."),
        ],
    },
    {
        "slug": "minecraft/paper",
        "name": "Minecraft Paper",
        "description": "High-performance Minecraft Java server on the Paper fork, with automatic latest-version resolution.",
        "image": "ghcr.io/aetheris-project/minecraft-paper:latest",
        "ports": ["25565"],
        "startup": "java -Xms${MEMORY}M -Xmx${MEMORY}M -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -jar ${SERVER_JARFILE} nogui",
        "done": "Done (",
        "stop": "stop",
        "install": paper_install,
        "java": True,
        "variables": [
            var("Minecraft Version", "MC_VERSION", "latest", "required|string|max:16", "Minecraft version to install (latest or specific)."),
            var("Server Jarfile", "SERVER_JARFILE", "server.jar", "required|string|max:64", "The jarfile to run."),
            var("Memory (MB)", "MEMORY", "4096", "required|integer|min:512|max:131072", "Memory allocated to the server in MB."),
            var("Accept EULA", "ACCEPT_EULA", "true", "required|boolean", "Accept the Minecraft EULA."),
            var("Max Players", "MAX_PLAYERS", "20", "required|integer|min:1|max:500", "Maximum concurrent players."),
            port_var("25565", "Minecraft server port."),
            var("Online Mode", "ONLINE_MODE", "true", "required|boolean", "Verify client identities with Mojang."),
            var("MOTD", "MOTD", "Aetheris Paper Server", "string|max:60", "Server description shown in the server list."),
        ],
    },
    {
        "slug": "minecraft/velocity",
        "name": "Velocity Proxy",
        "description": "Modern, high-performance Minecraft proxy for networks of servers with forwarding, plugins and built-in MOTD.",
        "image": "ghcr.io/aetheris-project/minecraft-velocity:latest",
        "ports": ["25577"],
        "startup": "java -Xms${MEMORY}M -Xmx${MEMORY}M -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -jar velocity.jar",
        "done": "Done (",
        "stop": "end",
        "install": velocity_install,
        "java": True,
        "variables": [
            var("Memory (MB)", "MEMORY", "1024", "required|integer|min:256|max:65536", "Memory allocated to the proxy in MB."),
            port_var("25577", "Proxy listener port."),
            var("Max Players", "MAX_PLAYERS", "500", "required|integer|min:1|max:5000", "Maximum concurrent players across the network."),
            var("Online Mode", "ONLINE_MODE", "true", "required|boolean", "Verify client identities with Mojang."),
            var("MOTD", "MOTD", "Aetheris Network", "string|max:60", "Proxy MOTD shown in the server list."),
        ],
    },
    # --- Steam games ---------------------------------------------------------
    {
        "slug": "7dtd",
        "name": "7 Days to Die",
        "description": "7 Days to Die dedicated server: survival sandbox with horde nights, RWG worlds and full modding support.",
        "image": "ghcr.io/aetheris-project/7dtd:latest",
        "ports": ["26900"],
        "startup": "./7DaysToDieServer.x86_64 -configfile=serverconfig.xml -quit -batchmode -nographics -dedicated -ServerPort=${SERVER_PORT} -ServerName=\"${HOSTNAME}\" -ServerMaxPlayerCount=${MAX_PLAYERS} -ServerPassword=\"${SERVER_PASSWORD}\" -TelnetPort=${TELNET_PORT} -TelnetPassword=\"${TELNET_PASSWORD}\"",
        "done": "GameServer.Started",
        "stop": "saveworld",
        "install": lambda: steam_install("7 Days to Die", "294420", beta="latest_experimental",
            post="""# Default server configuration (minimal)
cat > serverconfig.xml <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<ServerSettings>
  <property name="ServerName" value="Aetheris 7 Days to Die"/>
  <property name="ServerPort" value="26900"/>
  <property name="ServerMaxPlayerCount" value="16"/>
  <property name="ServerPassword" value=""/>
  <property name="GameMode" value="GameModeSurvival"/>
  <property name="GameWorld" value="Navezgane"/>
  <property name="TelnetPort" value="8081"/>
  <property name="TelnetPassword" value=""/>
</ServerSettings>
EOF"""),
        "variables": [
            hostname_var("Aetheris 7 Days to Die"),
            port_var("26900", "Game port (UDP)."),
            var("Telnet Port", "TELNET_PORT", "8081", "required|integer|min:1|max:65535", "Telnet administration port."),
            var("Telnet Password", "TELNET_PASSWORD", "changeme", "string|max:64", "Telnet administration password."),
            max_players_var("16"),
            password_var(),
            var("Game World", "GAME_WORLD", "Navezgane", "required|string|max:64", "World name or RWG seed."),
        ],
    },
    {
        "slug": "vrising",
        "name": "V Rising",
        "description": "V Rising dedicated server: open-world vampire survival with castle building, clans and PvP or PvE rulesets.",
        "image": "ghcr.io/aetheris-project/vrising:latest",
        "ports": ["9874"],
        "startup": "./VRisingServer -serverName \"${HOSTNAME}\" -serverPort ${SERVER_PORT} -gamePort ${GAME_PORT} -queryPort ${QUERY_PORT} -maxUsers ${MAX_PLAYERS} -password \"${SERVER_PASSWORD}\" -secure ${SECURE} -persistentDataPath ./save-data -logFile ./logs/VRisingServer.log",
        "done": "Started MasterServer",
        "stop": "quit",
        "install": lambda: steam_install("V Rising", "1829350",
            post="""mkdir -p /home/container/save-data /home/container/logs"""),
        "variables": [
            hostname_var("Aetheris V Rising"),
            var("Server Port", "SERVER_PORT", "9874", "required|integer|min:1|max:65535", "Primary server port (UDP/TCP)."),
            game_port_var("9875", "Game port (UDP)."),
            query_port_var("9876"),
            max_players_var("40"),
            password_var(),
            var("Secure Mode", "SECURE", "true", "required|boolean", "Require secure connections."),
        ],
    },
    {
        "slug": "enshrouded",
        "name": "Enshrouded",
        "description": "Enshrouded dedicated server: co-op survival action RPG with base building, shroud exploration and bosses.",
        "image": "ghcr.io/aetheris-project/enshrouded:latest",
        "ports": ["15636"],
        "startup": "./enshrouded_server \"--name=${HOSTNAME}\" \"--port=${SERVER_PORT}\" \"--query-port=${QUERY_PORT}\" \"--slot-count=${MAX_PLAYERS}\" --log-file /home/container/logs/enshrouded.log",
        "done": "enshrouded server started",
        "stop": "CTRL_C",
        "install": lambda: steam_install("Enshrouded", "2278520",
            post="""mkdir -p /home/container/logs"""),
        "variables": [
            hostname_var("Aetheris Enshrouded"),
            port_var("15636", "Game port (UDP)."),
            query_port_var("15637"),
            max_players_var("16"),
        ],
    },
    {
        "slug": "dst",
        "name": "Don't Starve Together",
        "description": "Don't Starve Together dedicated shard: wilderness survival with seasons, caves and mods.",
        "image": "ghcr.io/aetheris-project/dst:latest",
        "ports": ["10999"],
        "startup": "./dontstarve_dedicated_server_nullrenderer -console -cluster ${CLUSTER_NAME} -shard ${SHARD_NAME}",
        "done": "Sim paused",
        "stop": "c_shutdown()",
        "install": lambda: steam_install("Don't Starve Together", "343946",
            post="""# DST requires a cluster directory layout under ~/.klei/DoNotStarveTogether
mkdir -p /home/container/.klei/DoNotStarveTogether/${CLUSTER_NAME:-AetherisCluster}/Master
cat > /home/container/.klei/DoNotStarveTogether/${CLUSTER_NAME:-AetherisCluster}/cluster.ini <<'EOF'
[NETWORK]
cluster_name = Aetheris DST
cluster_description = Aetheris hosted server
cluster_password =
[GAMEPLAY]
max_players = 16
pvp = false
[SHARD]
shard_enabled = true
shard_selection = master
EOF"""),
        "variables": [
            var("Cluster Name", "CLUSTER_NAME", "AetherisCluster", "required|string|max:32", "Cluster directory name."),
            var("Shard Name", "SHARD_NAME", "Master", "required|string|max:32", "Shard to run (Master or Caves)."),
            var("Max Players", "MAX_PLAYERS", "16", "required|integer|min:1|max:64", "Maximum concurrent players."),
            password_var(),
        ],
    },
    {
        "slug": "vintage-story",
        "name": "Vintage Story",
        "description": "Vintage Story dedicated server: deep survival sandbox with realistic crafting, seasons and mods.",
        "image": "ghcr.io/aetheris-project/vintage-story:latest",
        "ports": ["42420"],
        "startup": "dotnet VintagestoryServer.dll --dataPath /home/container/data --port ${SERVER_PORT} --maxPlayers ${MAX_PLAYERS} --password \"${SERVER_PASSWORD}\"",
        "done": "Server started",
        "stop": "stop",
        "install": lambda: textwrap.dedent("""\
            # @author Aetheris Project
            # @description Vintage Story server install
            # @user-alpine

            apt-get update -y
            apt-get install -y curl unzip

            cd /home/container
            VERSION=${VS_VERSION:-latest}
            # Vintage Story publishes versioned linux server archives.
            if [ "$VERSION" = "latest" ]; then
              VERSION=$(curl -s https://api.vintagestory.at/lateststable.txt | tr -d '\\r' | tr -d '\\n')
            fi
            curl -s -o vs.zip "https://cdn.vintagestory.at/gamefiles/stable/vs_server_linux-x64_${VERSION}.tar.gz" || \\
              curl -s -o vs.tar.gz "https://cdn.vintagestory.at/gamefiles/stable/vs_server_linux-x64_${VERSION}.tar.gz"
            if [ -f vs.zip ]; then unzip -q vs.zip; rm vs.zip; fi
            if [ -f vs.tar.gz ]; then tar -xzf vs.tar.gz; rm vs.tar.gz; fi
            chmod +x VintagestoryServer.dll 2>/dev/null || true
            mkdir -p data
            """).strip() + "\n",
        "variables": [
            var("Vintage Story Version", "VS_VERSION", "latest", "required|string|max:16", "Server version to install."),
            port_var("42420", "Game port (TCP/UDP)."),
            max_players_var("16"),
            password_var(),
        ],
    },
    {
        "slug": "scpsl",
        "name": "SCP: Secret Laboratory",
        "description": "SCP: Secret Laboratory dedicated server: multiplayer horror with round-based gameplay and configurable roles.",
        "image": "ghcr.io/aetheris-project/scpsl:latest",
        "ports": ["7777"],
        "startup": "./LocalAdmin ${SERVER_PORT} -- --port ${SERVER_PORT} --config config_gameplay.txt",
        "done": "Waiting for players",
        "stop": "STOP",
        "install": lambda: steam_install("SCP Secret Laboratory", "996560"),
        "variables": [
            port_var("7777", "Game port."),
            max_players_var("24"),
            password_var(),
            var("Tickrate", "TICKRATE", "60", "required|integer|min:10|max:128", "Server tick rate."),
        ],
    },
    {
        "slug": "tf2",
        "name": "Team Fortress 2",
        "description": "Team Fortress 2 dedicated server via Source dedicated server: class-based multiplayer with community mods.",
        "image": "ghcr.io/aetheris-project/tf2:latest",
        "ports": ["27015"],
        "startup": "./srcds_run -game tf -console -port ${SERVER_PORT} +sv_password \"${SERVER_PASSWORD}\" +map ${DEFAULT_MAP} +maxplayers ${MAX_PLAYERS} +hostname \"${HOSTNAME}\" +rcon_password \"${RCON_PASSWORD}\" +sv_lan 0 -tickrate ${TICKRATE}",
        "done": "Connection to Steam servers successful",
        "stop": "quit",
        "install": lambda: steam_install("Team Fortress 2", "232250"),
        "variables": [
            hostname_var("Aetheris TF2"),
            port_var("27015", "Game port (UDP/TCP)."),
            query_port_var("27015"),
            max_players_var("24"),
            password_var(),
            rcon_var(),
            tickrate_var(),
            var("Default Map", "DEFAULT_MAP", "cp_dustbowl", "required|string|max:64", "Map loaded on first start."),
        ],
    },
    {
        "slug": "l4d2",
        "name": "Left 4 Dead 2",
        "description": "Left 4 Dead 2 dedicated server via Source dedicated server: co-op zombie survival with campaigns and mutations.",
        "image": "ghcr.io/aetheris-project/l4d2:latest",
        "ports": ["27015"],
        "startup": "./srcds_run -game left4dead2 -console -port ${SERVER_PORT} +sv_password \"${SERVER_PASSWORD}\" +map ${DEFAULT_MAP} +maxplayers ${MAX_PLAYERS} +hostname \"${HOSTNAME}\" +rcon_password \"${RCON_PASSWORD}\" +sv_lan 0 -tickrate ${TICKRATE}",
        "done": "Connection to Steam servers successful",
        "stop": "quit",
        "install": lambda: steam_install("Left 4 Dead 2", "222860"),
        "variables": [
            hostname_var("Aetheris L4D2"),
            port_var("27015", "Game port (UDP/TCP)."),
            query_port_var("27015"),
            max_players_var("8"),
            password_var(),
            rcon_var(),
            tickrate_var(),
            var("Default Map", "DEFAULT_MAP", "c1m1_hotel", "required|string|max:64", "Campaign map loaded on first start."),
        ],
    },
    {
        "slug": "conan-exiles",
        "name": "Conan Exiles",
        "description": "Conan Exiles dedicated server: open-world survival with base building, thralls and PvP or PvE conflicts.",
        "image": "ghcr.io/aetheris-project/conan-exiles:latest",
        "ports": ["7777"],
        "startup": "./ConanSandboxServer -log -Port=${SERVER_PORT} -QueryPort=${QUERY_PORT} -RconPort=${RCON_PORT} -RconPassword=\"${RCON_PASSWORD}\" -ServerName=\"${HOSTNAME}\" -MaxPlayers=${MAX_PLAYERS} -ServerPassword=\"${SERVER_PASSWORD}\"",
        "done": "Server started",
        "stop": "quit",
        "install": lambda: steam_install("Conan Exiles", "443030"),
        "variables": [
            hostname_var("Aetheris Conan Exiles"),
            port_var("7777", "Game port (UDP)."),
            query_port_var("27015"),
            var("RCON Port", "RCON_PORT", "25575", "required|integer|min:1|max:65535", "RCON administration port."),
            rcon_var(),
            max_players_var("40"),
            password_var(),
        ],
    },
    {
        "slug": "space-engineers",
        "name": "Space Engineers",
        "description": "Space Engineers dedicated server: voxel-based sandbox with ship building, planets and multiplayer survival.",
        "image": "ghcr.io/aetheris-project/space-engineers:latest",
        "ports": ["27016"],
        "startup": "./DedicatedServer64/SpaceEngineersDedicated -port ${SERVER_PORT} -path ./data -ip 0.0.0.0 -fullScreen false",
        "done": "Server started",
        "stop": "quit",
        "install": lambda: steam_install("Space Engineers", "298740"),
        "variables": [
            port_var("27016", "Game port (UDP)."),
            max_players_var("16"),
            password_var(),
            var("World Name", "WORLD_NAME", "Aetheris World", "string|max:64", "World save name."),
        ],
    },
    {
        "slug": "starbound",
        "name": "Starbound",
        "description": "Starbound dedicated server: space exploration sandbox with planets, colonies and mods.",
        "image": "ghcr.io/aetheris-project/starbound:latest",
        "ports": ["21025"],
        "startup": "./starbound_server",
        "done": "Server started",
        "stop": "shutdown",
        "install": lambda: steam_install("Starbound", "211820",
            post="""chmod +x /home/container/linux64/starbound_server 2>/dev/null || true"""),
        "variables": [
            port_var("21025", "Game port (TCP)."),
            max_players_var("8"),
            password_var(),
        ],
    },
]


def dockerfile_for(game: dict) -> str:
    java = game.get("java", False)
    if java:
        return textwrap.dedent(f"""\
            # Aetheris {game['name']} runtime image.
            # Published as {game['image']}
            FROM eclipse-temurin:21-jre-jammy

            ENV DEBIAN_FRONTEND=noninteractive \\
                LC_ALL=C.UTF-8 \\
                LANG=C.UTF-8

            RUN apt-get update \\
                && apt-get install -y --no-install-recommends curl ca-certificates tzdata \\
                && rm -rf /var/lib/apt/lists/* \\
                && useradd -m -d /home/container container

            USER container
            WORKDIR /home/container

            EXPOSE {" ".join(game["ports"])}

            CMD ["bash"]
            """).strip() + "\n"
    return textwrap.dedent(f"""\
        # Aetheris {game['name']} runtime image (SteamCMD based).
        # Published as {game['image']}
        FROM debian:bookworm-slim

        ENV DEBIAN_FRONTEND=noninteractive \\
            LC_ALL=C.UTF-8 \\
            LANG=C.UTF-8

        RUN dpkg --add-architecture i386 \\
            && apt-get update \\
            && apt-get install -y --no-install-recommends \\
                curl ca-certificates tzdata lib32gcc-s1 lib32stdc++6 \\
            && rm -rf /var/lib/apt/lists/* \\
            && useradd -m -d /home/container container

        USER container
        WORKDIR /home/container

        EXPOSE {" ".join(game["ports"])}

        CMD ["bash"]
        """).strip() + "\n"


def readme_for(game: dict) -> str:
    slug = game["slug"]
    slug_path = slug.replace("/", "/")
    vars_md = "\n".join(
        f"| `{v['env_variable']}` | {v['description']} | `{v['default_value']}` |"
        for v in game["variables"]
    )
    return f"""# {game['name']} egg

Aetheris egg for **{game['name']}**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `{game['image']}`
- **Default port**: {", ".join(game["ports"])}
- **Stop command**: `{game["stop"]}`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
{vars_md}

## Install

```bash
php artisan p:egg:import {slug_path}/egg.json
```

## Runtime image

```bash
docker build -t {game['image']} images/{slug.replace('/', '-')}
```
"""


def main() -> None:
    generated = 0
    for game in GAMES:
        slug = game["slug"]
        egg = make_egg(
            slug=slug,
            name=game["name"],
            description=game["description"],
            image=game["image"],
            startup=game["startup"],
            done=game["done"],
            stop=game["stop"],
            install_script=game["install"](),
            variables=game["variables"],
            ports=game["ports"],
        )
        egg_dir = ROOT / "eggs" / slug
        egg_dir.mkdir(parents=True, exist_ok=True)
        (egg_dir / "egg.json").write_text(
            json.dumps(egg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        (egg_dir / "README.md").write_text(readme_for(game), encoding="utf-8")

        # Images live in flat, dash-separated directories (images/minecraft-java)
        # so the validator can pair every image with its Dockerfile.
        image_dir = ROOT / "images" / slug.replace("/", "-")
        image_dir.mkdir(parents=True, exist_ok=True)
        (image_dir / "Dockerfile").write_text(dockerfile_for(game), encoding="utf-8")

        generated += 1
        print(f"generated eggs/{slug}")

    print(f"\n{generated} eggs written")


if __name__ == "__main__":
    main()
