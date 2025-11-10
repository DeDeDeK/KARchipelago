#!/bin/bash

python Launcher.py "Build APWorlds" -- "Kirby Air Ride"
python Launcher.py "Generate Template Options" -- --skip_open_folder

cp build/apworlds/kirby_air_ride.apworld ~/Downloads
cp 'Players/Templates/Kirby Air Ride.yaml' ~/Downloads/kirby_air_ride.yaml
