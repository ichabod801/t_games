"""
prisoner_game.py

An implementation of the Iterated Prisoner's Dilemma.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Prisoner's Dilemma.
OPTIONS: The options for Prisoner's Dilemma.
RULES: The rules for Prisoner's Dilemma.

Classes:
PrisonerBot: A bot template for the Iterated Prisoner's Dilemma. (player.Bot)
ChooserBot: Return a random move from the foe's history. (PrisonerBot)
FairButFirmBot: Retaliate after sucker bet. (PrisonerBot)
GradualBot: Retailiate n times after the nth retailiation. (PrisonerBot)
GrimBot: An IPD bot that defects if its foe ever defected. (PrisonerBot)
MajorityBot: A bot that moves based on majority of foe moves. (PrisonerBot)
PavlovBot: Repeats the last choice if he got a bad result (PrisonerBot)
PrisonerNumBot: An IPD bot set on simple parameters. (PrisonerBot)
ProbeBot: An IPD bot that guesses foe's strategy. (PrisonerNumBot)
PrisonersDilemma: A game of the Interated Prisoner's Dilemma. (game.Game)
"""


from __future__ import division

import itertools
import random

from .. import game
from .. import player


CREDITS = """
Game Design: Merrill Flood and Melvin Dresher
Game Programming: Craig "Ichabod" O'Brien
Bot Design: Robert Axelrod, B. Beaufils, S. Braver, R. Boyd, K. Deb, J.
    Delahaye, James Friedman, S. Komorita, David Kraines, Vivian Kraines, J.
    Li, J. P. Lorberbaum, S. Mittal, J. Nachbar, Mathieu Our, Anatol Rapoport,
    J. Sheposh, R. Sugden
"""

OPTIONS = """
num-extra= (ne=): The maximum number of extra random rounds played (defaults
    to 3)
num-turns= (nt=): The number of rounds played (defaults to 10).
punishment= (p=): The punishment score. It must be higher than the sucker bet.
reward= (r=): The reward score. It must be higher than the punishment score.
sucker= (s=): The sucker bet score. It must be lower than the punishment score.
temptation= (t=): The temptation score. It must be higher than the reward
    score.
gonzo (gz): Equivalent to 'iterations=12 hard-majr grim pavlov prober random
    soft-majr tit-tat tit-2tat 2tit-tat'.

Bot Options:
adapt (ap): Tests some cooperates and defects, then plays whatever is scoring
    the best.
all-co (ac): Add an Always Cooperate bot.
all-def (ad): Add an Always Defect bot.
chooser (ch): Returns a random move from its foe's list of moves.
generous-tft (gt): Tit for Tat, but 9 out ot 10 times cooperates instead of
    defecting.
gradual (gl): Tit for Tat, but n tits for nth tat, with cool down.
grim (gm): Retaliates forever after a single defect.
hard-majr (hm): Defects on a majority of defects, otherwise cooperates.
hard-tft (ht): Tit for Tat, but retaliates for any defect in the last three
    moves.
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
reverse-tft (rt): Tit for Tat, but defects first, then does opposite of foe's
    last move.
soft-grudge (sg): Retailiates four times, followed by two cooperations.
soft-majr (sm): Cooperates on a majority of cooperations, otherwise defects.
suspicious-tft (st): Tit for Tat, but defects on the first move.
tit-tat (tt): Add a Tit for Tat bot.
tit-2tat (t2): Add a Tit for Two Tats bot.
2tit-tat (2t): Add a Two Tits for Tat bot.

The default bots are three chosen at random.
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
"""


