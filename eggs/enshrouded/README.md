# Enshrouded egg

Aetheris egg for **Enshrouded**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/enshrouded:latest`
- **Default port**: 15636
- **Stop command**: `CTRL_C`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `HOSTNAME` | Server name shown in the server browser. | `Aetheris Enshrouded` |
| `SERVER_PORT` | Game port (UDP). | `15636` |
| `QUERY_PORT` | Source query port used by the server browser. | `15637` |
| `MAX_PLAYERS` | Maximum number of concurrent players. | `16` |

## Install

```bash
php artisan p:egg:import enshrouded/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/enshrouded:latest images/enshrouded
```
