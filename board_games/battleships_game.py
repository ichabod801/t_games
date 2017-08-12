"""
battleships_game.py

A game of Battleships.

!! Make the coordiates an object, for easier handling. (should be in board.py)
!! Have a 3D version named Yamato. 5x5x5, longest ship would be 4.
    (already done by Solvenians, see Wikipedia)

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

import tgames.game as game
import tgames.player as player


# The design and programming credits.
CREDITS = """
Although Milton-Bradley did make a version of this game, it is a traditional
game dating back to the First World War.

Programming by Craig "Ichabod" O'Brien.
"""

# Different inventories of ships to place.
INVENTORIES = {'bradley': {'Carrier': (5, 1), 'Battleship': (4, 1), 'Cruiser': (3, 1), 
        'Destroyer': (2, 1), 'Submarine': (3, 1)},
    'bednar': {'Carrier': (5, 1), 'Battleship': (4, 1), 'Cruiser': (3, 1),
        'Destroyer': (2, 2), 'Submarine': (1, 2)},
    'ichabod': {'Carrier': (5, 1), 'Battleship': (4, 2), 'Cruiser': (3, 3),
        'Destroyer': (2, 4), 'Submarine': (1, 1)},
    'wikipedia': {'Carrier': (6, 1), 'Battleship': (4, 2), 'Cruiser': (3, 3),
        'Destroyer': (2, 4), 'Submarine': (1, 0)}}

# The rules of the game.
RULES = """
You layout your ships on your board. Only you can see where your ships are. 
Each ship takes up one or more squares on the board. Ships must be arranged
orthogonally, and cannot be orthogonally adjacent to each other.

Then you and your opponent simultaneously fire shots at each other's boards.
You are told if the shot is a hit or a miss. If all of the squares on a ship
are hit, that ship is sunk, and the person who sunk it is informed. If all of
your ships are sunk, you lose the game.

You will be shown two grids, with the columns labelled 0-9 and the rows 
labelled A-J. You call shots (and place ships) by using letter-number
coordinates, such as A8. The top grid represents your opponents board, and the
bottom grid represents your board. Hits are marked 'X', misses are marked '/',
and ship squares not yet hit (on your board only) are marked 'O'.

Options:

inventory=: This determines the number and size of ships played with. The
value can be Bradley (the Milton Bradley version), Bednar (an open source
version by Samuel Bednar), Ichabod (the version I remember), and Wikipedia
(the inventory shown in a picture in the Wikipedia article on the game.) the
inventories give the following ships (name size x count):
    Bradley: Carrier 5x1, Battleship 4x1, Cruiser 3x1, Destroyer 2x1,
        Submarine 3x1.
    Bednar: Carrier 5x1, Battleship 4x1, Cruiser 3x1, Destroyer 2x2,
        Submarine 1x2.
    Ichabod: Carrier 5x1, Battleship 4x2, Cruiser 3x3, Destroyer 2x4,
        Submarine 1x1.
    Wikipedia: Carrier 6x1, Battleship 4x2, Cruiser 3x3, Destroyer 2x4,
        No Submarine.
