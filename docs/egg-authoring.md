# Authoring guide

This document explains how to add a new game to the Aetheris egg catalog and
how the pieces fit together.

## Anatomy of an egg

Every egg lives in `eggs/<game-slug>/` and consists of:

| File | Purpose |
| --- | --- |
| `egg.json` | The Pterodactyl `PTDL_v2` manifest imported by the panel |
| `install.sh` | (optional) Standalone copy of the install script for humans |
| `README.md` | Game-specific notes: ports, firewall rules, variables |

The runtime image lives in `images/<game-slug>/Dockerfile` and is published
to `ghcr.io/aetheris-project/<game-slug>:latest`.

## Adding a new game

1. **Pick a slug.** Lowercase, hyphens only (`minecraft-java`, `ark-asa`).
   The slug must be stable: it becomes the egg id used by the Aetheris
   Pterodactyl bridge and the store.

2. **Create the folders.**

   ```bash
   mkdir -p eggs/<slug> images/<slug>
   ```

3. **Write the runtime image** in `images/<slug>/Dockerfile`. Rules:
   - Run as a non-root user (`container`, uid 1000).
   - Declare `WORKDIR /home/container`.
   - Install only the libraries the server needs (SteamCMD games need
     `lib32gcc-s1 lib32stdc++6 libcurl4-gnutls-dev`).
   - Expose the default ports (game port, query port, RCON).

4. **Write the egg manifest** in `eggs/<slug>/egg.json`. Copy an existing egg
   as a template and adapt:

   - `docker_images`: point at `ghcr.io/aetheris-project/<slug>:latest`.
   - `startup`: keep it **environment-variable driven**; never hardcode ports
     or paths. Use `${VAR}` for Pterodactyl env vars and `{{VAR}}` for
     Pterodactyl internal placeholders.
   - `config.stop`: the exact string that stops the server gracefully
     (`stop`, `quit`, `exit`, `restart`).
   - `config.startup.done`: the log line that signals the server is ready.
   - `scripts.installation`: an idempotent bash script run in the install
     container. Download to the working directory, resolve latest versions
     from the official API where possible, write default configs only if they
     do not exist.

5. **Declare variables.** Every env var used in `startup` must be declared in
   `variables` with a sensible `default_value`, a human `description`, and a
   `rules` string (Laravel validation rules, as Pterodactyl expects).

6. **Validate.**

   ```bash
   python tools/validate_eggs.py
   ```

   The validator rejects manifests with undeclared startup env vars, missing
   image folders, duplicate variables or invalid schemas.

7. **Document.** Add a `README.md` in the egg folder: default ports, the
   variable table, firewall rules, and any game-specific quirks.

8. **Register in the catalog.** Add a row to the game table in the root
   `README.md`.

## Install script conventions

- **Idempotent**: running twice yields the same result.
- **Fail loudly**: `set -euo pipefail`; `exit 1` with a message when a
  download URL cannot be resolved.
- **Version-aware**: resolve `latest` from the official API at install time
  instead of pinning a stale build.
- **Config only when absent**: `if [ ! -f server.properties ]` — never
  overwrite an admin's existing configuration.
- **Wrap SteamCMD servers** in a `start_server.sh` that re-validates the app
  before launching, so a crash loop self-heals on the next start.

## Variable naming rules

- Uppercase snake case (`MAX_PLAYERS`, `RCON_PASSWORD`).
- Reuse the standard names across eggs (`SERVER_PORT`, `SERVER_PASSWORD`,
  `MAX_PLAYERS`, `SERVER_NAME`, `ADMIN_PASSWORD`, `RCON_PASSWORD`) so the
  store UI and the Pterodactyl bridge can map them generically.
- Never declare the memory variable as a startup variable: memory comes from
  the server allocation, not from the egg.
