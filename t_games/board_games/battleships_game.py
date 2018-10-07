"""
battleships_game.py

A game of Battleships.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The design and programming credits. (str)
INVENTORIES: Different inventories of ships to place. (dict of str: tuple of int)
RULES: The rules of the game. (str)
SQUARE_RE: A regular expression matching coordinate. (re.SRE_Pattern)

Classes:
Battleships: A game of Battleships. (game.Game)
BattleBot: A bot for playing Battleships. (player.Bot)
SeaBoard: A board in a game of Battleships. (object)

Functions:
test: Basic testing of the board object. (None)
"""


import random
import re

import t_games.game as game
import t_games.options as options
import t_games.player as player


CREDITS = """
Although Milton-Bradley did make a version of this game, it is a traditional
    game dating back to the First World War.
Programming by Craig "Ichabod" O'Brien.
"""

INVENTORIES = {'bradley': {'Carrier': (5, 1), 'Battleship': (4, 1), 'Cruiser': (3, 1),
        'Destroyer': (2, 1), 'Submarine': (3, 1)},
    'bednar': {'Carrier': (5, 1), 'Battleship': (4, 1), 'Cruiser': (3, 1),
        'Destroyer': (2, 2), 'Submarine': (1, 2)},
    'ichabod': {'Carrier': (5, 1), 'Battleship': (4, 2), 'Cruiser': (3, 3),
        'Destroyer': (2, 4), 'Submarine': (1, 1)},
    'wikipedia': {'Carrier': (6, 1), 'Battleship': (4, 2), 'Cruiser': (3, 3),
        'Destroyer': (2, 4), 'Submarine': (1, 0)}}

RULES = """
You layout your ships on your board by specifying two squares using the board
coordinates on the edges of the board. Only you can see where your ships are.
Each ship takes up one or more squares on the board. Ships must be arranged
orthogonally, and cannot be orthogonally adjacent to each other.

Instead of specifying the start and end squares of a ship, you may respond
with 'random' or just 'r', and the game will place the ship randomly for you.

Then you and your opponent simultaneously fire shots at each other's boards.
You are told if the shot is a hit or a miss. If all of the squares on a ship
are hit, that ship is sunk, and the person who sunk it is informed. If all of
your ships are sunk, you lose the game.

You will be shown two grids, with the columns labelled 0-9 and the rows
labelled A-J. You call shots (and place ships) by using letter-number
coordinates, such as A8. The top grid represents your opponents board, and the
bottom grid represents your board. Hits are marked 'X', misses are marked '/',
and ship squares not yet hit (on your board only) are marked 'O'.

The winner's score is the number of un-hit squares that they had left.

Options:

inventory= (i): This determines the number and size of ships played with. The
value can be Bradley (the Milton Bradley version), Bednar (an open source
version by Samuel Bednar), Ichabod (the version I remember), and Wikipedia
(the inventory shown in a picture in the Wikipedia article on the game.) the
inventories give the following ships (name size x count):
    Bradley/Br: Carrier 5x1, Battleship 4x1, Cruiser 3x1, Destroyer 2x1,
        Submarine 3x1.
    Bednar/Bd: Carrier 5x1, Battleship 4x1, Cruiser 3x1, Destroyer 2x2,
        Submarine 1x2.
    Ichabod/Ik: Carrier 5x1, Battleship 4x2, Cruiser 3x3, Destroyer 2x4,
        Submarine 1x1.
    Wikipedia/Wk: Carrier 6x1, Battleship 4x2, Cruiser 3x3, Destroyer 2x4,
        No Submarine.
"""

SQUARE_RE = re.compile(r'[ABCDEFGHIJ]\d')


