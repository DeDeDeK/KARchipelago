# Kirby Air Ride

- [Kirby Air Ride](#kirby-air-ride)
  - [What is this?](#what-is-this)
  - [Where do I get the apworld and yaml file?](#where-do-i-get-the-apworld-and-yaml-file)
  - [How do I set this up?](#how-do-i-set-this-up)
  - [What is the goal of Kirby Air Ride in Archipelago?](#what-is-the-goal-of-kirby-air-ride-in-archipelago)
    - [City Trial](#city-trial)
    - [Air Ride](#air-ride)
    - [Top Ride](#top-ride)
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
      - [Top Ride](#top-ride-1)
      - [Air Ride](#air-ride-1)
      - [Multiplayer](#multiplayer)
      - [Code/misc](#codemisc)
  - [Contributing](#contributing)

## What is this?

This is an APWorld for the Archipelago multi-world, multi-game randomizer: [archipelago.gg](https://archipelago.gg/)

## Where do I get the apworld and yaml file?

You can get the apworld file and an example player configuration yaml in the [releases page.](https://github.com/DeDeDeK/KARchipelago/releases)

## How do I set this up?

Follow the [setup guide (webhost link)](/tutorial/Kirby%20Air%20Ride/setup/en) or [setup guide (github)](https://github.com/DeDeDeK/KARchipelago/blob/main/worlds/kirby_air_ride/docs/setup_en.md).

## What is the goal of Kirby Air Ride in Archipelago?

Besides having fun being a part of a multiworld with friends, there are also a few pre-selected archipelago goals for the game that will result in a "game complete":

### City Trial
- Fill in over 100 Checklist Boxes!
  - in the base game, this allows you to unlock viewing the game's ending
- Fill in N Checklist Boxes!
  - fill in as many checklist boxes as you want, you can configure the number from 1-120.
- In one match, complete both Dragoon and Hydra!
  - this is the standard checkbox from the base game
- Stadium: VS. KING DEDEDE KO King Dedede in less than a minute!
- You can also specify the name of any checklist box to set that as your specific goal for City Trial.
- None
  - this disables City Trial from being a part of your world. No locations for City Trial will exist to be checked.

### Air Ride
- Fill in over 100 Checklist Boxes!
  - in the base game, this allows you to unlock viewing the game's ending
- Fill in N Checklist Boxes!
  - fill in as many checklist boxes as you want, you can configure the number from 1-120.
- You can also specify the name of any checklist box to set that as your specific goal for Air Ride.
- None
  - this disables Air Ride from being a part of your world. No locations for Air Ride will exist to be checked.

### Top Ride
- Fill in over 100 Checklist Boxes!
  - in the base game, this allows you to unlock viewing the game's ending
- Fill in N Checklist Boxes!
  - fill in as many checklist boxes as you want, you can configure the number from 1-120.
- You can also specify the name of any checklist box to set that as your specific goal for Top Ride.
- None
  - this disables Top Ride from being a part of your world. No locations for Top Ride will exist to be checked.

You can mix and match goals between all game modes. If there is a goal for multiple game modes, you can only complete your game by completing both goals.

You can mix and match goals between City Trial and Air Ride. If there is a goal for both City Trial and Air ride, you can only complete your game by completing both goals.

## What does randomization do to this game? Which locations get shuffled?

Currently, randomization affects nothing in the game except the AP items you receive for completing checkboxes or receive from other worlds.

No locations are currently shuffled. Eventually, all checkboxes will be able to be randomized. 

## What does another world's item look like in Kirby Air Ride?

There is no change in the graphical appearance of other's items. Completing checkboxes will earn whatever item is attached to that checkbox.

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

NOTE: There are currently no items that apply to Air Ride or Top Ride mode, but you can earn items for City Trial by completing Air Ride or Top Ride checkboxes.

### EnergyLink

If you have EnergyLink enabled in your yaml or if you enabled it in the client with `/energylink`, gathering patches in the City will add to the collective energy pool of the multiworld, as well as destroying objects (rocks, trees, coral, star pole, houses, etc.). You can spend this gathered energy to receive any (archipelago) item immediately! Use `/energylink_spend "Item Name" item_amount` in the Kirby Air Ride Client.

Each patch collected gives 1 energy, and each object destroyed gives .1 energy. Items by default cost 10 energy, except for All patches which cost 90.

For example, to buy 5 Top Speed Up patches (assuming you have 50 energy to spend):

`/energylink_spend "Top Speed Up" 5`

## I need help! What do I do?

Try the troubleshooting steps in the [setup guide (webhost link)](/tutorial/Kirby%20Air%20Ride/setup/en) or [(github link)](https://github.com/DeDeDeK/KARchipelago/blob/main/worlds/kirby_air_ride/docs/setup_en.md). If you are still stuck, please ask in the "Kirby Air Ride" discussion thread in the "future-game-design" channel in the Archipelago Discord server! [Link.](https://discord.com/channels/731205301247803413/1291501105389502554)

## Known issues

- DeathLink currently only reliably works one-way. The player can trigger DeathLink by dying quite reliably, but can only be killed by DeathLink some of the time/on certain vehicles.
- DeathLink for killing vehicles just takes health down to ~0 (likely due to floating point stuff)
- Restarting the game client results in all permanent patches being received again
- Energylink stops adding energy after a certain point for picking up patches (even below the max patch limit)
- Energylink is occasionally flaky with adding multiple items at once (via `amount` argument)
- Players can not receive items on the following stages due to stage ID conflicts: 
  - Stadium: DESTRUCTION DERBY 4
  - Stadium: DESTRUCTION DERBY 5
  - Stadium: SINGLE RACE 1
  - FANTASY MEADOWS
- Top Ride currently does not support items until a memory address is found that reflects whether we're in game in top
  ride or not
- Patch items for City Trial are not guaranteed to work depending on what vehicle you are on. They always work on compact star.

Feel free to report any other issues or suggest improvements in the "Kirby Air Ride" discussion thread in the "future-game-design" channel in the Archipelago Discord server [(Link)](https://discord.com/channels/731205301247803413/1291501105389502554) or in the issues [here](https://github.com/DeDeDeK/KARchipelago/issues).

## Planned Features

Much of the planned features are gated by progress on modding the game itself or finding proper memory addresses to read/write to. Contributions are very welcome! Eventually, we will see a hard cap on what we can do with Archipelago and will
need to work on creating Gecko codes and modifying the iso to make new features work.

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
- air ride speed increase item (permanent speed increases?)
- other air ride items

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

#### Top Ride
- Top Ride items

#### Air Ride
- Air Ride items

#### Multiplayer
- All players receiving items

#### Code/misc
- more fine-grained options for which traps or patches are enabled
- option to reveal (but not unlock) the whole checklist at game start by writing 10 to every checkbox?
- fully unlock every checkbox on game complete?
- yaml option to sync the local checklist state with the server checked locations upon connection. for people who don't care about saves being edited/wiped and want the convenience of not having to juggle save files for each lobby
- options presets that set goals for different "game modes" (killing enemies focused checkboxes, collecting items focused, etc.)
- enable lists of locations as goals. get every checkbox on the list to complete your game. Allows for making custom games, essentially
- energylink for air ride: laps completed, enemies killed
- energylink for top ride: laps completed
- kirby gets bigger as energylink grows?
- ItemLink
- performance pass on location checking
- possible variable deathlink cooldown?
- colored text for goal completion

## Contributing

Feel free to [raise an issue](https://github.com/DeDeDeK/KARchipelago/issues) or [submit a PR](https://github.com/DeDeDeK/KARchipelago/pulls)!  
