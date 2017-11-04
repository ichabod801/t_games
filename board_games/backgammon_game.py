"""
backgammon_game.py

Classes:
Backgammon: A game of Backgammon. (game.Game)
BackgammonBoard: A board for Backgammon. (board.LineBoard)
"""


import tgames.board as board
import tgames.game as game


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

FRAME_HIGH = [' 1 1 1 1 1 1   1 2 2 2 2 2 ', ' 3 4 5 6 7 8   9 0 1 2 3 4 ', '+-------------------------+']

FRAME_LOW = ['+-------------------------+',  ' 1 1 1                     ', ' 2 1 0 9 8 7   6 5 4 3 2 1 ']


class Backgammon(game.Game):
    """
    A game of Backgammon. (game.Game)

    Overridden Methods:
    set_up
    """

    categories = ['Board Games', 'Race Games']
    credits = CREDITS
    name = 'Backgammon'

    def set_up(self):
        """Set up the game. (None)"""
        self.board = BackgammonBoard((24,))
        self.doubling_die = 1


class BackgammonBoard(board.MultiBoard):
    """
    A board for Backgammon. (board.LineBoard)

    Methods:
    get_moves: Get the legal moves for a given roll. (list)
    """

    def __init__(self, dimensions):
        """
        Set up the grid of cells. (None)

        Paramters:
        dimensions: The dimensions of the board, in cells. (tuple of int)
        """
        super(DimBoard, self).__init__(dimensions)
        self.bar = BoardCell(-1, [])
        self.set_up()

    def get_moves(self, piece, roll):
        pass

    def get_text(self, piece):
        """
        Get the board text from a particular player's perspective. (str)

        Parameters:
        piece: The piece for the player to display. (str)
        """
        piece_text = '{} '.format(piece)
        frame_high = FRAME_HIGH
        frame_low = FRAME_LOW
        order_high = list(range(12, 24))
        order_low = list(range(11, -1, -1))
        if piece == 'O':
            frame_high = [line[::-1] for line in frame_high]
            frame_low = [line[::-1] for line in frame_low]
            order_high.reverse()
            order_low.reverse()
        lines = frame_high[:]
        lines.extend(piece_text(order_high, piece_text))
        lines.append('|            H            |')
        lines.extend(piece_text(order_low, piece_text))
        lines.extend(frame_low)
        if self.bar.piece:
            lines.extend(['', 'Bar: {}'.format(''.join(self.bar.piece))])
        return '\n'.join(lines)

    def piece_text(self, locations, piece_text):
        lines = []
        for row in range(5);
            row_text = '| '
            for bar_check, location in enumerate(locations):
                pieces = len(self.cells[location].piece)
                if pieces > row:
                    if row == 0 and pieces > 5:
                        if pieces > 9:
                            row_text += '1 '
                        elif pieces > 5:
                            row_text += ' {}'.format(pieces)
                    elif row == 1 and pieces > 9:
                        row_text += ' {}'.format(pieces % 10)
                    else:
                        row_text += piece_text
                else:
                    row_text += '{} '.format('|:'[location % 2])
                if bar_check == 5:
                    row_text += 'H '
            lines.append(row_text + '|')
        return lines

    def set_up(self):
        for location, count in ((13, 6), (8, 3), (13, 5), (24, 2)):
            self.cells[location - 1].piece = ['X'] * count
            self.cells[24 - location].piece = ['O'] * count