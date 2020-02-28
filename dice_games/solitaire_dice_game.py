"""
solitaire_dice_game.py

A game of solitaire dice.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for the game and the programming. (str)
RULES: The rules of Solitaire Dice. (str)
SUM_LEADS: Text used in displaying the scores. (list of str)
SUM_VALUES: The scoring for each possible sum. (list of int)

Classes:
SolitaireDice: A game of Solitaire Dice. (game.Game)
"""


import collections
import re

from .. import dice
from .. import game


CREDITS = """
Game Design: Sid Sackson
Game Programming: Craig O'Brien
"""

RULES = """
Each turn you roll five dice. You discard one die, and split the other four
into two pairs. You sum the two pairs, and keep a record of how many times
each total is rolled.

You can only discard three different numbers. Once you discard three different
numbers, you cannot discard any other numbers unless you didn't roll any of
the three numbers you had already discarded. Once you have discarded any
single number eight times, the game is over.

If a total has been rolled zero OR five times, it scores nothing. If it has
been rolled one to four times, it scores -200 points. If it has been rolled
six to ten times, it scores the number of times it's been rolled over five
times a value based on the total: 2 and 12 score 100, 3 and 11 score 70, 4
and 10 score 60, 5 and 9 score 50, 6 and 8 score 40, and 7 scores 30. Rolling a
total eleven or more times results in the same score as rolling it ten times.

Any score under 0 is recorded as a loss, any non-negative score up to 500 is
recorded as a draw, and any score over 500 is recorded as a win.
"""

SUM_LEADS = ['Pts   Sum Count', '---   --- -----', '(100)  2:', ' (70)  3:',
    ' (60)  4:', ' (50)  5:', ' (40)  6:', ' (30)  7:', ' (40)  8:',
    ' (50)  9:', ' (60) 10:', ' (70) 11:', '(100) 12:']

SUM_VALUES = [0, 0, 100, 70, 60, 50, 40, 30, 40, 50, 60, 70, 100]


