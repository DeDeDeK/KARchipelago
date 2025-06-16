# Kirby Air Ride

- [Kirby Air Ride](#kirby-air-ride)
  - [Where is the options page?](#where-is-the-options-page)
  - [What does randomization do to this game?](#what-does-randomization-do-to-this-game)
  - [Which locations get shuffled?](#which-locations-get-shuffled)
  - [What is the goal of Kirby Air Ride?](#what-is-the-goal-of-kirby-air-ride)
  - [What does another world's item look like in Kirby Air Ride?](#what-does-another-worlds-item-look-like-in-kirby-air-ride)
  - [What happens when the player receives an item?](#what-happens-when-the-player-receives-an-item)
  - [I opened the game in Dolphin, but I don't have any of my starting items!](#i-opened-the-game-in-dolphin-but-i-dont-have-any-of-my-starting-items)
  - [I need help! What do I do?](#i-need-help-what-do-i-do)
  - [Known issues](#known-issues)
  - [Planned Features](#planned-features)
      - [Items](#items)
      - [Randomization](#randomization)
      - [Progression](#progression)
      - [Air Ride and Top Ride](#air-ride-and-top-ride)
      - [Multiplayer](#multiplayer)


## Where is the options page?

The [player options page for this game](../player-options) contains all the options you need to configure and export a
config yaml file.

## What does randomization do to this game?

Currently, randomization affects nothing in the game except the rewards you receive for completing City Trial checkboxes.

## Which locations get shuffled?

No locations are currently shuffled.

## What is the goal of Kirby Air Ride?

Have fun! There are also a few pre-selected archipelago goals for the game, all related to City Trial:
- Fill in over 100 Checklist Boxes!
  - this allows you to unlock viewing the game's ending
- Fill in N Checklist Boxes!
  - fill in as many checklist boxes as you want
- In one match, complete both Dragoon and Hydra
- Stadium: VS. KING DEDEDE KO King Dedede in less than a minute!

In general, all goals are related to completing checklist boxes.

## What does another world's item look like in Kirby Air Ride?

There is no change in the graphical appearance of other's items.

## What happens when the player receives an item?

Items are currently limited to patches and permanent patches. These will be applied immediately if the player is in City Trial when they are received, or they are applied at the beginning of the next City Trial run if they are not. Permanent patches are applied at the beginning of every City Trial run.

NOTE: you must collect a patch in the city after receving patch items for the stat increases/decreases to take effect. 

## I opened the game in Dolphin, but I don't have any of my starting items!

You must connect to the multiworld room to receive any items. 

## I need help! What do I do?

Try the troubleshooting steps in the [setup guide](/tutorial/Kirby%20Air%20Ride/setup/en). If you are still stuck, please ask in the "Kirby Air Ride" discussion thread in the "future-game-design" channel in the Archipelago Discord server! [Link](https://discord.com/channels/731205301247803413/1291501105389502554)

## Known issues

- DeathLink currently only reliably works one-way. The player can trigger DeathLink by dying but can only be killed by DeathLink some of the time/on certain vehicles.
- DeathLink for killing vehicles just takes health down to ~0 (likely due to floating point stuff)
- Restarting the game client results in all items being received again.
- Linux not working due to differences in dolphin memory engine (little endian on linux, read_byte differences)

Feel free to report any other issues or suggest improvements in the "Kirby Air Ride" discussion thread in the "future-game-design" channel in the Archipelago Discord server! [Link](https://discord.com/channels/731205301247803413/1291501105389502554)

## Planned Features

Much of the planned features are gated by progress on modding the game itself or finding proper memory addresses to read/write to. 

#### Items
- permanent increase/decrease item spawn rates as useful/filler/trap items
- food items as filler/useful
- kirby abilities as useful/filler/trap items
- kirby effects (such as "run amok") as useful/filler/trap items
- city trial events as useful/filler/trap items
- spawning boxes as filler/useful items
- checklist box fillers as progression item

#### Randomization
- randomization of checklist box rewards
- randomization of starting air ride machine

#### Progression
- "progressive stadium" items for City Trial, required to advance to the next stadium
- progressive kirby color unlocks
- progressive kirby ability unlocks
- progressive air ride machine unlocks
- progressive city trial event unlock items

#### Air Ride and Top Ride
- Air Ride checklist and items
- Top Ride checklist and items


#### Multiplayer
- All players receiving items