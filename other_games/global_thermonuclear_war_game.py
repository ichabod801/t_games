"""
global_thermonuclear_war_game.py

A game inspired by Global Thermonuclear War in the movie War Games.

!! Assume a 10% starvation rate for every 100 bombs detonated.

!! Assume a 7% failure rate for missiles. (option)

PLEASE LIST PRIMARY TARGETS:

Classes:
GlobalThermonuclearWar: A game of thermonuclear armageddon. (game.Game)
"""


import collections
import itertools
import random

from .. import game
from .. import player
from .. import utility


CHOOSE_SIDE = """
WHICH SIDE DO YOU WANT?

  1.    UNITED STATES
  2.    RUSSIA

PLEASE CHOOSE ONE:  """


def GlobalThermonuclearWar(game.Game):
    """
    A game of thermonuclear armageddon. (game.Game)

    Note that the allies and enemies lists are in no way meant to be realistic.
    This is a silly game that you always lose, and I couldn't find an easy source
    for the data, so I just spent a couple days skimming foreign relations articles
    on Wikipedia. I'm sure it's wrong. I'm not seeing the point in worrying about
    it either. The priority was ensuring an escalation of the conflict. Also, note
    that Israel has no allies listed only so that it will keep all of it's missiles
    until it is attacked directly or it sees the end of the world coming. It's not
    that I think no one likes Israel or Israel hates everybody. And yes, I know
    nuclear winter is a controversial topic. It's a game, dude.

    Overridden Methods:
    set_options
    set_up
    """

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Check for Chess win.
        if self.force_end:
            return False
        # Get the name of the player's country.
        if player == self.human:
            country = self.human_country
        else:
            country = player.name
        # Get the primary targets.
        primaries = []
        player.tell('\nPLEASE LIST PRIMARY TARGETS:')
        while True:
            city = input('')
            if city:
                primaries.append(city)
            else:
                break
        # Get the secondary targets.
        secondaries = []
        player.tell('\nPLEASE LIST SECONDARY TARGETS:')
        while True:
            city = input('')
            if city:
                secondaries.append(city)
            else:
                break
        # Update any currently flying missiles
        # (done here to keep missiles in play sequence so bots can tell what's been fired this round)
        self.update_missiles(country) # !! not written
        # Fire the missiles at the selected targets.
        for missiles, targets in ((5, primaries), (2, secondaries)):
            for target in targets:
                target_country, distance = self.confirm_target(target) # !! not written
                self.missiles_flying.append((country, missiles, target, target_country, distance))
                self.missiles_launched += missiles

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.add_option('united-states', ['us'])
        self.option_set.add_option('russia', ['r'])

    def set_up(self):
        """Set up the game. (None)"""
        # Try to play chess instead.
        if self.human.ask("\nWOULDN'T YOU PREFER A GOOD GAME OF CHESS?") in utility.YES:
            results = self.interface.games['chess'].play('')
            self.win_loss_draw = [1, 0, 0]
            self.scores[self.human.name] = results[3]
            self.force_end = 'chess'
        # Load the country data.
        self.countries = collections.defaultdict(dict)
        self.powers = []
        with open('country_data.csv') as country_data:
            num_countries = int(country_data.readline())
            for country in range(num_countries):
                name = country_data.readline().strip()
                data = {'name': name, cities = []}
                missiles, paranoia, defense, defense_missiles = country_data.readline().split(',')
                data['missiles'] = int(missiles)
                data['paranoia'] = int(paranoia)
                data['defense_rate'] = int(defense)
                data['defense_missiles'] = int(defense_missiles)
                data['allies'] = [country.strip() for country in country_data.readline().split(,)]
                data['enemies'] = [country.strip() for country in country_data.readline().split(,)]
                self.countries[name] = data
                self.powers.append(name)
        # Load the city data.
        self.cities = {}
        with open('city_data.csv') as city_data:
            city_data.readline()
            for line in city_data:
                name, longitude, latitude, country, capital, population = line.split(',')
                self.city_data[name.lower()] = {'name': name, 'latitude': latitude,
                    'longitude': longitude, 'country': country, 'capital': capital,
                    'population': int(population)}
                self.countires[country]['cities'].append(name)
                if capital == 'primary':
                    self.countries[country]['capital'] = name
        # Get the country to play.
        if self.united_states:
            self.human_country = 'United States'
        elif self.russia:
            self.human_country = 'Russia'
        else:
            while True:
                side_num = self.human.input(CHOOSE_SIDE).strip()
                if side_num == '1':
                    self.human_country = 'United States'
                elif side_num == '2':
                    self.human_country = 'Russia'
                else:
                    self.human.tell('PLEASE CHOOSE 1 OR 2.')
                    continue
                break
        # Set up the players.
        self.players = [self.human]
        self.players.extend(NationBot(*data) for data in self.powers if data['name'] != self.human_country)

