"""
prisoners_game.py

An implementation of the Iterated Prisoner's Dilemma.

Constants:
CREDITS: The credits for Priosoner's Dilemma.
RULES: The rules for Prisoner's Dilemma.

Classes:
PrisonerBot: A bot template for the Iterated Prisoner's Dilemma. (player.Bot)
PrisonersDilemma: A game of the Interated Prisoner's Dilemma. (game.Game)
"""


import itertools

from .. import game
from .. import player


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


class PrisonerBot(player.Bot):
    """
    A bot template for the Iterated Prisoner's Dilemma. (player.Bot)

    Methods:
    get_move: Make a move in the game. (str)

    Overridden Methods:
    ask
    set_up
    tell
    """

    def ask(self, query):
        """
        Answer a question to the player. (str)

        Parameters:
        query: The question asked of the player. (str)
        """
        if query.startswith('What is your move'):
            return self.get_move(query[26:-2])
        else:
            player.BotError('Unexpected move asked of {}: {!r}'.format(self.__class__.__name__, query))

    def get_move(self, foe_name):
        """
        Make a move in the game. (str)

        Parameters:
        foe_name: The name of the player to make a move against.
        """
        return random.choice(('cooperate', 'defect'))

    def set_up(self):
        """Set up the bot."""
        self.history = {player.name: [] for player in self.game.players}
        del self.history[self.name]

    def tell(self, *args, **kwargs):
        """Give the player some information. (None)"""
        if 'chose to' in args[0]:
            middle = args[0].index(' chose to ')
            foe_name = args[0][:middle]
            if 'cooperate' in args[0]:
                self.history[foe_name].append('cooperate')
            else:
                self.history[foe_name].append('defect')


class AlwaysCooperate(PrisonerBot):
    """
    A prisoner that always cooperates. (PrisonerBot)

    Overridden Methods:
    get_move
    """

    def get_move(self, foe_name):
        """
        Make a move in the game. (str)

        Parameters:
        foe_name: The name of the player to make a move against.
        """
        return 'cooperate'


class AlwaysDefect(PrisonerBot):
    """
    A prisoner that always defects. (PrisonerBot)

    Overridden Methods:
    get_move
    """

    def get_move(self, foe_name):
        """
        Make a move in the game. (str)

        Parameters:
        foe_name: The name of the player to make a move against.
        """
        return 'defect'


class TitForTat(PrisonerBot):
    """
    A player that repeats its foe's last move. (PrisonerBot)

    If the foe has not been met yet, Tit for Tat defects.

    Overridden Methods:
    get_move
    """

    def get_move(self, foe_name):
        """
        Make a move in the game. (str)

        Parameters:
        foe_name: The name of the player to make a move against.
        """
        if self.history[foe_name]:
            return self.history[foe_name][-1]
        else:
            return 'defect'


class PrisonersDilemma(game.Game):
    """
    A game of the Interated Prisoner's Dilemma. (game.Game)

    Class Attributes:
    move_alaises: Different names for the possible moves. (dict of str: str)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_options
    """

    categories = ['Other Games']
    credits = CREDITS
    move_aliases = {'c': 'cooperate', 'd': 'defect'}
    name = "Prisoner's Dilemma"
    num_options = 4
    rules = RULES

    def game_over(self):
        """Check for the end of the game. (bool)"""
        if self.turns == self.num_turns:
            scores = [(score, player) for player, score in self.scores.items()]
            scores.sort(reverse = True)
            human_score = self.scores[self.human.name]
            result_index = 1
            self.human.tell('\nFinal Scores:')
            for score, name in scores:
                self.human.tell('{}: {}'.format(score, name))
                if name == self.human.name:
                    continue
                if score > human_score:
                    self.win_loss_draw[1] += 1
                elif score < human_score:
                    self.win_loss_draw[0] += 1
                else:
                    self.win_loss_draw[2] += 1
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options from the user. (None)"""
        self.option_set.handle_settings(self.raw_options)

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
                    move = player.ask(query).lower()
                    move = self.move_aliases.get(move, move)
                    if move in ('cooperate', 'defect'):
                        break
                    else:
                        self.handle_cmd(move)
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
        self.option_set.default_bots = [(TitForTat, ()), (AlwaysCooperate, ()), (AlwaysDefect, ())]
        self.option_set.add_option('sucker', ['s'], int, default = 0, action = 'key=sucker',
            target = self.points,
            question = 'How much should the sucker bet be worth (return for 0)? ')
        self.option_set.add_option('punishment', ['p'], int, default = 1, action = 'key=punishment',
            target = self.points,
            question = 'How much should the punishment be worth (return for 1)? ')
        self.option_set.add_option('reward', ['r'], int, default = 2, action = 'key=reward',
            target = self.points,
            question = 'How much should the reward be worth (return for 2)? ')
        self.option_set.add_option('temptation', ['t'], int, default = 3, action = 'key=temptation',
            target = self.points,
            question = 'How much should the temptation be worth (return for 3)? ')
        self.option_set.add_option('num-turns', ['nt'], int, default = 10,
            question = 'How many turns should be played (return for 10)? ')
