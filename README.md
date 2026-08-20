# Aetheris Game Eggs

Official game server eggs for the [Aetheris](https://github.com/aetheris-project)
virtualization platform. Every egg is a drop-in **Pterodactyl-compatible**
definition (schema `PTDL_v2`) and can be imported into any Pterodactyl panel,
including the Pterodactyl bridge built into Aetheris.

The repository ships three layers for each game:

1. **Egg definition** - the `egg.json` manifest: Docker image, startup command,
   stop command, server configuration parsing, and install variables.
2. **Install script** - a deterministic, idempotent installer that downloads the
   server files, validates checksums and writes the configuration.
3. **Configuration blueprint** - sane defaults (ports, world names, memory
   presets) so a server starts on first boot with zero manual steps.

## Supported games

| Game | Egg | Image | Default port |
| --- | --- | --- | --- |
| Minecraft Java | `eggs/minecraft/java` | `ghcr.io/aetheris-project/minecraft-java` | 25565 |
| Minecraft Forge | `eggs/minecraft/forge` | `ghcr.io/aetheris-project/minecraft-forge` | 25565 |
| Minecraft Paper | `eggs/minecraft/paper` | `ghcr.io/aetheris-project/minecraft-paper` | 25565 |
| Minecraft Velocity | `eggs/minecraft/velocity` | `ghcr.io/aetheris-project/minecraft-velocity` | 25577 |
| Minecraft Bedrock | `eggs/minecraft/bedrock` | `ghcr.io/aetheris-project/minecraft-bedrock` | 19132 |
| Terraria | `eggs/terraria` | `ghcr.io/aetheris-project/terraria` | 7777 |
| Valheim | `eggs/valheim` | `ghcr.io/aetheris-project/valheim` | 2456 |
| Palworld | `eggs/palworld` | `ghcr.io/aetheris-project/palworld` | 8211 |
| ARK: Survival Ascended | `eggs/ark-asa` | `ghcr.io/aetheris-project/ark-asa` | 7777 |
| Counter-Strike 2 | `eggs/cs2` | `ghcr.io/aetheris-project/cs2` | 27015 |
| Rust | `eggs/rust` | `ghcr.io/aetheris-project/rust` | 28015 |
| Garry's Mod | `eggs/gmod` | `ghcr.io/aetheris-project/gmod` | 27015 |
| FiveM | `eggs/fivem` | `ghcr.io/aetheris-project/fivem` | 30120 |
| Project Zomboid | `eggs/project-zomboid` | `ghcr.io/aetheris-project/project-zomboid` | 16261 |
| Factorio | `eggs/factorio` | `ghcr.io/aetheris-project/factorio` | 34197 |
| Satisfactory | `eggs/satisfactory` | `ghcr.io/aetheris-project/satisfactory` | 7777 |
| 7 Days to Die | `eggs/7dtd` | `ghcr.io/aetheris-project/7dtd` | 26900 |
| V Rising | `eggs/vrising` | `ghcr.io/aetheris-project/vrising` | 9874 |
| Enshrouded | `eggs/enshrouded` | `ghcr.io/aetheris-project/enshrouded` | 15636 |
| Don't Starve Together | `eggs/dst` | `ghcr.io/aetheris-project/dst` | 10999 |
| Vintage Story | `eggs/vintage-story` | `ghcr.io/aetheris-project/vintage-story` | 42420 |
| SCP: Secret Laboratory | `eggs/scpsl` | `ghcr.io/aetheris-project/scpsl` | 7777 |
| Team Fortress 2 | `eggs/tf2` | `ghcr.io/aetheris-project/tf2` | 27015 |
| Left 4 Dead 2 | `eggs/l4d2` | `ghcr.io/aetheris-project/l4d2` | 27015 |
| Conan Exiles | `eggs/conan-exiles` | `ghcr.io/aetheris-project/conan-exiles` | 7777 |
| Space Engineers | `eggs/space-engineers` | `ghcr.io/aetheris-project/space-engineers` | 27016 |
| Starbound | `eggs/starbound` | `ghcr.io/aetheris-project/starbound` | 21025 |

## Quick start

### Import into Pterodactyl

```bash
# From the Pterodactyl panel directory
cd /var/www/pterodactyl

# Import a single egg
php artisan p:egg:import /path/to/aetheris-game-eggs/eggs/minecraft/java/egg.json

# Import every egg in the repository
for egg in /path/to/aetheris-game-eggs/eggs/*/egg.json; do
  php artisan p:egg:import "$egg"
done
```

### Use with the Aetheris Pterodactyl bridge

The Aetheris backend provisions servers through its Pterodactyl driver
(`aetheris-app/src/lib/adapters/hypervisors/pterodactyl.ts`). Point the driver
at this repository when a client orders a game server:

```json
{
  "provider": "pterodactyl",
  "baseUrl": "https://panel.example.com",
  "applicationKey": "ptlc_...",
  "clientKey": "ptlc_...",
  "eggCatalog": "https://github.com/aetheris-project/aetheris-game-eggs"
}
```

The bridge resolves the egg by its `id` (the stable slug in the egg manifest),
so `minecraft-java`, `terraria`, `valheim` and friends map directly to the
game selection shown in the Aetheris store.

## Repository layout

```
eggs/
  <game>/
    egg.json          # Pterodactyl PTDL_v2 manifest
    install.sh        # Idempotent installation script (runs in the install container)
    README.md         # Game-specific notes, variables, firewall rules
images/
  <game>/Dockerfile   # Runtime images published to ghcr.io/aetheris-project/*
tools/
  generate_eggs.py    # Declarative generator for SteamCMD and Minecraft eggs
  validate_eggs.py    # Schema + consistency validator (CI gate)
docs/
  egg-authoring.md    # How to add a new egg to this catalog
```

## Validation

Every egg is validated in CI before merge:

```bash
python tools/validate_eggs.py
```

The validator checks that each `egg.json`:

- is valid JSON with the `PTDL_v2` meta schema;
- declares a `startup` command, a `stop` command and install scripts;
- references an image that exists in `images/`;
- declares variables with defaults, descriptions and validation rules;
- keeps the same `id` slug across the egg, its folder and its image tag.

## Generating eggs

SteamCMD-based and Minecraft-family eggs are generated from a declarative
catalog in `tools/generate_eggs.py`:

```bash
python tools/generate_eggs.py
```

The generator writes the `egg.json`, `README.md` and `images/<slug>/Dockerfile`
for every entry and is deterministic, so the generated files stay in sync with
the catalog. Hand-tuned eggs (for example `minecraft/java` with its Aikar's
flags) remain checked in and are not overwritten.

## Contributing

Read [docs/egg-authoring.md](docs/egg-authoring.md) for the full authoring
guide, then open a pull request. Game-specific runtime quirks are documented
inside each egg folder.

## License

AGPL-3.0, with an additional permission for the eggs, install scripts and
images in this repository (see [LICENSE.md](LICENSE.md)). Copyright (C) 2026
Leonardo Galli (Leo-Galli), Aetheris Project.
