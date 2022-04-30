import os
import json
from collections import defaultdict


class Game:
    """
    The Game class represents the world. Internally, we use a 
    graph of Location objects and Item objects, which can be at a 
    Location or in the player's inventory. Each locations has a set of
    exits which are the directions that a player can move to get to an
    adjacent location. The player can move from one location to another
    location by typing a command like "Go North".
    """
    def __init__(self, start_at):
        # start_at is the location in the game where the player starts
        self.curr_location = start_at
        self.curr_location.has_been_visited = True
        
        # inventory is the set of objects that the player has collected
        self.inventory = {}
        
        # properties of the play
        self.properties = {}
        
        # Print the special commands associated with items in the game (helpful 
        # for debugging and for novice players).
        self.print_commands = True
        
        # visited locations
        self.visited_place = set()

        # different kinds of scores
        self.visited_place_score_max = 24
        self.collected_items_score_max = 35
        self.defeat_enemy_score_max = 30
        self.defeat_enemy_score = 0
        self.special_event_score = 0

    def describe(self):
        """
        Describe the current game state by first describing the current 
        location, then listing any exits, and then describing any objects
        in the current location.
        """
        location = self.describe_current_location()
        exits = self.describe_exits()
        return "\n".join([location, exits]) + "\n"

    def describe_current_location(self):
        """
        Describe the current location by printing its description field.
        """
        return self.curr_location.description

    def describe_exits(self):
        """
        List the directions that the player can take to exit from the current location.
        """
        exits = []
        for exit in self.curr_location.connections.keys():
            exits.append(exit.title())
        return "Exits: " + ", ".join(exits)
    
    def describe_items(self):
        """
        Describe what objects are in the current location.
        """
        items = []
        narration = ""
        if len(self.curr_location.items) > 0:
            for item_name in self.curr_location.items:
                item = self.curr_location.items[item_name]
                if item.properties["character"]:
                    continue
                if len(item.get_commands()) > 0:
                    items.append(item.name + "\n\t" + ", ".join(item.get_commands()))
                else:
                    items.append(item.name.title() + "\n")
        if len(items) > 0:
            narration = "You see:\n" + "".join(items)
        return narration

    def get_current_characters(self):
        characters = []
        if len(self.curr_location.items) > 0:
            for item_name in self.curr_location.items:
                character = self.curr_location.items[item_name]
                if not character.properties["character"]:
                    continue
                characters.append({
                    "name": character.name,
                    "headshot": "game/characters/" + character.name_clean + ".png",
                    "location": self.curr_location.name,
                    "location_description": self.curr_location.description,
                    "persona": character.description,
                    "appearance": character.examine_text,
                    "dialogues": []
                })
        return characters

    def get_current_items(self):
        items = []
        for item_name in self.curr_location.items:
            item = self.curr_location.items[item_name]
            if item.properties["character"]:
                continue
            items.append({
                "name": item.name.title(),
                "image": "game/items/" + item.name_clean + ".png",
                "description": item.description,
                "in_location": True
            })
        for item_name in self.inventory:
            item = self.inventory[item_name]
            if item.properties["character"]:
                continue
            items.append({
                "name": item.name.title(),
                "image": "game/items/" + item.name_clean + ".png",
                "description": item.description,
                "in_location": False
            })
        return items

    def add_to_inventory(self, item):
        """
        Add an item to the player's inventory.
        """
        self.inventory[item.name] = item
    
    def is_in_inventory(self,item):
        return item.name in self.inventory

    def get_items_in_scope(self):
        """
        Returns a list of items in the current location and in the inventory
        """
        items_in_scope = []
        for item_name in self.curr_location.items:
            items_in_scope.append(self.curr_location.items[item_name])
        for item_name in self.inventory:
            items_in_scope.append(self.inventory[item_name])
        return items_in_scope


