"""
wumpus_game.py

A game of Hunt the Wumpus.

This is at least the third time I have used the Cave and Dodecahedron objects
to create a Hunt the Wumpus game. However, I want to redo those as subclasses
of Board and MultiCell.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
ADJACENT: Adjacent points on a dodecahedron. (list of tuple of int)
CREDITS: The game design and programming credits. (str)
DESCRIPTIONS: The room descriptions. (list of str)
OPTIONS: The options for Hunt the Wumpus. (str)
RULES: Text describing the game. (str)

Classes:
Cave: One cave in a cave complex. (object)
Dodecahedron: A cave complex arranged as a dodecahedron. (object)
Wumpus: A game of Hunt the Wumpus. (game.Game)
"""


import random

from .. import game


ADJACENT = [(4, 5, 1), (0, 6, 2), (1, 7, 3), (2, 8, 4), (3, 9, 0),
    (0, 14, 10), (1, 10, 11), (2, 11, 12), (3, 12, 13), (4, 13, 14),
    (5, 15, 6), (6, 16, 7), (7, 17, 8), (8, 18, 9), (9, 19, 5),
    (10, 19, 16), (11, 15, 17), (12, 16, 18), (13, 17, 19), (14, 18, 15)]

CREDITS = """
Game Design/Original Programming: Gregory Yob
Python Game Programming: Craig "Ichabod" O'Brien
"""

DESCRIPTIONS = ['wumpus dung in the corner', '', '', '', '', 'ants crawling all over everything',
    'lots of cobwebs', 'a dart board on the wall', 'a spooky echo', 'remains of a fire',
    'rude graffiti on the wall', 'a battered helmet on the floor', 'a pile of junk in the corner',
    'a family of lizards hiding in cracks in the wall', 'a strange mist in the air',
    'several notches marked on the wall', 'an obelisk carved out of a stalagmite', 'a tall roof',
    'a skull on the floor', 'a big red X marked on the floor']

OPTIONS = """
arrows= (a=): How many arrows you get. (1 to 5, defaults to 5)
gonzo (gz): Equivalent to 'arrows = 1'.
"""

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


class Cave(object):
    """
    One cave in a cave complex. (object)

    Attributes:
    adjacent: The caves reachable from this cave. (list of Cave)
    bats: A flag for the cave containing giant bats. (bool)
    description: A short description of the cave. (str)
    id: A unique identifier for the cave. (int)
    pit: A flag for the cave containing a bottomless pit. (bool)
    wumpus: A flag for the cave containing the wumpus. (bool)

    Overridden Methods:
    __init__
    __eq__
    """

    def __init__(self, id):
        """
        Set up the default attributes of the cave. (None)

        Parameters:
        id: A unique identifier for the cave. (int)
        """
        self.id = id
        self.adjacent = []
        self.description = ''
        self.pit = False
        self.bats = False
        self.wumpus = False

    def __repr__(self):
        """Generate a debugging text representation."""
        # Get the base text.
        text = '<Cave {}'.format(self.id)
        # Add text for any flags that are on.
        for flag in ('bats', 'pit', 'wumpus'):
            if getattr(self, flag):
                text = '{} {}'.format(text, flag.capitalize())
        return '{}>'.format(text)

    def __eq__(self, other):
        """
        Compare caves by id. (bool)

        Parameters:
        other: the cave to compare with (Cave)
        """
        if isinstance(other, Cave):
            return self.id == other.id
        else:
            return NotImplemented


