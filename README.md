<p align="center">
  <img src="https://raw.githubusercontent.com/aetheris-project/.github/main/assets/icon.svg" alt="Aetheris Game Eggs" width="88" style="filter: drop-shadow(0 0 20px rgba(236,72,153,0.55))">
</p>

<h1 align="center">Aetheris Game Eggs</h1>

<p align="center">
  <strong>Official Pterodactyl-compatible egg catalog (PTDL_v2) for the Aetheris virtualization platform — 27 games, 31 images</strong>
</p>

<p align="center">
  <a href="https://aetheris-docs.vercel.app/wiki/game-hosting"><img src="https://img.shields.io/badge/Docs-Game%20Hosting-0EA5E9?style=for-the-badge&logo=readthedocs&logoColor=white" alt="Docs"></a>
  <a href="https://aetheris-docs.vercel.app/wiki/game-hosting-catalog"><img src="https://img.shields.io/badge/Catalog-27%20Games-EC4899?style=for-the-badge&logo=steam&logoColor=white" alt="Catalog"></a>
  <a href="https://discord.gg/6GcfebuT2A"><img src="https://img.shields.io/badge/Discord-Help-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Pterodactyl-PTDL__v2-18181B?style=flat-square&logo=pterodactyl&logoColor=white" alt="Pterodactyl">
  <img src="https://img.shields.io/badge/Docker-31%20Images-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Games-27-EC4899?style=flat-square" alt="Games">
  <img src="https://img.shields.io/badge/Variants-31-F59E0B?style=flat-square" alt="Variants">
  <img src="https://img.shields.io/badge/CI-Validated-10B981?style=flat-square&logo=githubactions&logoColor=white" alt="CI">
  <img src="https://img.shields.io/badge/Aetheris-Bridge%20Ready-10B981?style=flat-square" alt="Bridge">
</p>

---

<br>

> **Drop-in game-server definitions compatible with Pterodactyl PTDL_v2** and
> natively consumed by the Aetheris Pterodactyl Bridge. Every egg ships
> three layers — the JSON manifest, a deterministic install script and a
> set of sane-port / memory / firewall defaults so servers boot on the
> first start with zero manual configuration.
>
> Images are published to **ghcr.io/aetheris-project/\*** and source
> Dockerfiles live in `images/<slug>/` for every variant.

<br>

## ✨ Features

<table>
  <tr>
    <td width="33%" align="center" valign="top">
      <h3>🎮 27 games</h3>
      <p>Minecraft family (5) · Survival (10) · Source/Valve (5) · Sandbox (5) · Other (2) — 31 total variants.</p>
    </td>
    <td width="33%" align="center" valign="top">
      <h3>⚓ Pterodactyl PTDL_v2</h3>
      <p>100% compatible with stock Pterodactyl. Import via <code>php artisan p:egg:import</code> with no conversion.</p>
    </td>
    <td width="33%" align="center" valign="top">
      <h3>🐳 Deterministic images</h3>
      <p>Per-game Dockerfiles in <code>images/</code>. Published to ghcr.io with immutable tags.</p>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top">
      <h3>🧱 Sane defaults</h3>
      <p>Correct default port, allocations, memory presets, environment variables, startup flags + stop commands.</p>
    </td>
    <td align="center" valign="top">
      <h3>🔁 Idempotent install</h3>
      <p>Each install script validates checksums, resumes interrupted downloads and verifies server binaries.</p>
    </td>
    <td align="center" valign="top">
      <h3>🛡️ CI validated</h3>
      <p>Schema check · ID slug consistency · image-Dockerfile pairing · variable descriptions — all gate merges.</p>
    </td>
  </tr>
</table>

<br>

## 🚀 Quick Start

### Method A — Import into stock Pterodactyl

```bash
cd /var/www/pterodactyl

# Import ONE egg
php artisan p:egg:import /path/to/aetheris-game-eggs/eggs/minecraft/java/egg.json

# Import ALL eggs (Linux shell)
for egg in /path/to/aetheris-game-eggs/eggs/*/egg.json \
           /path/to/aetheris-game-eggs/eggs/minecraft/*/egg.json; do
  php artisan p:egg:import "$egg"
done
```

### Method B — Use via Aetheris Pterodactyl Bridge

The Aetheris control plane provisions servers through its typed Pterodactyl
driver. In `admin/nodes` → driver config point `eggCatalog` at this repo:

```json
{
  "provider":      "pterodactyl",
  "baseUrl":       "https://panel.example.com",
  "applicationKey":"ptla_xxxxxxxxxxxxxxxxxxxx",
  "clientKey":     "ptlc_yyyyyyyyyyyyyyyyyyyy",
  "eggCatalog":    "https://github.com/aetheris-project/aetheris-game-eggs"
}
```

The bridge resolves egg IDs directly from the catalog: `minecraft-java`,
`valheim`, `palworld`, `cs2`, `rust`, etc. map 1:1 to the slugs below.

### Validate the catalog locally

```bash
python tools/validate_eggs.py
```

<br>

## 🎮 Full Catalog

Click any egg folder in the repo for game-specific variables, firewall notes
and install-script behavior.

