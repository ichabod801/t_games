"""
other_cmd_test.py

Unit testing of t_games/other_cmd.py.

Classes:
OtherCmdTest: Tests of a text command handler. (unittest.TestCase)
"""


import unittest

import t_games.other_cmd as other_cmd
import t_games.player as player


class OtherCmdTest(unittest.TestCase):
    """Tests of a text command handler. (unittest.TestCase)"""

    def setUp(self):
        self.cmd_handler = other_cmd.OtherCmd(player.Bot())
        self.cmd_handler.human.name = 'George'

    def testRepr(self):
        """Test the debugging text representation for the command handler."""
        self.assertEqual('<OtherCmd for <Bot George>>', repr(self.cmd_handler))


if __name__ == '__main__':
    unittest.main()
