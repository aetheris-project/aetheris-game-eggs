# Space Engineers egg

Aetheris egg for **Space Engineers**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/space-engineers:latest`
- **Default port**: 27016
- **Stop command**: `quit`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `SERVER_PORT` | Game port (UDP). | `27016` |
| `MAX_PLAYERS` | Maximum number of concurrent players. | `16` |
| `SERVER_PASSWORD` | Password required to join (leave empty for a public server). | `` |
| `WORLD_NAME` | World save name. | `Aetheris World` |

## Install

```bash
php artisan p:egg:import space-engineers/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/space-engineers:latest images/space-engineers
```
