"""
battleships_test.py

Unit testing of t_games/board_games/battleships_game.py

Classes:
BotTest: Tests of Battleships bots. (unittest.TestCase)
GameOverTest: Tests of Battleships.game_over. (unittest.TestCase)
SeaBoardAdjTest: Test of adjacent squares on a Battleships' board. (TestCase)
SeaBoardFireTest: Test of firing on a Battleships' board. (unittest.TestCase)
SeaBoardMakeShipTest: Test getting ship squares from end points. (TestCase)
SeaBoardPlaceRandomTest: Test generating a random ship. (unittest.TestCase)
SeaBoardPlaceShipsTest: Test placing ships on the board. (unittest.TestCase)
SeaBoardTextTest: Tests of text versions of a Battleships' board. (TestCase)
"""


import itertools
import unittest

from ..board_games import battleships_game as battleships
from . import unitility


BOARD_LINES = ['', ' 0123456789', 'JOXXOO./...J', 'I//...X....I', 'H..../X.../H', 'G.../.X../.G',
    'F../..X./O.F', 'E./..../.O.E', 'D/OOO./..O.D', 'C..../..../C', 'B.../.OO./.B', 'A../..../..A',
     ' 0123456789']


BotTest = unitility.bot_test(battleships.Battleships, [battleships.BattleBot, battleships.SmarterBot], 10,
    [2])


class GameOverTest(unittest.TestCase):
    """Tests of Battleships.game_over. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['r'] * 5)
        self.game = battleships.Battleships(self.bot, 'none')
        self.game.set_up()
        self.game.win_loss_draw = [0, 0, 0]
        self.game.scores = {player.name: 0 for player in self.game.players}

    def testContinueReturn(self):
        """Test the return value from an unfinished game."""
        self.assertFalse(self.game.game_over())

    def testDrawMessage(self):
        """Test the message displayed for a draw."""
        self.game.boards[self.bot.name].fleet = []
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        check = "\nIt's a draw! You destroyed each other's fleets at the same time.\n"
        self.assertEqual(check, self.bot.info[-1])

    def testDrawResults(self):
        """Test the results after a draw."""
        self.game.boards[self.bot.name].fleet = []
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        self.assertEqual([0, 0, 1], self.game.win_loss_draw)

    def testDrawReturn(self):
        """Test the return value from for a draw."""
        self.game.boards[self.bot.name].fleet = []
        self.game.boards[self.game.bot.name].fleet = []
        self.assertTrue(self.game.game_over())

    def testLossMessage(self):
        """Test the messages displayed for a loss."""
        self.game.boards[self.bot.name].fleet = []
        self.game.game_over()
        check = ["\n{} sank your fleet. You lose.\n".format(self.game.bot.name)]
        check.append('{} had 17 squares of ships left.\n'.format(self.game.bot.name))
        self.assertEqual(check, self.bot.info[-2:])

    def testLossResults(self):
        """Test the results after a loss."""
        self.game.boards[self.bot.name].fleet = []
        self.game.game_over()
        self.assertEqual([0, 1, 0], self.game.win_loss_draw)

    def testLossReturn(self):
        """Test the return value from a loss."""
        self.game.boards[self.bot.name].fleet = []
        self.game.game_over()
        self.assertTrue(self.game.game_over())

    def testLossScore(self):
        """Test the score a loss."""
        self.game.boards[self.bot.name].fleet = []
        self.game.game_over()
        self.assertEqual(-17, self.game.scores[self.bot.name])

    def testWinMessage(self):
        """Test the messages displayed for a win."""
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        check = ["\nYou sank {}'s fleet and won!\n".format(self.game.bot.name)]
        check.append('You have 17 squares of ships left.\n')
        self.assertEqual(check, self.bot.info[-2:])

    def testWinResults(self):
        """Test the results after a win."""
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        self.assertEqual([1, 0, 0], self.game.win_loss_draw)

    def testWinReturn(self):
        """Test the return value from a win."""
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        self.assertTrue(self.game.game_over())

    def testWinScore(self):
        """Test the score a win."""
        self.game.boards[self.game.bot.name].fleet = []
        self.game.game_over()
        self.assertEqual(17, self.game.scores[self.bot.name])


class SeaBoardAdjTest(unittest.TestCase):
    """Test of adjacent squares on a Battleships' board. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['r'] * 5)
        self.board = battleships.SeaBoard(self.bot)

    def testBottom(self):
        """Test adjacent squares of a square on the bottom."""
        self.assertEqual(['B1', 'A0', 'A2'], self.board.adjacent_squares('A1'))

    def testBottomLeft(self):
        """Test adjacent squares of a square on the bottom left."""
        self.assertEqual(['B0', 'A1'], self.board.adjacent_squares('A0'))

    def testLeft(self):
        """Test adjacent squares of a square on the left."""
        self.assertEqual(['D0', 'F0', 'E1'], self.board.adjacent_squares('E0'))

    def testLeftTop(self):
        """Test adjacent squares of a square on the left top."""
        self.assertEqual(['I0', 'J1'], self.board.adjacent_squares('J0'))

    def testMiddle(self):
        """Test adjacent squares of a square in the middle."""
        self.assertEqual(['B4', 'D4', 'C3', 'C5'], self.board.adjacent_squares('C4'))

    def testRight(self):
        """Test adjacent squares of a square on the right."""
        self.assertEqual(['F9', 'H9', 'G8'], self.board.adjacent_squares('G9'))

    def testRightBottom(self):
        """Test adjacent squares of a square on the right bottom."""
        self.assertEqual(['I0', 'J1'], self.board.adjacent_squares('J0'))

    def testTop(self):
        """Test adjacent squares of a square on the top."""
        self.assertEqual(['I5', 'J4', 'J6'], self.board.adjacent_squares('J5'))

    def testTopRight(self):
        """Test adjacent squares of a square on the top right."""
        self.assertEqual(['I9', 'J8'], self.board.adjacent_squares('J9'))