class PrisonerBot(player.Bot):
    """
    A bot template for the Iterated Prisoner's Dilemma. (player.Bot)

    The foe_data dictionary has the following keys:
        * name: The name of the player. (str)
        * me: A history of the moves made against the foe. (list of str)
        * them: A corresponding history of moves made by the foe. (list of str)

    Bots may add keys to the foe_data dictionary, and that information will
    be tracked for that foe. The data dictionary is all of the foe_data
    dictionaries keyed by player.

    Attributes:
    data: Data on the opponents the bot is playing against. (dict)
    foe_data: Data on the opponent is currently making a move against. (dict)

    Methods:
    get_move: Make a move in the game. (str)
    last_me: Return the last move by this bot. (str)
    last_pair: Return the last moves by this bot and the current foe. (str)
    last_them: Return the last move by the current foe. (str)

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
            self.foe_data = self.data[foe_name]
            move = self.get_move()
            self.foe_data['me'].append(move)
            return move
        else:
            player.BotError('Unexpected move asked of {}: {!r}'.format(self.__class__.__name__, query))

    def get_move(self):
        """Make a move in the game. (str)"""
        return random.choice(('cooperate', 'defect'))

    def last_me(self):
        """Return the last move by this bot. (str)"""
        try:
            return self.foe_data['me'][-1]
        except IndexError:
            return ''

    def last_pair(self):
        """Return the last moves by this bot and the current foe. (str)"""
        return self.last_me(), self.last_them()

    def last_them(self):
        """Return the last move by the current foe. (str)"""
        try:
            return self.foe_data['them'][-1]
        except IndexError:
            return ''

    def set_up(self):
        """Set up the bot."""
        self.data = {player: {'me': [], 'them': [], 'name': player.name} for player in self.game.players}
        del self.data[self]

    def tell(self, *args, **kwargs):
        """Give the player some information. (None)"""
        if 'chose to' in args[0]:
            middle = args[0].index(' chose to ')
            foe_name = args[0][:middle]
            if 'cooperate' in args[0]:
                self.data[foe_name]['them'].append('cooperate')
            else:
                self.data[foe_name]['them'].append('defect')


class AdaptiveBot(PrisonerBot):
    """
    Keep track of the score, and play what's working best. (PrisonerBot)

    The AdaptiveBot adds two keys to the foe_data dictionary:
        * c_scores: The scores achieved with cooperate (list of int)
        * d_scores: The scores achieved with defect (list of int)

    Overridden Methods:
    get_move
    set_up
    """

    def get_move(self):
        """Make a move in the game. (str)"""
        # Score the last move. !! refactor this for all bots, and make it a dict call.
        moves = len(self.foe_data['them'])
        if moves:
            me, them = self.last_pair()
            c_scores = self.foe_data['c_scores']
            d_scores = self.foe_data['d_scores']
            if me == 'cooperate':
                if them == 'cooperate':
                    c_scores.append(self.game.points['reward'])
                else:
                    c_scores.append(self.game.points['sucker'])
            else:
                if them == 'cooperate':
                    d_scores.append(self.game.points['temptation'])
                else:
                    d_scores.append(self.game.points['punishment'])
        # Determine the current move.
        if moves < len(self.start):
            return self.start[moves]
        elif sum(c_scores) / len(c_scores) > sum(d_scores) / len(d_scores):
            return 'cooperate'
        else:
            return 'defect'

    def set_up(self):
        """Set up the bot."""
        super(AdaptiveBot, self).set_up()
        test_len = min(max(self.game.num_turns // 20, 1), 5)
        self.start = ['cooperate'] * test_len + ['defect'] * test_len
        for data in self.data.values():
            data['c_scores'] = []
            data['d_scores'] = []


class ChooserBot(PrisonerBot):
    """
    Return a random move from the foe's history. (PrisonerBot)

    Overridden Methods:
    get_move
    """

    def get_move(self):
        """Make a move in the game. (str)"""
        try:
            return random.choice(self.foe_data['them'])
        except IndexError:
            return random.choice(('cooperate', 'defect'))


class FirmButFairBot(PrisonerBot):
    """
    Retaliate after sucker bet. (PrisonerBot)

    Overridden Methods:
    get_move
    """

    def get_move(self, foe_name):
        """Make a move in the game. (str)"""
        if self.last_pair() == ('cooperate', 'defect'):
            return 'defect'
        else:
            return 'cooperate'


class GrimBot(PrisonerBot):
    """
    An IPD bot that defects if its foe ever defected. (PrisonerBot)

    The GrimBot adds the grim key to the foe_data, a boolean.

    Overridden Methods:
    """

    def get_move(self):
        """Get the next move. (str)"""
        self.foe_data['grim'] = self.foe_data['grim'] or self.last_them() == 'defect'
        if self.foe_data['grim']:
            return 'defect'
        else:
            return 'cooperate'

    def set_up(self):
        """Set up the bot. (None)"""
        super(GrimBot, self).set_up()
        for player in self.game.players:
            if player != self:
                self.data[player]['grim'] = False


class GradualBot(PrisonerBot):
    """
    Retailiate n times after the nth retailiation. (PrisonerBot)

    It follows retaliation with two cooperates to cool things down.

    Overridden Methods:
    get_move
    set_up
    """

    def get_move(self):
        """Make a move in the game. (str)"""
        if self.foe_data['tits']:
            return self.foe_data['tits'].pop()
        elif self.last_them() == 'defect':
            self.foe_data['retaliations'] += 1
            self.foe_data['tits'] = ['cooperate', 'cooperate'] + ['defect'] * self.foe_data['retaliations']
            return self.foe_data['tits'].pop()
        else:
            return 'cooperate'

    def set_up(self):
        """Set up the bot for play. (None)"""
        super(GradualBot, self).set_up()
        for player in self.game.players:
            if player != self:
                self.data[player].update({'retaliations': 0, 'tits': []})


class MajorityBot(PrisonerBot):
    """
    An IPD bot that decides based on majoryities of foe moves. (PrisonerBot)

    Attributes:
    majority: The majority to check for. (str)
    move: The move to make on a majority. (str)
    other: The move to make on a minority. (str)

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

    def get_move(self):
        """Make a move in the game. (str)"""
        count = self.foe_data['them'].count(self.majority)
        other_count = len(self.foe_data['them']) - count
        if count >= other_count:
            return self.move
        else:
            return self.other


