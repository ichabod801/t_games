"""
mate_game.py

A game of Mate.

Constants:
CREDITS: The credits for Mate. (str)
RULES: The rules of Mate. (str)

Classes:
Mate: A game of mate. (game.Game)
"""


import random

import t_games.dice as dice
import t_games.game as game
import t_games.player as player


CREDITS = """
Game Design: Craig "Ichabod" O'Brien
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Mate is a dice game using special dice that have Chess pieces as sides. Each
player has five dice which are rolled at the beginning of the game, and set in
a row opposite the other player's dice. Each 'piece' has a different point
value, and a differnt way to capture:

    * Queen: Queens can capture any opposing piece and are worth 5 points.
    * Rooks: Rooks can capture any opposing piece in the same or an adjacent
      column, and they are worth 3 points.
    * Bishops: Bishops can capture any opposing piece in an adjacent column,
      and they are worth 2 points.
    * Knights: Knights can capture any opposing piece two or three columns away
      from them, and they are worth 2 points.
    * Pawns: Pawns can capture the other piece in their column, and they are
      worth one point.

Players alternate turns. On their turn a play choses the column of one of their
own pieces (the attacker) and the column of an opponent's piece (the captured
piece). If the entry is valid, the player scores points equal to the opponent's
piece, and both dice are rerolled.

The first player to 64 points wins the game. If the score is tied at 64 or
higher, two more turns are played.
"""


class Mate(game.Game):
    """
    A game of Mate. (game.Game)

    Attributes:
    dice: The dice for each player, keyed by player name. (dict of str: dice.Pool)
    turns_left: The number of turns left after a winning tie. (int)

    Methods:
    dice_line: Show a player's dice with their columns. (str)
    get_moves: Determine the valid moves for a given player. (self)

    Overridden Methods:
    __str__
    game_over
    player_action
    set_up
    """

    attacks = {'Pawn': (0,), 'Knight': (-3, -2, 2, 3), 'Bishop': (-1, 1),
        'Rook': (-1, 0, 1), 'Queen': tuple(range(-5, 6))}
    categories = ['Dice Games']
    name = 'Mate'
    sides = ('Pawn', 'Pawn', 'Knight', 'Bishop', 'Rook', 'Queen')
    points = {'Pawn': 1, 'Knight': 2, 'Bishop': 2, 'Rook': 3, 'Queen': 5}

    def __str__(self):
        """Human readable text representation. (str)"""
        if self.players[self.player_index] == self.human:
            bot = self.players[1 - self.player_index]
        else:
            bot = self.players[self.player_index]
        lines = ['']
        lines.append('{}: {}'.format(bot.name, self.scores[bot.name]))
        lines.append(self.dice_line(self.dice[bot.name]))
        lines.append('-' * 53)
        lines.append(self.dice_line(self.dice[self.human.name]))
        lines.append('{}: {}'.format(self.human.name, self.scores[self.human.name]))
        return '\n'.join(lines)

    def dice_line(self, pool):
        """
        Show a player's dice with their columns. (str)

        Parameters:
        pool: The dice to show. (dice.Pool)
        """
        text = ['{}: {:<8}'.format(column, die.value) for column, die in enumerate(pool)]
        return ''.join(text)

    def game_over(self):
        """Check for the end of the game. (bool)"""
        if self.players[self.player_index] == self.human:
            bot = self.players[1 - self.player_index]
        else:
            bot = self.players[self.player_index]
        bot_score = self.scores[bot.name]
        human_score = self.scores[self.human.name]
        if bot_score == human_score and bot_score >= 64:
            self.turns_left = 2
            return False
        elif bot_score < 64 and human_score < 64:
            return False
        elif bot_score > human_score:
            self.human.tell('You lose, {} to {}. :('.format(human_score, bot_score))
            self.win_loss_draw = [0, 1, 0]
        else:
            self.human.tell('You win! {} to {}!'.format(human_score, bot_score))
            self.win_loss_draw = [1, 0, 0]
        return True

    def get_moves(self, player):
        """
        Determine the valid moves for a given player. (self)

        Parameters:
        player: The current player. (player.Player)
        """
        valid = []
        targets = range(5)
        for attacker in range(5):
            for attack in self.attacks[self.dice[player.name].values[attacker]]:
                if attacker + attack in targets:
                    valid.append([attacker, attacker + attack])
        return valid

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        player.tell(self)
        # Get the player's move.
        valid_pairs = self.get_moves(player)
        attack_choice = player.ask_int('\nEnter the column of your attacking piece: ', low = 0, high = 4)
        valid_targets = [target for attacker, target in valid_pairs if attacker == attack_choice]
        target_choice = player.ask_int('Enter the column of your target: ', valid = valid_targets)
        # Score the move.
        foe = self.players[1 - self.player_index]
        self.scores[player.name] += self.points[self.dice[foe.name].values[target_choice]]
        # Reroll the dice.
        self.dice[player.name].roll(attack_choice)
        self.dice[foe.name].roll(target_choice)

    def set_up(self):
        """Set up the game. (None)"""
        self.players = [self.human, MateAttackBot(taken_names = [self.human.name])]
        for player in self.players:
            player.game = self
        self.dice = {}
        for player in self.players:
            self.dice[player.name] = dice.Pool([self.sides for die in range(5)])


class MateBot(player.Bot):
    """
    A bot player for the game of Mate. (player.Bot)

    The base MateBot just plays randomly.

    Methods:
    choose_attacker: Choose the column to attack with. (int)
    choose_target: Choose the column to attack. (int)

    Overridden Methods:
    ask_int
    """

    def ask_int(self, prompt, low = None, high = None, valid = [], default = None, cmd = True):
        """
        Get an integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        valid: The valid values for the integer. (container of int)
        default: The default choice. (int or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        if prompt.endswith('attacking piece: '):
            return self.choose_attacker()
        elif prompt.endswith('your target: '):
            target = self.choose_target(valid)
            values = (self.name, self.game.dice[self.game.human.name].values[target], target)
            values += (self.game.dice[self.name].values[self.attacker], self.attacker)
            self.game.human.tell('\n{} takes your {} ({}) with their {} ({}).'.format(*values))
            return target
        else:
            raise BotError('Unexpected question asked of {}: {!r}.'.format(self.__class__.name, prompt))

    def choose_attacker(self):
        """Choose the column to attack with. (int)"""
        self.attacker = random.randrange(5)
        return self.attacker

    def choose_target(self, valid):
        """
        Choose the column to attack. (int)

        Parameters:
        valid: The columns that can be attacked. (list of int)
        """
        return random.choice(valid)


class MateAttackBot(MateBot):
    """
    A bot that goes after the biggest target. (MateBot)

    Overridden Methods:
    choose_attacker
    choose_target
    """

    def choose_attacker(self):
        """Choose the column to attack with. (int)"""
        moves = self.game.get_moves(self)
        moves = [(target, attacker) for attacker, target in moves]
        human_values = self.game.dice[self.game.human.name].values
        my_values = self.game.dice[self.name].values
        pieces = [(human_values[target], my_values[attacker]) for target, attacker in moves]
        values = [(self.game.points[target], self.game.points[attacker]) for target, attacker in pieces]
        valued_moves = list(zip(values, moves))
        valued_moves.sort(reverse = True)
        max_valued = [move for value, move in valued_moves if value == valued_moves[0][0]]
        self.target, self.attacker = max_valued[0]
        return self.attacker

    def choose_target(self, valid):
        """
        Choose the column to attack. (int)

        Parameters:
        valid: The columns that can be attacked. (list of int)
        """
        return self.target


