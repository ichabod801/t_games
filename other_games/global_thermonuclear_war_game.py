"""
global_thermonuclear_war_game.py

A game inspired by Global Thermonuclear War in the movie War Games.

To Do:
End of game
    Nuclear winter, 1% starvation rate for every 10 bombs detonated.
Can't fire if no missiles

Classes:
GlobalThermonuclearWar: A game of thermonuclear armageddon. (game.Game)
"""


import itertools
from math import radians, sin, cos, acos, ceil
import os
import random
import time

from .. import game
from .. import player
from .. import utility


CHOOSE_SIDE = """
WHICH SIDE DO YOU WANT?

  1.    UNITED STATES
  2.    RUSSIA

PLEASE CHOOSE ONE:  """


class GlobalThermonuclearWar(game.Game):
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

    categories = ['Other Games']
    earth_radius = 3957
    earth_circumference = 24881.0
    name = 'Global Thermonuclear War'
    num_options = 2
    world_population = 7700000000

    def confirm_target(self, raw_target):
        """
        Confirm the name and distance to a target city. (tuple of str, int)

        Parameters:
        target: The target as entered by the user. (str)
        """
        # !! refactor (new_city method?)
        player = self.players[self.player_index]
        target = raw_target.lower()
        if target in self.cities:
            # If it's in the data, use the data.
            confirmed = target.lower()
            country = self.cities[confirmed]['country']
            latitude = self.cities[confirmed]['latitude']
            longitude = self.cities[confirmed]['longitude']
        else:
            # Get text distances to other city names.
            distances = []
            for city in self.cities:
                if target in city:
                    # Prioritize city names containing the target name.
                    distances.append((0, city))
                else:
                    distances.append((utility.levenshtein(target, city), city))
            # List the three closest city names as options, with an option to enter a new city.
            distances.sort()
            lines = ['', 'I DO NOT RECOGNIZE {}'.format(target.upper()), '', 'POSSIBLE MATCHES:', '']
            for city_index, city in enumerate(distances[:3], start = 1):
                lines.append('{}: {}'.format(city_index, self.cities[city[1]]['name']).upper())
            lines.extend(['4: NONE OF THE ABOVE', '', 'SELECT THE BEST MATCH:  '])
            query = '\n'.join(lines)
            choice = player.ask_int(query, low = 1, high = 4)
            if choice == 4:
                confirmed = target
                # Get the country.
                while True:
                    country = player.ask('\nWHAT COUNTRY IS {} IN?  '.format(confirmed.upper())).lower()
                    if country.lower() in self.countries:
                        break
                    elif not country:
                        return ('', 0)
                    player.tell('\nI DO NOT RECOGNIZE THAT COUNTRY.')
                    player.tell('PLEASE TRY AGAIN OR HIT ENTER TO CANCEL TARGET.')
                # Get the city coordinates from the country.
                latitude = self.countries[country]['latitude']
                longitude = self.countries[country]['longitude']
                # Get the population of the city.
                query = '\nWHAT IS THE POPULATION OF {}?'.format(confirmed)
                population = player.ask_int(query, low = 1, high = 1000000)
                # Enter the new city.
                self.cities[confirmed] = {'name': confirmed, 'population': population, 'country': country,
                    'latitude': latitude, 'longitude': longitude, 'hits': 0}
                self.countries[country]['cities'].append(confirmed)
            else:
                # Use the user's choice.
                distance, confirmed = distances[choice - 1]
                country = self.cities[confirmed]['country']
                latitude = self.cities[confirmed]['latitude']
                longitude = self.cities[confirmed]['longitude']
        # Calculate the distance
        start = (self.countries[country.lower()]['latitude'], self.countries[country.lower()]['longitude'])
        end = (latitude, longitude)
        distance = ceil(sphere_dist(start, end, self.earth_radius) / self.earth_circumference * 6)
        # Return the confirmed name and the distance.
        return confirmed, distance

    def game_over(self):
        """Check for the end of the world. (bool)"""
        if self.turns >= 7 and not self.missiles_flying:
            # !! Needs more output and nuclear winter.
            self.human.tell('{} ESITMATED FATALITIES.'.format(self.bomb_daths))
            self.human.tell('WINNER:  NONE')
            self.win_loss_draw = [0, 1, 0]
            self.scores[self.human.name] = -self.bomb_deaths
            return True
        else:
            return False

    def load_cities(self):
        """Load the city data. (None)"""
        self.cities = {}
        with open(os.path.join(utility.LOC, 'other_games', 'city_data.csv')) as city_data:
            city_data.readline()
            for line in city_data:
                name, longitude, latitude, country, capital, population = line.split(',')
                name_key, country_key = name.lower(), country.lower()
                #print(name)
                self.cities[name_key] = {'name': name, 'latitude': float(latitude),
                    'longitude': float(longitude), 'country': country, 'capital': capital,
                    'population': int(population), 'hits': 0}
                if country_key not in self.countries:
                    self.countries[country_key] = {'name': country, 'cities': [], 'death_toll': 0}
                self.countries[country_key]['cities'].append(name_key)
                if capital == 'primary':
                    self.countries[country_key]['capital'] = name_key
        for country_name in self.countries:
            max_pop, max_city = 0, ''
            lat_total, long_total = 0, 0
            for city_name in self.countries[country_name]['cities']:
                city_lower = city_name.lower()
                if self.cities[city_lower]['population'] > max_pop:
                    max_pop = self.cities[city_lower]['population']
                    max_city = city_name
                lat_total += self.cities[city_lower]['latitude']
                long_total += self.cities[city_lower]['longitude']
            self.countries[country_name]['largest'] = max_city
            num_cities = len(self.countries[country_name]['cities'])
            self.countries[country_name]['latitude'] = lat_total / num_cities
            self.countries[country_name]['longitude'] = long_total / num_cities

    def load_countries(self):
        """Load the country data. (None)"""
        self.countries = {}
        self.powers = []
        with open(os.path.join(utility.LOC, 'other_games', 'country_data.txt')) as country_data:
            num_countries = int(country_data.readline())
            for country in range(num_countries):
                name = country_data.readline().strip()
                data = {'name': name, 'cities': [], 'death_toll': 0}
                arsenal, paranoia, defense, defense_missiles = country_data.readline().split(',')
                data['arsenal'] = int(arsenal)
                data['paranoia'] = int(paranoia)
                data['defense_rate'] = float(defense)
                data['defense_missiles'] = int(defense_missiles)
                data['allies'] = [country.strip() for country in country_data.readline().split(',')]
                data['enemies'] = [country.strip() for country in country_data.readline().split(',')]
                self.countries[name.lower()] = data
                self.powers.append(data)

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Check for Chess win or no missiles.
        if self.force_end or player.arsenal_left <= 0:
            return False
        # Get the name of the player's country.
        if player == self.human:
            country = self.human_country
        else:
            country = player.name
        # Get the targets.
        if player.arsenal_left > 0:
            primaries = []
            secondaries = []
            for target_list, name in ((primaries, 'PRIMARY'), (secondaries, 'SECONDARY')):
                player.tell('\nPLEASE LIST {} TARGETS:'.format(name))
                while True:
                    city = player.ask('')
                    if city:
                        target_list.append(city)
                    else:
                        break
        else:
            self.player.ask('\nYOU HAVE NO MISSILES LEFT. PRESS ENTER TO CONTINUE:  ')
        # Update any currently flying missiles
        # (done here to keep missiles in play sequence so bots can tell what's been fired this round)
        self.update_missiles(country)
        # Fire the missiles at the selected targets.
        for missiles, targets in ((5, primaries), (2, secondaries)):
            for target in targets:
                confirmed, distance = self.confirm_target(target)
                if not confirmed:
                    continue
                target_country = self.cities[confirmed]['country']
                if player != self.human:
                    self.human.tell('{} launches missiles at {}.'.format(player.name, target).upper())
                    time.sleep(1)
                self.missiles_flying.append((country, missiles, confirmed, target_country, distance))
                self.missiles_launched += missiles
                player.arsenal_left -= missiles
                if player.arsenal_left <= 0:
                    player.tell('You have run out of missiles.')
                    break
        print(self.missiles_flying)
        print(player.arsenal_left)
        return False

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.add_option('united-states', ['us'])
        self.option_set.add_option('russia', ['r'])
        self.option_set.add_option('failure_rate', ['fr'], float, 0.07, check = lambda fr: 0 <= fr <= 1)

    def set_up(self):
        """Set up the game. (None)"""
        self.players = [self.human]
        # Try to play chess instead.
        if self.human.ask("\nWOULDN'T YOU PREFER A GOOD GAME OF CHESS? ") in utility.YES:
            results = self.interface.games['chess'].play('')
            self.win_loss_draw = [1, 0, 0]
            self.scores[self.human.name] = results[3]
            self.force_end = 'chess'
        else:
            # Load the data.
            self.load_countries()
            self.load_cities()
            # Initialize the tracking variables.
            self.bomb_deaths, self.winter_deaths = 0, 0
            self.missiles_flying = []
            self.missiles_launched = 0
            # Get the country to play.
            if self.united_states:
                self.human_country = 'United States'
            elif self.russia:
                self.human_country = 'Russia'
            else:
                while True:
                    side_num = self.human.ask(CHOOSE_SIDE).strip()
                    if side_num == '1':
                        self.human_country = 'United States'
                    elif side_num == '2':
                        self.human_country = 'Russia'
                    else:
                        self.human.tell('PLEASE CHOOSE 1 OR 2.')
                        continue
                    break
            # Set up the players.
            for country_data in self.powers:
                if country_data['name'] == self.human_country:
                    for key, value in country_data.items():
                        setattr(self.human, key, value)
                    self.human.arsenal_left = self.human.arsenal
                else:
                    self.players.append(NationBot(**country_data))
                    self.players[-1].game = self

    def update_missiles(self, current_country):
        new_missiles = []
        for country, missiles, target, target_country, distance in self.missiles_flying:
            if country == current_country:
                if distance == 1:
                    hits = 0
                    deaths = 0
                    for shot in range(missiles):
                        if random.random() > self.failure_rate:
                            death_mod = max(0.01, (10 - hits) / 10.0)
                            death_base = int(self.cities[target]['population'] * death_mod)
                            death_range = death_base // 10
                            hits += 1
                            deaths += random.randint(death_base - death_range, death_base + death_range)
                    if hits:
                        text = '{} IS HIT WITH {} RESULTING IN {} ESTIMATED FATALITIES.'
                        hit_text = utility.number_plural(hits, 'missile').upper()
                        self.human.tell(text.format(target.upper(), hit_text, deaths))
                        time.sleep(1)
                        self.countries[target_country.lower()]['death_toll'] += deaths
                        self.bomb_deaths += deaths
                        self.cities[target]['hits'] += hits
                else:
                    new_missiles.append((country, missiles, target, target_country, distance - 1))
            else:
                new_missiles.append((country, missiles, target, target_country, distance))
        self.missiles_flying = new_missiles

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
                target = target_list.pop()
                return target
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
        if random.random() < 0.801:
            return foe
        else:
            return self.get_indirect(foe)

    def get_indirect(self, foe):
        """
        Get a target country based on an indirect attack.

        Paramters:
        foe: The country that attacked you. (str)
        """
        their_allies = self.game.countries[foe.lower()].get('allies', [])
        targets = [ally for ally in their_allies if ally not in self.allies]
        if targets:
            return random.choice(targets)
        else:
            return foe

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
            if not self.game.cities[self.game.countries[target_country.lower()]['capital']]['hits']:
                self.primary_targets.append(self.game.countries[target_country.lower()]['capital'])
            elif not self.game.cities[self.game.countries[target_country.lower()]['largest']]['hits']:
                self.primary_targets.append(self.game.countries[target_country.lower()]['largest'])
            else:
                city = random.choice(self.game.countries[target_country.lower()]['cities'])
                self.secondary_targets.append(city)
            self.num_targets -= 1
            if not self.num_targets:
                break

    def set_strategy(self):
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


def sphere_dist(point_a, point_b, radius):
    """
    The distance between two points on a sphere. (float)

    Parameters:
    point_a: Latitude and longitude of the first point. (tuple of float)
    point_b: Latitude and longitude of the second point. (tuple of float)
    radius: Radius of the sphere. (float)
    """
    # lambda is longitude
    # Convert to Cartesian coordinates.
    p1 = [radians(x) for x in point_a]
    #v1 = [math.cos(p1[1]) * math.cos(p1[0]), math.sin(p1[1]) * math.cos(p1[0]), math.sin(p1[0])]
    p2 = [radians(x) for x in point_b]
    #v2 = [math.cos(p2[1]) * math.cos(p2[0]), math.sin(p2[1]) * math.cos(p2[0]), math.sin(p2[0])]
    # Multiply the vectors.
    #cos_a = sum([c1 * c2 for c1, c2 in zip(v1, v2)])
    cos_a = min(1, sin(p1[0]) * sin(p2[0]) + cos(p1[0]) * cos(p2[0]) * cos(p2[1] - p1[1]))
    # Return the distance.
    return radius * acos(cos_a)
