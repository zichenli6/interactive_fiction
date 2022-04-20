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
        items = self.describe_items()
        return "\n".join([location, exits, items])

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
                    items.append(item.description + "\n\t" + ", ".join(item.get_commands()))
                else:
                    items.append(item.description + "\n")
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

    def is_blocked(self, direction, game):
        """
        Check to if there is an obstacle in this direction.
        """
        if not direction in self.blocks:
            return False
        (block_description, preconditions) = self.blocks[direction]
        if check_preconditions(preconditions, game):
            # All the preconditions have been met. You may pass.
            return False
        else: 
            # There are still obstalces to overcome or puzzles to solve.
            return True

    def get_block_description(self, direction):
        """
        Check to if there is an obstacle in this direction.
        """
        if not direction in self.blocks:
            return ""
        else:
            (block_description, preconditions) = self.blocks[direction]
            return block_description

    def add_block(self, blocked_direction, block_description, preconditions):
        """
        Create an obstacle that prevents a player from moving in the blocked 
        location until the preconditions are all met.
        """
        self.blocks[blocked_direction] = (block_description, preconditions)
    
    def check_special_events(self, game):
        """
        Special events happen when the preconditions are all met.
        """
        for preconditions, descriptions in self.special_events:
            if check_preconditions(preconditions, game, print_failure_reasons=False):
                print(descriptions)


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

    def do_action(self, command_text, game):
        """
        Perform a special action associated with this item.
        """
        narration = ""
        end_game = False    # Switches to True if this action ends the game.
        if command_text in self.commands:
            function, arguments, preconditions, failure_reason = self.commands[command_text]
            if check_preconditions(preconditions, game):
                end_game, narration = function(game, arguments)
            elif failure_reason != "":
                narration = failure_reason
        else:
            narration = ("Cannot perform the action %s" % command_text)
        return end_game, narration


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
        if "," in command:
            # Let the player type in a comma separted sequence of commands
            return "sequence"
        elif command.lower() == "redescribe":
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
        else: 
            for item in self.game.get_items_in_scope():
                special_commands = item.get_commands()
                for special_command in special_commands:
                    if command == special_command.lower():
                        return "special"

    def parse_command(self, command):
        # Add this command to the history
        self.command_history.append(command)

        # By default, none of the intents end the game. The following are ways this
        # flag can be changed to True.
        # * Going to a certain place.
        # * Entering a certain special command
        # * Picking up a certain object.
        end_game = False
        
        # Intents are functions that can be executed
        intent = self.get_player_intent(command)
        if intent == "direction":
            end_game, narration = self.go_in_direction(command)
        elif intent == "redescribe":
            self.game.describe()
        elif intent == "examine":
            narration = self.examine(command)
        elif intent == "take":
            end_game = self.take(command)
        elif intent == "drop":
            self.drop(command)
        elif intent == "inventory":
            self.check_inventory(command)
        elif intent == "special":
            end_game, narration = self.run_special_command(command)
        elif intent == "sequence":
            end_game = self.execute_sequence(command)
        else:
            narration = "I'm not sure what you want to do.\n"
            
        # Check stay time at current location
        self.game.curr_location.stay_time += 1
        if self.game.curr_location.stay_time > 3 and not self.game.curr_location.is_lingerable:
            end_game = True
            narration += "You have stayed here for too long."

        # Query current characters at location
        characters = None
        if intent == "direction":
            characters = self.game.get_current_characters()

        return narration, characters

    ### Intent Functions ###
    def go_in_direction(self, command):
        """
        The user wants to in some direction.
        """
        direction = self.get_direction(command)
        narration = "* " + direction + "\n"

        if direction:
            if direction in self.game.curr_location.connections:
                if self.game.curr_location.is_blocked(direction, self.game):
                    # check to see whether that direction is blocked.
                    print(self.game.curr_location.get_block_description(direction))
                else:
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
                    
                    self.game.curr_location.check_special_events(self.game)
            else:
                narration += ("You can not reach %s from here.\n" % direction.title())
        return self.game.curr_location.get_property('end_game'), narration

    def check_inventory(self, command):
        """ The player wants to check their inventory"""
        if len(self.game.inventory) == 0:
            print("You don't have anything.")
        else:
            descriptions = []
            for item_name in self.game.inventory:
                item = self.game.inventory[item_name]
                descriptions.append(item.description)
            print("You have: " + ", ".join(descriptions))
    
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
        """ The player wants to put something in their inventory """
        command = command.lower()
        matched_item = False

        # This gets set to True if posession of this object ends the game.
        end_game = False

        # check whether any of the items at this location match the command
        for item_name in self.game.curr_location.items:
            if item_name in command:
                item = self.game.curr_location.items[item_name]
                if item.get_property('gettable'):
                    self.game.add_to_inventory(item)
                    self.game.curr_location.remove_item(item)
                    print(item.take_text)
                    end_game = item.get_property('end_game')                  
                else:
                    print("You cannot take the %s." % item_name)
                matched_item = True
                break
        # check whether any of the items in the inventory match the command
        if not matched_item:
            for item_name in self.game.inventory:
                if item_name in command:
                    print("You already have the %s." % item_name)
                    matched_item = True
        # fail
        if not matched_item:
            print("You can't find it.")

        return end_game

    def drop(self, command):
        """ The player wants to remove something from their inventory """
        command = command.lower()
        matched_item = False
        # check whether any of the items in the inventory match the command
        if not matched_item:
            for item_name in self.game.inventory:
                if item_name in command:
                    matched_item = True
                    item = self.game.inventory[item_name]
                    self.game.curr_location.add_item(item_name, item)
                    self.game.inventory.pop(item_name)
                    print("You drop the %s." % item_name)
                    break
        # fail
        if not matched_item:
            print("You don't have that.")

    def run_special_command(self, command):
        """
        Run a special command associated with one of the items in this location
        or in the player's inventory.
        """
        for item in self.game.get_items_in_scope():
            special_commands = item.get_commands()
            for special_command in special_commands:
                if command == special_command.lower():
                    end_game, narration = item.do_action(special_command, self.game)
                    return end_game, narration
        return False, None

    def execute_sequence(self, command):
        for cmd in command.split(","):
            cmd = cmd.strip()
            self.parse_command(cmd)

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


