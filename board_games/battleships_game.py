"""
battleships_game.py

A game of Battleships.

!! Make the coordiates an object, for easier handling. (should be in board.py)
!! Have a 3D version named Yamato. 5x5x5, longest ship would be 4.
"""


import random
import re

import tgames.game as game
import tgames.player as player


LAYOUTS = {'Bradley': {'Carrier': (5, 1), 'Battleship': (4, 1), 'Cruiser': (3, 1), 
        'Destroyer': (2, 1), 'Submarine': (3, 1)},
    'Bednar': {'Carrier': (5, 1), 'Battleship': (4, 1), 'Cruiser': (3, 1),
        'Destroyer': (2, 2), 'Submarine': (1, 2)},
    'Ichabod': {'Carrier': (5, 1), 'Battleship': (4, 2), 'Cruiser': (3, 3),
        'Destroyer': (2, 4), 'Submarine': (1, 1)},
    'Wikipedia': {'Carrier': (6, 1), 'Battleship': (4, 2), 'Cruiser': (3, 3),
        'Destroyer': (2, 4), 'Submarine': (1, 0)}}

SQUARE_RE = re.compile(r'[ABCDEFGHIJ]\d')


class Battleships(game.Game):
    """
    A game of Battleships. (object)
    """

    aka = ['Battleship', 'Sea Battle', 'Broadsides']
    categories = ['Board Games', 'Displace Games']
    name = 'Battleships'

    def handle_options(self):
        self.bot = BattleBot([self.human.name])
        self.players = [self.human, self.bot]
        self.layout = 'Bradley'

    def game_over(self):
        if not (self.boards[self.bot.name].fleet or self.boards[self.human.name].fleet):
            self.human.tell("It's a draw! You destroyed each other's fleets at the same time.")
            self.win_loss_draw[2] = 1
        elif not self.boards[self.bot.name].fleet:
            self.human.tell("You sank {}'s fleet and won!".format(self.bot.name))
            self.win_loss_draw[0] = 1
        elif not self.boards[self.human.name].fleet:
            self.human.tell("{} sank your fleet. You lose.".format(self.bot.name))
            self.win_loss_draw[1] = 1
        else:
            return False
        return True

    def player_turn(self, player):
        while True:
            human_shot = self.human.ask('Where do you want to shoot? ').strip()[:2].upper()
            if SQUARE_RE.match(human_shot):
                break
            self.human.tell('That was an invalid shot.')
        bot_shot = self.bot.ask('Where do you want to shoot? ')
        self.boards[self.bot.name].fire(human_shot, self.human)
        self.boards[self.human.name].fire(bot_shot, self.bot)
        self.human.tell(self.boards[self.bot.name].show(to = 'foe'))
        self.human.tell(self.boards[self.human.name].show())

    def set_up(self):
        self.boards = {self.bot.name: SeaBoard(self.bot, self.layout)}
        self.boards[self.human.name] = SeaBoard(self.human, self.layout)


class BattleBot(player.Bot):
    """
    A bot for playing Battleships. (Bot)
    """

    def __init__(self, taken_names):
        super(BattleBot, self).__init__(taken_names)
        # just track places not to shoot. Why doesn't matter.
        self.misses = set()
        self.hits = set()
        self.adjacents = set()
        self.targets = []
        self.target_ship = []
        self.last_shot = ''

    def add_adjacents(self):
        for square in self.target_ship:
            for adjacent in self.game.boards[self.name].adjacent_squares(square):
                if adjacent not in self.target_ship:
                    self.adjacents.add(adjacent)

    def ask(self, prompt):
        if prompt.startswith('\nPlace'):
            length = int(prompt[-3])
            return self.place_ship(length)
        elif prompt.startswith('Where'):
            return self.fire()

    def fire(self):
        if not self.targets:
            while True:
                self.last_shot = random.choice(SeaBoard.letters) + random.choice(SeaBoard.numbers)
                if self.last_shot in self.misses:
                    continue
                elif self.last_shot in self.hits:
                    continue
                elif self.last_shot in self.adjacents:
                    continue
                break
        else:
            self.last_shot = random.choice(self.targets)
            self.targets.remove(self.last_shot)
        return self.last_shot

    def place_ship(self, length):
        start = (random.randrange(10), random.randrange(10))
        if length == 1:
            return chr(65 + start[0]) + str(start[1])
        options = []
        text = '{}{} to {}{}'
        if start[0] + length - 1 < 10:
            end = (start[0] + length - 1, start[1])
            options.append(text.format(chr(65 + start[0]), start[1], chr(65 + end[0]), end[1]))
        if start[1] + length - 1 < 10:
            end = (start[0], start[1] + length - 1)
            options.append(text.format(chr(65 + start[0]), start[1], chr(65 + end[0]), end[1]))
        if start[0] - length + 1 > -1:
            end = (start[0] - length + 1, start[1])
            options.append(text.format(chr(65 + start[0]), start[1], chr(65 + end[0]), end[1]))
        if start[1] - length + 1 > -1:
            end = (start[0], start[1] - length + 1)
            options.append(text.format(chr(65 + start[0]), start[1], chr(65 + end[0]), end[1]))
        return random.choice(options)

    def retarget(self):
        adjacents = self.game.boards[self.name].adjacent_squares(self.last_shot)
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
        else:
            self.targets = adjacents
            self.target_ship = [self.last_shot]

    def tell(self, text):
        if 'hit' in text:
            self.hits.add(self.last_shot)
            self.retarget()
        elif 'miss' in text:
            self.misses.add(self.last_shot)
        elif 'sank a' in text:
            self.add_adjacents()
            self.target_ship = []
            self.targets = []


