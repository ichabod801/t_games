"""
game.py

The base game object for tgames.

Classes:
Game: A game with a text interface. (OtherCmd)
Flip: A test game of flipping coins. (Game)
Sorter: A test game of sorting a sequence. (Game)

Functions:
load_games: Load all of the games defined locally. (tuple of dict)
"""


from __future__ import print_function

import glob
import itertools
import math
import operator
import os
import random

from tgames.other_cmd import OtherCmd
from tgames.player import Player
import tgames.utility as utility


class Game(OtherCmd):
    """
    A game with a text interface. (OtherCmd)

    In non-solitaire games, the players attribute should be set in handle_options.

    The flags attribute represents a bunch of binary flags:
        1: Options were set by the player.
        2: The debug command was used by the player.
        4: The game was lost via the quit command.
        8: The gipf command was used in this game.
        16: This game was started by the gipf command.

    Class Attributes:
    aka: Other names for the game. (list of str)
    credits: The design and programming credits for this game. (str)
    categories: The categories of the game. (list of str)
    help: The help text for the game. (dict of str: str)
    name: The primary name of the game. (str)
    rules_text: The rules of the game. (str)

    Attributes:
    flags: Flags for different game events tracked in the results. (int)
    force_end: How to force the end of the game. (str)
    human: The primary player of the game. (Player)
    raw_options: The options as given by the play command. (str)
    scores: The players' scores in the game. (dict of str: int)
    turns: The number of turns played in the game. (int)
    win_loss_draw: A list of the player's results in the game. (list of int)

    Methods:
    clean_up: Handle any end of game tasks. (None)
    do_credits: Show the credits. (bool)
    do_help: Show the help text for a given area. (bool)
    do_quit: Quit the game, which counts as a loss. (bool)
    do_rpn: Process reverse Polish notation statements to do calculations. (None)
    do_rules: Show the rules text. (bool)
    game_over: Check for the end of the game. (bool)
    handle_options: Handle game options and set the player list. (None)
    play: Play the game. (list of int)
    player_turn: Handle a player's turn or other player actions. (bool)
    set_up: Handle any pre-game tasks. (None)
    tournament: Run a tournament of the game. (dict)

    Overridden Methods:
    __init__
    do_debug
    """

    aka = []
    categories = ['Test Games', 'Solitaire']
    credits = 'No credits have been specified for this game.'
    help = {}
    name = 'Null'
    # The operators used by rpn.
    operators = {'|': (abs, 1), '+': (operator.add, 2), 'C': (utility.choose, 2), '/%': (divmod, 2), 
        '!': (math.factorial, 1), '//': (operator.floordiv, 2), '*': (operator.mul, 2), 
        '%': (operator.mod, 2), '+-': (operator.neg, 1), 'P': (utility.permutations, 2), '^': (pow, 2), 
        '1/': (lambda x: 1 / x, 1), '-': (operator.sub, 2), '/': (operator.truediv, 2), 
        'ab/c': (lambda a, b, c: a + b / c, 3), 'cos': (math.cos, 1), 'ln': (math.log, 1), 
        'log': (math.log10, 1), 'R': (random.random, 0), 'F': (utility.flip, 0), 'sin': (math.sin, 1), 
        'V': (math.sqrt, 1), 'tan': (math.tan, 1)}
    rules = 'No rules have been specified for this game.'

    def __init__(self, human, options, interface = None):
        """Set up the game. (None)"""
        self.human = human
        self.interface = interface
        self.raw_options = options.strip()
        self.flags = 0
        self.handle_options()
        if not hasattr(self, 'players'):
            self.players = [self.human]
        for player in self.players:
            player.game = self
        self.gipfed = []

    def clean_up(self):
        """Handle any end of game tasks. (None)"""
        pass

    def do_credits(self, arguments):
        """
        Show the credits. (bool)

        Parameters:
        arguments: This parameter is ignored. (str)
        """
        self.human.tell(self.credits)
        return True

    def do_debug(self, arguments):
        """
        Handle debugging commands. (bool)

        Parameters:
        arguments: The debugging information needed. (str)
        """
        self.flags |= 2
        return super(Game, self).do_debug(arguments)

    def do_help(self, arguments):
        """
        Show the help text for a given area. (bool)

        Parameter:
        arguments: The area to get help on. (str)
        """
        if arguments.lower() in self.help:
            self.human.tell(self.help[arguments.lower()])
        else:
            self.human.tell("I can't help you with that.")
        return True

    def do_quit(self, arguments):
        """
        Quit the game, which counts as a loss. (bool)

        Parameters:
        arguments: This parameter is ignored. (str)
        """
        self.flags |= 4
        self.force_end = 'loss'
        self.win_loss_draw = [0, max(len(self.players) - 1, 1), 0]
        return False

    def do_rpn(self, arguments):
        """
        Process reverse Polish notation statements to do calculations. (None)

        Parameters:
        arguments: The calculation to process. (str)
        """
        # Process reverse Polish notation.
        stack = []
        for word in arguments.split():
            # handle operators
            if word in self.operators:
                # process operator
                op, n_params = self.operators[word]
                params = stack[-n_params:]
                stack = stack[:-n_params]
                result = op(*params)
                # add to stack
                if isinstance(result, tuple):
                    stack.extend(result)
                else:
                    stack.append(result)
            # handle integers
            elif word.isdigit():
                stack.append(int(word))
            # handle decimals
            elif self.float_re.match(word):
                stack.append(float(word))
            # handle garbage
            else:
                self.human.tell('Invalid RPN expression.')
        # Display the stack.
        self.human.tell(' '.join([str(x) for x in stack]))
        return True

    def do_rules(self, arguments):
        """
        Show the rules text. (bool)

        Parameters:
        arguments: This parameter is ignored. (str)
        """
        self.human.tell(self.rules)
        return True

    def do_xyzzy(self, arguments):
        """
        Nothing happens. (bool)

        Parameters:
        arguments: What doesn't happen. (str)
        """
        if self.interface.valve.blow(self):
            game_class = random.choice(list(self.interface.games.values()))
            game = game_class(self.human, 'none', self.interface)
            self.flags |= 32
            self.human.tell('\nPoof!')
            self.human.tell('You are now playing {}.\n'.format(game.name))
            results = game.play()
            results[4] |= 64
            self.human.store_results(game.name, results)
            if results[1] == 0:
                self.flags |= 128
                self.force_end = 'win'
                self.win_loss_draw = [max(len(self.players) - 1, 1), 0, 0]
                self.human.tell('\nThe incantation is complete. You win at {}.\n'.format(self.name))
                go = False
            else:
                go = True
        else:
            self.human.tell('Nothing happens.')
            go = True
        return go

    def game_over(self):
        """Check for the end of the game. (bool)"""
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
        self.flags |= 8
        games = {game_name: self.interface.games[game_name] for game_name in game_names}
        aliases = {}
        for game_name in game_names:
            aliases[game_name] = [alias.lower() for alias in games[game_name].aliases] + [game_name]
        for game_name in game_names:
            if argument in aliases[game_name] and game_name not in self.gipfed:
                self.gipfed.append(game_name)
                game = games[game_name](self.human, 'none', self.interface)
                results = game.play()
                results[4] |= 16
                self.human.store_results(game.name, results)
                return game_name, results[1]
        return 'invalid-game', 1 

    def handle_options(self):
        """Handle game options and set the player list. (None)"""
        pass

    def play(self):
        """
        Play the game. (list of int)

        The return value is the win, loss, draw, and score for the primary player.
        The win/loss/draw is per player for one game. So if you tie for second 
        with five players, your win/loss/draw is 2, 1, 1.
        """
        # Set up the game.
        self.scores = {player.name: 0 for player in self.players}
        self.win_loss_draw = [0, 0, 0]
        self.turns = 0
        self.force_end = ''
        self.flags &= 1 # reset everything but the options flag.
        self.set_up()
        # Loop through the players repeatedly.
        for player in itertools.cycle(self.players):
            # Loop through player actions until their turn is done.
            while self.player_turn(player):
                pass
            # Update tracking.
            self.turns += 1
            # Check for the end of game.
            if self.force_end or self.game_over():
                break
        # Clean up the game.
        self.clean_up()
        self.gipfed = []
        # Report the results.
        return self.win_loss_draw + [self.scores[self.human.name], self.flags]

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        The return value is a flag for the player's turn being done.

        Parameters:
        player: The player whose turn it is. (Player)
        """
        move = player.ask('What is your move, {}? '.format(player.name))

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
        # Set up the players.
        self.players = players
        for player in self.players:
            player.game = self
        # Set one of the players to be the human.
        human_hold = self.human
        self.human = self.players[0]
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
        # Clean up.
        self.human = human_hold
        return {'scores': score_tracking, 'places': place_tracking}


class Flip(Game):
    """
    A test game of flipping coins. (Game)

    Attributes:
    bot: The non-human player. (FlipBot)

    Overridden Methods:
    game_over
    player_turn
    set_up
    """

    categories = ['Test Games', 'Multi-Player']
    credits = 'Design and programming by Craig "Ichabod" O''Brien'
    name = 'Flip'
    rules = 'Whoever gets two more heads than their opponent wins.'

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
                return True

    def player_turn(self, player):
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
        print()


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
        print('{} chooses to flip {}.'.format(self.name, self.count_words[flips]))
        return str(flips)

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        if args:
            print(args[0].replace('You', self.name).replace('have', 'has'))


class Sorter(Game):
    """
    A test game of sorting a sequence. (Game)

    Attributes:
    length: The length of the sequences to sort. (int)
    minimum: The minimum number of swaps to sort the sequence. (int)
    sequence: The sequence to sort. (list of int)

    Overridden Methods:
    handle_options
    player_turn
    set_up
    """

    credits = 'Design and programming by Craig "Ichabod" O''Brien.'
    name = 'Sorter'
    rules = 'Each turn, swap two numbers. If you can sort the list with a minimum of swaps, you win.'

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

    def player_turn(self, player):
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
        ndxs = [self.sequence.index(x) for x in numbers]
        self.sequence[ndxs[0]], self.sequence[ndxs[1]] = self.sequence[ndxs[1]], self.sequence[ndxs[0]]

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
    base = '*/'
    while True:
        new_files = glob.glob(base + '*_game.py')
        if new_files:
            game_files.extend(new_files)
            base += '*/'
        else:
            break
    # Import the Python files.
    for game_file in game_files:
        __import__(game_file.replace(os.sep, '.')[:-3])
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
            for game_category in game_class.categories:
                if game_category not in category['sub-categories']:
                    category['sub-categories'][game_category] = {'sub-categories': {}, 'games': []}
                category = category['sub-categories'][game_category]
            category['games'].append(game_class)
        # Search the full hierarchy of sub-classes.
        search.extend(game_class.__subclasses__())
    return games, categories


if __name__ == '__main__':
    craig = Player('Craig')
    game = Game(craig, '')
    result = game.play()
    print(result)
    flip = Flip(Player('Ref'), '')
    bots = [FlipBot('Flip'), FlipBot('Tosser')]
    t_result = flip.tournament(bots, 10)
    print(t_result)