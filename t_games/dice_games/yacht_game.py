"""
yacht_game.py

Yacht and other similar games.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Yacht. (str)
RULES: The rules and options for Yacht. (str)

Scoring Functions:
five_kind: Score the yacht category. (int)
four_kind: Score the four of a kind category. (int)
four_kind_strict: Score the four of a kind category, w/o five of a kind. (int)
full_house: Score the full house category. (int)
full_house_strict: Score the full house category, w/o five of a kind. (int)
score_number: Create a scoring function for a number category. (callable)
straight: Score a straight category. (int)
straight_high: Score a high straight category. (int)
straight_low: Score a low straight category. (int)
straight_wild: Score a straight category with twos wild. (int)
three_kind: Score the three of a kind category. (int)

Classes:
Bacht: A bot to play Yacht. (player.Bot)
Bachter: A bachter Bacht. (Bacht)
ScoreCategory: A category for a category dice game. (object)
Yacht: The game of Yacht and it's cousins. (game.Game)

Other Functions:
validate_score_spec: Validate a score specification. (bool)
"""


import random

import t_games.dice as dice
import t_games.game as game
import t_games.options as options
import t_games.player as player


# The credits for Yacht.
CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

# The rules and options for Yacht.
RULES = """
You start by rolling five dice. You may set any number of the dice aside and
reroll the rest. You may set aside a second time and roll a third time. Dice
that are set aside may not be rerolled that turn. Once you get a final roll,
you choose a category to score it in. Each category may be scored only once.
If you do not meet the criteria for the category, you may still score it, but
it is worth zero points. The game is over when everyone has scored all of the
categories.

To set aside dice, use the hold (h) command, follow by a list of the values
you want to set asside. To roll again, use the roll (r) command. To score, use
the score (s) command followed by either the name of the category or the
character preceding the category in the score table.

The categories (and their scores) are:

Yacht: Five of a kind (50)
Big Straight: 2-3-4-5-6 (30)
Little Straight: 1-2-3-4-5 (30)
Four of a Kind: Four of the same number. (Sum of the four of a kind)
Full House: Two of one number and three of another. (Sum of the dice)
Chance: Any roll. (Sum of the dice)
Sixes: As many sixes as possible. (Sum of the sixes)
Fives: As many fives as possible. (Sum of the fives)
Fours: As many fours as possible. (Sum of the fours)
Threes: As many threes as possible. (Sum of the threes)
Twos: As many twos as possible. (Sum of the twos)
Ones: As many ones as possible. (Sum of the ones)

Options:
easy=: How many easy bots you want to play against.
extra-five=: Each player's second and later five of a kinds score bonus points
    equal to this option.
five-name=: Change the name of the five of a kind category. Underscores are
    converted to spaces.
max-rolls: The maximum number of rolls you can make.
medium=: How many medium bots you want to play against.
n-bonus=: A bonus for getting enough points in ones through sixes. The value
    of this options should be two numbers separated by a slash (the score
    needed/the bonus points).
strict-four: Four of a kind cannot be scored with five of a kind.
strict-full: Full house cannot be scored with five of a kind.
super-five: If you get five of a kind without rerolling, you win isntantly.
wild-straight: Ones can be used as 2 or 6 in straights.

Score Options:
The score options allow changing the scores of the categories. They are done
with 'category-option = score-specification'. The score specification can be
total (sum of the dice), sub-total (sum of the qualifying dice), a number for
a straight score, two numbers separated by a slash (the score if done without
rerolling/the normal score), or total+ a number (sum of the dice plus the
bonus to give). If the score is set to 0, that category is removed from the
game. The category options are: five-kind, big-straight, low-straight,
four-kind, full-house, three-kind, chance, and low-chance. Note that
three-kind and low-chance are not in the normal game. Assigning them a score
specification will add them to the game. The low-chance category must be
lower than the normal chance category. If it is not, the second one scored
counts as 0.

Variant Options:
cheerio: Equivalent to five-name=Cheerio big-straight=25 low-straight=20
    four-kind=0 max-rolls=2
general: Equivalent to five-name=Small_General five-kind=60 four-kind=45/40
    full-house=35/30 big-straight=25/20 low-straight=0 chance=0 super-five
    wild-straight
hindenberg: Equivalent to five-name=Hindenberg five-kind=30 big-straight=20
    low-straight=15 four-kind=0 chance=0
yahtzee: Equivalent to five-name=Yahtzee big-straight=40 full-house=25
    three-kind=total n-bonus=35/63 extra-five=100
yam: Equivalent to five-name=Yam five-kind=total+40 big-straight=total+30
    full-house=total+20 low-chance=total low-straight=0 four-kind=0
    n-bonus=30/60
"""


def five_kind(dice):
    """
    Score the yacht (five of a kind) category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    if values[0] == values[4]:
        return 5 * values[0]
    else:
        return 0


def four_kind(dice):
    """
    Score the four of a kind category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    if values[0] == values[3] or values[1] == values[4]:
        return 4 * values[2]
    else:
        return 0


