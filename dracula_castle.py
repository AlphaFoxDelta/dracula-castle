# Dracula's Castle - a text adventure game.
# My first real Python project, written for a school assignment.
# Then I kept going: a bigger castle, a real boss fight, traps, locked doors,
# a save system, NPCs, mini-bosses, puzzles, crafting, and multiple endings.
# Same game at heart, just a lot more of it.

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
        "gold": 0,
        "directions": {"East": "Living Room"},
    },
    "Living Room": {
        "description": (
            "The Living Room reeks of old smoke. A fireplace full of cold ash squats "
            "beneath a portrait whose painted eyes seem to follow you around the room."
        ),
        "item": "Sunlight Amulet",
        "gold": 0,
        "directions": {"West": "Grand Foyer", "North": "Library", "South": "Kitchen", "East": "Secret Passage"},
    },
    "Library": {
        "description": (
            "Floor-to-ceiling shelves sag with rotting books. Pages rustle in the dark "
            "though there is no wind. A stone staircase spirals up into shadow. Coins "
            "glint between the fallen books."
        ),
        "item": "Crucifix",
        "gold": 15,
        "directions": {"South": "Living Room", "East": "Study", "Up": "Bell Tower"},
    },
    "Study": {
        "description": (
            "A desk buried in yellowed letters, an inkwell dry for a century. One letter "
            "is newer than the rest. It reads: 'Forgive me.' A heavy oak door leads east. "
            "An ornate chest sits in the corner, its lock suspiciously shiny."
        ),
        "item": "Holy Water",
        "gold": 20,
        "directions": {"West": "Library", "East": "Chapel"},
    },
    "Kitchen": {
        "description": (
            "Pots hang from rusted hooks over a dead stove. Something scuttles behind "
            "the flour sacks and goes very quiet. Stone steps lead down into the dark."
        ),
        "item": "Garlic Necklace",
        "gold": 0,
        "directions": {"North": "Living Room", "East": "Armory", "Down": "Wine Cellar"},
    },
    "Armory": {
        "description": (
            "Rusted swords line the walls. Empty suits of armor stand at attention, "
            "guarding nothing. An iron grate in the floor leads down. A few coins "
            "lie scattered where a purse once burst."
        ),
        "item": "Wooden Stake",
        "gold": 10,
        "directions": {"West": "Kitchen", "Down": "Dungeon"},
    },
    "Secret Passage": {
        "description": (
            "A narrow corridor behind the walls. The stones sweat, and the air smells of "
            "earth. Ahead, the passage opens into something vast and cold. A hooded "
            "figure lurks in an alcove, watching you."
        ),
        "item": "Silver Dagger",
        "gold": 0,
        "directions": {"West": "Living Room", "North": "Dracula's Lair"},
    },
    "Wine Cellar": {
        "description": (
            "Barrels loom in the dark, stacked to the ceiling. One of them leans at a "
            "bad angle, looking ready to fall."
        ),
        "item": "Healing Tonic",
        "gold": 10,
        "directions": {"Up": "Kitchen"},
    },
    "Dungeon": {
        "description": (
            "Chains hang from the walls and straw covers the floor. The straw moves. "
            "Rats, dozens of them, eyes shining in the dark. A prisoner rattles his "
            "chains in the far cell. A low stone arch leads east."
        ),
        "item": "Chapel Key",
        "gold": 0,
        "directions": {"Up": "Armory", "East": "Crypt"},
    },
    "Chapel": {
        "description": (
            "Moonlight falls through a shattered stained-glass window, painting the altar "
            "red and gold. Dust hangs in the light like snow."
        ),
        "item": "Sacred Chalice",
        "gold": 0,
        "directions": {"West": "Study"},
    },
    "Bell Tower": {
        "description": (
            "Wind howls through the open arches. Far below, the castle sprawls dark and "
            "silent. A thick rope hangs from the great bell overhead. Coins are wedged "
            "between the floorboards, dropped by long-dead bell ringers."
        ),
        "item": None,
        "gold": 25,
        "directions": {"Down": "Library"},
    },
    "Crypt": {
        "description": (
            "A low vault of carved stone. Sarcophagi line the walls, their lids slightly "
            "askew, as if their occupants left in a hurry. An ancient shield leans "
            "against the far wall, untouched by rust."
        ),
        "item": "Ancient Shield",
        "gold": 30,
        "directions": {"West": "Dungeon"},
    },
    "Dracula's Lair": {
        "description": (
            "A vast chamber of black marble. At its heart sits an open coffin. The air is "
            "ice, and the shadows are wrong."
        ),
        "item": None,
        "gold": 0,
        "directions": {},
    },
}

