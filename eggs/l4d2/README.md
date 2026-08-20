# Left 4 Dead 2 egg

Aetheris egg for **Left 4 Dead 2**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/l4d2:latest`
- **Default port**: 27015
- **Stop command**: `quit`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `HOSTNAME` | Server name shown in the server browser. | `Aetheris L4D2` |
| `SERVER_PORT` | Game port (UDP/TCP). | `27015` |
| `QUERY_PORT` | Source query port used by the server browser. | `27015` |
| `MAX_PLAYERS` | Maximum number of concurrent players. | `8` |
| `SERVER_PASSWORD` | Password required to join (leave empty for a public server). | `` |
| `RCON_PASSWORD` | RCON password for remote administration. | `changeme` |
| `TICKRATE` | Server simulation tick rate. | `64` |
| `DEFAULT_MAP` | Campaign map loaded on first start. | `c1m1_hotel` |

## Install

```bash
php artisan p:egg:import l4d2/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/l4d2:latest images/l4d2
```
