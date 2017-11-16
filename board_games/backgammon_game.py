"""
backgammon_game.py

Classes:
Backgammon: A game of Backgammon. (game.Game)
BackgammonBoard: A board for Backgammon. (board.LineBoard)
"""


from __future__ import print_function


import tgames.board as board
import tgames.dice as dice
import tgames.game as game
import tgames.options as options


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

FRAME_HIGH = ['  1 1 1 1 1 1   1 2 2 2 2 2  ', '  3 4 5 6 7 8   9 0 1 2 3 4  ', 
    '+-------------+-------------+']

FRAME_LOW = ['+-------------+-------------+',  '  1 1 1                      ', 
    '  2 1 0 9 8 7   6 5 4 3 2 1  ']


class Backgammon(game.Game):
    """
    A game of Backgammon. (game.Game)

    Overridden Methods:
    set_up
    """

    aliases = {'b': 'bear'}
    categories = ['Board Games', 'Race Games']
    credits = CREDITS
    name = 'Backgammon'

    def check_win(self, piece):
        other_piece = 'XO'['OX'.index(piece)]
        result = 0
        if len(self.board.out[piece].piece) == 15:
            result = self.doubling_die
            if not len(self.board.out[other_piece].piece):
                if other_piece in self.board.bar.piece:
                    result *= 3
                else:
                    result *= 2
        return result 

    def do_bear(self, argument):
        """
        Bear a piece off of the board. (bool)

        Parameters:
        argument: The point or points to bear off from. (str)
        """
        # Get the current player.
        player = self.players[self.player_index]
        piece = self.pieces[player.name]
        # Convert the arguments.
        words = argument.split()
        if words[0].lower() == 'off':
            words = words[1:]
        try:
            points = [int(word) for word in words]
        except ValueError:
            player.tell('Invalid argument to the bear command: {}.'.format(argument))
            return True
        locations = [loc for loc in self.board.cells if piece in self.board.cells[loc].piece]
        # Check for all pieces in the player's home.
        if (piece == 'X' and max(locations) > 5) or (piece == 'O' and min(locations) < 18):
            player.tell('You do not have all of your pieces in your home yet.')
            return True
        elif piece in self.bar.piece:
            player.tell('You still have a piece on the bar.')
            return True
        # Play any legal moves
        for point in points:
            # Check for a valid roll and 
            if not self.board.cells[(point - 1,)].piece:
                player.tell('You do not have a piece on the {} point.')
                continue
            elif point in self.moves:
                self.moves.remove(point)
            elif point < max(self.moves):
                self.moves.remove(max(self.moves))
            else:
                player.tell('There is no valid move for the {} point.')
                continue
            self.board.out[piece] = self.board.cells[(point - 1,)].piece.pop()

    def game_over(self):
        """Check for the end of the game."""
        human_win = self.win_check(self.pieces[self.human.name])
        if human_win:
            self.win_loss_draw[0] = human_win
        bot_win = self.win_check(self.pieces[self.bot.name])
        if bot_win:
            self.win_loss_draw[1] = bot_win
        return max(self.win_loss_draw) >= self.match

    def get_moves(self):
        """Determine the moves from the dice roll. (None)"""
        self.moves = self.dice.values[:]
        if self.moves[0] == self.moves[1]:
            self.moves.extend(self.moves)

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.add_option('o', target = 'human_piece', value = 'O', default = 'X',
            question = 'Would you like to play with the O piece? bool')
        self.option_set.add_option('match', ['m'], int, 1, check = lambda x: x > 0,
            question = 'What should be the winning match score (return for 1)? ')

    def player_turn(self, player):
        # !! need a check for no legal moves left.
        player_piece = self.pieces[player.name]
        player.tell(self.board.get_text(player_piece))
        if not self.moves:
            # !! need to check for doubling.
            self.dice.roll()
            self.dice.sort()
            player.tell('You rolled a {} and a {}.'.format(*self.dice))
            self.get_moves()
        move = player.ask_int_list('What is your move? ', low = 1, high = 24, valid_lens = [1, 2])
        if len(move) == 1:
            possible = []
            for maybe in set(self.moves):
                start = move[0] + maybe
                if self.board.cells[(start,)] and self.board.cells[(start,)][0] == player_piece:
                    possible.append(start)
            if len(possible) == 1:
                start = possible[0]
                end = move[0]
            elif len(possible) > 1:
                player.tell('That move is ambiguous.')
                return True
            else:
                player.tell('There is no legal move to that point.')
                return True
        else:
            start, end = [x - 1 for x in move]
        start_pieces = self.board.cells[(start,)].piece
        end_pieces = self.board.cells[(end,)].piece
        if not (start_pieces and start_pieces[0] == player_piece):
            player.tell('You do not have a piece on that starting square.')
            return True
        elif start - end not in self.moves:
            player.tell('You do not have a die roll matching that move.')
            return True
        elif end_pieces and end_pieces[0] != player_piece and len(end_pieces) > 1:
            player.tell('That end point is blocked.')
            return True
        else:
            self.board.move((start,), (end,))
            self.moves.remove(start - end)
        return self.moves

    def set_up(self):
        """Set up the game. (None)"""
        self.board = BackgammonBoard((24,))
        self.doubling_die = 1
        self.pieces[self.human.name] = self.human_piece
        if self.human_piece == 'X':
            self.pieces[self.bot.name] = 'O'
        else:
            self.pieces[self.bot.name] = 'X'
        self.dice = dice.Pool()
        while self.dice.values[0] == self.dice.values[1]:
            self.dice.roll()
        self.get_moves()


