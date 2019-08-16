"""
slot_machine_game.py

Constants:
CREDITS: The credits for slot machines. (str)
RULES: The rules for playing slot machines. (str)

Classes:
Machine: A slot machine. (object)
MachineError: An error in the operation of a slot machine. (ValueError)
Ampersand: A simple slot machine based on the Liberty Bell slot. (Machine)
SevenWords: A two-dollar machine based on four letter words. (Machine)
Slots: Play a slot machine. (game.Game)
"""


import collections
import itertools
import os
import random
import time

from .. import game
from .. import utility


AMPERSAND_PAYOUTS = """
Ampersand

Cost per play: 1 buck

Payouts:
Two Alphasands                 (@-!-@):  1 buck
Two Alphasands and an Asterisk (@-@-*):  2 bucks
Three Dollars                  ($-$-$):  4 bucks
Three Factorials               (!-!-!):  6 bucks
Three Octothorpes              (#-#-#):  8 bucks
Three Ampersands               (&-&-&): 10 bucks

Ampersand only has one play.

The Ampersand machine is based on the original Liberty Bell, the first slot
machine. The Liberty Bell was designed by Charles Fey in 1895. The play is
the same, but the symbols are different, and Liberty Bell cost a nickel.
"""

CREDITS = """
Game Design: Charles Fey
Machine Designs: Charles Fey and Craig O'Brien
Game Programming: Craig "Ichabod" O'Brien
"""

EIGHT_BALL_PAYOUTS = """
Eight Ball

Cost per play: 1 buck

Payouts:
Split Pair      (4-0-4):  1 buck
Left Pair       (2-2-5):  2 bucks
Right Pair      (9-1-1):  2 bucks
Three of a Kind (6-6-6):  9 bucks
Downer          (5-4-3): 11 bucks
Upper           (1-2-3): 12 bucks
The Lotus       (1-0-8): 24 bucks
The Wheel       (8-0-1): 24 bucks

One or more eights in the result doubles the payout, so the Lotus and the
Wheel payout 48 bucks total. Downers and uppers must be sequences in order,
and the Lotus and the Wheel must be those exact numbers.

Eight Ball only has one play.
"""

RULES = """
At the start you choose which game (type of slot machine) you want to play.
Pick one, and enter the spin command. The cost of the machine will be auto-
matically deducted from your stake. The reels will spin, as shown on the
screen, and based on the final values, you may get a payout in return.

Some machines will have more than row in the final output, and will allow you
to make multiple plays each spin. To make more than one play, you entere the
number of plays you want to make as an argument to the spin command, such as
'spin 3'. Alternatively, you can change the default number of plays from 1
using the plays command.

Note that the spin command has many aliases, including pull, s, and p. Ad-
ditionally, you can just enter return, and the reels will spin with the default
number of plays.

You can change games with the switch command ('switch game'). You can also use
the switch command to change to a different machine of the same type ('switch
machine'). This resets the wheels of the machine.

The payouts command will give you the payouts for the current machine.
"""

SEVEN_WORDS_PAYOUTS = """
Seven Words

Cost per play: 2 bucks

Payouts:
A Pair          (A-B-A-C):    1 buck
3-Letter Word   (B-E-T-X):    3 bucks
4-Letter Word   (B-U-C-K):   16 bucks
Two Pair        (D-F-F-D):   22 bucks
Three of a Kind (G-H-G-G):   40 bucks
Four of a Kind  (I-I-I-I): 1080 bucks
The Seven       (?-?-?-?): 2626 bucks

The Seven Words that give the max payout are secret, but the Ginger Oracle
knows. Pairs and three of a kind can be in any order. Three letter words
must be either the first three letters or the last three letters. All words
must be in order.

Seven Words has three rows and one, two, or three plays. One play plays the
center row, two plays plays the top and bottom row, and three plays plays all
three rows.
"""