class SeaBoard(object):
    """
    A board in a game of Battleships. (object)
    """

    letters = 'ABCDEFGHIJ'
    numbers = '0123456789'

    def __init__(self, player, layout = 'Bradley'):
        self.player = player
        self.layout = LAYOUTS[layout]
        self.misses = set()
        self.hits = set()
        self.place_ships()

    def adjacent_squares(self, square):
        coordinates = (self.letters.index(square[0]), int(square[1]))
        adjacent = []
        if coordinates[0] > 0:
            adjacent.append(self.letters[coordinates[0] - 1] + str(coordinates[1]))
        if coordinates[0] < 9:
            adjacent.append(self.letters[coordinates[0] + 1] + str(coordinates[1]))
        if coordinates[1] > 0:
            adjacent.append(square[0] + str(coordinates[1] - 1))
        if coordinates[1] < 9:
            adjacent.append(square[0] + str(coordinates[1] + 1))
        return adjacent

    def fire(self, square, foe):
        for ship, squares in self.fleet:
            if square in squares:
                self.hits.add(square)
                foe.tell('You hit.')
                squares.remove(square)
                if not squares:
                    self.player.tell('Your {} has been sunk.'.format(ship))
                    foe.tell('You sank a {}.'.format(ship))
                    fleet_squares = sum([squares for ship, squares in self.fleet], [])
                    if not fleet_squares:
                        self.fleet = []
                break
        else:
            self.misses.add(square)
            foe.tell('You missed.')

    def make_ship(self, start, end):
        start, end = sorted([start, end])
        squares = []
        if start[0] == end[0]:
            start_index = int(start[1])
            end_index = int(end[1])
            for number in range(start_index, end_index + 1):
                squares.append(start[0] + str(number))
        elif start[1] == end[1]:
            start_index = self.letters.index(start[0])
            end_index = self.letters.index(end[0])
            for letter in self.letters[start_index:end_index + 1]:
                squares.append(letter + start[1])
        return squares

    def place_ships(self):
        # Get the ships sorted by size.
        ships = sorted(self.layout.items(), key = lambda ship: ship[1][0], reverse = True)
        invalid_squares = set()
        self.fleet = []
        for ship, (size, count) in ships:
            for ship_index in range(count):
                self.player.tell(self.show())
                while True:
                    message = '\nPlace {} #{} of {}, length {}: '
                    move = self.player.ask(message.format(ship.lower(), ship_index + 1, count, size))
                    squares = SQUARE_RE.findall(move.upper())
                    if size == 1 and len(squares) != 1:
                        self.player.tell('You must enter one square for a {}.'.format(ship.lower()))
                        continue
                    elif size > 1 and len(squares) != 2:
                        self.player.tell('Please enter a start and end square.')
                        continue
                    if size == 1:
                        ship_squares = [squares[0]]
                    else:
                        ship_squares = self.make_ship(*squares)
                    if not ship_squares:
                        self.player.tell('Ships must be horizontal or vertical.')
                        continue
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
        lines = ['\n 0123456789']
        for letter in reversed(self.letters):
            line = letter
            for number in range(10):
                square = letter + str(number)
                if square in self.hits:
                    line += 'X'
                elif square in self.misses:
                    line += '/'
                elif to == 'friend' and any([square in squares for ship, squares in self.fleet]):
                    line += 'O'
                else:
                    line += '.'
            line += letter
            lines.append(line)
        lines.append(' 0123456789')
        return '\n'.join(lines)


def test():
    board = SeaBoard()
    print('B3 to B7', board.make_ship('B3', 'B7'))
    print('C5 to F5', board.make_ship('C5', 'F5'))
    print('B3 to F5', board.make_ship('B3', 'F5'))
    print('adj E5', board.adjacent_squares('E5'))
    print('adj A5', board.adjacent_squares('A5'))
    print('adj J5', board.adjacent_squares('J5'))
    print('adj E0', board.adjacent_squares('E0'))
    print('adj E9', board.adjacent_squares('E9'))
    print('adj A0', board.adjacent_squares('A0'))
    craig = BattleBot('Craig')
    board = SeaBoard(craig, layout = 'Ichabod')
    board.place_ships()
    print(board.show())
    sarah = player.Player('Sarah')
    for shot in range(30):
        square = random.choice(board.letters) + random.choice(board.numbers)
        board.fire(square, sarah)
    print(board.show())
    print(board.show(to = 'foe'))

if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    game = Battleships(player.Player(name), '')
    game.play()