WEAPONS = {
    "Sunlight Amulet": {"damage": 15, "text": "You raise the Sunlight Amulet. Searing light floods the chamber."},
    "Silver Dagger": {"damage": 12, "text": "You slash with the Silver Dagger, opening a smoking wound."},
    "Crucifix": {"damage": 10, "text": "You hold the Crucifix high. Your foe recoils, hissing.", "weakens": 2},
    "Garlic Necklace": {"damage": 6, "text": "You press the Garlic Necklace forward. Your foe gags and staggers.", "weakens": 1},
    "Holy Water": {"damage": 22, "text": "You hurl Holy Water. It burns like acid.", "uses": 3},
    "Wooden Stake": {"damage": 35, "text": "You drive the Wooden Stake toward its heart.", "uses": 2},
}

# Weapons you can craft. Registered into WEAPONS when crafted.
CRAFTED_WEAPONS = {
    "Blessed Stake": {"damage": 45, "uses": 2, "text": "You raise the Blessed Stake, blazing with holy light."},
    "Garlic Dagger": {"damage": 18, "weakens": 1, "text": "You slash with the Garlic Dagger. The wound smokes and your foe gags."},
}

CRAFT_RECIPES = {
    ("Holy Water", "Wooden Stake"): ("Blessed Stake", "You pour the Holy Water over the Wooden Stake. It glows with pale fire."),
    ("Garlic Necklace", "Silver Dagger"): ("Garlic Dagger", "You rub garlic into the Silver Dagger's edge. It reeks of victory."),
}

CONSUMABLES = {
    "Healing Tonic": {"heal": 30, "text": "You drink the Healing Tonic. Warmth spreads through your limbs."},
    "Greater Elixir": {"heal": "full", "text": "You drink the Greater Elixir. You feel like you could fight a mountain."},
    "Sacred Chalice": {"heal": "full", "text": "You drink from the Sacred Chalice. Your wounds close as if they were never there."},
}

TRAPS = {
    "Wine Cellar": {"damage": 8, "text": "A barrel breaks loose and crashes into you! (-8 HP)"},
    "Dungeon": {"damage": 10, "text": "Rats swarm out of the straw, biting at your ankles! (-10 HP)"},
}

