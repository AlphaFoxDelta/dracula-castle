# Dracula's Castle - a text adventure game.
# My first real Python project, written for a school assignment.
# Later I expanded it: a bigger castle, a real boss fight with Dracula,
# traps, locked doors, and a save system. Same game at heart, just more of it.

import copy
import json
import os
import random

SAVE_FILE = "dracula_save.json"

ROOM_DEFS = {
    "Grand Foyer": {
        "description": (
            "You stand in the Grand Foyer. Dust sheets drape the furniture like sleeping "
            "ghosts, and a chandelier of black candles hangs overhead, unlit. Somewhere "
            "above you, something heavy drags across the floor."
        ),
        "item": None,
        "directions": {"East": "Living Room"},
    },
    "Living Room": {
        "description": (
            "The Living Room reeks of old smoke. A fireplace full of cold ash squats "
            "beneath a portrait whose painted eyes seem to follow you around the room."
        ),
        "item": "Sunlight Amulet",
        "directions": {"West": "Grand Foyer", "North": "Library", "South": "Kitchen", "East": "Secret Passage"},
    },
    "Library": {
        "description": (
            "Floor-to-ceiling shelves sag with rotting books. Pages rustle in the dark "
            "though there is no wind. A stone staircase spirals up into shadow."
        ),
        "item": "Crucifix",
        "directions": {"South": "Living Room", "East": "Study", "Up": "Bell Tower"},
    },
    "Study": {
        "description": (
            "A desk buried in yellowed letters, an inkwell dry for a century. One letter "
            "is newer than the rest. It reads: 'Forgive me.' A heavy oak door leads east."
        ),
        "item": "Holy Water",
        "directions": {"West": "Library", "East": "Chapel"},
    },
    "Kitchen": {
        "description": (
            "Pots hang from rusted hooks over a dead stove. Something scuttles behind "
            "the flour sacks and goes very quiet. Stone steps lead down into the dark."
        ),
        "item": "Garlic Necklace",
        "directions": {"North": "Living Room", "East": "Armory", "Down": "Wine Cellar"},
    },
    "Armory": {
        "description": (
            "Rusted swords line the walls. Empty suits of armor stand at attention, "
            "guarding nothing. An iron grate in the floor leads down."
        ),
        "item": "Wooden Stake",
        "directions": {"West": "Kitchen", "Down": "Dungeon"},
    },
    "Secret Passage": {
        "description": (
            "A narrow corridor behind the walls. The stones sweat, and the air smells of "
            "earth. Ahead, the passage opens into something vast and cold."
        ),
        "item": "Silver Dagger",
        "directions": {"West": "Living Room", "North": "Dracula's Lair"},
    },
    "Wine Cellar": {
        "description": (
            "Barrels loom in the dark, stacked to the ceiling. One of them leans at a "
            "bad angle, looking ready to fall."
        ),
        "item": "Healing Tonic",
        "directions": {"Up": "Kitchen"},
    },
    "Dungeon": {
        "description": (
            "Chains hang from the walls and straw covers the floor. The straw moves. "
            "Rats, dozens of them, eyes shining in the dark."
        ),
        "item": "Chapel Key",
        "directions": {"Up": "Armory"},
    },
    "Chapel": {
        "description": (
            "Moonlight falls through a shattered stained-glass window, painting the altar "
            "red and gold. Dust hangs in the light like snow. For the first time since you "
            "arrived, you feel safe."
        ),
        "item": "Sacred Chalice",
        "directions": {"West": "Study"},
    },
    "Bell Tower": {
        "description": (
            "Wind howls through the open arches. Far below, the castle sprawls dark and "
            "silent. A thick rope hangs from the great bell overhead."
        ),
        "item": None,
        "directions": {"Down": "Library"},
    },
    "Dracula's Lair": {
        "description": (
            "A vast chamber of black marble. At its heart sits an open coffin. The air is "
            "ice, and the shadows are wrong."
        ),
        "item": None,
        "directions": {},
    },
}