class SeaBoardFireTest(unittest.TestCase):
    """Test of firing on a Battleships' board. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['J0 J4', 'H0 H3', 'F0 F2', 'D0 D2', 'B0 B1'])
        self.board = battleships.SeaBoard(self.bot)
        self.foe = unitility.AutoBot()

    def testHitHit(self):
        """Test a basic hit getting recorded."""
        self.board.fire('J0', self.foe)
        self.assertIn('J0', self.board.hits)

    def testHitMessage(self):
        """Test notification of a basic hit."""
        self.board.fire('H1', self.foe)
        self.assertEqual(['You hit.\n'], self.foe.info)

    def testHitRemoval(self):
        """Test a basic hit being marked on the ship."""
        self.board.fire('F2', self.foe)
        self.assertNotIn('F2', self.board.fleet[2][1])

    def testMissMessage(self):
        """Test notification of a basic miss."""
        self.board.fire('C4', self.foe)
        self.assertEqual(['You missed.\n'], self.foe.info)

    def testMissMiss(self):
        """Test a basic miss being recorded."""
        self.board.fire('J9', self.foe)
        self.assertEqual({'J9'}, self.board.misses)

    def testSinkFleet(self):
        """Test updating a fleet when all ships are sunk."""
        for square in 'J0 J1 J2 J3 J4 H0 H1 H2 H3 F0 F1 F2 D0 D1 D2 B0 B1'.split():
            self.board.fire(square, self.foe)
        self.assertEqual([], self.board.fleet)

    def testSinkMessageFoe(self):
        """Test notifying the attacker of a sunk ship."""
        self.board.fire('B0', self.foe)
        self.board.fire('B1', self.foe)
        self.assertEqual(['You hit.\n', 'You hit.\n', 'You sank a destroyer.\n'], self.foe.info)

    def testSinkMessagePlayer(self):
        """Test notifying the owner of a sunk ship."""
        self.board.fire('D0', self.foe)
        self.board.fire('D1', self.foe)
        self.board.fire('D2', self.foe)
        self.assertEqual(['Your cruiser has been sunk.\n'], self.bot.info[5:])


class SeaBoardMakeShipTest(unittest.TestCase):
    """Test getting the ship squares from the end points. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['J0 J4', 'H0 H3', 'F0 F2', 'D0 D2', 'B0 B1'])
        self.board = battleships.SeaBoard(self.bot)

    def testDown(self):
        """Test making a ship going down."""
        self.assertEqual(['H0', 'H1', 'H2', 'H3', 'H4', 'H5'], self.board.make_ship('H5', 'H0'))

    def testLeft(self):
        """Test making a ship going to the left."""
        self.assertEqual(['E5', 'E6', 'E7', 'E8', 'E9'], self.board.make_ship('E9', 'E5'))

    def testNegative(self):
        """Test failing to make a ship with a negative slope."""
        self.assertEqual([], self.board.make_ship('D6', 'A3'))

    def testPositive(self):
        """Test failing to make a ship with a positive slope."""
        self.assertEqual([], self.board.make_ship('B3', 'F7'))

    def testRight(self):
        """Test making a ship going to the right."""
        self.assertEqual(['D6', 'D7', 'D8', 'D9'], self.board.make_ship('D6', 'D9'))

    def testUp(self):
        """Test maing a ship going up."""
        self.assertEqual(['A7', 'B7', 'C7'], self.board.make_ship('A7', 'C7'))


