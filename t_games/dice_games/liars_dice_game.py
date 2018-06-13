"""
liars_dice_game.py

A game of Liar's Dice.

Classes:
LiarsDice: A game of Liar's Dice. (game.Game)
ABBot: An honest Liar's Dice bot. (player.Bot)
"""


import collections

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
    claim: The claim made by the last player. (list of int)
    dice: The dice used in the game. (dice.Pool)
    phase: The current action the player needs to take. (str)

    Methods:
    challenge: Handle someone making a claim. (None)
    poker_score: Generate a poker hand score for a set of values. (list of int)
    poker_text: Convert a poker score into text. (str)
    reset: Reset the tracking variables. (None)
    validate_claim: Validate that a claim is higher than the previosu one. (bool)

    Overridden Methods:
    game_over
    player_action
    set_up
    """

    # Other names for the game.
    aka = ['Doubting Dice', 'Schummeln']
    # The menu categories for the game.
    categories = ['Dice Games']
    # The name templates for the poker hand versions of the dice.
    hand_names = ['six high missing {}.', 'a pair of {}s with {}', 'two pair {}s over {}s with a {}', 
        'three {}s with {} and {}', 'a {}-high straight', 'full house {}s over {}s', 'four {}s and a {}', 
        'five {}s']
    # The name of the game.
    name = "Liar's Dice"

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
            drop_message = '\n{} has lost all of their tokens and is out of the game.'
            if claim_score > real_score:
                self.human.tell('{} is a liar.'.format(player.name))
                self.scores[player.name] -= 1
                if not self.scores[player.name]:
                    self.players.remove(player)
                    self.human.tell(drop_message.format(player.name))
                    self.player_index -= 1
            # Handle challenger loss
            else:
                self.human.tell('{} told the truth.'.format(player.name))
                self.scores[next_player.name] -= 1
                if not self.scores[next_player.name]:
                    self.players.remove(next_player)
                    self.human.tell(drop_message.format(next_player.name))
            self.phase = 'start'
            self.human.tell()
        else:
            self.phase = 'reroll'

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
            self.phase = 'claim'
        elif self.phase == 'reroll':
            player.tell('\nThe roll passed to you is {}.'.format(self.dice))
        elif self.phase == 'claim':
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
        elif self.phase == 'reroll':
            # Get the dice to reroll.
            query = 'Enter the numbers you would like to reroll: '
            rerolls = player.ask_int_list(query, valid = self.dice.values, valid_lens = range(6), 
                default = [])
            # Handle other commands.
            if isinstance(rerolls, str):
                return self.handle_cmd(rerolls)
            # Reroll the specified dice and move to making a claim.
            else:
                self.rerolls = len(rerolls)
                # Announce the rerolls
                reroll_text = number_word(self.rerolls)
                dice = ['dice', 'die'][self.rerolls == 1]
                self.human.tell('\n{} rerolled {} {}.'.format(player.name, reroll_text, dice))
                # Make the rerolls
                for die_index, value in enumerate(self.dice.values):
                    if value in rerolls:
                        self.dice.roll(die_index)
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
        self.claim = [0, 1, 2, 3, 6]
        self.history = []
        self.rerolls = 5

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the players.
        self.players = [self.human]
        taken_names = [self.human.name]
        for bot in range(3):
            self.players.append(ABBot(taken_names))
            taken_names.append(self.players[-1].name)
            self.players[-1].game = self
        # Set up the scores.
        self.scores = {player.name: 3 for player in self.players}
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
            return self.make_claim()
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

    def make_claim(self):
        """Make a claim about the current roll. (list of int)"""
        # Get the scores for the roll and thre previous claim.
        roll_score = self.game.poker_score(self.game.dice.values)
        claim_score = self.game.poker_score(self.game.claim)
        # Be honest if you can.
        if roll_score > claim_score:
            claim = default
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