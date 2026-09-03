#!/bin/bash
set -euo pipefail

BUILT="build/apworlds/kirby_air_ride.apworld"
INSTALL_DIR="$HOME/.local/share/Archipelago/worlds"

# Drop the previous artifact first so a failed build can't leave a stale one to install
rm -f "$BUILT"

uv run python Launcher.py "Build APWorlds" -- "Kirby Air Ride" --skip_open_folder
uv run python Launcher.py "Generate Template Options" -- --skip_open_folder

if [[ ! -f "$BUILT" ]]; then
    echo "Build produced no $BUILT - not installing" >&2
    exit 1
fi

mkdir -p "$INSTALL_DIR"
cp "$BUILT" "$INSTALL_DIR/"
echo "Installed $(basename "$BUILT") to $INSTALL_DIR"
