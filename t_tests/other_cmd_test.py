"""
other_cmd_test.py

Unit testing of t_games/other_cmd.py.

Classes:
OtherCmdCmdTest: Tests of actually handling other commands. (unittest.TestCase)
OtherCmdDebugTest: Tests of debugging with a text command handler. (TestCase)
OtherCmdHelpTest: Tests of help text from a command handler. (TestCase)
OtherCmdShortcutTest: Tests of setting shortcuts. (unittest.TestCase)
OtherCmdTextTest: Tests of text for a command handler. (unittest.TestCase)
"""


import unittest

from t_games import other_cmd
from t_games import player
from t_games.t_tests import unitility


class OtherCmdCmdTest(unittest.TestCase):
    """Tests of actually handling other commands. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot([''])
        self.cmd_handler = other_cmd.OtherCmd(self.bot)

    def testAliasArguments(self):
        """Test handling an alias with arguments."""
        self.cmd_handler.handle_cmd('& self.human.name')
        self.assertEqual("'{}'\n".format(self.bot.name), self.bot.info[0])

    def testAliasPlain(self):
        """Test handling an alias with no arguments."""
        self.cmd_handler.handle_cmd('?')
        self.assertEqual('\nResistance is futile.\n', self.bot.info[0])

    def testArguments(self):
        """Test handling a command with arguments."""
        self.cmd_handler.handle_cmd('set foo bar')
        self.assertEqual('bar', self.bot.shortcuts['foo'])

    def testPlain(self):
        """Test handling a command with no arguments."""
        self.cmd_handler.handle_cmd('help')
        self.assertEqual('\nResistance is futile.\n', self.bot.info[0])

    def testUnknown(self):
        """Test handling an unknown command."""
        self.cmd_handler.handle_cmd('sit')
        self.assertEqual("\nI do not recognize the command 'sit'.\n", self.bot.errors[0])


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
        self.assertEqual(repr(id(self.cmd_handler)), self.bot.info[0].strip())

    def testTurnContinuation(self):
        """Test that debugging does not end the turn."""
        self.cmd_handler.do_debug('1 ** 1 * 2 ** 2 * 3 ** 3')
        self.assertTrue(self.bot.info[0])


class OtherCmdHelpTest(unittest.TestCase):
    """Tests of help text from a command handler. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot([''])
        self.cmd_handler = other_cmd.OtherCmd(self.bot)
        self.cmd_handler.help_text['test'] = '\nCheck, 1, 2, 3, 4.\n'

    def testAliasHelp(self):
        """Test help text from a doc string."""
        self.cmd_handler.do_help('&')
        self.assertEqual("\nI can't help you with that.\n", self.bot.info[0])

    def testBlankHelpText(self):
        """Test the default help text."""
        self.cmd_handler.do_help('')
        self.assertEqual('\nResistance is futile.\n', self.bot.info[0])

    def testBlankHelpTopics(self):
        """Test the default help topic list."""
        self.cmd_handler.do_help('')
        self.assertEqual('set, test\n', self.bot.info[-1])

    def testDictionaryHelp(self):
        """Test help text from the help_text dictionary."""
        self.cmd_handler.do_help('test')
        self.assertEqual('\nCheck, 1, 2, 3, 4.\n', self.bot.info[0])

    def testDocStringHelp(self):
        """Test help text from a doc string."""
        self.cmd_handler.do_help('debug')
        self.assertEqual("\nI can't help you with that.\n", self.bot.info[0])

    def testMethodHelpCall(self):
        """Test help calling a help_foo method."""
        self.cmd_handler.help_foo = unitility.ProtoObject()
        self.cmd_handler.do_help('foo')
        self.assertEqual([()], self.cmd_handler.help_foo.arg_list)

    def testMethodHelpCall(self):
        """Test help calling a help_foo method."""
        self.cmd_handler.help_foo = unitility.ProtoObject()
        self.cmd_handler.do_help('foo')
        self.assertEqual([()], self.cmd_handler.help_foo.arg_list)

    def testMethodHelpAsk(self):
        """Test a help_foo asking for an enter."""
        self.cmd_handler.help_foo = unitility.ProtoObject()
        self.cmd_handler.do_help('foo')
        self.assertEqual([], self.bot.replies)

    def testMethodHelpSkip(self):
        """Test a help_foo not asking for an enter."""
        self.cmd_handler.help_foo = lambda: True
        self.cmd_handler.do_help('foo')
        self.assertEqual([''], self.bot.replies)

    def testUnknownHelp(self):
        """Test help text for an unknown topic."""
        self.cmd_handler.do_help("Cthulhu")
        self.assertEqual("\nI can't help you with that.\n", self.bot.info[0])


class OtherCmdShortcutTest(unittest.TestCase):
    """Tests of setting shortcuts. (unittest.TestCase)"""

    def setUp(self):
        self.bot = unitility.AutoBot()
        self.cmd_handler = other_cmd.OtherCmd(self.bot)

    def testLong(self):
        """Test setting a multi-word shortcut."""
        self.cmd_handler.do_set('spam spam spam spam eggs')
        self.assertEqual('spam spam spam eggs', self.bot.shortcuts['spam'])

    def testNoShortcutError(self):
        """Test giving an error for a shortcut with no shortcut."""
        self.cmd_handler.do_set('')
        self.assertEqual('\nNo shortcut was provided, nothing was set.\n', self.bot.errors[0])

    def testNoShortcutNoSet(self):
        """Test not setting a shortcut with no shortcut."""
        self.cmd_handler.do_set('')
        self.assertEqual({}, self.bot.shortcuts)

    def testNoTextError(self):
        """Test giving an error for a shortcut with no expansion text."""
        self.cmd_handler.do_set('whoops')
        check = '\nNo expansion text was provided, the shortcut was not set.\n'
        self.assertEqual(check, self.bot.errors[0])

    def testNoTextNoSet(self):
        """Test not setting a shortcut with no expansion text."""
        self.cmd_handler.do_set('whoops')
        self.assertEqual({}, self.bot.shortcuts)

    def testShort(self):
        """Test setting a one word shortcut."""
        self.cmd_handler.do_set('foo bar')
        self.assertEqual('bar', self.bot.shortcuts['foo'])


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
