"""
ten_thousand_game.py

A game of Ten Thousand.

Constants:
CREDITS: The credits for TenThousand. (str)
RULES: The rules for TenThousand. (str)

Classes:
TenThousand: A game of TenThousand. (game.Game)
"""

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
minimum= (m=): The minimum number of points you must roll before you can score
    them.
no-second (n2): Second chance rolls are not allowed.
super-strikes (ss): If you don't score three turns in a row, you loose all of
    your points.
three-strikes (3s): If you don't score three turns in a row, you loose 500
    points.
threes-only (3o): Only ones, fives, and three of a kind score.
train-wreck (tw): If you roll all six dice and don't score, you lose all of
    your points.
wild: One die has a wild. If rolled with a pair or more, it must be used to
    complete the n-of-a-kind.
win= (w=): The number of points needed to win.
"""

class TenThousandBot(player.Bot):

    def ask(self, prompt):
        if prompt == '\nWhat is your move? ':
            if self.held and self.game.turn_score > 350:
                self.held = False
                move = 'score'
            elif self.held:
                self.held = False
                move = 'roll'
            else:
                self.held = True
                move = 'hold'
            print(self.name, move, self.game.dice, self.game.turn_score, self.game.scores[self.name])
            return move

    def set_up(self):
        self.held = False

    def tell(self, *args, **kwargs):
        pass

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
        return full_text.format(score_text, self.turn_score, self.dice)

    def do_hold(self, arguments):
        """
        Hold (set aside) scoring dice. (h)

        The values of the dice should be the arguments. If no arguments are given, all
        scoring dice are held. You can only hold scoring dice. For taking a second
        chance to score, use the second command.
        """
        player = self.players[self.player_index]
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
        else:
            # Hold all scoring dice if no arguments are given.
            possibles = [die.value for die in self.dice if not die.held]
            counts = [possibles.count(value) for value in range(7)]
            if sorted(possibles) == [1, 2, 3, 4, 5, 6] and self.straight:
                values = possibles
            elif counts.count(2) == 3 and self.two_pair:
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
        counts = [values.count(possible) for possible in range(7)]
        if values == [1, 2, 3, 4, 5, 6]:
            held_score = self.straight_score
        elif counts.count(2) == 3:
            held_score = self.three_pair_score
        else:
            held_score = 0
            for possible, count in enumerate(counts):
                sub_score = self.combo_scores[possible][count]
                if count and not sub_score:
                    error = "{} {}'s do not score and cannot be held"
                    player.error(error.format(utility.number_word(count), possible))
                    return True
                held_score += sub_score
        # Record the score and hold the dice.
        self.turn_score += held_score
        self.dice.hold(values)
        self.held_this_turn = True
        return True

    def do_roll(self, arguments):
        """
        Roll the unheld dice. (r)

        If all of the dice are held, all of the dice are rerolled.
        """
        player = self.players[self.player_index]
        # Check for having held dice.
        if not self.held_this_turn:
            player.error('You must hold dice before you can roll.')
            return False
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
        if not counts[1] and not counts[5] and counts.count(2) != 3 and max(counts) < 3:
            if values != [1, 2, 3, 4, 5, 6]:
                player.tell('{} did not score with that roll, their turn is over.'.format(player.name))
                self.end_turn()
                return False
        return True

    def do_score(self, arguments):
        """
        End the turn and score the points you rolled this turn. (s)
        """
        if self.must_roll:
            player.error('You must roll again because you rolled a {}.'.format(self.must_roll))
        elif not self.turn_score:
            player.error('You cannot stop without holding some scoring dice.')
        else:
            self.scores[self.players[self.player_index].name] += self.turn_score
            self.end_turn()
            return False
        return True

    def end_turn(self):
        """Reset the tracking variables for the next player. (None)"""
        self.held_this_turn = False
        self.turn_score = 0
        self.dice.release()
        self.dice.roll()

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
                if self.human.name != ranking[0][1]:
                    human_rank = ranking.index((self.scores[self.human.name], self.human.name)) + 1
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
        # Check for scoring options.
        self.straight_score = 1500
        self.three_pair_score = 1000
        self.win = 10000
        self.players = [self.human, TenThousandBot([self.human.name])]

    def player_action(self, player):
        """
        Handle a player's action. (bool)

        Parameters:
        player: The current player.
        """
        player.tell(self)
        move = player.ask('\nWhat is your move? ')
        return self.handle_cmd(move)

    def set_up(self):
        """Set up the game. (None)"""
        self.dice = dice.Pool([6] * 6)
        self.turn_score = 0
        self.held_this_turn = False
        self.last_player = None
        self.must_roll = ''
