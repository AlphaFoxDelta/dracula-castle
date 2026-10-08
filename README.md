# dracula-castle

A text adventure game. Explore Dracula's castle, arm yourself, and face
Dracula himself in a real fight. Win if you are prepared and clever. Lose
if you are not.

This was my first real Python project, written for a school assignment. I
have since expanded it well beyond the homework: a bigger castle, boss
fights, NPCs, puzzles, crafting, and multiple endings. I am keeping it here
exactly for that reason: it is where I started, and it shows how far a
little practice goes.

## How to play

```bash
python3 dracula_castle.py
```

Move with `go North`, `go South`, `go East`, `go West`, `go Up`, `go Down`.
Pick things up with `get <item name>`. Type `help` for the full command
list, `save` to save your game, and `quit` to stop.

The castle has 13 rooms. Six weapons are hidden through the halls: the
Sunlight Amulet, the Crucifix, Holy Water, the Garlic Necklace, the Wooden
Stake, and the Silver Dagger. The deeper rooms hold supplies like a Healing
Tonic and a Sacred Chalice, plus a Chapel Key for a locked door. Gold coins
are scattered in forgotten corners. Watch your step: not every room is safe.

Not every resident is hostile. A prisoner in the dungeon will trade hints,
and a merchant lurks in the secret passage, selling tonics for gold.

## The fights

Dracula's brides nest in the chapel and the bell tower, and they do not
let visitors pass unchallenged. Fights are turn-based: attack with a weapon,
spend a turn healing, or flee to regroup. Each weapon hits differently. The
stake hits hardest but breaks after two uses, holy water burns but the vial
runs dry, and garlic and the crucifix weaken your enemy's attacks.

When you are ready, walk north from the Secret Passage into Dracula's Lair.
He has 120 HP and hits back every turn. Ring the bell tower's bell before
you go in, and combine holy water with a wooden stake if you want the best
weapon in the game.

## Endings

How it ends is up to you. Destroy Dracula outright for the dawn ending.
Be thorough, ring the bell, destroy his brides, and forge the Blessed
Stake, and you will earn the legendary ending. Or, when he is beaten and
begging, take his offer instead, and see what eternal night feels like.

## What I cleaned up from the school version

The version I turned in for class had a few bugs:

- Typing `get` in a room with no item crashed the game.
- Typing `go` without a direction crashed the game.
- The status screen was a raw Python list. Now it reads like a game.

The original six rooms and six items are all still there, in the same
places. The expansion just gave them a bigger castle to sit in.

## What I would do differently now

A Room class instead of nested dictionaries. A proper game state object
instead of a dict passed between functions. And a real parser instead of
startswith checks, so "take the amulet" works as well as "get sunlight
amulet." But it works, it is finished, and it is fun, which is more than
most first projects get to say.