ENEMIES = {
    "dracula": {
        "name": "Count Dracula",
        "hp": 120,
        "min_atk": 10,
        "max_atk": 16,
        "intro": [
            "Count Dracula rises from the coffin, eyes burning red.",
            "'You carry light into MY house? Let us see how long it lasts.'",
        ],
        "attacks": [
            "Dracula lunges, claws raking across your arm!",
            "Dracula moves faster than sight and slams you into the marble!",
            "Cold hands close around your throat and squeeze!",
            "Dracula's eyes flare, and pain lances through your skull!",
        ],
        "death": "Dracula staggers, clutches his chest, and collapses into dust and old cloth.",
    },
    "bride_chapel": {
        "name": "Dracula's Bride",
        "hp": 35,
        "min_atk": 7,
        "max_atk": 11,
        "intro": [
            "A woman in a torn wedding dress drops from the rafters, fangs bared.",
            "'The chalice is MINE, little mouse.'",
        ],
        "attacks": [
            "The bride rakes her claws across your face!",
            "She moves like smoke and slams you against a pew!",
            "Her fangs sink toward your neck! You twist away, barely!",
        ],
        "death": "The bride shrieks and dissolves into mist. Gold coins clatter to the floor where she stood.",
        "gold_drop": 20,
    },
    "bride_tower": {
        "name": "Dracula's Bride",
        "hp": 35,
        "min_atk": 7,
        "max_atk": 11,
        "intro": [
            "A pale figure unfolds from the shadows of the bell, smiling with too many teeth.",
            "'No one rings MY bell.'",
        ],
        "attacks": [
            "The bride's nails carve lines down your arm!",
            "She hurls you into the bell. It booms, and your skull rings with it!",
            "She is suddenly behind you, breath ice-cold on your neck!",
        ],
        "death": "The bride crumples into mist. Gold coins scatter across the floorboards.",
        "gold_drop": 20,
    },
}

NPCS = {
    "Dungeon": {
        "name": "prisoner",
        "greet": "A prisoner rattles his chains. 'You! You're not one of his. Listen, I know this place.'",
        "hints": [
            "'The chapel door is locked, but the jailer dropped a key down here in the dark. Look around.'",
            "'His brides nest in the chapel and the bell tower. Don't face them empty-handed.'",
            "'There's a merchant hiding in the secret passage east of the living room. He sells to anyone with gold.'",
            "'Ring the bell tower's bell before you face the Count. Holy sound hurts him.'",
            "'The crypt east of here is sealed by a riddle. The answer is something you hear but never see.'",
            "'If you find holy water and a spare stake, combine them. Trust me.'",
        ],
    },
    "Secret Passage": {
        "name": "merchant",
        "greet": "A hooded merchant leans against the wall. 'Psst. Supplies for the living. Gold only.'",
        "stock": {"Healing Tonic": 25, "Greater Elixir": 60},
    },
}

RIDDLE_QUESTION = (
    "A stone door bars the way, carved with words:\n"
    "'I speak without a mouth and hear without ears.\n"
    "I have no body, but I come alive with wind.\n"
    "What am I?'"
)
RIDDLE_ANSWER = "echo"

TOTAL_COLLECTIBLES = 10  # 6 weapons + key + 2 consumables + shield


def new_game():
    """Fresh game state."""
    return {
        "current_room": "Grand Foyer",
        "inventory": {},  # item name -> uses left (None means unlimited)
        "gold": 0,
        "hp": 100,
        "max_hp": 100,
        "brides_defeated": [],
        "taken_rooms": [],
        "gold_taken_rooms": [],
        "visited": [],
        "chapel_unlocked": False,
        "crypt_unlocked": False,
        "bell_rung": False,
        "chest_opened": False,
        "chest_disarmed": False,
        "crafted": [],
        "hint_index": 0,
        "offer_made": False,
        "dracula_hp": 120,
        "bell_applied": False,
    }


def build_rooms(state):
    """Rebuild the room map from the pristine definitions, minus picked-up items and gold."""
    rooms = copy.deepcopy(ROOM_DEFS)
    for room_name in state["taken_rooms"]:
        rooms[room_name]["item"] = None
    for room_name in state["gold_taken_rooms"]:
        rooms[room_name]["gold"] = 0
    return rooms


def register_crafted(state):
    """Re-register crafted weapons after loading a save."""
    for name in state.get("crafted", []):
        if name in CRAFTED_WEAPONS:
            WEAPONS[name] = CRAFTED_WEAPONS[name]


def get_input(prompt):
    """Read a line of input. Ctrl+D / end of stream quits cleanly instead of crashing."""
    try:
        return input(prompt)
    except EOFError:
        return "quit"


def find_item(name, collection):
    """Case-insensitive lookup of an item name. Returns the real name or None."""
    for real_name in collection:
        if real_name.lower() == name.strip().lower():
            return real_name
    return None


