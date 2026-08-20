# Team Fortress 2 egg

Aetheris egg for **Team Fortress 2**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/tf2:latest`
- **Default port**: 27015
- **Stop command**: `quit`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `HOSTNAME` | Server name shown in the server browser. | `Aetheris TF2` |
| `SERVER_PORT` | Game port (UDP/TCP). | `27015` |
| `QUERY_PORT` | Source query port used by the server browser. | `27015` |
| `MAX_PLAYERS` | Maximum number of concurrent players. | `24` |
| `SERVER_PASSWORD` | Password required to join (leave empty for a public server). | `` |
| `RCON_PASSWORD` | RCON password for remote administration. | `changeme` |
| `TICKRATE` | Server simulation tick rate. | `64` |
| `DEFAULT_MAP` | Map loaded on first start. | `cp_dustbowl` |

## Install

```bash
php artisan p:egg:import tf2/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/tf2:latest images/tf2
```
