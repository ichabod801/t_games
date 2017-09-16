"""
solitaire_dice_game.py

A game of solitaire dice.

Constants:
CREDITS: The credits for the game and the programming. (str)
RULES: The rules of Solitaire Dice. (str)
SUM_LEADS: Text used in displaying the scores. (list of str)
SUM_VALUES: The scoring for each possible sum. (list of int)
"""


import re

import tgames.dice as dice
import tgames.game as game


# The credits for the game and the programming.
CREDITS = """
Game Design: Sid Sackson
Game Programming: Craig O'Brien
"""

# The rules of Solitaire Dice.
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
and 10 score 60, 5 and 9 score 50, 6 and 8 score 40, and 7 scores 30.

Any score under 0 is recorded as a loss, any non-negative score up to 500 is
recorded as a draw, and any score over 500 is recorded as a win.

Note that when you type in your discard, you can type in three numbers instead
of one. The second and third numbers are assumed to be your split. This allows
you to enter your discard and your split at the same time.
"""

# Text used in displaying the scores.
SUM_LEADS = ['Pts   Sum Count', '---   --- -----', '(100)  2:', ' (70)  3:',
    ' (60)  4:', ' (50)  5:', ' (40)  6:', ' (30)  7:', ' (40)  8:',
    ' (50)  9:', ' (60) 10:', ' (70) 11:', '(100) 12:']

# The scoring for each possible sum.
SUM_VALUES = [0, 0, 100, 70, 60, 50, 40, 30, 40, 50, 60, 70, 100]


class SolitaireDice(game.Game):
    """
    A game of Solitaire Dice. (game.Game)

    Attributes:
    die: The die that is rolled. (dice.Die)
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
    update_score: Update the game score. (None)

    Overridden Methods:
    set_up
    game_over
    player_turn
    """

    aka = ['SoDi']
    categories = ['Dice Games', 'Other']
    credits = CREDITS
    name = 'Solitaire Dice'
    rules = RULES
    two_numbers_re = re.compile('([123456]).*?([123456])')
    three_numbers_re = re.compile('([123456]).*?([123456]).*?([123456])')

    def discard_mode(self, player):
        """
        Discard a die. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Determine what can be discarded.
        if len(self.discards) == 3:
            allowed_discards = [d for d in self.discards if d in self.roll]
            # Check for a free ride.
            if not allowed_discards or self.free_free:
                player.tell('Free ride! You may discard any die you want.')
                allowed_discards = set(self.roll)
        else:
            allowed_discards = set(self.roll)
        # Get the required/requested discard.
        if len(allowed_discards) == 1:
            discard = str(list(allowed_discards)[0])
            self.message += '\nYou must discard a {}.'.format(discard)
        else:
            discard = player.ask('Which number would you like to discard? ')
        # Check for discard and split.
        split_check = self.three_numbers_re.match(discard.strip())
        if split_check:
            discard = split_check.groups()[0]
            self.held_split = ' '.join(split_check.groups()[1:])
        else:
            self.held_split = ''
        # Handle the discard.
        if discard.strip().isdigit():
            discard = int(discard)
            # Check for discard being rolled.
            if discard not in self.roll:
                self.message += 'You did not roll a {}, so you cannot discard it.'.format(discard)
                return False
            # Check for invalid discard.
            elif discard not in allowed_discards:
                self.message += '\n{} is an invalid discard.'.format(discard)
                self.message += '\nYou must discard one of {}.'.format(str(allowed_discards)[1:-1])
                return False
            # Process valid discards (don't store free rides).
            if len(self.discards) < 3 or discard in self.discards:
                self.discards[discard] = self.discards.get(discard, 0) + 1
            self.roll.remove(discard)
            self.free_free = False
            self.mode = 'split'
        # Handle other commands.
        else:
            return self.handle_cmd(discard)

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        game, losses = self.gipf_check(arguments, ('freecell',))
        if game == 'freecell':
            if not losses:
                self.free_free = True
        else:
            self.human.tell("I don't understand.")

    def game_over(self):
        """Check for any number being discarded 8 times. (bool)"""
        if self.mode == 'roll' and max(self.discards.values()) == 8:
            score = self.scores[self.human.name]
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

    def player_turn(self, player):
        """
        Roll, discard, and choose two pairs. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        player.tell()
        # Roll five dice.
        if self.mode == 'roll':
            self.roll_mode(player)
        self.show_status(player)
        # Discard one die.
        if self.mode == 'discard':
            if not self.discard_mode(player):
                return False
        # Split into pairs.
        if self.mode == 'split':
            if not self.split_mode(player):
                return False

    def roll_mode(self, player):
        """
        Roll the dice. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Roll the dice.
        self.roll = [self.die.roll() for die in range(5)]
        self.roll.sort()
        # Set tracking variables.
        self.mode = 'discard'
        self.message = ''

    def set_up(self):
        """Set up the game. (None)"""
        self.die = dice.Die()
        self.totals = [0] * 13
        self.discards = {}
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
        for value in self.discards:
            player.tell('{}: {}'.format(value, self.discards[value]))
        # show score
        player.tell('\nYour current score is {}.'.format(self.scores[player.name]))
        # show message
        if self.message:
            player.tell(self.message.strip())
            self.message = ''
        # show roll
        player.tell('Your roll is:', ', '.join([str(x) for x in self.roll]))

    def split_mode(self, player):
        """
        Choose two pairs of dice. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Get the requested split.
        if self.held_split:
            split = self.held_split
            self.held_split = ''
        else:
            split = player.ask('Choose two numbers to make a pair: ')
        # Check for a valid split.
        split_check = self.two_numbers_re.match(split.strip())
        if split_check:
            split = [int(die) for die in split_check.groups()]
            if split[0] == split[1]:
                in_check = self.roll.count(split[0]) >= 2
            else:
                in_check = split[0] in self.roll and split[1] in self.roll
            if not in_check:
                self.message += '\nYou did not roll both those numbers.'
                return False
            # Handle a valid split
            self.totals[sum(split)] += 1
            self.roll.remove(split[0])
            self.roll.remove(split[1])
            self.totals[sum(self.roll)] += 1
            self.update_score(player, split)
            self.mode = 'roll'
        else:
            return self.handle_cmd(split)

    def update_score(self, player, split):
        """
        Update the game score. (None)

        Parameters:
        player: The player whose turn it is. (Player)
        split: One pair from the recent split. (list of int)
        """
        score = 0
        for total, value in zip(self.totals, SUM_VALUES):
            if 0 < total < 5:
                score -= 200
            elif total:
                score += (min(total, 10) - 5) * value
        self.scores[player.name] = score


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    sodi = SolitaireDice(player.Player(name), '')
    sodi.play()
