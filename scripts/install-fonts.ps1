param(
  [string]$Family = "",
  [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ManifestPath = Join-Path $Root "sdk\fonts.manifest.json"

if (-not (Test-Path $ManifestPath)) {
  throw "Missing sdk/fonts.manifest.json. Run: python scripts/build_font_sdk.py"
}

$Manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$FontDir = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$RegistryPath = "HKCU:\Software\Microsoft\Windows NT\CurrentVersion\Fonts"

if (-not $WhatIf) {
  New-Item -ItemType Directory -Force -Path $FontDir | Out-Null
}

$Faces = $Manifest.faces | Where-Object {
  $_.extension -in @("ttf", "otf", "ttc", "otc") -and
  ([string]::IsNullOrWhiteSpace($Family) -or $_.family -match $Family)
}

$Installed = 0
foreach ($Face in $Faces) {
  $Source = Join-Path $Root $Face.path
  if (-not (Test-Path $Source)) {
    Write-Warning "Missing font: $($Face.path)"
    continue
  }

  $Target = Join-Path $FontDir (Split-Path $Source -Leaf)
  $RegistryName = "$($Face.fullName) ($($Face.extension.ToUpperInvariant()))"

  if ($WhatIf) {
    Write-Host "Would install $($Face.path) -> $Target"
    continue
  }

  Copy-Item -LiteralPath $Source -Destination $Target -Force
  New-ItemProperty -Path $RegistryPath -Name $RegistryName -Value (Split-Path $Target -Leaf) -PropertyType String -Force | Out-Null
  $Installed += 1
}

Write-Host "Installed $Installed font faces for current user."