# The six original weapons. Damage, flavor text, and how they wear out.
WEAPONS = {
    "Sunlight Amulet": {"damage": 15, "text": "You raise the Sunlight Amulet. Searing light floods the chamber and Dracula screams."},
    "Silver Dagger": {"damage": 12, "text": "You slash with the Silver Dagger, opening a smoking wound."},
    "Crucifix": {"damage": 10, "text": "You hold the Crucifix high. Dracula recoils, hissing.", "weakens": 2},
    "Garlic Necklace": {"damage": 6, "text": "You press the Garlic Necklace forward. Dracula gags and staggers.", "weakens": 1},
    "Holy Water": {"damage": 22, "text": "You hurl Holy Water. It burns him like acid.", "uses": 3},
    "Wooden Stake": {"damage": 35, "text": "You drive the Wooden Stake toward his heart.", "uses": 2},
}

CONSUMABLES = {
    "Healing Tonic": {"heal": 30, "text": "You drink the Healing Tonic. Warmth spreads through your limbs."},
    "Sacred Chalice": {"heal": "full", "text": "You drink from the Sacred Chalice. Your wounds close as if they were never there."},
}

TRAPS = {
    "Wine Cellar": {"damage": 8, "text": "A barrel breaks loose and crashes into you! (-8 HP)"},
    "Dungeon": {"damage": 10, "text": "Rats swarm out of the straw, biting at your ankles! (-10 HP)"},
}

DRACULA_ATTACKS = [
    "Dracula lunges, claws raking across your arm!",
    "Dracula moves faster than sight and slams you into the marble!",
    "Cold hands close around your throat and squeeze!",
    "Dracula's eyes flare, and pain lances through your skull!",
]

TOTAL_COLLECTIBLES = 9


def new_game():
    """Fresh game state."""
    return {
        "current_room": "Grand Foyer",
        "inventory": {},  # item name -> uses left (None means unlimited)
        "hp": 100,
        "max_hp": 100,
        "dracula_hp": 120,
        "dracula_max_hp": 120,
        "dracula_penalty": 0,
        "taken_rooms": [],
        "visited": [],
        "chapel_unlocked": False,
        "bell_rung": False,
    }


def build_rooms(state):
    """Rebuild the room map from the pristine definitions, minus picked-up items."""
    rooms = copy.deepcopy(ROOM_DEFS)
    for room_name in state["taken_rooms"]:
        rooms[room_name]["item"] = None
    return rooms


def find_item(name, collection):
    """Case-insensitive lookup of an item name. Returns the real name or None."""
    for real_name in collection:
        if real_name.lower() == name.strip().lower():
            return real_name
    return None


def get_input(prompt):
    """Read a line of input. Ctrl+D / end of stream quits cleanly instead of crashing."""
    try:
        return input(prompt)
    except EOFError:
        return "quit"


def show_status(state, rooms):
    """Print where you are, what is here, your health, and your inventory."""
    room = rooms[state["current_room"]]
    print()
    print(room["description"])
    if room["item"]:
        print(f"You see a {room['item']} here.")
    if room["directions"]:
        print("Exits: " + ", ".join(room["directions"].keys()))
    else:
        print("There are no exits.")
    print(f"Health: {state['hp']}/{state['max_hp']}")
    if state["inventory"]:
        print("Inventory: [" + ", ".join(state["inventory"].keys()) + "]")
    else:
        print("Inventory: [Empty]")
    print(f"Items collected: {len(state['taken_rooms'])}/{TOTAL_COLLECTIBLES}")


def move_between_rooms(state, rooms, command):
    """Handle 'go <direction>', including the locked chapel door."""
    parts = command.split(" ", 1)
    if len(parts) < 2 or not parts[1].strip():
        print("Go where? Try: go North")
        return
    direction = parts[1].strip().capitalize()
    current = state["current_room"]
    if direction not in rooms[current]["directions"]:
        print("You can't go that way.")
        return
    target = rooms[current]["directions"][direction]
    if target == "Chapel" and not state["chapel_unlocked"]:
        if "Chapel Key" in state["inventory"]:
            state["chapel_unlocked"] = True
            print("You unlock the chapel door with the Chapel Key.")
        else:
            print("The chapel door is locked tight. You need a key.")
            return
    state["current_room"] = target
    # Traps spring the first time you enter a trapped room.
    if target in TRAPS and target not in state["visited"]:
        trap = TRAPS[target]
        state["hp"] -= trap["damage"]
        print(trap["text"])
        if state["hp"] <= 0:
            state["hp"] = 0
    if target not in state["visited"]:
        state["visited"].append(target)
    if target == "Dracula's Lair":
        start_combat(state)


