"""
battleships_game.py

A game of Battleships.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The design and programming credits. (str)
INVENTORIES: Different inventories of ships to place. (dict of str: tuple)
OPTIONS: The options for Battleships. (str)
RULES: The rules of the game. (str)
SQUARE_RE: A regular expression matching coordinate. (re.SRE_Pattern)

Classes:
Battleships: A game of Battleships. (game.Game)
BattleBot: A bot for playing Battleships. (player.Bot)
SmarterBot: A smarter BattleBot with a search pattern. (BattleBot)
SeaBoard: A board in a game of Battleships. (object)

Functions:
test: Basic testing of the board object. (None)
"""


import random
import re

from .. import board
from .. import game
from .. import options
from .. import player


CREDITS = """
Game Design: Although Milton-Bradley did make a version of this game, it is a
    traditional game dating back to the First World War.
Game Programming: Craig "Ichabod" O'Brien.
"""

OPTIONS = """
bot-level= (b=): How strong the computer opponent is. Can be easy (e) or
    medium (m). Defaults to medium.
inventory= (i=): This determines the number and size of ships played with. The
    value can be Bradley (the Milton Bradley version), Bednar (an open source
    version by Samuel Bednar), Ichabod (the version I remember), and Wikipedia
    (the inventory shown in a picture in the Wikipedia article on the game.)
    The inventories give the following ships (name size x count):
    Bradley/Br: Carrier 5x1, Battleship 4x1, Cruiser 3x1, Destroyer 2x1,
        Submarine 3x1. This is the default layout.
    Bednar/Bd: Carrier 5x1, Battleship 4x1, Cruiser 3x1, Destroyer 2x2,
        Submarine 1x2.
    Gonzo/Gz: Battleship 7x1, Submarine 2x1
    Ichabod/Ik: Carrier 5x1, Battleship 4x2, Cruiser 3x3, Destroyer 2x4,
        Submarine 1x1.
    Wikipedia/Wk: Carrier 6x1, Battleship 4x2, Cruiser 3x3, Destroyer 2x4,
        No Submarine.
"""

