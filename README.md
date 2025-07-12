# Kirby Air Ride APWorld

- [Kirby Air Ride APWorld](#kirby-air-ride-apworld)
  - [What is this?](#what-is-this)
  - [Where do I get the apworld?](#where-do-i-get-the-apworld)
  - [What is the goal of Kirby Air Ride in Archipelago?](#what-is-the-goal-of-kirby-air-ride-in-archipelago)
  - [What does randomization do to this game? Which locations get shuffled?](#what-does-randomization-do-to-this-game-which-locations-get-shuffled)
  - [What does another world's item look like in Kirby Air Ride?](#what-does-another-worlds-item-look-like-in-kirby-air-ride)
  - [What happens when the player receives an item?](#what-happens-when-the-player-receives-an-item)
    - [EnergyLink](#energylink)
  - [I need help! What do I do?](#i-need-help-what-do-i-do)
  - [Known issues](#known-issues)
  - [Planned Features](#planned-features)
      - [Items](#items)
      - [Randomization](#randomization)
      - [Progression](#progression)
      - [Air Ride and Top Ride](#air-ride-and-top-ride)
      - [Multiplayer](#multiplayer)
      - [Code/misc](#codemisc)
  - [Contributing](#contributing)


## What is this?

This is an APWorld for the Archipelago multi-world, multi-game randomizer: archipelago.gg

## Where do I get the apworld?

You can get the apworld file and an example player configuration yaml in the [releases page.](https://github.com/DeDeDeK/KARchipelago/releases)

## What is the goal of Kirby Air Ride in Archipelago?

Besides having fun being a part of a multiworld with friends, there are also a few pre-selected archipelago goals for the game, all related to City Trial, that will result in a "game complete":

- Fill in over 100 Checklist Boxes!
  - in the base game, this allows you to unlock viewing the game's ending
- Fill in N Checklist Boxes!
  - fill in as many checklist boxes as you want, you can configure the number from 1-120.
- In one match, complete both Dragoon and Hydra!
  - this is the standard checkbox from the base game
- Stadium: VS. KING DEDEDE KO King Dedede in less than a minute!

You can also specify the name of any checklist box to set that as your specific goal.

## What does randomization do to this game? Which locations get shuffled?

Currently, randomization affects nothing in the game except the AP items you receive for completing City Trial checkboxes or receive from other worlds.

No locations are currently shuffled. Eventually, all checkboxes will be able to be randomized. 

## What does another world's item look like in Kirby Air Ride?

There is no change in the graphical appearance of other's items. Completing checkboxes in City Trial checklist will earn whatever item is attached to that checkbox.

## What happens when the player receives an item?

Current items players are able to receive are:
- Patches (Top Speed Up, Boost Up, etc.)
- Trap Patches ("Top Speed Down, Boost Down, etc.)
- Permanent +1 Patch Increases
- "Effect" items
  - 1 HP Trap
  - Full Heal
  
Any items will be applied immediately if the player is in City Trial when they are received, or they are applied at the beginning of the next City Trial run if they are not. Permanent patch increases are applied at the start of every City Trial run (after a few seconds have elapsed). 

NOTE: you must collect any patch in the city after receiving patch items for the stat increases/decreases to take effect. 

### EnergyLink

If you have EnergyLink enabled in your yaml or if you enabled it in the client, gathering patches in the City will add to the collective energy pool of the multiworld. You can spend this gathered energy to receive any item immediately! Use `/energylink` and `/energylink_spend` in the Kirby Air Ride Client.

## I need help! What do I do?

Try the troubleshooting steps in the [setup guide](https://github.com/DeDeDeK/KARchipelago/blob/main/worlds/kirby_air_ride/docs/setup_en.md). If you are still stuck, please ask in the "Kirby Air Ride" discussion thread in the "future-game-design" channel in the Archipelago Discord server! [Link](https://discord.com/channels/731205301247803413/1291501105389502554)

## Known issues

- DeathLink currently only reliably works one-way. The player can trigger DeathLink by dying but can only be killed by DeathLink some of the time/on certain vehicles.
- DeathLink for killing vehicles just takes health down to ~0 (likely due to floating point stuff)
- Restarting the game client results in all items being received again.

Feel free to report any other issues or suggest improvements in the "Kirby Air Ride" discussion thread in the "future-game-design" channel in the Archipelago Discord server [(Link)](https://discord.com/channels/731205301247803413/1291501105389502554) or in the issues here. 

## Planned Features

Much of the planned features are gated by progress on modding the game itself or finding proper memory addresses to read/write to. Contributions are very welcome!

#### Items
- permanent increase/decrease item spawn rates as useful/filler/trap items
- food items as filler/useful
- kirby abilities as useful/filler/trap items
- kirby effects (such as "run amok") as useful/filler/trap items
- city trial events as useful/filler/trap items
- spawning boxes as filler/useful items
- checklist box fillers as progression item
- drop patches trap item
- physics-based trap items (altitude increase/decrease, teleport forward/backward/random location, gravity changes, etc.)

#### Randomization
- randomization of checklist box rewards
- randomization of starting air ride machine

#### Progression
- "progressive stadium" items for City Trial, required to advance to the next stadium
- progressive kirby color unlocks
- progressive kirby ability unlocks
- progressive air ride machine unlocks
- progressive city trial event unlock items
- progressive hot dogs/food items
- other progressive rng-related items

#### Air Ride and Top Ride
- Air Ride checklist and items
- Top Ride checklist and items

#### Multiplayer
- All players receiving items

#### Code/misc
- more fine-grained options for which traps or patches are enabled
- option to reveal (but not unlock) the whole checklist at game start by writing 10 to every checkbox?
- fully unlock every checkbox on game complete?
- yaml option to sync the local checklist state with the server checked locations upon connection. for people who don't care about saves being edited/wiped and want the convenience of not having to juggle save files for each lobby

## Contributing

Feel free to [raise an issue](https://github.com/DeDeDeK/KARchipelago/issues) or [submit a PR](https://github.com/DeDeDeK/KARchipelago/pulls)!  
