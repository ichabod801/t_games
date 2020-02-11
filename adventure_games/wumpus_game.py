"""
wumpus_hunt_game.py

A game of Hunt the Wumpus.

Constants:
BAT_TEXT: The text to display for being grabbed by giant bats. (str)
CREDITS: The credits for Hunt the Wumpus. (str)
OPTIONS: The options for Hunt the Wumpus. (str)
PIT_TEXT: The text to display for falling down a pit. (str)
RULES: The rules for Hunt the Wumpus. (str)
WIFF_TEXT: The text to display for a missed shot. (str)
WUMPUS_TEXT: The text to display when you get eaten by a wumpus. (str)

Classes:
Cave: One cave in a cave complex. (board.BoardCell)
Dodecahedron: Caves arranged as the vertices of a dodecahedron. (LineBoard)
Wumpus: A game of Hunt the Wumpus. (game.Game)
"""


import random
import re

from .. import board
from .. import game
from ..utility import num_text

BAT_TEXT = """
You are grabbed by a giant, screeching bat and flown through the caves at
random."""

CREDITS = """
Game Design/Original Programming: Gregory Yob
Python Game Programming: Craig "Ichabod" O'Brien
"""

OPTIONS = """
arrows= (a=): How many arrows you get. (1 to 5, defaults to 5)
gonzo (gz): Equivalent to 'arrows = 1'.
"""

PIT_TEXT = """
You stumble in the dark and fall down a bottomless pit. Well, okay, it's got a
bottom. Give us some room for poetic license here."""

RULES = """
The goal is to search the cave system for the wumpus, a large and heavy beast
with a gaping maw and wall-climbing suckers it's claws. You also have to watch
out for giant bats that will carry you off to some place you may not want to go
and bottomless pits. As you go through the caves you will sense when you get
near to the hazards of the caves: you can hear the bats, feel the draft from
the pits, and smell the fould stench of the wumpus (he's not big on bathing).
You have five crooked arrows to shoot the wumpus with, but if you miss the
wumpus, he may move to a different cave.

The commands are:
   LEFT: Move through the left hand passage.
   RIGHT: Move through the right hand passage.
   BACK: Move through the passage behind you.
   CLIMB: Climb out of the cave system (only from the cave you started in).
   SHOOT: Shoot a crooked arrow. You can provide 1-3 directions for the arrow
      to travel through the passages (frex, SHOOT LRL).
   RULES: Read these fascinating, well written instructions again.
"""

UP_TEXT = """
You climb back out of the bowels of the earth.

All right, we'll call it a draw."""

WIFF_TEXT = """
You hear an arrow break uselessly against a cave wall. Then you hear a grumble
and a strange suck-pop sound."""

WUMPUS_TEXT = """
The heavy weight of a wumpus lands on you, and you are trapped in it's sucker
tipped claws. In seconds you are shoved into it's huge maw and eaten alive."""


class Cave(board.BoardCell):
    """
    One cave in a cave complex. (board.BoardCell)

    Attributes:
    adjacent: The caves reachable from this cave. (list of Cave)
    bats: A flag for the cave containing giant bats. (bool)
    description: A short description of the cave. (str)
    location: A unique identifier for the cave. (int)
    pit: A flag for the cave containing a bottomless pit. (bool)
    wumpus: A flag for the cave containing the wumpus. (bool)

    Overridden Methods:
    __init__
    __repr__
    __str__
    """

    def __init__(self, location):
        """
        Set up the default attributes of the cave. (None)

        Parameters:
        location: The location of the cave. (int)
        """
        self.location = location
        self.contents = None
        self.empty = ''
        self.adjacent = []
        self.description = ''
        self.pit = False
        self.bats = False
        self.wumpus = False

    def __repr__(self):
        """Generate a debugging text representation."""
        # Get the base text.
        text = '<Cave {}'.format(self.location)
        # Add text for any flags that are on.
        for flag in ('bats', 'pit', 'wumpus'):
            if getattr(self, flag):
                text = '{} {}'.format(text, flag.capitalize())
        return '{}>'.format(text)

    def __str__(self):
        """Human readable text representation."""
        lines = [self.description]
        flap, draft = False, False
        for cave in self.adjacent:
            flap = flap or cave.bats
            draft = draft or cave.pit
            if cave.wumpus:
                lines.append('You smell a foul odor.')
        if draft:
            lines.append('You feel a cool draft.')
        if flap:
            lines.append('You hear a stange flapping sound.')
        return '\n'.join(lines)


