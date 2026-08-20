# Velocity Proxy egg

Aetheris egg for **Velocity Proxy**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/minecraft-velocity:latest`
- **Default port**: 25577
- **Stop command**: `end`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `MEMORY` | Memory allocated to the proxy in MB. | `1024` |
| `SERVER_PORT` | Proxy listener port. | `25577` |
| `MAX_PLAYERS` | Maximum concurrent players across the network. | `500` |
| `ONLINE_MODE` | Verify client identities with Mojang. | `true` |
| `MOTD` | Proxy MOTD shown in the server list. | `Aetheris Network` |

## Install

```bash
php artisan p:egg:import minecraft/velocity/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/minecraft-velocity:latest images/minecraft-velocity
```