class SolitaireDice(game.Game):
    """
    A game of Solitaire Dice. (game.Game)

    Attributes:
    dice: The dice that are rolled. (dice.Pool)
    discards: The numbers discarded and how many times. (dict of int: int)
    free_free: A flag for a 'free' free ride. (bool)
    message: A message to show the user in show_status. (str)
    mode: Where we are in the player's turn. (str)
    roll: The current roll. (list of int)
    totals: The number of times each total has been rolled. (list of int)

    Methods:
    discard_mode: Discard a die. (bool)
    roll_mode: Roll the dice. (bool)
    show_status: Show the current game state. (None)
    split_mode: Choose a pair of dice. (bool)
    update_score: Update the game score. (None)

    Overridden Methods:
    game_over
    player_action
    set_up
    """

    aka = ['SoDi']
    categories = ['Dice Games']
    credits = CREDITS
    name = 'Solitaire Dice'
    rules = RULES

    def discard_mode(self, player):
        """
        Discard a die. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Determine what can be discarded.
        if len(self.discards) == 3:
            allowed_discards = [d for d in self.discards if d in self.dice]
            # Check for a free ride.
            if not allowed_discards or self.free_free:
                player.tell('Free ride! You may discard any die you want.')
                allowed_discards = self.dice
                self.free_free = False
        else:
            allowed_discards = self.dice
        # Get the required/requested discard.
        if len(allowed_discards) == 1:
            discard = allowed_discards.pop()
            self.message += '\nYou must discard a {}.'.format(discard)
        else:
            discard = player.ask_int('Which number would you like to discard? ', valid = allowed_discards)
        if isinstance(discard, int):
            # Process valid discards (don't store free rides).
            if len(self.discards) < 3 or discard in self.discards:
                self.discards[discard] += 1
            self.dice.hold(discard)
            self.mode = 'split'
        else:
            return self.handle_cmd(discard)

    def do_gipf(self, arguments):
        """
        Freecell gives you a free ride.

        Gargantua lets you change one die into a six.
        """
        game, losses = self.gipf_check(arguments, ('freecell', 'gargantua'))
        # Freecell gives you a free ride no matter what the roll is.
        if game == 'freecell':
            if not losses:
                self.free_free = True
        # Gargantua lets you change one die to a six.
        elif game == 'gargantua':
            if not losses:
                self.human.tell('Your roll is: {}.', self.dice)
                query = 'Which value would you like to change to a six? '
                to_six = self.human.ask_int(query, valid = self.dice)
                to_change = self.dice.index(to_six)
                self.dice[to_change].value = 6
                return True
        # Otherwise I'm confused.
        else:
            self.human.tell("I don't understand.")

    def game_over(self):
        """Check for any number being discarded 8 times. (bool)"""
        if self.mode == 'roll' and max(self.discards.values()) == 8:
            score = self.scores[self.human]
            # Win
            if score < 0:
                self.human.tell('You lost with {} points. :('.format(score))
                self.win_loss_draw[1] = 1
            # Loss
            elif score <= 500:
                self.human.tell('You drew with {} points. :|'.format(score))
                self.win_loss_draw[2] = 1
            # Draw
            else:
                self.human.tell('You won with {} points! :)'.format(score))
                self.win_loss_draw[0] = 1
            return True

    def player_action(self, player):
        """
        Roll, discard, and choose two pairs. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Roll five dice.
        if self.mode == 'roll':
            self.roll_mode(player)
        self.show_status(player)
        # Discard one die.
        if self.mode == 'discard':
            return self.discard_mode(player)
        # Split into pairs.
        if self.mode == 'split':
            return self.split_mode(player)

    def roll_mode(self, player):
        """
        Roll the dice. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Roll the dice.
        self.dice.release()
        self.dice.roll()
        self.dice.sort()
        # Set tracking variables.
        self.mode = 'discard'
        self.message = ''

    def set_options(self):
        """Set the possible options for the game. (None)"""
        # Add a dummy option group.
        self.option_set.add_group('gonzo', ['gz'], '')

    def set_up(self):
        """Set up the game. (None)"""
        self.dice = dice.Pool([6] * 5)
        self.totals = [0] * 13
        self.discards = collections.defaultdict(int)
        self.free_free = False
        self.mode = 'roll'

    def show_status(self, player):
        """
        Show the current game state. (None)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # show sums
        player.tell()
        player.tell('SUMS:')
        for line in range(13):
            player.tell(SUM_LEADS[line], end = ' ')
            if SUM_VALUES[line] and self.totals[line]:
                player.tell(self.totals[line])
            else:
                player.tell()
        # show discards
        player.tell('\nDISCARDS:')
        player.tell('#  Count')
        player.tell('-- -----')
        for value in sorted(self.discards.items()):
            player.tell('{}: {}'.format(*value))
        # show score
        player.tell('\nYour current score is {}.'.format(self.scores[player]))
        # show message
        if self.message:
            player.tell(self.message.strip())
            self.message = ''
        # show roll
        player.tell('Your roll is: {}.'.format(self.dice))

    def split_mode(self, player):
        """
        Choose two pairs of dice. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the split
        prompt = 'Choose two numbers to make a pair: '
        split = player.ask_int_list(prompt, valid = self.dice, valid_lens = [2])
        if isinstance(split, list):
            # Handle a valid split
            self.totals[sum(split)] += 1
            self.dice.hold(split[0])
            self.dice.hold(split[1])
            self.totals[sum(self.dice.get_free())] += 1
            self.update_score(player, split)
            self.mode = 'roll'
        else:
            # Handle other commands
            return self.handle_cmd(split)

    def update_score(self, player, split):
        """
        Update the game score. (None)

        Parameters:
        player: The player whose turn it is. (Player)
        split: One pair from the recent split. (list of int)
        """
        # Update the whole score from scratch, total by total.
        score = 0
        for total, value in zip(self.totals, SUM_VALUES):
            if 0 < total < 5:
                score -= 200
            elif total:
                score += (min(total, 10) - 5) * value
        self.scores[player] = score
