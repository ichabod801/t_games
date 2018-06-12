"""
liars_dice_game.py

A game of Liar's Dice.

Classes:
LiarsDice: A game of Liar's Dice. (game.Game)
"""


import t_games.dice as dice
import t_games.game as game
from t_games.utility import number_word


class LiarsDice(game.Game):
    """
    A game of Liar's Dice. (game.Game)

    Class Attributes:
    hand_names: The name templates for the poker hand versions of the dice. (str)

    Attributes:
    claim: The claim made by the last player. (list of int)
    dice: The dice used in the game. (dice.Pool)
    phase: The current action the player needs to take. (str)

    Methods:
    poker_score: Generate a poker hand score for a set of values. (list of int)
    poker_text: Convert a poker score into text. (str)
    validate_claim: Validate that a claim is higher than the previosu one. (bool)

    Overridden Methods:
    player_action
    set_up
    """

    # Other names for the game.
    aka = ['Doubting Dice', 'Schummeln']
    # The menu categories for the game.
    categories = ['Dice Games']
    # The name templates for the poker hand versions of the dice.
    hand_names ['five {}s', 'four {}s and a {}', 'full house {}s over {}s', 'a {}-high straight', 
        'three {}s with {} and {}', 'two pair {}s over {}s with a {}', 'a pair of {}s with {}',
        'six high missing {}.']
    # The name of the game.
    name = "Liar's Dice"

    def player_action(self, player):
        """
        Get a game action from the player. (None)

        Parameter:
        player: The current player. (player.Player)
        """
        # Display the game state.
        if self.phase == 'start':
            self.dice.roll()
            player.tell('\nThe new roll to you is {}.'.format(self.dice))
            self.phase = 'claim'
        elif self.phase == 'reroll':
            player.tell('\nThe roll passed to you is {}.'.format(self.dice))
        elif self.phase == 'claim':
            player.tell('\nYour roll is {}.'.format(self.dice))
        # Get the player action
        if self.phase == 'claim':
            # Get the claimed value.
            query = 'Enter five numbers for your claim, or return to be honest: '
            claim = player.ask_int_list(query, low = 1, high = 6, valid_lens = [6], 
                default = self.dice.values)
            # Handle other commands.
            if isintance(claim, str):
                return self.handle_cmd(claim)
            # Validate the claim and check for a challenge.
            elif self.validate_claim(claim, player):
                self.challenge()
                return False
        elif self.phase == 'reroll':
            # Get the dice to reroll.
            query = 'Enter the numbers you would like to reroll: '
            rerolls = player.ask_int_list(query, valid = self.dice.values, valid_len = range(6), 
                default = [])
            # Handle other commands.
            if isinstance(rerolls, str):
                return self.handle_cmd(rerolls)
            # Reroll the specified dice and move to making a claim.
            else:
                for die_index, value in enumerate(self.dice.values):
                    if value in rerolls:
                        self.dice.reroll(die_index)
                        rerolls.remove(value)
                self.phase = 'claim'
        return True

    def poker_score(self, values):
        """
        Generate a poker hand score for a set of values. (list of int)

        The score is a list of integers. The first number is the type of hand, from 7
        for five of a kind to 0 for high card. The rest of the numbers are the dice
        values in comparison order for that type of hand. Therefore you can naively
        compare the two integer lists to find out which is the higher hand.

        Parmeters:
        values: The claimed or rolled dice values. (lsit of int)
        """
        # Summarize the values.
        by_count = collections.defaultdict(list)
        for value in set(values):
            by_count[values.count(value)].append(value)
        max_count = max(by_count)
        # Score by value.
        # Score five of a kind.
        if max_count == 5:
            score = [7] + by_count[5] * 5
        # Score four of a kind.
        elif max_count == 4:
            score = [6] + by_count[4] * 4 + by_count[1]
        # Score full house.
        elif max_count == 3 and 2 in by_count:
            score = [5] + by_count[3] * 3 + by_count[2] * 2
        # Score straight.
        elif max_count == 1 and (max(values) == 5 or min(values) == 2):
            score = [4] + sorted(values, reverse = True)
        # Score three of a kind.
        elif max_count == 3:
            score = [3] + by_count[3] * 3 + sorted(by_count[1], reverse = True)
        # Score high card (scored out of order to ensure 2 in by_count)
        elif max_count == 1:
            score = [0] + sorted(values, reverse = True)
        # Score two pair.
        elif len(by_count[2]) == 2:
            pairs = sorted(by_count[2], reverse = True)
            score = [2] + pairs[:1] * 2 + pairs[1:] * 2 + by_count[1]
        # Score a pair.
        else:
            score = [1] + by_count[2] * 2 + sorted(by_count[1], reverse = True)
        return score

    def poker_text(self, score):
        """
        Convert a poker score into text. (str)

        Parameters:
        score: A score returned by poker_score. (list of int)
        """
        # Get the hand name template.
        hand_name = self.hand_names[score[0]]
        # Fill in the template with the word versions of the numbers.
        # Five of a kind and straights need one word.
        if score[0] in (4, 7):
            hand_name = hand_name.format(number_word(score[1]))
        # Four of a kind and full house need the first and the last word.
        elif score[0] in (5, 6):
            hand_name = hand_name.format(number_word(score[1]), number_word(score[5]))
        # Three of a kind needs the first word and two trailing words.
        elif score[0] == 3:
            trailers = ', '.join([number_word(value) for value in score[-2:]])
            hand_name = hand_name.format(number_word(score[1]), trailers)
        # Two pair needs the odd numbered words.
        elif score[0] == 2:
            words = number_word(score[1]), number_word(score[3]), number_word(score[5])
            hand_name = hand_name.format(*words)
        # One pair needs the first word and three trailing words.
        elif score[0] == 1:
            trailers = ', '.join([number_word(value) for value in score[-3:]])
            hand_name = hand_name.format(number_word(score[1]), trailers)
        # High card needs the missing word.
        elif score[0] == 0:
            missing = [value for value in range(7) if value not in score][0]
            hand_name = hand_name.format(number_word(missing))
        # Return the hand name after fixing and six plural.
        return hand_name.replace('sixs', 'sixes')

    def set_up(self):
        """Set up the game. (None)"""
        self.scores = {player.name: 3 for player in self.players}
        self.dice = dice.Pool([6] * 5)
        self.claim = [1, 2, 3, 4, 6]
        self.phase = 'start'

    def validate_claim(self, claim, player):
        """
        Validate that a player's claim is higher than the previosu one. (bool)

        Parameters:
        claim: The current player's claimed roll. (list of int)
        player: The current player. (player.Player)
        """
        new_score = self.poker_score(claim)
        old_score = self.poker_score(self.claim)
        if new_score > old_score:
            self.claim = claim
            return True
        else:
            new_text = self.poker_text(new_score)
            old_score = self.poker_text(old_score)
            message = 'Your claim of {} is not better than the previous claim of {}.'
            self.player.error(message.format(new_text, old_text))
            return False

