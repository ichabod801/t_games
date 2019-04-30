"""
ten_thousand_game.py

A game of Ten Thousand.

Constants:
CREDITS: The credits for TenThousand. (str)
RULES: The rules for TenThousand. (str)

Classes:
TenThousand: A game of TenThousand. (game.Game)
"""

import random

from .. import dice
from .. import game
from .. import player
from .. import utility


CREDITS = """
Game Design: Traditional.
Game Programming: Craig "Ichabod" O'Brien
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
second (2): Make a second chance roll (list the dice you are trying to complete
    as a parameter to this command).

Options:
add-combos (ac): Five and six of a kind are worth 300 and 400 points times the
    number rolled, respectively.
clear-combo (cc): If your last roll scored a three or more of a kind, and you
    roll the number of that combo, you must reroll all the dice you just
    rolled.
crash (cr): If you roll all six dice and don't score, you loose 500 points.
drop-zero (d0): All scores listed are divided by 10.
entry= (e=): The minimum number of points needed to get on the table.
exact-win (ew): You must get exactly 10,000 points to win. If you do, no one
    gets a chance to beat you.
five-dice (5d): The game is played with five dice, with no six of a kind or
    straight.
force-combo (fc): If you score with three or more of a kind, you *must* roll
    again.
force-six (f6): If you score on all six dice, you *must* roll again.
min-grows (mg): You must roll more points as the previous scored in order to
    score yourself.
minimum= (m=): The minimum number of points you must roll before you can score
    them.
no-second (n2): Second chance rolls are not allowed.
straight= (s=): The score for a straight (1-6). Defaults to 0, or no straights.
super-strikes (ss): If you don't score three turns in a row, you loose all of
    your points.
three-pair= (3p=): The score for three pair. Defaults to 0, no three pair.
three-strikes (3s): If you don't score three turns in a row, you loose 500
    points.
threes-only (3o): Only ones, fives, and three of a kind score.
train-wreck (tw): If you roll all six dice and don't score, you lose all of
    your points.
wild: One die has a wild. If rolled with a pair or more, it must be used to
    complete the n-of-a-kind.
win= (w=): The number of points needed to win.
"""

class TenKBot(player.Bot):

    def ask(self, prompt):
        if prompt == '\nWhat is your move? ':
            if not self.game.held_this_turn:
                move = self.hold()
            elif self.game.turn_score < self.game.minimum:
                move = 'roll'
            elif self.game.turn_score < self.game.entry and not self.game.scores[self.name]:
                move = 'roll'
            elif self.game.last_player is not None:
                if self.game.scores[self.name] + self.game.turn_score <= max(self.game.scores.values()):
                    move = 'roll'
                else:
                    move = self.roll_or_score()
            else:
                move = self.roll_or_score()
            return move

    def hold(self):
        return 'hold'

    def roll_or_score(self):
        if self.game.turn_score < 350:
            return 'roll'
        else:
            return 'score'

    def set_up(self):
        self.bank = 0

    def tell(self, *args, **kwargs):
        if isinstance(args[0], TenThousand):
            new_bank = self.game.turn_score
            if new_bank == 0:
                self.bank = new_bank
            elif new_bank != self.bank:
                self.game.human.tell('{} banked {} points.'.format(self.name, new_bank - self.bank))
                self.bank = new_bank
        else:
            super(TenKBot, self).tell(*args, **kwargs)


class GamblerBot(TenKBot):

    score_chance = [0.97, 0.33, 0.56, 0.72, 0.84, 0.92]

    def roll_or_score(self):
        to_roll = len(filter(lambda die: not die.held, self.game.dice))
        if random.random() < self.score_chance[to_roll]:
            return 'roll'
        else:
            return 'score'


