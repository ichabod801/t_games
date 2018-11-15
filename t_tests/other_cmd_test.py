"""
other_cmd_test.py

Unit testing of t_games/other_cmd.py.

Classes:
OtherCmdDebugTest: Tests of debugging with a text command handler. (TestCase)
OtherCmdTextTest: Tests of text for a command handler. (unittest.TestCase)
"""


import unittest

import t_games.other_cmd as other_cmd
import t_games.player as player
import t_tests.unitility as unitility


class OtherCmdDebugTest(unittest.TestCase):
	"""Tests of debugging with a text command handler. (unittest.TestCase)"""

	def setUp(self):
		self.bot = unitility.AutoBot()
		self.cmd_handler = other_cmd.OtherCmd(self.bot)

	def testBasic(self):
		"""Test a basic debugging."""
		self.cmd_handler.do_debug('1 ** 1 * 2 ** 2 * 3 ** 3')
		self.assertEqual('108\n', self.bot.info[0])

	def testException(self):
		"""Test the debug command catching an exception."""
		self.cmd_handler.do_debug('1 / 0')
		check = '\nThere was an exception raised while processing that command:\n'
		self.assertEqual(check, self.bot.errors[0])

	def testSelf(self):
		"""Test that self in debugging references the other_cmd instance."""
		self.cmd_handler.do_debug('id(self)')
		self.assertEqual(str(id(self.cmd_handler)), self.bot.info[0].strip())

	def testTurnContinuation(self):
		"""Test that debugging does not end the turn."""
		self.cmd_handler.do_debug('1 ** 1 * 2 ** 2 * 3 ** 3')
		self.assertTrue(self.bot.info[0])


class OtherCmdTextTest(unittest.TestCase):
    """Tests of a text command handler. (unittest.TestCase)"""

    def setUp(self):
        self.cmd_handler = other_cmd.OtherCmd(player.Bot())
        self.cmd_handler.human.name = 'George'

    def testRepr(self):
        """Test the debugging text representation for the command handler."""
        self.assertEqual('<OtherCmd for <Bot George>>', repr(self.cmd_handler))


if __name__ == '__main__':
    unittest.main()
