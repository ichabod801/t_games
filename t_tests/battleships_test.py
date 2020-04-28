"""
battleships_test.py

Unit testing of t_games/board_games/battleships_game.py

Classes:
BotTest: Tests of Battleships bots. (unittest.TestCase)
GameOverTest: Tests of Battleships.game_over. (unittest.TestCase)
SeaBoardAdjTest: Test of adjacent squares on a Battleships' board. (TestCase)
SeaBoardFireTest: Test of firing on a Battleships' board. (unittest.TestCase)
SeaBoardMakeShipTest: Test getting ship squares from end points. (TestCase)
SeaBoardPlaceShipsTest: Test placing ships on the board. (unittest.TestCase)
SeaBoardTextTest: Tests of text versions of a Battleships' board. (TestCase)
"""


import itertools
import unittest

from t_games.board_games import battleships_game as battleships
from t_games.t_tests import unitility


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
        self.assertEqual(((1, 3), (2, 2), (1, 1)), tuple(self.board.adjacent_squares('A1')))

    def testBottomLeft(self):
        """Test adjacent squares of a square on the bottom left."""
        self.assertEqual(((1, 2), (2, 1)), tuple(self.board.adjacent_squares('A0')))

    def testLeft(self):
        """Test adjacent squares of a square on the left."""
        self.assertEqual(((5, 2), (6, 1), (4, 1)), tuple(self.board.adjacent_squares('E0')))

    def testLeftTop(self):
        """Test adjacent squares of a square on the left top."""
        self.assertEqual(((10, 2), (9, 1)), tuple(self.board.adjacent_squares('J0')))

    def testMiddle(self):
        """Test adjacent squares of a square in the middle."""
        self.assertEqual(((3, 6), (4, 5), (3, 4), (2, 5)), tuple(self.board.adjacent_squares('C4')))

    def testRight(self):
        """Test adjacent squares of a square on the right."""
        self.assertEqual(((8, 10), (7, 9), (6, 10)), tuple(self.board.adjacent_squares('G9')))

    def testRightBottom(self):
        """Test adjacent squares of a square on the right bottom."""
        self.assertEqual(((10, 2), (9, 1)), tuple(self.board.adjacent_squares('J0')))

    def testTop(self):
        """Test adjacent squares of a square on the top."""
        self.assertEqual(((10, 7), (10, 5), (9, 6)), tuple(self.board.adjacent_squares('J5')))

    def testTopRight(self):
        """Test adjacent squares of a square on the top right."""
        self.assertEqual(((10, 9), (9, 10)), tuple(self.board.adjacent_squares('J9')))


