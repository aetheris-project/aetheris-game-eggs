# Minecraft Paper egg

Aetheris egg for **Minecraft Paper**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/minecraft-paper:latest`
- **Default port**: 25565
- **Stop command**: `stop`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `MC_VERSION` | Minecraft version to install (latest or specific). | `latest` |
| `SERVER_JARFILE` | The jarfile to run. | `server.jar` |
| `MEMORY` | Memory allocated to the server in MB. | `4096` |
| `ACCEPT_EULA` | Accept the Minecraft EULA. | `true` |
| `MAX_PLAYERS` | Maximum concurrent players. | `20` |
| `SERVER_PORT` | Minecraft server port. | `25565` |
| `ONLINE_MODE` | Verify client identities with Mojang. | `true` |
| `MOTD` | Server description shown in the server list. | `Aetheris Paper Server` |

## Install

```bash
php artisan p:egg:import minecraft/paper/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/minecraft-paper:latest images/minecraft-paper
```
