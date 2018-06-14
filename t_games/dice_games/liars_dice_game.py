"""
liars_dice_game.py

A game of Liar's Dice.

Classes:
LiarsDice: A game of Liar's Dice. (game.Game)
ABBot: An honest Liar's Dice bot. (player.Bot)
"""


from __future__ import division

import collections
import random

import t_games.dice as dice
import t_games.game as game
import t_games.player as player
from t_games.utility import number_word, YES


class LiarsDice(game.Game):
    """
    A game of Liar's Dice. (game.Game)

    Class Attributes:
    hand_names: The name templates for the poker hand versions of the dice. (str)

    Attributes:
    betting: A flag for passing chips instead of losing them. (bool)
    chips: The number of tokens each player starts with. (int)
    claim: The claim made by the last player. (list of int)
    dice: The dice used in the game. (dice.Pool)
    one_six: A flag for ones counting as sixes. (bool)
    one_wild: A flag for ones being wild. (bool)
    phase: The current action the player needs to take. (str)
    two_rerolls: A flag for getting a second reroll. (bool)

    Methods:
    challenge: Handle someone making a claim. (None)
    one_six_adjust: Adjust value counts for the one-six option. (dict)
    one_wild_adjust: Adjust value counts for the one-six option. (tuple)
    poker_score: Generate a poker hand score for a set of values. (list of int)
    poker_text: Convert a poker score into text. (str)
    reset: Reset the tracking variables. (None)
    resolve_challenge: Handle the result of a challenge. (None)
    validate_claim: Validate that a claim is higher than the previosu one. (bool)

    Overridden Methods:
    game_over
    player_action
    set_up
    """

    # Other names for the game.
    aka = ['Doubting Dice', 'Schummeln']
    # Command aliases
    aliases = {'scores': 'score'}
    # The menu categories for the game.
    categories = ['Dice Games']
    # The name templates for the poker hand versions of the dice.
    hand_names = ['six high missing {}', 'a pair of {}s with {}', 'two pair {}s over {}s with a {}', 
        'three {}s with {} and {}', 'a {}-high straight', 'full house {}s over {}s', 'four {}s and a {}', 
        'five {}s']
    # The name of the game.
    name = "Liar's Dice"
    # The number of game options.
    num_options = 5

    def challenge(self):
        """Handle someone making a claim. (None)"""
        # Get the relevant players.
        next_player = self.players[(self.player_index + 1) % len(self.players)]
        player = self.players[self.player_index]
        # Show the claim.
        claim_score = self.poker_score(self.claim)
        # Check for a challenge to the claim.
        if self.claim == [6, 6, 6, 6, 6]:
            next_player.ask('The claim is five sixes, you must challenge. Press Enter to continue: ')
            challenge = 'yes'
        else:
            challenge = next_player.ask('Do you wish to call {} a liar? '.format(player.name))
        if challenge in YES:
            self.human.tell('{} challenges {}.'.format(next_player.name, player.name))
            # Show the real score.
            real_score = self.poker_score(self.dice.values)
            self.human.tell('{} actually had {}.'.format(player.name, self.poker_text(real_score)))
            # Handle challengers win.
            if claim_score > real_score:
                self.human.tell('{} is a liar.'.format(player.name))
                self.resolve_challenge(next_player, player)
            # Handle challenger loss
            else:
                self.human.tell('{} told the truth.'.format(player.name))
                self.resolve_challenge(player, next_player)
            self.phase = 'start'
            self.human.tell()
        else:
            self.phase = 'reroll'

    def do_score(self, arguments):
        """
        Show how many tokens players have left. (bool)

        Parameters:
        arguments: The (ignored) arguments to the score command. (str)
        """
        # Get the sorted scores.
        scores = [(score, name) for name, score in self.scores.items() if score]
        scores.sort(reverse = True)
        # Show the scores
        self.human.tell()
        for score, name in scores:
            self.human.tell('{}: {}'.format(score, name))
        return True

    def game_over(self):
        """Check for the human losing or winning."""
        # Check for the human being out of the game.
        if self.human not in self.players:
            # Announce the loss.
            self.human.tell('\nYou have no more tokens, you lose the game.')
            before = len(self.scores) - len(self.players) - 1
            self.human.tell('{} players left the game before you did.'.format(before))
            # Record the win/loss/draw.
            self.win_loss_draw = [len(self.players), before, 0]
        # Check for the human being the only one left.
        elif len(self.players) == 1:
            # Announce and record the win.
            self.human.tell('\nYou win!')
            self.win_loss_draw = [len(self.scores) - 1, 0, 0]
        # Otherwise, continue.
        else:
            return False
        # If not continuing, end.
        return True

    def one_six_adjust(self, by_count, values):
        """
        Adjust value counts for the one-six option. (dict of int: list of int)

        Parameters:
        by_count: The counts and values with those counts. (dict of int: list of int)
        values: The values that were counted. (list of int)
        """
        # Get the counts.
        ones = values.count(1)
        sixes = values.count(6)
        # Remove the counts (if they exist)
        if ones:
            by_count[ones].remove(1)
            if sixes:
                by_count[sixes].remove(6)
            # Add the new count.
            by_count[ones + sixes].append(6)
        return by_count

    def one_wild_adjust(self, by_count, values):
        """
        Adjust value counts for the one-six option. (tuple of dict, list)

        Parameters:
        by_count: The counts and values with those counts. (dict of int: list of int)
        values: The values that were counted. (list of int)
        """
        ones = values.count(1)
        if ones:
            # Remove the count of ones.
            by_count[ones].remove(1)
            if not by_count[ones]:
                del by_count[ones]
            # Get the largest value with the largest count.
            max_count = max(by_count)
            max_value = max(by_count[max_count])
            # Check for a straight
            if max(by_count) == 1 and ones < 3:
                by_count = {1: [2, 3, 4, 5, 6]}
                values = [2, 3, 4, 5, 6]
            else:
                # Otherwise increase the best group.
                by_count[max_count].remove(max_value)
                if not by_count[max_count]:
                    del by_count[max_count]
                by_count[max_count + ones].append(max_value)
        return by_count, values

    def player_action(self, player):
        """
        Get a game action from the player. (None)

        Parameter:
        player: The current player. (player.Player)
        """
        # Display the game state.
        if self.phase == 'start':
            self.dice.roll()
            self.reset()
            self.human.tell('\n{} starts a new round by rolling all five dice.'.format(player.name))
            player.tell('\nThe new roll to you is {}.'.format(self.dice))
            if self.two_rerolls:
                self.phase = 'reroll-two'
            else:
                self.phase = 'claim'
        elif self.phase == 'reroll':
            player.tell('\nThe roll passed to you is {}.'.format(self.dice))
        elif self.phase in ('claim', 'reroll-two'):
            player.tell('\nYour roll is {}.'.format(self.dice))
        # Get the player action
        if self.phase == 'claim':
            # Get the claimed value.
            query = 'Enter five numbers for your claim, or return to be honest: '
            claim = player.ask_int_list(query, low = 1, high = 6, valid_lens = [5], 
                default = self.dice.values[:])
            # Handle other commands.
            if isinstance(claim, str):
                return self.handle_cmd(claim)
            # Validate the claim and check for a challenge.
            elif self.validate_claim(claim, player):
                self.challenge()
                return False
        elif self.phase.startswith('reroll'):
            # Get the dice to reroll.
            query = 'Enter the numbers you would like to reroll: '
            rerolls = player.ask_int_list(query, valid = self.dice.values, valid_lens = range(6), 
                default = [])
            # Handle other commands.
            if isinstance(rerolls, str):
                return self.handle_cmd(rerolls)
            # Reroll the specified dice and move to making a claim.
            else:
                if self.phase == 'reroll-two':
                    self.rerolls = max(self.rerolls, len(rerolls))
                else:
                    self.rerolls = len(rerolls)
                # Announce the rerolls
                reroll_text = number_word(len(rerolls))
                dice = ['dice', 'die'][len(rerolls) == 1]
                self.human.tell('\n{} rerolled {} {}.'.format(player.name, reroll_text, dice))
                # Make the rerolls
                for die_index, value in enumerate(self.dice.values):
                    if value in rerolls:
                        self.dice.roll(die_index)
                        rerolls.remove(value)
                if self.two_rerolls and self.phase != 'reroll-two':
                    self.phase = 'reroll-two'
                else:
                    self.phase = 'claim'
        return True

    def poker_score(self, values):
        """
        Generate a poker hand score for a set of values. (list of int)

        The score is a list of integers. The first number is the type of hand, from 7
        for five of a kind to 0 for high card. The rest of the numbers are the dice
        values in comparison order for that type of hand. Therefore you can naively
        compare the two integer lists to find out which is the higher hand.

        score[0] mapping:
            7 = five of a kind
            6 = four of a kind
            5 = full house
            4 = straight
            3 = three of a kind
            2 = two pair
            1 = pair
            0 = high card

        Parmeters:
        values: The claimed or rolled dice values. (lsit of int)
        """
        # Summarize the values.
        by_count = collections.defaultdict(list)
        for value in set(values):
            by_count[values.count(value)].append(value)
        # Account for ones being wild.
        if self.one_wild:
            by_count, values = self.one_wild_adjust(by_count, values)
        # Account for ones counting as sixes
        elif self.one_six:
            by_count = self.one_six_adjust(by_count, values)
        max_count = max(by_count)
        # Score by value.
        # Score a dummy hand.
        if 0 in values:
            score = [0] * 6
        # Score five of a kind.
        elif max_count == 5:
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
            print(score, self.dice)
            hand_name = hand_name.format(number_word(score[1]), number_word(score[5]))
        # Three of a kind needs the first word and two trailing words.
        elif score[0] == 3:
            words = number_word(score[1]), number_word(score[4]), number_word(score[5])
            hand_name = hand_name.format(*words)
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

    def reset(self):
        """Reset the tracking variables. (None)"""
        self.claim = [0, 0, 0, 0, 0]
        self.history = []
        self.rerolls = 5

    def resolve_challenge(self, winner, loser):
        """
        Handle the result of a challenge. (None)

        Parameters:
        winner: The player who won the challenge. (player.Player)
        loser: The player who lost the challenge. (player.Player)
        """
        # Adjust the scores.
        self.scores[loser.name] -= 1
        if self.betting:
            self.scores[winner.name] += 1
        # Remove players if necessary.
        if not self.scores[loser.name]:
            self.players.remove(loser)
            drop_message = '\n{} has lost all of their tokens and is out of the game.'
            self.human.tell(drop_message.format(loser.name))
            # Adjust the next player if the current player is removed.
            if self.player_index > len(self.players) or self.players[self.player_index] == loser:
                self.player_index -= 1

    def set_options(self):
        """Set the game specific options. (None)"""
        self.option_set.add_option('betting',
            question = 'Should lost tokens be given to the winner of the challenge? bool')
        self.option_set.add_option('two-rerolls', 
            question = 'Should you be able to make a second reroll? bool')
        self.option_set.add_option('chips', [], int, check = lambda x: x > 1,
            question = 'How many chips should each player start with (return for 3)? ')
        self.option_set.add_option('one-six', question = 'Should ones count as sixes? bool')
        self.option_set.add_option('one-wild', question = 'Should ones be wild? bool')

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the players.
        self.players = [self.human]
        taken_names = [self.human.name]
        for bot in range(4):
            bot_class = random.choice((ABBot, Challenger, Liar))
            self.players.append(bot_class(taken_names))
            taken_names.append(self.players[-1].name)
            self.players[-1].game = self
        # Set up the scores.
        self.scores = {player.name: self.chips for player in self.players}
        # Set up the dice.
        self.dice = dice.Pool([6] * 5)
        # Set up the tracking variables.
        self.reset()
        self.phase = 'start'

    def validate_claim(self, claim, player):
        """
        Validate that a player's claim is higher than the previosu one. (bool)

        Parameters:
        claim: The current player's claimed roll. (list of int)
        player: The current player. (player.Player)
        """
        # Get the old and new scores.
        new_score = self.poker_score(claim)
        old_score = self.poker_score(self.claim)
        if new_score > old_score:
            # If new score is higher, update tracking and move on.
            self.human.tell('{} claims they have {}.'.format(player.name, self.poker_text(new_score)))
            self.history.append(self.claim)
            self.claim = claim
            return True
        else:
            # If the new score isn't higher, post a warning and ask again.
            new_text = self.poker_text(new_score)
            old_text = self.poker_text(old_score)
            message = 'Your claim of {} is not better than the previous claim of {}.'
            player.error(message.format(new_text, old_text))
            return False