def grab_item(state, rooms, command):
    """Handle 'get <item>'."""
    room_item = rooms[state["current_room"]]["item"]
    if room_item is None:
        print("There is nothing to pick up here.")
        return
    wanted = command[4:].strip()
    if not wanted:
        print("Get what?")
        return
    if wanted.lower() != room_item.lower():
        print("There is no such item here.")
        return
    uses = None
    if room_item in WEAPONS and "uses" in WEAPONS[room_item]:
        uses = WEAPONS[room_item]["uses"]
    if room_item in CONSUMABLES:
        uses = 1
    state["inventory"][room_item] = uses
    state["taken_rooms"].append(state["current_room"])
    rooms[state["current_room"]]["item"] = None
    print(f"You picked up the {room_item}.")


def use_item(state, command):
    """Handle 'use <item>' for consumables like the tonic and chalice."""
    wanted = command[4:].strip()
    if not wanted:
        print("Use what?")
        return
    name = find_item(wanted, state["inventory"])
    if name is None:
        print("You don't have that.")
        return
    if name not in CONSUMABLES:
        print(f"You can't use the {name} that way. (Weapons are for attacking.)")
        return
    info = CONSUMABLES[name]
    print(info["text"])
    if info["heal"] == "full":
        state["hp"] = state["max_hp"]
    else:
        state["hp"] = min(state["max_hp"], state["hp"] + info["heal"])
    del state["inventory"][name]
    print(f"Health: {state['hp']}/{state['max_hp']}")


def dracula_attack(state):
    """Dracula takes his turn. Returns True if the player is still alive."""
    damage = max(5, random.randint(10, 16) - state["dracula_penalty"])
    print(random.choice(DRACULA_ATTACKS) + f" (-{damage} HP)")
    state["hp"] -= damage
    if state["hp"] <= 0:
        state["hp"] = 0
        print("\nThe chamber goes dark. Dracula feeds, and the castle keeps its secret.")
        return False
    return True


def do_attack(state, command):
    """Handle 'attack <item>' during the boss fight."""
    wanted = command[len("attack"):].strip()
    if wanted.lower().startswith("with "):
        wanted = wanted[5:]
    if not wanted:
        print("Attack with what?")
        return
    name = find_item(wanted, state["inventory"])
    if name is None:
        print("You don't have that.")
        return
    if name not in WEAPONS:
        print(f"The {name} is not a weapon.")
        return
    weapon = WEAPONS[name]
    print(weapon["text"])
    damage = random.randint(weapon["damage"] - 2, weapon["damage"] + 2)
    state["dracula_hp"] -= damage
    print(f"Dracula takes {damage} damage. ({max(0, state['dracula_hp'])}/{state['dracula_max_hp']} HP)")
    if "weakens" in weapon:
        state["dracula_penalty"] += weapon["weakens"]
        print("Dracula's attacks grow weaker.")
    if "uses" in weapon:
        state["inventory"][name] -= 1
        if state["inventory"][name] <= 0:
            del state["inventory"][name]
            print(f"The {name} is spent!" + (" It splinters into pieces." if name == "Wooden Stake" else ""))


def start_combat(state):
    """The boss fight. Runs until someone wins or the player flees."""
    if state["bell_rung"]:
        state["dracula_hp"] -= 10
        print("The bell's toll still echoes through the castle. Dracula is rattled. (-10 HP)")
    print("\nCount Dracula rises from the coffin, eyes burning red.")
    print("'You carry light into MY house? Let us see how long it lasts.'\n")
    missing = [w for w in WEAPONS if w not in state["inventory"]]
    if missing:
        print("You face him without all six weapons. Brave. Probably fatal.\n")

    while state["dracula_hp"] > 0 and state["hp"] > 0:
        print(f"--- Your HP: {state['hp']}/{state['max_hp']} | Dracula HP: {max(0, state['dracula_hp'])}/{state['dracula_max_hp']} ---")
        command = get_input("Fight! (attack <weapon> / use <item> / flee): ").strip().lower()
        if not command:
            continue
        if command == "flee":
            state["current_room"] = "Secret Passage"
            state["dracula_hp"] = min(state["dracula_max_hp"], state["dracula_hp"] + 10)
            print("You sprint back into the Secret Passage. Behind you, Dracula laughs, and catches his breath. (+10 HP)")
            return
        if command.startswith("attack"):
            do_attack(state, command)
        elif command.startswith("use "):
            use_item(state, command)
        elif command in ("quit", "exit"):
            print("Quitting game. Goodbye!")
            raise SystemExit
        else:
            print("You're fighting for your life! Attack with a weapon, use an item, or flee.")
        if state["dracula_hp"] <= 0:
            break
        if not dracula_attack(state):
            return

    if state["dracula_hp"] <= 0:
        print("\nDracula staggers, clutches his chest, and collapses into dust and old cloth.")
        print("Dawn breaks through the high windows. You walk out of the castle into the morning, alive.")
        raise SystemExit


