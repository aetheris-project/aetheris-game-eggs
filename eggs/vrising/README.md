# V Rising egg

Aetheris egg for **V Rising**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/vrising:latest`
- **Default port**: 9874
- **Stop command**: `quit`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `HOSTNAME` | Server name shown in the server browser. | `Aetheris V Rising` |
| `SERVER_PORT` | Primary server port (UDP/TCP). | `9874` |
| `GAME_PORT` | Game port (UDP). | `9875` |
| `QUERY_PORT` | Source query port used by the server browser. | `9876` |
| `MAX_PLAYERS` | Maximum number of concurrent players. | `40` |
| `SERVER_PASSWORD` | Password required to join (leave empty for a public server). | `` |
| `SECURE` | Require secure connections. | `true` |

## Install

```bash
php artisan p:egg:import vrising/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/vrising:latest images/vrising
```
