"""
yacht_game.py

Games similar to Yacht.

Classes:
ScoreCategory: A category for a category dice game. (object)
Bacht: A bot to play Yacht. (player.Bot)
Yacht: The game of Yacht and it's cousins. (game.Game)

Functions:
five_kind: Score the yacht category. (int)
four_kind: Score the four of a kind category. (int)
full_house: Score the full house category. (int)
score_n: Creating a scoring function for a number category. (callable)
straight: Score a straight category. (int)
straight_low: Score a low straight category. (int)
straight_high: Score a high straight category. (int)
three_kind: Score the three of a kind category. (int)
"""


import random

import tgames.dice as dice
import tgames.game as game
import tgames.options as options
import tgames.player as player


CREDITS = """
Game Design: Traditional
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
You start by rolling five dice. You may set any number of the dice aside and
reroll the rest. You may set aside a second time and roll a third time. Dice
that are set aside may not be rerolled that turn. Once you get a final roll,
you choose a category to score it in. Each category may be scored only onece.
If you do not meet the criteria for the category, you may still score it, but
it is worth zero points. The game is over when everyone has scored all of the
categories. The categories (and their scores) are:

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
extra-five=: Each player's second and later five of a kinds score bonus points
    equal to this option.
five-name=: Change the name of the five of a kind category. Underscores are
    converted to spaces.
max-rolls: The maximum number of rolls you can make.
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


class ScoreCategory(object):
    """
    A category for a category dice game. (object)

    Attributes:
    description: A description of the category. (str)
    first: The bonus for getting the roll on the first roll. (int)
    name: The name of the category. (str)
    check: A function to check validity and get the sub-total. (callable)
    score_type: How the category is scored. (str)

    Methods:
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

    def copy(self):
        """Create an independent copy of the category. (ScoreCategory)"""
        new = ScoreCategory(self.name, self.description, self.check, str(self.score_type), self.first)
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


