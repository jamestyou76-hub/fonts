# Fonts SDK

This repository is structured as a usable local font SDK. Raw font binaries stay in their source folders, while `sdk/` exposes stable machine-readable and Web-consumable entrypoints.

## Structure

- `doc-font/`: document and CJK fonts.
- `italic/`: display and italic fonts.
- `narrow/`: narrow monospace font family files.
- `sdk/fonts.manifest.json`: generated font inventory for tools.
- `sdk/fonts.css`: generated `@font-face` entrypoint for `.ttf` and `.otf` fonts.
- `scripts/build_font_sdk.py`: regenerates SDK outputs from local font files.
- `scripts/validate_font_sdk.py`: validates that manifest files exist and fonts are readable.
- `scripts/install-fonts.ps1`: installs fonts for the current Windows user.
- `scripts/install-fonts.sh`: installs fonts for macOS/Linux user font folders.

Archive and installer files such as `.rar` and `.exe` are intentionally not treated as SDK font assets.

## Use In Web/CSS

Import the generated stylesheet:

```css
@import "./sdk/fonts.css";

body {
  font-family: var(--font-sdk-cjk-sc);
}

code {
  font-family: var(--font-sdk-mono);
}
```

Provided CSS variables:

- `--font-sdk-cjk-sc`
- `--font-sdk-cjk-jp`
- `--font-sdk-sans`
- `--font-sdk-mono`

Provided utility classes:

- `.font-sdk-cjk-sc`
- `.font-sdk-cjk-jp`
- `.font-sdk-sans`
- `.font-sdk-mono`

## Use In Tooling

Read `sdk/fonts.manifest.json`. Each face includes family, subfamily, path, format, weight, style, size, collection index, CSS eligibility, and whether the source file is tracked by Git.

```bash
python scripts/build_font_sdk.py
python scripts/validate_font_sdk.py
```

## Install Locally

Windows, current user:

```powershell
.\scripts\install-fonts.ps1
.\scripts\install-fonts.ps1 -Family "Noto Sans CJK SC"
.\scripts\install-fonts.ps1 -WhatIf
```

macOS/Linux:

```bash
sh scripts/install-fonts.sh
sh scripts/install-fonts.sh "Noto Sans CJK SC"
```

## Publish Rule

Before publishing or pushing an SDK release, run validation and keep generated SDK files in sync with the version-controlled font files.
