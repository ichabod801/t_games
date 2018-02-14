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
"""


import random

import tgames.dice as dice
import tgames.game as game
import tgames.player as player


class ScoreCategory(object):
    """
    A category for a category dice game. (object)

    !! I will want to move this to dice.py.

    Attributes:
    description: A description of the category. (str)
    first: The bonus for getting the roll on the first roll. (int)
    name: The name of the category. (str)
    validator: A function to check validity and get the sub-total. (callable)
    score_type: How the category is scored. (str)

    Methods:
    score: Score a roll based on this category. (int)

    Overridden Methods:
    __init__
    """

    def __init__(self, name, description, validator, score_type = 'sub-total', first = 0):
        """
        Set up the category. (None)

        Parameters:
        description: A description of the category. (str)
        name: The name of the category. (str)
        validator: A function to check validity and get the sub-total. (callable)
        score_type: How the category is scored. (str)
        first: The bonus for getting the roll on the first roll. (int)
        """
        # Set basic attributes.
        self.name = name
        self.description = description
        self.validator = validator
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
        new = ScoreCategory(self.name, self.description, self.validator, str(self.score_type), self.first)
        new.bonus = self.bonus
        return new

    def score(self, dice, roll_count):
        """
        Score a roll based on this category. (int)

        Parameters:
        dice: The roll to score. (dice.Pool)
        roll_count: How many rolls it took to get the roll. (int)
        """
        sub_total = self.validator(dice)
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
            score += self.bonus
            if roll_count == 1:
                score += self.first
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
    # !! I should take the sorting out of the functions for efficiency.
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

def full_house(dice):
    """
    Score the full house category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    if values[0] == values[1] and values[2] == values[4] and values[1] != values[2]:
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
        return number * dice.count(number)
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
        return 30
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
            elif self.game.roll_count == 3 or self.next == 'score' or not self.game.dice.dice:
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
        for category in self.game.score_cats:
            if self.game.category_scores[self.name][category.name] is None:
                ranking.append((category.score(self.game.dice, self.game.roll_count), category.name))
        ranking.reverse() # reverse is done so ties go to category with lowest potential.
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
            elif my_scores['Little Straight'] is None and len(set([die for die in pending if die < 6])) > 2:
                hold = set([die for die in pending if die < 6])
            elif my_scores['Big Straight'] is None and len(set([die for die in pending if die > 1])) > 2:
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
    name = 'Yacht'
    score_cats = [ScoreCategory('Ones', 'As many ones as possible', score_n(1)),
        ScoreCategory('Twos', 'As many twos as possible', score_n(2)),
        ScoreCategory('Threes', 'As many threes as possible', score_n(3)),
        ScoreCategory('Fours', 'As many fours as possible', score_n(4)),
        ScoreCategory('Fives', 'As many fives as possible', score_n(5)),
        ScoreCategory('Sixes', 'As many sixes as possible', score_n(6)),
        ScoreCategory('Full House', 'Three of a kind and a pair', full_house),
        ScoreCategory('Four of a Kind', 'Four of the same number', four_kind),
        ScoreCategory('Little Straight', '1-2-3-4-5', straight, '30'),
        ScoreCategory('Big Straight', '2-3-4-5-6', straight, '30'),
        ScoreCategory('Choice', 'Any roll', lambda dice: 1, 'total'),
        ScoreCategory('Yacht', 'Five of the same number', five_kind, '50')]

    def __str__(self):
        """Human readable text representation (str)"""
        cat_names = [category.name for category in self.score_cats]
        max_len = max(len(name) for name in cat_names)
        play_lens = [min(len(player.name), 18) for player in self.players]
        line_format = ('{{:<{}}}' + '  {{:>{}}}' * len(self.players)).format(max_len, *play_lens)
        lines = [line_format.format('Categories', *[player.name[:18] for player in self.players])]
        lines.append('-' * len(lines[0]))
        for category in self.score_cats:
            sub_scores = [self.category_scores[player.name][category.name] for  player in self.players]
            sub_scores = ['-' if score is None else score for score in sub_scores]
            lines.append(line_format.format(category.name, *sub_scores))
        lines.append('-' * len(lines[0]))
        lines.append(line_format.format('Total', *[self.scores[player.name] for player in self.players]))
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
            return False
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
        if self.roll_count == 3:
            player.error('You have already rolled three times.')
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
        # !! It would be good to provide some flexibility in identifying categories.
        for category in self.score_cats:
            if arguments.lower() == category.name.lower():
                break
        else:
            # Handle unknown categories.
            player.error('I do not recognize that category.')
            known = [category.name for category in self.score_cats]
            player.error('The categories I know are: {}.'.format(', '.join(known)))
            return True
        # Score the roll in that category.
        score = category.score(self.dice, self.roll_count)
        if self.category_scores[player.name][category.name] is None:
            self.category_scores[player.name][category.name] = score
            self.scores[player.name] += score
            # Reset the dice for the next player.
            self.roll_count = 1
            self.dice.release()
            self.dice.roll()
            return False
        else:
            # Handle previously scored categories.
            player.error('You have already scored in that category.')
            return True

    def game_over(self):
        """Check for all categories having been used. (bool)"""
        count = sum([list(self.category_scores[plyr.name].values()).count(None) for plyr in self.players])
        if count:
            return False
        else:
            human_score = self.scores[self.human.name]
            best = max(self.scores.values())
            winners = [name for name, score in self.scores.items() if score == best]
            self.human.tell(self)
            if len(winners) == 1:
                self.human.tell('\nThe winner is {} with {} points.'.format(winners[0], best))
            else:
                message = 'The winners are {} and {}; with {} points.'
                self.human.tell(message.format(', '.join(winners[:-1]), winners[-1], best))
            self.win_loss_draw[0] = len([score for score in self.scores.values() if score < human_score])
            self.win_loss_draw[1] = len([score for score in self.scores.values() if score > human_score])
            self.win_loss_draw[2] = len([score for score in self.scores.values() if score == human_score])
            self.win_loss_draw[2] -= 1
            return True

    def handle_options(self):
        """Handle the game options."""
        super(Yacht, self).handle_options()
        self.score_cats = [category.copy() for category in Yacht.score_cats]
        self.players = [self.human, Bacht()]
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
        player.tell('You have {} rerolls left.\n'.format(3 - self.roll_count))
        # Get the player's move.
        move = player.ask('What is your move? ')
        return self.handle_cmd(move)

    def set_up(self):
        """Set up the game. (None)"""
        self.dice = dice.Pool([6] * 5)
        self.roll_count = 1
        score_base = {category.name: None for category in self.score_cats}
        self.category_scores = {player.name: score_base.copy() for player in self.players}
        self.scores = {player.name: 0 for player in self.players}