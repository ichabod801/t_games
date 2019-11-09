"""
prisoner_game.py

An implementation of the Iterated Prisoner's Dilemma.

Copyright (C) 2018 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Priosoner's Dilemma.
RULES: The rules for Prisoner's Dilemma.

Classes:
PrisonerBot: A bot template for the Iterated Prisoner's Dilemma. (player.Bot)
PrisonerNumBot: An IPD bot set on simple parameters. (PrisonerBot)
RemorsefulBot: An IPD bot that regrets provoking it's foe. (PrisonerNumBot)
PrisonerMethodBot: An IPD Bot based on overriding methods. (PrisonerBot)
GradualBot: Retailiate n times after the nth retailiation. (PrisonerMethodBot)
PavlovBot: Repeats the last choice if he got a bad result (PrisonerMethodBot)
PrisonersDilemma: A game of the Interated Prisoner's Dilemma. (game.Game)
"""


import itertools
import random

from .. import game
from .. import player


CREDITS = """
Game Design: Merrill Flood and Melvin Dresher
Game Programming: Craig "Ichabod" O'Brien
Bot Design: Robert Axelrod, B. Beaufils, S. Braver, K. Deb, J. Delahaye, James
    Friedman, J. Komorita, David Kraines, Vivian Kraines, S. Mittal, Mathieu Our,
    Anatol Rapoport, J. Sheposh
"""

RULES = """
Each turn, you and your opponent make the choice to cooperate or defect. If
both players cooperate, they both score the reward. If they both defect,
they both score the punishment. If one defects and the other cooperates, the
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

Bot Options:
all-co (ac): Add an Always Cooperate bot.
all-def (ad): Add an Always Defect bot.
gradual (gl): Tit for Tat, but n tits for nth tat, with cool down.
grim (gm): Retaliates forever after a single defect.
hard-majr (hm): Defects on a majority of defects, otherwise cooperates.
naive-prober (np): Add a Naive Prober bot (Tit for Tat with occasional
    defection)
pavlov (pv): Add a Pavlov bot (changes his move when he scores poorly, keeps it
    otherwise)
prober (pb): Starts with d, c, c. Defects forever if foe cooperates second and
    third move, otherwise plays Tit for Tat.
prober-2 (p2): Starts with d, c, c. Cooperates forever if foe plays d, c second
    and third move, otherwise plays Tit for Tat.
prober-3 (p3): Starts with d, c. Defects forever if foe plays c on the second
    move, otherwise plays Tit for Tat.
random (rd): Add a Random bot.
soft-grudge (sg): Retailiates four times, followed by two cooperations.
soft-majr (sm): Cooperates on a majority of cooperations, otherwise defects.
tit-tat (tt): Add a Tit for Tat bot.
tit-2tat (t2): Add a Tit for Two Tats bot.
2tit-tat (2t): Add a Two Tits for Tat bot.

The default bots are three chosen at random.
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
            foe_name = query[26:-2]
            last_move = self.get_move(foe_name)
            self.history['Me vs. {}'.format(foe_name)].append(last_move)
            return last_move
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
        self.history.update({'Me vs. {}'.format(player.name): [] for player in self.game.players})
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


class MajorityBot(PrisonerBot):
    """
    An IPD bot that decides based on majoryities of foe moves. (PrisonerBot)

    Overridden Methods:
    get_move
    """

    def __init__(self, move = 'cooperate', majority = 'cooperate', taken_names = [], initial = ''):
        """
        Set up the strategy for the bot.

        Parameters:
        move: The move to make on a majority. (str)
        majority: The majority to check. (str)
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        super(MajorityBot, self).__init__(taken_names, initial)
        self.move = move
        self.majority = majority
        self.other = 'cooperate' if move == 'defect' else 'defect'

    def get_move(self, foe_name):
        """
        Make a move in the game. (str)

        Parameters:
        foe_name: The name of the player to make a move against.
        """
        count = self.history[foe_name].count(self.majority)
        other_count = len(self.history[foe_name]) - count
        if count >= other_count:
            return self.move
        else:
            return self.other


