#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
MANIFEST="$ROOT/sdk/fonts.manifest.json"

if [ ! -f "$MANIFEST" ]; then
  echo "Missing sdk/fonts.manifest.json. Run: python scripts/build_font_sdk.py" >&2
  exit 1
fi

case "$(uname -s)" in
  Darwin) FONT_DIR="$HOME/Library/Fonts" ;;
  *) FONT_DIR="$HOME/.local/share/fonts" ;;
esac

mkdir -p "$FONT_DIR"

python3 - "$ROOT" "$MANIFEST" "$FONT_DIR" "${1:-}" <<'PY'
import json
import shutil
import sys
from pathlib import Path

root = Path(sys.argv[1])
manifest = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
font_dir = Path(sys.argv[3])
family_filter = sys.argv[4].lower()

installed = 0
for face in manifest["faces"]:
    if face["extension"] not in {"ttf", "otf", "ttc", "otc"}:
        continue
    if family_filter and family_filter not in face["family"].lower():
        continue
    source = root / face["path"]
    if not source.exists():
        print(f"missing: {face['path']}", file=sys.stderr)
        continue
    shutil.copy2(source, font_dir / source.name)
    installed += 1

print(f"Installed {installed} font faces into {font_dir}.")
PY

if command -v fc-cache >/dev/null 2>&1; then
  fc-cache -f "$FONT_DIR"
fi