class Machine(object):
    """
    A slot machine. (object)

    Class Attributes:
    plays: The different number of plays and what reels/rows they use. (dict)
    reels: The reels of the slot machine. (list of list)
    rows: The number of playable rows. (int)
    sep: The separator when displaying the reels. (str)

    Methods:
    finish: Fill in the extra rows of the machine. (None)
    reset: Randomly set the state of the machine. (None)
    row_text: Get the text for a row. (str)
    shuffle: Shuffle the reels. (None)
    spin: Spin the reels. (int)
    step: Step the reels forward once. (None)

    Overridden Methods:
    __init__
    __repr__
    __str__
    """

    cost = 1
    name = 'Eight Ball'
    payout_text = EIGHT_BALL_PAYOUTS
    plays = {1: [[(0, 0), (0, 1), (0, 2)]]}
    reels = [list('0123456789') for reel in range(3)]
    rows = 1
    sep = '-'

    def __init__(self):
        """Set up the machine. (None)"""
        self.shuffle()
        self.reset()

    def __repr__(self):
        """Debugging text representation. (str)"""
        text = '<{} Machine with {} and {}>'
        reel_text = '{} {}'.format(len(self.reels), utility.plural(len(self.reels), 'reel'))
        row_text = '{} {}'.format(rows, utility.plural(rows, 'row'))
        return text.format(self.name, reel_text, row_text)

    def __str__(self):
        """Human readable text representation. (str)"""
        lines = [''] + [self.row_text(row) for row in self.state]
        return '\n'.join(lines)

    def all_payouts(self, plays):
        """
        Get the payouts for all of the plays. (list)

        There is an item in the returned list for each payout. That item is a tuple of
        the values the payout is based on, the bucks payed out, and a phrase describing
        the combination responsible for the payout.

        Parameters:
        plays: The number of plays for this spin. (int)
        """
        all_payouts = []
        for play in self.plays[plays]:
            values = [self.reels[reel][self.state[row][reel]] for row, reel in play]
            payouts = self.payout(values)
            for payout, text in payouts:
                all_payouts.append((values, payout, text))
        return all_payouts

    def finish(self):
        """Fill in the extra rows of the machine. (None)"""
        for reel in range(len(self.reels) - 1):
            self.state.append([(index + 1) % len(reel) for index, reel in zip(self.state[-1], self.reels)])
        self.state = self.state[-self.rows:]

    def payout(self, values):
        """
        Calculate the payout for a given set of values. (list of tuple)

        values: The values of the current play. (list of str)
        """
        counts = tuple(values.count(value) for value in values)
        payout, text = 0, 'nothing'
        if counts == (2, 1, 2):
            payout, text = 1, "a split pair ({}'s)".format(values[0])
        elif counts == (2, 2, 1):
            payout, text = 2, "a left pair ({}'s)".format(values[0])
        elif counts == (1, 2, 2):
            payout, text = 2, "a right pair ({}'s)".format(values[1])
        elif counts == (3, 3, 3):
            payout, text = 9, "a three-of-a-kind".format(values[0])
        if not payout:
            nums = [int(value) for value in values]
            if nums[1] - nums[0] == 1 and nums[2] - nums[1] == 1:
                payout, text = 12, "an upper (to the {})".format(values[2])
            elif nums[0] - nums[1] == 1 and nums[1] - nums[2] == 1:
                payout, text = 11, "a downer (to the {})".format(values[2])
            elif nums == [1, 0, 8]:
                payout, text = 24, 'the Lotus'
            elif nums == [8, 0, 1]:
                payout, text = 24, 'the Wheel'
        if payout and '8' in values:
            payout *= 2
            if payout < 48:
                text = '{} with an eight'.format(text)
        return [(payout, text)]

    def reset(self):
        """Randomly set the state of the machine. (None)"""
        self.state = [[random.randrange(len(reel)) for reel in self.reels]]
        self.finish()

    def row_text(self, row):
        """
        Get the text for a row. (str)

        Parameters:
        row: The row to generate text for. (list of int)
        """
        return self.sep.join([reel[index] for index, reel in zip(row, self.reels)])

    def shuffle(self):
        """Shuffle the reels. (None)"""
        for reel in self.reels:
            random.shuffle(reel)

    def spin(self, player, plays):
        """
        Spin the reels. (list)

        The return value explained in the help for all_payouts.

        Parameters:
        player: The player making the spin. (player.Player)
        plays: How many lines to play on. (int)
        """
        # Check for a valid number of plays.
        if plays not in self.plays:
            raise MachineError('\n{} machines do not support {} plays.'.format(self.name, plays))
        # Spin the reels.
        self.reset()
        pause = 0.015
        player.tell('')
        for step in range(108):
            player.tell(self.row_text(self.state[-1]))
            time.sleep(pause)
            if step >= 50:
                pause += 0.005
            if step >= 80:
                pause += 0.005
            self.step()
        # Show the final state of the machine.
        self.finish()
        player.tell(self)
        # Calculate the payout.
        return self.all_payouts(plays)

    def step(self):
        """Step the reels forward once. (None)"""
        next_reel = []
        for index, reel in zip(self.state[-1], self.reels):
            next_reel.append((index + (random.random() < 0.9)) % len(reel))
        self.state.append(next_reel)

    def test(self, player):
        """
        Run all possible combinations and report the payouts. (None)

        Parameters:
        player: The player to report the results to. (player.Player)
        """
        # Check every possible combination.
        counts = collections.defaultdict(int)
        total_payouts = collections.defaultdict(int)
        for spin in itertools.product(*self.reels):
            payouts = self.payout(spin)
            for payout, text in payouts:
                key = text.split('(')[0]
                counts[key] += 1
                total_payouts[key] += payout
        # Print the results from most frequent to least.
        player.tell('')
        order = sorted(((count, value) for value, count in counts.items()), reverse = True)
        for count, value in order:
            print('{}: n = {}, $ = {}'.format(value, count, total_payouts[value]))
        print('\nTotal Combinations: {}'.format(sum(counts.values())))
        print('\nTotal Payout: {}'.format(sum(total_payouts.values())))


