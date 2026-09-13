#!/usr/bin/env bash
# Builds PlutoTheCat.dll with Mono msbuild and assembles the Thunderstore / r2modman zip.
# Requirements: mono + msbuild + nuget (Mono.framework), python3 + Pillow for the art.
set -euo pipefail
cd "$(dirname "$0")"
VERSION=$(python3 -c "import json;print(json.load(open('thunderstore/manifest.json'))['version_number'])")

echo "==> regenerating art"
python3 tools/make_art.py

echo "==> restoring packages"
( cd PlutoTheCat && nuget restore packages.config -PackagesDirectory packages -ConfigFile nuget.config >/dev/null )

echo "==> building"
( cd PlutoTheCat && msbuild PlutoTheCat.csproj -p:Configuration=Release -v:m -nologo )

echo "==> validating"
python3 tools/validate.py

echo "==> packaging"
rm -rf dist && mkdir -p dist/pkg/plugins
cp PlutoTheCat/bin/Release/PlutoTheCat.dll dist/pkg/plugins/
cp thunderstore/manifest.json thunderstore/README.md thunderstore/CHANGELOG.md thunderstore/icon.png thunderstore/pluto_check.sh dist/pkg/
( cd dist/pkg && zip -qr "../Pluto_The_Cat-${VERSION}.zip" . )
rm -rf dist/pkg
ls -la dist/
echo "==> done: dist/Pluto_The_Cat-${VERSION}.zip"