class Battleships(game.Game):
    """
    A game of Battleships. (object)

    Class Attributes:
    inventory_aliases: Aliases for the inventory_name.

    Attributes:
    boards: The boards for each player. (dict of str: SeaBoard)
    bot: The bot opponent. (player.Bot)
    inventory_name: The name of the inventory of ships. (str)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['Battleship', 'Sea Battle', 'Broadsides', 'Batt']
    categories = ['Board Games']
    credits = CREDITS
    inventory_aliases = {'br': 'bradley', 'bd': 'bednar', 'ik': 'ichabod', 'wk': 'wikipedia'}
    name = 'Battleships'
    num_options = 1
    rules = RULES

    def do_gipf(self, arguments):
        """
        Gesundheit.
        """
        game, losses = self.gipf_check(arguments, ('wumpus', 'pig', 'canfield'))
        go = True
        # Hunt the Wumpus tells you where a particular ship type is.
        if game == 'wumpus':
            if not losses:
                self.gipf_wumpus()
                go = False
        # Pig gives you a bonus shot if you hit your next shot.
        elif game == 'pig':
            if not losses:
                self.gipf_pig()
        # Canfield gives you a random hit.
        elif game == 'canfield':
            if not losses:
                self.gipf_canfield()
                go = False
        # Game with no gipf link
        else:
            self.human.tell('Gesundheit.')
        # Update the human after a loss.
        if game != 'invalid-game' and losses:
            self.human.tell(self.boards[self.bot.name].show(to = 'foe'))
            self.human.tell(self.boards[self.human.name].show())
        return go

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Check for a tie.
        if not (self.boards[self.bot.name].fleet or self.boards[self.human.name].fleet):
            self.human.tell("\nIt's a draw! You destroyed each other's fleets at the same time.")
            self.win_loss_draw[2] = 1
        # Check for a win.
        elif not self.boards[self.bot.name].fleet:
            self.human.tell("\nYou sank {}'s fleet and won!".format(self.bot.name))
            squares_left = sum([len(squares) for ship, squares in self.boards[self.human.name].fleet])
            self.scores[self.human.name] = squares_left
            self.human.tell("You have {} squares of ships left.".format(squares_left))
            self.win_loss_draw[0] = 1
        # Check for a loss.
        elif not self.boards[self.human.name].fleet:
            self.human.tell("\n{} sank your fleet. You lose.".format(self.bot.name))
            squares_left = sum([len(squares) for ship, squares in self.boards[self.bot.name].fleet])
            self.scores[self.human.name] = squares_left * -1
            self.human.tell("{} had {} squares of ships left.".format(self.bot.name, squares_left))
            self.win_loss_draw[1] = 1
        else:
            # Otherwise, game on.
            return False
        # Report the end of the game.
        return True

    def gipf_canfield(self):
        """Handle the Canfield edge. (None)"""
        # Get a random hit for the human.
        not_hit = []
        for ship, ship_squares in self.boards[self.bot.name].fleet:
            not_hit.extend(set(ship_squares) - self.boards[self.bot.name].hits)
        human_shot = random.choice(not_hit)
        self.human.tell('You fired on {}.'.format(human_shot))
        # Get the bot's shot.
        bot_shot = self.bot.ask('\nWhere do you want to shoot? ')
        # Fire the shots.
        self.boards[self.bot.name].fire(human_shot.upper(), self.human)
        self.boards[self.human.name].fire(bot_shot, self.bot)
        # Update the human. (Bots don't need updates.)
        self.human.tell(self.boards[self.bot.name].show(to = 'foe'))
        self.human.tell(self.boards[self.human.name].show())

    def gipf_pig(self):
        """Handle the Pig edge. (None)"""
        # Remind the human.
        self.human.tell(self.boards[self.bot.name].show(to = 'foe'))
        self.human.tell(self.boards[self.human.name].show())
        # Get the first shot.
        while True:
            human_shot = self.human.ask('\nWhere do you want to shoot? ').upper().strip()
            if SQUARE_RE.match(human_shot):
                break
        bot_shot = self.bot.ask('Where do you want to shoot? ')
        # Fire the shots.
        self.boards[self.bot.name].fire(human_shot, self.human)
        self.boards[self.human.name].fire(bot_shot, self.bot)
        # Check for second shot.
        if human_shot in self.boards[self.bot.name].hits:
            self.human.tell('You hit, so you get a bonus shot.')
            while True:
                human_shot = self.human.ask('Where do you want to shoot? ').upper().strip()
                if SQUARE_RE.match(human_shot):
                    break
            self.boards[self.bot.name].fire(human_shot, self.human)
        # Update the human. (Bots don't need updates.)
        self.human.tell(self.boards[self.bot.name].show(to = 'foe'))
        self.human.tell(self.boards[self.human.name].show())

    def gipf_wumpus(self):
        """Handle the Hunt the Wumpus edge. (None)"""
        # Remind the human.
        self.human.tell(self.boards[self.bot.name].show(to = 'foe'))
        self.human.tell(self.boards[self.human.name].show())
        # Get a ship type.
        while True:
            ship = self.human.ask('\nEnter a ship type: ')
            if ship in INVENTORIES[self.inventory_name]:
                break
            self.human.error('I do not recognize that ship type.')
        # Get that ship type.
        board = self.boards[self.bot.name]
        ships = [(name, squares) for name, squares in board.fleet if name == ship and squares]
        if not ships:
            # Warn the player if there are no more of that ship.
            self.human.error('There are no more {}s.'.format(ship.lower()))
        else:
            # Get a random square from one of those ships.
            name, squares = random.choice(ships)
            square = random.choice(squares)
            self.human.tell('There is a {} at {}.'.format(ship, square))

    def handle_options(self):
        """Handle the option settings for the current game. (None)"""
        super(Battleships, self).handle_options()
        # Handle inventory aliases.
        self.inventory_name = self.inventory_aliases.get(self.inventory_name, self.inventory_name)
        # Set up the players.
        if self.bot_level.startswith('e'):
            self.bot = BattleBot(taken_names = [self.human.name])
        elif self.bot_level.startswith('m'):
            self.bot = SmarterBot(taken_names = [self.human.name])
        self.players = [self.human, self.bot]

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Update the human. (Bots don't need updates.)
        self.human.tell(self.boards[self.bot.name].show(to = 'foe'))
        self.human.tell(self.boards[self.human.name].show())
        # Get the players' moves.
        human_shot = self.human.ask('\nWhere do you want to shoot? ').strip()
        if not SQUARE_RE.match(human_shot.upper()):
            self.player_index = 0  # Make sure output goes to the human.
            return self.handle_cmd(human_shot)
        bot_shot = self.bot.ask('\nWhere do you want to shoot? ')
        # Fire the shots.
        self.boards[self.bot.name].fire(human_shot.upper(), self.human)
        self.boards[self.human.name].fire(bot_shot, self.bot)

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.add_option('inventory', ['i'], converter = options.lower, default = 'bradley',
            target = 'inventory_name',
            valid = ['bradley', 'br', 'bednar', 'bd', 'ichabod', 'ik', 'wikipedia', 'wk'],
            question = 'Which inventory would you like to use (return for Bradley)? ',
            error_text = 'The available inventories are Bradley, Bednar, Ichabod, and Wikipedia')
        self.option_set.add_option('bot-level', ['b'], converter = options.lower, default = 'medium',
            valid = ['e', 'easy', 'm', 'medium'],
            question = 'How hard should the bot be (Easy, Medium, or Hard, return for medium)? ')

    def set_up(self):
        """Set up a board for each player. (None)"""
        self.boards = {self.bot.name: SeaBoard(self.bot, self.inventory_name)}
        self.boards[self.human.name] = SeaBoard(self.human, self.inventory_name)


class BattleBot(player.Bot):
    """
    A bot for playing Battleships. (player.Bot)

    Attributes:
    dont_shoot: The squares that should not be fired at. (set of str)
    last_shot: The last shot fired. (str)
    target_ship: The squares hit on the currently targetted ship. (list of str)
    targets: Current targets based on recent hits. (list of str)

    Methods:
    add_adjacents: Add adjacent squares of a ship to the don't shoot set. (None)
    fire: Decide where to fire the next shot. (str)
    new_shot: Make a shot when there are no current targets. (str)
    retarget: Reset target list based on a recent hit. (None)

    Overridden Methods:
    ask
    error
    set_up
    tell
    """

    def add_adjacents(self):
        """Add adjacent squares of a ship to the don't shoot set."""
        for square in self.target_ship:
            self.dont_shoot.update(self.game.boards[self.name].adjacent_squares(square))

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question to ask the player. (str)
        """
        # Handle ship placements.
        if prompt.startswith('\nPlace'):
            return 'random'
        # Handle firing shots.
        elif prompt.startswith('\nWhere'):
            return self.fire()

    def error(self, *args, **kwargs):
        """
        Warn the player about an invalid play. (None)

        Parameters:
        The parameters are as teh built-in print function.
        """
        # Ignore errors when placing ships, as the bot places at random until it fits.
        if 'overlaps' in args[0]:
            pass
        # Handle other errrors normally.
        else:
            super(BattleBot, self).error(*args, **kwargs)

    def fire(self):
        """Decide where to fire the next shot. (str)"""
        # Shoot ranomly when there are no specified targets.
        if not self.targets:
            self.last_shot = self.new_shot()
        # Shoot a randomly targetted square.
        else:
            self.last_shot = random.choice(self.targets)
            self.targets.remove(self.last_shot)
        # Return the chosen shot.
        self.dont_shoot.add(self.last_shot)
        return self.last_shot

    def new_shot(self):
        """Make a shot when there are no current targets. (str)"""
        # Shoot ranomly.
        while True:
            new_shot = random.choice(SeaBoard.letters) + random.choice(SeaBoard.numbers)
            if new_shot not in self.dont_shoot:
                break
        return new_shot

    def retarget(self):
        """Reset target list based on a recent hit. (None)"""
        adjacents = self.game.boards[self.name].adjacent_squares(self.last_shot)
        # Handle working your way down the ship.
        if self.target_ship:
            # Add to the target ship.
            self.target_ship.append(self.last_shot)
            # Find the axis of the target ship.
            other_square = self.target_ship[0]
            if other_square[0] == self.last_shot[0]:
                match = 0
            else:
                match = 1
            # clear out extraneous targets.
            if len(self.target_ship) == 2:
                self.targets = [target for target in self.targets if target[match] == other_square[match]]
            # Add the adjacent on the axis but not hit yet.
            for adjacent in adjacents:
                if adjacent[match] == self.last_shot[match] and adjacent not in self.target_ship:
                    self.targets.append(adjacent)
        # Handle initial targetting.
        else:
            self.targets = [adjacent for adjacent in adjacents if adjacent not in self.dont_shoot]
            self.target_ship = [self.last_shot]

    def set_up(self):
        """Reset the bot for a new game. (None)"""
        self.dont_shoot = set()
        self.targets = []
        self.target_ship = []
        self.last_shot = ''

    def tell(self, text):
        """
        Send information to the player. (None)

        Parameters:
        text: The message from the game. (str)
        """
        # Handle hits.
        if 'hit' in text:
            self.retarget()
        # Handle sinkings.
        elif 'sank a' in text:
            self.add_adjacents()
            self.target_ship = []
            self.targets = []


class SmarterBot(BattleBot):
    """
    A smarter BattleBot with a search pattern. (BattleBot)

    The search pattern is a series of lines drawn across the board. These lines
    are called search lines. You start with a random one. After each one is
    searched, the next one is added so that the longest remaining enemy ship
    cannot fit between it and the last search line.

    Attributes:
    search_direction: The slope of the search lines. (-1 or 1)
    search_squares: The squares to search for new targets. (list of str)
    search_starts: The A-row squares search lines start from. (list of int)
    target_sizes: The sizes of the remaining enemy ships. (list of int)

    Methods:
    add_line: Add a search line to the search pattern. (None)
    expand_search: Add another search line to the search pattern. (None)

    Overridden Methods:
    new_shot
    set_up
    tell
    """

    def add_line(self, start):
        """Add a search line to the search pattern. (None)"""
        # Save the new start.
        self.search_starts.append(start)
        # Get the new squares.
        new_line = []
        for letter in SeaBoard.letters:
            new_line.append('{}{}'.format(letter, start))
            start = (start + self.search_direction) % 10
        # Add them to the search pattern without impossible squares
        self.search_squares = list(set(self.search_squares) - self.dont_shoot)
        self.search_squares.extend(new_line)

    def expand_search(self):
        """Add another search line to the search pattern. (None)"""
        # Determine width between lines.
        line_spacing = max(self.target_sizes)
        sorted_start = sorted(self.search_starts)
        sorted_start.append(sorted_start[0] + 10)
        diffs = [abs(a - b) for a, b in zip(sorted_start, sorted_start[1:])]
        if diffs:
            line_spacing = min(line_spacing, max(diffs) // 2)
        # Find the new line.
        next_start = self.search_starts[-1]
        while True:
            next_start = (next_start + line_spacing) % 10
            if next_start not in self.search_starts:
                break
            # Prevent infinite loops
            if next_start == self.search_starts[-1]:
                line_spacing -= 1
        # Add the line.
        self.add_line(next_start)

    def new_shot(self):
        """Make a shot when there are no current targets. (str)"""
        # Update the search pattern if necessary.
        while not self.search_squares:
            self.expand_search()
        # Target a random square from the search pattern.
        square = random.choice(self.search_squares)
        self.search_squares.remove(square)
        return square

    def set_up(self):
        """Teset the bot for a new game. (None)"""
        # Set up the targetting of found ships.
        super(SmarterBot, self).set_up()
        # Set up the search pattern.
        self.search_direction = random.choice([-1, 1])
        self.search_starts = []
        self.search_squares = []
        self.add_line(random.randrange(10))
        # Set up tracking the sizes of remaining enemy ships.
        self.target_sizes = []
        for size, count in self.game.boards[self.name].inventory.values():
            self.target_sizes.extend([size] * count)

    def tell(self, text):
        """
        Send information to the player. (None)

        Parameters:
        text: The message from the game. (str)
        """
        # Track sizes of remaining enemy ships.
        if 'sank a' in text:
            self.target_sizes.remove(len(self.target_ship))
        # Handle targetting found ships.
        super(SmarterBot, self).tell(text)
        # Remove impossible squares from the search pattern.
        if 'sank a' in text:
            self.search_squares = list(set(self.search_squares) - self.dont_shoot)

class SeaBoard(object):
    """
    A board in a game of Battleships. (object)

    Class Attributes:
    letters: The letters for coordinates. (str)
    numbers: The numbers for coordinates. (str)

    Attributes:
    fleet: The ships on the board. (list of tuple)
    hits: The squares with made shots. (set of str)
    inventory: The inventory of ships used for the game. (dict)
    misses: The squares with missed shots. (set of str)
    player: The player the board belongs to. (player.Player)

    Methods:
    adjacent_squares: Get the adjacent squares for a given square. (list of str)
    fire: Fire a shot on the board. (None)
    make_ship: Get a list of ship coordinates from the end points. (list of str)
    place_random: Place a ship randomly. (list of str)
    place_ships: Get the placement of the ships from the player. (None)
    show: Show the current status of the board. (str)
    """

    letters = 'ABCDEFGHIJ'
    numbers = '0123456789'

    def __init__(self, player, inventory_name = 'bradley'):
        """
        Set up the board. (None)

        Parameters:
        player: The player the board is for. (player.Player)
        inventory_name: The name of the inventory to use. (str)
        """
        # Set the specified attributes.
        self.player = player
        self.inventory = INVENTORIES[inventory_name]
        # Set the default attributes.
        self.hits = set()
        self.misses = set()
        # Get the ships placed.
        self.place_ships()

    def __repr__(self):
        """Create a debugging text representation. (str)"""
        fleet_squares = sum([squares for ship, squares in self.fleet], [])
        text = '<SeaBoard for {!r} with {} of {} hits>'
        return text.format(self.player, len(self.hits), len(self.hits) + len(fleet_squares))

    def adjacent_squares(self, square):
        """
        Get the adjacent board squares for a given square. (list of str)

        Parameters:
        square: The square to get adjacents for. (str)
        """
        # Turn the square into numeric components.
        coordinates = (self.letters.index(square[0]), int(square[1]))
        # Get valid adjacencies.
        adjacent = []
        if coordinates[0] > 0:
            adjacent.append(self.letters[coordinates[0] - 1] + str(coordinates[1]))
        if coordinates[0] < 9:
            adjacent.append(self.letters[coordinates[0] + 1] + str(coordinates[1]))
        if coordinates[1] > 0:
            adjacent.append(square[0] + str(coordinates[1] - 1))
        if coordinates[1] < 9:
            adjacent.append(square[0] + str(coordinates[1] + 1))
        # Return the adjancent squares.
        return adjacent

    def fire(self, square, foe):
        """
        Fire a shot on the board. (None)

        Parameters:
        square: The square to shoot at. (str)
        foe: The player making the shot. (player.Player)
        """
        # Check all of the ships in the fleet.
        for ship, squares in self.fleet:
            if square in squares:
                # Record the hit to the ship.
                self.hits.add(square)
                foe.tell('You hit.')
                # Check for sinking the ship.
                squares.remove(square)
                if not squares:
                    self.player.tell('Your {} has been sunk.'.format(ship))
                    foe.tell('You sank a {}.'.format(ship))
                    # Check for sinking the fleet (an empty fleet is a flag for Battleships.game_over).
                    fleet_squares = sum([squares for ship, squares in self.fleet], [])
                    if not fleet_squares:
                        self.fleet = []
                break
        else:
            # If it doesn't hit, you must have missed.
            self.misses.add(square)
            foe.tell('You missed.')

    def make_ship(self, start, end):
        """
        Get a list of ship coordinates from the end points. (list of str)

        If the ship is diagonal, an empty list is returned to indicated
        an invalid ship definition.

        Parameters:
        start: The starting square of the ship. (str)
        end: The ending square of the ship. (str)
        """
        # General set up.
        start, end = sorted([start, end])
        squares = []
        # Determine ship orientation.
        if start[0] == end[0]:
            # Set up vertical loop.
            start_index = int(start[1])
            end_index = int(end[1])
            # Loop through squares.
            for number in range(start_index, end_index + 1):
                squares.append(start[0] + str(number))
        elif start[1] == end[1]:
            # Set up horizontal loop.
            start_index = self.letters.index(start[0])
            end_index = self.letters.index(end[0])
            # Loop through squares.
            for letter in self.letters[start_index:end_index + 1]:
                squares.append(letter + start[1])
        return squares

    def place_random(self, size, invalid_squares):
        """
        Place a ship randomly. (list of str)

        Parameters:
        size: The size of the ship to place. (int)
        invalid_squares: Squares blocked by previously placed ships. (set of str)
        """
        while True:
            # Get a random line of the specified size.
            same_index = random.randrange(10)
            start_index = random.randrange(11 - size)
            end_index = start_index + size - 1
            # Get the start and end squares, randomly horizontal or vertical.
            if random.random() < 0.5:
                start = self.letters[same_index] + self.numbers[start_index]
                end = self.letters[same_index] + self.numbers[end_index]
            else:
                start = self.letters[start_index] + self.numbers[same_index]
                end = self.letters[end_index] + self.numbers[same_index]
            # Check the ship for valid placement
            ship_squares = self.make_ship(start, end)
            for square in ship_squares:
                if square in invalid_squares:
                    break
            else:
                # Return the first valid placement found.
                return start, end

    def place_ships(self):
        """Get the placement of the ships from the player. (None)"""
        # Get the available ships sorted by size.
        ships = sorted(self.inventory.items(), key = lambda ship: ship[1][0], reverse = True)
        # Set up the tracking variables.
        invalid_squares = set()
        self.fleet = []
        # Loop through the ships.
        for ship, (size, count) in ships:
            # Loop through multiple copies of the same size.
            for ship_index in range(count):
                # Show the current layout to the player.
                self.player.tell(self.show())
                while True:
                    # Get the start and end squares from the player
                    message = '\nPlace {} #{} of {}, length {}: '
                    move = self.player.ask(message.format(ship.lower(), ship_index + 1, count, size))
                    squares = SQUARE_RE.findall(move.upper())
                    # Check for random placement.
                    if move.lower() in ('r', 'rand', 'random'):
                        squares = self.place_random(size, invalid_squares)
                    # Check for the correct number of squares.
                    elif size == 1 and len(squares) != 1:
                        self.player.error('You must enter one square for a {}.'.format(ship.lower()))
                        continue
                    elif size > 1 and len(squares) != 2:
                        self.player.error('Please enter a start and end square.')
                        continue
                    # Get the full list of squares.
                    if size == 1:
                        ship_squares = [squares[0]]
                    else:
                        ship_squares = self.make_ship(*squares)
                    # Check for diagonal ships.
                    if not ship_squares:
                        self.player.error('Ships must be horizontal or vertical.')
                        continue
                    # Check for the correct size of ship.
                    elif len(ship_squares) != size:
                        self.player.error('{}s must be {} squares long.'.format(ship.lower(), size))
                        continue
                    # Check for adjacent or overlapping ships.
                    for square in ship_squares:
                        if square in invalid_squares:
                            break
                    else:
                        # Track and store valid ships.
                        for square in ship_squares:
                            invalid_squares.add(square)
                            invalid_squares.update(self.adjacent_squares(square))
                        self.fleet.append((ship, ship_squares))
                        break
                    # Warn player about overlapping or adjacent ships.
                    self.player.error('That ship is adjacent to or overlaps another ship.')

    def show(self, to = 'friend'):
        """
        Show the current status of the board. (str)

        Parameters:
        to: If to is not 'friend', ships are not shown. (str)
        """
        # Start with an axis label.
        lines = ['\n 0123456789']
        for letter in reversed(self.letters):
            # Left axis label.
            line = letter
            # Squares for that row.
            for number in range(10):
                square = letter + str(number)
                if square in self.hits:
                    line += 'X'
                elif square in self.misses:
                    line += '/'
                # Only show ships to friends.
                elif to == 'friend' and any([square in squares for ship, squares in self.fleet]):
                    line += 'O'
                else:
                    line += '.'
            # Right axis label.
            line += letter
            lines.append(line)
        # End with an axis label.
        lines.append(' 0123456789')
        return '\n'.join(lines)


def test():
    """Basic testing of the board object. (None)"""
    # Test ship creation.
    board = SeaBoard()
    print('B3 to B7', board.make_ship('B3', 'B7'))
    print('C5 to F5', board.make_ship('C5', 'F5'))
    print('B3 to F5', board.make_ship('B3', 'F5'))
    # Test adjacent squares.
    print('adj E5', board.adjacent_squares('E5'))
    print('adj A5', board.adjacent_squares('A5'))
    print('adj J5', board.adjacent_squares('J5'))
    print('adj E0', board.adjacent_squares('E0'))
    print('adj E9', board.adjacent_squares('E9'))
    print('adj A0', board.adjacent_squares('A0'))
    # Test ship placement.
    craig = BattleBot('Craig')
    board = SeaBoard(craig, inventory = 'Ichabod')
    board.place_ships()
    print(board.show())
    # Test firing shots.
    sarah = player.Player('Sarah')
    for shot in range(30):
        square = random.choice(board.letters) + random.choice(board.numbers)
        board.fire(square, sarah)
    print(board.show(to = 'foe'))
    print(board.show())


if __name__ == '__main__':
    # Play the game without the interface.
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    game = Battleships(player.Humanoid(name), '')
    game.play()