| Family | Slug | Game | Default Port | Image |
|---|---|---|---|---|
| **Minecraft** | `minecraft-java` | Minecraft Java Edition | 25565 | `ghcr.io/aetheris-project/minecraft-java` |
| | `minecraft-forge` | Minecraft Forge (modded) | 25565 | `ghcr.io/aetheris-project/minecraft-forge` |
| | `minecraft-paper` | Minecraft Paper (optimized) | 25565 | `ghcr.io/aetheris-project/minecraft-paper` |
| | `minecraft-velocity` | Minecraft Velocity (proxy) | 25577 | `ghcr.io/aetheris-project/minecraft-velocity` |
| | `minecraft-bedrock` | Minecraft Bedrock Edition | 19132/udp | `ghcr.io/aetheris-project/minecraft-bedrock` |
| **Survival / Open-World** | `valheim` | Valheim | 2456/udp | `ghcr.io/aetheris-project/valheim` |
| | `palworld` | Palworld | 8211/udp | `ghcr.io/aetheris-project/palworld` |
| | `ark-asa` | ARK: Survival Ascended | 7777/udp | `ghcr.io/aetheris-project/ark-asa` |
| | `project-zomboid` | Project Zomboid | 16261/udp | `ghcr.io/aetheris-project/project-zomboid` |
| | `factorio` | Factorio | 34197/udp | `ghcr.io/aetheris-project/factorio` |
| | `satisfactory` | Satisfactory | 7777/udp | `ghcr.io/aetheris-project/satisfactory` |
| | `7dtd` | 7 Days to Die | 26900 | `ghcr.io/aetheris-project/7dtd` |
| | `vrising` | V Rising | 9874/udp | `ghcr.io/aetheris-project/vrising` |
| | `enshrouded` | Enshrouded | 15636/udp | `ghcr.io/aetheris-project/enshrouded` |
| | `vintage-story` | Vintage Story | 42420 | `ghcr.io/aetheris-project/vintage-story` |
| **Source / Valve** | `cs2` | Counter-Strike 2 | 27015 | `ghcr.io/aetheris-project/cs2` |
| | `rust` | Rust | 28015/udp | `ghcr.io/aetheris-project/rust` |
| | `gmod` | Garry's Mod | 27015 | `ghcr.io/aetheris-project/gmod` |
| | `tf2` | Team Fortress 2 | 27015 | `ghcr.io/aetheris-project/tf2` |
| | `l4d2` | Left 4 Dead 2 | 27015 | `ghcr.io/aetheris-project/l4d2` |
| **Sandbox / Other** | `terraria` | Terraria | 7777 | `ghcr.io/aetheris-project/terraria` |
| | `fivem` | FiveM (GTA V) | 30120 | `ghcr.io/aetheris-project/fivem` |
| | `dst` | Don't Starve Together | 10999/udp | `ghcr.io/aetheris-project/dst` |
| | `scpsl` | SCP: Secret Laboratory | 7777 | `ghcr.io/aetheris-project/scpsl` |
| | `conan-exiles` | Conan Exiles | 7777/udp | `ghcr.io/aetheris-project/conan-exiles` |
| | `space-engineers` | Space Engineers | 27016/udp | `ghcr.io/aetheris-project/space-engineers` |
| | `starbound` | Starbound | 21025 | `ghcr.io/aetheris-project/starbound` |

<br>

## 🧩 Repository Layout

```text
aetheris-game-eggs/
├── eggs/                           # 🍳 One folder per egg slug
│   ├── <game-slug>/
│   │   ├── egg.json                # Pterodactyl PTDL_v2 manifest (authoritative)
│   │   ├── install.sh              # Idempotent install script (runs in Pterodactyl install container)
│   │   └── README.md               # Game-specific notes · env vars · firewall rules
│   └── minecraft/
│       ├── java / forge / paper / velocity / bedrock/   # 5 sub-eggs
├── images/                         # 🐳 Source Dockerfiles (→ ghcr.io/aetheris-project/*)
│   └── <slug>/Dockerfile
├── tools/
│   ├── generate_eggs.py            # Declarative generator for SteamCMD and Minecraft-family eggs
│   └── validate_eggs.py            # CI gate — schema, IDs, image pairing, var coverage
├── docs/
│   └── egg-authoring.md            # How to add a new egg (template + checklist)
└── LICENSE.md                      # AGPL-3.0 + egg/additional-permission clause
```

<br>

## 🧪 CI & Validation

Every egg is gated in `.github/workflows/validate.yml`:

```bash
python tools/validate_eggs.py
```

The validator confirms each `egg.json`:
- Is valid JSON and declares the `PTDL_v2` meta schema
- Has `startup`, `stop`, install commands and sane defaults
- References an image whose Dockerfile exists in `images/<slug>/`
- Declares every install variable with a default, description and validation regex
- Keeps a stable `id` slug consistent across folder name, image tag and manifest

SteamCMD and Minecraft-family eggs can be regenerated deterministically:

```bash
python tools/generate_eggs.py
```

Hand-tuned eggs (e.g. Minecraft Java with Aikar's JVM flags) are checked in
directly and never overwritten.

---

<p align="center">
  <strong>Made with 💚 by <a href="https://github.com/Leo-Galli">Leonardo Galli</a></strong>
</p>

<p align="center">
  <a href="https://github.com/aetheris-project/aetheris-app">App</a>
  ·
  <a href="https://github.com/aetheris-project/aetheris-docs">Docs</a>
  ·
  <a href="https://github.com/aetheris-project/aetheris-installer">Installer</a>
  ·
  <a href="https://discord.gg/6GcfebuT2A">Discord</a>
  ·
  <a href="https://paypal.me/LeonardoGalliITA">Donate</a>
</p>

## 📄 License

AGPL-3.0 with an **additional permission** for the eggs, install scripts
and container images in this repository (they may be compiled into /
distributed alongside server binaries without triggering the AGPL's
corresponding-source clause on the game files themselves).
See [LICENSE.md](LICENSE.md) for the exact wording.

Copyright (C) 2026 Leonardo Galli (Leo-Galli) · Aetheris Project.
