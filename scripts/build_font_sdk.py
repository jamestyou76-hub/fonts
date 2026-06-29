#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fontTools.ttLib import TTCollection, TTFont


FONT_EXTENSIONS = {".otf", ".ttf", ".otc", ".ttc"}
CSS_EXTENSIONS = {".otf", ".ttf"}
IGNORED_DIRS = {".git", "node_modules", ".tmp", ".tmp-noto-cjk"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def tracked_files(root: Path) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return set()
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def iter_font_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in IGNORED_DIRS for part in rel_parts):
            continue
        if path.suffix.lower() in FONT_EXTENSIONS:
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix().lower())


def name_value(font: TTFont, name_id: int) -> str | None:
    names = font["name"] if "name" in font else None
    if names is None:
        return None
    value = names.getDebugName(name_id)
    if value:
        return value
    for record in names.names:
        if record.nameID == name_id:
            try:
                return record.toUnicode()
            except Exception:
                continue
    return None


def font_names(font: TTFont) -> dict[str, str]:
    family = name_value(font, 16) or name_value(font, 1) or "Unknown"
    subfamily = name_value(font, 17) or name_value(font, 2) or "Regular"
    full_name = name_value(font, 4) or f"{family} {subfamily}".strip()
    postscript_name = name_value(font, 6) or ""
    return {
        "family": family,
        "subfamily": subfamily,
        "fullName": full_name,
        "postScriptName": postscript_name,
    }


def css_style(subfamily: str) -> str:
    text = subfamily.lower()
    if "italic" in text or "oblique" in text:
        return "italic"
    return "normal"


def css_stretch(path: Path, family: str, subfamily: str) -> str:
    text = f"{path.name} {family} {subfamily}".lower()
    if "condensed" in text or "-cd-" in text or "narrow" in text:
        return "condensed"
    if "expanded" in text or "-ex-" in text:
        return "expanded"
    return "normal"


def weight_class(font: TTFont, subfamily: str) -> int:
    if "OS/2" in font:
        try:
            return int(font["OS/2"].usWeightClass)
        except Exception:
            pass

    text = subfamily.lower()
    weight_map = [
        ("thin", 100),
        ("extralight", 200),
        ("ultralight", 200),
        ("light", 300),
        ("regular", 400),
        ("book", 400),
        ("medium", 500),
        ("semibold", 600),
        ("demibold", 600),
        ("bold", 700),
        ("extrabold", 800),
        ("ultrabold", 800),
        ("black", 900),
        ("heavy", 900),
    ]
    for token, value in weight_map:
        if token in text:
            return value
    return 400


def font_format(extension: str) -> str:
    return {
        ".otf": "opentype",
        ".ttf": "truetype",
        ".otc": "collection",
        ".ttc": "collection",
    }.get(extension.lower(), "unknown")


