# Setup Guide for Kirby Air Ride Archipelago

Welcome to Kirby Air Ride Archipelago! This guide will help you set up the game and play your first multiworld.
If you're playing Kirby Air Ride, you must follow a few simple steps to get started.

## Requirements

You'll need the following components to be able to play Kirby Air Ride:
* Install [Dolphin Emulator](https://dolphin-emu.org/download/). **We recommend using the latest release.**
    * Linux users can use the flatpak package
    [available on Flathub](https://flathub.org/apps/org.DolphinEmu.dolphin-emu).
* A Kirby Air Ride ISO (GKYE01) (North American version, NTSC-U), probably named "Kirby Air Ride (USA).iso".
  * CRC32: f1a3e7a2
  * MD5: bd936616ba7f998d8d0a1eb3f553b634
  * SHA-1: b57132b1d0990264c271a1ad2168aa75b93b2f92


## Setting Up a YAML

All players playing Kirby Air Ride must provide the room host with a YAML file containing the settings for their world.
Visit the [Kirby Air Ride options page](/games/Kirby%20Air%20Ride/player-options) to generate a YAML with your desired
options. Once you're happy with your settings, provide the room host with your YAML file and proceed to the next step.

## Connecting to a Room

The multiworld host will provide you a link to your room or the server name and port number.

Once you're ready, follow these steps to connect to the room:
1. Open Dolphin and use it to open the Kirby Air Ride ISO.
2. Start `ArchipelagoLauncher.exe` (without `.exe` on Linux) and choose `Kirby Air Ride Client`, which will open the
text client. If Dolphin is not already open, or you have yet to start a new file, you will be prompted to do so.
  * Once you've opened the ISO in Dolphin, the client should say "Dolphin connected successfully.".
3. Connect to the room by entering the server name and port number at the top and pressing `Connect`. For rooms hosted
on the website, this will be `archipelago.gg:<port>`, where `<port>` is the port number. If a game is hosted from the
`ArchipelagoServer.exe` (without `.exe` on Linux), the port number will default to `38281` but may be changed in the
`host.yaml`.
  * You will be prompted to enter your slot name, which is the name you selected when creating your yaml. Type that in and press enter.
4. You are now connected and ready to play!

## Troubleshooting

* Ensure you are running the same version of Archipelago on which the multiworld was generated.
* Ensure `kirby_air_ride.apworld` is not in your Archipelago installation's `custom_worlds` folder.
* Do not run the Archipelago Launcher or Dolphin as an administrator on Windows.
* Ensure that you do not have any Dolphin cheats or codes enabled. Some cheats or codes can unexpectedly interfere with
  emulation and make troubleshooting errors difficult. Some gecko or action replay codes may work, but they may also break
  the game state that archipelago depends on to function.
* Ensure that `Enable Emulated Memory Size Override` in Dolphin (under `Options` > `Configuration` > `Advanced`) is
  **disabled**.
* If the client cannot connect to Dolphin, ensure Dolphin is on the same drive as Archipelago. Having Dolphin on an
  external drive has reportedly caused connection issues.
* Ensure the `Fallback Region` in Dolphin (under `Options` > `Configuration` > `General`) is set to `NTSC-U`.
* If you run with a custom GC boot menu, you'll need to skip it by going to `Options` > `Configuration` > `GameCube`
  and checking `Skip Main Menu`.
