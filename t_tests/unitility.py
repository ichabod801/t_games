"""
unitility.py

Utility classes and functions for unit testing.

Classes:
AutoBot: A programmatically controlled bot. (player.Bot)
ProtoStdIn: A programatically controlled stdin. (object)
ProtoStdOut: A locally stored stdout. (object)
"""


import sys

import t_games.game as game
import t_games.player as player


class AutoBot(player.Bot):
    """
    A programmatically controlled bot. (player.Bot)

    Attributes:
    info: Things the bot has been told. (list of str)
    replies: The answers to questions the bot will be asked. (list)

    Overridden Methods:
    __init__
    ask
    ask_int
    ask_int_list
    ask_valid
    tell
    """

    def __init__(self, replies = []):
        """
        Set up the bot. (None)

        Parameters:
        name: The name of the bot. (str)
        replies: The answers to questions the bot will be asked. (list)
        """
        super(AutoBot, self).__init__()
        self.replies = replies
        self.info = []
        self.errors = []
        self.game = game.Game(self, 'none')

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        return replies.pop(0)

    def ask_int(self, prompt, low = None, high = None, valid = [], default = None, cmd = True):
        """
        Get an integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        valid: The valid values for the integer. (container of int)
        default: The default choice. (int or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        return replies.pop(0)

    def ask_int_list(self, prompt, low = None, high = None, valid = [], valid_lens = [], default = None,
        cmd = True):
        """
        Get a multiple integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (list or None)
        high: The highest acceptable value for the integer. (laist or None)
        valid: The valid values for the integer. (list of int)
        valid_lens: The valid numbers of values. (list of int)
        default: The default choice. (list or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        return replies.pop(0)

    def ask_valid(self, prompt, valid, default = '', lower = True):
        """
        Get and validate responses from the user. (str)

        Note that default must be in valid.

        Parameters:
        prompt: The question to ask the user. (str)
        valid: The valid responses from the user. (container of str)
        default: The default value for the response. (str)
        lower: A flag for case insensitive matching. (bool)
        """
        return replies.pop(0)

    def error(self, *args, **kwargs):
        """
        Warn the player about an invalid play. (None)

        Parameters:
        The parameters are as teh built-in print function.
        """
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        self.errors.append('{}{}'.format(sep.join(args), end))

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        self.info.append('{}{}'.format(sep.join(args), end))


class ProtoStdIn(object):
    """
    A programatically controlled stdin. (object)

    Attributes:
    lines: The lines of input to give. (list of str)

    Methods:
    readline: Return the next line of input. (list of str)

    Overridden Methods:
    __init__
    """

    def __init__(self, lines = []):
        """Set up the starting input. (None)"""
        self.lines = lines

    def readline(self):
        """Return the next line of input. (str)"""
        return self.lines.pop(0)


class ProtoStdOut(object):
    """
    A locally stored stdout. (object)

    Attributes:
    output: The pieces of output received. (list of str)

    Methods:
    write: Receive the next piece of output. (list of str)

    Overridden Methods:
    __init__
    """

    def __init__(self):
        """Set the instance up to receive output. (None)"""
        self.output = []

    def write(self, text):
        """
        Recieve the next piece of output. (list of str)

        Parameters:
        text: The output received. (str)
        """
        self.output.append(text)
