"""
ten_thousand_game.py

A game of Ten Thousand.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Ten Thousand. (str)
OPTIONS: The options for Ten Thousand.
RULES: The rules for Ten Thousand. (str)

Classes:
TenKBot: A base bot for the game of Ten Thousand. (player.Bot)
GamblerBot: A bot that rolls as often as it's chance of scoring. (TenKBot)
GeneBot: A bot for a genetic algorithm. (TenKBot)
KniziaBot: A bot following Reiner Knizia's Strategy. (TenKBot)
ProbabilityBot: A bot using expected values. (TenKBot)
TenThousand: A game of TenThousand. (game.Game)
"""


from __future__ import division

import itertools
import random

from .. import dice
from .. import game
from .. import player
from .. import utility


CREDITS = """
Game Design: Traditional.
Game Programming: Craig "Ichabod" O'Brien
Bot Design: Reiner Knizia, Craig O'Brien
"""

OPTIONS = """
5000 (5k): Equivalent to win = 5000.
carry-on (co): If a player fails to score, you can carry on with their points
    and dice.
clear-combo (cc): If your last roll scored a three or more of a kind, and you
    roll the number of that combo, you must reroll all the dice you just
    rolled.
crash= (cr=): How many points you lose if you roll all six dice and don't
    score. Defaults to 0, typically 500.
entry= (e=): The minimum number of points needed to get on the table.
explosion (ex): Rolling six 1's is too many points and you lose.
five-dice (5d): The game is played with five dice, with no six of a kind or
    straight.
five-kind (5k): The score for getting five of a kind, typically 2,000 or
    4,000. If this and five-mult are 0, five of a kind is not allowed.
five-mult (5m): The score multiplied by the die face for five of a kind,
    typically 300 or 400. If this and five-kind are 0, five of a kind is not
    allowed.
force-combo (fc): If you score with three or more of a kind, you *must* roll
    again.
force-six (f6): If you score on all six dice, you *must* roll again.
four-kind (4k): The score for getting four of a kind. Typically 1,000 or
    2,000. If this and four-mult are 0, four of a kind is not allowed.
four-mult (4m): The score multiplied by the die face for four of a kind,
    typically 200. If this and four-kind are 0, four of a kind is not allowed.
full-house (fh): The bonus added to the three of a kind score when scoring a
    full house. Defaults to 0, or no full houses.
gonzo (gz): Equivalent to three-pair=600 sstraight=1500 full-house=250
    four_mult=200 five-mult=400 six-mult=800 three-strikes=500 train-wreck
    carry-on clear-combo force-combo force-six entry=350 min-grows
    second-chance explosion instant-win wild
instant-win (iw): You win instantly if you roll six sixes.
min-grows (mg): You must roll more points as the previous scored in order to
    score yourself.
minimum= (m=): The minimum number of points you must roll before you can score
    them.
must-score (ms): You have no choice in what to hold, you must hold all
    scoring dice.
no-risk (nr): If you roll no points, your turn still ends, but you score any
    points you had rolled this turn.
second-chance (2c): You may make a second chance roll when you do not score.
    You selected two or more just rolled dice and reroll the rest of them.
    You must score a combo (or straight, if allowed) with the selected dice
    in order to keep going.
six-kind (6k): The score for getting six of a kind, typically 3,000, 6,000, or
    10,000. If this and six-mult are 0, six of a kind is not allowed.
six-mult (6m): The score multiplied by the die face for six of a kind,
    typically 400 or 800. If this and six-kind are 0, six of a kind is not
    allowed.
straight= (s=): The score for a straight (1-6). Defaults to 0, or no straights.
super-strikes (ss): If you don't score three turns in a row, you loose all of
    your points.
three-pair= (3p=): The score for three pair. Defaults to 0, no three pair.
three-strikes (3s): If you don't score three turns in a row, you loose 500
    points.
train-wreck (tw): If you roll all six dice and don't score, you lose all of
    your points.
wild: One die has a wild. If rolled with a pair or more, it must be used to
    complete the n-of-a-kind.
wimpout (wo): Equivalent to five-dice entry=350 five-mult=1000 wild force-combo
    clear-combo force-six win=5000 must-score'
win= (w=): The number of points needed to win.
zen= (z=): The points scored if you roll all the dice and none of them score.
    Defaults to 0, typically 500.

Bot Options:
base-pace (bp): Add a bot that tries to stay close to the lead.
gambler (gm): Add a bot that stops as often as it's odds of not scoring.
knizia (kz): Add a bot using Reiner Knizia's strategy.
mod (md): Add a bot that goes for more points the farther it is behind.
prob (pb): Add a bot that uses expected value calculations.
random (rd): Add a bot with a random strategy.
value (vu): Add a bot that ties to score a set value.
"""

RULES = """
At the start of each turn you roll six dice. After each roll you may set aside
any scoring dice, and roll the remaining dice. Once you have rolled 1,000
points, you may stop after any scoring roll and score all of the points you
have rolled this turn. If you have not scored any points in the game yet, you
must roll 1,500 points before you can stop and score them. This is called
"getting on the table." If you have scored on all six dice, you may roll all
six dice again. If at any point you roll the dice and none of the dice you
just rolled score anything, you turn ends and you get no points for the turn.
The first person to get 10,000 points wins the game. However, each remaining
player gets one last chance to beat their score. The highest score wins.

Scoring:
Ones: Each one scores 100 points.
Fives: Each five scores 50 points.
Three of a Kind: Three of a kind are worth 100 points times the number rolled,
    or 1,000 points for three ones.
Four of a Kind: Four of a kind are worth 200 points times the number rolled,
    or 2,000 points for four ones.
Five of a Kind: Five of a kind are worth 400 points times the number rolled,
    or 4,000 points for four ones.
Six of a Kind: Six of a kind are worth 800 points times the number rolled,
    or 8,000 points for four ones.
Straight: A straight from one to six is worth 1,500 points.
Three Pair: Three pairs are worth 1,000 points.
* For combinations of dice, all dice in the combination must be rolled at the
    same time. However, if you have a pair or a partial straight, you can take
    a second chance roll to complete the three of a kind or the straight. If
    you fail to complete the score, your turn is over with zero points even if
    you have other scoring dice.

Commands:
hold (h): Set aside scoring dice (list the dice as a parameter to the command).
score (s): Score the points rolled this turn and end your turn.
"""