class SeaBoardPlaceRandomTest(unittest.TestCase):
    """Test generating a random ship. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['J0 J4', 'H0 H3', 'F0 F2', 'D0 D2', 'B0 B1'])
        self.board = battleships.SeaBoard(self.bot)
        self.invalid_squares = [''.join(chars) for chars in itertools.product('ABCDEDFGHIJ', '0123456789')]

    def testHorizontalFive(self):
        """Test generating a random horizontal five space ship."""
        for square in 'I7 I6 I5 I4 I3'.split():
            self.invalid_squares.remove(square)
        self.assertEqual(('I3', 'I7'), self.board.place_random(5, self.invalid_squares))

    def testHorizontalThree(self):
        """Test generating a random horizontal three space ship."""
        for square in 'I7 I6 I5 I4 I3'.split():
            self.invalid_squares.remove(square)
            check = [('I5', 'I7'), ('I4', 'I6'), ('I3', 'I5')]
        self.assertIn(self.board.place_random(3, self.invalid_squares), check)

    def testVerticalFive(self):
        """Test generating a random horizontal five space ship."""
        for square in 'F0 F1 F2 F3 F4'.split():
            self.invalid_squares.remove(square)
        self.assertEqual(('F0', 'F4'), self.board.place_random(5, self.invalid_squares))

    def testVerticalThree(self):
        """Test generating a random vertical three space ship."""
        for square in 'B4 B5 B6 B7 B8'.split():
            self.invalid_squares.remove(square)
            check = [('B4', 'B6'), ('B5', 'B7'), ('B6', 'B8')]
        self.assertIn(self.board.place_random(3, self.invalid_squares), check)


class SeaBoardPlaceShipsTest(unittest.TestCase):
    """Test placing ships on the board. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()

    def testCollisionCross(self):
        """Test the error from a ship crossing another ship."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'e6 c6', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(['That ship is adjacent to or overlaps another ship.\n'], self.bot.errors)

    def testCollisionEnd(self):
        """Test the error from a ship touching the end of another ship."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'g2 g0', 'e6 e4', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(['That ship is adjacent to or overlaps another ship.\n'], self.bot.errors)

    def testCollisonSide(self):
        """Test the error from a ship touching the side of another ship."""
        self.bot.replies = ['i6 i2', 'h4 e4', 'g6 g3', 'e6 e4', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(['That ship is adjacent to or overlaps another ship.\n'], self.bot.errors)

    def testDiagonal(self):
        """Test the error from entering a diagonal ship."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 c4', 'e6 e4', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(['Ships must be horizontal or vertical.\n'], self.bot.errors)

    def testHorizontalFiveFleet(self):
        """Test placing a horizontal five square ship in the fleet."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(('Carrier', ['I2', 'I3', 'I4', 'I5', 'I6']), board.fleet[0])

    def testHorizontalFourFleet(self):
        """Test placing a horizontal four square ship in the fleet."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(('Battleship', ['G3', 'G4', 'G5', 'G6']), board.fleet[1])

    def testHorizontalThreeFleet(self):
        """Test placing a horizontal three square ship in the fleet."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(('Submarine', ['E4', 'E5', 'E6']), board.fleet[2])

    def testHorizontalTwoFleet(self):
        """Test placing a horizontal two square ship in the fleet."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(('Destroyer', ['A7', 'A8']), board.fleet[4])

    def testInvalidFirstSquare(self):
        """Test the error from entering an invalid start square."""
        self.bot.replies = ['k1 g1', 'A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(['Please enter a start and end square.\n'], self.bot.errors)

    def testInvalidLength(self):
        """Test the error from entering a ship of the wrong size."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'c4 c1', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(['Cruisers must be 3 squares long.\n'], self.bot.errors)

    def testInvalidSecondSquare(self):
        """Test the error from entering an invalid end square."""
        self.bot.replies = ['A1 ea', 'A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(['Please enter a start and end square.\n'], self.bot.errors)

    def testOneError(self):
        """Test the error from giving two squares for a one square ship."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'c4 c3', 'd8 d9', 'a8 a9', 'a8', 'f8']
        board = battleships.SeaBoard(self.bot, inventory_name = 'bednar')
        self.assertEqual(['You must enter one square for a submarine.\n'], self.bot.errors)

    def testNoCollisionCorner(self):
        """Test no error when ships touch at the corner."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'j8 j9']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual([], self.bot.errors)

    def testOneFleet(self):
        """Test placing a horizontal one square ship in the fleet."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'c4 c3', 'd8 d9', 'a8', 'f8']
        board = battleships.SeaBoard(self.bot, inventory_name = 'bednar')
        self.assertEqual(('Submarine', ['A8']), board.fleet[5])

    def testTwoError(self):
        """Test the error from giving one square for a three square ship."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(['Please enter a start and end square.\n'], self.bot.errors)

    def testVerticalFiveFleet(self):
        """Test placing a vertical five square ship in the fleet."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(('Carrier', ['A1', 'B1', 'C1', 'D1', 'E1']), board.fleet[0])

    def testVerticalFourFleet(self):
        """Test placing a vertical four square ship in the fleet."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(('Battleship', ['D3', 'E3', 'F3', 'G3']), board.fleet[1])

    def testVerticalThreeFleet(self):
        """Test placing a vertical three square ship in the fleet."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(('Cruiser', ['G7', 'H7', 'I7']), board.fleet[3])

    def testVerticalTwoFleet(self):
        """Test placing a vertical two square ship in the fleet."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(('Destroyer', ['I9', 'J9']), board.fleet[4])


class SeaBoardTextTest(unittest.TestCase):
    """Tests of text versions of a Battleships' board. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['j0 j4', 'i5 f5', 'd1 d3', 'f8 d8', 'b5 b6'])
        self.bot.name = 'Ramius'
        self.board = battleships.SeaBoard(self.bot)

    def testRepr(self):
        """Test the computer readable representaiton of a starting SeaBoard."""
        self.assertEqual('<SeaBoard for <AutoBot Ramius> with 0 of 17 hits>', repr(self.board))

    def testReprHit(self):
        """Test the computer readable representaiton of a SeaBoard with some hits."""
        # Hit a ship but don't sink it.
        ship, squares = self.board.fleet[0]
        for square in squares[:-1]:
            self.board.fire(square, unitility.AutoBot())
        # Check the repr.
        self.assertEqual('<SeaBoard for <AutoBot Ramius> with 4 of 17 hits>', repr(self.board))

    def testReprSunk(self):
        """Test the computer readable representaiton of a SeaBoard with a ship sunk."""
        # Sink a ship
        ship, squares = self.board.fleet[0]
        for square in squares[:]:
            self.board.fire(square, unitility.AutoBot())
        # Check the repr.
        self.assertEqual('<SeaBoard for <AutoBot Ramius> with 5 of 17 hits>', repr(self.board))

    def testShowFoe(self):
        """Test the player's view of their own board."""
        self.board.hits = set('J2 J1 I5 H5 G5 F5'.split())
        self.board.misses = set('J6 I0 I1 H4 H9 G3 G8 F2 F7 E1 E6 D0 D5 C4 C9 B3 B8 A2 A7'.split())
        self.assertEqual('\n'.join(BOARD_LINES).replace('O', '.'), self.board.show(to = 'foe'))

    def testShowFriend(self):
        """Test the player's view of their own board."""
        self.board.hits = set('J2 J1 I5 H5 G5 F5'.split())
        self.board.misses = set('J6 I0 I1 H4 H9 G3 G8 F2 F7 E1 E6 D0 D5 C4 C9 B3 B8 A2 A7'.split())
        self.assertEqual('\n'.join(BOARD_LINES), self.board.show())
