# 7 Days to Die egg

Aetheris egg for **7 Days to Die**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/7dtd:latest`
- **Default port**: 26900
- **Stop command**: `saveworld`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `HOSTNAME` | Server name shown in the server browser. | `Aetheris 7 Days to Die` |
| `SERVER_PORT` | Game port (UDP). | `26900` |
| `TELNET_PORT` | Telnet administration port. | `8081` |
| `TELNET_PASSWORD` | Telnet administration password. | `changeme` |
| `MAX_PLAYERS` | Maximum number of concurrent players. | `16` |
| `SERVER_PASSWORD` | Password required to join (leave empty for a public server). | `` |
| `GAME_WORLD` | World name or RWG seed. | `Navezgane` |

## Install

```bash
php artisan p:egg:import 7dtd/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/7dtd:latest images/7dtd
```
