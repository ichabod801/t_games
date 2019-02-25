"""
prisoners_game.py

An implementation of the Iterated Prisoner's Dilemma.

Constants:
CREDITS: The credits for Priosoner's Dilemma.
RULES: The rules for Prisoner's Dilemma.

Classes:
PrisonersDilemma: A game of the Interated Prisoner's Dilemma. (game.Game)
"""


import itertools

from .. import game


CREDITS = """
Game Design: Merrill Flood and Melvin Dresher
Game Programming: Craig "Ichabod" O'Brien
Bot Design: Anatol Rapoport
"""

RULES = """
Each turn, you and your opponent make the choice to cooperate or defect. If
both players cooperate, they both score the punishment. If they both defect,
they both score the reward. If one defects and the other cooperates, the
cooperator scores the sucker bet, while the defecter wins the temptation. The
standard scores are:

    Temptation: 3
    Reward: 2
    Punishment: 1
    Sucker Bet: 0

The game is played over multiple turns. Each round you know who you are playing
against, but you don't know their move until the result is calculated.

The idea of the game is that the rational move is always to defect: that will
get you the best score no matter what your opponent does. However, mutual
cooperation is a better outcome (the total score is highest).

Options:
iterations= (i=): The number of rounds played (defaults to 10).
punishment= (p=): The punishment score. It must be higher than the sucker bet.
reward= (r=): The reward score. It must be higher than the punishment score.
sucker= (s=): The sucker bet score. It must be lower than the punishment score.
temptation= (t=): The temptation score. It must be higher than the reward
    score.
"""


class PrisonersDilemma(game.Game):
    """
    A game of the Interated Prisoner's Dilemma. (game.Game)
    """

    credits = CREDITS
    move_aliases = {'c': 'cooperate', 'd': 'defect'}
    num_options = 4
    rules = RULES

    def game_over(self):
        """Check for the end of the game. (bool)"""
        return self.turns == self.num_turns

    def handle_options(self):
        """Handle the game options from the user. (None)"""
        super(PrisonersDilemma, self).handle_options(self)

    def player_action(self, player):
        """
        Run one round of the player's dilemma. (None)

        This doesn't run one player's action, it runs one iteration of the Iterated
        Prisoner's Dilemma. That is, it does the Prisoner's Dilemma for every pair of
        players.
        """
        # Check each pair of players.
        for sub_players in itertools.combinations(self.players, 2):
            # Get the moves
            moves = []
            queries = ['What is your move against {}? '.format(player.name) for player in sub_players]
            queries.reverse()
            for player, query in zip(sub_players, queries):
                while True:
                    move = player_1.ask(query).lower()
                    move = move_aliases.get(move_1, move_1)
                    if move in ('cooperate', 'defect'):
                        break
                    else:
                        self.handle_cmd(move_1)
            moves.append(move)
            # Get the scoring results.
            if moves == ['cooperate', 'cooperate']:
                round_scores = [self.points['punishment'], self.points['punishment']]
            elif moves == ['cooperate', 'defect']:
                round_scores = [self.points['temptation'], self.points['sucker']]
            elif moves == ['defect', 'cooperate']:
                round_scores = [self.points['sucker'], self.points['temptation']]
            elif moves == ['defect', 'defect']:
                round_scores = [self.points['reward'], self.points['reward']]
            # Score the points and inform the players
            for player, round_score in zip(sub_players, round_scores):
                self.scores[player.name] += round_score
                foe_index = 1 - sub_players.index(player)
                foe_name = sub_players[foe_index].name
                foe_move = moves[foe_index]
                player.tell('{} chose to {}.'.format(foe_name, foe_move))
        return False

    def set_options(self):
        """Set the possible game options. (None)"""
        self.points = {}
        self.option_set.add_option('sucker', ['s'], int, default = 0, action = 'key=sucker',
            target = self.points,
            question = 'How much should the sucker bet be worth (return for 0)? ')
        self.option_set.add_option('sucker', ['s'], int, default = 0, action = 'key=sucker',
            target = self.points,
            question = 'How much should the punishment be worth (return for 1)? ')
        self.option_set.add_option('sucker', ['s'], int, default = 0, action = 'key=sucker',
            target = self.points,
            question = 'How much should the reward be worth (return for 2)? ')
        self.option_set.add_option('sucker', ['s'], int, default = 0, action = 'key=sucker',
            target = self.points,
            question = 'How much should the temptation be worth (return for 3)? ')