def five_kind(dice):
    """
    Score the yacht category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    if values[0] == values[4]:
        return 5 * values[0]

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
    if values[0] == values[1] and values[2] == values[4]:
        return sum(values)
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
    if values[0] == values[1] and values[2] == values[4] and values[0] != values[4]:
        return sum(values)
    if values[0] == values[2] and values[3] == values[4] and values[0] != values[4]:
        return sum(values)
    else:
        return 0

def score_n(number):
    """
    Creating a scoring function for a number category. (callable)

    Parameters:
    number: The number of the category. (int)
    """
    def score_num(dice):
        return number * dice.values.count(number)
    return score_num

def straight(dice):
    """
    Score a straight category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    for value_index, value in enumerate(values[1:]):
        if value - values[value_index] != 1: # indexes are correctly off due to skipping values[0]
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

    This is just a dummy bot to test the game functionality.

    Attributes:
    next: The bacht's next move, if known. (str)

    Methods:
    get_category: Get the category to score a roll in. (str)
    get_holds: Get the dice to hold for the next roll. (list of int)

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
            if self.next == 'roll':
                self.next = ''
                return 'roll'
            elif (self.game.roll_count == self.game.max_rolls or self.next == 'score' 
                or not self.game.dice.dice):
                move = 'score ' + self.get_category()
            else:
                move = 'hold ' + ' '.join([str(x) for x in self.get_holds()])
                if move == 'hold ':
                    move = 'roll'
                elif self.game.dice.dice: # !! does not work, since hald hasn't happened yet.
                    self.next = 'roll'
                else:
                    self.next = 'score'
        else:
            raise player.BotError('Unexpected query to Bacht: {!r}'.format(query))
        return move

    def get_category(self):
        """Get the category to score the current roll in. (str)"""
        ranking = []
        my_scores = self.game.category_scores[self.name]
        for category in self.game.score_cats:
            if my_scores[category.name] is None:
                score = category.score(self.game.dice, self.game.roll_count)
                # !! repeated code, needs refactoring. Score method of Yacht?
                if category.name == 'low Chance' and 'Chance' in my_scores:
                    chance = my_scores['Chance']
                    if chance is not None and chance <= score:
                        score = 0
                elif category.name == 'Chance' and 'Low Chance' in my_scores:
                    low_chance = my_scores['Low Chance']
                    if low_chance is not None and score <= low_chance:
                        score = 0
                ranking.append((score, category.name))
        ranking.sort()
        return ranking[-1][1]

    def get_holds(self):
        """
        Get the dice to hold for the next roll. (list of int)

        If the roll is ready to score, this method holds all of the dice.
        """
        held = self.game.dice.held
        pending = self.game.dice.dice
        my_scores = self.game.category_scores[self.name]
        if not held:
            counts = [pending.count(value) for value in range(7)]
            ordered = sorted(counts[:], reverse = True)
            if ordered[1] > 1:
                hold = [counts.index(ordered[0])] * ordered[0]
                if ordered[0] == ordered[1]:
                    hold = [counts.index(ordered[0], counts.index(ordered[0]) + 1)] * ordered[0]
                else:
                    hold += [counts.index(ordered[1])] * ordered[1]
            elif ordered[0] > 2:
                hold = [counts.index(ordered[0])] * ordered[0]
            elif my_scores.get('Little Straight', 0) is None and len(set([die for die in pending if die < 6])) > 2:
                hold = set([die for die in pending if die < 6])
            elif my_scores.get('Big Straight', 0) is None and len(set([die for die in pending if die > 1])) > 2:
                hold = set([die for die in pending if die > 1])
            elif my_scores.get('Straight', 0) is None and len(set([die for die in pending if die > 1])) > 2:
                hold = set([die for die in pending if die > 1])
            elif ordered[0] > 1:
                hold = [counts.index(ordered[0])] * ordered[0]
            else:
                hold = [max(pending)]
        else:
            unique_held = len(set(held))
            if unique_held == 1:
                hold = [held[0]] * pending.count(held[0])
            elif unique_held == 2:
                if pending[0] in held:
                    hold = pending[:1]
                else:
                    hold = []
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
    A Bachter Bacht.

    Attributes:
    category_data: Target number of dice and score for each category. (dict)

    Overridden Methods:
    set_up
    """

    def get_category(self):
        """Get the category to score the current roll in. (str)"""
        ranking = []
        my_scores = self.game.category_scores[self.name]
        for category in self.game.score_cats:
            if my_scores[category.name] is None:
                score = category.score(self.game.dice, self.game.roll_count)
                score -= self.category_data[category.name][2]
                # !! repeated code, needs refactoring. Score method of Yacht?
                if category.name == 'low Chance' and 'Chance' in my_scores:
                    chance = my_scores['Chance']
                    if chance is not None and chance <= score:
                        score = 0
                elif category.name == 'Chance' and 'Low Chance' in my_scores:
                    low_chance = my_scores['Low Chance']
                    if low_chance is not None and score <= low_chance:
                        score = 0
                ranking.append((score, category.name))
        ranking.sort()
        return ranking[-1][1]

    def get_holds(self):
        """Get dice to hold. (list of int)"""
        held = self.game.dice.held
        pending = self.game.dice.dice
        my_scores = self.game.category_scores[self.name]
        num_cats = ['Zeros', 'Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes']
        if not held:
            possibles = []
            counts = [(self.game.dice.count(roll), roll) for roll in range(1, 7)]
            counts.sort(reverse = True)
            for category_name, score in my_scores.items():
                if score is not None:
                    continue
                target_dice, test_values, target_score, category = self.category_data[category_name]
                if category_name in num_cats:
                    roll = num_cats.index(category_name)
                    count = self.game.dice.count(roll)
                    score_diff = roll * count - target_score
                    possibles.append((count - target_dice, [roll] * count, score_diff, 'run'))
                elif 'of a Kind' in category_name or category_name == self.game.five_name:
                    count, roll = counts[0]
                    score_diff = category.score(self.game.dice, 1) - target_score
                    possibles.append((count - target_dice, [roll] * count, score_diff, 'run'))
                elif 'Chance' in category_name:
                    hold = [5] * self.game.dice.count(5) + [6] * self.game.dice.count(6)
                    score_diff = category.score(self.game.dice, 1) - target_score
                    possibles.append((len(hold) - target_dice, hold, score_diff, 'chance'))
                elif 'Straight' in category_name: # !! not working. bot got straight on first roll, held 1 six.
                    # ?? possibles[x][0] wrong?!!
                    hold = set(self.game.dice.values).intersection(test_values)
                    score_diff = category.score(self.game.dice, 1) - target_score
                    possibles.append((len(hold) - target_dice, hold, score_diff, 'straight'))
                elif category_name == 'Full House':
                    count_a, roll_a = counts[0]
                    count_b, roll_b = counts[1]
                    hold = [roll_a] * count_a + [roll_b] * count_b
                    score_diff = category.score(self.game.dice, 1) - target_score
                    possibles.append((5 - count_a - count_b, hold, score_diff, 'full'))
            possibles.sort(reverse = True)
            hold = possibles[0][1]
            self.target = possibles[0][-1]
        else:
            unique_held = len(set(held))
            if self.target == 'run':
                hold = [held[0]] * pending.count(held[0])
            elif self.target == 'full':
                if pending[0].value in held:
                    hold = pending[:1]
                else:
                    hold = []
            elif self.target == 'straight':
                hold = list(set([die for die in pending if die not in held]))
                if 6 in hold and 1 in held:
                    hold.remove(6)
                elif 1 in hold and 6 in held:
                    hold.remove(1)
            elif self.target == 'chance':
                hold = list([die.value for die in pending if die.value > 2])
        return hold

    def set_up(self):
        """Set up the bot. (None)"""
        self.next = ''
        self.target = 'run'
        self.category_data = {'Ones': (3, [1, 1, 1, 2, 3]), 'Twos': (3, [2, 2, 2, 3, 4]), 
            'Threes': (3, [3, 3, 3, 4, 5]), 'Fours': (3, [4, 4, 4, 5, 6]), 'Fives': (3, [5, 5, 5, 6, 1]), 
            'Sixes': (3, [6, 6, 6, 1, 2]), 'Three of a Kind': (3, [4, 4, 4, 3, 5]), 
            'Low Chance': (3, [3, 4, 4, 5, 5]), 'Chance': (3, [4, 4, 5, 5, 6]), 
            'Little Straight': (5, [1, 2, 3, 4, 5]), 'Big Straight': (5, [2, 3, 4, 5, 6]),
            'Full House': (5, [3, 3, 2, 2, 2]), 'Four of a Kind': (4, [2, 2, 2, 2, 4]),
            self.game.score_cats[-1].name: (5, [4, 4, 4, 4, 4])}
        self.category_data['Straight'] = self.category_data['Big Straight']
        self.dice = dice.Pool([6] * 5)
        # !! not working correctly
        for category in self.game.score_cats:
            self.dice.values = self.category_data[category.name][1]
            self.category_data[category.name] += (category.score(self.dice, 2), category)
        self.category_data = {name: data for name, data in self.category_data.items() if len(data) == 4}


class Yacht(game.Game):
    """
    The game of Yacht and it's cousins. (game.Game)

    Class Attributes:
    score_cats: The scoring categories in the game. (dict of str: ScoreCategory)

    Attributes:
    category_scores: The player's scores in each category. (dict of str: dict)
    dice: The pool of dice for the game. (dice.Pool)

    Methods:
    do_hold: Hold back dice for scoring. (bool)
    do_roll: Roll the dice (excluding any held back). (bool)
    do_score: Score the current dice roll. (bool)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_up
    """

    aliases = {'h': 'hold', 'r': 'roll', 's': 'score'}
    categories = ['Dice Games', 'Category Games']
    credits = CREDITS
    letters = '123456ABCDEFGH'
    name = 'Yacht'
    num_options = 16
    rules = RULES
    score_cats = [ScoreCategory('Ones', 'As many ones as possible', score_n(1)),
        ScoreCategory('Twos', 'As many twos as possible', score_n(2)),
        ScoreCategory('Threes', 'As many threes as possible', score_n(3)),
        ScoreCategory('Fours', 'As many fours as possible', score_n(4)),
        ScoreCategory('Fives', 'As many fives as possible', score_n(5)),
        ScoreCategory('Sixes', 'As many sixes as possible', score_n(6)),
        ScoreCategory('Three of a Kind', 'Threed of the same number', three_kind, '0'),
        ScoreCategory('Low Chance', 'Any roll (lower than Chance)', lambda dice: 1, '0'),
        ScoreCategory('Chance', 'Any roll', lambda dice: 1, 'total'),
        ScoreCategory('Little Straight', '1-2-3-4-5', straight_low, '30'),
        ScoreCategory('Big Straight', '2-3-4-5-6', straight_high, '30'),
        ScoreCategory('Full House', 'Three of a kind and a pair', full_house),
        ScoreCategory('Four of a Kind', 'Four of the same number', four_kind),
        ScoreCategory('Yacht', 'Five of the same number', five_kind, '50')]

    def __str__(self):
        """Human readable text representation (str)"""
        cat_names = [category.name for category in self.score_cats]
        max_len = max(len(name) for name in cat_names) + 3
        play_lens = [min(len(player.name), 18) for player in self.players]
        line_format = ('{{}} {{:<{}}}' + '  {{:>{}}}' * len(self.players)).format(max_len, *play_lens)
        lines = [line_format.format('  ', 'Categories', *[player.name[:18] for player in self.players])]
        lines.append('-' * len(lines[0]))
        for char, category in zip(self.letters, self.score_cats):
            sub_scores = [self.category_scores[player.name][category.name] for  player in self.players]
            sub_scores = ['-' if score is None else score for score in sub_scores]
            lines.append(line_format.format(char + ':', category.name, *sub_scores))
            if category.name == 'Sixes' and self.n_bonus[0]:
                sub_scores = [self.category_scores[player.name]['Bonus'] for player in self.players]
                sub_scores = ['-' if score is None else score for score in sub_scores]
                lines.append(line_format.format('-:', 'Bonus', *sub_scores))
        lines.append('-' * len(lines[0]))
        lines.append(line_format.format('  ', 'Total', *[self.scores[plyr.name] for plyr in self.players]))
        return '\n'.join(lines)

    def do_hold(self, arguments):
        """
        Hold back dice for scoring. (bool)

        Parameters:
        arguments: The dice (values) to hold. (str)
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
        Roll the dice (excluding any held back). (bool)

        Parameters:
        arguments: The dice (values) to hold. (str)
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
        Score the current dice roll. (bool)

        Parameters:
        arguments: The category to score the roll in. (str)
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
        score = category.score(self.dice, self.roll_count)
        if category.name == 'Low Chance' and 'Chance' in self.category_scores[player.name]:
            chance = self.category_scores[player.name]['Chance']
            if chance is not None and chance <= score:
                score = 0
        elif category.name == 'Chance' and 'Low Chance' in self.category_scores[player.name]:
            low_chance = self.category_scores[player.name]['Low Chance']
            if low_chance is not None and score <= low_chance:
                score = 0
        # Apply the score to the player.
        if self.category_scores[player.name][category.name] is None:
            self.category_scores[player.name][category.name] = score
            self.scores[player.name] += score
            # Check for a number bonus.
            if self.n_bonus[0] and category.name in ('Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes'):
                try:
                    n_sum = 0
                    for category_name in ('Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes'):
                        n_sum += self.category_scores[player.name][category_name]
                    if n_sum >= self.n_bonus[0]:
                        self.category_scores[player.name]['Bonus'] = self.n_bonus[1]
                        self.scores[player.name] += self.n_bonus[1]
                    else:
                        self.category_scores[player.name]['Bonus'] = 0
                except TypeError:
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
                    # !! duplicate code.
                    self.win_loss_draw[0] = len([x for x in self.scores.values() if x < human_score])
                    self.win_loss_draw[1] = len([x for x in self.scores.values() if x > human_score])
                    self.win_loss_draw[2] = len([x for x in self.scores.values() if x == human_score])
                    self.win_loss_draw[2] -= 1
                    if self.scores[player.name] < human_score:
                        self.win_loss_draw[1] += 1
                        self.win_loss_draw[0] -= 1
                    elif self.scores[player.name] == human_score:
                        self.win_loss_draw[1] += 1
                        self.win_loss_draw[2] -= 1
            return False
        elif self.extra_five and self.score_cats[-1] == category:
            self.scores[player.name] += self.extra_five
            self.category_scores[player.name][self.score_cats[-1].name] += self.extra_five
        else:
            # Handle previously scored categories.
            player.error('You have already scored in that category.')
            return True

    def game_over(self):
        """Check for all categories having been used. (bool)"""
        if self.turns == len(self.score_cats) * len(self.players):
            human_score = self.scores[self.human.name]
            best = max(self.scores.values())
            winners = [name for name, score in self.scores.items() if score == best]
            self.human.tell(self)
            if len(winners) == 1:
                self.human.tell('\nThe winner is {} with {} points.\n'.format(winners[0], best))
            else:
                message = '\nThe winners are {} and {}; with {} points.\n'
                self.human.tell(message.format(', '.join(winners[:-1]), winners[-1], best))
            self.win_loss_draw[0] = len([score for score in self.scores.values() if score < human_score])
            self.win_loss_draw[1] = len([score for score in self.scores.values() if score > human_score])
            self.win_loss_draw[2] = len([score for score in self.scores.values() if score == human_score])
            self.win_loss_draw[2] -= 1
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options."""
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
        self.dice = dice.Pool([6] * 5)
        self.roll_count = 1
        score_base = {category.name: None for category in self.score_cats}
        if self.n_bonus[0]:
            score_base['Bonus'] = None
        self.category_scores = {player.name: score_base.copy() for player in self.players}
        self.scores = {player.name: 0 for player in self.players}


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