class PavlovBot(PrisonerBot):
    """
    Repeats the last choice unless he got a bad result (PrisonerBot)

    Overridden Methods:
    tat
    tit
    """

    def get_move(self):
        """Get a move for the bot. (str)"""
        last_pair = self.last_pair()
        if last_pair in (('cooperate', 'defect'), ('defect', 'defect')):
            return 'cooperate' if last_pair[0] == 'defect' else 'defect'
        elif last_pair[0]:
            return last_pair[0]
        else:
            return 'cooperate'


class PrisonerNumBot(PrisonerBot):
    """
    An IPD bot set on simple parameters. (PrisonerBot)

    Here's how the bot works. With probability {start_nice}, it opens with
    cooperation. Each turn after that, it checks back {view} enemy moves. If it
    finds at least {tats} defections, it defects {tits} times and then cooperates
    {cool} times (with probability {prob_mean}, otherwise it cooperates). If it
    does not find enough defects, it cooperates with probability {prob_nice},
    otherwise it defects. The default settings give a standard tit-for-tat bot.

    PrisonerNumBot adds the following keys to foe_data:
        * current_tits: The queued responses for the given bot. (list of str)
        * cool: How long the cool down period is. (int)
        * prob_nice: If not retaliating, how nice to be. (float)
        * prob_mean: If retaliating, how mean to be. (float)
        * tats: How many defects it takes for the bot to retaliate. (int)
        * tits: How many times the bot retaliates. (list of str)
        * view: How far back to check for tats. (int)

    While only currrent_tits is needed for the base class, they are all stored per
    foe so that they can be adjusted individually by child classes. The actual
    decisions are made in the be_mean, be_nice, and start methods, also to assist
    sub-classing.

    Attributes
    cool: How long the cool down period is. (int)
    prob_mean: If retaliating, how likely the bot is to defect. (float)
    prob_nice: If not retaliating, how likely the bot is to cooperate. (float)
    start_nice: The probability of the first move being cooperate. (float)
    tats: How many defects it takes for the bot to retaliate. (int)
    tits: How the bot retaliates. (list of str)
    view: How far back to check for tats. (int)

    Methods:
    be_mean: Generate a retaliatory move. (str)
    be_nice: Generate a 'nice' move. (str)
    start: Make the first move of the game. (str)

    Overridden Methods:
    __init__
    __repr__
    get_move
    set_up
    """

    def __init__(self, tits = 1, cool = 0, tats = 1, view = 1, prob_nice = 1, prob_mean = 1,
        start_nice = 1, taken_names = [], initial = ''):
        """
        Set up the strategy for the bot. (None)

        Parameters:
        tits: How many times the bot retaliates. (int)
        cool: How long the cool down period is. (int)
        tats: How many defects it takes for the bot to retaliate. (int)
        view: How far back to check for tats. (int)
        prob_nice: If not retaliating, how likely the bot is to cooperate. (float)
        prob_mean: If retaliating, how likely the bot is to defect. (float)
        start_nice: The probability of the first move being cooperate. (float)
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        super(PrisonerNumBot, self).__init__(taken_names, initial)
        self.tits = tits
        self.cool = cool
        self.tats = tats
        self.view = view
        self.prob_nice = prob_nice
        self.prob_mean = prob_mean
        self.start_nice = start_nice

    def __repr__(self):
        """Generate a debugging text representation. (str)"""
        fields = (self.__class__.__name__, self.name, self.tits, self.cool, self.tats, self.view,
            self.prob_nice, self.prob_mean, self.start_nice)
        return '<{} {} {} {} {} {} {:.2f} {:.2f} {:.2f}>'.format(*fields)

    def be_mean(self):
        """Generate a retaliatory move. (str)"""
        if random.random() < self.foe_data['prob_mean']:
            self.foe_data['current_tits'] = ['cooperate'] * self.foe_data['cool']
            self.foe_data['current_tits'] += ['defect'] * self.foe_data['tits']
            if self.foe_data['current_tits']:
                return self.foe_data['current_tits'].pop()
            else:
                return 'defect'
        else:
            return 'cooperate'

    def be_nice(self):
        """Generate a 'nice' move. (str)"""
        return 'cooperate' if random.random() < self.foe_data['prob_nice'] else 'defect'

    def get_move(self):
        """Make a move in the game. (str)"""
        current_tits = self.foe_data['current_tits']
        tats = self.foe_data['tats']
        if current_tits:
            return current_tits.pop()
        elif not self.foe_data['them']:
            return self.start()
        elif self.foe_data['them'][-self.foe_data['view']:].count('defect') >= tats:
            return self.be_mean()
        else:
            return self.be_nice()

    def set_up(self):
        """Set up the bot. (None)"""
        super(PrisonerNumBot, self).set_up()
        for player in self.game.players:
            if player != self:
                self.data[player].update({'current_tits': [], 'tats': self.tats, 'tits': self.tits})
                self.data[player].update({'cool': self.cool, 'view': self.view})
                self.data[player].update({'prob_mean': self.prob_mean, 'prob_nice': self.prob_nice})
                self.data[player]['start_nice'] = self.start_nice

    def start(self):
        """Make the first move of the game. (str)"""
        return 'cooperate' if random.random() < self.foe_data['start_nice'] else 'defect'


class ProbeBot(PrisonerNumBot):
    """
    An IPD bot that guesses foe's strategy. (PrisonerNumBot)

    Attributes:
    mask: What the bot is looking for. (list of str)
    remorse: A flag for regretting defects. (bool)
    start: The bot's initial plays, or probe. (list of str)

    Overridden Methods:
    __init__
    get_move
    """

    def __init__(self, start = ['d', 'c', 'c'], mask = ['dc', 'c', 'c'], prob_mean = 1, remorse = False,
        taken_names = [], initial = ''):
        """
        Set up the strategy for the bot. (None)

        Parameters:
        start: The bot's initial plays, or probe. (list of str)
        mask: What the bot is looking for. (list of str)
        prob_mean: If the mask matches, how likely the bot is to defect. (float)
        remorse: A flag for regretting defects. (bool)
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        super(ProbeBot, self).__init__(tats = 0, prob_mean = prob_mean, taken_names = taken_names,
            initial = initial)
        self.start = start
        self.mask = mask
        self.remorse = remorse and prob_mean > 0

    def get_move(self):
        """Make a move in the game. (str)"""
        responses = len(self.foe_data['them'])
        # Switch to TFT if the enemy moves match the mask.
        if responses == len(self.start):
            check = [move[0] in target for move, target in zip(self.foe_data['them'], self.mask)]
            if not all(check):
                self.foe_data['tats'] = 1
                self.foe_data['prob_mean'] = 1
        # Respond to the current move.
        if responses < len(self.start):
            move = self.start[responses]
        else:
            move = super(ProbeBot, self).get_move()
            if self.remorse:
                mine_two_back = self.foe_data['me'][-2][0]
                their_last = self.foe_data['them'][-1][0] if self.foe_data['them'] else 'x'
                if mine_two_back == 'd' and their_last == 'd':
                    move = 'cooperate'
                    self.foe_data['current_tits'] = ['cooperate']
        return move


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
    bot_classes = {'num-bot': PrisonerNumBot, 'firm': FirmButFairBot, 'gradual': GradualBot,
        'grim': GrimBot, 'majority': MajorityBot, 'pavlov': PavlovBot, 'probe': ProbeBot,
        'adapt': AdaptiveBot, 'base': PrisonerBot, 'chooser': ChooserBot}
    categories = ['Other Games', 'Theoretical Games']
    credits = CREDITS
    move_aliases = {'c': 'cooperate', 'd': 'defect'}
    name = "Prisoner's Dilemma"
    num_options = 7
    options = OPTIONS
    rules = RULES

    def do_gipf(self, arguments):
        """
        The Dollar Game lets you defect, but your opponent thinks you cooperated.

        Hangman gives you the temptation score no matter what you do.
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
        if self.turns == self.total_turns:
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
                        self.current_player = player
                        self.player_index = self.players.index(player)
                        self.handle_cmd(move)
                        if self.force_end:
                            return False
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
                    self.temp_bonus = False
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
        self.option_set.add_option('adapt', ['dp'], action = 'bot', target = 'adapt', default = None)
        self.option_set.add_option('all-co', ['ac'], action = 'bot', target = 'num-bot',
            value = (0, 0, 0, 1, 1, 0, 1), default = None)
        self.option_set.add_option('all-def', ['ad'], action = 'bot', target = 'num-bot',
            value = (1, 0, 0, 1, 0, 1, 0), default = None)
        self.option_set.add_option('chooser', ['ch'], action = 'bot', target = 'chooser', default = None)
        self.option_set.add_option('gradual', ['gl'], action = 'bot', target = 'gradual', default = None)
        self.option_set.add_option('grim', ['gm'], action = 'bot', target = 'grim', default = None)
        self.option_set.add_option('hard-majr', ['hm'], action = 'bot', target = 'majority',
            value = ('defect', 'defect'), default = None)
        self.option_set.add_option('naive-probe', ['np'], action = 'bot', target = 'num-bot',
            value = (1, 0, 1, 1, 0.90), default = None)
        self.option_set.add_option('pavlov', ['pv'], action = 'bot', target = 'pavlov', default = None)
        self.option_set.add_option('prober', ['pb'], action = 'bot', target = 'probe',
            value = True, default = None)
        self.option_set.add_option('prober-2', ['p2'], action = 'bot', target = 'probe',
            value = (['d', 'c', 'c'], ['dc', 'd', 'c'], 0), default = None)
        self.option_set.add_option('prober-3', ['p3'], action = 'bot', target = 'probe',
            value = (['d', 'c'], ['dc', 'c']), default = None)
        self.option_set.add_option('random', ['rd'], action = 'bot', target = 'base', default = None)
        self.option_set.add_option('soft-grudge', ['sg'], action = 'bot', target = 'num-bot',
            value = (4, 2), default = None)
        self.option_set.add_option('soft-majr', ['sm'], action = 'bot', target = 'majority', default = None)
        self.option_set.add_option('tit-tat', ['tt'], action = 'bot', target = 'num-bot', default = None)
        self.option_set.add_option('tit-2tat', ['t2'], action = 'bot', target = 'num-bot',
            value = (1, 0, 2, 2), default = None)
        self.option_set.add_option('2tit-tat', ['2t'], action = 'bot', target = 'num-bot',
            value = (2, 0, 1, 1), default = None)
        self.option_set.add_option('generous-tft', ['gt'], action = 'bot', target = 'num-bot',
            value = (1, 0, 1, 1, 1, 0.9), default = None)
        self.option_set.add_option('suspicious-tft', ['st'], action = 'bot', target = 'num-bot',
            value = (1, 0, 1, 1, 1, 1, 0), default = None)
        self.option_set.add_option('hard-tft', ['ht'], action = 'bot', target = 'num-bot',
            value = (1, 0, 1, 3), default = None)
        self.option_set.add_option('reverse-tft', ['rt'], action = 'bot', target = 'num-bot',
            value = (1, 0, 1, 1, 0, 0, 0), default = None)
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
        self.option_set.add_option('num-extra', ['ne'], int, default = 3,
            question = 'What should be the maximum number of random extra rounds (return for 3)? ')
        # Set the option groups.
        gonzo = 'num-turns=12 hard-majr grim pavlov prober random soft-majr tit-tat tit-2tat 2tit-tat'
        self.option_set.add_group('gonzo', ['gz'], gonzo)

    def set_up(self):
        """Set up the game. (None)"""
        self.hypno = False
        self.temp_bonus = False
        self.total_turns = self.num_turns + random.randint(0, self.num_extra)
        random.shuffle(self.players)