class KniziaBot(TenKBot):
    """Almost, it leaves out one tiny bit."""

    def hold(self):
        """Determine the hold command (which dice to hold). (None)"""
        # Calculate the values used in the decision making.
        possibles = [die.value for die in self.game.dice if not die.held]
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
            if self.game.turn_score > 2850:
                self.score = True
            elif self.game.turn_score > 1550:
                if max_points >= 200:
                    self.score = True
                else:
                    move = 'hold 1' if counts[1] else 'hold 5'
            elif self.game.turn_score > 900:
                if max_points >= 250 or counts[2] == 3:
                    self.score = True
                else:
                    move = 'hold 1' if counts[1] else 'hold 5'
            elif self.game.turn_score:
                if max_points >= 300 or (counts[2] == 3 and not (counts[1] + counts[5])):
                    self.score = True
                else:
                    move = 'hold 1' if counts[1] else 'hold 5'
            # Handle initial rolls.
            elif counts[2] == 3:
                if counts[5] == 2:
                    self.score = True
            elif counts[3] != 3 and counts[1]:
                move = 'hold {}'.format(' '.join(['1'] * counts[1]))
            elif counts[3] != 3:
                move = 'hold 5'
        # For five dice, hold minimally and roll without three of a kind, score otherwise.
        elif dice_thrown == 5:
            if counts[2] == 3:
                self.score = True
            elif counts[1] == 2:
                if counts[5]:
                    self.score = True
            else:
                move = 'hold 1' if counts[1] else 'hold 5'
        # For four dice, hold minimally unless three 2's, score on three 2's or three individual 1's.
        elif dice_thrown == 4:
            if counts[2] == 3:
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
        if self.score and [die for die in self.game.dice if not die.held]:
            move = 'score'
        else:
            move = 'roll'
        self.score = False
        return move

    def set_up(self):
        super(KniziaBot, self).set_up()
        self.score = False


class TenThousand(game.Game):
    """
    A game of TenThousand. (game.Game)

    Overridden Methods:
    __str__
    setup
    """

    aka = ['Zilch', 'Dice 10,000', 'Dice 10000', 'Dice 10K', 'Farkle', '10K']
    aliases = {'h': 'hold', 'r': 'roll', 's': 'score'}
    categories = ['Dice Games']
    name = 'Ten Thousand'

    combo_scores = [[0], [0, 100, 200, 1000, 1100, 1200, 2000], [0, 0, 0, 200, 0, 0, 400],
        [0, 0, 0, 300, 0, 0, 600], [0, 0, 0, 400, 0, 0, 800],
        [0, 50, 100, 500, 550, 600, 1000], [0, 0, 0, 600, 0, 0, 1200]]

    def __str__(self):
        """Human readable text representation. (str)"""
        score_text = '\n'.join('{}: {}'.format(name, score) for name, score in self.scores.items())
        full_text = '\nScores:\n{}\n\nYou have banked {} points this turn.\nThe roll to you is {}.'
        if self.min_grows:
            full_text = '{}\nThe minimum turn score is {}.'.format(full_text, self.minimum)
        return full_text.format(score_text, self.turn_score, self.dice)

    def do_hold(self, arguments):
        """
        Hold (set aside) scoring dice. (h)

        The values of the dice should be the arguments. If no arguments are given, all
        scoring dice are held. You can only hold scoring dice. For taking a second
        chance to score, use the second command.
        """
        player = self.players[self.player_index]
        possibles = [die.value for die in self.dice if not die.held]
        counts = [possibles.count(value) for value in range(7)]
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
                values = map(int, values)
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
            if sorted(possibles) == [1, 2, 3, 4, 5, 6] and self.straight:
                values = possibles
            elif counts.count(2) == 3 and self.three_pair:
                values = possibles
            else:
                values = []
                for possible in set(possibles):
                    for count in range(counts[possible], 0, -1):
                        if self.combo_scores[possible][count]:
                            values.extend([possible] * count)
                            break
        values.sort()
        # Score the held dice.
        held_score = self.score_dice(values)
        if held_score == -1:
            error = "{} {}'s do not score and cannot be held"
            player.error(error.format(utility.number_word(count), possible))
            return True
        # Record the score and hold the dice.
        self.dice.hold(values)
        self.turn_score += held_score
        self.held_this_turn = True
        return True

    def do_roll(self, arguments):
        """
        Roll the unheld dice. (r)

        If all of the dice are held, all of the dice are rerolled.
        """
        player = self.players[self.player_index]
        # Check for having held dice.
        if not (self.held_this_turn or self.new_turn):
            player.error('You must hold dice before you can roll.')
            return True
        # Reset the dice if they've all been rolled.
        if not filter(lambda die: not die.held, self.dice):
            self.dice.release()
        # Roll the dice.
        self.dice.roll()
        self.held_this_turn = False
        values = sorted([die.value for die in self.dice if not die.held])
        print('\n{} rolled: {}.'.format(player.name, ', '.join([str(value) for value in values])))
        # Check for no score.
        counts = [values.count(possible) for possible in range(7)]
        if not counts[1] and not counts[5] and max(counts) < 3:
            if self.straight and values == [1, 2, 3, 4, 5, 6]:
                pass
            if self.three_pair and counts.count(2) == 3:
                pass
            else:
                player.tell('{} did not score with that roll, their turn is over.'.format(player.name))
                self.end_turn()
                if self.min_grows:
                    self.minimum = 0
                return False
        return True

    def do_score(self, arguments):
        """
        End the turn and score the points you rolled this turn. (s)
        """
        player = self.players[self.player_index]
        if self.must_roll:
            player.error('You must roll again because you rolled a {}.'.format(self.must_roll))
        elif not self.turn_score:
            player.error('You cannot stop without holding some scoring dice.')
        elif self.turn_score < self.minimum:
            player.error('You cannot stop until you score {} points.'.format(self.minimum))
        elif self.turn_score < self.entry and not self.scores[player.name]:
            player.error('You cannot stop the first time until you score {} points.'.format(self.entry))
        else:
            self.scores[self.players[self.player_index].name] += self.turn_score
            if self.min_grows:
                self.minimum = self.turn_score + 50
            self.end_turn()
            return False
        return True

    def end_turn(self):
        """Reset the tracking variables for the next player. (None)"""
        self.held_this_turn = False
        self.turn_score = 0
        self.dice.release()
        self.new_turn = True

    def game_over(self):
        """Determine if the game is over. (bool)"""
        if max(self.scores.values()) >= self.win:
            player = self.players[self.player_index]
            if self.last_player is None:
                self.last_player = self.players[self.player_index - 1]
                warning = 'Everyone gets one roll to beat {}. {} gets the last roll.'
                self.human.tell(warning.format(player, self.last_player))
                return False
            elif player == self.last_player:
                ranking = [(score, player) for player, score in self.scores.items()]
                ranking.sort(reverse = True)
                self.human.tell('{1} wins with {0} points.'.format(*ranking[0]))
                human_score = self.scores[self.human.name]
                for score, name in ranking:
                    if score > human_score:
                        self.win_loss_draw[1] += 1
                    elif score == human_score and name != self.human.name:
                        self.win_loss_draw[2] += 1
                    elif score < human_score:
                        self.win_loss_draw[0] += 1
                if self.human.name != ranking[0][1]:
                    human_rank = self.win_loss_draw[1] + 1
                    text = 'You came in {} place with {} points.'
                    rank_word = utility.number_word(human_rank, ordinal = True)
                    self.human.tell(text.format(rank_word, self.scores[self.human.name]))
                return True
        else:
            return False