def slug(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "font"


def category(rel_path: str) -> str:
    top = rel_path.split("/", 1)[0]
    return {
        "doc-font": "document",
        "italic": "display",
        "narrow": "monospace",
    }.get(top, top)


def face_entry(root: Path, path: Path, font: TTFont, collection_index: int | None, tracked: bool) -> dict[str, Any]:
    rel_path = path.relative_to(root).as_posix()
    names = font_names(font)
    extension = path.suffix.lower()
    subfamily = names["subfamily"]
    entry_id = slug("-".join([names["family"], subfamily, extension[1:], str(collection_index or 0)]))
    return {
        "id": entry_id,
        "family": names["family"],
        "subfamily": subfamily,
        "fullName": names["fullName"],
        "postScriptName": names["postScriptName"],
        "path": rel_path,
        "extension": extension[1:],
        "format": font_format(extension),
        "size": path.stat().st_size,
        "weight": weight_class(font, subfamily),
        "style": css_style(subfamily),
        "stretch": css_stretch(path, names["family"], subfamily),
        "category": category(rel_path),
        "collectionIndex": collection_index,
        "css": extension in CSS_EXTENSIONS,
        "tracked": tracked,
    }


def read_faces(root: Path, path: Path, tracked_set: set[str]) -> list[dict[str, Any]]:
    rel_path = path.relative_to(root).as_posix()
    tracked = rel_path in tracked_set
    extension = path.suffix.lower()
    if extension in {".ttc", ".otc"}:
        collection = TTCollection(path)
        faces: list[dict[str, Any]] = []
        try:
            for index, font in enumerate(collection.fonts):
                faces.append(face_entry(root, path, font, index, tracked))
        finally:
            for font in collection.fonts:
                font.close()
        return faces

    font = TTFont(path, lazy=True)
    try:
        return [face_entry(root, path, font, None, tracked)]
    finally:
        font.close()


def css_url(manifest_path: str) -> str:
    return quote(f"../{manifest_path}", safe="/._-")


def build_css(faces: list[dict[str, Any]]) -> str:
    groups: dict[tuple[str, int, str, str], list[dict[str, Any]]] = defaultdict(list)
    for face in faces:
        if face["css"]:
            key = (face["family"], face["weight"], face["style"], face["stretch"])
            groups[key].append(face)

    lines = [
        "/* Generated by scripts/build_font_sdk.py. Do not edit by hand. */",
        "",
        ":root {",
        '  --font-sdk-cjk-sc: "Noto Sans CJK SC", "Source Han Sans SC", "DengXian", "Microsoft YaHei", sans-serif;',
        '  --font-sdk-cjk-jp: "Noto Sans CJK JP", "Source Han Sans JP", "Meiryo", sans-serif;',
        '  --font-sdk-sans: "Alibaba Sans", "Alibaba PuHuiTi 3.0", Arial, sans-serif;',
        '  --font-sdk-mono: "NK57 Monospace", Consolas, monospace;',
        "}",
        "",
        ".font-sdk-cjk-sc { font-family: var(--font-sdk-cjk-sc); }",
        ".font-sdk-cjk-jp { font-family: var(--font-sdk-cjk-jp); }",
        ".font-sdk-sans { font-family: var(--font-sdk-sans); }",
        ".font-sdk-mono { font-family: var(--font-sdk-mono); }",
        "",
    ]

    for (family, weight, style, stretch), items in sorted(groups.items()):
        source_items = sorted(items, key=lambda item: (item["extension"] != "ttf", item["path"]))
        src = ",\n       ".join(
            f'url("{css_url(item["path"])}") format("{item["format"]}")' for item in source_items
        )
        lines.extend(
            [
                "@font-face {",
                f'  font-family: "{family}";',
                f"  src: {src};",
                f"  font-weight: {weight};",
                f"  font-style: {style};",
                f"  font-stretch: {stretch};",
                "  font-display: swap;",
                "}",
                "",
            ]
        )

    return "\n".join(lines)


def build_manifest(root: Path, faces: list[dict[str, Any]]) -> dict[str, Any]:
    family_counts = Counter(face["family"] for face in faces)
    css_count = sum(1 for face in faces if face["css"])
    tracked_count = sum(1 for face in faces if face["tracked"])
    return {
        "schemaVersion": 1,
        "name": "@wheregone/fonts",
        "description": "Local font SDK manifest generated from this repository.",
        "summary": {
            "files": len({face["path"] for face in faces}),
            "faces": len(faces),
            "cssFaces": css_count,
            "families": len(family_counts),
            "trackedFaces": tracked_count,
            "untrackedFaces": len(faces) - tracked_count,
        },
        "families": [
            {"family": family, "faces": count}
            for family, count in sorted(family_counts.items(), key=lambda item: item[0].lower())
        ],
        "faces": faces,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the font SDK manifest and CSS.")
    parser.add_argument("--root", type=Path, default=repo_root())
    args = parser.parse_args()

    root = args.root.resolve()
    sdk_dir = root / "sdk"
    sdk_dir.mkdir(exist_ok=True)

    tracked_set = tracked_files(root)
    faces: list[dict[str, Any]] = []
    failures: list[str] = []

    for path in iter_font_files(root):
        try:
            faces.extend(read_faces(root, path, tracked_set))
        except Exception as exc:
            failures.append(f"{path.relative_to(root).as_posix()}: {exc}")

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    seen: Counter[str] = Counter()
    for face in faces:
        seen[face["id"]] += 1
        if seen[face["id"]] > 1:
            face["id"] = f'{face["id"]}-{seen[face["id"]]}'

    manifest = build_manifest(root, faces)
    (sdk_dir / "fonts.manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (sdk_dir / "fonts.css").write_text(build_css(faces), encoding="utf-8")

    print(
        f"Generated sdk/fonts.manifest.json and sdk/fonts.css "
        f"({manifest['summary']['files']} files, {manifest['summary']['faces']} faces)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