class NationBot(player.Bot):
    """
    A bot representing one of the nuclear powers. (player.Bot)

    Attributes:
    aggressor: The power being targeted by the current strategy. (str)
    arsenal: The starting number of nuclear missiles available. (int)
    arsenal_left: The current number of nuclear missiles available. (int)
    defense_rate: The quality of the nation's missile defenses. (float)
    defense_missiles: The number of defensive missings available. (int)
    output_mode: The target type currently being provided. (str)
    paranoia: The number of missiles fired that will induce paranoia. (int)
    primary_targets: The current nations to fire five missiles at. (list of str)
    strategy: The strategy recommended by the WOPR computer. (str)
    secondary_targets: The current nations to fire two missiles at. (list of str)

    Methods:
    get_strategy: Set the strategy for the next round of target selection. (None)
    get_targets: Determine who to fire missiles at. (None)

    Overridden Methods:
    __init__
    ask
    tell
    """

    def __init__(self, **kwargs):
        """
        Set up the bot. (None)

        Parameters:
        kwargs: A country profile from self.game.powers. (dict)
        """
        # Base bot initialization.
        super(NationBot, self).__init__()
        # Initialize specified attributes.
        for name, value in kwargs.items():
            setattr(self, name, value)
        # Initialize derived attributes.
        self.arsenal_left = self.arsenal
        # Initialize default attributes.
        self.output_mode = ''
        self.indirect_foes = []
        self.direct_foes = []
        self.primary_targets = []
        self.secondary_targets = []
        self.capital_hits = []
        self.largest_hits = []
        self.num_targets = 0

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        if not prompt:
            if self.output_mode == 'primary':
                target_list = self.primary_targets
            elif self.output_mode == 'secondary':
                target_list = self.secondary_targets
            else:
                raise player.BotError('Target request to NationBot with no targets specified.')
            try:
                return target_list.pop()
            except IndexError:
                self.output_mode = ''
                return ''
        else:
            super(NationBot, self).ask(prompt)

    def get_direct(self, foe):
        """
        Get a target country based on a direct attack.

        Parameters:
        foe: The country that attacked you. (str)
        """
        if random.random() > 0.5:
            return foe
        else:
            return self.get_indirect(foe)

    def get_indirect(self, foe):
        """
        Get a target country based on an indirect attack.

        Paramters:
        foe: The country that attacked you. (str)
        """
        their_allies = self.game.countries[foe]['allies']
        targets = [ally for ally in their_allies if ally not in self.allies]
        if targets:
            return random.choice(targets)
        else:
            return foe

    def get_strategy(self):
        """Set the strategy for the next round of target selection. (None)"""
        self.num_targets = 1
        for country, missiles, target, target_country, distance in self.game.missiles_flying:
            if country == self.name:
                continue
            if target_country == self.name and country not in self.direct_foes:
                self.direct_foes.append(country)
            elif target_country in self.allies and country not in self.indirect_foes:
                self.indirect_foes.append(country)
            self.num_targets += 1
        self.indect_foes = [country for country in self.indirect_foes if country not in self.direct_foes]
        if self.game.missiles_launched >= self.paranoia or self.arsenal_left * 2 < self.arsenal:
            self.paranoid = True

    def get_targets(self):
        """Determine who to fire missiles at. (None)"""
        targets = self.direct_foes + self.indect_foes
        if self.paranoid:
            targets += self.enemies
        for foe in itertools.chain(targets):
            if foe in self.indirect_foes:
                target_country = self.get_indirect(foe)
            else:
                target_country = self.get_direct(foe)
            if target_country not in self.capital_hits:
                self.primary_targets.append(self.game.countries[target_country]['capital'])
                self.capital_hits.append(target_country)
            elif target_country not in self.largest_hits:
                self.primary_targets.append(self.game.countries[target_country]['largest'])
                self.largest_hits.append(target_country)
            else:
                self.secondary_targets.append(random.choice(self.game.countries[target_country]['cities']))
            self.num_targets -= 1
            if not self.num_targets:
                break

    def set_up(self):
        """Set up the bot's tracking variables. (None)"""
        self.paranoid = False

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        if args[0] == '\nPLEASE LIST PRIMARY TARGETS:':
            self.set_strategy()
            self.get_targets()
            self.output_mode = 'primary'
        elif args[0] == '\nPLEASE LIST SECONDARY TARGETS:':
            self.output_mode = 'secondary'
