"""
unitility.py

Utility classes and functions for unit testing.

Classes:
AutoBot: A programmatically controlled bot. (player.Bot)
ProtoObject: An object whose attributes can be defined w/ __init__. (object)
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
        self.results = []

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        return self.replies.pop(0)

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
        return self.replies.pop(0)

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
        return self.replies.pop(0)

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
        return self.replies.pop(0)

    def error(self, *args, **kwargs):
        """
        Warn the player about an invalid play. (None)

        Parameters:
        The parameters are as teh built-in print function.
        """
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        self.errors.append('{}{}'.format(sep.join(args), end))

    def store_results(self, game_name, result):
        """
        Store game results. (None)

        Parameters:
        game_name: The name of the game the result is from. (str)
        results: The results of playing the game. (list of int)
        """
        self.results.append([game_name] + result)

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        self.info.append('{}{}'.format(sep.join(args), end))


class MockRandom(object):
    """
    A fake random module for testing with random numbers. (object)

    Attributes:
    values: A stack of fake random values to return. (list of number)

    Methods:
    choice: Fake choice function. (object)
    push: Add more values to the fake random number list. (None)
    randint: Fake randint function. (number)
    random: Fake random number. (number)
    randrange: Fake randrange function. (number)

    Overridden Methods:
    __init__
    """

    def __init__(self, values = []):
        """
        Set the values to return. (None)

        Parameters:
        values: A stack of fake random values to return. (list of number)
        """
        self.values = values

    def choice(self, seq):
        """Fanke choice function. (object)"""
        return seq[self.values.pop()]

    def push(self, values):
        """
        Add more values to the fake random number list. (None)

        Parameters:
        values: A takc of fake random values to return. (number or seq of number)
        """
        try:
            self.values.extend(values)
        except TypeError:
            self.values.append(values)

    def randint(self, start, stop):
        """Fake randint function. (number)"""
        return self.values.pop()

    def random(self):
        """Fake random number. (number)"""
        return self.values.pop()

    def randrange(self, start, stop = None, step = None):
        """Fake randrange function. (number)"""
        return self.values.pop()


class ProtoObject(object):
    """
    An object whose attributes can be defined during initialization. (object)

    Methods:
    dummy_method: Return whatever is passed to this method.

    Overriddent Methods:
    __init__
    """

    def __init__(self, *args, **kwargs):
        """
        Set up the object's attributes. (None)

        Parameters:
        *args: The names of any dummy methods.
        **kwargs: Attributes and their values.
        """
        self.__dict__.update(kwargs)
        for arg in args:
            setattr(self, arg, self.dummy_method)

    def dummy_method(self, *args, **kwargs):
        """Return whatever is passed to this method."""
        if args and kwargs:
            return args, kwargs
        elif args:
            return args
        elif kwargs:
            return kwargs


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
