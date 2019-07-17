"""
global_thermonuclear_war_game.py

A game inspired by Global Thermonuclear War in the movie War Games.

Classes:
GlobalThermonuclearWar: A game of thermonuclear armageddon. (game.Game)
"""


from .. import game
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
    that I think no one likes Israel or Israel hates everybody.

    Overridden Methods:
    set_options
    set_up
    """

    # Number of missiles, paranoia factor
    powers = {'United States': (1600, 800), 'Russia': (1600, 800), 'United Kingdom': (120, 700),
        'France': (280, 600), 'China': (140, 900), 'India': (70, 500), 'Pakistan': (70, 400),
        'North Korea': (7, 1), 'Israel': (40, 900)}

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