def save_game(state):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        print(f"Game saved to {SAVE_FILE}.")
    except OSError as e:
        print(f"Could not save the game: {e}")


def load_game():
    try:
        with open(SAVE_FILE) as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        print(f"Could not load the game: {e}")
        return None


def show_intro():
    """Display the game introduction."""
    print("\nWelcome to Dracula's Castle!\n")
    print("*** STORYLINE ***\n")
    print("After returning home from a long, busy day at school, you quickly fall asleep.")
    print("You soon awaken to find that you are no longer in your bedroom.")
    print("You appear to now be standing in the foyer of a large, extravagant castle.")
    print("It is then you hear a deep, disembodied voice echo throughout the room.")
    print("'I have brought you here in the hopes that you may prove a challenge.")
    print("I am Count Dracula, and you are now in my domain!'")
    print("Travel the castle and arm yourself before facing Dracula.")
    print("Six weapons are hidden in these halls. The deeper rooms hold supplies,")
    print("but they are not unguarded. Do not face him unprepared,")
    print("or you will never make it home alive!\n")


def show_help():
    """Display the command list."""
    print("\n*** COMMANDS ***")
    print("  go <direction>     Move: go North, go South, go East, go West, go Up, go Down")
    print("  get <item>         Pick up an item")
    print("  use <item>         Drink a tonic or chalice")
    print("  attack <weapon>    Fight Dracula (in his lair)")
    print("  flee               Run from the fight, back to the Secret Passage")
    print("  look               Look around the room again")
    print("  pull rope          Ring the bell in the Bell Tower (once)")
    print("  save               Save your game")
    print("  load               Load your saved game")
    print("  help               Show this list")
    print("  quit               Quit the game\n")


def main():
    state = new_game()
    if os.path.exists(SAVE_FILE):
        answer = get_input("A saved game exists. Load it? (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            loaded = load_game()
            if loaded:
                state = loaded
    rooms = build_rooms(state)

    show_intro()
    show_help()
    print("*** GAME START ***")

    while True:
        if state["hp"] <= 0:
            print("\nGame over. The castle keeps you.")
            return
        show_status(state, rooms)
        command = get_input("\nWhat do you do? ").strip().lower()

        if not command:
            continue
        if command in ("quit", "exit"):
            print("Quitting game. Goodbye!")
            return
        if command == "help":
            show_help()
        elif command == "look":
            print()
            print(rooms[state["current_room"]]["description"])
        elif command == "save":
            save_game(state)
        elif command == "load":
            loaded = load_game()
            if loaded:
                state = loaded
                rooms = build_rooms(state)
                print("Game loaded.")
        elif command.startswith("get "):
            grab_item(state, rooms, command)
        elif command.startswith("use "):
            use_item(state, command)
        elif command.startswith("go "):
            move_between_rooms(state, rooms, command)
        elif command in ("pull rope", "ring bell", "pull", "ring"):
            if state["current_room"] == "Bell Tower" and not state["bell_rung"]:
                state["bell_rung"] = True
                print("You haul the rope. The bell tolls across the castle, deep and furious.")
                print("Somewhere below, something ancient stirs in anger. (Dracula -10 HP when you face him)")
            elif state["current_room"] == "Bell Tower":
                print("The bell is already ringing itself out.")
            else:
                print("There is no rope here.")
        else:
            print("I don't understand that command. Type 'help' for the list.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