"""

#A regular expression matching coordinate.
SQUARE_RE = re.compile(r'[ABCDEFGHIJ]\d')


class Battleships(game.Game):
    """
    A game of Battleships. (object)

    Attributes:
    boards: The boards for each player. (dict of str: SeaBoard)
    bot: The bot opponent. (player.Bot)
    inventory_name: The name of the inventory of ships. (str)

    Overridden Methods:
    handle_options
    game_over
    player_turn
    set_up
    """

    aka = ['Battleship', 'Sea Battle', 'Broadsides']
    categories = ['Board Games', 'Displace Games']
    credits = CREDITS
    name = 'Battleships'
    rules = RULES

    def handle_options(self):
        """Handle game options and set the player list. (None)"""
        # Set the defaults.
        self.bot = BattleBot([self.human.name])
        self.inventory_name = 'bradley'
        # Check for options
        if self.raw_options.strip():
            for word in self.raw_options.lower().split():
                if word.startswith('inventory='):
                    value = word[10:]
                    if value in INVENTORIES:
                        self.inventory_name = word[10:]
                    else:
                        self.human.tell('Invalid inventory option.')
        # Get options from the player.
        else:
            while True:
                inventory = self.human.ask('Which inventory would you like to use (return for Bradley)? ')
                if not inventory.lower() or inventory in INVENTORIES:
                    break
                self.human.tell('The available inventories are Bradley, Bednar, Ichabod, and Wikipedia')
            if inventory:
                self.inventory_name = inventory.lower()
        # Set player list.
        self.players = [self.human, self.bot]

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Check for a tie.
        if not (self.boards[self.bot.name].fleet or self.boards[self.human.name].fleet):
            self.human.tell("It's a draw! You destroyed each other's fleets at the same time.")
            self.win_loss_draw[2] = 1
        # Check for a win.
        elif not self.boards[self.bot.name].fleet:
            self.human.tell("You sank {}'s fleet and won!".format(self.bot.name))
            squares_left = sum([len(squares) for ship, squares in self.boards[self.human.name].fleet])
            self.scores[self.human.name] = sum(squares_left)
            self.human.tell("You have {} squares of ships left.".format(squares_left))
            self.win_loss_draw[0] = 1
        # Check for a loss.
        elif not self.boards[self.human.name].fleet:
            self.human.tell("{} sank your fleet. You lose.".format(self.bot.name))
            self.win_loss_draw[1] = 1
        else:
            # Otherwise, game on.
            return False
        # Report the end of the game.
        return True

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the players' moves.
        while True:
            human_shot = self.human.ask('Where do you want to shoot? ').strip()[:2].upper()
            if SQUARE_RE.match(human_shot):
                break
            self.human.tell('That was an invalid shot.')
        bot_shot = self.bot.ask('Where do you want to shoot? ')
        # Fire the shots.
        self.boards[self.bot.name].fire(human_shot, self.human)
        self.boards[self.human.name].fire(bot_shot, self.bot)
        # Update the human. (Bots don't need updates.)
        self.human.tell(self.boards[self.bot.name].show(to = 'foe'))
        self.human.tell(self.boards[self.human.name].show())

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
    add_adjacent: Add adjacent squares of a ship to the don't shoot set. (None)
    fire: Decide where to fire the next shot. (str)
    place_ship: Place a ship at random. (str)
    retarget: Reset target list based on a recent hit. (None)

    Overridden Methods:
    __init__
    ask
    tell
    """

    def __init__(self, taken_names):
        """
        Initialize the bot. (None)

        Parameters:
        taken_names: Names already in use in the game. (list of str)
        """
        # Do basic bot initialization.
        super(BattleBot, self).__init__(taken_names)
        # Set up tracking variables.
        self.dont_shoot = set()
        self.targets = []
        self.target_ship = []
        self.last_shot = ''

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
            length = int(prompt[-3])
            return self.place_ship(length)
        # Handle firing shots.
        elif prompt.startswith('Where'):
            return self.fire()

    def fire(self):
        """Decide where to fire the next shot. (str)"""
        # Shoot ranomly when there are no specified targets.
        if not self.targets:
            while True:
                self.last_shot = random.choice(SeaBoard.letters) + random.choice(SeaBoard.numbers)
                if self.last_shot not in self.dont_shoot:
                    break
        # Shoot a random targetted square.
        else:
            self.last_shot = random.choice(self.targets)
            self.targets.remove(self.last_shot)
        # Return the chosen shot.
        self.dont_shoot.add(self.last_shot)
        return self.last_shot

    def place_ship(self, length):
        """
        Place a ship at random. (str)

        Note that this doesn't check for overlapping or adjacent ships. It leaves
        that to the board doing the set up.

        Parameters:
        length: How long the ship should be. (int)
        """
        # !! I might want to move this to SeaBoard so it is an option for humans.
        # Find a random start.
        start = (random.randrange(10), random.randrange(10))
        # Return the start for one-square ships.
        if length == 1:
            return chr(65 + start[0]) + str(start[1])
        # Get a ship of the specified length in every possible direction.
        options = []
        text = '{}{} to {}{}'
        # Check east.
        if start[0] + length - 1 < 10:
            end = (start[0] + length - 1, start[1])
            options.append(text.format(chr(65 + start[0]), start[1], chr(65 + end[0]), end[1]))
        # Check north.
        if start[1] + length - 1 < 10:
            end = (start[0], start[1] + length - 1)
            options.append(text.format(chr(65 + start[0]), start[1], chr(65 + end[0]), end[1]))
        # Check west.
        if start[0] - length + 1 > -1:
            end = (start[0] - length + 1, start[1])
            options.append(text.format(chr(65 + start[0]), start[1], chr(65 + end[0]), end[1]))
        # Check south.
        if start[1] - length + 1 > -1:
            end = (start[0], start[1] - length + 1)
            options.append(text.format(chr(65 + start[0]), start[1], chr(65 + end[0]), end[1]))
        # Pick a directional layout at random.
        return random.choice(options)

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


class SeaBoard(object):
    """
    A board in a game of Battleships. (object)

    Class Attributes:
    letters: The letters for coordinates. (str)
    numbers: The numbers for coordinates. (str)

    Attributes:
    hits: The squares with made shots. (set of str)
    misses: The squares with missed shots. (set of str)

    Methods:
    adjacent_squares: Get the adjacent squares for a given square. (list of str)
    fire: Fire a shot on the board. (None)
    make_ship: Get a list of ship coordinates from the end points. (list of str)
    place_ships: Get the placement of the ships from the player. (None)
    show: Show the current status of the board. (str)
    """

    letters = 'ABCDEFGHIJ'
    numbers = '0123456789'

    def __init__(self, player, inventory_name = 'Bradley'):
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
                    # Check for the correct number of squares.
                    if size == 1 and len(squares) != 1:
                        self.player.tell('You must enter one square for a {}.'.format(ship.lower()))
                        continue
                    elif size > 1 and len(squares) != 2:
                        self.player.tell('Please enter a start and end square.')
                        continue
                    # Get the full list of squares.
                    if size == 1:
                        ship_squares = [squares[0]]
                    else:
                        ship_squares = self.make_ship(*squares)
                    # Check for diagonal ships.
                    if not ship_squares:
                        self.player.tell('Ships must be horizontal or vertical.')
                        continue
                    # Check for the correct size of ship.
                    elif len(ship_squares) != size:
                        self.player.tell('{}s must be {} squares long.'.format(ship.lower(), size))
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
                    self.player.tell('That ship is adjacent to or overlaps another ship.')

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
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    game = Battleships(player.Player(name), '')
    game.play()