class Ampersand(Machine):
    """
    A simple slot machine based on the original Liberty Bell slot. (Machine)

    Overridden Methods:
    payout
    """

    name = 'Ampersand'
    payout_text = AMPERSAND_PAYOUTS
    reels = [list('!@#$&*') for reel in range(3)]

    def payout(self, values):
        """
        Calculate the payout for a given set of values. (list of tuple)

        values: The values of the current play. (list of str)
        """
        counts = tuple(values.count(value) for value in values)
        payout, text = 0, 'nothing'
        if 2 in counts and sorted(values)[1] == '@':
            if '*' in values:
                payout, text = 2, 'two alphasands and an asterisk'
            else:
                payout, text = 1, 'two alphasands'
        elif 3 in counts:
            if values[0] == '$':
                payout, text = 4, 'three dollars'
            elif values[0] == '!':
                payout, text = 6, 'three factorials'
            elif values[0] == '#':
                payout, text = 8, 'three octothorpes'
            elif values[0] == '&':
                payout, text = 10, 'three ampersands'
        return [(payout, text)]


class FullHouse(Machine):
    """
    A five-dollar machine based on pairs and trips. (Machine)

    Overridden Methods:
    all_payouts
    payout
    """

    cost = 5
    digits = set('1234567890')
    lowers = set('gqxyz')
    name = 'Full House'
    plays = {1: [[(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)]],
        3: [[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)], [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],
           [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)]],
        5: [[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)], [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],
           [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)], [(2, 0), (1, 1), (0, 2), (1, 3), (2, 4)],
           [(0, 0), (1, 1), (2, 2), (1, 3), (0, 4)]]}
    """reels = [list('12345678901234567890!@#$%&*?=|'), list('1234567890GQXYZgqxyz!@#$%&*?=|'),
        list('1234567890GQXYZgqxyzGQXYZgqxyz!@#$%&*?=|'), list('1234567890GQXYZgqxyz!@#$%&*?=|'),
        list('1234567890GQXYZgqxyz!@#$%&*?=|!@#$%&*?=|')]"""
    reels = [list('1234567890GQXYZgqxyz!@#$%&*?=|') for reel in range(5)]
    rows = 3
    sep = ':'
    symbols = set('!@#$%&*?=|')
    uppers = set('GQXYZ')

    def all_payouts(self, plays):
        """
        Get the payouts for all of the plays. (list)

        There is an item in the returned list for each payout. That item is a tuple of
        the values the payout is based on, the bucks payed out, and a phrase describing
        the combination responsible for the payout.

        Parameters:
        plays: The number of plays for this spin. (int)
        """
        payouts = super(FullHouse, self).all_payouts(plays)
        payout_types = [text.split('(')[0].strip() for values, payout, text in payouts]
        pairs = payout_types.count('a pair') + payout_types.count('two_pair') * 2
        pass_pairs = payout_types.count('a password pair')
        trips = payout_types.count('three-of-a-kind')
        constructed = (pass_pairs + pairs) * trips
        if constructed:
            payout = 38 * (pass_pairs * trips) + 35 * (pairs * trips)
            number_text = utility.number_word(constructed)
            house_text = utility.plural(constructed, 'house')
            payouts.append(([], payout, '{} constructed full {}'.format(number_text, house_text)))
        houses = payout_types.count('a full house')
        if houses:
            total_payout = sum(payout for values, payout, text in payouts)
            bonus = (total_payout - 1800) * 2 * houses
            if bonus:
                bonus_text = 'a bonus for {}.'.format(utility.number_plural(houses, 'full house'))
                payouts.append([], bonus, bonus_text)
        return payouts

    def payout(self, raw_values):
        """
        Calculate the payout for a given set of values. (list of tuple)

        raw_values: The values of the current play. (list of str)
        """
        values = sorted(raw_values)
        counts = sorted(values.count(value) for value in values)
        has_digits = self.digits.intersection(values)
        has_lowers = self.lowers.intersection(values)
        has_symbols = self.symbols.intersection(values)
        has_uppers = self.uppers.intersection(values)
        has_letters = has_lowers or has_uppers
        if has_digits and has_lowers and has_uppers and has_symbols:
            payout, text = 6, 'a password'
        else:
            payout, text = 0, 'nothing'
        if counts == [5, 5, 5, 5, 5]:
            payout, text = 180000, 'the fiver jackpot'
        elif has_digits and not has_letters and not has_symbols:
            payout, text = 23, 'pure digits'
        elif ''.join(raw_values).lower() == 'xyzzy':
            payout, text = 180000, 'the xyzzy jackpot'
        elif not has_digits and has_letters and not has_symbols:
            payout, text = 23, 'pure letters'
        elif not has_digits and not has_letters and has_symbols:
            payout, text = 23, 'pure symbols'
        elif counts == [1, 1, 1, 2, 2]:
            for pair in values:
                if values.count(pair) == 2:
                    break
            if text == 'a password':
                payout, text = 9, "a password pair ({}'s)".format(pair)
            else:
                payout, text = 3, "a pair ({}'s)".format(pair)
        elif counts == [1, 2, 2, 2, 2]:
            high, low = values[3], values[1]
            payout, text = 18, "two pair ({}'s and {}'s)".format(high, low)
        elif counts == [1, 1, 3, 3, 3]:
            payout, text = 23, "three-of-a-kind ({}'s)".format(values[2])
        elif counts == [2, 2, 3, 3, 3]:
            trip = values[2]
            if values[0] == trip:
                pair = values[4]
            else:
                pair = values[0]
            payout, text = 1800, "a full house ({}'s over {}'s)".format(trip, pair)
        elif counts == [1, 4, 4, 4, 4]:
            payout, text = 801, "four-of-a-kind ({}'s)".format(values[2])
        return [(payout, text)]


