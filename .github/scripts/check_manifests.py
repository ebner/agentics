"""Check that the marketplace manifest and every plugin manifest agree.

Fails when a manifest is not valid JSON, a marketplace entry points at a missing
plugin, a plugin directory is not listed in the marketplace, names differ between
the two manifests, a marketplace entry sets a version (the version belongs only in
plugin.json), a plugin.json has no version, or a plugin has no README.md.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    errors = []
    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    listed = set()

    for entry in marketplace["plugins"]:
        name = entry["name"]
        plugin_dir = (ROOT / entry["source"]).resolve()
        listed.add(plugin_dir)
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        if not manifest_path.is_file():
            errors.append(f"{name}: {manifest_path.relative_to(ROOT)} is missing")
            continue
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("name") != name:
            errors.append(f"{name}: plugin.json name is {manifest.get('name')!r}")
        if "version" in entry:
            errors.append(f"{name}: marketplace.json entry sets a version; keep it only in plugin.json")
        if not manifest.get("version"):
            errors.append(f"{name}: plugin.json has no version")
        if not (plugin_dir / "README.md").is_file():
            errors.append(f"{name}: README.md is missing")

    for plugin_dir in sorted((ROOT / "plugins").iterdir()):
        if plugin_dir.is_dir() and plugin_dir.resolve() not in listed:
            errors.append(f"{plugin_dir.name}: not listed in marketplace.json")

    for error in errors:
        print(f"error: {error}")
    if not errors:
        print(f"ok: {len(marketplace['plugins'])} plugins, manifests consistent")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
