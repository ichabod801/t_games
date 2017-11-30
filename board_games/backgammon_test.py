"""
backgammon_test.py

Unit testing for backgammon_game.py.

Classes:
MoveTest: Test move generation. (TestCase)
"""


import unittest

from tgames.board_games import backgammon_game as bg


class MoveTest(unittest.TestCase):
	"""Test move generation. (TestCase)"""

	def setBoard(self, layout = ((6, 5), (8, 3), (13, 5), (24, 2)), moves = [], piece = 'O', 
		rolls = [6, 5]):
		"""Set up the board for a test. (None)"""
		self.board = bg.BackgammonBoard(layout = layout)
		for start, end in moves:
			self.board.move(start, end)
		raw_moves = self.board.get_moves(piece, rolls)
		self.legal_moves = set(tuple(move) for move in raw_moves)

	def testStart(self):
		"""Test the moves at the start of the game."""
		self.setBoard()
		check = [(((11,), (16,)), ((0,), (6,))), (((11,), (16,)), ((11,), (17,))), 
			(((11,), (16,)), ((16,), (22,))), (((16,), (21,)), ((0,), (6,))), 
			(((16,), (21,)), ((11,), (17,))), (((16,), (21,)), ((16,), (22,))), 
			(((0,), (6,)), ((6,), (11,))), (((11,), (17,)), ((17,), (22,)))]
		check = set(check)
		self.assertEqual(check, self.legal_moves)

	def testStartBlock(self):
		"""Test the moves at the start of the game."""
		# !! add block moves, remove blocked moves
		self.setBoard()
		check = [(((11,), (16,)), ((0,), (6,))), (((11,), (16,)), ((11,), (17,))), 
			(((11,), (16,)), ((16,), (22,))), (((16,), (21,)), ((0,), (6,))), 
			(((16,), (21,)), ((11,), (17,))), (((16,), (21,)), ((16,), (22,))), 
			(((0,), (6,)), ((6,), (11,))), (((11,), (17,)), ((17,), (22,)))]
		check = set(check)
		self.assertEqual(check, self.legal_moves)


if __name__ == '__main__':
	unittest.main()