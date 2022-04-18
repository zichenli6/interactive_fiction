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
            exits.append(exit.capitalize())
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
                if len(item.get_commands()) > 0:
                    items.append(item.description + "\n\t" + ", ".join(item.get_commands()))
                else:
                    items.append(item.description + "\n")
        if len(items) > 0:
            narration = "You see:\n" + "".join(items)
        return narration

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
    that a player can examine.
    """
    def __init__(self,
                 name,
                 description,
                 examine_text="",
                 take_text="",
                 start_at=None,
                 gettable=True):
        # The name of the object
        self.name = name
        # The default description of the object.
        self.description = description
        # The detailed description of the player examines the object.
        self.examine_text = examine_text
        # Text that displays when player takes an object.
        self.take_text = take_text if take_text else ("You take the %s." % self.name)
        self.properties = defaultdict(bool)
        self.properties["gettable"] = gettable
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
        return end_game, narration

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
                narration += ("You can't go %s from here.\n" % direction.capitalize())
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

def eat_fish(game, *args):
    """Try to eat the fish."""
    (action_description) = args[0]
    print(action_description)
    return False

def drive_off_troll(game, *args):
    """Drive off the troll by feeding it fish."""
    (action_description) = args[0]
    print(action_description)
    return False

def perform_multiple_actions(game, *args):
    """perform multiple actions."""
    (multiple_actions) = args[0]
    is_end = False
    for action, arguments in multiple_actions:
        is_end = is_end or action(game, arguments)
    return is_end

def give_rose_to_princess(game, *args):
    """give rose to princess."""
    (reaction_text) = args[0]
    print(reaction_text)
    return False

def kiss_princess(game, *args):
    """try to kiss the princess ."""
    (refuse_text, kiss_text, is_married) = args[0]
    if is_married:
        print(kiss_text)
    else:
        print(refuse_text)
    return False

def be_rude_to_princess(game, *args):
    """be rude to princess."""
    (reaction_text) = args[0]
    print(reaction_text)
    return False

def talk_to_princess(game, *args):
    """talk to princess."""
    (conversation_text) = args[0]
    print(conversation_text)
    return False

def marry_princess(game, *args):
    """marry princess."""
    (princess, accepct_text) = args[0]
    print(accepct_text)
    princess.properties["married"] = True
    game.properties["married"] = True
    return False

def decipher_runes(game, *args):
    """decipher runes."""
    (clue_text) = args[0]
    print(clue_text)
    return False

def add_special_event_score(game, *args):
    """add special event score"""
    (score) = args[0]
    game.special_event_score = game.special_event_score + score
    return False

def add_defeat_enemy_score(game, *args):
    """add defeat enemy score"""
    (score) = args[0]
    game.defeat_enemy_score = min(game.defeat_enemy_score + score, game.defeat_enemy_score_max)
    return False

def end_game(game, *args):
    """Ends the game."""
    end_message = args[0]
    print(end_message)
    return True


def build_game():
    # Locations
    nowhere = Location("nowhere", "")

    cottage = Location("Cottage", "You are standing in a small cottage.")
    garden_path = Location("Garden Path", "You are standing on a lush garden path. There is a cottage here.")
    cliff = Location("Cliff", "There is a steep cliff here. You fall off the cliff and lose the game. THE END.")
    cliff.set_property('end_game', True)
    fishing_pond = Location("Fishing Pond", "You are at the edge of a small fishing pond.")
    winding_path = Location("Winding Path", "You are walking along a winding path.")
    top_of_the_tall_tree = Location("Top of the Tall Tree", "You are the top of the tall tree.")
    drawbridge = Location("Drawbridge", "You are standing on one side of a drawbridge leading to ACTION CASTLE..")
    courtyard = Location("Courtyard", "You are in the courtyard of ACTION CASTLE.")
    tower_stairs = Location("Tower Stairs", "You are climbing the stairs to the tower.")
    tower = Location("Tower", "You are inside a tower.")
    dungeon_stairs = Location("Dungeon Stairs", "You are climbing the stairs down to the dungeon.")
    dungeon = Location("Dungeon", "You are in the dungeon.")
    great_feasting_hall = Location("Great Feasting Hall", "You stand inside the Great Feasting Hall.")
    throne_room = Location("Throne Room", "This is the throne room of ACTION CASTLE.")

    # Connections
    def _add_connections(curr_location, directions, next_locations):
        for direction, next_location in zip(directions, next_locations):
            curr_location.add_connection(direction, next_location)
    _add_connections(cottage, ["out"], [garden_path])
    _add_connections(garden_path, ["south", "north"], [fishing_pond, winding_path])
    _add_connections(winding_path, ["up", "east"], [top_of_the_tall_tree, drawbridge])
    _add_connections(drawbridge, ["east"], [courtyard])
    _add_connections(courtyard, ["east", "up", "down"], [great_feasting_hall, tower_stairs, dungeon_stairs])
    _add_connections(tower_stairs, ["up"], [tower])
    _add_connections(dungeon_stairs, ["down"], [dungeon])
    _add_connections(great_feasting_hall, ["east"], [throne_room])

    # Items that you can pick up
    lamp = Item("lamp", "a lamp", "Player can now LIGHT the lamp. While the lantern is lit the player can go directly from the courtyard to the dungeon by going down.", start_at=None)
    lighted_lamp = Item("lighted_lamp", "a lighted lamp", "This lighted lamp lights up darkness.", start_at=None)
    fishing_pole = Item("pole", "a fishing pole", "A SIMPLE FISHING POLE.", start_at=cottage)
    potion = Item("potion", "a poisonous potion", "IT'S BRIGHT GREEN AND STEAMING.", start_at=cottage, take_text='As you near the potion, the fumes cause you to faint and lose the game. THE END.')
    potion.set_property('end_game', True)
    rose = Item("rose", "a red rose", "IT SMELLS GOOD.", start_at=None)
    fish = Item("fish", "a dead fish", "IT SMELLS TERRIBLE.", start_at=None)
    branch = Item("branch", "a stout dead branch", "It can be used once to HIT or CLUB something, whereupon it will break into pieces and be rendered unusable.", "Taking the dead branch causes it to snap off.", start_at=top_of_the_tall_tree)
    key = Item("key", "a key", start_at=None)
    candle = Item("candle", "a candle", start_at=great_feasting_hall)
    crown = Item("crown", "a crown", "you may only wear it once married.", start_at=None)
    wearing_crown = Item("wearing_crown", "the crown you're wearing", "the crown you're wearing", start_at=None)

    # Scenery (not things that you can pick up)
    pond = Item("pond", "a small fishing pond", "THERE ARE FISH IN THE POND.", start_at=fishing_pond, gettable=False)
    rosebush = Item("rosebush", "a rosebush", "THE ROSEBUSH CONTAINS A SINGLE RED ROSE.    IT IS BEAUTIFUL.", start_at=garden_path, gettable=False)
    tree = Item("tree", "a tall tree", "The tree contains a stout, dead branch.", start_at=top_of_the_tall_tree, gettable=False)
    troll = Item("troll", "a mean troll", "The troll is warty, green and hungry.", start_at=drawbridge, gettable=False)
    guard = Item("guard", "a armed guard", "The guard is brandishing a short sword.", start_at=courtyard, gettable=False)
    unconcious_guard = Item("unconcious_guard", "an unconcious_guard", "The guard is unconcious_guard.", start_at=nowhere, gettable=False)
    kneeing_guard = Item("kneeing_guard", "a kneeing guard", "The guard drops to a knee and hails his new king.", start_at=nowhere, gettable=False)
    locked_door = Item("locked_door", "a locked door", "This is a locked door.", start_at=tower_stairs, gettable=False)
    princess = Item("princess", "a beautiful princess", start_at=tower, gettable=False)
    ghost = Item("ghost", "the ghost has claw-like ﬁngers and wears a crown.", start_at=dungeon, gettable=False)
    runes = Item("runes", "strange runes.", "The runes seem to be a spell of exorcism", start_at=great_feasting_hall, gettable=False)
    throne = Item("throne", "an ornate golden throne.", start_at=throne_room, gettable=False)

    # Add special functions to your items
    rosebush.add_action("pick rose", perform_multiple_actions, 
        ([
            (add_item_to_inventory, (rose, "You pick the lone rose from the rosebush.", "You already picked the rose."))
        ]),
        preconditions={"in_location": garden_path}
    )
    rose.add_action("smell rose", describe_something, ("It smells sweet."))
    pond.add_action("catch fish", describe_something, ("You reach into the pond and try to catch a fish with your hands, but they are too fast."))
    pond.add_action("catch fish with pole", perform_multiple_actions, 
        ([
            (add_item_to_inventory, (fish, "You dip your hook into the pond and catch a fish.","You weren't able to catch another fish."))
        ]),
        preconditions={"inventory_contains":fishing_pole, "in_location": fishing_pond}
    )
    fish.add_action("eat fish", eat_fish, ("The fish is raw and cannot be eaten."), preconditions={"inventory_contains": fish})
    tree.add_action("jump down", end_game, ("It's suicide."), preconditions={"inventory_contains": fish})
    troll.add_action("attack", end_game, ("The player is killed by the troll. THE END."))
    troll.add_action("feed troll with fish", perform_multiple_actions, 
        ([
            (destroy_item, (fish, "You give fish to the hungry troll.", "You already tried that.")),
            (destroy_item, (troll,"The guard leaves because it's full.", "There is no troll")),
            (add_defeat_enemy_score, (10)),
        ]),
        preconditions={"inventory_contains":fish , "location_has_item": troll}
    )
    guard.add_action("hit guard with branch", perform_multiple_actions, 
        ([
            (destroy_item, (branch, "You use your branch hit the guard. It breaks into pieces.", "")),
            (destroy_item, (guard, "The guard is knocked out, unconscious.", "There is no guard awake")),
            (create_item, (unconcious_guard, "", courtyard)),
            (create_item, (key, "The key drops to the floor.", courtyard)),
            (add_defeat_enemy_score, (10)),
        ]),
        preconditions={"inventory_contains":branch , "location_has_item": guard}
    )
    princess.add_action("give rose to princess", perform_multiple_actions, 
        ([
            (give_rose_to_princess, ("The rose is so beautiful, I like it!")),
            (destroy_item, (rose, "You give rose to the princess", "You already gave rose to the princess")),
            (add_special_event_score, (5)),
        ]),
        preconditions={"inventory_contains":rose , "location_has_item": princess}
    )
    princess.add_action("kiss princess", kiss_princess, ("Not until we're wed!", "...", princess.properties["married"]))
    princess.add_action("be rude to princess", be_rude_to_princess, ("Pa!!! You are slapped!"))
    princess.add_action("talk to princess", talk_to_princess, ("My father haunts the dungeon as a restless spirit.\
                                                                \nOnly the rightful heir to the throne may wear it!\
                                                                \nI cannot leave this tower until I am married!\
                                                                 \nOnly the king may sit on the throne."))
    princess.add_action("propose to princess", perform_multiple_actions, 
        ([
            (marry_princess, (princess, "Yes, I do!")),
            (destroy_item, (unconcious_guard, "The guard wakes up because the new ruler arrives", "")),
            (create_item, (kneeing_guard, "", courtyard)),
            (destroy_item, (crown, "The princess places the crown on your head", "")),
            (create_item, (wearing_crown, "You're wearing the crown.", None)),
            (add_item_to_inventory, (wearing_crown, "", "")),
        ]),
        preconditions={"inventory_contains":crown, "princess_is_not_married": princess},
        failure_reason="You’re not royalty!"
    )
    runes.add_action("decipher runes", decipher_runes, ("The runes seem to be a spell of exorcism."))
    lamp.add_action("light lamp", perform_multiple_actions, 
        ([
            (destroy_item, (lamp, "You light the lamp.", "You already lit the lamp.")),
            (add_item_to_inventory, (lighted_lamp, "", ""))
        ]),
        preconditions={"inventory_contains":lamp , "in_location": dungeon_stairs}
    )
    ghost.add_action("light candle", perform_multiple_actions, 
        ([
            (destroy_item, (candle, "You light the candle.", "")),
            (destroy_item, (ghost, "What a terrible smell!", "")),
            (create_item, (crown, "The crown drops to the ground.", dungeon)),
            (add_defeat_enemy_score, (10)),
        ]),
        preconditions={"inventory_contains":candle , "location_has_item": ghost}
    )
    throne.add_action("sit on the throne", perform_multiple_actions, 
        ([
            (add_special_event_score, (5)),
            (end_game, ("You sit on the ornate golden throne. The people cheer for the new ruler of... ACTION CASTLE!")),
        ]),
        preconditions={"inventory_contains": wearing_crown , "in_location": throne_room}
    )

    # add special events
    tower.special_events = [({"location_has_item": princess, "has_crown": crown}, "My father’s crown! You have put his soul at rest and may now succeed him!")]
    courtyard.special_events = [({"location_has_item": kneeing_guard, "is_wear_crown": wearing_crown}, "The guard drops to a knee and hails his new king.")]
    great_feasting_hall.special_events = [({"is_wear_crown": wearing_crown}, "The great feasting hall is full of revelers celebrating the new ruler of ACTION CASTLE!")]
    throne_room.special_events = [({"is_wear_crown": wearing_crown}, "The throne room is full of courtiers and guards.")]

    # places where the player cannot linger
    drawbridge.is_lingerable = False
    dungeon.is_lingerable = False
    
    # places with block
    drawbridge.add_block("east", "there is a hungry troll in your way.", preconditions={"location_has_guard": troll})
    courtyard.add_block("east", "there is an armed guard in your way.", preconditions={"location_has_guard": guard})
    tower_stairs.add_block("up", "The player needs the guard’s key to access the tower.", preconditions={"inventory_contains": key})
    dungeon_stairs.add_block("down", "The player needs light to go down.", preconditions={"inventory_contains": lighted_lamp})
    
    # The player starts the game with a lamp in his inventory.
    game = Game(cottage)
    game.add_to_inventory(lamp)
    return game


# def game_loop():
#     game = build_game()
#     parser = Parser(game)
#     narration = game.describe()
#     print(narration)

#     command = ""
#     while not (command.lower() == "exit" or command.lower == "q"):
#         command = input(">")
#         end_game, narration = parser.parse_command(command)
#         print("n:", narration)
#         if end_game:
#             location_score = min(2 * len(game.visited_place), game.visited_place_score_max)
#             item_score = min(5 * len(game.collected_items), game.collected_items_score_max)
#             defeat_enemy_score = game.defeat_enemy_score
#             special_event_score = game.special_event_score
#             total_score = location_score + item_score + defeat_enemy_score + special_event_score + 1
#             print(f"player's total score: {total_score}/100")
#             return game
#     return narration

# game = game_loop()
# print('THE GAME HAS ENDED.')