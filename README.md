# dracula-castle

A text adventure game. Explore Dracula's castle, collect 6 items, then face
Dracula himself. Win if you are prepared. Lose if you are not.

This was my first real Python project, written for a school assignment. I am
keeping it here exactly for that reason: it is where I started. Everything
else on my profile came after this.

## How to play

```bash
python3 dracula_castle.py
```

Move with `go North`, `go South`, `go East`, `go West`. Pick things up with
`get <item name>`. Type `quit` or `exit` to stop.

There are 6 items hidden around the castle: the Sunlight Amulet, the
Crucifix, Holy Water, the Garlic Necklace, the Wooden Stake, and the Silver
Dagger. Find them all before you walk into Dracula's Lair, or it does not
end well for you.

## What I cleaned up

The version I turned in for class had a few bugs I have since fixed:

- Typing `get` in a room with no item crashed the game. It does not anymore.
- Typing `go` without a direction crashed the game. It does not anymore.
- The status screen now shows your exits as a readable list and tracks how
  many of the 6 items you have collected.

The game itself is unchanged. Same rooms, same items, same Dracula.

## What I would do differently now

Honestly, almost everything. A dictionary of rooms with string keys works,
but a Room class would be cleaner. The game state lives in globals, which
made the cleanup harder than it needed to be. And there is no save feature,
no combat, no real puzzles, just walking and collecting.

But that is the point of keeping it. It works, it is finished, and it
reminds me how far a little practice goes.
