# SCP: Secret Laboratory egg

Aetheris egg for **SCP: Secret Laboratory**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/scpsl:latest`
- **Default port**: 7777
- **Stop command**: `STOP`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `SERVER_PORT` | Game port. | `7777` |
| `MAX_PLAYERS` | Maximum number of concurrent players. | `24` |
| `SERVER_PASSWORD` | Password required to join (leave empty for a public server). | `` |
| `TICKRATE` | Server tick rate. | `60` |

## Install

```bash
php artisan p:egg:import scpsl/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/scpsl:latest images/scpsl
```