class SeaBoardFireTest(unittest.TestCase):
    """Test of firing on a Battleships' board. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['J0 J4', 'H0 H3', 'F0 F2', 'D0 D2', 'B0 B1'])
        self.board = battleships.SeaBoard(self.bot)
        self.foe = unitility.AutoBot()

    def testHitHit(self):
        """Test a basic hit getting recorded."""
        self.board.fire('J0', self.foe)
        self.assertIsInstance(self.board[(10, 1)].contents, battleships.Hit)

    def testHitMessage(self):
        """Test notification of a basic hit."""
        self.board.fire('H1', self.foe)
        self.assertEqual(['You hit.\n'], self.foe.info)

    def testHitRemoval(self):
        """Test a basic hit being marked on the ship."""
        ship = self.board[6, 3].contents.ship
        self.board.fire('F2', self.foe)
        self.assertNotIn((6, 3), ship.sections)

    def testMissMessage(self):
        """Test notification of a basic miss."""
        self.board.fire('C4', self.foe)
        self.assertEqual(['You missed.\n'], self.foe.info)

    def testMissMiss(self):
        """Test a basic miss being recorded."""
        self.board.fire('J9', self.foe)
        self.assertIsInstance(self.board[(10, 10)].contents, battleships.Miss)

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
        start, end = self.board.convert('H5'), self.board.convert('H0')
        self.assertEqual([(8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6)], self.board.make_ship(start, end))

    def testLeft(self):
        """Test making a ship going to the left."""
        start, end = self.board.convert('E9'), self.board.convert('E5')
        self.assertEqual([(5, 6), (5, 7), (5, 8), (5, 9), (5, 10)], self.board.make_ship(start, end))

    def testNegative(self):
        """Test failing to make a ship with a negative slope."""
        start, end = self.board.convert('D6'), self.board.convert('A3')
        self.assertEqual([], self.board.make_ship(start, end))

    def testPositive(self):
        """Test failing to make a ship with a positive slope."""
        start, end = self.board.convert('B3'), self.board.convert('F7')
        self.assertEqual([], self.board.make_ship(start, end))

    def testRight(self):
        """Test making a ship going to the right."""
        start, end = self.board.convert('D6'), self.board.convert('D9')
        self.assertEqual([(4, 7), (4, 8), (4, 9), (4, 10)], self.board.make_ship(start, end))

    def testUp(self):
        """Test maing a ship going up."""
        start, end = self.board.convert('A7'), self.board.convert('C7')
        self.assertEqual([(1, 8), (2, 8), (3, 8)], self.board.make_ship(start, end))


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
        check = battleships.Ship('Carrier', [(9, 3), (9, 4), (9, 5), (9, 6), (9, 7)])
        self.assertEqual(check.sections, board.fleet[0].sections)

    def testHorizontalFourFleet(self):
        """Test placing a horizontal four square ship in the fleet."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        check = battleships.Ship('Submarine', [(7, 4), (7, 5), (7, 6), (7, 7)])
        self.assertEqual(check.sections, board.fleet[1].sections)

    def testHorizontalThreeFleet(self):
        """Test placing a horizontal three square ship in the fleet."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        check = battleships.Ship('Submarine', [(5, 5), (5, 6), (5, 7)])
        self.assertEqual(check.sections, board.fleet[2].sections)

    def testHorizontalTwoFleet(self):
        """Test placing a horizontal two square ship in the fleet."""
        self.bot.replies = ['i6 i2', 'g6 g3', 'e6 e4', 'c4 c2', 'a7 a8']
        board = battleships.SeaBoard(self.bot)
        check = battleships.Ship('Destroyer', [(1, 8), (1, 9)])
        self.assertEqual(check.sections, board.fleet[4].sections)

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
        check = battleships.Ship('Submarine', [(1, 9)])
        self.assertEqual(check.sections, board.fleet[5].sections)

    def testTwoError(self):
        """Test the error from giving one square for a three square ship."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        self.assertEqual(['Please enter a start and end square.\n'], self.bot.errors)

    def testVerticalFiveFleet(self):
        """Test placing a vertical five square ship in the fleet."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        check = battleships.Ship('Battleship', [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2)])
        self.assertEqual(check.sections, board.fleet[0].sections)

    def testVerticalFourFleet(self):
        """Test placing a vertical four square ship in the fleet."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        check = battleships.Ship('Battleship', [(4, 4), (5, 4), (6, 4), (7, 4)])
        self.assertEqual(check.sections, board.fleet[1].sections)

    def testVerticalThreeFleet(self):
        """Test placing a vertical three square ship in the fleet."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        check = battleships.Ship('Cruiser', [(7, 8), (8, 8), (9, 8)])
        self.assertEqual(check.sections, board.fleet[3].sections)

    def testVerticalTwoFleet(self):
        """Test placing a vertical two square ship in the fleet."""
        self.bot.replies = ['A1 e1', 'g3 D3', 'e5 g5', 'I7 G7', 'I9 j9']
        board = battleships.SeaBoard(self.bot)
        check = battleships.Ship('Destroyer', [(9, 10), (10, 10)])
        self.assertEqual(check.sections, board.fleet[4].sections)


class SeaBoardTextTest(unittest.TestCase):
    """Tests of text versions of a Battleships' board. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot(['j0 j4', 'i5 f5', 'd1 d3', 'f8 d8', 'b5 b6'])
        self.bot.name = 'Ramius'
        self.board = battleships.SeaBoard(self.bot)

    def testRepr(self):
        """Test the computer readable representaiton of a starting SeaBoard."""
        self.assertEqual('<SeaBoard with 10x10 Waters>', repr(self.board))

    def testShowFoe(self):
        """Test the player's view of their own board."""
        for hit in 'J2 J1 I5 H5 G5 F5'.split():
            self.board.place(self.board.convert(hit), battleships.Hit())
        for miss in 'J6 I0 I1 H4 H9 G3 G8 F2 F7 E1 E6 D0 D5 C4 C9 B3 B8 A2 A7'.split():
            self.board.place(self.board.convert(miss), battleships.Miss())
        self.assertEqual('\n'.join(BOARD_LINES).replace('O', '.'), self.board.show(to = 'foe'))

    def testShowFriend(self):
        """Test the player's view of their own board."""
        for hit in 'J2 J1 I5 H5 G5 F5'.split():
            self.board.place(self.board.convert(hit), battleships.Hit())
        for miss in 'J6 I0 I1 H4 H9 G3 G8 F2 F7 E1 E6 D0 D5 C4 C9 B3 B8 A2 A7'.split():
            self.board.place(self.board.convert(miss), battleships.Miss())
        self.assertEqual('\n'.join(BOARD_LINES), self.board.show())


if __name__ == '__main__':
    unittest.main()
