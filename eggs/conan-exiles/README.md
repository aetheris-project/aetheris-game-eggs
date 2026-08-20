# Conan Exiles egg

Aetheris egg for **Conan Exiles**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/conan-exiles:latest`
- **Default port**: 7777
- **Stop command**: `quit`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `HOSTNAME` | Server name shown in the server browser. | `Aetheris Conan Exiles` |
| `SERVER_PORT` | Game port (UDP). | `7777` |
| `QUERY_PORT` | Source query port used by the server browser. | `27015` |
| `RCON_PORT` | RCON administration port. | `25575` |
| `RCON_PASSWORD` | RCON password for remote administration. | `changeme` |
| `MAX_PLAYERS` | Maximum number of concurrent players. | `40` |
| `SERVER_PASSWORD` | Password required to join (leave empty for a public server). | `` |

## Install

```bash
php artisan p:egg:import conan-exiles/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/conan-exiles:latest images/conan-exiles
```
