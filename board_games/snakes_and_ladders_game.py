"""
snakes_and_ladders_game.py
"""


import random

from .. import dice
from .. import board
from .. import game
from .. import player
from .. import utility


class SnakeBot(player.Bot):

    def ask(self, prompt):
        if prompt.startswith('\nPress enter'):
            return ''
        elif prompt.startswith('\nWhat symbol'):
            return random.choice('!@#$%^&*<>?')

    def tell(self, *args, **kwargs):
        if not (isinstance(args[0], SnakeBoard) or args[0].startswith('That symbol')):
            super(SnakeBot, self).tell(*args, **kwargs)


class SnakeBoard(board.LineBoard):

    layouts = {'Nepalese': [(9, 8), (10, 23), (16, 4), (17, 69), (20, 32), (24, 7), (27, 41), (28, 50),
        (29, 6), (37, 66), (44, 9), (45, 67), (46, 62), (52, 35), (54, 66), (55, 3), (61, 13), (63, 2),
        (72, 51)],
        'Milton-Bradley': [(10, 10), (1, 38), (4, 14), (9, 31), (16, 6), (21, 42), (28, 84), (36, 44),
        (47, 26), (49, 11), (51, 67), (56, 53), (62, 19), (64, 60), (71, 91), (80, 100), (87, 24), (93, 73),
        (95, 75), (98, 78)]}

    def __init__(self, name = 'Milton-Bradley', exact = 'no', columns = 0, rows = 0, level = ''):
        """
        Set up the board. (None)

        Parameters:
        name: The name of the layout. (str)
        exact: Whether an exact roll is needed for a win. (str)
        columns: The number of columns in the layout. (int)
        rows: The number of rows in the layout. (int)
        """
        self.exact = exact
        self.die = dice.Die()
        if name == 'Random':
            layout = self.random_layout(columns, rows)
        else:
            layout = self.layouts[name]
        self.columns, self.rows = layout[0]
        super(SnakeBoard, self).__init__(self.columns * self.rows, extra_cells = [0])
        self.snakes, self.ladders = {}, {}
        for start, end in layout[1:]:
            if start < end:
                self.ladders[start] = end
                self.cells[start].add_piece('L')
            else:
                self.snakes[start] = end
                self.cells[start].add_piece('S')

    def __str__(self):
        """Human readable text representation. (str)"""
        number_text, piece_text = [''], ['']
        for index in range(1, self.columns * self.rows + 1):
            number_text.append('{:^4}'.format(index))
            piece_text.append('{:^4}'.format(''.join(self.cells[index].contents)))
        lines = []
        for column in range(self.columns - 1, -1, -1):
            #lines.append('')
            row_order = range(self.rows, 0, -1) if column % 2 else range(1, self.rows + 1)
            numbers, pieces = [], []
            for row in row_order:
                n = column * self.rows + row
                numbers.append(number_text[n])
                pieces.append(piece_text[n])
            lines.append(' '.join(pieces))
            lines.append(' '.join(numbers))
        return '\n'.join(lines)

    def roll(self, player, location, piece):
        """
        Roll the dice and move the player. (int)

        The return value is the new location of the player.

        Parameters:
        player: The player being moved. (player.Player)
        player: Where the player is on the board. (int)
        piece: The player's piece symbol. (str)
        """
        self.cells[location].remove_piece(piece)
        roll = self.die.roll()
        player.tell('You rolled a {}.'.format(roll))
        end = location + roll
        if end > self.columns * self.rows:
            if self.exact == 'stop':
                player.tell('{} did not move because they rolled too high.'.format(player.name))
                end = location
            elif self.exact == 'bounce':
                player.tell('{} rolled too high and bounces back.'.format(player.name))
                end = 200 - location - roll
            else:
                end = self.columns * self.rows
        if end != location:
            player.tell('{} moved to square #{}.'.format(player.name, end))
        if end in self.ladders:
            new_end = self.ladders[end]
            player.tell('Square #{} is a ladder up to square #{}.'.format(end, new_end))
            end = new_end
        if end in self.snakes:
            new_end = self.snakes[end]
            player.tell('Square #{} is a snake down to square #{}.'.format(end, new_end))
            end = new_end
        self.cells[end].add_piece(piece)
        if roll == 6 and end != self.columns * self.rows:
            player.tell('{} rolled a 6, so they get to roll again.'.format(player.name))
            end = self.roll(player, end, piece)
        return end