def four_kind_strict(dice):
    """
    Score the four of a kind category, disallowing five of a kind. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    if (values[0] == values[3] or values[1] == values[4]) and values[0] != values[4]:
        return 4 * values[2]
    else:
        return 0


def full_house(dice):
    """
    Score the full house category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    # Check for low pair.
    if values[0] == values[1] and values[2] == values[4]:
        return sum(values)
    # Check for high pair.
    if values[0] == values[2] and values[3] == values[4]:
        return sum(values)
    else:
        return 0


def full_house_strict(dice):
    """
    Score the full house category, disallowing five of a kind. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    # Check for low pair.
    if values[0] == values[1] and values[2] == values[4] and values[0] != values[4]:
        return sum(values)
    # Check for high pair.
    if values[0] == values[2] and values[3] == values[4] and values[0] != values[4]:
        return sum(values)
    else:
        return 0


def score_number(number):
    """
    Creating a scoring function for a number category. (callable)

    Parameters:
    number: The number of the category. (int)
    """
    def score_value(dice):
        return number * dice.values.count(number)
    return score_value


def straight(dice):
    """
    Score a straight category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    for lower, higher in zip(values, values[1:]):
        if higher - lower != 1:
            break
    else:
        return sum(values)
    return 0


def straight_low(dice):
    """
    Score a low straight category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    if 1 in dice.values:
        return straight(dice)
    else:
        return 0


def straight_high(dice):
    """
    Score a high straight category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    if 6 in dice.values:
        return straight(dice)
    else:
        return 0


def straight_wild(dice):
    """
    Score a straight category with twos wild. (int)

    Twos in a wild straight can count as ones or sixes.

    Parameters:
    dice: The dice roll to score. (int)
    """
    score = straight(dice)
    if not score:
        values = sorted(dice.values)
        if values in ([1, 1, 3, 4, 5], [1, 3, 4, 5, 6]):
            score = sum(values)
    return score