def show_status(state, rooms):
    """Print where you are, what is here, your health, gold, and inventory."""
    room = rooms[state["current_room"]]
    print()
    print(room["description"])
    if room["item"]:
        print(f"You see a {room['item']} here.")
    if room["gold"]:
        print(f"There are {room['gold']} gold coins here.")
    if state["current_room"] in NPCS:
        print(f"{NPCS[state['current_room']]['name'].capitalize()} is here. (talk to {NPCS[state['current_room']]['name']})")
    if room["directions"]:
        print("Exits: " + ", ".join(room["directions"].keys()))
    else:
        print("There are no exits.")
    print(f"Health: {state['hp']}/{state['max_hp']}  |  Gold: {state['gold']}")
    if state["inventory"]:
        print("Inventory: [" + ", ".join(state["inventory"].keys()) + "]")
    else:
        print("Inventory: [Empty]")


def move_between_rooms(state, rooms, command):
    """Handle 'go <direction>': locked doors, the riddle door, traps, and ambushes."""
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

    if target == "Crypt" and not state["crypt_unlocked"]:
        print(RIDDLE_QUESTION)
        print("(Type: answer <your answer>)")
        return

    came_from = current
    state["current_room"] = target

    if target in TRAPS and target not in state["visited"]:
        trap = TRAPS[target]
        state["hp"] -= trap["damage"]
        print(trap["text"])
        if state["hp"] <= 0:
            state["hp"] = 0
    if target not in state["visited"]:
        state["visited"].append(target)

    if target == "Dracula's Lair":
        start_combat(state, "dracula", came_from)
    elif target == "Chapel" and "bride_chapel" not in state["brides_defeated"]:
        start_combat(state, "bride_chapel", came_from)
    elif target == "Bell Tower" and "bride_tower" not in state["brides_defeated"]:
        start_combat(state, "bride_tower", came_from)


def grab_item(state, rooms, command):
    """Handle 'get <item>' and 'get gold'."""
    wanted = command[4:].strip()
    if not wanted:
        print("Get what?")
        return
    if wanted.lower() in ("gold", "gold coins", "coins"):
        amount = rooms[state["current_room"]]["gold"]
        if amount <= 0:
            print("There is no gold here.")
            return
        state["gold"] += amount
        state["gold_taken_rooms"].append(state["current_room"])
        rooms[state["current_room"]]["gold"] = 0
        print(f"You pocket {amount} gold coins. ({state['gold']} total)")
        return
    room_item = rooms[state["current_room"]]["item"]
    if room_item is None:
        print("There is nothing to pick up here.")
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
    """Handle 'use <item>': drinkables, plus the silver dagger chest trick."""
    wanted = command[4:].strip()
    if not wanted:
        print("Use what?")
        return
    name = find_item(wanted, state["inventory"])
    if name is None:
        print("You don't have that.")
        return
    # Disarming the study chest with the silver dagger.
    if name == "Silver Dagger" and state["current_room"] == "Study" and not state["chest_opened"] and not state["chest_disarmed"]:
        state["chest_disarmed"] = True
        print("You slide the dagger under the chest lid and feel the trap mechanism click harmlessly. Safe to open now.")
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


def talk_to(state, command):
    """Handle 'talk to <npc>'."""
    wanted = command.replace("talk to", "talk", 1)[4:].strip()
    room_npc = NPCS.get(state["current_room"])
    if room_npc is None or wanted.lower() != room_npc["name"]:
        print("There is no one here to talk to.")
        return
    print(room_npc["greet"])
    if room_npc["name"] == "prisoner":
        hints = room_npc["hints"]
        print(hints[state["hint_index"] % len(hints)])
        state["hint_index"] += 1
    elif room_npc["name"] == "merchant":
        print("His wares:")
        for item, price in room_npc["stock"].items():
            print(f"  {item}: {price} gold  (buy {item.lower()})")
        print(f"You have {state['gold']} gold.")