# Note that cosmic wimpout is zilch / cc cr d0 e=350 5d fc f6 m=0 ns ss tw wild w=5000
    def handle_options(self):
        """Handle the game options. (None)"""
        super(TenThousand, self).handle_options()

    def player_action(self, player):
        """
        Handle a player's action. (bool)

        Parameters:
        player: The current player.
        """
        if self.new_turn:
            if not self.do_roll(''):
                return False
            self.new_turn = False
        player.tell(self)
        move = player.ask('\nWhat is your move? ')
        return self.handle_cmd(move)

    def set_options(self):
        """Set the options for the game. (None)"""
        # Add name variants.
        self.option_set.add_group('5000', 'w=5000')
        self.option_set.add_group('5k', 'w=5000')
        # Set the bot options.
        self.option_set.default_bots = ((TenKBot, ()), (GamblerBot, ()), (KniziaBot, ()))
        # Set the scoring options.
        self.option_set.add_option('straight', ['s'], int, 0,
            question = 'How much should a straight score (return for 0)? ')
        self.option_set.add_option('three-pair', ['3p'], int, 0,
            question = 'How much should three pair score (return for 0)? ')
        # Set the stopping options.
        self.option_set.add_option('entry', ['e'], int, 0,
            question = 'How many points should be required to stop the first time (return for 0)? ')
        self.option_set.add_option('min-grows', ['mg'])
        self.option_set.add_option('minimum', ['m'], int, 0,
            question = 'How many points should be required to stop in general (return for 0)? ')
        # Set the end of game options.
        self.option_set.add_option('win', ['w'], int, 10000,
            question = 'How many points should it take to win (return for 10,000)? ')

    def set_up(self):
        """Set up the game. (None)"""
        self.dice = dice.Pool([6] * 6)
        self.turn_score = 0
        self.held_this_turn = False
        self.last_player = None
        self.must_roll = ''
        self.new_turn = True

    def score_dice(self, values, validate = True):
        counts = [values.count(possible) for possible in range(7)]
        if values == [1, 2, 3, 4, 5, 6] and self.straight:
            held_score = self.straight
        elif counts.count(2) == 3 and self.three_pair:
            held_score = self.three_pair
        else:
            held_score = 0
            for possible, count in enumerate(counts):
                sub_score = self.combo_scores[possible][count]
                if count and not sub_score:
                    if validate:
                        return -1
                    else:
                        for sub_count in range(count, 0, -1):
                            sub_score = self.combo_scores[possible][sub_count]
                            if sub_score:
                                break
                held_score += sub_score
        return held_score
