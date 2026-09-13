#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_PATH="$ROOT_DIR/dist/CubatureApp.app"
OUTPUT_DIR="$ROOT_DIR/dist"
DMG_PATH="$OUTPUT_DIR/CubatureApp-Installer.dmg"
RW_DMG="$OUTPUT_DIR/.CubatureApp-Installer-rw.dmg"
VOLUME_NAME="CubatureApp Installer"
BACKGROUND_DIR="/tmp/cubatureapp-dmg-background"
FONT_PATH="/System/Library/Fonts/Supplemental/Arial.ttf"

if [[ ! -d "$APP_PATH" ]]; then
    echo "Missing $APP_PATH. Run the macOS build first: python build.py" >&2
    exit 1
fi

rm -f "$DMG_PATH" "$RW_DMG"
rm -rf "$BACKGROUND_DIR"
mkdir -p "$BACKGROUND_DIR"

magick -size 900x560 gradient:'#c9efff-#ffffff' \
    -font "$FONT_PATH" -gravity NorthWest -fill '#073b5c' -pointsize 34 \
    -annotate +54+50 'CubatureApp' \
    -gravity NorthWest -fill '#426577' -pointsize 18 \
    -annotate +56+96 'Numerical cubature for polyhedral domains' \
    "$BACKGROUND_DIR/background.png"

hdiutil create -size 900m -fs HFS+ -volname "$VOLUME_NAME" -ov "$RW_DMG" >/dev/null
DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "$RW_DMG" | awk '/Apple_HFS/ {print $1; exit}')
MOUNT_POINT="/Volumes/$VOLUME_NAME"

cleanup() {
    hdiutil detach "$DEVICE" -quiet 2>/dev/null || true
    rm -rf "$BACKGROUND_DIR"
}
trap cleanup EXIT

mkdir -p "$MOUNT_POINT/.background"
cp "$BACKGROUND_DIR/background.png" "$MOUNT_POINT/.background/background.png"
cp -R "$APP_PATH" "$MOUNT_POINT/CubatureApp.app"
ln -s /Applications "$MOUNT_POINT/Applications"

osascript <<APPLESCRIPT
 tell application "Finder"
     tell disk "$VOLUME_NAME"
         open
         set current view of container window to icon view
         set toolbar visible of container window to false
         set statusbar visible of container window to false
         set bounds of container window to {120, 120, 1020, 680}
         set position of item "CubatureApp.app" to {250, 310}
         set position of item "Applications" to {650, 310}
         close
         open
     end tell
 end tell
APPLESCRIPT

hdiutil detach "$DEVICE" -quiet
trap - EXIT
hdiutil convert "$RW_DMG" -format UDZO -imagekey zlib-level=9 -o "$DMG_PATH" >/dev/null
rm -f "$RW_DMG"
echo "Created $DMG_PATH"