class SevenWords(Machine):
    """
    A two-dollar machine based on four letter words. (Machine)

    The reels used are based on the frequencies of the letters in each position of
    a four letter word. So the first reel is based on the frequency of the first
    letter of a four letter word. The three most common letters are on each reel
    three times, and the next four most common letters are on each reel twice.

    Attributes:
    the_seven: The seven jackpot words. (set of str)
    words_four: The four letter English words. (set of str)
    words_three: The three letter English words. (set of str)

    Methods:
    load_words: Load the four letter words. (None)

    Overridden Methods:
    __init__
    payout
    """

    cost = 2
    name = 'Seven Words'
    payout_text = SEVEN_WORDS_PAYOUTS
    plays = {1: [[(1, 0), (1, 1), (1, 2), (1, 3)]],
        2: [[(0, 0), (0, 1), (0, 2), (0, 3)], [(2, 0), (2, 1), (2, 2), (2, 3)]],
        3: [[(0, 0), (0, 1), (0, 2), (0, 3)], [(1, 0), (1, 1), (1, 2), (1, 3)],
            [(2, 0), (2, 1), (2, 2), (2, 3)]]}
    reels = [list('SSSBBBPPPPTTCCDDLLFMRGHWANOEJVKYIUZQ'), list('AAAOOOIIIEEUULLRRHNPWYCTMKDBVGSXFZJQ'),
        list('AAAEEENNNRRLLOOSSITMCUPGDBWFKVZYHXJ'), list('SSSEEETTTDDKKLLNNYPMRHGAOFBWIXCZUVJ')]
    rows = 3

    def __init__(self):
        """Set up the machine. (None)"""
        super(SevenWords, self).__init__()
        self.load_words()

    def load_words(self):
        """Load the four letter words. (None)"""
        path = os.path.join(utility.LOC, 'other_games', '3of6game.txt')
        self.words_four, self.words_three = set(), set()
        with open(path) as word_file:
            for word in word_file:
                if len(word) == 5:
                    self.words_four.add(word.strip().upper())
                elif len(word) == 4:
                    self.words_three.add(word.strip().upper())
        self.the_seven = set(('SHIT', 'PISS', 'FUCK', 'CUNT', 'TITS', 'COCK', 'MOFO'))

    def payout(self, values):
        """
        Calculate the payout for a given set of values. (list of tuple)

        values: The values of the current play. (list of str)
        """
        counts = sorted(values.count(value) for value in values)
        word = ''.join(values)
        payout, text = 0, 'nothing'
        if word in self.the_seven:
            payout, text = 2626, 'one of the Seven (CENSORED)'
        elif counts == [4, 4, 4, 4]:
            payout, text = 1080, "four-of-a-kind ({}'s)".format(values[0])
        elif counts == [1, 3, 3, 3]:
            values.sort()
            payout, text = 40, "three-of-a-kind ({}'s)".format(values[1])
        elif counts == [2, 2, 2, 2]:
            values.sort()
            payout, text = 22, "two pair ({}'s and {}'s)".format(values[0], values[2])
        elif word in self.words_four:
            payout, text = 16, 'a four letter English word ({})'.format(word.lower())
        elif word[:3] in self.words_three:
            payout, text = 3, 'a three letter English word ({})'.format(word[:3].lower())
        elif word[1:] in self.words_three:
            payout, text = 3, 'a three letter English word ({})'.format(word[1:].lower())
        elif counts == [1, 1, 2, 2]:
            for pair in values:
                if values.count(pair) == 2:
                    break
            payout, text = 1, "a pair ({}'s)".format(pair)
        return [(payout, text)]


