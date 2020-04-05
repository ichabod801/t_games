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
use the spin command (or 's' or '@') to spin the wheel to detrmine the winning
number.

Inside bets not involving 0 may be made without the name of the bet. So '18 5'
works as a five buck straight bet on 18, and '10-14 2' works as a two buck
corner bet on 10, 11, 13, and 14.

The bets are listed below. The number in brackets is the number of numbers
that must be specified for the bet. Bets with a capital F in the brackets may
only be made on the French layout, and bets with a capital A may only be made
on the American layout (see options). Bets with xN after them are actually N
bets, so whatever you bet will be mutliplied by N. This only occurs for called
bets.

Your score in the results and statistics will be how much money you won
(positive) or lost (negative). This means you can calcuate your total winnings
or losses by multiplying you average score times the number of games you have
played.

INSIDE BETS:
Basket/First Four/bk/f4: A bet on the first two rows of numbers (0, 1, 2, 3).
    [0F]
Corner/Square/cnr/sq: Bet on four numbers in a square. Specify the lowest and
    highest numbers in the square (low-high). [2]
Double Street/Six Line/ds/6l: Bet on six numbers that form two rows. Specify
    the first number of the first row and the last number of the second row
    (first-last). [2]
Split/sp: Bet on two numbers that are adjacent on the board. [2]
Straight/Single/str/sng: Bet on one number. [1]
Street/st: Bet on a three number row. Specify the last number in the row. [1]
Top Line (tl): Bet on the first two rowns of the American layout. (0-3/00) [0]
Trio (tr): Bet on three adjacent numbers, including at least one zero. [3]

OUTSIDE BETS:
Black/Noir/bl/nr: Bet on the black numbers. [0]
Column/col: Bet on a column of 12 numbers. The column can be specified with
    1/2/3, P/M/D (Premiere, Moyenne, Derniere) or F/S/T (First, Second, Third).
    [1]
Dozen/Douzaine/doz/dz: Bet on the first, second, or third dozen. Use 1/2/3,
    P/M/D, or F/S/T to specify the dozen (see column bet). [1]
Even/Pair/ev/pa: Bet on the even numbers. [0]
High/Passe/19-36/hi/ps: Bet on the high numbers (over 18). [0]
Low/Manque/1-18/lo/mq: Bet on the low numbers (18 and under). [0]
Odd/Impair/od/im: Bet on the odd numbers. [0]
Red/Rouge/rd/ro: Bet on the red numbers. [0]

CALLED BETS:
Complete/cmp: Make every inside bet that contains the specified number. May be
    done as 'complete progressive,' which multiplies each bet by the number
    of numbers in the bet. [1, x7-12, x17-40 progressive]
Final/Finals/Finale/fn: Bet on all non-zero numbers ending with the specified
    digit. [1, x3-4]
Neighbors of Zero/Voisins du Zero/nb zero: Seven bets covering 17 numbers
    around zero on the French layout. [0F, x9]
Neighbors/nb: The neighbors bet with a number specified bets on that number and
    the two numbers on either side on the wheel. [1, x5]
Niner/9r: Bet on a number and the four numbers on either side on the wheel.
    [1, x9]
Orphans/Orphelins/or: Bet on numbers not in Neighbors of Zero or Third of the
    Wheel. [0F, x5]
Prime/pr: Bet on the prime numbers. Twins can be used to exclude 2 and 23.
    [0, x11, x9 for twins]
Seven/sv: Bet on a number and the three numbers on either side on the wheel.
    [1, x7]
Snake/sn: A bet on the zig-zag of red numbers from 1 to 34. [0, x1]
Third of the Wheel/Le Tiers du Cylindre/3d: Bet on a specific third of the
    wheel on the French layout. If made with '5-8-10-11', those numbers are
    doubled up. If made with 'gioco Ferrari', 8, 11, 12, and 30 are also
    doubled up. [0F, x6, x10 5-8-10-11 or Ferrari]
Zero Game/Zero Spiel/Jeu Zero/0g: Bet on zero and six numbers near it on the
    French layout. If 'naca' is included, there is also a bet on 19.
    [0F, x4, x5 naca]