def three_kind(dice):
    """
    Score the three of a kind category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    if values[0] == values[2] or values[1] == values[3] or values[2] == values[4]:
        return 3 * values[2]
    else:
        return 0


class Bacht(player.Bot):
    """
    A bacht to play Yacht. (player.Bot)

    A basic bot for playing Yacht.

    Attributes:
    next: The bacht's next move, if known. (str)

    Methods:
    get_category: Get the category to score a roll in. (str)
    get_holds: Get the dice to hold for the next roll. (list of int)
    initial_holds: Get the holds on the first roll. (list of int)
    later_holds: Get the holds on the second and third rolls. (list of int)

    Overridden Methods:
    ask
    set_up
    """

    def ask(self, query):
        """
        Ask the bacht a question. (str)

        Parameters:
        query: The question to ask of the bacht. (str)
        """
        if query == 'What is your move? ':
            # Check for preset roll.
            if self.next == 'roll':
                self.next = ''
                return 'roll'
            # Check for time to score.
            elif (self.game.roll_count == self.game.max_rolls or self.next == 'score' or
                not self.game.dice.dice):
                move = 'score ' + self.get_category()
            # Otherwise hold dice.
            else:
                move = 'hold ' + ' '.join([str(x) for x in self.get_holds()])
                if move == 'hold ':
                    move = 'roll'
                elif self.game.dice.dice:
                    self.next = 'roll'
                else:
                    self.next = 'score'
        else:
            # Handle unknown questions.
            raise player.BotError('Unexpected query to Bacht: {!r}'.format(query))
        return move

    def get_category(self):
        """Get the category to score the current roll in. (str)"""
        # Get scores for checking used categories.
        my_scores = self.game.category_scores[self.name]
        # Loop through the score categories
        ranking = []
        for category in self.game.score_cats:
            # Save scores for unused categories.
            if my_scores[category.name] is None:
                ranking.append((self.game.score(category, self), category.name))
        # Choose the category that scores the most.
        ranking.sort()
        return ranking[-1][1]

    def get_holds(self):
        """
        Get the dice to hold for the next roll. (list of int)

        If the roll is ready to score, this method holds all of the dice.
        """
        # Hold on first round based on dice values.
        if not self.game.dice.held:
            hold = self.initial_holds()
        # Hold on later rounds by inferring why you held things on early rounds.
        else:
            hold = self.later_holds()
        return hold

    def initial_holds(self):
        """Get the holds on the first roll. (list of int)"""
        # Get local references to commonly used information.
        pending = self.game.dice.dice
        my_scores = self.game.category_scores[self.name]
        # Summarize the dice values.
        counts = [pending.count(value) for value in range(7)]
        ordered = sorted(counts[:], reverse = True)
        pending_low = set([die for die in pending if die < 6])
        pending_high = set([die for die in pending if die > 1])
        # If you have at least two pair, go for full house.
        if ordered[1] > 1:
            hold = [counts.index(ordered[0])] * ordered[0]
            if ordered[0] == ordered[1]:
                hold = [counts.index(ordered[0], counts.index(ordered[0]) + 1)] * ordered[0]
            else:
                hold += [counts.index(ordered[1])] * ordered[1]
        # Three of a kind goes for a run.
        elif ordered[0] > 2:
            hold = [counts.index(ordered[0])] * ordered[0]
        # Then check for straights.
        elif my_scores.get('Little Straight', 0) is None and len(pending_low) > 2:
            hold = pending_low
        elif my_scores.get('Big Straight', 0) is None and len(pending_high) > 2:
            hold = pending_high
        elif my_scores.get('Straight', 0) is None and len(pending_high) > 2:
            hold = pending_high
        # The go for runs from pairs.
        elif ordered[0] > 1:
            hold = [counts.index(ordered[0])] * ordered[0]
        # If all else fails, go for run with highest value.
        else:
            hold = [max(pending)]
        return hold

    def later_holds(self):
        """Get the holds on the second and third rolls. (list of int)"""
        # Get local references to commonly used information.
        held = self.game.dice.held
        pending = self.game.dice.dice
        unique_held = len(set(held))
        # Holding one value means go for a run.
        if unique_held == 1:
            hold = [held[0]] * pending.count(held[0])
        # Holding two values means go for a full house.
        elif unique_held == 2:
            if pending[0] in held:
                hold = pending[:1]
            else:
                hold = []
        # Holding three values means go for a straight.
        elif unique_held > 2:
            hold = list(set([die for die in pending if die not in held]))
            if 6 in hold and 1 in held:
                hold.remove(6)
            elif 1 in hold and 6 in held:
                hold.remove(1)
        return hold

    def set_up(self):
        """Set up the bot. (None)"""
        self.next = ''


class Bachter(Bacht):
    """
    A Bachter Bacht. (Bacht)

    The Bachter takes into account how good his dice are and what the expected
    scores are before going for a category, and the expected scores when choosing
    a category to score in. It also more explicitly indicates to itself what it
    going for based on the first roll.

    Attributes:
    category_data: Target number of dice and score for each category. (dict)
    target: The category the bacht is aiming for. (str)

    Overridden Methods:
    get_category
    initial_holds
    later_holds
    set_up
    """

    def get_category(self):
        """Get the category to score the current roll in. (str)"""
        # Get a local copy of scores for checking used categories.
        my_scores = self.game.category_scores[self.name]
        # Loop through the score categories.
        ranking = []
        for category in self.game.score_cats:
            # Check those that haven't been used.
            if my_scores[category.name] is None:
                # Rank by difference from target score.
                score = category.score(self.game.dice, self.game.roll_count)
                score -= self.category_data[category.name][2]
                # Handle chance category options.
                if category.name == 'Low Chance' and 'Chance' in my_scores:
                    chance = my_scores['Chance']
                    if chance is not None and chance <= score:
                        score = 0
                elif category.name == 'Chance' and 'Low Chance' in my_scores:
                    low_chance = my_scores['Low Chance']
                    if low_chance is not None and score <= low_chance:
                        score = 0
                ranking.append((score, category.name))
        # Score the category that is best compared to its expected score.
        ranking.sort()
        return ranking[-1][1]

    def initial_holds(self):
        """Get holds on the first roll. (list of int)"""
        # Get a local copy of scores for checking used categories.
        my_scores = self.game.category_scores[self.name]
        num_cats = ('Zeros', 'Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes')
        # Summarize the current roll.
        counts = [(self.game.dice.count(roll), roll) for roll in range(1, 7)]
        counts.sort(reverse = True)
        # Loop through the game categories.
        possibles = []
        for category_name, score in my_scores.items():
            # Skip used categories.
            if score is not None or category_name == 'Bonus':
                continue
            # Get the category data.
            target_dice, test_values, target_score, category = self.category_data[category_name]
            # Check each category against needed dice and target score.
            # Check ones through sixes.
            if category_name in num_cats:
                roll = num_cats.index(category_name)
                count = self.game.dice.count(roll)
                score_diff = roll * count - target_score
                possibles.append((count - target_dice, [roll] * count, score_diff, 'run'))
            # Check three/four of a kind
            elif 'of a Kind' in category_name or category_name == self.game.five_name:
                count, roll = counts[0]
                score_diff = category.score(self.game.dice, 1) - target_score
                possibles.append((count - target_dice, [roll] * count, score_diff, 'run'))
            # Check chance (so as not to waste it).
            elif 'Chance' in category_name:
                hold = [5] * self.game.dice.count(5) + [6] * self.game.dice.count(6)
                score_diff = category.score(self.game.dice, 1) - target_score
                possibles.append((len(hold) - target_dice, hold, score_diff, 'chance'))
            # Check straights.
            elif 'Straight' in category_name:
                hold = set(self.game.dice.values).intersection(test_values)
                score_diff = category.score(self.game.dice, 1) - target_score
                possibles.append((len(hold) - target_dice, list(hold), score_diff, 'straight'))
            # Check full house.
            elif category_name == 'Full House':
                count_a, roll_a = counts[0]
                count_b, roll_b = counts[1]
                hold = [roll_a] * count_a + [roll_b] * count_b
                score_diff = category.score(self.game.dice, 1) - target_score
                possibles.append((5 - count_a - count_b, hold, score_diff, 'full'))
        # Hold target category you have the best dice and difference with target score for.
        possibles.sort(reverse = True)
        hold = possibles[0][1]
        self.target = possibles[0][-1]
        return hold

    def later_holds(self):
        """Get the holds on the first roll. (list of int)"""
        # Get a local reference to the dice.
        held = self.game.dice.held
        pending = self.game.dice.dice
        # Hold based on target type as set in initial_hold.
        # Hold based on runs.
        if self.target == 'run':
            hold = [held[0]] * pending.count(held[0])
        # Hold for a full house.
        elif self.target == 'full':
            if pending[0].value in held:
                hold = pending[:1]
            else:
                hold = []
        # Hold for a straight.
        elif self.target == 'straight':
            hold = list(set([die for die in pending if die not in held]))
            if 6 in hold and 1 in held:
                hold.remove(6)
            elif 1 in hold and 6 in held:
                hold.remove(1)
        # Hold for chance.
        elif self.target == 'chance':
            hold = list([die.value for die in pending if die.value > 2])
        return hold

    def set_up(self):
        """Set up the bot. (None)"""
        # Intial bot state variables.
        self.next = ''
        self.target = 'run'
        # Basic category data.
        self.category_data = {'Ones': (3, [1, 1, 1, 2, 3]), 'Twos': (3, [2, 2, 2, 3, 4]),
            'Threes': (3, [3, 3, 3, 4, 5]), 'Fours': (3, [4, 4, 4, 5, 6]), 'Fives': (3, [5, 5, 5, 6, 1]),
            'Sixes': (3, [6, 6, 6, 1, 2]), 'Three of a Kind': (3, [4, 4, 4, 3, 5]),
            'Low Chance': (3, [3, 4, 4, 5, 5]), 'Chance': (3, [4, 4, 5, 5, 6]),
            'Little Straight': (5, [1, 2, 3, 4, 5]), 'Big Straight': (5, [2, 3, 4, 5, 6]),
            'Full House': (5, [3, 3, 2, 2, 2]), 'Four of a Kind': (4, [2, 2, 2, 2, 4]),
            self.game.score_cats[-1].name: (5, [4, 4, 4, 4, 4])}
        self.category_data['Straight'] = self.category_data['Big Straight']
        # Calcuate target scores and save actual category objects.
        pool = dice.Pool([6] * 5)
        for category in self.game.score_cats:
            pool.values = self.category_data[category.name][1]
            self.category_data[category.name] += (category.score(pool, 2), category)
        # Remove categories not used in the current variant.
        self.category_data = {name: data for name, data in self.category_data.items() if len(data) == 4}


class ScoreCategory(object):
    """
    A category for a category dice game. (object)

    Attributes:
    bonus: Bonus points added to the sum of the dice. (int)
    check: A function to check validity and get the sub-total. (callable)
    description: A description of the category. (str)
    first: The bonus for getting the roll on the first roll. (int)
    name: The name of the category. (str)
    score_type: How the category is scored. (str)

    Methods:
    copy: Create an independent copy of the category. (ScoreCategory)
    score: Score a roll based on this category. (int)

    Overridden Methods:
    __init__
    """

    def __init__(self, name, description, check, score_type = 'sub-total', first = 0):
        """
        Set up the category. (None)

        Parameters:
        description: A description of the category. (str)
        name: The name of the category. (str)
        check: A function to check validity and get the sub-total. (callable)
        score_type: How the category is scored. (str)
        first: The bonus for getting the roll on the first roll. (int)
        """
        # Set basic attributes.
        self.name = name
        self.description = description
        self.check = check
        self.first = first
        # Parse the score type.
        self.bonus = 0
        self.score_type = score_type.lower()
        # Check for set score.
        if score_type.isdigit():
            self.score_type = int(score_type)
        # Check for a bonus.
        elif self.score_type.startswith('total+'):
            self.bonus = int(score_type.split('+')[1])
            self.score_type = 'total'

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        # Get the score type text.
        type_text = self.score_type.capitalize()
        if isdigit(type_text) and self.first:
            type_text = '{}/{}'.format(type_text, self.first)
        if self.bonus:
            type_text = '{} + {}'.format(type_text, self.bonus)
        return '{}: {} ({})'.format()

    def copy(self):
        """Create an independent copy of the category. (ScoreCategory)"""
        # Create the new category.
        new = ScoreCategory(self.name, self.description, self.check, str(self.score_type), self.first)
        # Set the bonus.
        new.bonus = self.bonus
        return new

    def score(self, dice, roll_count):
        """
        Score a roll based on this category. (int)

        Parameters:
        dice: The roll to score. (dice.Pool)
        roll_count: How many rolls it took to get the roll. (int)
        """
        sub_total = self.check(dice)
        # Score a valid roll
        if sub_total:
            # Score by type of category.
            if isinstance(self.score_type, int):
                score = self.score_type
            elif self.score_type == 'sub-total':
                score = sub_total
            else:
                score = sum(dice.values)
            # Add bonuses.
            if roll_count == 1:
                score += self.first
            score += self.bonus
        else:
            # Invalid rolls score 0.
            score = 0
        return score


class Yacht(game.Game):
    """
    The game of Yacht and it's cousins. (game.Game)

    Class Attributes:
    letters: Letters for easy selection of score categories. (str)
    score_cats: The scoring categories in the game. (dict of str: ScoreCategory)

    Attributes:
    category_scores: The player's scores in each category. (dict of str: dict)
    dice: The pool of dice for the game. (dice.Pool)
    roll_count: The number of rolls taken this turn. (int)
    score_options: The score category option settings for this game. (dict)

    Methods:
    do_hold: Hold back dice for scoring. (bool)
    do_roll: Roll the dice (excluding any held back). (bool)
    do_score: Score the current dice roll. (bool)
    score: Score the current roll in the given category. (int)
    set_wld: Set the win/loss/draw record for the human. (None)

    Overridden Methods:
    __str__
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aliases = {'h': 'hold', 'r': 'roll', 's': 'score'}
    # Interface categories for the game.
    categories = ['Dice Games']
    credits = CREDITS
    letters = '123456ABCDEFGH'
    name = 'Yacht'
    num_options = 16
    rules = RULES
    score_cats = [ScoreCategory('Ones', 'As many ones as possible', score_number(1)),
        ScoreCategory('Twos', 'As many twos as possible', score_number(2)),
        ScoreCategory('Threes', 'As many threes as possible', score_number(3)),
        ScoreCategory('Fours', 'As many fours as possible', score_number(4)),
        ScoreCategory('Fives', 'As many fives as possible', score_number(5)),
        ScoreCategory('Sixes', 'As many sixes as possible', score_number(6)),
        ScoreCategory('Three of a Kind', 'Threed of the same number', three_kind, '0'),
        ScoreCategory('Low Chance', 'Any roll (lower than Chance)', lambda dice: 1, '0'),
        ScoreCategory('Chance', 'Any roll', lambda dice: 1, 'total'),
        ScoreCategory('Little Straight', '1-2-3-4-5', straight_low, '30'),
        ScoreCategory('Big Straight', '2-3-4-5-6', straight_high, '30'),
        ScoreCategory('Full House', 'Three of a kind and a pair', full_house),
        ScoreCategory('Four of a Kind', 'Four of the same number', four_kind),
        ScoreCategory('Yacht', 'Five of the same number', five_kind, '50')]

    def __str__(self):
        """Generate a human readable text representation (str)"""
        # Detrmine the width of the columns.
        cat_names = [category.name for category in self.score_cats]
        max_len = max(len(name) for name in cat_names) + 3
        play_lens = [min(len(player.name), 18) for player in self.players]
        # Set up the line template.
        line_format = ('{{}} {{:<{}}}' + '  {{:>{}}}' * len(self.players)).format(max_len, *play_lens)
        # Start with the titles.
        lines = [line_format.format('  ', 'Categories', *[player.name[:18] for player in self.players])]
        lines.append('-' * len(lines[0]))
        # Add the categories in storage order.
        for char, category in zip(self.letters, self.score_cats):
            # Get the scores (- for unused categories).
            sub_scores = [self.category_scores[player.name][category.name] for player in self.players]
            sub_scores = ['-' if score is None else score for score in sub_scores]
            # Add a line of the scores.
            lines.append(line_format.format(char + ':', category.name, *sub_scores))
            # Add a line for a bonus after the number categories.
            if category.name == 'Sixes' and self.n_bonus[0]:
                sub_scores = [self.category_scores[player.name]['Bonus'] for player in self.players]
                sub_scores = ['-' if score is None else score for score in sub_scores]
                lines.append(line_format.format('-:', 'Bonus', *sub_scores))
        # End with total scores.
        lines.append('-' * len(lines[0]))
        lines.append(line_format.format('  ', 'Total', *[self.scores[plyr.name] for plyr in self.players]))
        # Return as one string.
        return '\n'.join(lines)

    def do_gipf(self, arguments):
        """
        No hablo Ingles.
        """
        # Check the game and play it if valid.
        game, losses = self.gipf_check(arguments, ('rock-paper-scissors',))
        go = True
        # A Rock-Paper-Scissors win lets you turn one die to 3.
        if game == 'rock-paper-scissors':
            if not losses:
                # Remind the human.
                self.human.tell(self)
                self.human.tell('\nThe roll to you is {}.'.format(self.dice))
                self.human.tell('You have {} rerolls left.'.format(self.max_rolls - self.roll_count))
                # Get the value to change.
                query = '\nWhich value would you like to turn into a three? '
                value = self.human.ask_int(query, valid = set(self.dice.values), cmd = False)
                # Change the value and the underlying die.
                die_index = self.dice.values.index(value)
                self.dice.values[die_index] = 3
                # Check if the die is held or waiting to be rolled.
                if die_index >= len(self.dice.held):
                    die_index -= len(self.dice.held)
                    self.dice.dice[die_index].value = 3
                else:
                    self.dice.held[die_index].value = 3
        # Otherwise I'm confused.
        else:
            self.human.tell('No hablo Ingles.')
        return go

    def do_hold(self, arguments):
        """
        Hold back dice for scoring. (h)

        The dice are specified as space separated arguments to the hold command.
        Dice a specified by the value they are showing. Once the dice are held, they
        will be shown with an * after the value in the listing of the current roll.

        Held dice are not rerolled on the next roll. Held dice may not be unheld until
        the next player's turn.
        """
        # Get the current player.
        player = self.players[self.player_index]
        # Get the integer values to hold.
        try:
            holds = [int(word) for word in arguments.split()]
        except ValueError:
            player.error('Invalid argument to hold: {!r}.'.format(arguments))
            return True
        # Hold the dice.
        try:
            self.dice.hold(*holds)
        except ValueError:
            player.error('You do not have all of those dice to hold.')
        return True

    def do_roll(self, arguments):
        """
        Roll the dice (excluding any held back). (r)
        """
        # Get the current player.
        player = self.players[self.player_index]
        # Check the roll count
        if self.roll_count == self.max_rolls:
            player.error('You have already rolled {} times.'.format(self.max_rolls))
        else:
            # Roll the dice and mark the roll.
            self.dice.roll()
            self.roll_count += 1
        return True

    def do_score(self, arguments):
        """
        Score the current dice roll. (s)

        You must specify a score category as an argument. The score category can
        either be specified by name (see below) or by the character preceding the
        name in the score table. That character is 1-6 for the number categories and
        A, B, C, and so on for the other categories.

        The score categories are:
            Yacht: Five of a kind (50)
            Big Straight: 2-3-4-5-6 (30)
            Little Straight: 1-2-3-4-5 (30)
            Four of a Kind: Four of the same number. (Sum of the four of a kind)
            Full House: Two of one number and three of another. (Sum of the dice)
            Chance: Any roll. (Sum of the dice)
            Sixes: As many sixes as possible. (Sum of the sixes)
            Fives: As many fives as possible. (Sum of the fives)
            Fours: As many fours as possible. (Sum of the fours)
            Threes: As many threes as possible. (Sum of the threes)
            Twos: As many twos as possible. (Sum of the twos)
            Ones: As many ones as possible. (Sum of the ones)
        """
        # Get the current player.
        player = self.players[self.player_index]
        # Find the correct category.
        for category in self.score_cats:
            if arguments.lower() == category.name.lower():
                break
        else:
            # Check for single character category reference.
            if arguments.upper() in self.letters:
                category = self.score_cats[self.letters.index(arguments.upper())]
            else:
                # Handle unknown categories.
                player.error('I do not recognize that category.')
                known = [category.name for category in self.score_cats]
                player.error('The categories I know are: {}.'.format(', '.join(known)))
                return True
        # Score the roll in that category.
        score = self.score(category, player)
        # Apply the score to the player.
        if self.category_scores[player.name][category.name] is None:
            self.category_scores[player.name][category.name] = score
            self.scores[player.name] += score
            # Check for a number bonus.
            if self.n_bonus[0] and category.name in ('Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes'):
                try:
                    # Sum the categories.
                    n_sum = 0
                    for category_name in ('Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes'):
                        n_sum += self.category_scores[player.name][category_name]
                    # Check against the required total
                    if n_sum >= self.n_bonus[0]:
                        self.category_scores[player.name]['Bonus'] = self.n_bonus[1]
                        self.scores[player.name] += self.n_bonus[1]
                    else:
                        self.category_scores[player.name]['Bonus'] = 0
                except TypeError:
                    # Any unscored categories will send the code here.
                    pass
            # Reset the dice for the next player.
            self.roll_count = 1
            self.dice.release()
            self.dice.roll()
            # Check for instant win.
            if self.super_five and score and category == self.score_cats[-1] and self.roll_count == 1:
                self.force_end = True
                if player == self.human:
                    self.win_loss_draw[0] = len(self.players) - 1
                else:
                    human_score = self.scores[self.human.name]
                    self.set_wld()
                    if self.scores[player.name] < human_score:
                        self.win_loss_draw[1] += 1
                        self.win_loss_draw[0] -= 1
                    elif self.scores[player.name] == human_score:
                        self.win_loss_draw[1] += 1
                        self.win_loss_draw[2] -= 1
            return False
        # Check for secondary fives of a kind.
        elif self.extra_five and self.score_cats[-1] == category:
            self.scores[player.name] += self.extra_five
            self.category_scores[player.name][self.score_cats[-1].name] += self.extra_five
        else:
            # Handle previously scored categories.
            player.error('You have already scored in that category.')
            return True

    def game_over(self):
        """Check for all categories having been used. (bool)"""
        # Make sure everyone has one turn per score category.
        if self.turns == len(self.score_cats) * len(self.players):
            # Get the human score.
            human_score = self.scores[self.human.name]
            # Get the winners.
            best = max(self.scores.values())
            winners = [name for name, score in self.scores.items() if score == best]
            # Show the final scores.
            self.human.tell(self)
            # Announce the winner(s).
            if len(winners) == 1:
                self.human.tell('\nThe winner is {} with {} points.'.format(winners[0], best))
            else:
                message = '\nThe winners are {} and {}; with {} points.'
                self.human.tell(message.format(', '.join(winners[:-1]), winners[-1], best))
            # Calculate the win/loss/draw (for the human)
            self.set_wld()
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options. (None)"""
        super(Yacht, self).handle_options()
        # Handle the score category options.
        self.score_cats = [category.copy() for category in Yacht.score_cats]
        for category in self.score_cats:
            if category.name in self.score_options:
                score_spec = self.score_options[category.name]
                if isinstance(score_spec, list):
                    # Handle bonus for scoring without rerolling.
                    category.first = int(score_spec[0]) - int(score_spec[1])
                    category.score_type = int(score_spec[1])
                elif score_spec.isdigit():
                    # Handle set scores.
                    category.score_type = int(score_spec)
                elif score_spec.startswith('total'):
                    # Handle total of all dice, inclduing bonuses.
                    category.score_type = 'total'
                    if '+' in score_spec:
                        category.bonus = int(score_spec.split('+')[1])
                elif score_spec == 'sub-total':
                    # Handle total of qualifying dice.
                    category.score_type = 'sub-total'
        # Handle strict categories.
        if self.strict_full:
            self.score_cats[11].check = full_house_strict
        if self.strict_four:
            self.score_cats[12].check = four_kind_strict
        # Remove non-scoring score categories.
        self.score_cats = [category for category in self.score_cats if category.score_type]
        # Set the five of a kind name.
        self.score_cats[-1].name = self.five_name.replace('_', ' ')
        # Catch having only one straight category.
        straight_cats = [category for category in self.score_cats if 'Straight' in category.name]
        if len(straight_cats) == 1:
            straight_cats[0].name = 'Straight'
            straight_cats[0].check = straight
        # Handle wild straights option.
        if self.wild_straight:
            for score_cat in straight_cats:
                score_cat.check = straight_wild
        # Set the players.
        self.players = [self.human]
        taken_names = [self.human.name]
        for bot_index in range(self.easy):
            self.players.append(Bacht(taken_names))
            taken_names.append(self.players[-1].name)
        for bot_index in range(self.medium):
            self.players.append(Bachter(taken_names))
            taken_names.append(self.players[-1].name)
        random.shuffle(self.players)

    def player_action(self, player):
        """
        Handle a player's action during their turn. (bool)

        Parameters:
        player: The player whose turn it is. (player.Player)
        """
        # Show the game status.
        player.tell(self)
        player.tell('\nThe roll to you is {}.'.format(self.dice))
        player.tell('You have {} rerolls left.\n'.format(self.max_rolls - self.roll_count))
        # Get the player's move.
        move = player.ask('What is your move? ')
        return self.handle_cmd(move)

    def score(self, category, player):
        """
        Score the current roll in the given category. (int)

        Parameters:
        category: The category to score the roll in. (ScoreCategory)
        player: The player the roll is being scored for. (player.Player)
        """
        # Get the base score.
        score = category.score(self.dice, self.roll_count)
        # Handle linked chance categories.
        if category.name == 'Low Chance' and 'Chance' in self.category_scores[player.name]:
            chance = self.category_scores[player.name]['Chance']
            if chance is not None and chance <= score:
                score = 0
        elif category.name == 'Chance' and 'Low Chance' in self.category_scores[player.name]:
            low_chance = self.category_scores[player.name]['Low Chance']
            if low_chance is not None and score <= low_chance:
                score = 0
        return score

    def set_options(self):
        """Define the game options. (None)"""
        # Set the variant groups.
        self.option_set.add_group('cheerio',
            'five-name=Cheerio big-straight=25 low-straight=20 four-kind=0 max-rolls=2')
        self.option_set.add_group('general',
            'five-name=Small_General five-kind=60 four-kind=45/40 full-house=35/30 big-straight=25/20 ' +
            'low-straight=0 chance=0 super-five wild-straight')
        self.option_set.add_group('hindenberg',
            'five-name=Hindenberg five-kind=30 big-straight=20 low-straight=15 four-kind=0 chance=0')
        self.option_set.add_group('yahtzee',
            'five-name=Yahtzee big-straight=40 full-house=25 three-kind=total n-bonus=63/35 ' +
            'extra-five=100')
        self.option_set.add_group('yam',
            'five-name=Yam five-kind=total+40 big-straight=total+30 full-house=total+20 ' +
            'low-chance=total low-straight=0 four-kind=0 n-bonus=60/30')
        # Set the score category options.
        self.score_options = {}
        self.option_set.add_option('low-chance', action = 'key=Low Chance', target = self.score_options,
            default = None, check = valid_score_spec, converter = options.lower,
            question = 'What is the score for low chance (return for not used)? ')
        self.option_set.add_option('chance', action = 'key=Chance', target = self.score_options,
            default = None, check = valid_score_spec, converter = options.lower,
            question = 'What is the score for chance (return for total)? ')
        self.option_set.add_option('three-kind', action = 'key=Three of a Kind',
            target = self.score_options, default = None, check = valid_score_spec,
            converter = options.lower,
            question = 'What is the score for three of a kind (return for not used)? ')
        self.option_set.add_option('full-house', action = 'key=Full House', target = self.score_options,
            default = None, check = valid_score_spec, converter = options.lower,
            question = 'What is the score for full house (return for total)? ')
        self.option_set.add_option('four-kind', action = 'key=Four of a Kind', target = self.score_options,
            default = None, check = valid_score_spec, converter = options.lower,
            question = 'What is the score for four of a kind (return for total)? ')
        self.option_set.add_option('low-straight', action = 'key=Little Straight',
            target = self.score_options, default = None, check = valid_score_spec,
            converter = options.lower,
            question = 'What is the score for little straights (return for 30)? ')
        self.option_set.add_option('big-straight', action = 'key=Big Straight',
            target = self.score_options, default = None, check = valid_score_spec,
            converter = options.lower,
            question = 'What is the score for big straights (return for 30)? ')
        self.option_set.add_option('five-kind', action = 'key=Yacht', target = self.score_options,
            default = None, check = valid_score_spec, converter = options.lower,
            question = 'What is the score for five of a kind (return for 50)? ')
        # Set the bot options.
        self.option_set.add_option('easy', default = 1, converter = int,
            question = 'How many easy bots would you like to play against (return for 1)? ')
        self.option_set.add_option('medium', default = 2, converter = int,
            question = 'How many medium bots would you like to play against (return for 2)? ')
        # Set the other options.
        self.option_set.add_option('extra-five', default = 0, converter = int,
            question = 'What should the bonus be for extra five of a kinds (return for none)? ')
        self.option_set.add_option('five-name', default = 'Yacht',
            question = 'What should the name of a five of a kind be (return for Yacht)? ')
        self.option_set.add_option('max-rolls', converter = int, default = 3,
            question = 'How many rolls should you get each turn (return for 3)? ')
        self.option_set.add_option('n-bonus', default = [0, 0], converter = int,
            check = lambda x: len(x) == 2,
            question = 'What should the number bonus be (total needed/bonus points, return for none)? ')
        self.option_set.add_option('strict-four',
            question = 'Should five of a kind be invalid for the four of a kind category? bool')
        self.option_set.add_option('strict-full',
            question = 'Should five of a kind be invalid for the full house category? bool')
        self.option_set.add_option('super-five',
            question = 'Should a five of a kind without rerolling win the game? bool')
        self.option_set.add_option('wild-straight',
            question = 'Should 2s be able to count as 1 or 6 in straights? bool')

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the dice.
        self.dice = dice.Pool([6] * 5)
        self.roll_count = 1
        # Set up the scores.
        score_base = {category.name: None for category in self.score_cats}
        if self.n_bonus[0]:
            score_base['Bonus'] = None
        self.category_scores = {player.name: score_base.copy() for player in self.players}
        self.scores = {player.name: 0 for player in self.players}

    def set_wld(self):
        """Set the win/loss/draw record for the human. (None)"""
        human_score = self.scores[self.human.name]
        self.win_loss_draw[0] = len([x for x in self.scores.values() if x < human_score])
        self.win_loss_draw[1] = len([x for x in self.scores.values() if x > human_score])
        self.win_loss_draw[2] = len([x for x in self.scores.values() if x == human_score])
        self.win_loss_draw[2] -= 1


def valid_score_spec(score_spec):
    """
    Validate a score specification. (bool)

    Parameters:
    score_spec: A user entered score specification. (str)
    """
    valid = False
    if score_spec in ('sub-total', 'total'):
        # Sums of dice.
        valid = True
    elif isinstance(score_spec, list):
        # Bonus for scoring on the first roll.
        if len(score_spec) == 2 and score_spec[0].isdigit() and score_spec[1].isdigit():
            valid = True
    elif score_spec.isdigit():
        # Set scores
        valid = True
    elif score_spec.startswith('total+'):
        # Totals with bonuses
        score_spec = score_spec.split('+')
        if len(score_spec) == 2 and score_spec[1].isdigit():
            valid = True
    return valid


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    yacht = Yacht(player.Humanoid(name), '')
    yacht.play()
