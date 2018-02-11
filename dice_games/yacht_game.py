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
        if score_type.isdigit():
            self.score_type = int(score_type)
        else:
            self.score_type = score_type.lower()
        # Check for a bonus.
        if self.score_type.startswith('total+'):
            self.bonus = int(score_type.split('+')[1])
            self.score_type = 'total'
        else:
            self.bonus = 0

    def copy(self):
        """Create an independent copy of the category. (ScoreCategory)"""
        clone = ScoreCategory(self.name, self.description, self.validator, self.score_type, self.first)
        clone.bonus = self.bonus
        return clone

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
                score = sum(dice)
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
    if values[0] == values[3] or values[2] == values[4]:
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

def straight(dice):
    """
    Score a straight category. (int)

    Parameters:
    dice: The dice roll to score. (int)
    """
    values = sorted(dice.values)
    for value_index, value in enumerate(values):
        if value - values[value_index - 1] != 1:
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
            elif game.roll_count == 3 or self.next == 'score':
                move = 'score ' + self.get_category()
            else:
                move = 'hold ' + ' '.join([str(x) for x in self.get_holds()])
                if self.game.dice:
                    self.next = 'roll'
                else:
                    self.next = 'score'
        else:
            raise player.BotError('Unexpected query to Bacht: {!r}'.format(query))

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
            if len([count for count in counts if count > 1]) > 1:
                # save those
            elif max(counts) > 2:
                # save that
            elif my_scores['Little Straight'] is None and len(set([die for die in pending if die < 6])) > 3:
                # save those
            elif my_scores['Big Straight'] is None and len(set([die for die in pending if die > 1])) > 3:
                # save those
            else:
                # save the max

    def set_up(self):
        """Set up the bot. (None)"""
        self.next = ''


class Yacht(game.Game):
    """
    The game of Yacht and it's cousins. (game.Game)

    Class Attributes:
    categories: The scoring functions for each category. (dict of str: callable)

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

    categories = ['ones': ScoreCategory('Ones', 'As many ones as possible', score_n(1)),
        'twos': ScoreCategory('Twos', 'As many twos as possible', score_n(2)),
        'threes': ScoreCategory('Threes', 'As many threes as possible', score_n(3)),
        'fours': ScoreCategory('Fours', 'As many fours as possible', score_n(4)),
        'fives': ScoreCategory('Fives', 'As many fives as possible', score_n(5)),
        'sixes': ScoreCategory('Sixes', 'As many sixes as possible', score_n(6)),
        'full-house': ScoreCategory('Full House', 'Three of a kind and a pair', full_house),
        'four-kind': ScoreCategory('Four of a Kind', 'Four of the same number', four_kind),
        'litte-straight': ScoreCategory('Little Straight', '1-2-3-4-5', straight, '30'),
        'big-straight': ScoreCategory('Big Straight', '2-3-4-5-6', straight, '30'),
        'choice': SubCategory('Choice', 'Any roll', lambda dice: 1, 'total'),
        'yacht': SubCategory('Yacht', 'Five of the same number', five_kind, '50')]

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
        # Hold the dice.
        try:
            self.dice.hold(holds)
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
        for category in self.categories:
            if arguments.lower() == category.name.lower():
                break
        else:
            # Handle unknown categories.
            player.error('I do not recognize that category.')
            known = [category.name for category in self.categories]
            player.error('The categories I know are: {}.'.format(', '.join(known)))
            return False
        # Score the roll in that category.
        score = category.score(self.dice, self.roll_count)
        if self.category_scores[player.name][category.name] is None:
            self.category_scores[player.name][category.name] = score
            self.scores[player.name] += score
            # Reset the dice for the next player.
            self.roll_count = 1
            self.dice.release()
            self.dice.roll()
            return True
        else:
            # Handle previously scored categories.
            player.error('You have already scored in that category.')
            return False

    def game_over(self):
        """Check for all categories having been used. (bool)"""
        count = sum([list(player.score.values()).count(None) for player in self.players])
        if not count:
            self.category_scores = self.scores
            for player_name in self.category_scores:
                self.scores[player_name] = sum(self.category_scores[player_name].values())
        return count == 0

    def handle_options(self):
        """Handle the game options."""
        super(Yacht, self).handle_options()
        self.categories = [category.copy() for category in Yacht.categories]

    def player_action(self, player):
        """
        Handle a player's action during their turn. (bool)

        Parameters:
        player: The player whose turn it is. (player.Player)
        """
        # Show the game status.
        player.tell('\nThe roll to you is {}.'.format(self.dice))
        player.tell('You have {} rerolls left.\n'.format(3 - self.roll_count))
        # Get the player's move.
        move = player.ask('What is your move? ')
        return self.handle_cmd(move)

    def set_up(self):
        """Set up the game. (None)"""
        self.dice = dice.Pool([6] * 5)
        score_base = {category.name: None for category in self.categories}
        self.category_scores = {player.name: score_base.copy() for player in self.players}
        self.scores = {player.name: 0 for player in self.players}