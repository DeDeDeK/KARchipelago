# Kirby Air Ride APWorld

- [Kirby Air Ride APWorld](#kirby-air-ride-apworld)
  - [What is this?](#what-is-this)
  - [How do I set this up?](#how-do-i-set-this-up)
  - [Game modes and goals](#game-modes-and-goals)
    - [City Trial](#city-trial)
    - [Air Ride](#air-ride)
    - [Top Ride](#top-ride)
    - [Mixing goals](#mixing-goals)
  - [Access gating](#access-gating)
  - [Cross-mode placement](#cross-mode-placement)
  - [What does randomization do to this game?](#what-does-randomization-do-to-this-game)
  - [What does another world's item look like in Kirby Air Ride?](#what-does-another-worlds-item-look-like-in-kirby-air-ride)
  - [What happens when the player receives an item?](#what-happens-when-the-player-receives-an-item)
    - [Checkbox filler items](#checkbox-filler-items)
    - [Patch cap increase items](#patch-cap-increase-items)
    - [Permanent patch increase items](#permanent-patch-increase-items)
    - [Stadium unlock items](#stadium-unlock-items)
    - [Spawn Rate Up items](#spawn-rate-up-items)
    - [Access-gating unlock items](#access-gating-unlock-items)
    - [When items are applied](#when-items-are-applied)
  - [Traps and TrapLink](#traps-and-traplink)
  - [EnergyLink](#energylink)
    - [Auto-Charge](#auto-charge)
  - [DeathLink](#deathlink)
  - [Other features](#other-features)
    - [Reveal checklists](#reveal-checklists)
    - [Server sync](#server-sync)
  - [I need help! What do I do?](#i-need-help-what-do-i-do)
  - [Known Issues](#known-issues)
  - [Planned Features](#planned-features)
  - [Contributing](#contributing)


## What is this?

This is an APWorld for the Archipelago multi-world, multi-game randomizer: [archipelago.gg](https://archipelago.gg/)

This APWorld allows you to play Kirby Air Ride in an Archipelago Multiworld, or solo.

## How do I set this up?

Setting up the game and instructions on where to get the apworld file, yaml file, and mod files are in the [setup guide](https://github.com/DeDeDeK/KARchipelago/blob/main/worlds/kirby_air_ride/docs/setup_en.md).

## Game modes and goals

Kirby Air Ride has three independent game modes: City Trial, Air Ride, and Top Ride. You can enable any combination of them, each with its own goal, locations, and progression settings. Setting a mode's goal to "None" disables that mode entirely, so none of its checklist locations will exist.

### City Trial

- **Fill in over 100 Checklist Boxes** (default). In the base game this unlocks viewing the ending.
- **Fill in N Checklist Boxes.** Choose the number from 1 to 120 with "Number of Checklist Boxes for City Trial".
- **Complete both Dragoon and Hydra in one match.** The standard legendary-machine checkbox from the base game.
- **Beat King Dedede.** KO King Dedede in under a minute in the VS. KING DEDEDE stadium.
- **Complete a specific list of checklist boxes.** You choose the exact boxes (or location group names) with "City Trial Goal Locations".
- **Max stats in one run.** Reach the per-stat patch cap target on every stat in a single City Trial round. Pairs well with Progressive Patch Caps, which makes the target reachable only after collecting Patch Cap Increase items.
- **None.** Disables City Trial.

### Air Ride

- **Fill in over 100 Checklist Boxes.**
- **Fill in N Checklist Boxes** (1 to 120).
- **Complete a specific list of checklist boxes** (via "Air Ride Goal Locations").
- **None** Disables Air Ride (default).

### Top Ride

- **Fill in over 100 Checklist Boxes.**
- **Fill in N Checklist Boxes** (1 to 120).
- **Complete a specific list of checklist boxes** (via "Top Ride Goal Locations").
- **None** Disables Top Ride (default).

### Mixing goals

You can mix and match goals across modes. When more than one mode has a goal, you only complete your game by completing every enabled goal.

## Access gating

Most categories of content can be locked behind AP items. When a category is gated, that content starts locked and you must find its unlock items to access it; the checkboxes and races that depend on it become logically reachable only once you have the unlock. When a category is not gated, that content is available from the start and no unlock items are placed for it.

The gateable categories are:

- **City Trial events** (Dyna Blade, Meteor, Tac, etc.)
- **Copy abilities** (Fire, Sword, Bomb, etc.). Affects both City Trial and Air Ride.
- **City Trial patch types** (Accel, Top Speed, Offense, etc.)
- **City Trial game items** (All Up, Speed Max, Candy, food, hazards, legendary parts, etc.)
- **Air ride machines.** Affects both City Trial and Air Ride.
- **City Trial box types** (Blue, Green, Red)
- **Air Ride courses**
- **Top Ride courses**
- **Top Ride items.** Items tied to copy abilities (Freeze Fan, Fire, Bomb, Walky) are gated by the copy ability unlock instead.
- **Kirby colors** (every color other than Pink). Affects all three modes.
- **City Trial stadiums.** When gated, you start with one random stadium unlocked and find the rest (see [Stadium unlock items](#stadium-unlock-items)).

When a category is ungated, the mod unlocks all of its content the instant you connect, so it is available from the very start of your run no matter which modes you have enabled. A few categories are normally unlocked in vanilla by completing specific in-game checklist squares — air ride machines, Kirby colors, the Nebula Belt course, the reward stadiums, and the Top Ride "New Item" types (Lantern, Who? Paint, Chickie). When one of those categories is ungated, the mod has already unlocked it at connect, so those checklist reward squares are not placed as items and are skipped. The only effect is cosmetic: you won't see those particular checkbox rewards (their description text or icon) appear in your own checklist. Nothing is lost for progression — the content is already available.

## Cross-mode placement

When you have more than one mode enabled, "Cross-Mode Placement" controls whether they share progression.

- **On (default):** any of your items can land at any of your checklist locations across every enabled mode. An Air Ride unlock might be found on a City Trial checkbox, and vice versa.
- **Off:** progression is kept separate per mode, so City Trial progress comes only from City Trial checks, Air Ride from Air Ride, and Top Ride from Top Ride. Two things still tie modes together: unlocks that genuinely apply to more than one mode (copy abilities and machines affect City Trial and Air Ride; colors affect all three) may appear in any mode they apply to, and only progression is locked. Non-progression items (checklist rewards, Spawn Rate Ups, traps, and filler) gate nothing, so they are still placed freely across enabled modes.

Items placed in other players' worlds are never affected either way.

## What does randomization do to this game?

Randomization decides which AP item is attached to each checkbox you complete, and which unlock items you must find to reach gated content. No in-game locations are physically shuffled: every checkbox still triggers its normal in-game result, except where gating replaces that result with the corresponding AP unlock (for example stadiums, courses, abilities, machines, and so on, when those categories are gated).

## What does another world's item look like in Kirby Air Ride?

There is no change in the graphical appearance of other worlds' items. Completing a checkbox sends whatever AP item is attached to that location.

## What happens when the player receives an item?

The items you can receive include:

- Checkbox filler items (one per mode)
- Patch cap increase items (City Trial)
- Permanent patch increase items (City Trial)
- Stadium unlock items (City Trial)
- Spawn Rate Up items (City Trial / Top Ride)
- Game item gives (boxes, food, copy abilities, legendary machine parts, All Up, etc.)
- Access-gating unlock items (events, abilities, machines, patch types, items, boxes, courses, colors, Top Ride items)
- Traps (1 HP Trap, stat-down patches, fake patches, hazards)

### Checkbox filler items

Receiving a checkbox filler item for a given checklist auto-completes a checklist block immediately. Look to the side of the checklist for the purple boxes. The game only shows up to 5 of them at once, but if you have unlocked more they are still yours and you can keep using them as they run out. There is a separate filler item for each mode (City Trial, Air Ride, Top Ride).

### Patch cap increase items

With "City Trial Progressive Patch Caps" enabled, the per-stat patch cap starts low and each Patch Cap Increase item raises it by one, up to your "Patch Cap Target". This is tracked per stat. For example, with a cap of 6, collecting a 7th Top Speed will drop you back to 6 until you raise the cap.

### Permanent patch increase items

With "City Trial Permanent Patches" enabled (the default), these items give a permanent +1 to a stat that persists for the rest of your run.

### Stadium unlock items

With "City Trial Stadiums Gated" enabled, stadiums must be found and unlocked, and receiving a stadium unlock item unlocks that stadium in-game. You always start with one random stadium already unlocked, chosen from any of the 24 stadiums (but never VS. KING DEDEDE when that is your goal).

### Spawn Rate Up items

With "Progressive Spawn Rate" enabled, the City Trial and Top Ride item spawn rate starts at your "Spawn Rate Min" and each Spawn Rate Up item raises it by 10% toward your "Spawn Rate Max". Air Ride has no spawn-rate scaling and is unaffected.

### Access-gating unlock items

When a category is gated (see [Access gating](#access-gating)), receiving its unlock item makes that content available for the rest of your run.

### When items are applied

City Trial items are applied immediately if you are in City Trial when they arrive, otherwise at the start of your next City Trial run. Permanent patch increases are applied at the start of every City Trial run.

NOTE: after receiving patch items, you must collect any patch in the city for the stat increases or decreases to take effect.

## Traps and TrapLink

Set "Trap Chance" above 0 to turn a percentage of your non-progression item slots into traps. Traps are grouped into categories you can weight independently: Direct Damage (1 HP Trap), Stat Debuff (All Down, stat-down patches, etc.), Fake Patches (items that look like stat-ups but are harmful), and Hazards (Panic Spin, Sensor Bomb, Gordo).

With "Trap Link" enabled, traps you receive are broadcast to other players who have TrapLink on, and you receive the traps they broadcast in return. This is independent of "Trap Chance": you can take part in TrapLink even with no traps in your own pool. TrapLink can be toggled in your yaml or from the in-game menu; the yaml only seeds the initial state and the in-game menu is authoritative after that.

## EnergyLink

EnergyLink is a City Trial feature. While it is on, collecting patches and destroying objects (rocks, trees, coral, houses, etc.) in the City contributes energy to the multiworld's shared pool, and you can spend that pool from within the game to receive items.

EnergyLink can be enabled in your yaml or from the in-game menu. The yaml only seeds the initial state on first connect; after that the in-game menu is authoritative for the rest of the session.

### Auto-Charge

Auto-Charge (Settings → Energy Link → Auto-Charge in the in-game menu) spends pooled energy to keep your machine's charge meter topped up. Instead of instantly snapping it to full, it adds a steady amount each frame, so it gently assists your own charging — holding A, or coasting and gliding — and your energy drains gradually rather than all at once.

The **Auto-Charge Rate** setting (Slow / Medium / Fast) controls how quickly the meter fills; a slower rate makes a given amount of energy last longer. The total energy spent to fill the meter is the same at every rate — only the pacing changes.

## DeathLink

DeathLink is supported and can be enabled in your yaml. When on, dying links your deaths with other DeathLink players in the multiworld.

## Other features

### Reveal checklists

With "Reveal Checklists" enabled, the checklists for each of your enabled modes start fully revealed instead of hidden.

### Server sync

The client syncs your completed AP checks to your in-game checklist every time you connect to the server. This keeps your game in sync with the server even if you lose your save file, start fresh for a same-slot co-op, or have had checks collected by another player.

## I need help! What do I do?

Try the troubleshooting steps in the [setup guide](https://github.com/DeDeDeK/KARchipelago/blob/main/worlds/kirby_air_ride/docs/setup_en.md).

If you are still stuck, please ask us over in the "Kirby Air Ride" discussion thread in the "future-game-design" channel in the Archipelago Discord server! [(Link)](https://discord.com/channels/731205301247803413/1291501105389502554)

## Known Issues

Known bugs and issues are tracked in the GitHub issues [here.](https://github.com/DeDeDeK/KARchipelago/issues?q=is%3Aissue%20state%3Aopen%20label%3Abug)

Feel free to report any issues or suggest improvements either there or in the "Kirby Air Ride" discussion thread in the "future-game-design" channel in the Archipelago Discord server [(Link)](https://discord.com/channels/731205301247803413/1291501105389502554)

## Planned Features

Many planned features are gated by progress on modding the game itself. Contributions are very welcome!

You can see a current list of planned features and other requests [here.](https://github.com/DeDeDeK/KARchipelago/issues?q=is%3Aissue%20state%3Aopen%20label%3Aenhancement)

## Contributing

Feel free to [raise an issue](https://github.com/DeDeDeK/KARchipelago/issues) or [submit a PR](https://github.com/DeDeDeK/KARchipelago/pulls)! And you can always pop into the [Discord channel](https://discord.com/channels/731205301247803413/1291501105389502554) to ask questions or collaborate!