class Location:
    """
    Locations are the places in the game that a player can visit.
    Internally they are represented nodes in a graph. Each location stores
    a description of the location, any items in the location, its connections
    to adjacent locations, and any blocks that prevent movement to an adjacent
    location. The connections is a dictionary whose keys are directions and
    whose values are the location that is the result of traveling in that 
    direction. The travel_descriptions also has directions as keys, and its 
    values are an optional short desciption of traveling to that location.
    """
    def __init__(self, name, description):
        # A short name for the location
        self.name = name
        # A cleaned filename for the location
        self.name_cleaned = name.lower().replace(" ", "_").replace("/", "_")
        # A description of the location
        self.description = description
        # The properties should contain a key "end_game" with value True
        # if entering this location should end the game
        self.properties = defaultdict(bool)
        # Dictionary mapping from directions to other Location objects
        self.connections = {}
        # Dictionary mapping from directions to text description of the path there
        self.travel_descriptions = {}
        # Dictionary mapping from item name to Item objects present in this location
        self.items = {}
        # Dictionary mapping from direction to Block object in that direction
        self.blocks = {}
        # Flag that gets set to True once this location has been visited by player
        self.has_been_visited = False
        # number of turns the player stays at this location
        self.stay_time = 0
        # dangerous status
        self.is_lingerable = True
        # special events preconditions
        self.special_events = []

    def set_property(self, property_name, property_bool=True):
        """
        Sets the property of this item
        """
        self.properties[property_name] = property_bool
    
    def get_property(self, property_name):
        """
        Gets the boolean value of this property for this item (defaults to False)
        """
        return self.properties[property_name]

    def add_connections(self, directions, next_locations):
        for direction, next_location in zip(directions, next_locations):
            self.add_connection(direction, next_location)

    def add_connection(self, direction, connected_location, travel_description=""):
        """
        Add a connection from the current location to a connected location.
        Direction is a string that the player can use to get to the connected
        location.    If the direction is a cardinal direction, then we also 
        automatically make a connection in the reverse direction.
        """
        direction = direction.lower()
        self.connections[direction] = connected_location
        self.travel_descriptions[direction] = travel_description
        if direction == 'north':
            connected_location.connections["south"] = self
            connected_location.travel_descriptions["south"] = ""
        if direction == 'south':
            connected_location.connections["north"] = self
            connected_location.travel_descriptions["north"] = ""
        if direction == 'east':
            connected_location.connections["west"] = self
            connected_location.travel_descriptions["west"] = ""
        if direction == 'west':
            connected_location.connections["east"] = self
            connected_location.travel_descriptions["east"] = ""
        if direction == 'up':
            connected_location.connections["down"] = self
            connected_location.travel_descriptions["down"] = ""
        if direction == 'down':
            connected_location.connections["up"] = self
            connected_location.travel_descriptions["up"] = ""
        if direction == 'in':
            connected_location.connections["out"] = self
            connected_location.travel_descriptions["out"] = ""
        if direction == 'out':
            connected_location.connections["in"] = self
            connected_location.travel_descriptions["in"] = ""
        if direction == 'inside':
            connected_location.connections["outside"] = self
            connected_location.travel_descriptions["outside"] = ""
        if direction == 'outside':
            connected_location.connections["inside"] = self
            connected_location.travel_descriptions["inside"] = ""

    def add_item(self, name, item):
        """
        Put an item in this location.
        """
        self.items[name] = item

    def remove_item(self, item):
        """
        Remove an item from this location (for instance, if the player picks it
        up and puts it in their inventory).
        """
        self.items.pop(item.name)


class Item:
    """
    Items are objects that a player can get, or scenery
    that a player can examine, or characters player can
    interact with.
    """
    def __init__(
        self,
        name,
        description,
        examine_text="",
        take_text="",
        start_at=None,
        gettable=True,
        character=False
    ):

        # The name of the object
        self.name = name

        # The cleaned naem of the object
        self.name_clean = name.lower().replace(" ", "_")
        
        # The default description of the object.
        self.description = description

        # The detailed description of the player examines the object.
        self.examine_text = examine_text

        # Text that displays when player takes an object.
        self.take_text = take_text if take_text else ("You take the %s." % self.name)
        self.properties = defaultdict(bool)
        self.properties["gettable"] = gettable
        self.properties["character"] = character

        # The location in the Game where the object starts.
        if start_at:
            start_at.add_item(name, self)
        self.location = start_at
        self.commands = {}


    def get_commands(self):
        """Returns a list of special commands associated with this object"""
        return self.commands.keys()

    def set_property(self, property_name, property_bool=True):
        """Sets the property of this item"""
        self.properties[property_name] = property_bool
    
    def get_property(self, property_name):
        """Gets the boolean value of this property for this item (defaults to False)"""
        return self.properties[property_name]

    def add_action(self, command_text, function, arguments, preconditions={}, failure_reason=""):
        """Add a special action associated with this item"""
        self.commands[command_text] = (function, arguments, preconditions, failure_reason)