class Dodecahedron(object):
    """
    A cave complex arranged as a dodecahedron. (object)

    Attributes:
    caves: The caves in the complex. (list of Cave)
    current: The cave the player is in. (Cave)
    previous: The cave the player was in last. (Cave)
    start: The cave the player started in. (Cave)
    wumpus_start: The cave the wumpus started in. (Cave)

    Methods:
    bats: Move the player to a random cave. (None)
    check_cave: Give the details for the specified cave. (list of str)
    move: Move the player in the specified direction. (None)
    move_wumpus: Move the wumpus after a miss. (None)
    next_cave: Determine the next cave in a given direction. (Cave)
    shoot: Shoot a crooked arrow from the current location. (int)

    Overridden Methods:
    __init__
    """

    def __init__(self):
        """Set up the cave complex and its initial state. (None)"""
        self.caves = [Cave(x) for x in range(20)]
        for cave, adjacent in zip(self.caves, ADJACENT):
            cave.adjacent = [self.caves[id] for id in adjacent]
        # get a random list of caves
        random_locations = list(range(20))
        random.shuffle(random_locations)
        # set descriptions randomly
        for description_index, cave_index in enumerate(random_locations):
            self.caves[cave_index].description = DESCRIPTIONS[description_index]
        # set initial locations, making sure they're all distinct
        self.caves[random_locations[0]].wumpus = True
        self.wumpus_start = self.caves[random_locations[0]]
        self.caves[random_locations[1]].bats = True
        self.caves[random_locations[2]].bats = True
        self.caves[random_locations[3]].pit = True
        self.caves[random_locations[4]].pit = True
        self.current = self.caves[random_locations[random.randrange(5, 20)]]
        self.start = self.current
        # the initial previous cave is arbitrary
        self.previous = self.current.adjacent[0]

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        # Get the base text.
        text = '<Dodecahedron Current: {}; Bats: {}; Pits: {}; Wumpus: {}>'
        # Get the flag data.
        bat_text = ', '.join([str(cave.id) for cave in self.caves if cave.bats])
        pit_text = ', '.join([str(cave.id) for cave in self.caves if cave.pit])
        wumpus_id = [cave.id for cave in self.caves if cave.wumpus][0]
        # Return the base text with the flag data.
        return text.format(self.current, bat_text, pit_text, wumpus_id)

    def bats(self):
        """Move the player to a random cave. (None)"""
        # randomize current (with arbitrary previous)
        self.current = self.caves[random.randrange(20)]
        self.previous = self.current.adjacent[0]

    def check_cave(self, cave = None):
        """
        Give the details for the specified cave. (list of str)

        If the cave parameter is None, the current cave is used. If cave is an
        integer, it gets the cave with that ID.

        Parameter:
        cave: The cave to get details on. (Cave, int, or None)
        """
        # get current if no cave specified
        if cave is None:
            cave = self.current
        # get cave by id if necessary
        elif isinstance(cave, int):
            cave = self.caves[cave]
        # get the description
        text = [cave.description]
        # check for hazards
        if cave.wumpus:
            text.append('WUMPUS')
        elif cave.bats:
            text.append('BATS')
        elif cave.pit:
            text.append('PIT')
        else:
            # if no hazards, check for nearby hazards
            for nearby in cave.adjacent:
                if nearby.bats and 'FLAP' not in text:
                    text.append('FLAP')
                if nearby.wumpus:
                    text.append('SMELL')
                if nearby.pit and 'DRAFT' not in text:
                    text.append('DRAFT')
        return text

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
        old_wumpus = [cave for cave in self.caves if cave.wumpus][0]
        new_wumpus = random.choice([old_wumpus] + old_wumpus.adjacent)
        # reset wumpus indicators
        old_wumpus.wumpus = False
        new_wumpus.wumpus = True

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
            next = current.adjacent[back_index]
        elif direction == 'L':
            next = current.adjacent[(back_index + 1) % 3]
        elif direction == 'R':
            next = current.adjacent[back_index - 1]
        return next

    def shoot(self, direction):
        """
        Shoot a crooked arrow from the current location. (int)

        The return value is >0 for hitting the wumpus, 0 for hitting yourself,
        and <0 for not hitting anything. Absolute value is the number of rooms
        shot through.

        Parameter:
        direction: The (L/R/B) directions to shoot the arrow in (str)
        """
        # initialize the arrow location
        target = self.current
        shooter = self.previous
        # shoot through up to three caves
        rooms = 1
        for char in direction[:3]:
            # move the arrow
            shooter, target = target, self.next_cave(shooter, target, char)
            # check for a hit
            if target.wumpus:
                return rooms
            if target.id == self.current.id:
                return 0
            # indicate a miss (for that cave at least)
            rooms += 1
        return rooms * -1