def buy_item(state, command):
    """Handle 'buy <item>' from the merchant."""
    if state["current_room"] not in NPCS or NPCS[state["current_room"]]["name"] != "merchant":
        print("There is no merchant here.")
        return
    wanted = command[4:].strip()
    stock = NPCS[state["current_room"]]["stock"]
    name = find_item(wanted, stock)
    if name is None:
        print("He doesn't sell that.")
        return
    price = stock[name]
    if state["gold"] < price:
        print(f"Not enough gold. The {name} costs {price}, you have {state['gold']}.")
        return
    state["gold"] -= price
    state["inventory"][name] = 1
    print(f"You buy the {name} for {price} gold. ({state['gold']} left)")


def answer_riddle(state, rooms, command):
    """Handle 'answer <text>' at the crypt door."""
    if state["current_room"] != "Dungeon" or state["crypt_unlocked"]:
        print("There is nothing to answer here.")
        return
    guess = command[len("answer"):].strip().lower()
    if guess == RIDDLE_ANSWER:
        state["crypt_unlocked"] = True
        print("The carvings glow faintly. Stone grinds on stone as the door swings open.")
        state["current_room"] = "Crypt"
        if "Crypt" not in state["visited"]:
            state["visited"].append("Crypt")
    else:
        print("The carvings stay silent. That is not the answer.")


def open_chest(state, command):
    """Handle 'open chest' in the study. It is trapped."""
    if state["current_room"] != "Study":
        print("There is no chest here.")
        return
    if state["chest_opened"]:
        print("The chest is empty.")
        return
    state["chest_opened"] = True
    if not state["chest_disarmed"]:
        print("Click! A poison dart fires from the lock and grazes your arm! (-12 HP)")
        state["hp"] -= 12
        if state["hp"] <= 0:
            state["hp"] = 0
            return
    else:
        print("The disarmed lock opens smoothly.")
    print("Inside: an Elixir of Vitality! You feel stronger just holding it. (+20 max HP)")
    state["max_hp"] += 20
    state["hp"] = min(state["max_hp"], state["hp"] + 20)


def craft_item(state, command):
    """Handle 'combine <a> with <b>' to forge stronger weapons."""
    text = command[len("combine"):].strip() if command.startswith("combine") else command[len("craft"):].strip()
    if " with " in text:
        first, second = text.split(" with ", 1)
    elif " and " in text:
        first, second = text.split(" and ", 1)
    else:
        print("Combine what with what? Try: combine holy water with wooden stake")
        return
    a = find_item(first, state["inventory"])
    b = find_item(second, state["inventory"])
    if a is None or b is None:
        print("You don't have both of those.")
        return
    key = tuple(sorted([a, b]))
    recipe = None
    for ingredients, result in CRAFT_RECIPES.items():
        if tuple(sorted(ingredients)) == key:
            recipe = (ingredients, result)
            break
    if recipe is None:
        print("Those two don't combine into anything useful.")
        return
    result_name, flavor = recipe[1]
    del state["inventory"][a]
    del state["inventory"][b]
    WEAPONS[result_name] = CRAFTED_WEAPONS[result_name]
    uses = CRAFTED_WEAPONS[result_name].get("uses")
    state["inventory"][result_name] = uses
    state["crafted"].append(result_name)
    print(flavor)
    print(f"Crafted: {result_name}!")


def enemy_attack(state, enemy):
    """The enemy takes its turn. Returns True if the player survives."""
    shield = 3 if "Ancient Shield" in state["inventory"] else 0
    damage = max(1, random.randint(enemy["min_atk"], enemy["max_atk"]) - state.get("enemy_penalty", 0) - shield)
    print(random.choice(enemy["attacks"]) + f" (-{damage} HP)")
    state["hp"] -= damage
    if state["hp"] <= 0:
        state["hp"] = 0
        return False
    return True


