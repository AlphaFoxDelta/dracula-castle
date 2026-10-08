# Dracula's Castle - a text adventure game.
# My first real Python project, written for a school assignment.
# Explore the castle, collect all 6 items, then face Dracula.

rooms = {
    "Grand Foyer": {
        "description": "You are standing in the Grand Foyer.",
        "item": None,
        "directions": {"East": "Living Room"},
    },
    "Living Room": {
        "description": "You are in the Living Room.",
        "item": "Sunlight Amulet",
        "directions": {"West": "Grand Foyer", "North": "Library", "South": "Kitchen", "East": "Secret Passage"},
    },
    "Library": {
        "description": "You are in the Library.",
        "item": "Crucifix",
        "directions": {"South": "Living Room", "East": "Study"},
    },
    "Study": {
        "description": "You are in the Study.",
        "item": "Holy Water",
        "directions": {"West": "Library"},
    },
    "Kitchen": {
        "description": "You are in the Kitchen.",
        "item": "Garlic Necklace",
        "directions": {"North": "Living Room", "East": "Armory"},
    },
    "Armory": {
        "description": "You are in the Armory.",
        "item": "Wooden Stake",
        "directions": {"West": "Kitchen"},
    },
    "Secret Passage": {
        "description": "You are in a Secret Passage.",
        "item": "Silver Dagger",
        "directions": {"West": "Living Room", "North": "Dracula's Lair"},
    },
    "Dracula's Lair": {
        "description": "You have entered Dracula's Lair!",
        "item": None,
        "directions": {},
    },
}

TOTAL_ITEMS = 6


def move_between_rooms(current_room, command):
    """Move to a new room if the direction is valid. Returns the (possibly unchanged) room."""
    parts = command.split(" ", 1)
    if len(parts) < 2 or not parts[1].strip():
        print("Go where? Try: go North")
        return current_room
    direction = parts[1].strip().capitalize()
    if direction in rooms[current_room]["directions"]:
        return rooms[current_room]["directions"][direction]
    print("You can't go that way.")
    return current_room


def grab_item(current_room, command, inventory):
    """Pick up the item in the room, if there is one and the name matches."""
    room_item = rooms[current_room]["item"]
    if room_item is None:
        return "There is nothing to pick up here."
    item_name = command[4:].strip().title()
    if item_name.lower() == room_item.lower():
        inventory.append(room_item)
        rooms[current_room]["item"] = None
        return f"You picked up the {room_item}."
    return "There is no such item here."


def show_status(current_room, inventory):
    """Print the current room, visible item, exits, inventory, and item count."""
    print()
    print(rooms[current_room]["description"])
    if rooms[current_room]["item"]:
        print(f"You see a {rooms[current_room]['item']} here.")
    directions = rooms[current_room]["directions"]
    if directions:
        print("Exits: " + ", ".join(directions.keys()))
    else:
        print("There are no exits.")
    if inventory:
        print("Inventory: [" + ", ".join(inventory) + "]")
    else:
        print("Inventory: [Empty]")
    print(f"Items collected: {len(inventory)}/{TOTAL_ITEMS}")


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
    print("Travel throughout the castle and collect all 6 items before facing Dracula.")
    print("Do not attempt to face Dracula without all the items,")
    print("or you will never make it home alive!\n")


def show_instructions():
    """Display the game instructions."""
    print("*** INSTRUCTIONS ***\n")
    print("To move, type: go North, go South, go East, go West")
    print('To pick up an item, type: get "item name" (without the quotes)')
    print("To quit the game, type: quit or exit\n")


def main():
    show_intro()
    show_instructions()
    print("*** GAME START ***")

    current_room = "Grand Foyer"
    inventory = []
    game_over = False

    while not game_over:
        show_status(current_room, inventory)
        command = input("\nWhat do you do? ").strip().lower()

        if not command:
            continue
        if command in ("quit", "exit"):
            print("Quitting game. Goodbye!")
            return
        if command.startswith("get "):
            print(grab_item(current_room, command, inventory))
        elif command.startswith("go "):
            current_room = move_between_rooms(current_room, command)
            if current_room == "Dracula's Lair":
                if len(inventory) == TOTAL_ITEMS:
                    print("\nCongratulations! You defeated Dracula and will return home safely!")
                else:
                    print("\nYou faced Dracula unprepared, and were never seen again.")
                game_over = True
        else:
            print("I don't understand that command. Try 'go North' or 'get <item>'.")

    print(f"\nGame over. You collected {len(inventory)}/{TOTAL_ITEMS} items.")


if __name__ == "__main__":
    main()