class Dodecahedron(board.LineBoard):
    """
    A cave complex arranged as the vertices of a dodecahedron. (board.LineBoard)

    Attributes:
    current: The cave the player is currently in. (Cave)
    previous: The last cave the player was in. (Cave)
    start: The cave the player started in. (Cave)
    wumpus: The cave containing the wumpus. (Cave)

    Class attributes:
    adjacent: The connections between the caves. (tuple of tuple of int)
    descriptions: The cave descriptions. (tuple of str)

    Methods:
    bats: Move the player to a random cave. (None)
    move: Move the player in the specified direction. (None)
    move_wumpus: Move the wumpus after a miss. (None)
    next_cave: Determine the next cave in a given direction. (Cave)

    Overridden Methods:
    __init__
    """

    adjacent = ((0, 0, 0), (5, 6, 2), (1, 7, 3), (2, 8, 4), (3, 9, 5), (4, 10, 1), (1, 15, 11), (2, 11, 12),
        (3, 12, 13), (4, 13, 14), (5, 14, 15), (6, 16, 7), (7, 17, 8), (8, 18, 9), (9, 19, 10), (10, 20, 6),
        (11, 20, 17), (12, 16, 18), (13, 17, 19), (14, 18, 20), (15, 19, 16))

    descriptions = ('', 'wumpus dung in the corner', '', '', '', '', 'ants crawling all over everything',
        'lots of cobwebs', 'a dart board on the wall', 'a spooky echo', 'remains of a fire',
        'rude graffiti on the wall', 'a battered helmet on the floor', 'a pile of junk in the corner',
        'a family of lizards hiding in cracks in the wall', 'a strange mist in the air',
        'several notches marked on the wall', 'an obelisk carved out of a stalagmite', 'a tall roof',
        'a skull on the floor', 'a big red X marked on the floor')

    def __init__(self):
        """Set up the cave complex. (None)"""
        # Set the base board.
        super(Dodecahedron, self).__init__(20, cell_class = Cave)
        # Set the adjacent locations and descriptions.
        random_locations = list(range(1, 21))
        random.shuffle(random_locations)
        for cave_index, random_index in enumerate(random_locations, start = 1):
            self.cells[cave_index].adjacent = tuple(self.cells[adj] for adj in self.adjacent[cave_index])
            self.cells[random_index].description = self.descriptions[cave_index]
        # Set the special caves.
        self.cells[random_locations[0]].wumpus = True
        self.wumpus = self.cells[random_locations[0]]
        self.cells[random_locations[1]].bats = True
        self.cells[random_locations[2]].bats = True
        self.cells[random_locations[3]].pit = True
        self.cells[random_locations[4]].pit = True
        self.current = self.cells[random_locations[random.randrange(5, 20)]]
        self.start = self.current
        self.previous = self.current.adjacent[0]

    def bats(self):
        """Move the player to a random cave. (None)"""
        # randomize current (with arbitrary previous)
        self.current = self.cells[random.randrange(1, 21)]
        self.previous = self.current.adjacent[0]

    def move(self, direction):
        """
        Move the player in the specified direction. (None)

        Parameters:
        direction: the direction (L/R/B) to move the player. (str)
        """
        self.previous, self.current = self.current, self.next_cave(self.previous, self.current, direction)

    def move_wumpus(self):
        """
        Move the wumpus after a miss. (None)

        There is a one in four chance the wumpus does not move.
        """
        # randomly choose from current and adjacent
        self.wumpus.wumpus = False
        self.wumpus = random.choice([self.wumpus] + list(self.wumpus.adjacent))
        self.wumpus.wumpus = True

    def next_cave(self, previous, current, direction):
        """
        Determine the next cave in a given direction. (Cave)

        Directions are relative depending on how you came into the cave, so the
        cave itself cannot determine the next cave in a given direction.

        Parameters:
        previous: The cave for 'back' moves. (Cave)
        current: The cave being moved from. (Cave)
        direction: The direction (L/R/B) of the move. (str)
        """
        # find back in the adjacent list
        back_index = current.adjacent.index(previous)
        # assume adjacent list is in clockwise order
        if direction == 'B':
            next_cave = current.adjacent[back_index]
        elif direction == 'L':
            next_cave = current.adjacent[(back_index + 1) % 3]
        elif direction == 'R':
            next_cave = current.adjacent[back_index - 1]
        return next_cave


