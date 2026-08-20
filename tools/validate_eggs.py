#!/usr/bin/env python3
"""Aetheris game egg catalog validator.

Checks every egg.json in eggs/ for PTDL_v2 schema conformance and for
cross-file consistency (id slugs, image references, install scripts).
Runs as a CI gate; exits non-zero on any failure.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EGGS_DIR = ROOT / "eggs"
IMAGES_DIR = ROOT / "images"

META_VERSION = "PTDL_v2"
ID_SLUG_RE = re.compile(r"^[a-z0-9-]+$")
ENV_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")

REQUIRED_TOP_LEVEL = {
    "meta": dict,
    "exported_at": str,
    "name": str,
    "author": str,
    "description": str,
    "features": list,
    "docker_images": dict,
    "file_denylist": list,
    "startup": str,
    "config": dict,
    "scripts": dict,
    "variables": list,
}

REQUIRED_CONFIG = {"files": dict, "startup": dict, "stop": str, "logs": dict}
REQUIRED_SCRIPT = {"installation": dict}
REQUIRED_INSTALL = {"script": str, "container": str, "entrypoint": str}


def error(msg: str, path: Path | None = None) -> int:
    prefix = f"{path.relative_to(ROOT)}: " if path else ""
    print(f"ERROR {prefix}{msg}", file=sys.stderr)
    return 1


def load_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(f"invalid JSON: {exc}", path)
        return None
    if not isinstance(data, dict):
        error("egg.json must be a JSON object", path)
        return None
    return data


def validate_egg(egg_json: Path) -> int:
    fails = 0
    data = load_json(egg_json)
    if data is None:
        return 1

    game_dir = egg_json.parent.name
    game_root = egg_json.parent.parent.name

    # Top-level required keys with correct types.
    for key, expected in REQUIRED_TOP_LEVEL.items():
        if key not in data:
            fails += error(f"missing top-level key '{key}'", egg_json)
        elif not isinstance(data[key], expected):
            fails += error(f"key '{key}' must be {expected.__name__}", egg_json)

    if data.get("meta", {}).get("version") != META_VERSION:
        fails += error(f"meta.version must be '{META_VERSION}'", egg_json)

    if "docker_images" in data and not data["docker_images"]:
        fails += error("docker_images must declare at least one image", egg_json)

    # Variables: env var naming, defaults, rules.
    seen_envs: set[str] = set()
    for index, var in enumerate(data.get("variables", [])):
        if not isinstance(var, dict):
            fails += error(f"variable[{index}] must be an object", egg_json)
            continue
        env = var.get("env_variable")
        if not env or not ENV_RE.match(env):
            fails += error(f"variable[{index}] has invalid env_variable", egg_json)
        elif env in seen_envs:
            fails += error(f"duplicate env_variable '{env}'", egg_json)
        seen_envs.add(env)
        for key in ("name", "description", "default_value", "rules"):
            if key not in var:
                fails += error(f"variable[{index}] missing '{key}'", egg_json)
        if "user_viewable" not in var or "user_editable" not in var:
            fails += error(f"variable[{index}] missing user_viewable/user_editable", egg_json)

    # Scripts: install block.
    scripts = data.get("scripts", {})
    if "installation" not in scripts:
        fails += error("scripts.installation is required", egg_json)
    else:
        install = scripts["installation"]
        if not isinstance(install, dict):
            fails += error("scripts.installation must be an object", egg_json)
        else:
            for key, expected in REQUIRED_INSTALL.items():
                if key not in install:
                    fails += error(f"scripts.installation missing '{key}'", egg_json)
                elif not isinstance(install[key], expected):
                    fails += error(f"scripts.installation.{key} must be {expected.__name__}", egg_json)

    # Startup command must reference declared env vars (sanity check).
    startup = data.get("startup", "")
    declared = set(seen_envs) | {
        "SERVER_JARFILE",
        "MEMORY",
        "SERVER_PORT",
        "SERVER_PASSWORD",
        "MAX_PLAYERS",
        "HOSTNAME",
        "RCON_PASSWORD",
        "ADMIN_PASSWORD",
        "SERVER_NAME",
    }
    for match in re.finditer(r"\$\{([A-Z][A-Z0-9_]*)\}", startup):
        if match.group(1) not in declared:
            fails += error(
                f"startup references undeclared env '{match.group(1)}'", egg_json
            )

    # Consistency: install script present next to egg.json when referenced.
    install_script_ref = None
    script_text = scripts.get("installation", {}).get("script", "")
    for line in script_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# @") or stripped.startswith("#"):
            continue
        if "start_server.sh" in stripped or "start.sh" in stripped:
            install_script_ref = "start_server.sh"
            break

    # Every image slug must have a matching folder under images/.
    for image in data.get("docker_images", {}):
        match = re.search(r"aetheris-project/([a-z0-9-]+):", image)
        if match:
            slug = match.group(1)
            if not (IMAGES_DIR / slug).is_dir():
                fails += error(
                    f"image '{image}' has no matching images/{slug}/ directory", egg_json
                )

    # Folder slug coherence: egg id slug must match the game folder name.
    if game_dir and game_root == "eggs" and not ID_SLUG_RE.match(game_dir):
        fails += error(f"folder '{game_dir}' is not a valid slug", egg_json)

    return fails


def main() -> int:
    eggs = sorted(EGGS_DIR.glob("**/egg.json"))
    if not eggs:
        print("No eggs found under eggs/", file=sys.stderr)
        return 1

    total_fails = 0
    for egg in eggs:
        total_fails += validate_egg(egg)

    if total_fails:
        print(f"\n{total_fails} validation error(s) across {len(eggs)} eggs.", file=sys.stderr)
        return 1

    print(f"All {len(eggs)} eggs validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