class SnakesAndLadders(game.Game):
    """
    A game of Snakes and Ladders. (game.Game)

    Methods:
    do_roll: Roll and move on the board.

    Overridden Methods:
    game_over
    player_action
    set_up
    """

    aka = ['Chutes and Ladders', 'SnAL']
    categories = ['Board Games']
    name = 'Snakes and Ladders'

    def do_roll(self, arguments):
        """
        Roll and move on the board. (r)
        """
        player = self.players[self.player_index]
        location = self.scores[player.name]
        piece = self.pieces[player.name]
        self.scores[player.name] = self.board.roll(player, location, piece)
        return False

    def game_over(self):
        """Check for the end of the game."""
        # Someone getting to the end finishes the game.
        if self.board.columns * self.board.rows in self.scores.values():
            # Get the overall winner.
            scores = [(score, name) for name, score in self.scores.items()]
            scores.sort(reverse = True)
            self.human.tell('\n{} wins!'.format(scores[0][1]))
            # Figure out the human's win/loss/draw score.
            human_score = self.scores[self.human.name]
            for score, name in scores:
                if score < human_score:
                    self.win_loss_draw[0] += 1
                elif score > human_score:
                    self.win_loss_draw[1] += 1
                elif name != self.human.name:
                    self.win_loss_draw[2] += 1
            # Let the human know where they placed if they didn't win.
            if self.human.name != scores[0][1]:
                rank = utility.number_word(self.win_loss_draw[1] + 1, ordinal = True)
                out_of = utility.number_word(len(self.players))
                self.human.tell('You came in {} out of {} players.'.format(rank, out_of))
            return True
        else:
            return False

    def handle_options(self):
        """Handle the options for this play of the game. (None)"""
        super(SnakesAndLadders, self).handle_options()
        taken_names = [self.human.name]
        for bot in range(self.n_bots):
            self.players.append(SnakeBot(taken_names = taken_names))
            taken_names.append(self.players[-1].name)

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        The return value is a flag for the player's turn continuing.

        Parameters:
        player: The player whose turn it is. (Player)
        """
        player.tell('')
        player.tell(self.board)
        command = player.ask('\nPress enter to roll: ')
        if not command:
            return self.do_roll('')
        else:
            return self.handle_cmd(command)

    def set_options(self):
        """Define the options for the game."""
        self.option_set.add_option('bots', ['b'], int, 3, valid = range(1, 12), target = 'n_bots',
            question = 'How many bots should there be in the game (1-11, return for 3)? ')
        self.option_set.add_option('exact', ['x'], str.lower, 'no', valid = ['no', 'stop', 'bounce'],
            question = 'What happens if you roll over 100 (stop, bounce, or return for no)? ')

    def set_up(self):
        """Set up the game."""
        # Get the symbols for the players' pieces.
        if not hasattr(self, 'pieces'):
            self.pieces = {}
            taken_pieces = set('SL')
            for player in self.players:
                while True:
                    # As for the symbol.
                    piece = player.ask('\nWhat symbol do you want to be on the board? ')
                    # All symbols must be visible and unique.
                    if piece in taken_pieces:
                        player.tell('That symbol is already taken, please choose another.')
                    elif not piece:
                        player.tell('You are not allowed to be invisible.')
                    # Store the symbol and go to the next player.
                    else:
                        self.pieces[player.name] = piece[0]
                        taken_pieces.add(piece[0])
                        break
        # Set up the board and player tracking.
        self.board = SnakeBoard(exact = self.exact)
        for player in self.players:
            self.board.cells[0].add_piece(self.pieces[player.name])
