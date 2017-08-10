"""
wumpus_game.py

A game of Hunt the Wumpus.

This is at least the third time I have used the Cave and Dodecahedron objects
to create a Hunt the Wumpus game.

Constants:
ADJACENT: Adjacent points on a dodecahedron. (list of tuple of int)
DESCRIPTIONS: The room descriptions. (list of str)
HELP_TEXT: Text describing the game. (str)

Classes:
Cave: One cave in a cave complex. (object)
Dodecahedron: A cave complex arranged as a dodecahedron. (object)
Wumpus: A game of Hunt the Wumpus. (game.Game)
"""


import random

import tgames.game as game


# Adjacent points on a dodecahedron.
ADJACENT = [(4, 5, 1), (0, 6, 2), (1, 7, 3), (2, 8, 4), (3, 9, 0),
    (0, 14, 10), (1, 10, 11), (2, 11, 12), (3, 12, 13), (4, 13, 14),
    (5, 15, 6), (6, 16, 7), (7, 17, 8), (8, 18, 9), (9, 19, 5),
    (10, 19, 16), (11, 15, 17), (12, 16, 18), (13, 17, 19), (14, 18, 15)]

# The room descriptions.
# 0 is where the wumpus starts, and 1:4 are blank because they are pits or bats.
DESCRIPTIONS = ['wumpus dung in the corner', '', '', '', '', 'ants crawling all over everything', 
    'lots of cobwebs', 'a dart board on the wall', 'a spooky echo', 'remains of a fire', 
    'rude graffiti on the wall', 'a battered helmet on the floor', 'a pile of junk in the corner', 
    'a family of lizards hiding in cracks in the wall', 'a strange mist in the air', 
    'several notches marked on the wall', 'an obelisk carved out of a stalagmite', 'a tall roof', 
    'a skull on the floor', 'a big red X marked on the floor']

# Text describing the game.
HELP_TEXT = """
Hunt the Wumpus

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
   HELP: Read these fascinating, well written instructions again.
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
        
    def __eq__(self, other):
        """
        Compare caves by id
        
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
        """
        Set up the cave complex and its initial state.
        """
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
        
    def bats(self):
        """
        Move the player to a random cave. (None)
        """
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
        new_wumpus = random.choice([self.current] + self.current.adjacent)
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
        
        The return value is 1 for hitting the wumpus, -1 for hitting yourself,
        and 0 for not hitting anything.
        
        Parameter:
        direction: The (L/R/B) directions to shoot the arrow in (str)
        """
        # initialize the arrow location
        target = self.current
        shooter = self.previous
        # shoot through up to three caves
        for char in direction[:3]:
            # move the arrow
            shooter, target = target, self.next_cave(shooter, target, char)
            # check for a hit
            if target.wumpus:
                return 1
            if target.id == self.current.id:
                return -1
            # indicate a miss (for that cave at least)
            print('Whiff!')
        return 0


class Wumpus(game.Game):
    """
    A game of Hunt the Wumpus.

    Attributes:
    arrows: The number of crooked arrows left. (int)
    dodec: The cave system. (Dodecahedron)

    Methods:
    shoot: Fire a crooked arrow. (None)
    status_check: Check the room for hazards and description. (None)

    Overridden Methods:
    game_over
    player_turn
    set_up
    """

    aka = ['Wumpus']
    cateories = ['Adventure Games']
    name = 'Hunt the Wumpus'

    def game_over(self):
        """Check for the game being over. (None)"""
        # Game over is flagged elsewhere by changing win/loss/draw.
        if self.win_loss_draw[1]:
            print('The wumpus wins. :(')
        elif self.win_loss_draw[0]:
            print('You win!')
        elif self.win_loss_draw[2]:
            print("Alright, we'll call it a draw.")
        else:
            # Game still on.
            return False
        # Record score and end game.
        self.scores[self.human.name] = self.turns
        return True

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        move = player.ask('What is your move? ').strip().lower()
        if move in ('b', 'back'):
            self.dodec.move('B')
        elif move in ('c', 'climb'):
            if self.dodec.current == self.dodec.start:
                print('You climb back out of the bowels of the earth.')
                self.win_loss_draw[2] = 1
            else:
                print('There is no way to climb out of here.')
        elif move in ('l', 'left'):
            self.dodec.move('L')
        elif move in ('q', 'quit'):
            self.win_loss_draw[1] = 1
        elif move in ('r', 'right'):
            self.dodec.move('R')
        elif move.split()[0] in ('s', 'shoot'):
            self.shoot(move.split()[1])
        if not sum(self.win_loss_draw):
            self.status_check()

    def set_up(self):
        """Set up the caves and the tracking variables. (None)"""
        self.dodec = Dodecahedron()
        self.arrows = 5
        self.status_check()
        
    def shoot(self, arg):
        """
        Fire a crooked arrow. (None)

        Parameters:
        arg: The directions to shoot the arrow in. (str)
        """
        # make sure there are arrows
        if self.arrows:
            # update arrows
            self.arrows -= 1
            # take the shot
            hit = self.dodec.shoot(arg.upper())
            # print the results
            if not hit:
                # miss means wumpus may move
                print('You hear the arrow break uselessly against a wall.')
                print('You hear a grumbling roar and a strange suck-pop sound.')
                print('You have {} crooked arrows left.'.format(self.arrows))
                self.dodec.move_wumpus()
            elif hit < 0:
                # shooting yourself is a loss
                print('Arrgh! You shot yourself in the back')
                self.win_loss_draw[1] = 1
            else:
                # shooting the wumpus is a win
                print('You hear the horrible scream of a dieing wumpus!')
                self.win_loss_draw[0] = 1
        else:
            print("You don't have any arrows left to shoot.")
    
    def status_check(self):
        """Check the room for hazards and description. (None)"""
        # check for hazards
        while True:
            status = self.dodec.check_cave()
            if 'WUMPUS' in status:
                # wumpus is a loss
                print("The heavy weight of a wumpus lands on you, and you are")
                print("trapped in it's sucker tipped claws. In seconds you are")
                print("shoved into it's huge maw and eaten alive.")
                self.win_loss_draw[1] = 1
            elif 'BATS' in status:
                # bats move randomly and skip to next cave
                print("You are grabbed by a giant, screeching bat and flown through")
                print("the caves at random.")
                self.dodec.bats()
                continue
            elif 'PIT' in status:
                # pit is a loss
                print("You stumble in the dark and fall down a bottomless pit. Well,")
                print("okay, it's got a bottom. Give us some room for poetic")
                print("license here.")
                self.win_loss_draw[1] = 1
            else:
                # print description
                print("You are in a cave with " + status[0])
                # print any nearby hazard warnings
                if 'FLAP' in status:
                    print("You hear a strange flapping sound.")
                if 'SMELL' in status:
                    print("You smell a foul odor.")
                if 'DRAFT' in status:
                    print("You feel a cool draft.")
                result = ''
            break


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    wumpus = Wumpus(player.Player(name), '')
    wumpus.play()