def do_attack(state, enemy, command):
    """Handle 'attack <weapon>' during a fight."""
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
    enemy["hp"] -= damage
    print(f"{enemy['name']} takes {damage} damage. ({max(0, enemy['hp'])}/{enemy['max_hp']} HP)")
    if "weakens" in weapon:
        state["enemy_penalty"] = state.get("enemy_penalty", 0) + weapon["weakens"]
        print(f"{enemy['name']}'s attacks grow weaker.")
    if "uses" in weapon:
        state["inventory"][name] -= 1
        if state["inventory"][name] <= 0:
            del state["inventory"][name]
            broken = " It splinters into pieces." if "Stake" in name else ""
            print(f"The {name} is spent!{broken}")


def start_combat(state, enemy_id, return_room):
    """Turn-based fight against Dracula or one of his brides."""
    enemy = copy.deepcopy(ENEMIES[enemy_id])
    enemy["max_hp"] = enemy["hp"]
    state["enemy_penalty"] = 0
    if enemy_id == "dracula":
        if state["bell_rung"] and not state["bell_applied"]:
            state["bell_applied"] = True
            state["dracula_hp"] = max(1, state["dracula_hp"] - 10)
            print("The bell's toll still echoes through the castle. Dracula is rattled. (-10 HP)")
        enemy["hp"] = state["dracula_hp"]
        enemy["max_hp"] = 120
    print()
    for line in enemy["intro"]:
        print(line)
    print()
    if enemy_id == "dracula":
        missing = [w for w in ("Sunlight Amulet", "Crucifix", "Holy Water", "Garlic Necklace", "Wooden Stake", "Silver Dagger") if w not in state["inventory"]]
        if missing:
            print("You face him without all six original weapons. Brave. Probably fatal.\n")

    while enemy["hp"] > 0 and state["hp"] > 0:
        print(f"--- Your HP: {state['hp']}/{state['max_hp']} | {enemy['name']} HP: {max(0, enemy['hp'])}/{enemy['max_hp']} ---")
        command = get_input("Fight! (attack <weapon> / use <item> / flee): ").strip().lower()

        if not command:
            continue
        if command == "flee":
            state["current_room"] = return_room
            if enemy_id == "dracula":
                state["dracula_hp"] = min(120, enemy["hp"] + 10)
                print("You sprint back into the Secret Passage. Behind you, Dracula laughs, and catches his breath.")
            else:
                print(f"You break away and retreat. {enemy['name']} hisses but does not follow... yet.")
            return
        if command.startswith("attack"):
            do_attack(state, enemy, command)
        elif command.startswith("use "):
            use_item(state, command)
        elif command == "spare" and enemy_id == "dracula":
            if not state["offer_made"]:
                print("Dracula laughs. 'Surrender? Already? How... premature.'")
            else:
                print("\n'Yes... YES. Kneel, and rise eternal.'")
                print("Darkness takes you gently. You wake hungry, and the castle is yours.")
                print("\nENDING: Eternal Night. (There are other endings. Try finishing him instead.)")
                raise SystemExit
        elif command in ("quit", "exit"):
            print("Quitting game. Goodbye!")
            raise SystemExit
        else:
            print("You're fighting for your life! Attack with a weapon, use an item, or flee.")

        if enemy["hp"] <= 0:
            break

        # Dracula begs when he is nearly beaten.
        if enemy_id == "dracula" and enemy["hp"] <= 25 and not state["offer_made"]:
            state["offer_made"] = True
            print("\nDracula drops to one knee, a hand pressed to his wounds.")
            print("'Mercy! Spare me, and I will make you like me... eternal life, eternal night.'")
            print("(Type 'spare' to accept, or keep attacking to finish him.)\n")

        if not enemy_attack(state, enemy):
            print("\nThe chamber goes dark, and the castle keeps its secret.")
            raise SystemExit

    # Victory.
    for line in enemy["death"].split("\n"):
        print(line)
    if enemy.get("gold_drop"):
        state["gold"] += enemy["gold_drop"]
        print(f"(+{enemy['gold_drop']} gold)")
    if enemy_id in ("bride_chapel", "bride_tower"):
        state["brides_defeated"].append(enemy_id)
        return
    # Dracula is dead. Which ending did you earn?
    legendary = state["bell_rung"] and len(state["brides_defeated"]) == 2 and "Blessed Stake" in state["crafted"]
    if legendary:
        print("Dawn breaks through the high windows, gold and merciless.")
        print("You rang the bell, destroyed his brides, and forged a blessed weapon.")
        print("The bards will sing about this one. You walk out of the castle into the morning, alive.")
        print("\nENDING: Legend of the Castle. (The best ending. Nicely done.)")
    else:
        print("Dawn breaks through the high windows. You walk out of the castle into the morning, alive.")
        print("\nENDING: Dawn Breaks. (Rumor says there is a greater victory for the thorough.)")
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
            state = json.load(f)
        # Fill in any fields added since the save was written.
        for key, value in new_game().items():
            state.setdefault(key, value)
        return state
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
    print("Weapons are hidden in these halls, but so are his brides, and they")
    print("do not share. Deeper rooms hold supplies and gold, and not every")
    print("door opens for the asking. Do not face him unprepared,")
    print("or you will never make it home alive!\n")


