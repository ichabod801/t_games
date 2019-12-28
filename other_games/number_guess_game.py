"""
number_guess_game.py

A classic number guessing game.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for the Number Guessing Game.
OPTIONS: The options for the Number Guessing Game.
RULES: The rules for the Number Guessing Game.

Classes:
GuessBot: A number guessing bot using a random strategy. (player.Bot)
GuessBotter: A number guessing bot using a binary search. (GuessBot)
NumberGuess: A classic number guessing game. (game.Game)
"""


import random

from .. import game
from .. import player
from .. import utility


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

OPTIONS = """
easy (e): Play against a random opponent.
gonzo (gz): Equivalent to 'high=1001'.
high= (h=): The highest possible secret number (defaults to 108).
low= (l=): The lowest possible secret number (defaults to 1).
"""

RULES = """
Each turn you guess a number chosen in secret by the computer. Then the
computer tries to guess a number you choose. Whoever guesses correctly with the
least number of guesses wins.
"""


class GuessBot(player.Bot):
    """
    A number guessing bot using a random strategy. (player.Bot)

    Attributes:
    high_guess: The highest guess the bot should make. (int)
    last_guess: The last guess the bot made. (int)
    low_guess: The lowest guess the bot should make. (int)

    Methods:
    guess: Guess a number.
    secret_number: Make a number to be guessed. (int)

    Overridden Methods:
    ask
    ask_int
    set_up
    tell
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        if prompt.startswith('Guess a number between'):
            self.last_guess = self.guess()
            return str(self.last_guess)

    def ask_int(self, prompt, **kwargs):
        """
        Get an integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        kwargs: The standard arguments to ask_int
        """
        if 'secret number' in prompt:
            return self.secret_number(kwargs['low'], kwargs['high'])
        else:
            return super(GuessBot, self).ask_int(prompt, **kwargs)

    def guess(self):
        """Guess a number. (int)"""
        return random.randint(self.low_guess, self.high_guess)

    def secret_number(self, low, high):
        """
        Make a number to be guessed. (int)

        Parameters:
        low: The lowest possible secret number. (int)
        high: The highest possible secret number. (int)
        """
        return random.randint(low, high)

    def set_up(self):
        """Set up the bot. (None)"""
        self.low_guess = self.game.low
        self.high_guess = self.game.high
        self.last_guess = None

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        if 'lower' in args[0]:
            self.low_guess = self.last_guess + 1
        elif 'higher' in args[0]:
            self.high_guess = self.last_guess - 1
        super(GuessBot, self).tell(*args, **kwargs)


class GuessBotter(GuessBot):
    """
    A number guessing bot using a binary search. (GuessBot)

    Overridden Methods:
    guess
    """

    def guess(self):
        """Guess a number. (int)"""
        # Use a binary search.
        guess = (self.high_guess - self.low_guess + 1) // 2 + self.low_guess
        # Fudge it early on to avoid predictability.
        if self.high_guess - self.low_guess > 10:
            guess += random.choice((-1, 0, 1))
        return guess

    def secret_number(self, low, high):
        """
        Make a number to be guessed. (int)

        Parameters:
        low: The lowest possible secret number. (int)
        high: The highest possible secret number. (int)
        """
        # Start in the middle, with fudging to avoid predictability.
        width = high - low + 1
        start = width // 2 + random.choice((-1, 0, 1))
        base = [low, start, high]
        # Run a binary search from there.
        while len(base) < width:
            next_row = []
            for first, second in zip(base, base[1:]):
                next_row.append((second - first + 1) // 2 + first)
            base = sorted(set(base + next_row))
        # Use of the last numbers that a binary search would find.
        return random.choice(next_row)


class NumberGuess(game.Game):
    """
    A classic number guessing game. (game.Game)

    Attributes:
    easy: A flag for easier game play. (bool)
    high: The highest possible secret number. (int)
    high_low: A flag for showing high/low information. (bool)
    info: The type of information to show the user. (str)
    last_guess: The user's last guess. (int or None)
    low: The lowest possible secret number. (int)
    number: The secret number. (int)
    phase: Whether the human is guessing or answering. (str)
    warm_cold: A flag for showing warm/cold information. (bool)

    Class Attributes:
    info_types: The translation of information given to information flags. (dict)

    Methods:
    do_guess: Guess the secret number. (bool)
    reset: Reset guess tracking. (None)

    Overridden Methods:
    default
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['NuGG', 'Guess a Number']
    categories = ['Other Games']
    credits = CREDITS
    info_types = {'high-low': (True, False), 'warm-cold': (False, True), 'both': (True, True)}
    name = 'Number Guessing Game'
    num_options = 3
    options = OPTIONS
    rules = RULES

    def default(self, line):
        """
        Handle unrecognized commands. (bool)

        Parameters:
        text: The raw text input by the user. (str)
        """
        try:
            guess = int(line)
        except ValueError:
            return super(NumberGuess, self).default(line)
        else:
            return self.do_guess(line)

    def do_gipf(self, arguments):
        """
        Canfield makes the game 'forget' your last guess. Ninety-nine tells you the
        remainder after dividing the secret number by 9.
        """
        # Run the edge, if possible.
        game, losses = self.gipf_check(arguments, ('canfield', 'ninety-nine'))
        # Winning Snakes and Ladders gets you a free spin.
        if game == 'canfield':
            if not losses:
                self.guesses -= 1
        elif game == 'ninety-nine':
            if not losses:
                self.human.tell('\nThe secret number modulo 9 is {}.'.format(self.number % 9))
        else:
            self.human.tell("\nGipf is inside the innermost possible secret number.")
        return True

    def do_guess(self, arguments):
        """
        Guess the secret number. (g)
        """
        player = self.players[self.player_index]
        # Check for integer input.
        try:
            guess = int(arguments)
        except ValueError:
            player.error('{!r} is not a valid integer.'.format(arguments))
        else:
            # Check that the input is in range.
            if guess < self.low:
                player.error('{} is below the lowest possible secret number.'.format(guess))
            elif guess > self.high:
                player.error('{} is above the highest possible secret number.'.format(guess))
            else:
                self.guesses += 1
                # Check the input against the secret number.
                if guess == self.number:
                    text = '{} is the secret number! You got it in {} guesses.'
                    player.tell(text.format(guess, self.guesses))
                    self.scores[player.name] = self.guesses
                    self.reset()
                    return False
                # Give high/low information, if allowed.
                if self.high_low:
                    if guess < self.number:
                        player.tell('{} is lower than the secret number.'.format(guess))
                    elif guess > self.number:
                        player.tell('{} is higher than the secret number.'.format(guess))
                # Give warm/cold information, if allowed.
                if self.warm_cold:
                    if self.last_guess is None:
                        # Give initial distance as a temperature.
                        close = abs(guess - self.number) / (self.high - self.low + 1.0)
                        if close < 0.05:
                            player.tell('You are hot.')
                        elif close < 0.25:
                            player.tell('You are warm.')
                        elif close < 0.95:
                            player.tell('You are cold.')
                        else:
                            player.tell('You are frozen.')
                    else:
                        # Give warmer/colder information.
                        distance = abs(guess - self.number)
                        last_distance = abs(self.last_guess - self.number)
                        if distance < last_distance:
                            player.tell('Warmer.')
                        elif distance > last_distance:
                            player.tell('Colder.')
                        else:
                            player.tell('No change in temperature.')
                self.last_guess = guess
        return True

    def game_over(self):
        """Determine if the game is finished or not. (bool)"""
        # Finish after each person guesses correctly.
        if self.turns == 2:
            if self.scores[self.human.name] < self.scores[self.bot.name]:
                text = 'You won, {0} guesses to {1}.'
                self.win_loss_draw[0] = 1
            elif self.scores[self.human.name] > self.scores[self.bot.name]:
                text = 'You lost, {0} guesses to {1}.'
                self.win_loss_draw[1] = 1
            else:
                text = 'It was a tie, with {0} guesses each.'
                self.win_loss_draw[2] = 1
            self.human.tell(text.format(self.scores[self.human.name], self.scores[self.bot.name]))
            return True
        else:
            return False

    def handle_options(self):
        """Process the option settings for the game. (None)"""
        super(NumberGuess, self).handle_options()
        # Check the range settings.
        if self.high == self.low:
            self.human.tell('\nThe high option must be different than the low option.')
            self.option_set.errors.append('Invalid range specified.')
        elif self.high < self.low:
            self.human.tell('\nThe range was entered backward and has been reversed.')
            self.low, self.high = self.high, self.low
        # Set the computer opponent.
        if self.easy:
            self.bot = GuessBot(taken_names = [self.human.name])
        else:
            self.bot = GuessBotter(taken_names = [self.human.name])
        self.players = [self.human, self.bot]
        # Set the information flags.
        #self.high_low, self.warm_cold = self.info_types[self.info]
        self.high_low, self.warm_cold = True, False

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Give the number of guesses.
        guess_text = utility.number_plural(self.guesses, 'guess', 'guesses')
        player.tell('\nYou have made {} so far.'.format(guess_text))
        # Get the secret number, if it hasn't been defined yet.
        if self.number is None:
            foe = self.players[1 - self.player_index]
            query = 'What do you want the secret number to be? '
            self.number = foe.ask_int(query, low = self.low, high = self.high, cmd = False)
        # Handle the player's move.
        query = 'Guess a number between {} and {}: '.format(self.low, self.high)
        return self.handle_cmd(player.ask(query))

    def reset(self):
        """Reset guess tracking. (None)"""
        self.number = None
        self.last_guess = None
        self.guesses = 0

    def set_options(self):
        """Set the options for the game. (None)"""
        self.option_set.add_option('easy', ['e'], question = 'Do you want to play in easy mode? bool')
        """self.option_set.add_option('info', ['i'], valid = ('high-low', 'warm-cold', 'both'),
            question = 'What information should you get (high-low (default), warm-cold, or both)? ')"""
        self.option_set.add_option('low', ['l'], int, 1,
            question = 'What should the lowest possible number be (return for 1)? ')
        self.option_set.add_option('high', ['h'], int, 108,
            question = 'What should the highest possible number be (return for 108)? ')
        self.option_set.add_group('gonzo', ['gz'], 'high=1001')

    def set_up(self):
        """Set up the game. (None)"""
        self.reset()