class Wumpus(game.Game):
    """
    A game of Hunt the Wumpus.

    Attributes:
    arrows: The number of crooked arrows to start with. (int)
    arrows_left: The number of crooked arrows left. (int)
    dodec: The cave system. (Dodecahedron)

    Methods:
    shoot: Fire a crooked arrow. (None)
    status_check: Check the room for hazards and description. (None)

    Overridden Methods:
    game_over
    player_action
    set_options
    set_up
    """

    aka = ['Wumpus', 'HuTW']
    categories = ['Adventure Games']
    credits = CREDITS
    name = 'Hunt the Wumpus'
    num_options = 1
    options = OPTIONS
    rules = RULES

    def do_gipf(self, argument):
        """
        Battleships forces the wumpus to move.

        Hangman gives you directions to the nearest pit.

        Pig summons the giant bats.
        """
        # Check the argument.
        game, losses = self.gipf_check(argument, ('battleships', 'hangman', 'pig'))
        go = True
        # Successful Battleships moves the wumpus.
        if game == 'battleships':
            if not losses:
                self.human.tell('\nYou hear a grumbling roar and a strange suck-pop sound.\n')
                self.dodec.move_wumpus()
                self.status_check()
                return False
        # Successful Hangman finds the nearest pit.
        elif game == 'hangman':
            if not losses:
                # Breadth first search to find the nearest pit.
                caves = [('', self.dodec.previous, self.dodec.current)]
                # Allow going backwards, but only as the first move
                back_cave = self.dodec.next_cave(self.dodec.previous, self.dodec.current, 'B')
                caves.append(('B', self.dodec.current, back_cave))
                while True:
                    path, previous, current = caves.pop(0)
                    for direction in ('L', 'R'):
                        new_cave = self.dodec.next_cave(previous, current, direction)
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
        # Successful Pig summons a giant bat.
        elif game == 'pig':
            if not losses:
                self.human.tell("\nYou are grabbed by a giant, screeching bat and flown through")
                self.human.tell("the caves at random.")
                self.dodec.bats()
                self.status_check()
                return False
        # Otherwise I'm confused.
        elif game == 'invalid-game':
            self.human.tell("\nYou're hunting a wumpus, not a gipf.")
        self.status_check()
        return go

    def game_over(self):
        """Check for the game being over. (bool)"""
        # Game over is flagged elsewhere by changing win/loss/draw.
        if self.win_loss_draw[1]:
            self.human.tell('The wumpus wins. :(')
        elif self.win_loss_draw[0]:
            self.human.tell('You win!')
        elif self.win_loss_draw[2]:
            self.human.tell("Alright, we'll call it a draw.")
        else:
            # Game still on.
            return False
        # Record score and end game.
        self.scores[self.human.name] = self.turns - 1
        return True

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Update the player
        self.human.tell()
        self.status_check()
        # Check for end of game.
        if sum(self.win_loss_draw):
            return False
        move = player.ask('What is your move? ').strip().lower()
        # Check for standard moves that are mediated by the Dodecahedron.
        if move in ('b', 'back'):
            self.dodec.move('B')
        elif move in ('c', 'climb'):
            if self.dodec.current == self.dodec.start:
                player.tell('You climb back out of the bowels of the earth.')
                self.win_loss_draw[2] = 1
            else:
                player.tell('There is no way to climb out of here.')
        elif move in ('l', 'left'):
            self.dodec.move('L')
        elif move in ('q', 'quit'):
            self.win_loss_draw[1] = 1
        elif move in ('r', 'right'):
            self.dodec.move('R')
        # Check for shooting an arrow.
        else:
            words = move.split()
            if words and words[0] in ('s', 'shoot'):
                if len(words) == 2:
                    self.shoot(move.split()[1])
                else:
                    player.error('The shoot command takes one and only one parameter.')
            # Check for other commands.
            else:
                return self.handle_cmd(move)
        # Set the current (losing) score.
        self.scores[self.human.name] = -self.turns

    def set_options(self):
        """Set the possible options for the game. (None)"""
        self.option_set.add_option('arrows', ['a'], int, valid = (1, 2, 3, 4, 5), default = 5,
            question = "How many arrows should you get (1 to 5, return for 5)? ")
        self.option_set.add_group('gonzo', ['gz'], 'arrows = 1')

    def set_up(self):
        """Set up the caves and the tracking variables. (None)"""
        self.dodec = Dodecahedron()
        self.arrows_left = self.arrows

    def shoot(self, arg):
        """
        Fire a crooked arrow. (None)

        Parameters:
        arg: The directions to shoot the arrow in. (str)
        """
        # make sure there are arrows
        if self.arrows_left:
            # update arrows
            self.arrows_left -= 1
            # take the shot
            hit = self.dodec.shoot(arg.upper())
            # Show the results
            for whiff in range(abs(hit) - 1):
                self.human.tell('Whiff!')
            if hit < 0:
                # miss means wumpus may move
                self.human.tell('You hear the arrow break uselessly against a wall.')
                self.human.tell('You hear a grumbling roar and a strange suck-pop sound.')
                self.human.tell('You have {} crooked arrows left.'.format(self.arrows_left))
                self.dodec.move_wumpus()
            elif hit == 0:
                # shooting yourself is a loss
                self.human.tell('Arrgh! You shot yourself in the back')
                self.win_loss_draw[1] = 1
            else:
                # shooting the wumpus is a win
                self.human.tell('You hear the horrible scream of a dying wumpus!')
                self.win_loss_draw[0] = 1
        else:
            self.human.tell("You don't have any arrows left to shoot.")

    def status_check(self):
        """Check the room for hazards and description. (None)"""
        # check for hazards
        while True:
            status = self.dodec.check_cave()
            if 'WUMPUS' in status:
                # wumpus is a loss
                self.human.tell("The heavy weight of a wumpus lands on you, and you are")
                self.human.tell("trapped in it's sucker tipped claws. In seconds you are")
                self.human.tell("shoved into it's huge maw and eaten alive.")
                self.win_loss_draw[1] = 1
            elif 'BATS' in status:
                # bats move randomly and skip to next cave
                self.human.tell("You are grabbed by a giant, screeching bat and flown through")
                self.human.tell("the caves at random.")
                self.dodec.bats()
                continue
            elif 'PIT' in status:
                # pit is a loss
                self.human.tell("You stumble in the dark and fall down a bottomless pit. Well,")
                self.human.tell("okay, it's got a bottom. Give us some room for poetic")
                self.human.tell("license here.")
                self.win_loss_draw[1] = 1
            else:
                # player.tell description
                self.human.tell("You are in a cave with " + status[0])
                # player.tell any nearby hazard warnings
                if 'FLAP' in status:
                    self.human.tell("You hear a strange flapping sound.")
                if 'SMELL' in status:
                    self.human.tell("You smell a foul odor.")
                if 'DRAFT' in status:
                    self.human.tell("You feel a cool draft.")
                result = ''
            break
