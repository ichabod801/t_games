"""
roulette_game.py

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Roulette. (str)
HOUSE_HELP: Help text for the house edge. (str)
OPTIONS: The options for Roulette. (str)
RULES: The rules of Roulette. (str)

Classes:
Roulette: A game of roulette. (game.Game)
"""


import random
import re
import time

from .. import game
from .. import utility


CREDITS = """
Game Design: Traditional (French monks)
Game Programming: Craig "Ichabod" O'Brien
"""

HOUSE_HELP = """
The house edge for all bets is 5.26% for the American layout and 2.70% for the
French layout. The one exception is the top line bet on the American layout,
which has a house edge of 7.89%.
"""

OPTIONS = """
american (a): Use the American layout (the default).
french (f): Use the French layout.
gonzo (gz): Equvalent to 'limit=1000 uk-rule'.
limit= (l=): The maximum bet for any single bet, defaults to 10.
stake= (s=): How much money you start with, defaults to 100.
uk-rule (uk): Outside bets on half the numbers only lose half the bet.
"""

RULES = """
You may make one or more bets on the numbers 0-36 (and 00 depending on the
layout). One of the numbers is chosen at random, and bets including that
number are paid out. Traditionally the number is chosen by spinning a small
wheel (the literal translation of roulette) with a pocket for each number, and
rolling a ball into a bowl with the wheel at the bottom.

Bets are typically made with a command, a number or set of numbers separated
by dashes, and the ammount bet. Payouts are made based on the number of
numbers bet on, assuming the zeroes do not exist (the zeros give the house
its edge). There are inside bets on individual numbers or groups of numbers
based on a layout of the numbers in three columns. There are outside bets
based on the features of the number, including high/low, even/odd and red/
black (each number has a color, with the zeroes being green). There are also
called bets that are groups of other bets. Once all of your bets are placed,
use the spin command to spin the wheel to detrmine the winning number.

The bets are listed below. The number in brackets is the number of numbers
that must be specified for the bet. Bets with a capital F in the brackets may
only be made on the French layout, and bets with a capital A may only be made
on the American layout (see options).

Your score in the results and statistics will be how much money you won
(positive) or lost (negative). This means you can calcuate your total winnings
or losses by multiplying you average score times the number of games you have
played.

INSIDE BETS:
Basket/First Four: A bet on the first two rows of numbers (0, 1, 2, 3). [0F]
Corner/Square: Bet on four numbers in a square. Specify the highest and lowest
    numbers in the square. [2]
Double Street/Six Line: Bet on six numbers that form two rows. Specify the
    first number of the first row and the last number of the second row. [2]
Split: Bet on two numbers that are adjacent on the board. [2]
Straight/Single: Bet on one number. [1]
Street: Bet on a three number row. Specify the last number in the row. [1]
Top Line: Bet on the first two rowns of the American layout. (0-3 and 00) [0]
Trio: Bet on three adjacent numbers, including at least one zero. [3]

OUTSIDE BETS:
Black/Noir: Bet on the black numbers. [0]
Column: Bet on a column of 12 numbers. The column can be specified with 1/2/3,
    P/M/D (Premiere, Moyenne, Derniere) or F/S/T (First, Second, Third). [1]
Dozen: Bet on the first, second, or third dozen. Use 1/2/3, P/M/D, or F/S/T
    to specify the dozen (see column bet). [1]
Even/Pair: Bet on the even numbers. [0]
High/19-36: Bet on the high numbers (over 18). [0]
Low/1-18: Bet on the low numbers (18 and under). [0]
Odd/Impair: Bet on the odd numbers. [0]
Red/Rouge: Bet on the red numbers. [0]

CALLED BETS:
Complete: Make every inside bet that contains the specified number. May be
    done as 'complete progressive,' which multiplies each bet by the number
    of numbers in the bet. [1]
Final/Finals/Finale: Bet on all non-zero numbers ending with the specified
    digit. [1]
Neighbors of Zero/Voisins du Zero: Nine bets covering 17 numbers around zero
    on the French layout. [0F]
Neighbors: The neighbors bet with a number specified bets on that number and
    the two numbers on either side on the wheel. [1]
Niner: Bet on a number and the four numbers on either side on the wheel. [1]
Orphans: Bet on numbers not in Neighbors of Zero or Third of the Wheel. [0F]
Prime: Bet on the prime numbers. Twins can be used to exclude 2 and 23. [0]
Seven: Bet on a number and the three numbers on either side on the wheel. [1]
Snake: A bet on the zig-zag of red numbers from 1 to 34. [0]
Third of the Wheel/Le Tiers du Cylindre: Bet on a specific third of the wheel
    on the French layout. If made with '5-8-10-11', those numbers are doubled
    up. If made with 'gioco Ferrari', 8, 11, 12, and 30 are doubled up. [0F]
Zero Game/Zero Spiel/Jeu Zero: Bet on zero and six numbers near it on the
    French layout. [0F]

OTHER COMMANDS:
Bets: Show a numbered list of the current bets.
Layout: Show the current layout, with colors marked.
Remove: Remove a bet, using the number from the bets command.
"""