class PrisonerNumBot(PrisonerBot):
    """
    An IPD bot set on simple parameters. (PrisonerBot)

    Methods:
    be_nice: Generate a 'nice' move. (str)
    get_move: Make a move in the game. (str)

    Overridden Methods:
    ask
    set_up
    tell
    """

    def __init__(self, tits = ['d'], tats = 0, prob_nice = 0.5, taken_names = [], initial = ''):
        """
        Set up the strategy for the bot. (None)

        Parameters:
        tits: How many times the bot retaliates. (int)
        tats: How many defects it takes for the bot to retaliate. (int)
        prob_nice: If not retaliating, how like the bot is to cooperate. (float)
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        super(PrisonerNumBot, self).__init__(taken_names, initial)
        self.tits = tits
        self.tats = tats
        self.prob_nice = prob_nice
        self.current_tits = []

    def be_nice(self):
        """Generate a 'nice' move. (str)"""
        return 'cooperate'

    def get_move(self, foe_name):
        """
        Make a move in the game. (str)

        Parameters:
        foe_name: The name of the player to make a move against.
        """
        if self.current_tits:
            return self.current_tits.pop()
        elif self.tats and self.history[foe_name][-self.tats:] == ['defect'] * self.tats:
            self.current_tits = self.tits[:]
            return self.current_tits.pop()
        elif random.random() < self.prob_nice:
            return self.be_nice()
        else:
            return 'defect'


class ProbeBot(PrisonerNumBot):
    """
    An IPD bot that guesses foe's strategy. (PrisonerNumBot)
    """

    def __init__(self, start = ['d', 'c', 'c'], mask = ['dc', 'c', 'c'], prob_nice = 0, remorse = False,
        taken_names = [], initial = ''):
        """
        Set up the strategy for the bot. (None)

        Parameters:
        start: The bot's initial plays, or probe. (list of str)
        mask: What the bot is looking for. (list of str)
        prob_nice: If not retaliating, how like the bot is to cooperate. (float)
        remorse: A flag for regretting random probes. (bool)
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        super(ProbeBot, self).__init__(prob_nice = prob_nice, taken_names = taken_names, initial = initial)
        self.start = start
        self.mask = mask
        self.remorse = remorse and prob_nice < 1

    def get_move(self, foe_name):
        """
        Make a move in the game. (str)

        Parameters:
        foe_name: The name of the player to make a move against.
        """
        responses = len(self.history[foe_name])
        if responses == len(self.start):
            check = [move[0] in target for move, target in zip(self.history[foe_name], self.mask)]
            if not all(check):
                self.tats = 1
                self.prob_nice = 1
        if len(self.start) <= responses:
            move = super(ProbeBot, self).get_move(foe_name)
            if self.remorse:
                mine_two_back = self.history['Me vs. {}'.format(foe_name)][-2][0]
                his_last = self.history[foe_name][-1][0] if self.history[foe_name] else 'x'
                if mine_two_back == 'd' and his_last == 'd':
                    move = 'cooperate'
                    self.current_tits = ['cooperate']
        else:
            move = self.start[responses]
        return move


class PrisonerMethodBot(PrisonerBot):
    """
    An IPD Bot based on overriding methods. (PrisonerBot)

    The base bot for this class is the Grim bot, which retaliates forever after any
    defection.

    If tits and tats can be methods, you can accomodate a lot of strategies. So one
    that is integer based, and one that is method based with subclasses

    Methods:
    get_move: Make a move in the game. (str)
    tat: Decide whether or not to retailiate. (bool)
    tit: Decide how to retailiate. (str)

    Overridden Methods:
    ask
    set_up
    tell
    """

    def __init__(self, prob_nice = 1, taken_names = [], initial = ''):
        """
        Set up the strategy for the bot.

        Parameters:
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        tits: How many times the bot retaliates. (int)
        tats: How many defects it takes for the bot to retaliate. (int)
        prob_nice: If not retaliating, how like the bot is to cooperate. (float)
        """
        super(PrisonerMethodBot, self).__init__(taken_names, initial)
        self.prob_nice = prob_nice

    def get_move(self, foe_name):
        """
        Make a move in the game. (str)

        Parameters:
        foe_name: The name of the player to make a move against.
        """
        if self.tat(foe_name):
            return self.tit()
        elif random.random() < self.prob_nice:
            return 'cooperate'
        else:
            return 'defect'

    def tat(self, foe_name):
        """Decide whether or not to retailiate. (bool)"""
        return 'defect' in self.history[foe_name]

    def tit(self):
        """Decide how to retailiate. (str)"""
        return 'defect'


