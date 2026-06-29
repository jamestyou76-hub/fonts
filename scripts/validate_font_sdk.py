#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from fontTools.ttLib import TTCollection, TTFont


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "sdk" / "fonts.manifest.json"
CSS = ROOT / "sdk" / "fonts.css"


def validate_face(face: dict) -> list[str]:
    errors: list[str] = []
    path = ROOT / face["path"]
    if not path.exists():
        return [f"missing file: {face['path']}"]

    extension = path.suffix.lower()
    try:
        if extension in {".ttc", ".otc"}:
            index = face.get("collectionIndex")
            collection = TTCollection(path)
            try:
                if index is None or index >= len(collection.fonts):
                    errors.append(f"invalid collection index: {face['path']}#{index}")
            finally:
                for font in collection.fonts:
                    font.close()
        else:
            font = TTFont(path, lazy=True)
            font.close()
    except Exception as exc:
        errors.append(f"cannot read font: {face['path']} ({exc})")

    if face.get("size") != path.stat().st_size:
        errors.append(f"size drift: {face['path']} manifest={face.get('size')} actual={path.stat().st_size}")
    return errors


def main() -> int:
    errors: list[str] = []
    if not MANIFEST.exists():
        errors.append("missing sdk/fonts.manifest.json")
    if not CSS.exists():
        errors.append("missing sdk/fonts.css")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    faces = manifest.get("faces", [])
    for face in faces:
        errors.extend(validate_face(face))

    css_text = CSS.read_text(encoding="utf-8")
    css_faces = sum(1 for face in faces if face.get("css"))
    if css_faces and "@font-face" not in css_text:
        errors.append("sdk/fonts.css has no @font-face rules")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    untracked = sum(1 for face in faces if not face.get("tracked", False))
    print(f"OK: {len(faces)} faces validated. Untracked faces in local manifest: {untracked}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
