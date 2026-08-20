# Don't Starve Together egg

Aetheris egg for **Don't Starve Together**, importable into any Pterodactyl panel or
provisioned directly through the Aetheris Pterodactyl bridge.

- **Image**: `ghcr.io/aetheris-project/dst:latest`
- **Default port**: 10999
- **Stop command**: `c_shutdown()`

## Variables

| Variable | Description | Default |
| --- | --- | --- |
| `CLUSTER_NAME` | Cluster directory name. | `AetherisCluster` |
| `SHARD_NAME` | Shard to run (Master or Caves). | `Master` |
| `MAX_PLAYERS` | Maximum concurrent players. | `16` |
| `SERVER_PASSWORD` | Password required to join (leave empty for a public server). | `` |

## Install

```bash
php artisan p:egg:import dst/egg.json
```

## Runtime image

```bash
docker build -t ghcr.io/aetheris-project/dst:latest images/dst
```