class Roulette(game.Game):
    """
    A game of roulette.

    Class Attributes:
    american: The order of the wheel in the American layout. (list of str)
    black: The black numbers. (list of str)
    french: The order of the wheel in the French layout. (list of str)
    int_re: A regular expression to capture numbers. (re.SRE_Pattern)
    red: The red numbers. (list of str)

    Attributes
    bets: Bets made this round. (list of tuple)
    forced_spin: The numbers the next spin must come from. (list of str)
    layout: American or French layout. (str)
    max_bet: The maximum allowed bet. (int)
    numbers: The numbers on the wheel. (list of str)
    stake: The starting money the player gets. (int)
    uk_rule: A flag for getting half back on losing 1:1 bets. (bool)

    Methods:
    check_bet: Do common checking for valid bets. (str, int)
    check_two_numbers: Check for two numbers in the layout. (bool)
    complete_corners: Get all corner bets for a complete bet. (list of tuple)
    complete_splits: Get all split bets for a complete bet. (list of tuple)
    complete_streets: Get all street and double street bets for a complete bet. (list)
    complete_zero: Get all 0 and 00 related bets for a complete bet. (list of tuple)
    do_basket: Make a four number bet incluidng 0. (bool)
    do_bets: Show a numbered list of the current bets. (bool)
    do_black: Bet on black. (bool)
    do_column: Bet on a column. (bool)
    do_complete: Make all inside bets on a given number. (bool)
    do_corner: Make a bet on a square of numbers. (bool)
    do_double: Make a bet on two consecutive rows of numbers. (bool)
    do_dozen: Bet on a consecutive dozen. (bool)
    do_even: Bet on the the even numbers. (bool)
    do_final: Bet on numbers ending with a specified digit. (bool)
    do_high: Bet on the the high half of the range. (bool)
    do_layout: Show the current layout. (bool)
    do_low: Bet on the the low half of the range. (bool)
    do_neighbors: Make a neighbors of zero bet or a and-the-neighbors bet. (bool)
    do_niner: Make a bet on a neighborhood of nine. (bool)
    do_odd: Bet on the odd numbers. (bool)
    do_orphans: Bet on the orphans: the numbers not in neighbors or thirds. (bool)
    do_prime: Make a bet on all but two prime numbers. (bool)
    do_red: Make a bet on the red numbers. (bool)
    do_remove: Remove a bet. (bool)
    do_seven: Make a bet on a neighborhood of seven. (bool)
    do_snake: Zig zag bet from 1 to 34. (bool)
    do_spin: Spin the wheel. (bool)
    do_split: Make a bet on a two adjacent numbers. (bool)
    do_straight: Make a bet on a single number. (bool)
    do_street: Make a bet on a three number row. (bool)
    do_third: Make a third of the wheel bet. (bool)
    do_top: Make a five number bet incluidng the zeros. (bool)
    do_trio: Make a three number bet with one or more zeroes. (bool)
    do_zero: Make a zero game bet. (bool)
    neighborhood: Bet on adjacent numbers on the wheel. (None)
    pay_out: Pay the winning bets. (None)

    Overridden Methods:
    do_quit
    game_over
    handle_options
    set_options
    set_up
    """

    aka = ['Roul']
    aliases = {'1-18': 'low', '19-36': 'high', 'double-street': 'double', 'douzaine': 'dozen',
        'finale': 'final', 'finals': 'final', 'first': 'basket', 'impair': 'odd', 'jeu': 'zero',
        'le': 'third', 'manque': 'low', 'noir': 'black', 'orphelins': 'orphans', 'pair': 'even',
        'passe': 'high', 'rouge': 'red', 'single': 'straight', 'six': 'double', 'six-line': 'double',
        'square': 'corner', 'tiers': 'third', 'voisins': 'neighbors'}
    american = ['0', '28', '9', '26', '30', '11', '7', '20', '32', '17', '5', '22', '34', '15', '3', '24',
        '36', '13', '1', '00', '27', '10', '25', '29', '12', '8', '19', '31', '18', '6', '21', '33', '16',
        '4', '23', '35', '14', '2']
    black = ['2', '4', '6', '8', '10', '11', '13', '15', '17', '20', '22', '24', '26', '28', '29', '31',
        '33', '35']
    categories = ['Gambling Games']
    credits = CREDITS
    french = ['0', '32', '15', '19', '4', '21', '2', '25', '17', '34', '6', '27', '13', '36', '11', '30',
        '8', '23', '10', '5', '24', '16', '33', '1', '20', '14', '31', '9', '22', '18', '29', '7', '28',
        '12', '35', '3', '26']
    help_text = {'house-edge': HOUSE_HELP}
    int_re = re.compile('\d+')
    move_query = 'Enter a bet or spin: '
    name = 'Roulette'
    num_options = 4
    options = OPTIONS
    red = ['1', '3', '5', '7', '9', '12', '14', '16', '18', '19', '21', '23', '25', '27', '30', '32', '34',
        '36']
    rules = RULES

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        bucks = utility.plural(self.scores[self.human.name], 'buck')
        return '\nYou have {} {}.'.format(self.scores[self.human.name], bucks)

    def check_bet(self, arguments):
        """
        Do common checking for valid bets. (str, int)

        This checks the valid number of arguments and a valid bet amount. The
        specific bet method will need to check that the thing being bet on is valid.

        Parameters:
        arguments: The arguments to the bet command. (str)
        """
        args = arguments.split()
        # Check for number and bet
        if len(args) != 2:
            self.human.error('Invalid number of arguments to a bet command.')
        else:
            target, bet = args
            # Check for a valid bet.
            if bet.isdigit():
                bet = int(bet)
                max_bet = min(self.max_bet, self.scores[self.human.name])
                # Return valid bet information.
                if 1 <= bet <= max_bet:
                    return target, bet
                # Warn the user about invalid bets.
                elif bet < 1:
                    self.human.error('That bet is too small. You must bet at least 1 buck.')
                else:
                    self.human.error('That bet is too large. You may only bet {} bucks.'.format(max_bet))
            else:
                self.human.error('All bets must be decimal integers.')
        # Return dummy (False) values on failure.
        return '', 0

    def check_two_numbers(self, pair, bet_type):
        """
        Check for two numbers in the layout. (bool)

        Parameters:
        pair: The two numbers separated by a dash. (str)
        bet_type: The type of bet trying to be made. (str)
        """
        pair = pair.split('-')
        # Check for two numbers.
        if len(pair) != 2:
            self.human.error('You must enter two numbers for a {} bet.'.format(bet_type))
        # Check that they are on the wheel.
        elif pair[0] not in self.numbers:
            self.human.error('{} is not in this layout.'.format(pair[0]))
        elif pair[1] not in self.numbers:
            self.human.error('{} is not in this layout.'.format(pair[1]))
        else:
            return True
        return False

    def complete_corners(self, bets, number, wager):
        """
        Get all corner bets for a complete bet. (list of tuple)

        Parameters:
        bets: The bets so far. (list of tuple)
        number: The number bet on. (int)
        wager: The ammount bet. (int)
        """
        # Add the up left corner bet.
        text = 'corner bet on {}-{}'
        if number > 3 and number % 3 != 1:
            targets = [str(n) for n in (number - 4, number - 3, number - 1, number)]
            bets.append((text.format(number - 4, number), targets, wager))
        # Add the up right corner bet.
        if number > 3 and number % 3:
            targets = [str(n) for n in (number - 3, number - 2, number, number + 1)]
            bets.append((text.format(number - 3, number + 1), targets, wager))
        # Add the down right corner bet.
        if number < 34 and number % 3:
            targets = [str(n) for n in (number, number + 1, number + 3, number + 4)]
            bets.append((text.format(number, number + 4), targets, wager))
        # Add the down left corner bet.
        if number < 34 and number % 3 != 1:
            targets = [str(n) for n in (number - 1, number, number + 2, number + 3)]
            bets.append((text.format(number - 1, number + 3), targets, wager))
        return bets

    def complete_splits(self, bets, number, wager):
        """
        Get all split bets for a complete bet. (list of tuple)

        Parameters:
        bets: The bets so far. (list of tuple)
        number: The number bet on. (int)
        wager: The ammount bet. (int)
        """
        text = 'split bet on {}-{}'
        number_text = str(number)
        # Add the up split bet.
        if number > 3:
            bets.append((text.format(number, number - 3), [number_text, str(number - 3)], wager))
        elif self.layout == 'french':
            if number:
                bets.append(('split bet on 0-{}'.format(number), ['0', number_text], wager))
        elif number:
            if number != 1:
                bets.append(('split bet on 00-{}'.format(number), ['00', number_text], wager))
            if number != 3:
                bets.append(('split bet on 0-{}'.format(number), ['0', number_text], wager))
        # Add the down split bet.
        if number < 34:
            if number:
                bets.append((text.format(number, number + 3), [number_text, str(number + 3)], wager))
            elif self.layout == 'french':
                for down in range(1, 3):
                    bets.append(('split bet on 0-{}'.format(number), ['0', number_text], wager))
            elif number_text == '0':
                bets.append(('split bet on 0-1', ['0', '1'], wager))
                bets.append(('split bet on 0-2', ['0', '2'], wager))
            elif number_text == '00':
                bets.append(('split bet on 00-2', ['00', '2'], wager))
                bets.append(('split bet on 00-3', ['00', '3'], wager))
        # Add the right split bet.
        if number % 3:
            bets.append((text.format(number, number + 1), [number_text, str(number + 1)], wager))
        # Add the left split bet.
        if number % 3 != 1:
            bets.append((text.format(number - 1, number), [number_text, str(number - 1)], wager))
        return bets

    def complete_streets(self, bets, number, wager):
        """
        Get all street and double street bets for a complete bet. (list of tuple)

        Parameters:
        bets: The bets so far. (list of tuple)
        number: The number bet on. (int)
        wager: The ammount bet. (int)
        """
        # Add the street bet.
        if number % 3:
            end = number + 3 - (number % 3)
        else:
            end = number
        if number:
            targets = [str(n) for n in range(end - 2, end + 1)]
            bets.append(('street bet on {}-{}-{}'.format(*targets), targets, wager))
        text = 'double street bet on {}-{}'
        # Add the up double street bet.
        if number > 3:
            targets = [str(n) for n in range(end - 5, end + 1)]
            bets.append((text.format(end - 5, end), targets, wager))
        # Add the down double street bet.
        if number < 34:
            targets = [str(n) for n in range(end - 2, end + 4)]
            bets.append((text.format(end - 2, end + 3), targets, wager))
        return bets

    def complete_zero(self, number, wager):
        """
        Get all 0 and 00 related bets for a complete bet. (list of tuple)

        Parameters:
        number: The number bet on. (int)
        wager: The ammount bet. (int)
        """
        sub_bets = [('trio bet on 0-1-2', ['0', '1', '2'], wager)]
        if self.layout == 'french':
            sub_bets.append(('trio bet on 0-2-3', ['0', '2', '3'], wager))
            sub_bets.append(('basket bet', ['0', '1', '2', '3'], wager))
        if self.layout == 'american':
            sub_bets.append(('trio bet on 00-2-3', ['00', '2', '3'], wager))
            sub_bets.append(('trio bet on 0-00-2', ['0', '00', '2'], wager))
            sub_bets.append(('top line bet', ['0', '00', '1', '2', '3'], wager))
        return [bet for bet in sub_bets if str(number) in bet[1]]

    def do_basket(self, arguments):
        """
        Make a four number bet incluidng 0. (first, first four)

        The bet is on 0, 1, 2, and 3. French layout only.

        The argument to the basket command should be the amount bet.
        """
        # Handle aliases.
        words = arguments.split()
        if words[0].lower() != 'four':
            words = ['basket'] + words
        # Check the bet.
        numbers, bet = self.check_bet(' '.join(words))
        # Check the layout.
        if numbers and self.layout == 'french':
            self.scores[self.human.name] -= bet
            self.bets.append(('basket bet', ('0', '1', '2', '3'), bet))
        elif numbers:
            self.human.error('That bet can only be made on a French layout.')
        return True

    def do_bets(self, arguments):
        """
        Show a numbered list of the current bets.
        """
        text = '\n'
        for bet_index, bet in enumerate(self.bets):
            text += '{}: {} ({} bucks)\n'.format(bet_index + 1, bet[0], bet[2])
        self.human.tell(text[:-1])
        return True

    def do_black(self, arguments):
        """
        Bet on black. (noir)

        The bet is on 2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33,
        and 35.

        The argument to the black command should be the amount bet.
        """
        # Check the bet.
        numbers, bet = self.check_bet('black {}'.format(arguments))
        if numbers:
            # Make the bet.
            self.scores[self.human.name] -= bet
            self.bets.append(('black bet', self.black, bet))
        return True

    def do_column(self, arguments):
        """
        Bet on a column.

        The first column is specified by the argument 1, p, or f. That bet is on the
        numbers 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, and 34.

        The second column is specified by the argument 2, m, or s. That bet is on the
        numbers 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, and 35.

        The third column is specified by the argument 3, d, or t. That bet is on the
        numbers 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, and 36.

        The second argument to the column command should be the amount bet.
        """
        # Check the bet
        column, bet = self.check_bet(arguments)
        if column:
            # Get the numbers for the column
            targets = []
            # Check for first column.
            if column.lower() in ('1', 'p', 'f'):
                targets = [str(number) for number in range(1, 37, 3)]
            # Check for second column.
            elif column.lower() in ('2', 'm', 's'):
                targets = [str(number) for number in range(2, 37, 3)]
            # Check for third column.
            elif column.lower() in ('3', 'd', 't'):
                targets = [str(number) for number in range(3, 37, 3)]
            if targets:
                # Make the bet.
                self.scores[self.human.name] -= bet
                self.bets.append(('column bet on {}'.format(column), targets, bet))
            else:
                # Warn on invalid column
                self.human.error('That is not a valid column. Please use 1/2/3, P/M/D, or F/S/T.')
        return True

    def do_complete(self, arguments):
        """
        Make all inside bets on a given number.

        This includes the single bet on that number, and any split, street, trio,
        basket, top line, corner, or double street bets available for that number on
        the current layout.

        If you use the argument progressive, each bet has the amount bet multiplied by
        the number of numbers in the bet.

        The second argument to the complete command should be the amount bet.
        """
        # Check for progressive bets.
        words = arguments.split()
        progressive = 'progressive' in words
        if progressive:
            words.remove('progressive')
        # Check the wager
        number_text, wager = self.check_bet(' '.join(words))
        if number_text:
            if number_text in self.numbers:
                number = int(number_text)
                # Add the single wager.
                bets = [('single bet on {}'.format(number), [number_text], wager)]
                # Add the multi-number bets bets.
                bets = self.complete_splits(bets, number, wager)
                bets = self.complete_streets(bets, number, wager)
                bets.extend(self.complete_zero(number, wager))
                bets = self.complete_corners(bets, number, wager)
                # Convert to progressive betting if required.
                if progressive:
                    prog_bets = []
                    for text, targets, wager in bets:
                        prog_bets.append((text, targets, wager * len(targets)))
                    bets = prog_bets
                # Check wager against what player has.
                total_bet = sum([wager for text, targets, wager in bets])
                if total_bet > self.scores[self.human.name]:
                    self.human.error('You do not have enough bucks for the total wager.')
                else:
                    # Maket the bets.
                    self.bets.extend(bets)
                    self.scores[self.human.name] -= total_bet
            else:
                # Warning for an invalid number_text.
                self.human.error('That number is not in the current layout.')
        return True

    def do_corner(self, arguments):
        """
        Make a bet on a square of numbers. (square)

        The first argument must be the high and low number in a square of four numbers
        on the layout, separated by a dash. That is, the high number must be the low
        number plus four, and the low number cannot be evenly divisible by three (in
        the third colum).

        The second argument to the corner command should be the amount bet.
        """
        # Check the bet.
        numbers, bet = self.check_bet(arguments)
        # Check for two numbers.
        if numbers and self.check_two_numbers(numbers, 'corner'):
            # Check for a valid corner.
            low, high = sorted([int(corner) for corner in numbers.split('-')])
            if high - low == 4 and low % 3:
                # Make the bet.
                self.scores[self.human.name] -= bet
                targets = [str(number) for number in (low, low + 1, high - 1, high)]
                self.bets.append(('corner bet on {}'.format(numbers), targets, bet))
            else:
                message = '{} and {} are not the low and high of a square of numbers.'
                self.human.error(message.format(low, high))
        return True

    def do_double(self, arguments):
        """
        Make a bet on two consecutive rows of numbers. (double street, double line,
            six line)

        The first argument must the be the high and low number of six numbers in two
        rows on the layout, separated by a dash. That is, the high must be the low
        plus six, and must be evenly divisible by three (in the third column).

        The second argument to the double command should be the amount bet.
        """
        # Handle extra words and aliases.
        words = arguments.lower().split()
        if words[0] in ('street', 'line'):
            arguments = ' '.join(words[1:])
        # Check the bet.
        numbers, bet = self.check_bet(arguments)
        # Check for two numbers.
        if numbers and self.check_two_numbers(numbers, 'double street'):
            # Check for valid double street.
            low, high = sorted([int(x) for x in numbers.split('-')])
            if high - low == 5 and not high % 3:
                # Make the bet.
                self.scores[self.human.name] -= bet
                targets = [str(number) for number in range(low, high + 1)]
                self.bets.append(('double street bet on {}'.format(numbers), targets, bet))
        return True

    def do_dozen(self, arguments):
        """
        Bet on a consecutive dozen. (douzaine)

        The first dozen is specified by the argument 1, p, or f, and is a bet on the
        numbers 1-12.

        The second dozen is specified by the argument 2, m, or s, and is a bet on the
        numbers 13-24.

        The third dozen is specified by the argument 3, d, or t, and is a bet on the
        nubmers 25-36.

        The second argument to the dozen command should be the amount bet.
        """
        # Check the bet.
        dozen, bet = self.check_bet(arguments)
        if dozen:
            # Get the numbers in the dozen.
            targets = []
            if dozen.lower() in ('1', 'p', 'f'):
                targets = [str(number) for number in range(1, 13)]
            elif dozen.lower() in ('2', 'm', 's'):
                targets = [str(number) for number in range(12, 25)]
            elif dozen.lower() in ('3', 'd', 't'):
                targets = [str(number) for number in range(24, 37)]
            if targets:
                # Make the bet.
                self.scores[self.human.name] -= bet
                self.bets.append(('dozen bet on {}'.format(dozen), targets, bet))
            else:
                # Warn the user if the dozen is invalid.
                self.human.error('That is not a valid dozen. Please use 1/2/3, P/M/D, or F/S/T.')
        return True

    def do_even(self, arguments):
        """
        Bet on the the even numbers. (pair)

        this is a bet on the numbers 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
        28, 30, 32, 34, and 36.

        The argument to the even command should be the amount bet.
        """
        # Check the bet.
        numbers, bet = self.check_bet('even {}'.format(arguments))
        if numbers:
            # Make the bet.
            self.scores[self.human.name] -= bet
            self.bets.append(('even bet', [str(number) for number in range(2, 37, 2)], bet))
        return True

    def do_final(self, arguments):
        """
        Bet on numbers ending in a particular digit. (finals, finale)

        The first argument should be the final digit to bet on. There are four numbers
        ending in each of the digits 0, 1, 2, 3, 4, 5, and 6. There are three numbers
        ending in each of the digits 7, 8, and 9. Betting on final 0 does not include
        0 or 00.

        The second argument should be the amount to bet on each number.
        """
        # Check the bet.
        digit, bet = self.check_bet(arguments)
        if digit:
            # Check the digit.
            if digit in '1234567890':
                # Get the numbers to bet on.
                numbers = [number for number in self.numbers if number[-1] == digit and number not in '00']
                # Check the full bet.
                full_bet = bet * len(numbers)
                if full_bet > self.scores[self.human.name]:
                    # Warn if user can't afford the full bet.
                    self.human.error('You do not have enough bucks for the full bet.')
                else:
                    # Make the bets.
                    for number in numbers:
                        self.bets.append(('single bet on {}'.format(number), [number], bet))
                    self.scores[self.human.name] -= full_bet
            else:
                self.human.error('That is not a valid final digit.')
        return True

    def do_gipf(self, arguments):
        """
        Connect Four allows you to select a square bet, and one of those numbers will
        come up on the next spin. Blackjack makes the next spin black. Klondike makes
        the next spin a multiple of seven.
        """
        # Check/play the gipf game.
        game, losses = self.gipf_check(arguments, ('blackjack', 'connect four', 'klondike'))
        # Connect Four lets you select a square and one of those numbers will come up.
        if game == 'connect four':
            if not losses:
                # Get a a corner bet
                while True:
                    corner = self.human.ask('Pick a square on the layout (low-high): ')
                    try:
                        low, high = sorted([int(word) for word in corner.split('-')])
                    except ValueError:
                        self.human.error('Please enter two numbers separated by a dash')
                    if low > 0 and high - low == 4:
                        targets = [str(n) for n in (low, low + 1, high - 1, high)]
                        # Make one of the four win.
                        self.forced_spin = targets[:]
                        # Set the bet to 1:1
                        targets = targets * 4 + targets[:2]
                        self.bets.append(('Corner bet on {}-{}.'.format(low, high), targets, 1))
                        self.scores[self.human.name] -= 1
                        break
                    else:
                        self.human.error('That is not a valid corner bet.')
        # A Blackjack win makes the next number black.
        elif game == 'blackjack':
            if not losses:
                self.forced_spin = self.black[:]
                self.human.tell('\nThe next spin will be black.')
        # A Klondike win makes the next number a multiple of seven.
        elif game == 'klondike':
            if not losses:
                self.forced_spin = ['7', '14', '21', '28', '35']
                self.human.tell('\nThe next spin will be a multiple of 7.')
        # Otherwise I'm confused.
        else:
            self.human.error("That bet is not available on this layout.")
        return True

    def do_high(self, arguments):
        """
        Bet on the the high half of the range. (19-36, passe)

        This bet is on the numbers 19-36.

        The argument to the high command should be the amount bet.
        """
        # Check the bet.
        numbers, bet = self.check_bet('high {}'.format(arguments))
        if numbers:
            # Make the bet.
            self.scores[self.human.name] -= bet
            self.bets.append(('high bet', [str(number) for number in range(19, 37)], bet))
        return True

    def do_layout(self, arguments):
        """
        Show the current layout.
        """
        # Get the correct zeroes.
        if self.layout == 'american':
            text = '\n  0  |  00  \n'
        else:
            text = '\n      0     \n'
        # Display the number is columns.
        for number in range(1, 37):
            # Use parens to signify black numbers.
            if str(number) in self.red:
                text += ' {:2} '.format(number)
            else:
                text += '({:2})'.format(number)
            if not number % 3:
                text += '\n'
        self.human.tell(text + '\nred (black)')
        return True

    def do_low(self, arguments):
        """
        Bet on the the low half of the range. (1-18, manque)

        This bet is on the numbers 1-18.

        The argument to the manque command should be the amount bet.
        """
        # Check the bet.
        numbers, bet = self.check_bet('low {}'.format(arguments))
        if numbers:
            # Make the bet.
            self.scores[self.human.name] -= bet
            self.bets.append(('low bet', [str(number) for number in range(1, 19)], bet))
        return True

    def do_neighbors(self, arguments):
        """
        Make a neighbors of zero bet or a 'and the neighbors' bet. (voisons)

        If two arguments are given, the first argument is taken as the number to bet
        on. In addition, four more bets are made are made on the two numbers on
        either side of that number on the roulette wheel. The order of the numbers on
        the American wheel is 0, 28, 9, 26, 30, 11, 7, 20, 32, 17, 5, 22, 34, 15, 3,
        24, 36, 13, 1, 00, 27, 10, 25, 29, 12, 8, 19, 31, 18, 6, 21, 33, 16, 4, 23,
        35, 14, 2. The order of numbers on the French wheel is 0, 32, 15, 19, 4, 21,
        2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31,
        9, 22, 18, 29, 7, 28, 12, 35, 3, 26. So a neighbors bet on 18 would be on the
        numbers 6, 18, 19, 21, and 31 on an American wheel, and on the numbers 7, 9,
        18, 22, and 29 on the French wheel.

        If only one argument is given, the bet is taken as a neighbors of zero bet, a
        special bet available only on the French layout. It includes the following
        bets:
            * A trio bet on 0-2-3.
            * Split bets on 4-7, 12-15, 18-21, 19-22, and 32-35.
            * A corner bet on 25-29.

        The last argument to the neighbors command should be how much to bet on each
        indivdual bet.
        """
        # Pull out the integer arguments.
        int_args = self.int_re.findall(arguments)
        # If there are two, make a and-the-neighbors bet.
        if len(int_args) == 2:
            number, bet = self.check_bet(' '.join(int_args))
            self.neighborhood(number, 5, bet)
        # Otherwise make a neighbors of zero bet.
        elif self.layout == 'french' and int_args:
            # Check the bet and the full bet.
            numbers, bet = self.check_bet('neighbors {}'.format(int_args[0]))
            if bet * 9 > self.scores[self.human.name]:
                self.human.error('You do not have enough money for the full bet.')
            elif numbers:
                # Make the bet.
                self.bets.append(('trio bet on 0-2-3', ['0', '2', '3'], bet * 2))
                self.bets.append(('split bet on 4-7', ['4', '7'], bet))
                self.bets.append(('split bet on 12-15', ['12', '15'], bet))
                self.bets.append(('split bet on 18-21', ['18', '21'], bet))
                self.bets.append(('split bet on 19-22', ['19', '22'], bet))
                self.bets.append(('corner bet on 25-29', ['25', '26', '28', '29'], bet * 2))
                self.bets.append(('split bet on 32-35', ['32', '35'], bet))
                self.scores[self.human.name] -= 9 * bet
        # Warn the user if there is invalid input.
        elif int_args:
            self.human.error('This bet is only available on the French layout.')
        else:
            self.human.error('You must provide an ammount to bet.')
        return True

    def do_niner(self, arguments):
        """
        Make a bet on a neighborhood of niner.

        This bet is the same as a neighbors bet on a specific number, but with eight
        neighbors instead of four. See the help for the neighbors bet for details.

        The second argument to the niner command should be the amount bet on the
        number specified, and on each neighbor.
        """
        # Check the bet.
        number, bet = self.check_bet(arguments)
        if number:
            # Make the bet.
            self.neighborhood(number, 9, bet)
        return True

    def do_odd(self, arguments):
        """
        Bet on the the odd numbers. (impair)

        This bet is on the numbers 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27,
        29, 31, 33, and 35.

        The argument to the odd command should be the amount to bet.
        """
        # Check the bet.
        numbers, bet = self.check_bet('odd {}'.format(arguments))
        if numbers:
            # Make the bet.
            self.scores[self.human.name] -= bet
            self.bets.append(('odd bet', [str(number) for number in range(1, 37, 2)], bet))
        return True

    def do_orphans(self, argument):
        """
        Bet on the orphans: the numbers not in the neighbors or the thirds.

        This bet is only available on the French layout and includes five bets:
            * A single bet on 1.
            * Split bets on 6-9, 14-17, 17-20, 31-34.

        The argument to the orphans command should be the amount to bet on each of the
        individual bets.
        """
        # Check the bet and the full bet.
        numbers, bet = self.check_bet('orphans {}'.format(argument))
        if bet * 5 > self.scores[self.human.name]:
            self.human.error('You do not have enough money for the full bet.')
        elif self.layout != 'french':
            self.human.error('You can only make that bet on the French layout.')
        elif numbers:
            # Make the bet.
            self.bets.append(('single bet on 1', ['1'], bet))
            self.bets.append(('split bet on 6-9', ['6', '9'], bet))
            self.bets.append(('split bet on 14-17', ['14', '17'], bet))
            self.bets.append(('split bet on 17-20', ['17', '20'], bet))
            self.bets.append(('split bet on 31-34', ['31', '34'], bet))
            self.scores[self.human.name] -= 5 * bet
        return True

    def do_prime(self, arguments):
        """
        Make a bet on the prime numbers.

        This bets is on the prime numbers on the board: 2, 3, 5, 7, 11, 13, 17, 19, 23,
        29, and 31. The bet can be done as 'prime twins' to exclude 2 and 23. The bet
        includes a splt bet on 2-3 and single bets on the other primes, or just single
        bets if the twins option is selected.

        The argument to the prime command should be the amount to bet on each of the
        individual bets.
        """
        # Check for betting on twin primes.
        primes = ['2', '3', '5', '7', '11', '13', '17', '19', '23', '29', '31']
        bet_mod = 10
        if arguments.lower().startswith('twins'):
            arguments = arguments[6:]
            primes.remove('2')
            primes.remove('23')
            bet_mod = 9
        # Check the bet.
        numbers, bet = self.check_bet('prime {}'.format(arguments))
        if bet * bet_mod > self.scores[self.human.name]:
            self.human.error('You do not have nough money for the full bet.')
        elif numbers:
            # Make the bet.
            if bet_mod == 10:
                self.bets.append(('split bet on 2-3', ['2', '3'], bet))
                primes = primes[2:]
            for prime in primes:
                self.bets.append(('single bet on {}'.format(prime), [prime], bet))
            self.scores[self.human.name] -= bet_mod * bet
        return True

    def do_quit(self, argument):
        """
        Stop playing Roulette. (!)

        If you have more money than you started with, the game is counted as a win. If
        you have less money than you started with, the game is counted as a loss.
        Otherwise the game is counted as a draw.
        """
        # Determine overall winnings or losses.
        self.scores[self.human.name] -= self.stake
        # Determine if the game is a win or a loss.
        result = 'won'
        if self.scores[self.human.name] > 0:
            self.win_loss_draw[0] = 1
        elif self.scores[self.human.name] < 0:
            result = 'lost'
            self.win_loss_draw[1] = 1
        else:
            self.win_loss_draw[2] = 1
        # Inform the user.
        plural = utility.plural(abs(self.scores[self.human.name]), 'buck')
        self.human.tell('\nYou {} {} {}.'.format(result, abs(self.scores[self.human.name]), plural))
        # Quit the game.
        self.flags |= 4
        self.force_end = True

    def do_red(self, arguments):
        """
        Bet on red. (rouge)

        This bet is on the numbers 1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27,
        30, 32, 34, and 36.

        The argument to the red command should be the amount to bet.
        """
        # Check the bet.
        numbers, bet = self.check_bet('red {}'.format(arguments))
        if numbers:
            # Make the bet.
            self.scores[self.human.name] -= bet
            self.bets.append(('red bet', self.red, bet))
        return True

    def do_remove(self, arguments):
        """
        Remove a bet.

        The argument to the remove command should be the number of a bet as given by
        the bets command. That bet is removed and the money is returned to the player.
        """
        # Default to the last bet.
        if not arguments.strip():
            arguments = str(len(self.bets))
        # Check for a number.
        if arguments.strip().isdigit():
            bet_index = int(arguments) - 1
            # Check for a valid number
            if bet_index < len(self.bets):
                # Remove the bet
                self.scores[self.human.name] += self.bets[bet_index][2]
                self.human.tell('The {} was removed.'.format(self.bets[bet_index][0]))
                self.bets.remove(self.bets[bet_index])
            # Warn the user about invalid input.
            else:
                self.human.error('There are not that many bets.')
        else:
            self.human.error('You must specify the bet with a postive integer.')
        return True

    def do_seven(self, arguments):
        """
        Make a bet on a neighborhood of seven.

        This bet is on the number seven and three numbers on either side of it on the
        wheel, making seven numbers in all. On an American wheel this bet is on the
        numbers 7, 11, 17, 20, 26, 30, and 32. On a French wheel this bet is on the
        numbers 7, 12, 18, 22, 28, 29, and 35.

        The argument to the sevens bet is the amount to bet on each of the seven
        numbers.
        """
        number, bet = self.check_bet(arguments)
        if number:
            # Make the bet.
            self.neighborhood(number, 7, bet)
        return True

    def do_snake(self, arguments):
        """
        Make a zig zag bet from 1 to 34.

        This bet is on the numbers 1, 5, 9, 12, 14, 16, 19, 23, 27, 30, 32, and 34.

        The argument to the snake command is the amount to bet.
        """
        # Check the bet.
        numbers, bet = self.check_bet('snake {}'.format(arguments))
        if numbers:
            # Make the bet.
            self.scores[self.human.name] -= bet
            targets = ['1', '5', '9', '12', '14', '16', '19', '23', '27', '30', '32', '34']
            self.bets.append(('snake bet', targets, bet))
        return True

    def do_spin(self, arguments):
        """
        Spin the wheel.

        This command spins the wheel to determine the winning number, and then pays
        out all winning bets (and removes all losing bets).
        """
        # Pretend a wheel is spinning.
        self.human.tell()
        for spin in range(random.randint(3, 5)):
            self.human.tell('Spinning...')
            time.sleep(1)
        self.human.tell('Clickety clackity...')
        time.sleep(1)
        # Get the winning number.
        if self.forced_spin:
            winner = random.choice(self.forced_spin)
            self.forced_spin = []
        else:
            winner = random.choice(self.numbers)
        self.human.tell('The winning number is {}.'.format(winner))
        # Pay any winning bets.
        self.pay_out(winner)
        return False

    def do_split(self, arguments):
        """
        Make a bet on a two adjacent numbers.

        The first argument should be the two numbers to bet on, separated by a dash,
        which must be next to each other on the layout. That means one must be one
        higher than the other (with the lower one not a multiple of three), or one
        must be three higher than the other one. The exception is bets including 0 or
        00. On the French layout 0-1, 0-2, and 0-3 are all allowed split bets. On the
        American layout 0-1, 0-2, 00-2, and 00-3 are all allowed split bets.

        The second argument to the split command should be the amount bet.
        """
        # Check the bet and two numbers.
        numbers, bet = self.check_bet(arguments)
        if numbers and self.check_two_numbers(numbers, 'split'):
            # Check for a valid split.
            low, high = sorted([int(x) for x in numbers.split('-')])
            valid = (low and high and abs(high - low) == 1 and min(low, high) % 3)
            valid = valid or (low and high and abs(high - low) == 3)
            valid = valid or (self.layout == 'american' and numbers in ('0-1', '0-2', '00-2', '00-3'))
            valid = valid or (self.layout == 'french' and numbers in ('0-1', '0-2', '0-3'))
            if valid:
                # Make the bet.
                self.scores[self.human.name] -= bet
                self.bets.append(('split bet on {}'.format(numbers), numbers.split('-'), bet))
            else:
                # Warn the user about invalid input.
                self.human.error('{} and {} are not adjacent on the layout.'.format(low, high))
        return True

    def do_straight(self, arguments):
        """
        Make a bet on a single number. (single)

        The first argument to the straight command is the number to bet on, the second
        is the amount to bet.
        """
        # Check the bet.
        number, bet = self.check_bet(arguments)
        if number:
            if number not in self.numbers:
                # Warn the user about invalid input.
                self.human.error('That number is not in this layout.')
            else:
                # Make the bet.
                self.scores[self.human.name] -= bet
                self.bets.append(('straight bet on {}'.format(number), [number], bet))
        return True

    def do_street(self, arguments):
        """
        Make a bet on a three number row.

        The first argument to the street command should be three dash-separated numbers
        forming a row on the layout. The bet is on those three numbers.

        The second argument to the street command should be the amount bet.
        """
        # Check the bet.
        number, bet = self.check_bet(arguments)
        if number:
            # Check for a valid end of a row.
            numbers = number.split('-')
            end = int(numbers[-1])
            if end % 3:
                # Warn the user on invalid input.
                self.human.error('A valid street must end in a multiple of three.')
            else:
                # Make the bet.
                text = '{}-{}-{}'.format(end - 2, end - 1, end)
                self.scores[self.human.name] -= bet
                self.bets.append(('street bet on {}'.format(text), text.split('-'), bet))
        return True

    def do_third(self, arguments):
        """
        Make a third of the wheel bet. (le tiers, tiers)

        This is a set of bets covering the third of the wheel (12 numbetr) opposite
        the zero on the French layout. These bets include the following split bets:
        5-8, 10-11, 13-16, 23-24, 27-30, and 33-36.

        If 5-8-10-11 is included as an argument, an individula bet is placed on each
        of those numbers as well. If 'gioco Ferrari' or just 'Ferrari' is included as
        an argument, invidual bets are placed on 8, 11, 23, and 30 as well.

        The last argument to the third bet is the amount to bet on each of the six (or
        ten) bets.
        """
        # Get the integer arguments
        int_args = self.int_re.findall(arguments)
        if int_args and self.layout == 'french':
            # Check the bet.
            numbers, bet = self.check_bet('third {}'.format(int_args[-1]))
            # Check the full wager.
            full_bet = bet * 6
            if '5-8-10-11' in arguments or 'ferrari' in arguments.lower():
                full_bet = bet * 10
            if full_bet > self.scores[self.human.name]:
                self.human.error('You do not have enough money for the full bet.')
            elif numbers:
                # Make the bet.
                self.bets.append(('split bet on 5-8', ['5', '8'], bet))
                self.bets.append(('split bet on 10-11', ['10', '11'], bet))
                self.bets.append(('split bet on 13-16', ['13', '16'], bet))
                self.bets.append(('split bet on 23-24', ['23', '24'], bet))
                self.bets.append(('split bet on 27-30', ['27', '30'], bet))
                self.bets.append(('split bet on 33-36', ['33', '36'], bet))
                # Add any special bets.
                if '5-8-10-11' in arguments:
                    self.bets.append(('single bet on 5', ['5'], bet))
                    self.bets.append(('single bet on 8', ['8'], bet))
                    self.bets.append(('single bet on 10', ['10'], bet))
                    self.bets.append(('single bet on 11', ['11'], bet))
                elif 'ferrari' in arguments.lower():
                    self.bets.append(('single bet on 8', ['8'], bet))
                    self.bets.append(('single bet on 11', ['11'], bet))
                    self.bets.append(('single bet on 23', ['23'], bet))
                    self.bets.append(('single bet on 30', ['30'], bet))
                self.scores[self.human.name] -= full_bet
        elif self.layout != 'french':
            self.human.error('You can only make that be on the French layout.')
        else:
            # Warn the user if no bet is given.
            self.human.error('You must give an amount to bet.')
        return True

    def do_top(self, arguments):
        """
        Make a five number bet incluidng the zeros. (line, top line)

        This is a bet on the five numbers at the top of the American layout. The
        argument to the top command is the amount to bet.
        """
        # Handle extra words/aliases.
        words = arguments.split()
        if words[0].lower() != 'line':
            words = ['line'] + words
        # Check the bet and the layout.
        numbers, bet = self.check_bet(' '.join(words))
        if numbers and self.layout == 'american':
            # Make the bet.
            self.scores[self.human.name] -= bet
            self.bets.append(('top line bet', ('0', '00', '1', '2', '3'), bet))
        elif numbers:
            # Warn the user if playing on a French layout.
            self.human.error('That bet can only be made on an American layout.')
        return True

    def do_trio(self, arguments):
        """
        Make a three number bet with one or more zeroes.

        The first argument should be the three numbers to bet on separated by dashes.
        On the American layout, the valid numbers are 0-1-2, 0-00-2, and 00-2-3. On
        French layout, the valid numbers are 0-1-2 or 0-2-3.

        The second argument to the trio command is how much to bet.
        """
        # Check the bet.
        numbers, bet = self.check_bet(arguments)
        if numbers:
            # Check the numbers based on the layout.
            if self.layout == 'american':
                valid = numbers in ('0-1-2', '0-00-2', '00-2-3')
            else:
                valid = numbers in ('0-1-2', '0-2-3')
            if valid:
                # Make the bet.
                self.scores[self.human.name] -= bet
                self.bets.append(('trio bet on {}'.format(numbers), numbers.split('-'), bet))
            else:
                # Warn the user about invalid input.
                self.human.error('That is not a valid trio on this layout.')
        return True

    def do_zero(self, arguments):
        """
        Make a zero game bet. (jeu, jeu zero)

        This is a variant of the neighbors bet, which bets on 0 and eight neighbors.
        The exact bets made are a straight bet on 26 and three split bets on 0-3,
        12-15, and 32-35. If 'naca' is included as an argument, a straight bet on 19 is
        added. As with the neighbors bet, this bet is only available on the French
        layout.

        The last argument to the zero command is the amount to bet on each of the
        individual bets.
        """
        # Get the integer arguments.
        int_args = self.int_re.findall(arguments)
        if self.layout == 'french' and int_args:
            # Check the bet.
            numbers, bet = self.check_bet('zero {}'.format(int_args[-1]))
            # Check the full bet.
            full_bet = bet * 4
            if 'naca' in arguments.lower():
                full_bet = bet * 5
            if full_bet > self.scores[self.human.name]:
                self.human.error('You do not have enough money for the full bet.')
            elif numbers:
                # Make the bet.
                self.bets.append(('split bet on 0-3', ['0', '3'], bet))
                self.bets.append(('split bet on 12-15', ['12', '15'], bet))
                self.bets.append(('single bet on 26', ['26'], bet))
                self.bets.append(('split bet on 32-35', ['32', '35'], bet))
                if 'naca' in arguments.lower():
                    self.bets.append(('single bet on 19', ['19'], bet))
                self.scores[self.human.name] -= full_bet
        # Warn the user about invalid input.
        elif int_args:
            self.human.error('This bet is only available on the French layout.')
        else:
            self.human.error('You must give an amount to bet.')
        return True

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # The game is over when the human is out of money (and live bets).
        if self.scores[self.human.name] == 0 and not self.bets:
            # Set the results.
            self.win_loss_draw[1] = 1
            self.scores[self.human.name] -= self.stake
            self.human.tell('\nYou lost all of your money.')
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options. (None)"""
        super(Roulette, self).handle_options()
        # Set the numbers in the layout.
        self.numbers = [str(number) for number in range(37)]
        if self.layout == 'american':
            self.numbers.append('00')

    def neighborhood(self, number, width, bet):
        """
        Bet on adjacent numbers on the wheel. (None)

        Parameters:
        number: The center of the neighborhood. (str)
        width: How many numbers there are in the neighborhood. (int)
        bet: The amount of each bet. (int)
        """
        # Check the full bet
        if bet * width > self.scores[self.human.name]:
            self.human.error('You do not have enough money for the full bet.')
        elif number:
            if number in self.numbers:
                # Get the right wheel.
                if self.layout == 'french':
                    wheel = self.french
                else:
                    wheel = self.american
                # Find the number.
                location = wheel.index(number)
                # Make the bets.
                for index in range(location - width // 2, location + width // 2 + 1):
                    slot = wheel[index % len(wheel)]
                    self.bets.append(('single on {}'.format(slot), [slot], bet))
                self.scores[self.human.name] -= width * bet

    def pay_out(self, winner):
        """
        Pay the winning bets. (None)

        Parameters:
        winner: The winning number. (str)
        """
        # Check each bet.
        total_winnings = 0
        for text, target, bet in self.bets:
            # Handle winners
            if winner in target:
                self.human.tell('Your {} won!'.format(text))
                winnings = bet * (36 // len(target))
                self.human.tell('You won {} bucks!'.format(winnings))
                self.scores[self.human.name] += winnings
                total_winnings += winnings
            # Handle losers
            else:
                self.human.tell('Your {} lost.'.format(text, target))
                if self.uk_rule and len(target) == 18:
                    self.scores[self.human.name] += bet // 2
        # Reset bets.
        self.bets = []
        # Inform the user of total winnings.
        if total_winnings:
            self.human.tell('Your total winnings this spin were {} bucks.'.format(total_winnings))
        else:
            self.human.tell('You did not win anything this spin.')

    def set_options(self):
        """Define the game options. (None)"""
        # Set the wheel options.
        self.option_set.add_option('french', ['f'], target = 'layout', value = 'french',
            default = 'american',
            question = 'Do you want to play with the Frech (single zero) layout? bool')
        self.option_set.add_option('american', ['a'], target = 'layout', value = 'american', default = None)
        # Set the money options.
        self.option_set.add_option('stake', ['s'], int, 100, check = lambda bucks: bucks > 0,
            question = 'How much money would you like to start with (return for 100)? ')
        self.option_set.add_option('limit', ['l'], int, 10, target = 'max_bet',
            check = lambda bucks: bucks > 0, question = 'What should the maximum bet be (return for 10)? ')
        # Set the payout options.
        self.option_set.add_option('uk-rule', ['uk'],
            question = 'Should the UK rule (1/2 back on lost 1:1 bets) be in effect? bool')
        # Set the option groups.
        self.option_set.add_group('gonzo', ['gz'], 'limit=1000 uk-rule')

    def set_up(self):
        """Set up the game. (None)"""
        self.scores = {self.human.name: self.stake}
        self.bets = []
        self.forced_spin = []
