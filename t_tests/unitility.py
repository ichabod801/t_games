"""
unitility.py

Utility classes and functions for unit testing.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
AutoBot: A programmatically controlled bot. (player.Bot)
MockRandom: A fake random module for testing with random numbers. (object)
ProtoObject: An object whose attributes can be defined w/ __init__. (object)
ProtoStdIn: A programatically controlled stdin. (object)
ProtoStdOut: A locally stored stdout. (object)
TestGame: A Game sub-class for testing purposes. (game.Game)

Functions:
Make a test case of playing the game with bots. (unittest.Testcase)
"""


import itertools
import sys
import unittest

from .. import game
from .. import player
from .. import utility


class AutoBot(player.Bot):
    """
    A programmatically controlled bot. (player.Bot)

    Attributes:
    all_done: A flag for the clean_up method being called. (bool)
    all_set: A flag for the set_up method being called. (bool)
    errors: Errors the bot has been warned about. (list of str)
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
        # Output from the bot.
        self.replies = replies
        # Input to the bot.
        self.info = []
        self.errors = []
        self.results = []
        # Method call tracking.
        self.all_set, self.all_done = False, False
        # Humanoid attributes.
        self.session_index = 0

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

    def clean_up(self):
        """Do any necessary post-game processing. (None)"""
        self.all_done = True

    def error(self, *args, **kwargs):
        """
        Warn the player about an invalid play. (None)

        Parameters:
        The parameters are as teh built-in print function.
        """
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        self.errors.append('{}{}'.format(sep.join([str(arg) for arg in args]), end))

    def set_up(self):
        """Do any necessary pre-game processing. (None)"""
        self.all_set = True

    def store_results(self, game_name, result):
        """
        Store game results. (None)

        Parameters:
        game_name: The name of the game the result is from. (str)
        results: The results of playing the game. (list of int)
        """
        self.results.append([game_name] + result)

    def store_shortcut(self, shortcut, text):
        """
        Store new shortcuts. (None)

        Parameters:
        shortcut: The word that is the short cut. (str)
        text: The text the shortcut expands into. (str)
        """
        # Store locally
        self.shortcuts[shortcut] = text

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        self.info.append('{}{}'.format(sep.join([str(arg) for arg in args]), end))


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
    __call__
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
        self.arg_list = []
        self.kwarg_list = []

    def __call__(self, *args, **kwargs):
        """
        Store any parameters passed to the object as a function. (None)

        Parameters:
        *args: The names of any dummy methods.
        **kwargs: Attributes and their values.
        """
        self.args = args
        self.arg_list.append(args)
        self.kwargs = kwargs
        self.kwarg_list.append(kwargs)

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


class TestGame(game.Game):
    """
    A Game sub-class for testing purposes. (game.Game)

    Attributes:
    all_set: A flag for the set_up method being called. (bool)
    all_done: A flag for the clean_up method being called. (bool)
    move: The move the player made.

    Overridden Methods
    game_over
    player_action
    """

    aka = '1'
    name = 'Unit'
    rules = '\nIf you enter win, you win; if you enter lose, you lose.\n'

    def __init__(self, human, raw_options, interface = None):
        """
        Set up the game. (None)

        human: The primary player of the game. (player.Player)
        raw_options: The user's option choices as provided by the interface. (str)
        interface: The interface that started the game playing. (interface.Interface)
        """
        super(TestGame, self).__init__(human, raw_options, interface)
        if hasattr(self.interface, 'flags'):
            self.flags = self.interface.flags
        self.all_set, self.all_done = False, False

    def clean_up(self):
        """Do any necessary post-game processing. (None)"""
        self.all_done = True

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Check for match play.
        if self.flags & 256:
            self.win_loss_draw = [2, 2, 1]
        # Resolve game ending moves.
        if self.move.startswith('win'):
            self.win_loss_draw[0] += 1
        elif self.move.startswith('lose') or self.move.startswith('loss'):
            self.win_loss_draw[1] += 1
        elif self.move.startswith('draw'):
            self.win_loss_draw[1] += 1
        else:
            # Keep playing.
            return False
        # Add additional wins, losses, and draws.
        for result_index, result_char in enumerate('+-='):
            self.win_loss_draw[result_index] += self.move.count(result_char)
        # Set the score when the game ends.
        self.scores[self.human.name] = self.turns
        return True

    def handle_options(self):
        """Handle the options for this play of the game."""
        if self.raw_options.lower() == 'error':
            self.option_set.error = True

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        self.move = player.ask('What is your move, {}? '.format(player.name)).lower()
        # Check for continuation.
        if self.move == 'continue':
            return True
        elif self.move.startswith('&'):
            return self.do_debug(self.move[2:])
        # Check for quitting early.
        elif self.move.startswith('quit'):
            if '+' in self.move:
                self.force_end = 'win'
            else:
                self.force_end = 'loss'

    def set_up(self):
        """Do any necessary pre-game processing. (None)"""
        self.all_set = True


def bot_test(game, bot_classes, rounds, n_bots, options = 'none', bot_params = []):
    """
    Make a test case of playing the game with bots. (unittest.Testcase)

    For every number of bots in n_bots, every combination of that many bots from
    the bots parameter is run in a tournament for the specified number of rounds.

    Parameters:
    game: The game to play. (game.Game)
    bot_classes: The bot classes to play the game. (list of type)
    rounds: The number of rounds to play each test. (int)
    n_bots: The valid numbers of bots. (list of int)
    options: The options passed to the game. (str)
    bot_params: The parameters to pass to the bot initializations. (list of tuple)
    """
    # A test framework to put the individual tournaments into.
    class BotTest(unittest.TestCase):
        """Tests of the bots in {}.""".format(game.name)
        def setUp(self):
            self.bot = AutoBot()
            self.game = game(self.bot, options)
            self.rounds = rounds
    # A function for adding a test for a specific set of bots.
    def make_bot_test(bots):
        def testSomeBots(self):
            self.game.tournament(bots, self.rounds)
        bot_text = utility.oxford([bot.__class__.__name__ for bot in bots])
        testSomeBots.__doc__ = 'Bot test of {}.'.format(bot_text)
        return testSomeBots
    # Instantiate the bots.
    if not bot_params:
        bot_params = [()] * len(bot_classes)
    bots = []
    taken_names = []
    for bot_class, params in zip(bot_classes, bot_params):
        bots.append(bot_class(*params, taken_names = taken_names))
        taken_names.append(bots[-1].name)
    # Add the tests to the class
    for num_bots in n_bots:
        for group_index, test_bots in enumerate(itertools.combinations(bots, num_bots)):
            new_test = make_bot_test(list(test_bots))
            setattr(BotTest, 'testBots{}_{:03}'.format(num_bots, group_index + 1), new_test)
    return BotTest
