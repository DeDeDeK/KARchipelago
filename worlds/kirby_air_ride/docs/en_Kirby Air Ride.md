# Kirby Air Ride APWorld

- [Kirby Air Ride APWorld](#kirby-air-ride-apworld)
  - [What is this?](#what-is-this)
  - [Where do I get the apworld and yaml file?](#where-do-i-get-the-apworld-and-yaml-file)
  - [How do I set this up?](#how-do-i-set-this-up)
  - [Game modes and goals](#game-modes-and-goals)
    - [City Trial](#city-trial)
    - [Air Ride](#air-ride)
    - [Top Ride](#top-ride)
    - [Mixing goals](#mixing-goals)
  - [Access gating](#access-gating)
  - [Shuffle checklist rewards](#shuffle-checklist-rewards)
  - [Checklist rewards gated](#checklist-rewards-gated)
  - [What does randomization do to this game?](#what-does-randomization-do-to-this-game)
  - [What does another world's item look like in Kirby Air Ride?](#what-does-another-worlds-item-look-like-in-kirby-air-ride)
  - [What happens when the player receives an item?](#what-happens-when-the-player-receives-an-item)
    - [Checkbox filler items](#checkbox-filler-items)
    - [Patch cap increase items](#patch-cap-increase-items)
    - [Permanent patch increase items](#permanent-patch-increase-items)
    - [Allowed item types](#allowed-item-types)
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


## What is this?

This is an APWorld for the Archipelago multi-world, multi-game randomizer: [archipelago.gg](https://archipelago.gg/)

## Where do I get the apworld and yaml file?

You can get the apworld file and an example player configuration yaml on the [releases page.](https://github.com/DeDeDeK/KARchipelago/releases)

## How do I set this up?

Follow the [setup guide](https://github.com/DeDeDeK/KARchipelago/blob/main/worlds/kirby_air_ride/docs/setup_en.md).

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
- **None** (default).

### Top Ride

- **Fill in over 100 Checklist Boxes.**
- **Fill in N Checklist Boxes** (1 to 120).
- **Complete a specific list of checklist boxes** (via "Top Ride Goal Locations").
- **None** (default).

### Mixing goals

You can mix and match goals across modes. When more than one mode has a goal, you only complete your game by completing every enabled goal. Your items all share a single pool across your enabled modes: any of your items can land at any of your checklist locations, so an Air Ride unlock might be found on a City Trial checkbox, and vice versa.

## Access gating

Most categories of content can be locked behind AP items. When a category is gated, that content starts locked and you must find its unlock items to access it; the checkboxes and races that depend on it become logically reachable only once you have the unlock. When a category is not gated, that content is available from the start and no unlock items are placed for it.

The gateable categories are:

- **City Trial events** (Dyna Blade, Meteor, Tac, etc.)
- **Copy abilities** (Fire, Sword, Bomb, etc.). Affects both City Trial and Air Ride.
- **City Trial patch types** (Boost, Top Speed, Offense, etc.)
- **City Trial game items** (All Up, Speed Max, Candy, food, hazards, legendary parts, etc.)
- **Air ride machines.** Affects both City Trial and Air Ride.
- **City Trial box types** (Blue, Green, Red)
- **Air Ride courses**
- **Top Ride courses**
- **Top Ride items.** Items tied to copy abilities (Freeze Fan, Fire, Bomb, Walky) are gated by the copy ability unlock instead.
- **Kirby colors** (every color other than Pink). Affects all three modes.
- **City Trial stadiums.** When gated, you start with one random stadium unlocked and find the rest (see [Stadium unlock items](#stadium-unlock-items)).

When a category is ungated, the mod unlocks all of its content the instant you connect, so it is available from the very start of your run no matter which modes you have enabled. A few categories are normally unlocked in vanilla by completing specific in-game checklist squares — air ride machines, Kirby colors, the Nebula Belt course, the reward stadiums, and the Top Ride "New Item" types (Lantern, Who? Paint, Chickie). When one of those categories is ungated, the mod has already unlocked it at connect, so those checklist reward squares are not placed as items and are skipped. The only effect is cosmetic: you won't see those particular checkbox rewards (their description text or icon) appear in your own checklist. Nothing is lost for progression — the content is already available.

## Shuffle checklist rewards

Many checklist boxes award a specific reward when ticked in the base game: a machine, a Kirby color, a music track, a sound test, a Dragoon or Hydra part, and so on. "Shuffle Checklist Rewards" controls only those reward items.

- **On (default):** each reward is shuffled into the multiworld like any other item, so it can turn up anywhere your items can, across any of your enabled modes.
- **Off:** every reward is placed back on the box that awards it in the base game, including the Dragoon and Hydra parts, so ticking that box gives what it gave in the original game.

A couple of edge cases when this is off: a reward whose native box is excluded from receiving good items (for example a box behind a progression flag you left off) is pinned only when it is a filler reward — a more valuable reward there is shuffled instead. And in a very tight single-mode seed, some filler rewards may shuffle rather than pin if their native box is needed to keep progression placeable. Content delivered by other unlock items (extra machines, hidden stadiums, the spare Kirby colors, and so on) still randomizes either way.

## Checklist rewards gated

Some checklist boxes award a minor extra when ticked: a music track, a sound test entry, an ending, a Top Ride rule, and so on. "Checklist Rewards Gated" controls whether those non-progression rewards are part of the multiworld at all.

- **Off (default):** none of these rewards are placed; the mod unlocks them all the instant you connect (the same way an ungated category works), and the checklist boxes that would have awarded them carry ordinary multiworld items instead. This leaves more room on your checklist boxes for the gating categories and other items. Because the rewards are no longer in the pool, "Shuffle Checklist Rewards" has nothing to act on for them.
- **On:** each such reward is an item you find in the multiworld, and "Shuffle Checklist Rewards" decides where it can land.

The Dragoon and Hydra parts are never affected — they are progression (they build the legendary machines), so they always stay in the multiworld regardless of this option. Turning this off is a good way to thin out low-value cosmetic items, at the cost of those checklist boxes no longer feeling like they "give" anything in-game.

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
- Traps (1 HP Trap, stat-down patches, fake patches)

### Checkbox filler items

Receiving a checkbox filler item for a given checklist auto-completes a checklist block immediately. Look to the side of the checklist for the purple boxes. The game only shows up to 5 of them at once, but if you have unlocked more they are still yours and you can keep using them as they run out. There is a separate filler item for each mode (City Trial, Air Ride, Top Ride).

### Patch cap increase items

With "City Trial Progressive Patch Caps" enabled, the per-stat patch cap starts low and each Patch Cap Increase item raises it by one, up to your "Patch Cap Target". This is tracked per stat. For example, with a cap of 6, collecting a 7th Top Speed will drop you back to 6 until you raise the cap.

### Permanent patch increase items

These items give a permanent +1 to a City Trial stat that persists for the rest of your run. They are in the pool as long as "Permanent Patches" is among your "Allowed Item Types" (see below).

### Allowed item types

"Allowed Item Types" controls which categories of optional (non-progression) give items appear in your pool. All categories are on by default; removing one keeps all of that category's items out of your pool. It is independent of "Trap Types" — trap items are governed only by that option, so a category here never adds or removes traps. The categories are: Permanent Patches, City Trial Item Gives (boxes, single-stat patches, food, candy, All Up, hazards, legendary-part spawns, etc.), City Trial Event Gives, Copy Ability Gives, and Top Ride Item Gives.

Note: "City Trial Item Gives" doubles as Air Ride's filler source and "Top Ride Item Gives" as Top Ride's, so in an Air-Ride-only or Top-Ride-only seed removing the corresponding category can leave excluded checklist boxes with nothing to fill them and will be rejected with a clear error.

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

Set "Trap Chance" above 0 to turn a percentage of your non-progression item slots into traps. "Trap Types" chooses which categories are in play (all on by default), and the selected categories are drawn at equal weight: Direct Damage (1 HP Trap), Stat Debuff (All Down, stat-down patches, etc.), and Fake Patches (items that look like stat-ups but are harmful).

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

**IMPORTANT:** Checks synced from the server are initially only *visible* in the checklist. They are unlocked by entering and then exiting (or normally finishing) a run in the relevant mode, which triggers the unlocking process for those checks.

## I need help! What do I do?

Try the troubleshooting steps in the [setup guide](https://github.com/DeDeDeK/KARchipelago/blob/main/worlds/kirby_air_ride/docs/setup_en.md).

If you are still stuck, please ask us in the "Kirby Air Ride" discussion thread in the "future-game-design" channel in the Archipelago Discord server! [(Link)](https://discord.com/channels/731205301247803413/1291501105389502554)