class Parser:
    """
    The Parser is the class that handles the player's input. The player 
    writes commands, and the parser performs natural language understanding
    in order to interpret what the player intended, and how that intent
    is reflected in the simulated world. 
    """
    def __init__(self, game):
        # A list of all of the commands that the player has issued.
        self.command_history = []
        # A pointer to the game.
        self.game = game

    def get_player_intent(self, command):
        command = command.lower()
        if command.lower() == "redescribe":
            return "redescribe"
        elif self.get_direction(command):
            # Check for the direction intent
            return "direction"
        elif command.lower() == "look" or command.lower() == "l":
            # when the user issues a "look" command, re-describe what they see
            return "redescribe"
        elif "examine " in command or command.lower().startswith("x "):
            return "examine"
        elif "take " in command or "get " in command:
            return "take"
        elif "drop " in command:
            return "drop"
        elif "inventory" in command or command.lower() == "i":
            return "inventory"
        elif "who is " in command:
            return "character"

    def parse_command(self, command):
        # Add this command to the history
        self.command_history.append(command)

        # Intents are functions that can be executed
        intent = self.get_player_intent(command)
        if intent == "direction":
            narration = self.go_in_direction(command)
        elif intent == "redescribe":
            narration = self.game.describe()
        elif intent == "examine":
            narration = self.examine(command)
        elif intent == "take":
            narration = self.take(command)
        elif intent == "drop":
            narration = self.drop(command)
        elif intent == "inventory":
            narration = self.check_inventory(command)
        elif intent == "character":
            narration = self.describe_character(command)
        else:
            narration = "I'm not sure what you want to do.\n"

        # Query current characters and items at location
        items = None
        characters = None
        if intent == "direction":
            characters = self.game.get_current_characters()
            items = self.game.get_current_items()
        if intent in ["take", "drop"]:
            items = self.game.get_current_items()

        return narration, characters, items

    ### Intent Functions ###
    def go_in_direction(self, command):
        """
        The user wants to in some direction.
        """
        direction = self.get_direction(command)
        narration = "* " + direction + "\n"

        if direction:
            for connection in self.game.curr_location.connections:
                if direction in connection:
                    direction = connection
            if direction in self.game.curr_location.connections:
                    # if it's not blocked, then move there 
                    self.game.curr_location = self.game.curr_location.connections[direction]
                    
                    # add curr_location to visited
                    self.game.visited_place.add(self.game.curr_location.name)
                    
                    # reset how many turns the play stays here
                    self.game.curr_location.stay_time = 0

                    # If moving to this location ends the game, only describe the location
                    # and not the available items or actions.
                    if self.game.curr_location.get_property('end_game'):
                        self.game.describe_current_location()
                    else:
                        narration += self.game.describe()
            else:
                narration += ("You can not reach %s from here.\n" % direction.title())
        return narration

    def check_inventory(self, command):
        """
        The player wants to check their inventory.
        """
        narration = ""
        if len(self.game.inventory) == 0:
            narration = "You don't have anything."
        else:
            item_names = [name for name in self.game.inventory]
            narration = "You have: " + ", ".join(item_names)
        return narration
    
    def examine(self, command):
        """
        The player wants to examine something.
        """
        narration = ""
        command = command.lower()
        matched_item = False
        # check whether any of the items at this location match the command
        for item_name in self.game.curr_location.items:
            if item_name in command:
                item = self.game.curr_location.items[item_name]
                if item.examine_text:
                    narration = item.examine_text
                    matched_item = True
                break
        # check whether any of the items in the inventory match the command
        for item_name in self.game.inventory:
            if item_name in command:
                item = self.game.inventory[item_name]
                if item.examine_text:
                    narration = item.examine_text
                    matched_item = True
        # fail
        if not matched_item:
            narration = "You don't see anything special."
        return narration

    def take(self, command):
        """
        The player wants to put something in their inventory.
        """
        narration = ""
        command = command.lower()
        matched_item = False

        # check whether any of the items at this location match the command
        for item_name in self.game.curr_location.items:
            if item_name in command:
                item = self.game.curr_location.items[item_name]
                if item.get_property('gettable'):
                    self.game.add_to_inventory(item)
                    self.game.curr_location.remove_item(item)
                    narration = item.take_text                
                else:
                    narration = "You cannot take the %s." % item_name
                matched_item = True
                break
    
        # check whether any of the items in the inventory match the command
        if not matched_item:
            for item_name in self.game.inventory:
                if item_name in command:
                    narration = "You already have the %s." % item_name
                    matched_item = True

        # fail
        if not matched_item:
            narration = "You cannot find it."

        return narration

    def drop(self, command):
        """
        The player wants to remove something from their inventory.
        """
        narration = ""
        command = command.lower()
        matched_item = False

        # check whether any of the items in the inventory match the command
        for item_name in self.game.inventory:
            if item_name in command:
                matched_item = True
                item = self.game.inventory[item_name]
                self.game.curr_location.add_item(item_name, item)
                self.game.inventory.pop(item_name)
                narration = "You drop the %s." % item_name
                break
        # fail
        if not matched_item:
            narration = "You do not have that."
        return narration

    def describe_character(self, command):
        """
        The player wants to get character description.
        """
        narration = ""
        command = command.lower()
        matched_character = False

        # check whether any of the characters at this location match the command
        for item_name in self.game.curr_location.items:
            item = self.game.curr_location.items[item_name]
            if item.properties["character"] and item_name.lower() in command:
                narration = item.description               
                matched_character  = True
                break
    
        # fail
        if not matched_character:
            narration = "There is no such person."

        return narration

    def get_direction(self, command):
        command = command.lower()
        if "go to " in command:
            return command.replace("go to ", "")
        if "go " in command:
            return command.replace("go ", "")
        if command == "n" or "north" in command:
            return "north" 
        if command == "s" or "south" in command:
            return "south"
        if command == "e" or "east" in command: 
            return "east"
        if command == "w" or "west" in command:
            return "west"
        if command == "up":
            return "up"
        if command == "down":
            return "down"
        if command.startswith("go out"):
            return "out"
        if command.startswith("go in"):
            return "in"
        for exit in self.game.curr_location.connections.keys():
            if command == exit.lower() or command == "go " + exit.lower():
                return exit
        return None


def build_game(
    locations_filename="game/static/game/data/locations.json",
    characters_filename="game/static/game/data/characters.json",
    items_filename="game/static/game/data/items.json"
):
    # initialize locations
    locations = {}
    location_data = json.load(open(locations_filename, 'r'))
    for name, data in location_data.items():
        locations[name] = {
            "obj": Location(name, data["description"]),
            "connections": data["connections"]
        }

    # initialize connections
    for name, data in locations.items():
        location, connections = data["obj"], data["connections"]
        connected_locations = [locations[name]["obj"] for name in connections]
        location.add_connections(connections, connected_locations)

    # initialize characters
    characters = []
    characters_data = json.load(open(characters_filename, 'r'))
    for name, data in characters_data.items():
        character = Item(name, data["description"], data["appearance"], start_at=locations[data["location"]]['obj'], character=True)
        characters.append(character)

    # initialize items
    items = []
    items_data = json.load(open(items_filename, 'r'))
    for name, data in items_data.items():
        item = Item(name, data["description"], data["description"], start_at=locations[data["location"]]['obj'], character=False)
        items.append(item)

    game = Game(list(locations.values())[5]["obj"])
    return game
