#!/bin/bash

uv run python Launcher.py "Build APWorlds" -- "Kirby Air Ride"
uv run python Launcher.py "Generate Template Options" -- --skip_open_folder

cp build/apworlds/kirby_air_ride.apworld ~/.local/share/Archipelago/worlds/
#cp build/apworlds/kirby_air_ride.apworld ~/Downloads
#cp 'Players/Templates/Kirby Air Ride.yaml' ~/Downloads/kirby_air_ride.yaml