class TenKBot(player.Bot):
    """
    A base bot for the game of Ten Thousand. (player.Bot)

    Attributes:
    bank: How much the player has banked this turn. (int)

    Methods:
    carry_on: Decided whether or not to carry on. (str)
    hold: Decide which dice to roll. (str)
    second_chance: Choose a pair to try to complete. (str)
    roll_or_score: Decide whether to roll for more or score what you've got. (str)

    Overridden Methods:
    ask
    ask_int_list
    setup
    tell
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        if prompt == '\nWhat is your move? ':
            # Hold if you haven't yet.
            if not self.game.held_this_turn:
                move = self.hold()
            # Roll if it makes no sense not to.
            elif self.game.turn_score < self.game.minimum:
                move = 'roll'
            elif self.game.turn_score < self.game.entry and not self.game.entered[self.name]:
                move = 'roll'
            elif self.game.no_risk:
                move = 'roll'
            elif self.game.must_roll:
                move = 'roll'
            # During last licks, roll if you haven't won yet.
            elif self.game.last_player is not None:
                if self.game.scores[self.name] + self.game.turn_score <= max(self.game.scores.values()):
                    move = 'roll'
                else:
                    # But maybe roll to get some distance.
                    move = self.roll_or_score()
            # Otherwise roll or score as per the bot-specific strategy.
            else:
                move = self.roll_or_score()
            return move
        # Handle other situations.
        elif prompt.startswith('Would you like to'):
            return self.carry_on()
        elif prompt.startswith('Your turn is over'):
            return 'Gorramit'
        else:
            super(TenKBot, self).ask(prompt)

    def ask_int(self, prompt, low = None, high = None, valid = [], default = None, cmd = True):
        """
        Get an integer response from the bot. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        valid: The valid values for the integer. (container of int)
        default: The default choice. (int or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        # Choose a number for a wild (the highest value one)
        if 1 in valid or low == 1:
            return 1
        elif valid:
            return max(valid)
        else:
            return high

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
        # Handle second chance opportunities.
        if prompt.startswith('Which dice would'):
            return self.second_chance()
        # Everything else goes to parent class (raises an error)
        else:
            super(TenKBot, self).ask_int_list(prompt, loe, high, valid, valid_lens, default)

    def carry_on(self):
        """Decide whether or not to carry on. (str)"""
        return 'yes' if self.roll_or_score() == 'roll' else 'no'

    def hold(self):
        """Decide which dice to roll. (str)"""
        return 'hold'

    def roll_or_score(self):
        """Decide whether to roll for more or score what you've got. (str)"""
        if self.game.turn_score < 350:
            return 'roll'
        else:
            return 'score'

    def second_chance(self):
        """Choose a pair to try to complete. (str)"""
        # Go for the highest scoring pair.
        values = self.game.dice.get_free().values
        pairs = [value for value in range(1, 7) if values.count(value) == 2]
        if 1 in pairs:
            return [1, 1]
        else:
            return [pairs[-1], pairs[-1]]

    def set_up(self):
        """Do any necessary pre-game processing. (None)"""
        self.bank = 0

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        if isinstance(args[0], TenThousand):
            # Inform the human of the bot's scoring.
            new_bank = self.game.turn_score
            if new_bank == 0:
                self.bank = new_bank
            elif new_bank != self.bank:
                if new_bank > self.bank:
                    self.game.human.tell('{} banked {} points.'.format(self.name, new_bank - self.bank))
                self.bank = new_bank
        else:
            # Handle other tells the standard way.
            super(TenKBot, self).tell(*args, **kwargs)


class GamblerBot(TenKBot):
    """
    A bot that rolls as often as it's chance of scoring. (TenKBot)

    !! This should be redone to calculate the chance (like ProbabilityBot).

    Class Attributes:
    score_chance: The probability of scoring with n dice. (list of float)

    Overridden Methods:
    roll_or_score
    """

    score_chance = [0.97, 0.33, 0.56, 0.72, 0.84, 0.92, 0.97]

    def roll_or_score(self):
        """Decide whether to roll for more or score what you've got. (str)"""
        # Roll with a chance equal to the chance you will score.
        to_roll = len(self.game.dice.get_held())
        if random.random() < self.score_chance[to_roll]:
            return 'roll'
        else:
            return 'score'


class GeneticBot(TenKBot):
    """
    A bot for a genetic algorithm. (TenKBot)

    The gene is a list of eleven integers, corresponding to the following
    attributes in order: min_value, min_behind, min_mod, min_dice, rolls, turns,
    score_and, combo_ones, combo_fives, plain_ones, plain_fives.

    Class Attributes:
    attributes: The names of the genetic attributes. (list of str)
    ranges: The randrange parameters for each attribute. (list of tuple)

    Attributes:
    combo_fives: How many fives to save with a combo. (int)
    combo_ones: How many ones to save with a combo. (int)
    genes: The numbers defining the bot's strategy. (list of int)
    min_behind: The minimum distance behind the leader to stop at. (int)
    min_dice: The minimum number of dice the bot will roll with. (int)
    min_mod: How many points behind adjust min_value by 50. (int)
    min_value: The minumum value to stop with. (int)
    p_zero: The probability that a random gene in 0. (float)
    plain_fives: How many fives to save without a combo. (int)
    plain_ones: How many ones to save without a combo. (int)
    rolls: The number of rolls to make each turn. (float)
    rolls_taken: How many rolls have been made this turn. (int)
    score_and: A flag for combining score determinations with 'and'. (int)
    scoring_turns: How many turns you've score on. (int)
    turns: The number of turns to try to win the game in. (int)

    Methods:
    breed: Combine genes with another bot to produce a third. (GeneticBot)
    fill_random: Fill out the genes with random values. (None)

    Overridden Methods:
    __init__
    hold
    roll_or_score
    set_up
    """

    attributes = ['min_value', 'min_behind', 'min_mod', 'min_dice', 'rolls', 'turns', 'score_and',
        'combo_ones', 'combo_fives', 'plain_ones', 'plain_fives']
    ranges = [(50, 801, 50), (-700, 101, 50), (500, 1301, 50), (1, 7), (1, 9), (1, 10), (2,),
        (1, 3), (1, 3), (1, 3), (1, 3)]

    def __init__(self, genes = None, p_zero = 0.5, taken_names = []):
        """
        Save the genetic material. (None)

        Parameter:
        gene: The numbers defining the bot's strategy. (list of int)
        p_zero: The probability that a random gene in 0. (float)
        """
        # Store the parameters.
        super(GeneticBot, self).__init__(taken_names = taken_names)
        self.genes = [] if genes is None else genes
        self.p_zero = p_zero
        # Fill out the genes as needed.
        if len(self.genes) < len(self.attributes):
            self.fill_random()

    def breed(self, other):
        """
        Combine genes with another bot to produce a third. (GeneticBot)

        Parameters:
        other: The other parent bot. (GeneticBot)
        """
        child = []
        for mine, theirs in zip(self.genes, other.genes):
            if random.random() < 0.5:
                child.append(mine)
            else:
                child.append(theirs)
        return GeneticBot(child)

    def fill_random(self):
        """Fill out the genes with random values. (None)"""
        for parameters in self.ranges[len(self.genes):]:
            if random.random() < self.p_zero:
                self.genes.append(random.randrange(*parameters))
            else:
                self.genes.append(0)

    def hold(self):
        """Determine the hold command (which dice to hold). (str)"""
        # Get what rolls have been made.
        values = self.game.dice.get_free().values[:]
        values.sort()
        counts = [values.count(value) for value in range(7)]
        # Find any combos in the roll.
        combo = True
        # Check for special scoring.
        if values == [1, 2, 3, 4, 5, 6] and self.game.straight:
            hold = values[:]
        elif counts.count(2) == 3 and self.game.three_pair:
            hold = values[:]
        elif 2 in counts and 3 in counts and self.game.full_house:
            if counts[1] == 1 or counts[5] == 1:
                hold = values[:]
            else:
                hold = [counts.index(3)] * 3 + [counts.index(2)] * 2
        # Check for n-of-a-kind.
        elif max(counts) >= 3:
            hold = []
            combos = [(value, count) for value, count in enumerate(counts) if count >= 3]
            for value, count in combos:
                holdable = max([size for size in self.combo_sizes if size <= count])
                hold.extend([value] * holdable)
        # Set up for holding with no combos.
        else:
            hold = []
            combo = False
        self.score_hold = []
        # Score loose ones.
        loose_ones = counts[1] - hold.count(1)
        if loose_ones:
            if combo:
                max_ones = min(loose_ones, self.combo_ones)
            else:
                max_ones = min(loose_ones, self.plain_ones)
            hold.extend([1] * max_ones)
            if max_ones < loose_ones:
                self.score_hold.extend([1] * (loose_ones - max_ones))
        # Score loose fives.
        loose_fives = counts[5] - hold.count(5)
        if loose_fives:
            if combo:
                max_fives = min(loose_fives, self.combo_fives)
            else:
                max_fives = min(loose_fives, self.plain_fives)
            hold.extend([5] * max_fives)
            if max_fives < loose_fives:
                self.score_hold.extend([5] * (loose_fives - max_fives))
        # Make sure something is held.
        if not hold:
            hold = [1] if counts[1] else [5]
            if hold[0] in self.score_hold:
                self.score_hold.remove(hold[0])
        # Hold 'em.
        return 'hold {}'.format(' '.join(map(str, hold)))

    def roll_or_score(self):
        """Deicide whether to roll for more points or score what you have. (str)"""
        # Prep tracking and general calculations.
        score_choices = []
        if not self.game.turn_score:
            self.rolls_taken = 0
        me_now = self.game.scores[self] + self.game.turn_score
        best_other = max([score for player, score in self.game.scores.items() if player != self])
        # Make the individual score choices.
        if self.min_value:
            if self.min_mod:
                mod = 50 * round((best_other - me_now) / self.min_mod)
            else:
                mod = 0
            score_choices.append(self.game.turn_score >= self.min_value + mod)
        if self.min_behind:
            score_choices.append(best_other - me_now <= self.min_behind)
        if self.min_dice:
            score_choices.append(len(self.game.dice.get_free()) < self.min_dice)
        if self.rolls:
            score_choices.append(self.rolls_taken >= self.rolls)
        if self.turns and self.turns != self.scoring_turns:   # Avoid division by zero.
            target = (self.game.win - self.game.scores[self]) / (self.scoring_turns - self.turns)
            score_choices.append(self.game.turn_score >= target)
        # Combine the score choices.
        if self.score_and:
            score = all(score_choices)
        else:
            score = any(score_choices)
        # Determine the move and update tracking.
        if score:
            self.scoring_turns += 1
            self.rolls_taken = 0
            move = 'hold' if self.score_hold else 'score'
            self.score_hold = []
        else:
            self.rolls_taken += 1
            move = 'roll'
        return move

    def set_up(self):
        """Store the genes in attributes."""
        super(GeneticBot, self).set_up()
        for attr, value in zip(self.attributes, self.genes):
            setattr(self, attr, value)
        # Set up tracking variables.
        self.rolls_taken = 0
        self.scoring_turns = 0
        self.score_hold = []
        # Determine which combos can be held.
        self.combo_sizes = [3]
        if self.game.four_kind or self.game.four_mult:
            self.combo_sizes.append(4)
        if self.game.five_kind or self.game.five_mult:
            self.combo_sizes.append(5)
        if self.game.six_kind or self.game.six_mult:
            self.combo_sizes.append(6)


class BasePaceBot(GeneticBot):
    """
    A bot that tries to score ammount and stay close to the lead. (GeneticBot)

    Overridden Methods:
    __init__
    """
    attributes = ['min_value', 'min_behind', 'min_mod', 'min_dice', 'rolls', 'turns', 'score_and',
        'combo_ones', 'combo_fives', 'plain_ones', 'plain_fives']

    def __init__(self, base = 300, pace = 250, taken_names = []):
        """
        Initialize the bot's parameters. (None)

        Parameters:
        base: The minimum points to score each round. (int)
        pace: The minimum points behind the leader. (int)
        taken_names: The names of other players. (list of str)
        """
        genes = [base, pace, 0, 0, 0, 0, 1, 0, 0, 1, 1]
        super(BasePaceBot, self).__init__(genes, taken_names = taken_names)


class ModifierBot(GeneticBot):
    """
    A bot that modifies it's target score by how far it's behind. (GeneticBot)

    Overridden Methods:
    __init__
    """

    def __init__(self, base = 350, modifier = 350, taken_names = []):
        """
        Initialize the bot's parameters. (None)

        Parameters:
        base: The minimum points to score each round. (int)
        modifier: The ammount behind to justify changing the base. (int)
        taken_names: The names of other players. (list of str)
        """
        genes = [base, 0, modifier, 0, 0, 0, 1, 0, 0, 1, 1]
        super(ModifierBot, self).__init__(genes, taken_names = taken_names)


class ValueBot(GeneticBot):
    """
    A bot that tries to score a set number of points each round. (GeneticBot)

    Overridden Methods:
    __init__
    """

    def __init__(self, value = 400, taken_names = []):
        """
        Initialize the bot's parameters. (None)

        Parameters:
        value: The minimum points to score each round. (int)
        taken_names: The names of other players. (list of str)
        """
        genes = [value, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2]
        super(ValueBot, self).__init__(genes, taken_names = taken_names)


class KniziaBot(TenKBot):
    """
    A bot following Reiner Knizia's Strategy. (TenKBot)

    Almost. It leaves out one detail at the end which didn't seem worth
    programming.

    Overridden Methods:
    carry_on
    hold
    roll_or_score
    set_up
    """

    def carry_on(self):
        """Decide whether or not to carry on. (str)"""
        return '0'

    def hold(self):
        """Determine the hold command (which dice to hold). (None)"""
        # Calculate the values used in the decision making.
        possibles = self.game.dice.get_free()
        counts = [possibles.count(value) for value in range(7)]
        dice_thrown = len(possibles)
        max_points = self.game.score_dice(possibles, validate = False)
        max_overall = max_points + self.game.turn_score
        move = 'hold'
        # Stop with 350 points.
        if max_overall >= 350:
            self.score = True
        # For six dice, hold minimally without three of kind, and roll unless you get a bad 300.
        elif dice_thrown == 6:
            # Handle rerolls after scoring all six dice.
            # !! Add handling for straights and three pair.
            if self.game.turn_score > 2850:
                self.score = True
            elif self.game.turn_score > 1550:
                if max_points >= 200:
                    self.score = True
                else:
                    move = 'hold 1' if counts[1] else 'hold 5'
            elif self.game.turn_score > 900:
                if max_points >= 250 or counts[2] >= 3:
                    self.score = True
                else:
                    move = 'hold 1' if counts[1] else 'hold 5'
            elif self.game.turn_score:
                if max_points >= 300 or (counts[2] >= 3 and not (counts[1] + counts[5])):
                    self.score = True
                else:
                    move = 'hold 1' if counts[1] else 'hold 5'
            # Handle initial rolls.
            elif counts[2] >= 3:
                if counts[5] == 2:
                    self.score = True
            elif counts[3] < 3 and counts[1]:
                move = 'hold {}'.format(' '.join(['1'] * counts[1]))
            elif counts[3] < 3:
                move = 'hold 5'
        # For five dice, hold minimally and roll without three of a kind, score otherwise.
        elif dice_thrown == 5:
            if counts[2] >= 3:
                self.score = True
            elif counts[1] == 2:
                if counts[5]:
                    self.score = True
            else:
                move = 'hold 1' if counts[1] else 'hold 5'
        # For four dice, hold minimally unless three 2's, score on three 2's or three individual 1's.
        elif dice_thrown == 4:
            if counts[2] >= 3:
                self.score = True
            if max_overall == 300:
                if max_points == 100 and counts[1]:
                    move = 'hold 1'
                else:
                    self.score = True
            else:
                move = 'hold 1' if counts[1] else 'hold 5'
        # Otherwise score whatever you have, unless you have a bunch of individual fives.
        elif (dice_thrown == 3 and max_overall == 200) or (dice_thrown == 2 and max_overall == 250):
            move = 'hold 5'
        else:
            self.score = True
        return move

    def roll_or_score(self):
        """Decide whether to roll for more or score what you've got. (str)"""
        # Score when the strategy says to, unless you have scored on all dice.
        to_roll = len(self.game.dice.get_free())
        if self.score and to_roll:
            move = 'score'
        elif self.game.must_score:
            move = 'score' if self.game.turn_score >= 350 or to_roll < 2 else 'roll'
        else:
            move = 'roll'
        self.score = False
        return move

    def set_up(self):
        """Do any necessary pre-game processing. (None)"""
        super(KniziaBot, self).set_up()
        self.score = False


class ProbabilityBot(TenKBot):
    """
    A bot using expected values. (TenKBot)

    Overridden Methods:
    roll_or_score
    set_up
    """

    def roll_or_score(self):
        """Decide whether to roll or to score the current points. (str)"""
        # Calculate the expected value of the roll.
        num_dice = len(self.game.dice.get_free())
        ev = self.chances[num_dice]['p-zero'] * -self.game.turn_score
        ev += self.chances[num_dice]['expected'] * (1 - self.chances[num_dice]['p-zero'])
        return 'roll' if ev > 0 else 'score'

    def set_up(self):
        """Make the probablity calculations. (None)"""
        super(ProbabilityBot, self).set_up()
        # Calculate the probabilites.
        self.chances = {}
        # Calculate for each possible number of dice rolled.
        for num_dice in range(1, 7):
            # Score all possible rolls.
            rolls = itertools.product(*[range(1, 7) for die in range(num_dice)])
            points = [self.game.score_dice(roll, False) for roll in rolls]
            # Store chance of no score and average scoring roll.
            num_zero = points.count(0)
            self.chances[num_dice] = {}
            self.chances[num_dice]['p-zero'] = num_zero / 6 ** num_dice
            self.chances[num_dice]['expected'] = sum(points) / (6 ** num_dice - num_zero)
        self.chances[0] = self.chances[6]


class TenThousand(game.Game):
    """
    A game of TenThousand. (game.Game)

    Class Attributes:
    combo_scores: The scores for the basic sets of die values. (list of list of int)

    Attributes:
    carry_on: A flag for being able to take over a failed roll. (bool)
    clear_combo: A flag for having to reroll if you match the last combo. (bool)
    crash: How many points are lost for not scoring on any dice. (int)
    dice: The dice used to play the game. (dice.Pool)
    entered: The players who have entered the game. (dict of str: bool)
    entry: How many points are needed on the first scoring turn. (int)
    explosion: A flag for losing when you roll a max combo of ones. (bool)
    fast: A flag for removing end of turn warnings. (bool)
    five_dice: A flag for using five dice instead of six. (bool)
    five_kind: The points scored for five of a kind. (int)
    five_mult: The points times the value of a five of a kind. (int)
    force_combo: A flag for being forced to roll after a combo. (bool)
    force_six: A flag for being forced to roll after scoring on all dice. (bool)
    four_kind: The points scored for four of a kind. (int)
    four_mult: The points times the value of a four of a kind. (int)
    full_house: The bonus points scored by the pair in a full house. (int)
    last_combo: The values of any combos rolled in the last roll. (list of int)
    last_player: The player who gets the last roll. (player.Player)
    held_this_turn: A flag for dice having been held this turn. (bool)
    instant_win: A flag for winning when rolling a max combo of sixes. (bool)
    min_grows: A flag for having to beat the previous players turn score. (bool)
    minimum: The minimum number of points needed to score each turn. (int)
    must_roll: The reason for being forced to roll the dice again. (str)
    must_score: A flag for being forced to hold all scoring dice. (bool)
    new_turn: A flag for this action being the start of a new turn. (bool)
    no_risk: A flag for scoring your turn score when you roll no points. (bool)
    second_chance: A flag for allowing second chances on failed rolls. (bool)
    six_kind: The points scored for six of a kind. (int)
    six_mult: The points times the value of a six of a kind. (int)
    straight: The points scored for a six die straight. (int)
    strikes: The number of times each player has not scored. (dict of str: int)
    super_strikes: A flag for losing all points after three strikes. (bool)
    three_pair: The point scored for rolling three pair. (int)
    three_strikes: How many points you lose for not scoring three times. (int)
    train_wreck: A flag for losing all points for not scoring on any dice. (bool)
    wild: A flag for having one die having a wild face. (bool)
    win: The points needed to win the game. (int)
    zen: How many points you score for not scoring on any dice. (int)

    Methods:
    do_hold: Process commands to hold dice. (True)
    do_roll: Process commands to roll the dice. (bool)
    do_score: Process commands to score the points rolled this turn. (bool)
    end_turn: Reset the tracking variables for the next player. (None)
    no_score: Handle rolls that do not score. (bool)
    retry: Handle second chances for rolls that do not score. (bool)
    score_dice: Calcuate the score for a set of dice. (int)
    wild_roll: Handle a wild being rolled. (None)

    Overridden Methods:
    __str__
    game_over
    handle_options
    player_action
    set_options
    setup
    """

    aka = ['Zilch', 'Dice 10,000', 'Dice 10000', 'Dice 10K', 'Farkle', '10K']
    aliases = {'h': 'hold', 'r': 'roll', 's': 'score'}
    bot_classes = {'base-pace': BasePaceBot, 'gamble': GamblerBot, 'knizia': KniziaBot, 'mod': ModifierBot,
        'prob': ProbabilityBot, 'random': GeneticBot, 'value': ValueBot}
    categories = ['Dice Games']
    combo_scores = [[0], [0, 100, 200, 1000, 1100, 1200, 2000], [0, 0, 0, 200, 0, 0, 400],
        [0, 0, 0, 300, 0, 0, 600], [0, 0, 0, 400, 0, 0, 800],
        [0, 50, 100, 500, 550, 600, 1000], [0, 0, 0, 600, 0, 0, 1200]]
    credits = CREDITS
    name = 'Ten Thousand'
    num_options = 30
    options = OPTIONS
    rules = RULES

    def __str__(self):
        """Human readable text representation. (str)"""
        score_text = '\n'.join('{}: {}'.format(name, score) for name, score in self.scores.items())
        full_text = '\nScores:\n{}\n\nYou have banked {} points this turn.\nThe roll to you is {}.'
        if self.min_grows:
            if self.entry and not self.entered[self.current_player]:
                min_roll = max(self.minimum, self.entry)
            else:
                min_roll = self.minimum
            full_text = '{}\nThe minimum turn score is {}.'.format(full_text, min_roll)
        return full_text.format(score_text, self.turn_score, self.dice)

    def do_gipf(self, arguments):
        """
        Winning Yacht gives you one reroll this turn.

        Winning Yukon allows you to change one unheld die by one pip.
        """
        # Run the edge, if possible.
        game, losses = self.gipf_check(arguments, ('pyramid', 'yukon'))
        # Winning Yacht gives you a choice between two rolls.
        if game == 'pyramid':
            if not losses:
                self.reroll = True
        # Winning Yukon allows you to change a die by one pip.
        elif game == 'yukon':
            if not losses:
                unheld = self.dice.get_free()
                self.current_player.tell('\nYour unheld dice are: {}.'.format(unheld))
                query = 'Which value would you like to change? '
                value = self.current_player.ask_int(query, valid = unheld, cmd = False)
                if value == 1:
                    change = 2
                    self.current_player.tell('Ones can only be changed to twos.')
                elif value == 6:
                    change = 5
                    self.current_player.tell('Sixes can only be changed to fives.')
                else:
                    query = 'What would you like to change it to? '
                    change = self.current_player.ask_int(query, valid = (value - 1, value + 1), cmd = False)
                die = [die for die in self.dice if not die.held and die == value][0]
                die.value = change
        # Otherwise I'm confused.
        else:
            self.human.tell('Like, well, I mean, you know ... What was the question again?')
        return True

    def do_hold(self, arguments):
        """
        Hold (set aside) scoring dice. (h)

        The values of the dice should be the arguments. If no arguments are given, all
        scoring dice are held. You can only hold scoring dice. For taking a second
        chance to score, use the second command.
        """
        # !! refactor
        player = self.players[self.player_index]
        possibles = self.dice.get_free()
        counts = possibles.counts()
        # Process the arguments.
        if arguments.strip():
            # Split out the individual values to hold.
            for delimiter in ',;/':
                if delimiter in arguments:
                    values = arguments.split(delimiter)
                    break
            else:
                values = arguments.split()
            # Convert the values to integers.
            try:
                values = list(map(int, values))
            except ValueError:
                player.tell('Invalid arguments to hold command: {!r}'.format(arguments))
                return True
            # Check against the unheld dice.
            v_counts = [values.count(value) for value in range(7)]
            if any(value > possible for value, possible in zip(v_counts, counts)):
                player.error('You do not have those dice to hold.')
                return True
        else:
            # Hold all scoring dice if no arguments are given.
            # Check for special combos.
            if sorted(possibles) == [1, 2, 3, 4, 5, 6] and self.straight:
                values = possibles
            elif counts.count(2) == 3 and self.three_pair:
                values = possibles
            elif 3 in counts and 2 in counts and self.full_house:
                values = [value for value in possibles if counts[value] in (2, 3)]
                # Check for loose 1 or 5 with three of a kind.
                if counts[1] == 1:
                    values.append(1)
                elif counts[5] == 1:
                    values.append(5)
            else:
                # Otherwise, get any combos or loose dice.
                values = []
                for possible in set(possibles.values):
                    for count in range(counts[possible], 0, -1):
                        if self.combo_scores[possible][count]:
                            values.extend([possible] * count)
                            break
        values.sort()
        # Check for holding combos (clear-combo and force-combo options).
        if self.clear_combo or self.force_combo:
            for first, third in zip(values, values[2:]):
                if first == third and first not in self.last_combo:
                    self.last_combo.append(first)
                    if self.force_combo:
                        self.must_roll = "you scored three or more {}'s".format(first)
        # Score the held dice.
        held_score = self.score_dice(values)
        if held_score < 0:
            possible = abs(held_score)
            count = values.count(possible)
            error = "{} {}'s do not score and cannot be held"
            player.error(error.format(utility.number_word(count), possible))
            return True
        # Record the score and hold the dice.
        self.dice.hold(values)
        self.turn_score += held_score
        self.held_this_turn = True
        # Check for holding all of the dice (force-six option).
        if self.force_six and not self.dice.get_free():
            self.must_roll = 'you scored on all {} dice'.format(len(self.dice))
        return True

    def do_roll(self, arguments):
        """
        Roll the unheld dice. (r)

        If all of the dice are held, all of the dice are rerolled.
        """
        player = self.current_player
        # Check for having held dice.
        if not (self.held_this_turn or self.new_turn or self.must_roll):
            player.error('You must hold dice before you can roll.')
            return True
        # Reset the dice if they've all been rolled.
        if not self.dice.get_free():
            self.dice.release()
        # Roll the dice.
        self.must_roll = ''
        self.dice.roll()
        # Handle any rerolls:
        if self.reroll:
            rolled = self.dice.get_free()
            if player.ask_yes_no('Your roll is {}. Would you like to reroll? '.format(rolled)):
                self.dice.roll()
                self.reroll = False
        # Handle any wilds.
        if self.wild and -1 in self.dice:
            self.wild_roll(player)
        # Make sure any combos have been cleared (clear-combo option).
        if self.clear_combo and self.last_combo:
            rolled = self.dice.get_free()
            if self.wild and -1 in rolled:
                self.wild_die(player)
            message = 'You must reroll because you matched the last combo.'
            while any(combo in rolled for combo in self.last_combo):
                player.tell('You rolled: {}.'.format(', '.join(map(str, rolled))))
                player.tell(message)
                self.dice.roll()
                if self.wild and -1 in self.dice:
                    self.wild_roll(player)
            self.last_combo = []
        self.held_this_turn = False
        values = sorted(self.dice.get_free().values)
        player.tell('\n{} rolled: {}.'.format(player, ', '.join([str(value) for value in values])))
        # Check for no score (end the turn if there isn't).
        roll_score = self.score_dice(values, validate = False)
        go = True
        if not roll_score:
            go = self.no_score(player, values)
        # Check for too many points.
        elif self.explosion and values == [1] * len(self.dice):
            player.tell("You rolled {} ones. That is too many points, so you lose.".format(len(self.dice)))
            self.scores[player] = 0
            self.players.remove(player)
            self.player_index -= 1
            return False
        # Check for an instant win.
        elif self.instant_win and values == [6] * len(self.dice):
            player.tell("You rolled {} sixes. You win instantly.".format(len(self.dice)))
            self.scores[player] = max(self.win, max(self.scores.values() + 50))
            self.last_player = player
            return False
        # Check for mandatory scoring.
        if go and self.must_score:
            self.do_hold('')
        elif not go:
            if self.fast:
                player.tell('Your turn is over.')
            else:
                player.ask('Your turn is over, press Enter to contine: ')
        return go

    def do_score(self, arguments):
        """
        End the turn and score the points you rolled this turn. (s)
        """
        player = self.current_player
        # Check for forced rolls and invalid stops.
        if not self.held_this_turn:
            player.error('You cannot stop without holding some scoring dice.')
        elif self.turn_score < self.minimum:
            player.error('You cannot stop until you score {} points.'.format(self.minimum))
        elif self.turn_score < self.entry and not self.entered[player]:
            player.error('You cannot stop the first time until you score {} points.'.format(self.entry))
        elif self.must_roll:
            player.error('You must roll because {}.'.format(self.must_roll))
        else:
            # Score the dice.
            self.scores[player] += self.turn_score
            # Clear the tracking variables.
            self.entered[player] = True
            self.strikes[player] = 0
            if self.min_grows:
                self.minimum = self.turn_score + 50
            self.end_turn()
            return False
        return True

    def end_turn(self):
        """Reset the tracking variables for the next player. (None)"""
        self.held_this_turn = False
        self.last_combo = []
        self.turn_score = 0
        self.dice.release()
        self.reroll = False
        self.new_turn = True

    def game_over(self):
        """Determine if the game is over. (bool)"""
        # Check for a winning score.
        if max(self.scores.values()) >= self.win:
            player = self.players[self.player_index]
            # Announce last licks and set the last player, if there isn't one.
            if self.last_player is None:
                self.last_player = self.players[self.player_index - 1]
                warning = 'Everyone gets one roll to beat {}. {} gets the last roll.'
                self.human.tell(warning.format(player, self.last_player))
                return False
            elif player == self.last_player:
                # End the game.
                self.human.tell('Final Scores:')
                score_text = '\n'.join('{}: {}'.format(name, score) for name, score in self.scores.items())
                self.human.tell(score_text)
                self.wins_by_score(show_self = False)
                return True
        else:
            # Continue the game.
            return False

    def handle_options(self):
        """Handle the game options. (None)"""
        super(TenThousand, self).handle_options()
        # Handle the combo scoring.
        kinds = [self.four_kind, self.five_kind, self.six_kind]
        mults = [self.four_mult, self.five_mult, self.six_mult]
        self.combo_sizes = [3]
        for size, kind, mult in zip((4, 5, 6), kinds, mults):
            if kind or mult:
                self.combo_sizes.append(size)
        for value in range(1, 7):
            for count, kind, mult in zip(range(4, 7), kinds, mults):
                # Check for a set score option.
                if kind:
                    self.combo_scores[value][count] = kind
                # If no set score, check for a multiplier option.
                elif mult:
                    # Ones multiply as tens
                    if value == 1:
                        self.combo_scores[value][count] = mult * 10
                    else:
                        self.combo_scores[value][count] = mult * value
        # Set up the dice.
        if self.five_dice:
            self.dice = dice.Pool([6] * 5)
        else:
            self.dice = dice.Pool([6] * 6)
        # Set the wild.
        if self.wild:
            self.dice.dice[-1].sides[1] = -1

    def no_score(self, player, values):
        """
        Handle rolls that do not score. (bool)

        Parameters:
        player: The current player. (player.Player)
        values: The faces of the unrolled dice. (list of int)
        """
        # Alert the player.
        player.tell('{} did not score with that roll.'.format(player.name))
        # Check for second chances.
        if self.second_chance and self.retry(player, values):
            return True
        elif self.second_chance:
            # Recalculate value list after rolls in retry.
            values = self.dice.get_free().values
        # Score anyway if the no-risk option is in effect..
        if self.no_risk:
            player.tell('{} scored {} points this turn.'.format(player, self.turn_score))
            self.scores[player] += self.turn_score
        elif not self.zen:
            # Record strikes and check for three strikes.
            self.strikes[player] += 1
            if self.strikes[player] == 3:
                self.strikes[player] = 0
                if self.three_strikes:
                    message = '{} gets three strikes, and loses {} points.'
                    player.tell(message.format(player, self.three_strikes))
                    self.scores[player] = max(self.scores[player] - self.three_strikes, 0)
                elif self.super_strikes:
                    player.tell('Three strikes, you lose all of your points.')
                    self.scores[player] = 0
        # Check for failing to score on all six dice (crash/train-wreck/zen options)
        if not self.dice.get_held():
            # Lose some points.
            if self.crash:
                player.tell('That is a crash, you lose {} points.'.format(self.crash))
                self.scores[player] = max(0, self.scores[player] - self.crash)
            # Lose all points.
            elif self.train_wreck:
                player.tell('That is a train wreck, you lose all of your points.')
                self.scores[player] = 0
            # Score some points.
            elif self.zen:
                player.tell('How Zen.'.format(player, self.zen))
                self.turn_score += self.zen
                self.dice.hold(values)
                self.held_this_turn = True
                return True
        # Let the next player keep going if the carry-on option is in effect.
        if self.carry_on and player != self.last_player:
            next_player = self.get_next_player()
            query = "Would you like to carry on with {}'s points and dice? "
            if next_player.ask(query.format(player)) in utility.YES:
                self.must_roll = "you chose to carry on {}'s roll".format(player)
                self.held_this_turn = True
                return False
        # Reset for the next turn.
        self.end_turn()
        if self.min_grows:
            self.minimum = 0
        return False

    def player_action(self, player):
        """
        Handle a player's action. (bool)

        Parameters:
        player: The current player.
        """
        # Make the initial roll for the player if needed.
        if self.new_turn:
            # Check for a train wreck.
            if not self.do_roll(''):
                return False
            self.new_turn = False
        # Show the game status.
        player.tell(self)
        # Make a forced roll, if necessary.
        if self.must_roll:
            player.tell('You must roll because {}.'.format(self.must_roll))
        # Get and handle the player's move.
        move = player.ask('\nWhat is your move? ')
        return self.handle_cmd(move)

    def retry(self, player, values):
        """
        Handle second chances for rolls that do not score. (bool)

        Parameters:
        player: The current player. (player.Player)
        values: The faces of the unrolled dice. (list of int)
        """
        # Check for enough dice and a possible completion.
        counts = [values.count(possible) for possible in range(7)]
        straightable = self.straight and len(values) == len(self.dice)
        if (len(values) < 3 or max(counts) == 1) and not straightable:
            return False
        # Check for multiple options.
        if counts.count(2) > 1 or straightable:
            while True:
                keepers = player.ask_int_list('Which dice would you like to take a second chance with? ')
                # Check for a pair or singletons.
                if (len(keepers) == 2 and keepers[0] == keepers[1]) or (len(keepers) == len(set(keepers))):
                    # Check for straights being legal. !! chk max # dice
                    if keepers[0] != keepers[1] and not self.straight:
                        player.error('You can only keep different dice if straights are allowed.')
                    elif keepers[0] != keepers[1] and not straightable:
                        player.error('You do not have the right dice to complete a straight.')
                    # Check for having the dice.
                    elif all([keepers.count(roll) <= values.count(roll) for roll in range(7)]):
                        break
                    else:
                        player.error('You do not have those dice to keep.')
                else:
                    player.error('You can only hold back a pair or single values.')
        # Make any mandatory choice.
        elif counts.count(2):
            keepers = [counts.index(2)] * 2
            player.tell('Holding back a pair of {}s'.format(keepers[0]))
        # Hold back the dice.
        base, to_roll = [], []
        if keepers[0] == keepers[1]:
            for die in self.dice:
                if die == keepers[0] and not die.held:
                    base.append(die)
                elif not die.held:
                    to_roll.append(die)
        else:
            for die in self.dice:
                if not (die.held or die in base):
                    base.append(die)
                elif not die.held:
                    to_roll.append(die)
        # Roll the dice.
        for die in to_roll:
            die.roll()
        if self.wild and -1 in self.dice:
            self.wild_roll()
        player.tell('You rolled: {}.'.format(', '.join(map(str, to_roll))))
        # Check for a match.
        if keepers[0] == keepers[1]:
            if keepers[0] in to_roll:
                player.tell('You matched the pair.')
                return True
        else:
            new_values = [die.value for die in base + to_roll]
            if len(set(new_values)) == len(self.dice):
                player.tell('You completed the straight.')
                return True
        # Note a failed match.
        player.tell('You failed to match the kept dice.')
        return False

    def set_options(self):
        """Set the options for the game. (None)"""
        # Note that cosmic wimpout is zilch / cc cr d0 e=350 5d fc f6 m=0 ns ss tw wild w=5000
        # Add name variants.
        self.option_set.add_group('5000', ['5k'], 'w=5000')
        self.option_set.add_group('wimpout', ['wo'], '5d e=350 5m=1000 wd fc cc f6 w=5000 ms')
        gonzo = '3p=600 s=1500 fh=250 4m=200 5m=400 6m=800 3s=500 tw co cc fc f6 e=350 mg 2c ex iw wd'
        self.option_set.add_group('gonzo', ['gz'], gonzo)
        # Set the bot options.
        self.option_set.default_bots = ((ProbabilityBot, ()), (ValueBot, ()), (ModifierBot, ()))
        self.option_set.add_option('base-pace', ['bp'],  action = 'bot', target = 'base-pace', value = (),
            default = None)
        self.option_set.add_option('gambler', ['gm'],  action = 'bot', target = 'gamble', value = (),
            default = None)
        self.option_set.add_option('knizia', ['kz'],  action = 'bot', target = 'knizia', value = (),
            default = None)
        self.option_set.add_option('mod', ['md'],  action = 'bot', target = 'mod', value = (),
            default = None)
        self.option_set.add_option('prob', ['pb'],  action = 'bot', target = 'prob', value = (),
            default = None)
        self.option_set.add_option('random', ['rd'],  action = 'bot', target = 'random', value = (),
            default = None)
        self.option_set.add_option('value', ['vu'],  action = 'bot', target = 'value', value = (),
            default = None)
        # Set the scoring options.
        self.option_set.add_option('crash', ['cr'], int, 0,
            question = 'How many points should you lose for not scoring on all dice (return for 0)? ')
        self.option_set.add_option('five-kind', ['5k'], int, 0,
            question = 'How much should five of a kind score (return for 0)? ')
        self.option_set.add_option('five-mult', ['5m'], int, 0,
            question = 'How much should the multiplier be for five of a kind (return for 0)? ')
        self.option_set.add_option('four-kind', ['4k'], int, 0,
            question = 'How much should four of a kind score (return for 0)? ')
        self.option_set.add_option('four-mult', ['4m'], int, 0,
            question = 'How much should the multiplier be for four of a kind (return for 0)? ')
        self.option_set.add_option('full-house', ['fh'], int, 0,
            question = 'What should the bonus for a full house be (return for 0)? ')
        self.option_set.add_option('must-score', ['ms'],
            question = 'Should you have to hold all scoring dice? bool')
        self.option_set.add_option('six-kind', ['6k'], int, 0,
            question = 'How much should six of a kind score (return for 0)? ')
        self.option_set.add_option('six-mult', ['6m'], int, 0,
            question = 'How much should the multiplier be for six of a kind (return for 0)? ')
        self.option_set.add_option('straight', ['s'], int, 0,
            question = 'How much should a straight score (return for 0)? ')
        self.option_set.add_option('super-strikes', ['ss'],
            question = 'Should you lose all of your points for not scoring three times in a row? bool')
        self.option_set.add_option('three-pair', ['3p'], int, 0,
            question = 'How much should three pair score (return for 0)? ')
        self.option_set.add_option('three-strikes', ['3s'], int, 0,
            question = 'How much should you lose for not scoring three times in a row (return for 0)? ')
        self.option_set.add_option('train-wreck', ['tw'],
            question = 'Should you lose all of your points for not scoring on all dice? bool')
        self.option_set.add_option('zen', ['z'], int, 0,
            question = 'How many points should you *GAIN* for not scoring on all dice (return for 0)? ')
        # Set the stopping options.
        self.option_set.add_option('carry-on', ['co'],
            question = "Should you be able to take on the previous player's failrd roll and points? bool")
        self.option_set.add_option('clear-combo', ['cc'],
            question = 'Should you have to reroll if you match thr last combo you scored? bool')
        self.option_set.add_option('entry', ['e'], int, 0,
            question = 'How many points should be required to stop the first time (return for 0)? ')
        self.option_set.add_option('force-combo', ['fc'],
            question = "Should you have to keep rolling after scoring three or more of a kind? bool")
        self.option_set.add_option('force-six', ['f6'],
            question = "Should you have to keep rolling after scoring on all of the dice? bool")
        self.option_set.add_option('min-grows', ['mg'],
            question = "Should you have beat the previous player's score? bool")
        self.option_set.add_option('minimum', ['m'], int, 0,
            question = 'How many points should be required to stop in general (return for 0)? ')
        self.option_set.add_option('no-risk', ['nr'],
            question = 'Should you score your banked points no matter what you roll? bool')
        self.option_set.add_option('second-chance', ['2c'],
            question = 'Should you get a second chance roll after a failed roll? bool')
        # Set the end of game options.
        self.option_set.add_option('explosion', ['ex'],
            question = 'Should you lose for rolling all ones on all dice? bool')
        self.option_set.add_option('instant-win', ['iw'],
            question = 'Should you win instantly for rolling all sixes on all dice? bool')
        self.option_set.add_option('win', ['w'], int, 10000,
            question = 'How many points should it take to win (return for 10,000)? ')
        # Set any other options.
        self.option_set.add_option('fast', ['fs'],
            question = 'Should your turn end without a pause? bool')
        self.option_set.add_option('five-dice', ['5d'],
            question = 'Should the game be played with five dice? bool')
        self.option_set.add_option('wild', ['wd'],
            question = 'Should one die have a wild instead of a two? bool? bool')

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the tracking variables.
        self.turn_score = 0
        self.held_this_turn = False
        self.last_combo = []
        self.last_player = None
        self.must_roll = ''
        self.reroll = False
        self.new_turn = True
        self.entered = {player.name: False for player in self.players}
        self.strikes = {player.name: 0 for player in self.players}
        # Randomize the turn order.
        random.shuffle(self.players)

    def score_dice(self, values, validate = True):
        """
        Calcuate the score for a set of dice. (int)

        If validate is True, returns -1 if any values provided don't score. Otherwise,
        calculates the maximum score for the values give.

        Parameters:
        values: The dice rolls to score. (list of int)
        validate: A flag for validating the dice chosen. (bool)
        """
        # Get data on the sets of dice.
        counts = [values.count(possible) for possible in range(7)]
        # Check for straights.
        if values == [1, 2, 3, 4, 5, 6] and self.straight:
            held_score = self.straight
        # Check for three pair.
        elif counts.count(2) == 3 and self.three_pair:
            held_score = self.three_pair
        # Check for full house.
        elif 3 in counts and 2 in counts and self.full_house:
            trip_value = counts.index(3)
            held_score = self.combo_scores[trip_value][3] + self.full_house
            if counts[1] == 1:
                held_score += 100
            elif counts[5] == 1:
                held_score += 50
        # Otherwise, score the sets.
        else:
            held_score = 0
            # Score each set in order.
            for possible, count in enumerate(counts):
                sub_score = self.combo_scores[possible][count]
                if count and not sub_score:
                    if validate:
                        # Return error code for invalid dice if validating.
                        return -possible
                    else:
                        # Otherwise, check for smaller sets that score.
                        for sub_count in range(count, 0, -1):
                            sub_score = self.combo_scores[possible][sub_count]
                            if sub_score:
                                break
                held_score += sub_score
        return held_score

    def wild_roll(self, player):
        """
        Handle a wild being rolled. (None)

        Parameters:
        player: The player who rolled the wild. (player.Player)
        """
        # Get the wild die.
        wild_die = self.dice[self.dice.index(-1)]
        # Get data on the other dice.
        values = [die.value for die in self.dice if not (die.held or die is wild_die)]
        counts = [values.count(possible) for possible in range(7)]
        # Find the combos.
        valid = [value for value, count in enumerate(counts) if count + 1 in self.combo_sizes]
        # Alert the player if there is only one option.
        if len(valid) == 1:
            wild_die.value = valid[0]
            player.tell('\nYou rolled a wild, which must be used as a {}.'.format(valid[0]))
        # If there are multiple options, have the player select one.
        else:
            player.tell('\nYou rolled a wild and {}.'.format(', '.join(map(str, values))))
            if valid:
                query = 'Do you want the wild to be a {}? '.format(utility.oxford(set(valid), 'or'))
                choice = player.ask_int(query, valid = valid, cmd = False)
            else:
                choice = player.ask_int('What do you want the wild to be? ', low = 1, high = 6, cmd = False)
            wild_die.value = choice
