"""
global_thermonuclear_war_game.py

A game inspired by Global Thermonuclear War in the movie War Games.

!! Assume a 10% starvation rate for every 100 bombs detonated.

PLEASE LIST PRIMARY TARGETS:

Classes:
GlobalThermonuclearWar: A game of thermonuclear armageddon. (game.Game)
"""


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

    # Number of missiles, paranoia factor, defense effectiveness, defensive missiles
    powers = {'United States': (1600, 800, .8, 100), 'Russia': (1600, 800, .85, 95),
        'United Kingdom': (120, 700, 9, 0), 'France': (280, 600, 0, 0),
        'China': (140, 900, .8, 25), 'India': (70, 500, .7, 15), 'Pakistan': (70, 400, 0, 0),
        'North Korea': (7, 1, 0, 0), 'Israel': (40, 900, .75, 10)}

    # !! make sure these names associate with the city data.
    allies = {'United States': ['United Kingdom', 'Ireland', 'Germany', 'Spain', 'Portugal', 'Saudi Arabia',
        'Mexico', 'Canada', 'Australia', 'Japan', 'Thailand', 'Israel', 'Jordan', 'Egypt', 'Kenya',
        'Columbia', 'Pakistan', 'South Korea', 'Turkey', 'Greece', 'Estonia', 'Latvia', 'Lithuania',
        'Poland', 'Czech Republic', 'Ukraine' 'Libya', 'Taiwan'],
        'Russia': ['India', 'Syria', 'Brazil', 'Venezuela', 'Cuba', 'Italy', 'Germany', 'Azerbaijan',
        'Belarus', 'Kazakhstan', 'Kyrgyzstan', 'Armenia', 'Moldova', 'Tajikstan', 'Uzbekistan',
        'Turkmenistan', 'China', 'Indonesia', 'Iran', 'Botswana', 'Mozambique', 'Namibia', 'Sudan',
        'Zimbabwe', 'Bolivia', 'Grenada', 'Uruguay', 'Armenia', 'Indonesia', 'Lebanon', 'Mongolia',
        'Myanmar', 'North Korea', 'Sri Lanka'],
        'United Kingdom': ['United States', 'Ireland', 'Canada', 'Australia', 'Chile', 'Columbia', 'Panama',
        'Brunei', 'Israel', 'Japan', 'Kazakhstan', 'Oman', 'South Korea', 'Turkey', 'Finland', 'Poland',
        'Germany', 'New Zealand', 'Nigeria', 'Barbados', 'Estonia', 'Latvia', 'Lithuania', 'Libya', 'India']
        'France': ['Turkey', 'Libya', 'Egypt', 'Germany', 'Democratic Republic of the Congo', 'Chad',
        'Niger', 'Brazil', 'Canada', 'India', 'Indonesia', 'Japan', 'South Korea', 'Qatar',
        'Bosnia and Herzegovina', 'Greece', 'Ireland', 'Latvia'],
        'China': ['Russia', 'Myanmar', 'North Korea', 'Pakistan', 'France', 'Italy', 'Algeria', 'Sudan',
        'Zaire', 'Nigeria', 'Egypt', 'Zimbabwe', 'Venezuela', 'Barbados', 'Cuba', 'Australia', 'Samoa'],
        'India': ['Russia', 'Israel', 'Afganistan', 'France', 'Bhutan', 'Bangladesh', 'South Africa',
        'Brazil', 'Mexico', 'Japan', 'Germany', 'Indonesia', 'Brazil', 'Mongolia', 'Singapore', 'UAE',
        'Ghana', 'Kenya', 'Lesotho', 'Mauritius', 'Morocco', 'Namibia', 'Nigeria', 'South Africa'],
        'Pakistan': ['United States', 'Turkey', 'United Kingdom', 'China', 'Indonesia', 'Algeria',
        'Tunisia', 'Morocco', 'Eritrea', 'Saudi Arabia', 'France'],
        'North Korea': ['China', 'Russia'],
        'Israel': []}

    enemies = {'United States': ['Russia', 'Cuba', 'China', 'Venezuela', 'Iran', 'Syria', 'Moldova',
        'Grenada', 'Lebanon', 'Myanmar', 'North Korea'],
        'Russia': ['Turkey', 'Ukraine', 'United States', 'Afganistan', 'Estonia', 'Latvia', 'Lithuania',
        'Georgia', 'Poland', 'Czech Republic', 'Japan' 'Libya', 'Pakistan', 'Chad'],
        'United Kingdom': ['Russia', 'Argentina', 'Iran'],
        'France': ['Madagascar', 'Comoros', 'Mauritius', 'China', 'North Korea'],
        'China': ['Taiwan', 'United Kingdom', 'Turkey', 'Libya', 'Mongolia', 'France', 'Japan', 'Vietnam',
        'Italy', 'Germany', 'India', 'Poland', 'United States', 'Jordan', 'Bangladesh'],
        'India': ['Pakistan', 'United Kingdom', 'Turkey'],
        'Pakistan': ['India', 'Afganistan', 'Israel'],
        'North Korea': ['South Korea', 'United States', 'Turkey', 'Portugal', 'Iraq', 'Chile', 'Argentina'],
        'Israel': ['Turkey', 'Algeria', 'Bahrain', 'Comoros', 'Djibouti', 'Iraq', 'Kuwait', 'Lebanon',
        'Libya', 'Morocco', 'Qatar', 'Saudi Arabia', 'Somalia', 'Sudan', 'Syrian', 'Tunisia', 'UAE',
        'Yemen', 'Afganistan', 'Bangladesh', 'Brunei', 'Indonesia', 'Iran', 'Malaysia', 'Mali', 'Niger',
        'Pakistan']}

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Check for Chess win.
        if self.force_end:
            return False

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.add_option('united-states', ['us'])
        self.option_set.add_option('russia', ['r'])

    def set_up(self):
        """Set up the game. (None)"""
        # Try to play chess instead.
        if self.human.ask("WOULDN'T YOU PREFER A GOOD GAME OF CHESS?") in utility.YES:
            results = self.interface.games['chess'].play('')
            self.win_loss_draw = [1, 0, 0]
            self.scores[self.human.name] = results[3]
            self.force_end = 'chess'
        # Load the city data.
        self.cities = {}
        with open('city_data.csv') as city_data:
            city_data.readline()
            for line in city_data:
                fields = line.split(',')
                self.city_data[fields[0].lower()] = {'name': fields[0], 'latitude': float(fields[1]),
                    'longitude': float(fields[2]), 'country': fields[3], 'capital': fields[4],
                    'population': int(fields[5])}
        # Load the country data.
        self.countries = {}
        with open('country_data.csv') as country_data:
            country_data.readline()
            for line in country_data:
                fields = line.split(',')
                # !! Need parsing here.
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

    def __init__(self, country, arsenal, paranoia, defense_rate, defense_missiles):
        """
        Set up the bot. (None)

        Parameters:
        country: The name of the country. (str)
        arsenal: The number of nuclear missiles available. (int)
        paranoia: The number of missiles fired that will induce paranoia. (int)
        defense_rate: The quality of the nation's missile defenses. (float)
        defense_missiles: The number of defensive missings available. (int)
        """
        # Base bot initialization.
        super(NationBot, self).__init__()
        # Initialize specified attributes.
        self.name = country
        self.arsenal = arsenal
        self.paranoia = paranoia
        self.defense_rate = defense_rate
        self.defense_missiles = defense_missiles
        # Initialize derived attributes.
        self.arsenal_left = arsenal
        # Initialize default attributes.
        self.output_mode = ''
        self.strategy = 'peace'
        self.aggressor = ''
        self.primary_targets = []
        self.secondary_targets = []

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

    def get_strategy(self):
        """Set the strategy for the next round of target selection. (None)"""
        if not self.arsenal_left:
            self.strategy = 'peace'
            self.aggressor = ''

    def get_targets(self):
        """Determine who to fire missiles at. (None)"""
        if self.strategy == 'peace':
            self.primary_targets = []
            self.secondary_targets = []

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