class BackgammonBoard(board.MultiBoard):
    """
    A board for Backgammon. (board.LineBoard)

    Methods:
    get_moves: Get the legal moves for a given roll. (list)
    """

    def __init__(self, dimensions = (24,)):
        """
        Set up the grid of cells. (None)

        Paramters:
        dimensions: The dimensions of the board, in cells. (tuple of int)
        """
        super(BackgammonBoard, self).__init__(dimensions)
        self.bar = board.BoardCell((-1,), [])
        self.out = {'X': board.BoardCell((-2,), []), 'O': board.BoardCell((-3,), [])}
        self.cells.update({(-1,): self.bar, (-2,): self.out['X'], (-3,): self.out['O']})
        self.set_up()

    def board_text(self, locations):
        lines = []
        for row in range(5):
            row_text = '| '
            for bar_check, location in enumerate(locations):
                pieces = len(self.cells[(location,)].piece)
                if pieces > row:
                    if row == 0 and pieces > 5:
                        if pieces > 9:
                            row_text += '{} '.format(pieces % 10)
                        elif pieces > 5:
                            row_text += '{} '.format(pieces)
                    elif row == 1 and pieces > 9:
                        row_text += '1 '
                    else:
                        row_text += '{} '.format(self.cells[(location,)].piece[0])
                else:
                    row_text += '{} '.format(':.'[location % 2])
                if bar_check == 5:
                    row_text += '| '
            lines.append(row_text + '|')
        return lines

    def get_moves(self, piece, rolls, moves = []):
        full_moves = []
        from_cells = [coord for coord in self.cells if piece in self.cells[coord].piece]
        direction = {'X': 1, 'O': -1}[piece]
        for roll in set(rolls):
            sub_rolls = rolls[:]
            sub_rolls.remove(roll)
            if piece in self.bar.piece:
                if piece == 'X':
                    end_coord = (23 - roll,)
                else:
                    end_coord = (roll - 1,)
                end_cell = self.cells[end_coord]
                if piece in end_cell.piece or len(end_cell.piece) < 2:
                    sub_board = self.copy()
                    capture = sub_board.move((-1,), end_coord)
                    if capture:
                        sub_board.bar.piece.append(capture)
                    new_moves = moves + [((-1,), end_coord)]
                    if sub_rolls:
                        full_moves.extend(sub_board.get_moves(piece, sub_rolls, new_moves))
                    else:
                        full_moves.append(new_moves)
            else:
                for coord in from_cells:
                    end_coord = coord + (roll * direction,)
                    if coord < (0,) or end_coord < (0,):
                        continue
                    end_cell = self.cells[end_coord]
                    if piece not in end_cell.piece and len(end_cell.piece) > 1:
                        continue
                    # !! duplicate code, don't like options for refactoring.
                    sub_board = self.copy()
                    capture = sub_board.move(coord, end_coord)
                    if capture:
                        sub_board.bar.piece.append(capture)
                    new_moves = moves + [(coord, end_coord)]
                    if sub_rolls:
                        full_moves.extend(sub_board.get_moves(piece, sub_rolls, new_moves))
                    else:
                        full_moves.append(new_moves)
        return full_moves

    def get_text(self, piece):
        """
        Get the board text from a particular player's perspective. (str)

        Parameters:
        piece: The piece for the player to display. (str)
        """
        frame_high = FRAME_HIGH
        frame_low = FRAME_LOW
        order_high = list(range(12, 24))
        order_low = list(range(11, -1, -1))
        if piece == 'O':
            frame_high = [line[::-1] for line in frame_high]
            frame_low = [line[::-1] for line in frame_low]
            order_high = list(range(0, 12))
            order_low = list(range(23, 11, -1))
        lines = frame_high[:]
        lines.extend(self.board_text(order_high))
        lines.append('|             |             |')
        lines.extend(reversed(self.board_text(order_low)))
        lines.extend(frame_low)
        if self.bar.piece:
            lines.extend(['', 'Bar: {}'.format(''.join(self.bar.piece))])
        return '\n'.join(lines)

    def set_up(self):
        for location, count in ((6, 5), (8, 3), (13, 5), (24, 2)):
            self.cells[(location - 1,)].piece = ['X'] * count
            self.cells[(24 - location,)].piece = ['O'] * count

if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    bg_board = BackgammonBoard()
    print(bg_board.get_text('X'))
    print()
    print(bg_board.get_text('O'))
    print()
    while True:
        print(bg_board.get_text('X'))
        print()
        move = input('Move? ')
        print()
        try:
            start, end = [(int(x) - 1,) for x in move.split()]
        except ValueError:
            break
        capture = bg_board.move(start, end)
        if capture:
            print('Capture:', capture)
    test_moves = bg_board.get_moves('O', [1, 2])