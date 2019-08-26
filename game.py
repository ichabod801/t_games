"""
game.py

The base game object for t_games.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
Game: A game with a text interface. (OtherCmd)
Flip: A test game of flipping coins. (Game)
FlipBot: A bot to play Flip against. (Player)
Sorter: A test game of sorting a sequence. (Game)

Functions:
load_games: Load all of the games defined locally. (tuple of dict)
"""


from __future__ import division, print_function

import glob
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import itertools
import math
import operator
import os
import random
import re
import sys

from . import dice
from . import options
from .other_cmd import OtherCmd
from .player import Player
from . import utility


class Game(OtherCmd):
    """
    A game with a text interface. (OtherCmd)

    In non-solitaire games, the players attribute should be set in handle_options.

    The flags attribute represents a bunch of binary flags:
        1: Options were set by the player.
        2: Internal command tracking.
        4: The game was lost via the quit command.
        8: Internal command tracking.
        16: Non-interface game play tracking.
        32: Internal command tracking.
        64: Non-interface game play tracking.
        128: Abnormal game win.
        256: This game was played as a match.
        512: This game was played with a cyborg.

    Class Attributes:
    aka: Other names for the game. (list of str)
    categories: The interface categories for the game. (list of str)
    credits: The design and programming credits for this game. (str)
    int_re: A regular expression matching integer numbers. (SRE_Pattern)
    float_re: A regular expression matching decimal numbers. (SRE_Pattern)
    help_text: Extra help text for the game. (dict of str: str)
    name: The primary name of the game. (str)
    num_options: The number of settable options for the game. (str)
    operators: Operator definitions for the RPN command. (dict of str: callable)
    rules: The rules of the game. (str)

    Attributes:
    flags: Flags for different game events tracked in the results. (int)
    force_end: How to force the end of the game. (str)
    human: The primary player of the game. (Player)
    interface: The interface that started the game playing. (Interface)
    option_set: The definitions of allowed options for the game (OptionSet)
    raw_options: The options as given by the play command. (str)
    scores: The players' scores in the game. (dict of str: int)
    turns: The number of turns played in the game. (int)
    win_loss_draw: A list of the player's results in the game. (list of int)

    Methods:
    clean_up: Handle any end of game tasks. (None)
    do_credits: Show the credits. (bool)
    do_quit: Quit the game, which counts as a loss. (bool)
    do_quit_quit: Quit the game and the t_games interface. (bool)
    do_rpn: Process reverse Polish notation statements to do calculations. (None)
    do_rules: Show the rules text. (bool)
    game_over: Check for the end of the game. (bool)
    handle_options: Handle game options and set the player list. (None)
    play: Play the game. (list of int)
    player_action: Handle a player's turn or other player actions. (bool)
    set_options: Define the options for the game. (bool)
    set_players: Reset/change the list of players. (None)
    set_up: Handle any pre-game tasks. (None)
    tournament: Run a tournament of the game. (dict)

    Overridden Methods:
    __init__
    __repr__
    default
    do_debug
    """

    aka = []
    aliases = {'!!': 'quit_quit', '=': 'rpn', '!': 'quit'}
    categories = ['Test Games']
    credits = 'No credits have been specified for this game.'
    help_text = {'help': '\nUse the rules command for instructions on how to play.'}
    int_re = re.compile('-?\d*$')
    float_re = re.compile('-?\d*\.\d+')
    name = 'Null'
    num_options = 0
    operators = {'|': (abs, 1), '+': (operator.add, 2), 'C': (utility.choose, 2), '/%': (divmod, 2),
        '!': (math.factorial, 1), '//': (operator.floordiv, 2), '*': (operator.mul, 2),
        '%': (operator.mod, 2), '+-': (operator.neg, 1), 'P': (utility.permutations, 2),
        '^': (utility.pow, 2), '1/': (lambda x: 1 / x, 1), '-': (operator.sub, 2),
        '/': (operator.truediv, 2), 'ab/c': (lambda a, b, c: a + b / c, 3), 'cos': (math.cos, 1),
        'ln': (math.log, 1), 'log': (math.log10, 1), 'R': (random.random, 0), 'F': (utility.flip, 0),
        'sin': (math.sin, 1), 'V': (math.sqrt, 1), 'tan': (math.tan, 1)}
    rules = 'No rules have been specified for this game.'

    def __init__(self, human, raw_options, interface = None, silent = False):
        """
        Set up the game. (None)

        human: The primary player of the game. (player.Player)
        raw_options: The user's option choices as provided by the interface. (str)
        interface: The interface that started the game playing. (interface.Interface)
        silent: A flag for supressing the greeting. (bool)
        """
        # Set the specified attributes.
        self.human = human
        self.interface = interface
        self.raw_options = raw_options.strip()
        # Set the default attributes.
        self.flags = 0
        self.gipfed = []
        # Inherit aliases and help text from parent classes.
        self.aliases = {}
        self.help_text = {}
        for cls in reversed(self.__class__.__mro__):
            if hasattr(cls, 'aliases'):
                self.aliases.update(cls.aliases)
            if hasattr(cls, 'help_text'):
                self.help_text.update(cls.help_text)
        # Introduce yourself.
        if self.name != 'Fireball' and not silent:
            self.human.tell('\nWelcome to a game of {}, {}.'.format(self.name, self.human.name))
        # Define and process the game options.
        self.option_set = options.OptionSet(self)
        self.set_options()
        self.handle_options()
        # Set up the players.
        if not hasattr(self, 'players'):
            self.players = [self.human]
        for player in self.players:
            player.game = self

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        plural = utility.plural(len(self.players), 'player')
        return '<Game of {} with {} {}>'.format(self.name, len(self.players), plural)

    def clean_up(self):
        """Handle any end of game tasks. (None)"""
        pass

    def default(self, text):
        """
        Handle unrecognized commands. (bool)

        Parameters:
        text: The raw text input by the user. (str)
        """
        player = self.players[self.player_index]
        player.error('\nI do not recognize the command {!r}.'.format(text))
        return True

    def do_credits(self, arguments):
        """
        Show the credits for the game.
        """
        self.human.tell(self.credits.rstrip())
        return True

    def do_debug(self, arguments):
        """
        I can't help you with that.
        """
        self.flags |= 2
        return super(Game, self).do_debug(arguments)

    def do_quit(self, arguments):
        """
        Quit the game, which counts as a loss. (!)

        If you pass quit (or q or !) as an argument to the quit command, it quits the
        game and the entire t_games interface.
        """
        self.flags |= 4
        self.force_end = 'loss'
        self.win_loss_draw = [0, max(len(self.players) - 1, 1), 0]
        if arguments.lower() in ('!', 'quit', 'q'):
            self.human.held_inputs = ['!!']
        return False

    def do_quit_quit(self, arguments):
        """
        Quit the game and the t_games interface. (!!)
        """
        self.human.held_inputs = ['!']
        return self.do_quit('quit')

    def do_rpn(self, arguments):
        """
        Process reverse Polish notation statements to do calculations. (=)

        The avaible operators are:
            |     absolute value
            +     addition
            C     choose
            cos   cosine
            /     division
            /%    division and modulus
            ^     exponentiation
            !     factorial
            F     flip a coin (1 or 0)
            //    floor division
            ln    logarithm (natural)
            log   logarithm (base 10)
            %     modulus
            *     multiplication
            +-    negation
            P     permutations
            R     random number (standard uniform distribution)
            1/    reciprocal
            sin   sine
            -     subtraction
            V     square root
            tan   tangent
            ab/c  a + b / c

        For example, '= 1 1 +' returns 2. '= 1 1 ^ 2 2 ^ 3 3 ^ * *' returns 108.
        '= R 108 * 1 + 1 //' returns a random number from 1 to 108. So does
        '= 1 R 108 * + 1 //'.

        Note that the full stack is displayed at the end of the calculation.
        """
        # Process reverse Polish notation.
        stack = []
        for word in arguments.split():
            # handle operators
            if word in self.operators:
                # process operator
                op, n_params = self.operators[word]
                if len(stack) < n_params:
                    self.human.tell('Too few parameters for {}.'.format(word))
                    break
                # Correctly handle no paramters.
                if n_params == 0:
                    n_params = -len(stack)
                params = stack[-n_params:]
                stack = stack[:-n_params]
                try:
                    result = op(*params)
                except ValueError:
                    self.human.error('Bad value for {} operator.'.format(word))
                    break
                except ZeroDivisionError:
                    self.human.error('Zero division error.')
                    break
                # add to stack
                if isinstance(result, tuple):
                    stack.extend(result)
                else:
                    stack.append(result)
            # handle integers
            elif self.int_re.match(word):
                stack.append(int(word))
            # handle decimals
            elif self.float_re.match(word):
                stack.append(float(word))
            # handle garbage
            else:
                self.human.error('\nInvalid RPN expression.')
                return True
        # Display the stack.
        self.human.tell()
        self.human.tell(' '.join([str(x) for x in stack]))
        return True

    def do_rules(self, arguments):
        """
        Show the rules for the game.
        """
        self.human.tell(self.rules.rstrip())
        return True

    def do_xyzzy(self, arguments):
        """
        Nothing happens.
        """
        # Check to see if the planets are in the correct alignment.
        if self.interface.valve.blow(self):
            # Begin the incantation.
            self.human.tell('\nPoof!')
            game_class = random.choice(list(self.interface.games.values()))
            game = game_class(self.human, 'none', self.interface)
            self.flags |= 32
            results = game.play()
            # Finsh the incantation.
            results[5] |= 64
            self.human.store_results(game.name, results)
            # Check for a successful incantation.
            if (results[1] == 0 and results[0] > 0) or (results[5] & 256 and results[0] > results[1]):
                # Bind the tongues and seal the sigils.
                self.flags |= 128
                self.force_end = 'win'
                self.win_loss_draw = [max(len(self.players) - 1, 1), 0, 0]
                self.human.tell('\nThe incantation is complete. You win at {}.\n'.format(self.name))
                go = False
            else:
                # Nothing to see here.
                go = True
        else:
            # Were you expecting something to happen?
            self.human.tell('Nothing happens.')
            go = True
        return go

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Dummy random determination of game end.
        roll = random.randint(1, 3)
        if roll == 1:
            self.human.tell('You lose.')
            self.win_loss_draw[1] = 1
        elif roll == 2:
            self.human.tell('Keep playing.')
        else:
            self.human.tell('You win.')
            self.win_loss_draw[0] = 1
        return sum(self.win_loss_draw)

    def gipf_check(self, argument, game_names):
        """
        Check for successful gipfing. (int)

        Parameters:
        argument: The argument to the gipf command. (str)
        game_name: The names of the games to check. (list of str)
        """
        # Get the possible games and their aliases.
        if self.name == 'Oregon Trail':
            game_names = ()
            if len(self.gipfed) < 2:
                all_games = self.interface.games.items()
                games = {name: game for name, game in all_games if game.categories != ['Test Games']}
                del games['oregon trail']
                del games['ortr']
            else:
                games = {}
        else:
            games = {game_name: self.interface.games[game_name] for game_name in game_names}
            if 'oregon trail' in self.interface.games:
                games['oregon trail'] = self.interface.games['oregon trail']
                game_names += ('oregon trail',)
        for game_name in game_names:
            games.update({alias.lower(): games[game_name] for alias in games[game_name].aka})
        # Find the correct game.
        argument = argument.lower()
        if argument in games and games[argument].name not in self.gipfed:
            # Play the game.
            game = games[argument](self.human, 'none', self.interface)
            results = game.play()
            # Record the giphing.
            self.flags |= 8
            self.gipfed.append(game.name)
            results[5] |= 16
            self.human.store_results(game.name, results)
            # Reset the human's focus.
            self.human.game = self
            # Return the result.
            losses = results[1]
            if game.flags & 256 and results[0] > results[1]:
                losses = 0
            elif not results[0]:
                losses = 1
            # Handle gipfing to the trail.
            if game.name == 'Oregon Trail':
                argument = random.choice(game_names[:-1])
            else:
                argument = game.name.lower()
            return argument, losses
        # Return dummy results for incorrect games.
        else:
            return 'invalid-game', 1

    def handle_options(self):
        """Handle game options and set the player list. (None)"""
        self.option_set.handle_settings(self.raw_options)

    def help_xyzzy(self):
        """Help for the xyzzy command. (None)"""
        if random.random() < 0.2:
            # Get the names of other help topics.
            names = [name[3:] for name in dir(self.__class__) if name.startswith('do_')]
            names.extend([name[5:] for name in dir(self.__class__) if name.startswith('help_')])
            names.extend(self.help_text.keys())
            # Clean up the names.
            names = list(set(names) - set(('debug', 'help', 'text')))
            # Show one at random.
            self.do_help(random.choice(names))
            return True
        else:
            # Usually, just show the classic nothing happens.
            self.human.tell('\nNothing happens.')

    def play(self):
        """
        Play the game. (list of int)

        The return value is a list of data about the game played. By index:
            0: The number of players the human beat.
            1: The number of players that beat the human.
            2: The number of players tied with the human.
            3: The human's score.
            4: The number of turns played.
            5: The flags for the game (see help(game) for details).
            6: The options used for the game.
        """
        # Set up the game.
        self.win_loss_draw = [0, 0, 0]
        self.turns = 0
        self.force_end = ''
        self.flags &= 257  # reset everything but the options and match play flags.
        self.scores = {}
        self.set_up()
        if not self.scores:
            self.scores = {player.name: 0 for player in self.players}
        for player in self.players:
            player.set_up()
        # Loop through the players repeatedly.
        self.player_index = 0
        while True:
            # Loop through player actions until their turn is done.
            while self.player_action(self.players[self.player_index]):
                pass
            self.turns += 1
            # Check for the end of game.
            if self.force_end or self.game_over():
                break
            # Move to the next player.
            self.player_index = (self.player_index + 1) % len(self.players)
        # Clean up the game.
        self.clean_up()
        for player in self.players:
            player.clean_up()
        self.gipfed = []
        # Report the results.
        results = [self.scores[self.human.name], self.turns, self.flags, self.option_set.settings_text]
        return self.win_loss_draw + results

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        The return value is a flag for the player's turn continuing.

        Parameters:
        player: The player whose turn it is. (Player)
        """
        move = player.ask('What is your move, {}? '.format(player.name))

    def set_options(self):
        """Define the options for the game. (None)"""
        pass

    def set_players(self, players):
        """
        Reset/change the list of players. (player.Player)

        This is used in tournament play to specify the players in the game. The
        return value is the current human player.

        Parameters:
        players: The new players for the game. (list of player.Player)
        """
        # Set the players.
        self.players = players
        for player in self.players:
            player.game = self
        # Set specific references to players.
        human_hold = self.human
        self.human = self.players[0]
        if hasattr(self, 'bot') and len(self.players) == 2:
            self.bot = self.players[1]
        return human_hold

    def set_up(self):
        """Handle any pre-game tasks. (None)"""
        pass

    def tournament(self, players, rounds):
        """
        Run a tournament of the game. (dict)

        Parameters:
        players: The players in the tournament. (list of player.Player)
        rounds: The number of rounds to play. (int)
        """
        # Mute the output.
        save_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            # Set up the players.
            human_hold = self.set_players(players)
            # Set up results tracking.
            score_tracking = {player.name: [] for player in self.players}
            place_tracking = {player.name: [] for player in self.players}
            # Run the tournament.
            for game_index in range(rounds):
                # Run the game.
                results = self.play()
                # Track the results.
                rankings = sorted(self.scores.values(), reverse = True)
                for player, score in self.scores.items():
                    score_tracking[player].append(score)
                    place_tracking[player].append(rankings.index(score) + 1)
        finally:
            # Clean up.
            self.human = human_hold
            sys.stdout = save_stdout
        return {'scores': score_tracking, 'places': place_tracking}


class Flip(Game):
    """
    A test game of flipping coins. (Game)

    Attributes:
    bot: The non-human player. (FlipBot)

    Overridden Methods:
    game_over
    handle_options
    player_action
    """

    credits = '\nDesign and programming by Craig "Ichabod" O''Brien'
    name = 'Flip'
    rules = '\nWhoever gets two more heads than their opponent wins.'

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # Only check after both players get a chance to flip.
        if not self.turns % 2:
            # Check for someone ahead by 2 flips.
            score_values = list(self.scores.values())
            score_diff = abs(score_values[1] - score_values[0])
            if score_diff == 2:
                # Figure out who won.
                winning_score = max(score_values)
                if self.scores[self.human.name] == winning_score:
                    self.win_loss_draw[0] = 1
                    self.human.tell('You beat {} with {} heads!'.format(self.bot.name, winning_score))
                else:
                    self.win_loss_draw[1] = 1
                    message = 'You lost to {} win {} heads.'
                    self.human.tell(message.format(self.bot.name, winning_score - 2))

    def handle_options(self):
        """Handle game options and set the player list. (None)"""
        # Make sure the bot has a unique name.
        if self.human.name != 'Flip':
            self.bot = FlipBot('Flip')
        else:
            self.bot = FlipBot('Tosser')
        # Set up the players as the human and the bot.
        self.players = [self.human, self.bot]
        random.shuffle(self.players)
        return True

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the number of flips.
        flips = player.ask('How many times would you like to flip the coin (only the last flip counts)? ')
        # Check for invalid answers.
        if not flips.strip().isdigit():
            return self.handle_cmd(flips)
        # Flip a coin the specified number of times.
        for flip_index in range(int(flips)):
            if random.random() < 0.5:
                flip = 'tails'
            else:
                flip = 'heads'
            player.tell('Flip #{} is {}.'.format(flip_index + 1, flip))
        # Record the final flip.
        if flip == 'heads':
            self.scores[player.name] += 1
        # Update the player.
        player.tell('You now have {} heads.'.format(self.scores[player.name]))
        player.tell()


class FlipBot(Player):
    """
    A bot to play Flip against. (Player)

    Class Attributes:
    count_words: Words for the number of flips the bot requests. (list of str)

    Overridden Methods:
    ask
    tell
    """

    count_words = ['none', 'once', 'twice', 'three times']

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        flips = random.randint(1, 3)
        self.game.human.tell('{} chooses to flip {}.'.format(self.name, self.count_words[flips]))
        return str(flips)

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        if args:
            self.game.human.tell(args[0].replace('You', self.name).replace('have', 'has'))


class Fireball(Game):
    """
    A game of blowing things up. (Game)

    Overridden Methods:
    game_over
    handle_options
    player_turn
    """

    credits = '\nDesign and programming by Craig "Ichabod" O''Brien.'
    name = 'Fireball'
    num_options = 1
    rules = '\nPlay more games.'

    def game_over(self):
        """Declare the end of the game."""
        # Check for no games as a loss.
        if not self.scores[self.human.name]:
            self.win_loss_draw[1] = 1
            self.human.tell('\nPing.')
        # Skip play again and counting this game.
        self.human.held_inputs = ['n'] + self.human.held_inputs
        self.human.fire_index = len(self.human.results) + 1
        return True

    def handle_options(self):
        """Handle the specified game options. (None)"""
        # The one option is the target.
        if not self.raw_options:
            self.target = 'your target'
        else:
            self.target = self.raw_options
            self.option_set.settings_text = self.raw_options

    def player_action(self, player):
        """
        Determine the damage. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the dice parameters (end the game if there are no dice).
        fire_results = self.human.results[self.human.fire_index:]
        dice_count = len(fire_results)
        if not dice_count:
            return False
        sides = len(set(result[0] for result in fire_results)) * 2 + 2
        pool = dice.Pool([sides] * dice_count)
        # Get the bonus to the roll.
        all_categories = set()
        for result in fire_results:
            categories = self.interface.games[result[0].lower()].categories
            all_categories.add(tuple(categories))
        bonus = len(all_categories)
        # Get the damage.
        pool.roll()
        damage = sum(pool) + bonus
        self.human.tell('\nYou did {} {} of damage.'.format(damage, utility.plural(damage, 'point')))
        self.scores[self.human.name] = damage
        # Check for a win.
        expected = (sides / 2.0 + 0.5) * dice_count
        percent = damage / expected
        # Output results.
        if percent > 1:
            self.human.tell('You completely destroyed {}.'.format(self.target))
            self.win_loss_draw[0] = 1
        elif percent >= 0.95:
            self.human.tell('You almost destroyed {}.'.format(self.target))
            self.win_loss_draw[2] = 1
        else:
            self.human.tell('You failed to destroy {}.'.format(self.target))
            self.win_loss_draw[1] = 1