class ABBot(player.Bot):
    """
    An honest Liar's Dice bot. (player.Bot)

    Well, as honest as they can be.

    Class Attributes:
    believable: Score changes that will not be challenged. (dict of int: list)

    Methods:
    claim_check: Decide whether or not to call someone a liar. (str)
    lie: Generate a lie based on the current claim. (list of int)
    make_claim: Make a claim about the current roll. (list of int)
    reroll_check: Decide which dice to reroll. (list of int)

    Overridden Methods:
    ask
    ask_int
    """

    # Score changes that will not be challenged.
    believable = {7: [7], 6: [6, 7], 5: [5], 4: [4], 3: [3, 5, 6], 2: [2, 5], 1: [1, 2, 3, 4], 
        0: [0, 1, 2, 3]}

    def ask(self, query):
        """
        Ask the bot a question.

        query: The question asked of the bot. (str)
        """
        if 'liar' in query:
            return self.claim_check()
        if 'must' in query:
            return 'uh oh'
        else:
            # Error on unknown questions.
            raise player.BotError('Unexpected question to ABBot: {!r}'.format(query))

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
        if 'reroll' in prompt:
            return self.reroll_check(valid)
        elif 'claim' in prompt:
            return self.make_claim(default)
        else:
            # Error on unexpected question.
            raise player.BotError('Unexpected question to ABBot: {!r}'.format(prompt))

    def claim_check(self):
        """Decide whether or not to call someone a liar. (str)"""
        # Get the relevant scores.
        claim_score = self.game.poker_score(self.game.claim)
        prev_score = self.game.poker_score(self.game.history[-1])
        # Check them against the believability matrix.
        if claim_score[0] in self.believable[prev_score[0]]:
            return 'nope'
        elif self.game.two_rerolls:
            return 'nah'
        else:
            return 'yup'

    def lie(self, claim_score):
        """
        Generate a lie based on the current claim. (list of int)

        Parameters:
        claim_score: The poker_score output for the claim to lie about. (list of int)
        """
        # Five of a kind goes up one. Obvious, but what you gonna do?
        if claim_score[0] == 7:
            claim = [claim_score[1] + 1] * 5
        # Four kind/two pair bumps off die if possible, otherwise the scoring dice.
        elif claim_score[0] in (2, 6):
            if claim_score[5] == 6:
                claim = [value + 1 for value in claim_score[1:5]] + [1]
            else:
                claim = claim_score[1:5] + [claim_score[5] + 1]
        # Full house bump the two if possible, otherwise the three.
        elif claim_score[0] == 5:
            if claim_score[5] == 6:
                claim = [claim_score[1] + 1] * 3 + claim_score[-2:]
            else:
                claim = claim_score[1:4] + [claim_score[5] + 1] * 2
        # Straight go to high straight if possible, low full house otherwise.
        elif claim_score[0] == 4:
            if claim_score[1] == 6:
                claim = [2, 2, 2, 3, 3]
            else:
                claim = [2, 3, 4, 5, 6]
        # Otherwise bump the lowest die.
        elif claim_score[0] in (0, 1, 3):
            claim = claim_score[1:5] + [claim_score[5] + 1]
        return claim

    def make_claim(self, roll):
        """
        Make a claim about the current roll. (list of int)

        Parameters:
        roll: What was actually rolled. (list of int)
        """
        # Get the scores for the roll and thre previous claim.
        roll_score = self.game.poker_score(self.game.dice.values)
        claim_score = self.game.poker_score(self.game.claim)
        # Be honest if you can.
        if roll_score > claim_score:
            claim = roll
        else:
            # Otherwise, try and for the next highest claim.
            claim = self.lie(claim_score)
        return claim

    def reroll_check(self, roll):
        """
        Decide which dice to reroll. (list of int)
        
        Parameters:
        roll: The dice that were rolled.
        """
        score = self.game.poker_score(roll)
        # Reroll any dice not involved in scoring the hand type.
        # Straights, five of a kind and full houses score on all dice.
        if score[0] in (4, 5, 7):
            reroll = []
        # Four of a kind and two pair have one die to roll.
        elif score[0] in (6, 2):
            reroll = [score[5]]
        # Three of kind has two dice to reroll
        elif score[0] == 3:
            reroll = score[-2:]
        # One pair has three dice to reroll
        elif score[0] == 1:
            reroll = score[-3:]
        # For high card, keep the 6 and the 5 if there is one.
        elif score[0] == 0:
            reroll = [value for value in roll if value < 5]
        return reroll

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        pass