def check_preconditions(preconditions, game, print_failure_reasons=True):
    """
    Checks whether the player has met all of the specified preconditions
    """
    all_conditions_met = True
    for check in preconditions: 
        if check == "inventory_contains":
            item = preconditions[check]
            if not game.is_in_inventory(item):
                all_conditions_met = False
                if print_failure_reasons:
                    print("You don't have the %s" % item.name)
        if check == "in_location":
            location = preconditions[check]
            if not game.curr_location == location:
                all_conditions_met = False
                if print_failure_reasons:
                    print("You aren't in the correct location")
        if check == "location_has_item":
            item = preconditions[check]
            if not item.name in game.curr_location.items:
                all_conditions_met = False
                if print_failure_reasons:
                    print("The %s isn't in this location" % item.name)
        if check == "linger":
            stay_time = game.curr_location.stay_time
            if stay_time <= 3:
                all_conditions_met = False
        if check == "location_has_guard":
            item = preconditions[check]
            if item.name in game.curr_location.items:
                all_conditions_met = False
        if check == "princess_is_not_married":
            princess = preconditions[check]
            if princess.properties["married"]:
                all_conditions_met = False
        if check == "has_crown":
            item = preconditions[check]
            if not game.is_in_inventory(item):
                all_conditions_met = False
        if check == "is_wear_crown":
            item = preconditions[check]
            if not game.is_in_inventory(item):
                all_conditions_met = False
        # todo - add other types of preconditions
    return all_conditions_met

def add_item_to_inventory(game, *args):
    """
    Add a newly created Item and add it to your inventory.
    """
    narration = ""
    (item, action_description, already_done_description) = args[0]
    if(not game.is_in_inventory(item)):
        narration = action_description
        game.add_to_inventory(item)
    else:
        narration = already_done_description
    return False, narration

def describe_something(game, *args):
    """Describe some aspect of the Item"""
    (description) = args[0]
    return False, description

def destroy_item(game, *args):
    """Removes an Item from the game by setting its location is set to None."""
    (item, action_description, already_done_description) = args[0]
    if game.is_in_inventory(item):
        game.inventory.pop(item.name)
        print(action_description)
    elif item.name in game.curr_location.items:
        game.curr_location.remove_item(item)
        if item.name in ["troll", "ghost"]:
            game.curr_location.is_lingerable = True
        print(action_description)
    elif item.name in item.location.items:
        item.location.remove_item(item)
        print(action_description)
    else:
        print(already_done_description)
    return False

def create_item(game, *args):
    """Create an Item and add to the game."""
    (item, create_text, start_at) = args[0]
    if start_at:
        start_at.add_item(item.name, item)
        item.location = start_at
    print(create_text)
    return False

def perform_multiple_actions(game, *args):
    """perform multiple actions."""
    (multiple_actions) = args[0]
    is_end = False
    for action, arguments in multiple_actions:
        is_end = is_end or action(game, arguments)
    return is_end


def build_game(
    locations_filename="game/static/game/data/locations.json",
    characters_filename="game/static/game/data/characters.json"
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

    game = Game(list(locations.values())[0]["obj"])
    return game