class MachineError(ValueError):
    """An error in the operation of a slot machine. (ValueError)"""
    pass


class Slots(game.Game):
    """
    A game of playing slot machines. (game.Game)

    Attributes:
    default_plays: The default number of plays per spin. (int)
    machine: The slot machine currently being played. (Machine)
    machines: The slot machines available to play. (list of Machine)

    Methods:
    do_spin: Spin the reels of the machine in hopes of a payout. (bool)
    do_switch: Switch to another game or machine. (bool)

    Overridden Methods:
    __str__
    default
    do_quit
    game_over
    player_action
    set_options
    set_up
    """

    aka = ['Fruit Machiness', 'Puggy', 'The Slots', 'Slots', 'Slot', 'Poker Machines', 'Pokies',
        'One-Armed-Bandits', 'SlMa']
    aliases = {'s': 'spin', 'sw': 'switch', 'pull': 'spin', 'p': 'spin', '': 'spin'}
    categories = ['Gambling Games']
    name = 'Slot Machines'

    def __str__(self):
        """Human readable text representation. (str)"""
        text = '\nYou are playing {}.\nYou have {} {} left'
        bucks = utility.plural(self.scores[self.human.name], 'buck')
        return text.format(self.machine.name, self.scores[self.human.name], bucks)

    def do_payouts(self, arguments):
        """
        Show the payouts for the current machine.
        """
        self.human.tell(self.machine.payout_text.rstrip())

    def do_plays(self, arguments):
        """
        Set the default number of plays.

        The argument is the number of plays for when you use the spin command without
        an argument.
        """
        # Check for an integer.
        try:
            plays = int(arguments)
        except ValueError:
            self.human.error('\nInvalid argument to the plays command: {!r}.'.format(arguments))
            return True
        if plays in self.machine.plays:
            # Assign a valid number of plays.
            self.default_plays = plays
            self.human.tell('\nThe default number of plays is now {}.'.format(plays))
        else:
            # Give information about an invalid number of plays.
            self.human.error('\nThe current machine does not support {} plays.'.format(plays))
            play_text = utility.oxford(sorted(self.machine.plays))
            self.human.error('It supports the follow numbers of plays: {}.'.format(play_text))
        return True

    def do_quit(self, argument):
        """
        Stop playing Blackjack. (!)
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

    def do_spin(self, arguments):
        """
        Spin the reels of the machine in hopes of a payout. (s, pull, p)

        The argument to spin is the number of plays you are spinning for. The number
        of plays you can make are dependent on the machine you are playing. If you do
        not provide an argument, the default number of plays is used. This starts as
        one, and can be changed with the plays command.
        """
        if arguments:
            # Check that the argument is an integer.
            try:
                plays = int(arguments)
            except:
                self.human.error('\nInvalid argument to spin command: {!r}.'.format(arguments))
                return True
        else:
            # Use the default if there are no arguments.
            plays = self.default_plays
        # Make sure the player has enough money.
        if plays * self.machine.cost > self.scores[self.human.name]:
            self.human.error('\nYou do not have enough money to do that.')
            return True
        # Spin the machine.
        try:
            payouts = self.machine.spin(self.human, plays)
        except MachineError as err:
            print(err.message)
            return True
        # Inform the player of the results.
        self.human.tell('')
        self.scores[self.human.name] -= self.machine.cost * plays
        total_payout = 0
        for values, bucks, text in payouts:
            # Emphasize good results with exclamation points.
            if bucks > self.machine.cost * 10:
                punctuation = '!!!'
            elif bucks > self.machine.cost:
                punctuation = '!'
            else:
                punctuation = '.'
            self.human.tell('You got {}{}'.format(text, punctuation))
            total_payout += bucks
        # Give the overall results.
        if total_payout:
            bucks = utility.plural(total_payout, 'buck')
            self.human.tell('\nYour won a total of {} {} this spin.'.format(total_payout, bucks))
            self.scores[self.human.name] += total_payout
        else:
            self.human.tell('\nYou did not win anything this spin.')

    def do_switch(self, arguments):
        """
        Switch to another game or machine. (sw)

        'switch machine' switches you to another machine of the same type. 'switch
        game' allows you to choose a new type of slot machine. These can be abbreviated
        as 'sw m' and 'sw g'.
        """
        if arguments.lower() in ('g', 'game'):
            # Build a Menu.
            menu_lines = ['']
            for number, game in enumerate(self.machines, start = 1):
                menu_lines.append('{}: {}'.format(number, game.name))
            menu_lines.extend(['', 'Choose a game: '])
            menu = '\n'.join(menu_lines)
            # Get the user's choice.
            choice = self.human.ask_int(menu, low = 1, high = len(self.machines), cmd = False)
            self.machine = self.machines[choice - 1]
            # Check default plays.
            if self.default_plays not in self.machine.plays:
                new_plays = min(self.machine.plays.keys())
                self.human.tell('\nThe current default plays setting is invalid for this machine.')
                self.human.tell('The default number of plays has been reset to {}.'.format(new_plays))
                self.default_plays = new_plays
        elif arguments.lower() in ('m', 'machine'):
            self.machine.shuffle()
            self.human.tell('\nYou have moved to a different machine.')
        else:
            self.human.error('\nInvalid argument to switch command: {!r}.'.format(arguments))

    def do_test(self, arguments):
        """
        Test the payouts of the machine.

        This only tests payouts from one play. This may take a while for more
        complicated games with more/larger reels.
        """
        self.machine.test(self.human)
        return True

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # The game is over when the human is out of money (and live bets).
        if self.scores[self.human.name] == 0:
            # Set the results.
            self.win_loss_draw[1] = 1
            self.human.tell('\nYou lost all of your money.')
            self.scores[self.human.name] -= self.stake
            return True
        else:
            return False

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        player.tell(self)
        move = player.ask('\nWhat would you like to do? ')
        return self.handle_cmd(move)

    def set_options(self):
        """Define the game options. (None)"""
        # Set the betting options.
        self.option_set.add_option('stake', ['s'], int, 100, check = lambda bucks: bucks > 0,
            question = 'How much money would you like to start with (return for 100)? ')

    def set_up(self):
        """Set up the slot machines. (None)"""
        # Instantiate each slot machine class.
        machine_classes = []
        search = [Machine]
        while search:
            machine_classes.append(search.pop())
            search.extend(machine_classes[-1].__subclasses__())
        self.machines = [cls() for cls in machine_classes]
        self.machines.sort(key = lambda machine: (machine.rows, len(machine.reels)))
        # Set up tracking variables:
        self.machine = None
        self.scores[self.human.name] = self.stake
        self.default_plays = 1
        self.do_switch('game')

