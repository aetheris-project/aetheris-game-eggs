# Starbound egg

Aetheris egg for **Starbound**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/starbound:latest`
- **Default port**: 21025
- **Stop command**: `shutdown`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `SERVER_PORT` | Game port (TCP). | `21025` |
| `MAX_PLAYERS` | Maximum number of concurrent players. | `8` |
| `SERVER_PASSWORD` | Password required to join (leave empty for a public server). | `` |

## Install

```bash
php artisan p:egg:import starbound/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/starbound:latest images/starbound
```
