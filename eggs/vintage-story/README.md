# Vintage Story egg

Aetheris egg for **Vintage Story**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/vintage-story:latest`
- **Default port**: 42420
- **Stop command**: `stop`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `VS_VERSION` | Server version to install. | `latest` |
| `SERVER_PORT` | Game port (TCP/UDP). | `42420` |
| `MAX_PLAYERS` | Maximum number of concurrent players. | `16` |
| `SERVER_PASSWORD` | Password required to join (leave empty for a public server). | `` |

## Install

```bash
php artisan p:egg:import vintage-story/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/vintage-story:latest images/vintage-story
```