class Challenger(ABBot):
    """
    A Liar's Dice bot that challenges based on the odds. (ABBot)

    Note that the odds calculated assume that all numbers were distinct. This
    is just an approximation for decision making purposes.

    Class Attributes:
    odds: The odds matrix for getting n numbers on d dice. (dict of tuple: int)

    Overridden Methods:
    claim_check
    """

    odds = {(1, 1): 1 / 6, (2, 2): 2 / 36, (2, 1): 11 / 36, (3, 3): 1 / 36, (3, 2): 91 / 216, 
        (3, 1): 5 / 36, (4, 4): 1 / 54, (4, 3): 1 / 12, (4, 2): 302 / 1296, (4, 1): 671 / 1296}

    def claim_check(self):
        """Decide whether or not to call someone a liar. (str)"""
        # Do the standard check.
        challenge = super(Challenger, self).claim_check()
        # If that's okay, look at the odds.
        if challenge != 'yup':
            # Get the number of changed dice.
            current = self.game.claim
            old = self.game.history[-1]
            for die in old:
                if die in current:
                    current.remove(die)
            changed = len(current)
            # Get the number of rolled dice.
            rolled = self.game.rerolls
            # Challenge the impossible
            if changed > rolled:
                challenge = 'da'
            # Challenge the rest at odds
            elif rolled < 5:
                # Get the odds
                odds = self.odds[(rolled, changed)]
                if self.game.two_rerolls:
                    odds = odds + (1 - odds) * odds
                if random.random() > odds:
                    challenge = '1'
        return challenge


class Liar(ABBot):
    """
    A Liar's Dice bot that lies more than it needs to. (ABBot)

    Overridden Methods:
    make_claim
    """

    def make_claim(self, roll):
        """
        Make a claim about the current roll. (list of int)

        Parameters:
        roll: What was actually rolled. (list of int)
        """
        # Get the standard claim.
        claim = super(Liar, self).make_claim(roll)
        # Consider lying if not already lying.
        if claim != roll:
            score = self.game.poker_score(claim)
            if random.random() > score[0] / 7:
                claim = self.lie(score)
        return claim