OTHER COMMANDS:
Bets/bt: Show a numbered list of the current bets.
Layout/ly: Show the current layout, with colors marked.
Remove/rm: Remove a bet, using the number from the bets command.
"""


class Roulette(game.Game):
    """
    A game of roulette.

    Class Attributes:
    american: The order of the wheel in the American layout. (list of str)
    black: The black numbers. (list of str)
    french: The order of the wheel in the French layout. (list of str)
    int_re: A regular expression to capture numbers. (re.SRE_Pattern)
    ordinals: The aliases for ordinals in bets. (dict of str: int)
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
    default
    do_quit
    game_over
    handle_options
    set_options
    set_up
    """

    aka = ['Roul']
    aliases = {'0g': 'zero', '1-18': 'low', '19-36': 'high', '3d': 'third', '6l': 'double', '9r': 'niner',
        'bk': 'basket', 'bl': 'black', 'bt': 'bets', 'cmp': 'complete', 'cnr': 'corner', 'col': 'column',
        'double-street': 'double', 'doz': 'dozen', 'douzaine': 'dozen', 'ds': 'double', 'dz': 'dozen',
        'ev': 'even', 'f4': 'basket', 'fin': 'final', 'finale': 'final', 'finals': 'final',
        'first': 'basket', 'fn': 'final', 'hi': 'high', 'im': 'odd', 'impair': 'odd', 'jeu': 'zero',
        'le': 'third', 'ly': 'layout', 'manque': 'low', 'mq': 'low', 'noir': 'black', 'nr': 'black',
        'od': 'odd', 'or': 'orphans', 'orphelins': 'orphans', 'pa': 'even', 'pair': 'even', 'passe': 'high',
        'pr': 'prime', 'primes': 'prime', 'ps': 'high', 'rd': 'red', 'rm': 'remove', 'ro': 'red',
        'rouge': 'red', 'single': 'straight', 'six': 'double', 'six-line': 'double', 'sn': 'snake',
        'sng': 'straight', 'sp': 'split', 'sq': 'corner', 'square': 'corner', 'st': 'street',
        'str': 'straight', 'sv': 'seven', 'tiers': 'third', 'tl': 'top', 'tr': 'trio',
        'voisins': 'neighbors', 'lo': 'low', 'nb': 'neighbors', '@': 'spin', 's': 'spin'}
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
    ordinals = {'1': '1', '2': '2', '3': '3', 'p': '1', 'm': '2', 'd': '3', 'premiere': '1', 'moyenne': '2',
        'derniere': '3', 'f': '1', 's': '2', 't': '3', 'first': '1', 'second': '2', 'third': '3'}
    options = OPTIONS
    red = ['1', '3', '5', '7', '9', '12', '14', '16', '18', '19', '21', '23', '25', '27', '30', '32', '34',
        '36']
    rules = RULES

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        in_hand = utility.num_text(self.scores[self.human.name], 'buck', ':n')
        total_bets = sum(bet for foo, bar, bet in self.bets)
        if total_bets:
            in_play = ', and {} in play'.format(utility.num_text(total_bets, 'buck', ':n'))
        else:
            in_play = ''
        return '\nYou have {}{}.'.format(in_hand, in_play)

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

    def default(self, line):
        """
        Handle unrecognized commands, checking for bets. (bool)

        Note that this doesn't check for a valid foo bet. It lets the do_foo method
        do that, so that the user gets a better error message.

        Parameters:
        line: The command entered by the user. (str)
        """
        # Check for two words with the second one a number.
        words = line.split()
        if len(words) == 2 and words[1].isdigit():
            if words[0].isdigit():
                # Two numbers is a straight bet.
                self.do_straight(line)
            # Check for dash separated numbers.
            elif '-' in words[0]:
                # Translate the numbers.
                try:
                    a, b = [int(number) for number in words[0].split('-')]
                except ValueError:
                    return super(Roulette, self).default(line)
                # Reject bets with 0 in them.
                if not b * a:
                    return super(Roulette, self).default(line)
                # Check for split bets.
                elif b - a in (1, 3):
                    self.do_split(line)
                # Check for street bets.
                elif b - a == 2:
                    self.do_street(line)
                # Check for corner bets.
                elif b - a == 4:
                    self.do_corner(line)
                # Check for double street bets.
                elif b - a == 5:
                    self.do_double(line)
        else:
            return super(Roulette, self).default(line)

    def do_basket(self, arguments):
        """
        Make a four number bet incluidng 0. (first, first four, bk, f4)

        The bet is on 0, 1, 2, and 3. French layout only.

        The argument to the basket command should be the amount bet.
        """
        if self.layout == 'american':
            self.human.error('That bet can only be made on a French layout.')
            return True
        target, wager, ignored = self.parse_bet('basket', arguments, [], ignore = ['four'])
        if wager:
            self.scores[self.human] -= wager
            self.bets.append(('basket bet', ('0', '1', '2', '3'), wager))
        return True

    def do_bets(self, arguments):
        """
        Show a numbered list of the current bets.
        """
        text = '\n'
        for bet_index, bet in enumerate(self.bets):
            text += '{}: {} ({})\n'.format(bet_index + 1, bet[0], utility.num_text(bet[2], 'buck'))
        self.human.tell(text[:-1])
        return True

    def do_black(self, arguments):
        """
        Bet on black. (noir, bl, nr)

        The bet is on 2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33,
        and 35.

        The argument to the black command should be the amount bet.
        """
        # Check the bet.
        target, wager, ignored = self.parse_bet('black', arguments, [])
        if wager:
            # Make the bet.
            self.scores[self.human] -= wager
            self.bets.append(('black bet', self.black, wager))
        return True

    def do_column(self, arguments):
        """
        Bet on a column. (col)

        The first column is specified by the argument 1, p, or f. That bet is on the
        numbers 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, and 34.

        The second column is specified by the argument 2, m, or s. That bet is on the
        numbers 2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, and 35.

        The third column is specified by the argument 3, d, or t. That bet is on the
        numbers 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, and 36.

        The second argument to the column command should be the amount bet.
        """
        target, wager, ignored = self.parse_bet('column', arguments, [0])
        if target and wager:
            # Make the bet.
            targets = [str(number) for number in range(int(target), 37, 3)]
            self.scores[self.human] -= wager
            self.bets.append(('column bet on {}'.format(target), targets, wager))
        return True

    def do_complete(self, arguments):
        """
        Make all inside bets on a given number. (cmp)

        This includes the single bet on that number, and any split, street, trio,
        basket, top line, corner, or double street bets available for that number on
        the current layout.

        If you use the argument progressive, each bet has the amount bet multiplied by
        the number of numbers in the bet.

        The second argument to the complete command should be the amount bet.
        """
        target, wager, ignored = self.parse_bet('complete', arguments, [1], ignore = ['progressive'])
        progressive = 'progressive' in ignored
        # Check the wager
        if target and wager:
            number = int(target)
            # Add the single wager.
            bets = [('single bet on {}'.format(number), [target], wager)]
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
            total_wager = sum([wager for text, targets, wager in bets])
            if total_wager > self.scores[self.human]:
                self.human.error('You do not have enough bucks for the total wager.')
            else:
                # Maket the bets.
                self.bets.extend(bets)
                self.scores[self.human.name] -= total_wager
        return True

    def do_corner(self, arguments):
        """
        Make a bet on a square of numbers. (square, cnr, sq)

        The first argument must be the high and low number in a square of four numbers
        on the layout, separated by a dash. That is, the high number must be the low
        number plus four, and the low number cannot be evenly divisible by three (in
        the third colum).

        The second argument to the corner command should be the amount bet.
        """
        targets, wager, ignored = self.parse_bet('corner', arguments, [0, 4])
        if targets and wager:
            # Check for a valid corner.
            low = int(targets[0])
            if low % 3:
                # Make the bet.
                self.scores[self.human.name] -= wager
                numbers = [str(number) for number in (low, low + 1, low + 3, low + 4)]
                self.bets.append(('corner bet on {}-{}'.format(*targets), numbers, wager))
            else:
                message = '{} and {} are not the low and high of a square of numbers.'
                self.human.error(message.format(*targets))
        return True

    def do_double(self, arguments):
        """
        Make a bet on two consecutive rows of numbers. (double street, double line,
            six line, ds, 6l)

        The first argument must the be the high and low number of six numbers in two
        rows on the layout, separated by a dash. That is, the high must be the low
        plus six, and must be evenly divisible by three (in the third column).

        The second argument to the double command should be the amount bet.
        """
        targets, wager, ignored = self.parse_bet('double', arguments, [0, 5], ignore = ['street', 'line'])
        if targets and wager:
            # Check for valid double street.
            low, high = [int(x) for x in targets]
            if high % 3:
                self.human.error('Double street bets must end in a multiple of 3.')
            else:
                # Make the bet.
                self.scores[self.human] -= wager
                numbers = [str(number) for number in range(low, high + 1)]
                self.bets.append(('double street bet on {}-{}'.format(*targets), numbers, wager))
        return True

    def do_dozen(self, arguments):
        """
        Bet on a consecutive dozen. (douzaine, doz, dz)

        The first dozen is specified by the argument 1, p, or f, and is a bet on the
        numbers 1-12.

        The second dozen is specified by the argument 2, m, or s, and is a bet on the
        numbers 13-24.

        The third dozen is specified by the argument 3, d, or t, and is a bet on the
        nubmers 25-36.

        The second argument to the dozen command should be the amount bet.
        """
        target, wager, ignored = self.parse_bet('dozen', arguments, [0])
        if target and wager:
                end = int(target) * 12 + 1
                numbers = [str(number) for number in range(end - 12, end)]
                self.scores[self.human] -= wager
                self.bets.append(('dozen bet on {}'.format(target), numbers, wager))
        return True

    def do_even(self, arguments):
        """
        Bet on the the even numbers. (pair, ev, pa)

        this is a bet on the numbers 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
        28, 30, 32, 34, and 36.

        The argument to the even command should be the amount bet.
        """
        # Check the bet.
        target, wager, ignored = self.parse_bet('even', arguments, [])
        if wager:
            # Make the bet.
            self.scores[self.human] -= wager
            self.bets.append(('even bet', [str(number) for number in range(2, 37, 2)], wager))
        return True

    def do_final(self, arguments):
        """
        Bet on numbers ending in a particular digit. (finals, finale, fin)

        The first argument should be the final digit to bet on. There are four numbers
        ending in each of the digits 0, 1, 2, 3, 4, 5, and 6. There are three numbers
        ending in each of the digits 7, 8, and 9. Betting on final 0 does not include
        0 or 00.

        The second argument should be the amount to bet on each number.
        """
        # Check the bet.
        digit, wager, ignored = self.parse_bet('final', arguments, [1])
        if digit and wager:
            # Check the digit.
            if len(digit) == 1 and digit in '1234567890':
                # Get the numbers to bet on.
                numbers = [number for number in self.numbers if number[-1] == digit and number not in '00']
                # Check the full bet.
                full_bet = wager * len(numbers)
                if full_bet > self.scores[self.human]:
                    # Warn if user can't afford the full bet.
                    self.human.error('You do not have enough bucks for the full bet.')
                else:
                    # Make the bets.
                    for number in numbers:
                        self.bets.append(('single bet on {}'.format(number), [number], wager))
                    self.scores[self.human] -= full_bet
            else:
                self.human.error('That is not a valid final digit.')
        return True

    def do_gipf(self, arguments):
        """
        Connect Four allows you to select a square bet, and one of those numbers will
        come up on the next spin.

        Blackjack makes the next spin black.

        Klondike makes the next spin a multiple of seven.
        """
        # Check/play the gipf game.
        game, losses = self.gipf_check(arguments, ('blackjack', 'connect four', 'klondike'))
        # Connect Four lets you select a square and one of those numbers will come up.
        if game == 'connect four':
            if not losses:
                # Get a a corner bet
                while True:
                    corner = self.human.ask('\nPick a square on the layout (low-high): ')
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
        Bet on the the high half of the range. (19-36, passe, hi, ps)

        This bet is on the numbers 19-36.

        The argument to the high command should be the amount bet.
        """
        # Check the bet.
        target, wager, ignored = self.parse_bet('high', arguments, [])
        if wager:
            # Make the bet.
            self.scores[self.human] -= wager
            self.bets.append(('high bet', [str(number) for number in range(19, 37)], wager))
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
        Bet on the the low half of the range. (1-18, manque, lo, mq)

        This bet is on the numbers 1-18.

        The argument to the low command should be the amount bet.
        """
        # Check the bet.
        target, wager, ignored = self.parse_bet('low', arguments, [])
        if wager:
            # Make the bet.
            self.scores[self.human] -= wager
            self.bets.append(('low bet', [str(number) for number in range(1, 19)], wager))
        return True

    def do_neighbors(self, arguments):
        """
        Make a neighbors of zero bet or a 'and the neighbors' bet. (voisons, nb)

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
        # If there are two, make an and-the-neighbors bet.
        if len(int_args) == 2:
            target, wager, ignored = self.parse_bet('neighbors', arguments, [1], 5)
            if target and wager:
                self.neighborhood(target, 5, wager)
        # Otherwise make a neighbors of zero bet.
        elif self.layout == 'french' and int_args:
            # Check the bet and the full bet.
            ignore = ('zero', 'of', 'du')
            target, wager, ignored = self.parse_bet('neighbors of zero', arguments, [], 9, ignore)
            if wager:
                # Make the bet.
                self.bets.append(('trio bet on 0-2-3', ['0', '2', '3'], wager * 2))
                self.bets.append(('split bet on 4-7', ['4', '7'], wager))
                self.bets.append(('split bet on 12-15', ['12', '15'], wager))
                self.bets.append(('split bet on 18-21', ['18', '21'], wager))
                self.bets.append(('split bet on 19-22', ['19', '22'], wager))
                self.bets.append(('corner bet on 25-29', ['25', '26', '28', '29'], wager * 2))
                self.bets.append(('split bet on 32-35', ['32', '35'], wager))
                self.scores[self.human] -= 9 * wager
        # Warn the user if there is invalid input.
        elif int_args:
            self.human.error('This bet is only available on the French layout.')
        else:
            self.human.error('You must provide an ammount to bet.')
        return True

    def do_niner(self, arguments):
        """
        Make a bet on a neighborhood of niner. (9r)

        This bet is the same as a neighbors bet on a specific number, but with eight
        neighbors instead of four. See the help for the neighbors bet for details.

        The second argument to the niner command should be the amount bet on the
        number specified, and on each neighbor.
        """
        # Check the bet.
        target, wager, ignored = self.parse_bet('niner', arguments, [1], 9)
        if target and wager:
            # Make the bet.
            self.neighborhood(target, 9, wager)
        return True

    def do_odd(self, arguments):
        """
        Bet on the the odd numbers. (impair, od, im)

        This bet is on the numbers 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27,
        29, 31, 33, and 35.

        The argument to the odd command should be the amount to bet.
        """
        # Check the bet.
        target, wager, ignored = self.parse_bet('odd', arguments, [])
        if wager:
            # Make the bet.
            self.scores[self.human] -= wager
            self.bets.append(('odd bet', [str(number) for number in range(1, 37, 2)], wager))
        return True

    def do_orphans(self, arguments):
        """
        Bet on the orphans: the numbers not in the neighbors or the thirds. (orphelins, or)

        This bet is only available on the French layout and includes five bets:
            * A single bet on 1.
            * Split bets on 6-9, 14-17, 17-20, 31-34.

        The argument to the orphans command should be the amount to bet on each of the
        individual bets.
        """
        # Check the bet and the full bet.
        target, wager, ignored = self.parse_bet('orphans', arguments, [], 5)
        if self.layout != 'french':
            self.human.error('You can only make that bet on the French layout.')
        elif wager:
            # Make the bet.
            self.bets.append(('single bet on 1', ['1'], wager))
            self.bets.append(('split bet on 6-9', ['6', '9'], wager))
            self.bets.append(('split bet on 14-17', ['14', '17'], wager))
            self.bets.append(('split bet on 17-20', ['17', '20'], wager))
            self.bets.append(('split bet on 31-34', ['31', '34'], wager))
            self.scores[self.human] -= 5 * wager
        return True

    def do_prime(self, arguments):
        """
        Make a bet on the prime numbers. (primes, pr)

        This bets is on the prime numbers on the board: 2, 3, 5, 7, 11, 13, 17, 19, 23,
        29, and 31. The bet can be done as 'prime twins' to exclude 2 and 23. The bet
        includes a splt bet on 2-3 and single bets on the other primes, or just single
        bets if the twins option is selected.

        The argument to the prime command should be the amount to bet on each of the
        individual bets.
        """
        # Check for betting on twin primes.
        primes = ['2', '3', '5', '7', '11', '13', '17', '19', '23', '29', '31']
        wager_mod = 10
        target, wager, ignored = self.parse_bet('prime', arguments, [], ignore = ('twin', 'twins'))
        if ignored:
            primes.remove('2')
            primes.remove('23')
            wager_mod = 9
        # Check the bet.
        if wager * wager_mod > self.scores[self.human]:
            self.human.error('You do not have nough money for the full bet.')
        elif wager:
            # Make the bet.
            if not ignored:
                self.bets.append(('split bet on 2-3', ['2', '3'], wager))
                primes = primes[2:]
            for prime in primes:
                self.bets.append(('single bet on {}'.format(prime), [prime], wager))
            self.scores[self.human] -= wager_mod * wager
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
        Bet on red. (rouge, rd, ro)

        This bet is on the numbers 1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27,
        30, 32, 34, and 36.

        The argument to the red command should be the amount to bet.
        """
        # Check the bet.
        target, wager, ignored = self.parse_bet('red', arguments, [])
        if wager:
            # Make the bet.
            self.scores[self.human] -= wager
            self.bets.append(('red bet', self.red, wager))
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
        Make a bet on a neighborhood of seven. (sv)

        This bet is on the number seven and three numbers on either side of it on the
        wheel, making seven numbers in all. On an American wheel this bet is on the
        numbers 7, 11, 17, 20, 26, 30, and 32. On a French wheel this bet is on the
        numbers 7, 12, 18, 22, 28, 29, and 35.

        The argument to the sevens bet is the amount to bet on each of the seven
        numbers.
        """
        target, wager, ignored = self.parse_bet('seven', arguments, [], 7)
        if wager:
            # Make the bet.
            self.neighborhood('7', 7, wager)
        return True

    def do_snake(self, arguments):
        """
        Make a zig zag bet from 1 to 34. (sn)

        This bet is on the numbers 1, 5, 9, 12, 14, 16, 19, 23, 27, 30, 32, and 34.

        The argument to the snake command is the amount to bet.
        """
        # Check the bet.
        target, wager, ignored = self.parse_bet('snake', arguments, [])
        if wager:
            # Make the bet.
            self.scores[self.human] -= wager
            targets = ['1', '5', '9', '12', '14', '16', '19', '23', '27', '30', '32', '34']
            self.bets.append(('snake bet', targets, wager))
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
        Make a bet on a two adjacent numbers. (sp)

        The first argument should be the two numbers to bet on, separated by a dash,
        which must be next to each other on the layout. That means one must be one
        higher than the other (with the lower one not a multiple of three), or one
        must be three higher than the other one. The exception is bets including 0 or
        00. On the French layout 0-1, 0-2, and 0-3 are all allowed split bets. On the
        American layout 0-1, 0-2, 00-2, and 00-3 are all allowed split bets.

        The second argument to the split command should be the amount bet.
        """
        # Check the bet.
        if self.layout == 'american':
            zero = ('0-1', '0-2', '00-2', '00-3')
        else:
            zero = ('0-1', '0-2', '0-3')
        targets, wager, ignored = self.parse_bet('split', arguments, [0, 1, 3], zero = zero)
        if targets and wager:
            # Make the bet.
            self.bets.append(('split bet on {}-{}'.format(*targets), targets, wager))
            self.scores[self.human] -= wager
        return True

    def do_straight(self, arguments):
        """
        Make a bet on a single number. (single, str, sng)

        The first argument to the straight command is the number to bet on, the second
        is the amount to bet.
        """
        # Check the bet.
        target, wager, ignored = self.parse_bet('straight', arguments, [1])
        if target and wager:
            # Make the bet.
            self.scores[self.human] -= wager
            self.bets.append(('straight bet on {}'.format(target), [target], wager))
        return True

    def do_street(self, arguments):
        """
        Make a bet on a three number row. (st)

        The first argument to the street command should be three dash-separated numbers
        forming a row on the layout. The bet is on those three numbers.

        The second argument to the street command should be the amount bet.
        """
        # Check the bet.
        targets, wager, ignored = self.parse_bet('street', arguments, [0, 2])
        if targets and wager:
            # Check for a valid end of a row.
            end = int(targets[1])
            if end % 3:
                # Warn the user on invalid input.
                self.human.error('A valid street must end in a multiple of three.')
            else:
                # Make the bet.
                text = '{}-{}-{}'.format(end - 2, end - 1, end)
                self.scores[self.human] -= wager
                self.bets.append(('street bet on {}'.format(text), text.split('-'), wager))
        return True

    def do_third(self, arguments):
        """
        Make a third of the wheel bet. (le tiers, tiers, 3d)

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
        if self.layout == 'french':
            ignore = 'of the wheel le tiers du cylindre 5-8-10-11 gioco ferrari'.split()
            target, wager, ignored = self.parse_bet('third', arguments, [], ignore = ignore)
            full_wager = wager * 6
            if '5-8-10-11' in ignored:
                full_wager += wager * 4
            if 'gioco' in ignored or 'ferrari' in ignored:
                full_wager += wager * 4
            if full_wager > self.scores[self.human]:
                self.human.error('You do not have enough money for the full bet.')
            elif wager:
                # Make the bet.
                self.bets.append(('split bet on 5-8', ['5', '8'], wager))
                self.bets.append(('split bet on 10-11', ['10', '11'], wager))
                self.bets.append(('split bet on 13-16', ['13', '16'], wager))
                self.bets.append(('split bet on 23-24', ['23', '24'], wager))
                self.bets.append(('split bet on 27-30', ['27', '30'], wager))
                self.bets.append(('split bet on 33-36', ['33', '36'], wager))
                # Add any special bets.
                if '5-8-10-11' in ignored:
                    self.bets.append(('single bet on 5', ['5'], wager))
                    self.bets.append(('single bet on 8', ['8'], wager))
                    self.bets.append(('single bet on 10', ['10'], wager))
                    self.bets.append(('single bet on 11', ['11'], wager))
                if 'ferrari' in ignored or 'gioco' in ignored:
                    self.bets.append(('single bet on 8', ['8'], wager))
                    self.bets.append(('single bet on 11', ['11'], wager))
                    self.bets.append(('single bet on 23', ['23'], wager))
                    self.bets.append(('single bet on 30', ['30'], wager))
                self.scores[self.human] -= full_wager
        else:
            self.human.error('You can only make that be on the French layout.')
        return True

    def do_top(self, arguments):
        """
        Make a five number bet incluidng the zeros. (line, top line, tl)

        This is a bet on the five numbers at the top of the American layout. The
        argument to the top command is the amount to bet.
        """
        # Check the bet and the layout.
        if self.layout == 'american':
            target, wager, ignored = self.parse_bet('top', arguments, [], ignore = 'line')
            # Make the bet.
            self.scores[self.human] -= wager
            self.bets.append(('top line bet', ('0', '00', '1', '2', '3'), wager))
        else:
            # Warn the user if playing on a French layout.
            self.human.error('That bet can only be made on an American layout.')
        return True

    def do_trio(self, arguments):
        """
        Make a three number bet with one or more zeroes. (tr)

        The first argument should be the three numbers to bet on separated by dashes.
        On the American layout, the valid numbers are 0-1-2, 0-00-2, and 00-2-3. On
        French layout, the valid numbers are 0-1-2 or 0-2-3.

        The second argument to the trio command is how much to bet.
        """
        # Check the bet.
        targets, wager, ignored = self.parse_bet('trio', arguments, [-1])
        if targets and wager:
            # Check the numbers based on the layout.
            if self.layout == 'american':
                valid = targets in ('0-1-2', '0-00-2', '00-2-3')
            else:
                valid = targets in ('0-1-2', '0-2-3')
            if valid:
                # Make the bet.
                self.scores[self.human] -= wager
                self.bets.append(('trio bet on {}'.format(targets), targets.split('-'), wager))
            else:
                # Warn the user about invalid input.
                self.human.error('That is not a valid trio on this layout.')
        return True

    def do_zero(self, arguments):
        """
        Make a zero game bet. (jeu, jeu zero, zero game, zero spiel, 0g)

        This is a variant of the neighbors bet, which bets on 0 and eight neighbors.
        The exact bets made are a straight bet on 26 and three split bets on 0-3,
        12-15, and 32-35. If 'naca' is included as an argument, a straight bet on 19 is
        added. As with the neighbors bet, this bet is only available on the French
        layout.

        The last argument to the zero command is the amount to bet on each of the
        individual bets.
        """
        # Check the layout.
        if self.layout == 'french':
            # Check the bet.
            ignore = ('game', 'zero', 'spiel', 'naca')
            target, wager, ignored = self.parse_bet('zero game', arguments, [], ignore = ignore)
            if wager:
                # Check the full bet.
                full_wager = wager * 4
                if 'naca' in ignored:
                    full_wager = wager * 5
                if full_wager > self.scores[self.human]:
                    self.human.error('You do not have enough money for the full bet.')
                elif wager:
                    # Make the bet.
                    self.bets.append(('split bet on 0-3', ['0', '3'], wager))
                    self.bets.append(('split bet on 12-15', ['12', '15'], wager))
                    self.bets.append(('single bet on 26', ['26'], wager))
                    self.bets.append(('split bet on 32-35', ['32', '35'], wager))
                    if 'naca' in arguments.lower():
                        self.bets.append(('single bet on 19', ['19'], wager))
                    self.scores[self.human] -= full_wager
        # Warn the user about invalid layout.
        else:
            self.human.error('This bet is only available on the French layout.')
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
        self.scores[self.human] -= width * bet

    def parse_bet(self, bet_type, arguments, target_spec, bet_count = 1, ignore = [], zero = []):
        """
        Parse the arguments to a bet command. (tuple)

        The return value is the target number(s) (str or list of str), the bet, and
        any words in the argument that were ignored.

        The target_spec is a list of numbers defining how to parse and validate the
        target of the bet. Valid target_specs include:
            * []: There is no target (useful for outside bets).
            * [-1]: The target should not be validated, the bet method will do that.
            * [0]: The target is an ordinal, not a number (as in dozen or column bets).
            * [1]: The target is one number.
            * [0, N]: The target is two numbers, with a difference of N. If only one
                number is provided, the second will be calculated automatically.
            * [0, N, M, ...]: The target is two numbers, with a difference in
                [N, M, ...]. If only one number is provided, the second will be
                calculated with N (the first difference in the target_spec).

        Parameters:
        bet_type: The type of bet being made. (str)
        arguments: The arguments to the bet command. (str)
        target_spec: A specification of allowed targets. (list of int)
        bet_count: How many bets are being made. (int)
        ignore: Words in the arguments to ignore. (list of str)
        zero: The allowed bets including zero for two-target bets. (list of str)
        """
        errors, words, ignored = [], [], []
        for word in arguments.lower().split():
            if word in ignore:
                ignored.append(word)
            else:
                words.append(word)
        # Handle no target.
        if not target_spec:
            target = ''
            words = ['null'] + words
        # Handle one target.
        elif len(target_spec) == 1:
            target = self.parse_one(bet_type, words, target_spec, errors)
        # Handle two number targets.
        elif len(target_spec) >= 2:
            target = self.parse_two(bet_type, words, target_spec, errors, zero)
        # Check for a valid wager.
        wager = self.parse_wager(bet_type, words, bet_count, errors)
        # Inform the user of any errors.
        for error in errors:
            self.human.tell(error)
        return target, wager, ignored

    def parse_one(self, bet_type, words, target_spec, errors):
        """
        Parse a single target number. (str)

        Parameters:
        bet_type: The type of bet being made. (str)
        words: The arguments to the bet command. (list of str)
        target_spec: A specification of allowed targets. (list of int)
        errors: The accumulated parsing errors. (list of str)
        """
        target = ''
        # Deal with targets that need special handling by bet method.
        # !! maybe check valid numbers, if all bets are using this for numbers.
        if target_spec[0] == -1:
            if len(words) == 2:
                target = words[0]
            else:
                errors.append('Invalid number of arguments for {} bet.'.format(bet_type))
        # Verify single number targets.
        elif target_spec[0] and words[0].isdigit():
            if words[0] in self.numbers:
                target = words[0]
            else:
                errors.append('{} is not a number in the current layout.'.format(words[0]))
        # Convert ordinal targets.
        elif words[0] in self.ordinals:
            target = self.ordinals[words[0]]
        # Otherwise pop an error.
        else:
            errors.append('Invalid target specification for {} bet: {!r}.'.format(bet_type, words[0]))
        return target

    def parse_two(self, bet_type, words, target_spec, errors, zero):
        """
        Parse a two-number target number range. (str)

        Parameters:
        bet_type: The type of bet being made. (str)
        words: The arguments to the bet command. (list of str)
        target_spec: A specification of allowed targets. (list of int)
        errors: The accumulated parsing errors. (list of str)
        zero: The allowed bets including zero. (list of str)
        """
        target = []
        numbers = words[0].split('-')
        # Calculate second number if only one given.
        if len(numbers) == 1 and numbers[0].isdigit():
            numbers.append(str(int(numbers[0]) + target_spec[1]))
        # Convert targets to integers.
        try:
            a, b = [int(num) for num in numbers]
        except ValueError:
            errors.append('Invalid target specification for {} bet: {!r}.'.format(bet_type, words[0]))
        else:
            # Validate targets.
            if numbers[0] not in self.numbers:
                errors.append('{} is not a number in the current layout.'.format(numbers[0]))
            if numbers[1] not in self.numbers:
                errors.append('{} is not a number in the current layout.'.format(numbers[1]))
            if not a:
                if words[0] not in zero:
                    errors.append('{!r} is not a valid {} bet.'.format(words[0], bet_type))
            elif b - a not in target_spec[1:]:
                err = 'Numbers for {} bets must be {} {} apart.'
                delta_text = utility.oxford([utility.number_word(delta) for delta in target_spec[1:]], 'or')
                if len(target_spec) > 2:
                    num_text = 'numbers'
                else:
                    num_text = utility.plural(target_spec[1], 'number')
                errors.append(err.format(bet_type, delta_text, num_text))
        # Apply valid targets.
        if not errors:
            target = numbers
        return target

    def parse_wager(self, bet_type, words, bet_count, errors):
        """
        Parse a wager. (str)

        Parameters:
        bet_type: The type of bet being made. (str)
        words: The arguments to the bet command. (list of str)
        bet_count: How many bets are being made. (int)
        errors: The accumulated parsing errors. (list of str)
        """
        wager = 0
        if len(words) == 1:
            errors.append('All bets must specify a wager.')
        elif len(words) > 2:
            err = 'Invalid wager specification for {} wager: {!r}.'
            errors.append(err.format(bet_type, ' '.join(words[1:])))
        elif words[1].isdigit():
            # Validate the size of the wager.
            wager = int(words[1])
            # Warn the user about invalid bets.
            if wager < 1:
                errors.append('That wager is too small. You must wager at least 1 buck.')
            elif wager * bet_count > self.scores[self.human] or wager > self.max_bet:
                err = 'That wager is too large. You may only wager {}.'
                errors.append(err.format(utility.num_text(max_bet // bet_count, 'buck', ':n')))
                wager = 0
        else:
            errors.append('All wagers must be positive integers.')
        return wager

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
                self.human.tell('You won {} bucks!'.format(winnings - bet))
                self.scores[self.human.name] += winnings
                total_winnings += winnings - bet
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