class FirmButFairBot(PrisonerMethodBot):
    """
    Retaliate after sucker bet. (PrisonerMethodBot)

    Overridden Methods:
    tat
    """

    def tat(self, foe_name):
        """Decide whether or not to retailiate. (bool)"""
        last_move = [self.history['Me vs. {}'.format(foe_name)][-1], self.history[foe_name][-1]]
        return last_move == ['cooperate', 'defect']


class GradualBot(PrisonerMethodBot):
    """
    Retailiate n times after the nth retailiation. (PrisonerMethodBot)

    It follows retaliation with two cooperates to cool things down.

    Overridden Methods:
    set_up
    tat
    tit
    """

    def set_up(self):
        """Set up the bot for play. (None)"""
        super(GradualBot, self).set_up()
        self.retaliations = 0
        self.tits = []

    def tat(self, foe_name):
        """Decide whether or not to retailiate. (bool)"""
        retaliate = self.history[foe_name] and self.history[foe_name][-1] == 'defect'
        if retaliate and not self.tits:
            self.retaliations += 1
            self.tits = ['c', 'c'] + ['d'] * self.retaliations
        return retaliate or self.tits

    def tit(self):
        """Decide how to retailiate. (str)"""
        return self.tits.pop()


class PavlovBot(PrisonerMethodBot):
    """
    Repeats the last choice unless he got a bad result (PrisonerMethodBot)

    Overridden Methods:
    tat
    tit
    """

    def tat(self, foe_name):
        """Decide whether or not to retailiate. (bool)"""
        try:
            # Switch the move on a bad result.
            last_move = (self.history['Me vs. {}'.format(foe_name)][-1], self.history[foe_name][-1])
            if last_move in (('cooperate', 'defect'), ('defect', 'defect')):
                self.next_move = 'cooperate' if self.next_move == 'defect' else 'defect'
        except IndexError:
            # Cooperate initially
            self.next_move = 'cooperate'
        # Always use "retaliate" to get the next move.
        return True

    def tit(self):
        """Decide how to retailiate. (str)"""
        return self.next_move


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

    aka = ['prdi']
    bot_classes = {'num-bot': PrisonerNumBot, 'meth-bot': PrisonerMethodBot, 'firm': FirmButFairBot,
        'gradual': GradualBot, 'majority': MajorityBot, 'pavlov': PavlovBot, 'probe': ProbeBot}
    categories = ['Other Games', 'Theoretical Games']
    credits = CREDITS
    move_aliases = {'c': 'cooperate', 'd': 'defect'}
    name = "Prisoner's Dilemma"
    num_options = 4
    rules = RULES

    def do_gipf(self, arguments):
        """
        The Dollar Game lets you defect, but your opponent thinks you cooperated.
        """
        game, losses = self.gipf_check(arguments, ('the dollar game', 'hangman'))
        # The Dollar Game lets you defect but seem to cooperate
        if game == 'the dollar game':
            if not losses:
                self.human.tell('\nYour next move can be a defect your opponent thinks is cooperation.\n')
                self.hypno = True
        elif game == 'hangman':
            if not losses:
                self.human.tell('\nYou get the temptation score next round no matter what you do.\n')
                self.temp_bonus = True
        # Otherwise I'm confused.
        else:
            self.human.tell("\nDude, Gipf got parole last year. I'm Gorf.")
        return True

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
        # Handle default bots (three at random).
        if len(self.players) == 1:
            # Get the possible bots.
            bots = []
            for option in self.option_set.definitions:
                if option['action'] == 'bot':
                    bots.append((self.bot_classes[option['target']], option['value']))
            # Get three at random.
            bots = random.sample(bots, 3)
            # Add them to the players.
            taken_names = [self.human.name]
            for bot_class, params in bots:
                if params is True:  # That is, there were no parameters given
                    params = []
                elif not isinstance(params, (list, tuple)):
                    params = [params]
                self.players.append(bot_class(*params, taken_names = taken_names))
                taken_names.append(self.players[-1].name)
        # Check that the scores are valid.
        if self.points['sucker'] >= self.points['punishment']:
            self.human.tell('The sucker bet must be less than the punishement.')
            self.option_set.errors.append('Sucker bet too high.')
        if self.points['punishment'] >= self.points['reward']:
            self.human.tell('The punishment must be less than the reward.')
            self.option_set.errors.append('Punishment too high.')
        if self.points['reward'] >= self.points['temptation']:
            self.human.tell('The reward must be less than the temptation.')
            self.option_set.errors.append('Reward too high.')

    def player_action(self, player):
        """
        Run one round of the player's dilemma. (None)

        This doesn't run one player's action, it runs one iteration of the Iterated
        Prisoner's Dilemma. That is, it does the Prisoner's Dilemma for every pair of
        players.
        """
        self.human.tell('')
        # Check each pair of players.
        for sub_players in itertools.combinations(self.players, 2):
            # Get the moves
            moves = []
            queries = ['What is your move against {}? '.format(player.name) for player in sub_players]
            queries.reverse()
            for player, query in zip(sub_players, queries):
                while True:
                    move = player.ask(query)
                    move = self.move_aliases.get(move.lower(), move)
                    if move in ('cooperate', 'defect'):
                        break
                    else:
                        self.handle_cmd(move)
                moves.append(move)
            # Get the scoring results.
            if moves == ['cooperate', 'cooperate']:
                round_scores = [self.points['reward'], self.points['reward']]
            elif moves == ['cooperate', 'defect']:
                round_scores = [self.points['sucker'], self.points['temptation']]
            elif moves == ['defect', 'cooperate']:
                round_scores = [self.points['temptation'], self.points['sucker']]
            elif moves == ['defect', 'defect']:
                round_scores = [self.points['punishment'], self.points['punishment']]
            # Score the points and inform the players
            for player, round_score in zip(sub_players, round_scores):
                if self.temp_bonus and player == self.human:
                    self.scores[player.name] += self.points['temptation']
                else:
                    self.scores[player.name] += round_score
                foe_index = 1 - sub_players.index(player)
                foe_name = sub_players[foe_index].name
                if self.hypno and foe_name == self.human.name:
                    foe_move = 'cooperate'
                    self.hypno = False
                else:
                    foe_move = moves[foe_index]
                player.tell('{} chose to {}.'.format(foe_name, foe_move))
        return False

    def set_options(self):
        """Set the possible game options. (None)"""
        # Set the bot options.
        self.option_set.add_option('all-co', ['ac'], action = 'bot', target = 'num-bot',
            value = ([], 0, 1), default = None)
        self.option_set.add_option('all-def', ['ad'], action = 'bot', target = 'num-bot',
            value = ([], 0, 0), default = None)
        self.option_set.add_option('gradual', ['gl'], action = 'bot', target = 'gradual', default = None)
        self.option_set.add_option('grim', ['gm'], action = 'bot', target = 'meth-bot', default = None)
        self.option_set.add_option('hard-majr', ['hm'], action = 'bot', target = 'majority',
            value = ('defect', 'defect'), default = None)
        self.option_set.add_option('naive-probe', ['np'], action = 'bot', target = 'num-bot',
            value = (['d'], 1, 0.90), default = None)
        self.option_set.add_option('pavlov', ['pv'], action = 'bot', target = 'pavlov', default = None)
        self.option_set.add_option('prober', ['pb'], action = 'bot', target = 'probe',
            value = True, default = None)
        self.option_set.add_option('prober-2', ['p2'], action = 'bot', target = 'probe',
            value = (['d', 'c', 'c'], ['dc', 'd', 'c'], 1), default = None)
        self.option_set.add_option('prober-3', ['p3'], action = 'bot', target = 'probe',
            value = (['d', 'c'], ['dc', 'c']), default = None)
        self.option_set.add_option('random', ['rd'], action = 'bot', target = 'num-bot', default = None)
        self.option_set.add_option('soft-grudge', ['sg'], action = 'bot', target = 'num-bot',
            value = (['c', 'c', 'd', 'd', 'd', 'd'], 1, 1), default = None)
        self.option_set.add_option('soft-majr', ['sm'], action = 'bot', target = 'majority', default = None)
        self.option_set.add_option('tit-tat', ['tt'], action = 'bot', target = 'num-bot',
            value = (['d'], 1, 1), default = None)
        self.option_set.add_option('tit-2tat', ['t2'], action = 'bot', target = 'num-bot',
            value = (['d'], 2, 1), default = None)
        self.option_set.add_option('2tit-tat', ['2t'], action = 'bot', target = 'num-bot',
            value = (['d', 'd'], 1, 1), default = None)
        # Set the score options.
        self.points = {}
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
        # Set the turn options
        self.option_set.add_option('num-turns', ['nt'], int, default = 10,
            question = 'How many turns should be played (return for 10)? ')

    def set_up(self):
        """Set up the game. (None)"""
        self.hypno = False
        self.temp_bonus = False