def show_help():
    """Display the command list."""
    print("\n*** COMMANDS ***")
    print("  go <direction>        Move: go North, South, East, West, Up, Down")
    print("  get <item>            Pick up an item (get gold for coins)")
    print("  use <item>            Drink a tonic or elixir")
    print("  attack <weapon>       Fight (in combat)")
    print("  flee                  Run from a fight")
    print("  talk to <name>        Talk to the prisoner or the merchant")
    print("  buy <item>            Buy from the merchant (Secret Passage)")
    print("  combine <a> with <b>  Craft weapons into stronger ones")
    print("  answer <text>         Answer the riddle on the crypt door")
    print("  open chest            Open the chest in the study (carefully)")
    print("  pull rope             Ring the bell in the Bell Tower (once)")
    print("  look                  Look around the room again")
    print("  save / load           Save or load your game")
    print("  help                  Show this list")
    print("  quit                  Quit the game\n")


def main():
    state = new_game()
    if os.path.exists(SAVE_FILE):
        answer = get_input("A saved game exists. Load it? (yes/no): ").strip().lower()
        if answer in ("yes", "y"):
            loaded = load_game()
            if loaded:
                state = loaded
    register_crafted(state)
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
                register_crafted(state)
                rooms = build_rooms(state)
                print("Game loaded.")
        elif command.startswith("get ") or command.startswith("take "):
            grab_item(state, rooms, "get " + command.split(" ", 1)[1])
        elif command.startswith("use "):
            use_item(state, command)
        elif command.startswith("go "):
            move_between_rooms(state, rooms, command)
        elif command.startswith("talk"):
            talk_to(state, command)
        elif command.startswith("buy "):
            buy_item(state, command)
        elif command.startswith("answer "):
            answer_riddle(state, rooms, command)
        elif command == "open chest":
            open_chest(state, command)
        elif command.startswith("combine ") or command.startswith("craft "):
            craft_item(state, command)
        elif command in ("pull rope", "ring bell", "pull", "ring"):
            if state["current_room"] == "Bell Tower":
                if "bride_tower" not in state["brides_defeated"]:
                    print("The bride blocks the rope, shrieking. You'll have to go through her.")
                elif not state["bell_rung"]:
                    state["bell_rung"] = True
                    print("You haul the rope. The bell tolls across the castle, deep and furious.")
                    print("Somewhere below, something ancient stirs in anger. (Dracula -10 HP when you face him)")
                else:
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