class Sorter(Game):
    """
    A test game of sorting a sequence. (Game)

    Attributes:
    length: The length of the sequences to sort. (int)
    minimum: The minimum number of swaps to sort the sequence. (int)
    sequence: The sequence to sort. (list of int)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_up
    """

    credits = '\nDesign and programming by Craig "Ichabod" O''Brien.'
    name = 'Sorter'
    num_options = 1
    rules = '\nEach turn, swap two numbers. If you can sort the list with a minimum of swaps, you win.'

    def game_over(self):
        """Check for the game being over. (bool)"""
        # Check for sorted sequences.
        if self.sequence == sorted(self.sequence):
            # Check if it is a win or a loss.
            if self.turns == self.minimum:
                self.win_loss_draw[0] = 1
                self.human.tell('You won!')
            else:
                self.win_loss_draw[1] = 1
                self.human.tell('You lost. The sequence could be sorted in {} swaps.'.format(self.minimum))
            # Set the score and end the game.
            self.scores[self.human.name] = self.minimum - self.turns
            return True

    def handle_options(self):
        """Set the length of the sequence to sort. (None)"""
        # Set the default options
        self.length = 5
        # If no options, ask for manual setting of options.
        if not self.raw_options.strip():
            self.raw_options = self.human.ask('Enter the length of the sequence to sort (return for 5): ')
        # Read any specified options
        if self.raw_options.isdigit():
            self.flags |= 1
            self.length = int(self.raw_options)

    def player_action(self, player):
        """
        Get two numbers to swap. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the move.
        player.tell('The current sequence is: ', str(self.sequence)[1:-1])
        move = player.ask('Pick two numbers to swap: ')
        # Parse the move.
        try:
            if ',' in move:
                numbers = [int(x) for x in move.split(',')]
            else:
                numbers = [int(x) for x in move.split()]
        except ValueError:
            # Handle invalid moves.
            return self.handle_cmd(move)
        # Make the move.
        spots = [self.sequence.index(x) for x in numbers]
        self.sequence[spots[0]], self.sequence[spots[1]] = self.sequence[spots[1]], self.sequence[spots[0]]

    def set_up(self):
        """Set up the sequence and minimum swaps. (None)"""
        # Set up the sequence to sort.
        self.sequence = list(range(self.length))
        while self.sequence == sorted(self.sequence):
            random.shuffle(self.sequence)
        # Determine the minimum number of swaps.
        self.minimum = 0
        check = self.sequence[:]
        for num_index, num in enumerate(check):
            if num_index != num:
                target_index = check.index(num_index)
                check[num_index], check[target_index] = check[target_index], check[num_index]
                self.minimum += 1


def load_games():
    """
    Load all of the games defined locally. (tuple of dict)

    The return value is two dictionaries. The first is game classes keyed to lower
    case game names and aliases. The second is tree of categories, each one with
    a dictionary of sub-categories and a list of games in that category.
    """
    # Find the Python game files.
    game_files = []
    base = '{0}{1}*{1}'.format(utility.LOC, os.sep)
    while True:
        new_files = glob.glob(base + '*_game.py')
        if new_files:
            game_files.extend(new_files)
            base += '*' + os.sep
        else:
            break
    # Import the Python files.
    for game_file in game_files:
        __import__(game_file[len(utility.LOC) - 7:-3].replace(os.sep, '.'))
    # Search through all of the game.Game sub-classes.
    categories = {'sub-categories': {}, 'games': []}
    games = {}
    search = [Game]
    while search:
        game_class = search.pop()
        # Store game by name.
        games[game_class.name.lower()] = game_class
        for alias in game_class.aka:
            games[alias.lower()] = game_class
        # Store game by category (except test games).
        category = categories
        if game_class.categories[0] != 'Test Games':
            # Go down the category chain, making new caetgories as needed.
            for game_category in game_class.categories:
                if game_category not in category['sub-categories']:
                    category['sub-categories'][game_category] = {'sub-categories': {}, 'games': []}
                category = category['sub-categories'][game_category]
            # Store the game in the terminal category.
            category['games'].append(game_class)
        # Search the full hierarchy of sub-classes.
        search.extend(game_class.__subclasses__())
    return games, categories


if __name__ == '__main__':
    # Run the unit testing.
    from t_tests.game_test import *
    unittest.main()