class Wumpus(game.Game):
    """
    A game of Hunt the Wumpus.

    Attributes:
    arrows: The number of crooked arrows to start with. (int)
    arrows_left: The number of crooked arrows left. (int)
    caves: The cave system. (Dodecahedron)

    Methods:
    do_back: Go back the way you came. (bool)
    do_left: Take the left hand passage. (bool)
    do_right: Take the right hand passage. (bool)
    do_shoot: Shoot a crooked arrow. (bool)
    do_up: Climb out of the caves. (u)

    Overridden Methods:
    game_over
    set_options
    set_up
    """

    aka = ['Wumpus', 'HuTW']
    aliases = {'b': 'back', 'l': 'left', 'r': 'right', 's': 'shoot', 'u': 'up'}
    categories = ['Adventure Games']
    credits = CREDITS
    shoot_re = re.compile('^[BRL]{1,3}$')
    name = 'Hunt the Wumpus'
    num_options = 1
    options = OPTIONS
    rules = RULES

    def __str__(self):
        """Human readable text representation. (str)"""
        text = '\nYou are in a cave with {}\n\nYou have {} left.'
        return text.format(self.caves.current, num_text(self.arrows_left, 'crooked arrow'))

    def do_gipf(self, argument):
        """
        Battleships forces the wumpus to move.

        Hangman gives you directions to the nearest pit.

        Pig summons the giant bats.
        """
        # Check the argument.
        game, losses = self.gipf_check(argument, ('battleships', 'hangman', 'pig'))
        go = False
        # Successful Battleships moves the wumpus.
        if game == 'battleships':
            if not losses:
                self.human.tell('\nYou hear a grumbling roar and a strange suck-pop sound.')
                self.caves.move_wumpus()
        # Successful Hangman finds the nearest pit.
        elif game == 'hangman':
            if not losses:
                # Breadth first search to find the nearest pit.
                caves = [('', self.caves.previous, self.caves.current)]
                # Allow going backwards, but only as the first move
                back_cave = self.caves.next_cave(self.caves.previous, self.caves.current, 'B')
                caves.append(('B', self.caves.current, back_cave))
                while True:
                    path, previous, current = caves.pop(0)
                    for direction in ('L', 'R'):
                        new_cave = self.caves.next_cave(previous, current, direction)
                        new_path = path + direction
                        if new_cave.pit:
                            break
                        else:
                            caves.append((new_path, current, new_cave))
                    # Double break from while loop.
                    if new_cave.pit:
                        break
                # Display the result.
                self.human.tell('\nThe path to the nearest pit is {}.'.format(new_path))
                go = True
        # Successful Pig summons a giant bat.
        elif game == 'pig':
            if not losses:
                self.human.tell(BAT_TEXT)
                self.caves.bats()
        # Otherwise I'm confused.
        elif game == 'invalid-game':
            self.human.tell("\nYou're hunting a wumpus, not a gipf.")
            go = True
        return go

    def do_back(self, arguments):
        """
        Go back the way you came. (b)
        """
        self.caves.move('B')

    def do_left(self, arguments):
        """
        Take the left hand passage. (l)
        """
        self.caves.move('L')

    def do_right(self, arguments):
        """
        Take the right hand passage. (r)
        """
        self.caves.move('R')

    def do_shoot(self, arguments):
        """
        Shoot a crooked arrow. (s)

        Give up to three directions as an argument, as in 'shoot lrl', or 'shoot brl'.
        """
        # Check arguments.
        arguments = arguments.upper()
        if not self.shoot_re.match(arguments):
            self.human.error('Invalid arguments to the shoot command: {!r}.'.format(arguments))
            return True
        # Check arrows.
        if not self.arrows_left:
            self.human.tell('You do not have any arrows left.')
            return True
        self.arrows_left -= 1
        # initialize the arrow location
        target = self.caves.current
        shooter = self.caves.previous
        # shoot through up to three caves
        for char in arguments[:3]:
            # move the arrow
            shooter, target = target, self.caves.next_cave(shooter, target, char)
            # check for a hit
            if target.wumpus:
                self.caves.wumpus = None
                return False
            if target.location == self.caves.current.location:
                self.arrows_left = -1
                return False
            # indicate a miss (for that cave at least)
            self.human.tell('Wiff!')
        self.caves.move_wumpus()
        self.human.tell(WIFF_TEXT)
        return False

    def do_up(self, arguments):
        """
        Climb out of the caves. (u)

        This can only be done in the cave you started in.
        """
        if self.caves.current == self.caves.start:
            self.caves.current = None
            return False
        else:
            self.human.error('There is no way up from here.')
            return True

    def game_over(self):
        """See if the human or wumpus has died. (bool)"""
        if self.caves.current is None:
            self.human.tell(UP_TEXT)
            self.win_loss_draw[2] = 1
        elif self.arrows_left == -1:
            self.human.tell('\nNice shot, right into your own chest.')
            self.win_loss_draw[1] = 1
        elif self.caves.current.wumpus:
            self.human.tell(WUMPUS_TEXT)
            self.win_loss_draw[1] = 1
        elif self.caves.current.pit:
            self.human.tell(PIT_TEXT)
            self.win_loss_draw[1] = 1
        elif self.caves.wumpus is None:
            self.human.tell('\nYou hear the horrible screams of a dying wumpus.\n\nYou win!')
            self.win_loss_draw[0] = 1
        else:
            return False
        return True

    def player_action(self, player):
        """
        Handle the player's next action. (bool)

        Parameters:
        player: The current player. (player.Player)
        """
        go = super(Wumpus, self).player_action(player)
        while self.caves.current is not None and self.caves.current.bats and not self.caves.current.wumpus:
            self.human.tell(BAT_TEXT)
            self.caves.bats()
        return go

    def set_options(self):
        """Set the possible options for the game. (None)"""
        self.option_set.add_option('arrows', ['a'], int, valid = (1, 2, 3, 4, 5), default = 5,
            question = "How many arrows should you get (1 to 5, return for 5)? ")
        self.option_set.add_group('gonzo', ['gz'], 'arrows = 1')

    def set_up(self):
        """Set up the caves and the tracking variables. (None)"""
        self.caves = Dodecahedron()
        self.arrows_left = self.arrows