INVENTORIES = {'bradley': {'Carrier': (5, 1), 'Battleship': (4, 1), 'Cruiser': (3, 1),
        'Destroyer': (2, 1), 'Submarine': (3, 1)},
    'bednar': {'Carrier': (5, 1), 'Battleship': (4, 1), 'Cruiser': (3, 1),
        'Destroyer': (2, 2), 'Submarine': (1, 2)},
    'gonzo': {'Battleship': (7, 1), 'Submarine': (2, 1)},
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
    inventory_aliases = {'br': 'bradley', 'bd': 'bednar', 'gz': 'gonzo', 'ik': 'ichabod', 'wk': 'wikipedia'}
    name = 'Battleships'
    num_options = 2
    options = OPTIONS
    rules = RULES

    def do_gipf(self, arguments):
        """
        Canfield gives you a random hit for your next shot.

        Pig gives you a free shot if you hit on your next shot.

        Hunt the Wumpus tells you a random square of a specific ship type.
        """
        game, losses = self.gipf_check(arguments, ('wumpus', 'pig', 'canfield'))
        go = True
        # Hunt the Wumpus tells you where a particular ship type is.
        if game == 'hunt the wumpus':
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
            self.human.tell(self.boards[self.bot].show(to = 'foe'))
            self.human.tell(self.boards[self.human].show())
        return go

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Check for a tie.
        if not (self.boards[self.bot].fleet or self.boards[self.human].fleet):
            self.human.tell("\nIt's a draw! You destroyed each other's fleets at the same time.")
            self.win_loss_draw[2] = 1
        # Check for a win.
        elif not self.boards[self.bot].fleet:
            self.human.tell("\nYou sank {}'s fleet and won!".format(self.bot))
            squares_left = sum([len(ship) for ship in self.boards[self.human].fleet])
            self.scores[self.human] = squares_left
            self.human.tell("You have {} squares of ships left.".format(squares_left))
            self.win_loss_draw[0] = 1
        # Check for a loss.
        elif not self.boards[self.human].fleet:
            self.human.tell("\n{} sank your fleet. You lose.".format(self.bot))
            squares_left = sum([len(ship) for ship in self.boards[self.bot].fleet])
            self.scores[self.human] = squares_left * -1
            self.human.tell("{} had {} squares of ships left.".format(self.bot, squares_left))
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
        for ship, ship_squares in self.boards[self.bot].fleet:
            not_hit.extend(set(ship_squares) - self.boards[self.bot].hits)
        human_shot = random.choice(not_hit)
        self.human.tell('You fired on {}.'.format(human_shot))
        # Get the bot's shot.
        bot_shot = self.bot.ask('\nWhere do you want to shoot? ')
        # Fire the shots.
        self.boards[self.bot].fire(human_shot.upper(), self.human)
        self.boards[self.human].fire(bot_shot, self.bot)
        # Update the human. (Bots don't need updates.)
        self.human.tell(self.boards[self.bot].show(to = 'foe'))
        self.human.tell(self.boards[self.human].show())

    def gipf_pig(self):
        """Handle the Pig edge. (None)"""
        # Remind the human.
        self.human.tell(self.boards[self.bot].show(to = 'foe'))
        self.human.tell(self.boards[self.human].show())
        # Get the first shot.
        while True:
            human_shot = self.human.ask('\nWhere do you want to shoot? ').upper()
            if SQUARE_RE.match(human_shot):
                break
        bot_shot = self.bot.ask('Where do you want to shoot? ')
        # Fire the shots.
        self.boards[self.bot].fire(human_shot, self.human)
        self.boards[self.human].fire(bot_shot, self.bot)
        # Check for second shot.
        if human_shot in self.boards[self.bot].hits:
            self.human.tell('You hit, so you get a bonus shot.')
            while True:
                human_shot = self.human.ask('Where do you want to shoot? ').upper()
                if SQUARE_RE.match(human_shot):
                    break
            self.boards[self.bot].fire(human_shot, self.human)
        # Update the human. (Bots don't need updates.)
        self.human.tell(self.boards[self.bot].show(to = 'foe'))
        self.human.tell(self.boards[self.human].show())

    def gipf_wumpus(self):
        """Handle the Hunt the Wumpus edge. (None)"""
        # Remind the human.
        self.human.tell(self.boards[self.bot].show(to = 'foe'))
        self.human.tell(self.boards[self.human].show())
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
            self.bot = BattleBot(taken_names = [self.human])
        elif self.bot_level.startswith('m'):
            self.bot = SmarterBot(taken_names = [self.human])
        self.players = [self.human, self.bot]

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Update the human. (Bots don't need updates.)
        self.human.tell(self.boards[self.bot].show(to = 'foe'))
        self.human.tell(self.boards[self.human].show())
        # Get the players' moves.
        human_shot = self.human.ask('\nWhere do you want to shoot? ')
        if not SQUARE_RE.match(human_shot.upper()):
            self.player_index = 0  # Make sure output goes to the human.
            return self.handle_cmd(human_shot)
        bot_shot = self.bot.ask('\nWhere do you want to shoot? ')
        # Fire the shots.
        self.boards[self.bot].fire(human_shot.upper(), self.human)
        self.boards[self.human].fire(bot_shot, self.bot)

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.add_option('inventory', ['i'], converter = options.lower, default = 'bradley',
            target = 'inventory_name',
            valid = ['bradley', 'br', 'bednar', 'bd', 'gz', 'gonzo', 'ichabod', 'ik', 'wikipedia', 'wk'],
            question = 'Which inventory would you like to use (return for Bradley)? ',
            error_text = 'The available inventories are Bradley, Bednar, Ichabod, and Wikipedia')
        self.option_set.add_option('bot-level', ['b'], converter = options.lower, default = 'medium',
            valid = ['e', 'easy', 'm', 'medium'],
            question = 'How hard should the bot be (Easy or Medium, return for medium)? ')
        self.option_set.add_group('gonzo', ['gz'], 'inventory = gonzo')

    def set_up(self):
        """Set up a board for each player. (None)"""
        self.bot = [player for player in self.players if player != self.human][0]
        self.boards = {self.bot: SeaBoard(self.bot, self.inventory_name)}
        self.boards[self.human] = SeaBoard(self.human, self.inventory_name)


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
            self.dont_shoot.update(self.game.boards[self].adjacent_squares(square))

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
            new_shot = board.Coordinate((random.randint(1, 10), random.randint(1, 10)))
            if new_shot not in self.dont_shoot:
                break
        return new_shot

    def retarget(self):
        """Reset target list based on a recent hit. (None)"""
        adjacents = list(self.game.boards[self].adjacent_squares(self.last_shot))
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
        for row in range(1, 11):
            new_line.append(board.Coordinate((start + 1, row)))
            start = (start + self.search_direction) % 10
        # Add them to the search pattern without impossible squares
        self.search_squares.extend(new_line)
        self.search_squares = list(set(self.search_squares) - self.dont_shoot)

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
        for size, count in INVENTORIES[self.game.inventory_name].values():
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


class Ship(object):
    """
    A ship in the game of Battleships. (object)

    Attributes:
    name: The name of the type of ship. (str)
    sections: The cells the ship is in. (list of Coordinate)

    Overridden Methods:
    __init__
    __bool__
    __repr__
    __str__
    """

    def __init__(self, name, sections):
        """
        Set up the ship. (None)

        Parameters:
        name: The name of the type of ship. (str)
        sections: The cells the ship is in. (list of Coordinate)
        """
        self.name = name
        self.sections = sections

    def __bool__(self):
        """Convert to true or false. (bool)"""
        return bool(self.sections)

    def __len__(self):
        """Give the length (sections left) of the ship. (int)"""
        return len(self.sections)

    def __nonzero__(self):
        """Convert to true or false. (bool)"""
        return bool(self.sections)

    def __repr__(self):
        """Dubugging text representation. (str)"""
        return '<Ship {}>'.format(', '.join(str(cell) for cell in self.sections))

    def __str__(self):
        """Human readable text representation. (str)"""
        return self.name.lower()


class Wake(object):
    """
    A piece representing a square adjacent to a ship. (object)

    Overridden Methods:
    __str__
    """

    def __str__(self):
        """Human readable text representation. (str)"""
        return '.'


class Hit(Wake):
    """
    A piece representing a square that had been successfully hit. (Wake)

    Overridden Methods:
    __str__
    """

    def __str__(self):
        """Human readable text representation. (str)"""
        return 'X'


class Miss(Wake):
    """
    A piece representing a square that had been unsuccessfully shot. (Wake)

    Overridden Methods:
    __str__
    """

    def __str__(self):
        """Human readable text representation. (str)"""
        return '/'


class Section(Wake):
    """
    A piece representing part of a ship. (Wake)

    Attributes:
    ship: The ship the square is a part of. (Ship)
    square: The square the ship is in. (board.Coordinate)

    Methods:
    hit: Record a hit to this section of the ship. (None)

    Overridden Methods:
    __init__
    __repr__
    __str__
    """

    def __init__(self, square, ship):
        """
        Record the section's attributes. (None)

        Parameters:
        square: The square the ship is in. (board.Coordinate)
        ship: The ship the square is a part of. (Ship)
        """
        self.square = square
        self.ship = ship

    def __repr__(self):
        """Debugging text representation. (str)"""
        return '<{} of {!r}>'.format(self.square, self.ship)

    def __str__(self):
        """Human readable text representation. (str)"""
        return 'O'

    def hit(self):
        """Record a hit to this section of the ship. (None)"""
        self.ship.sections.remove(self.square)


class Water(board.BoardCell):
    """
    A cell in a SeaBoard. (board.BoardCell)

    Overridden Methods:
    __init__
    """

    def __init__(self, location):
        """
        Initialize the cell. (None)

        Parameters:
        location: The location of the cell on the board. (hashable)
        """
        super(Water, self).__init__(location, piece = None, empty = '.')


class SeaBoard(board.DimBoard):
    """
    A board in a game of Battleships. (object)

    Class Attributes:
    letters: The letters for coordinates. (str)
    numbers: The numbers for coordinates. (str)
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
        # Set up the base board object.
        super(SeaBoard, self).__init__((10, 10), Water)
        # Set the specified attributes.
        self.player = player
        self.inventory = INVENTORIES[inventory_name]
        # Get the ships placed.
        self.place_ships()

    def adjacent_squares(self, square):
        """
        Create a generator for the squares around a square. (generator)

        Parameters:
        square: The square to get the neighbors of. (board.Coordinate)
        """
        if isinstance(square, str):
            square = self.convert(square)
        for offset in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            adjacent = square + offset
            if adjacent in self.cells:
                yield adjacent

    def convert(self, square):
        """
        Convert a letter-number square id to a coordinate. (Coordinate)

        Parameters:
        square: an A1 style square identifier. (str)
        """
        return board.Coordinate((self.letters.index(square[0]) + 1, self.numbers.index(square[1]) + 1))

    def fire(self, square, foe):
        """
        Fire a shot on the board. (None)

        Parameters:
        square: The square to shoot at. (board.Coordinate)
        foe: The player making the shot. (player.Player)
        """
        # Check the cell for a ship section.
        if isinstance(square, str):
            square = self.convert(square)
        current = self.cells[square].contents
        if isinstance(current, Section):
            # Hit the section
            foe.tell('You hit.')
            ship = current.ship
            current.hit()
            self.place(square, Hit())
            # Check for sinking a ship.
            if not ship:
                self.player.tell('Your {} has been sunk.'.format(ship))
                foe.tell('You sank a {}.'.format(ship))
                self.fleet.remove(ship)
        else:
            # Handle a miss.
            foe.tell('You missed.')
            if not isinstance(current, Hit):
                self.place(square, Miss())

    def make_ship(self, start, end):
        """
        Get a list of ship coordinates from the end points. (list of str)

        If the ship is diagonal, an empty list is returned to indicated
        an invalid ship definition.

        Parameters:
        start: The starting square of the ship. (board.Coordinate)
        end: The ending square of the ship. (board.Coordinate)
        """
        # Make the direction positive.
        start, end = sorted([start, end])
        # Determine ship orientation.
        if start[0] == end[0]:
            offset = (0, 1)
        elif start[1] == end[1]:
            offset = (1, 0)
        else:
            return []
        # Generate the ship squares
        squares = [start]
        while squares[-1] != end:
            squares.append(squares[-1] + offset)
        return squares

    def place_random(self, size):
        """
        Place a ship randomly. (list of str)

        Parameters:
        size: The size of the ship to place. (int)
        """
        while True:
            # Get a random line of the specified size.
            same_index = random.randrange(1, 11)
            start_index = random.randrange(1, 12 - size)
            end_index = start_index + size - 1
            # Get the start and end squares, randomly horizontal or vertical.
            if random.random() < 0.5:
                start = board.Coordinate((same_index, start_index))
                end = board.Coordinate((same_index, end_index))
            else:
                start = board.Coordinate((start_index, same_index))
                end = board.Coordinate((end_index, same_index))
            # Check the ship for valid placement
            ship_squares = self.make_ship(start, end)
            for square in ship_squares:
                if self.cells[square]:
                    break
            else:
                # Return the first valid placement found.
                return start, end

    def place_ships(self):
        """Get the placement of the ships from the player. (None)"""
        # Get the available ships sorted by size.
        ships = sorted(self.inventory.items(), key = lambda ship: (ship[1][0], ship[0]), reverse = True)
        # Set up the tracking variables.
        self.fleet = []
        # Loop through the ships.
        for ship_type, (size, count) in ships:
            # Loop through multiple copies of the same size.
            for ship_index in range(count):
                # Show the current layout to the player.
                self.player.tell(self.show())
                while True:
                    # Get the start and end squares from the player
                    message = '\nPlace {} #{} of {}, length {}: '
                    move = self.player.ask(message.format(ship_type.lower(), ship_index + 1, count, size))
                    squares = [self.convert(square) for square in SQUARE_RE.findall(move.upper())]
                    # Check for random placement.
                    if move.lower() in ('r', 'rand', 'random'):
                        squares = self.place_random(size)
                    # Check for the correct number of squares.
                    elif size == 1 and len(squares) != 1:
                        self.player.error('You must enter one square for a {}.'.format(ship_type.lower()))
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
                        self.player.error('{}s must be {} squares long.'.format(ship_type, size))
                        continue
                    # Check for adjacent or overlapping ships.
                    for square in ship_squares:
                        if self.cells[square]:
                            break
                    else:
                        # Track and store valid ships.
                        ship = Ship(ship_type, ship_squares)
                        for square in ship_squares:
                            self.place(square, Section(square, ship))
                            for wake_cell in self.adjacent_squares(square):
                                if not self.cells[wake_cell]:
                                    self.place(wake_cell, Wake())
                        self.fleet.append(ship)
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
        for row in range(10, 0, -1):
            line = [self.letters[row - 1]]
            for column in range(1, 11):
                line.append(str(self.cells[(row, column)]))
            line_text = ''.join(line)
            if to == 'foe':
                line_text = line_text.replace('O', '.')
            lines.append(line_text)
        # End with an axis label.
        lines.append(' 0123456789')
        return '\n'.join(lines)
