"""
global_thermonuclear_war_game.py

A game inspired by Global Thermonuclear War in the movie War Games.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CHOOSE_SIDE: The input prompt for choosing a side. (str)
CREDITS: The credits for Global Thermonuclear War. (str)
OPTIONS: The options for Global Thermonuclear War. (str)
RULES: The rules for Global Thermonuclear War. (str)

Classes:
GlobalThermonuclearWar: A game of thermonuclear armageddon. (game.Game)
NationBot: A bot representing one of the nuclear powers. (player.Bot)

Functions:
sphere_distance: The distance between two points on a sphere. (float)
"""


import itertools
import math
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

CREDITS = """
Game Design: Craig "Ichabod" O'Brien (based on the movie War Games)
Game Programming: Craig "Ichabod" O'Brien
"""

OPTIONS = """
failure-rate= (fr=): The probability a missile will fail. (0 to 0.5, default
    0.07)
fast (f): Eliminate pauses while displaying missile actions.
russia (r): Play as Russia.
united-states (us): Play as the United States of America.
"""

RULES = """
Each turn you can select primary targets (to fire 5 missiles at) and secondary
targets (to fire 2 missiles at). Targets are cities. The game has a database of
over 3,000 world cities. You can fire at cities not in the database, but you
will need to tell the game which country the city is in and what it's
population is.

When entering targets, you may start a line with 'CMD:' to enter a t_games
system command, or the data command. The data command takes a country name as
an argument, and returns information on that country.

To win, you just need to make sure that no one dies in either your country or
any of your allies' countries.
"""


class GlobalThermonuclearWar(game.Game):
    """
    A game of thermonuclear armageddon. (game.Game)

    Note that the allies and enemies lists are in no way meant to be realistic.
    This is a silly game that you always lose, and I couldn't find an easy source
    for the data, so I just spent a couple days skimming foreign relations articles
    on Wikipedia. I'm sure it's wrong. I'm not seeing the point in worrying about
    it either. The priority was ensuring an escalation of the conflict. And yes, I
    know nuclear winter is a controversial topic. It's a game, dude.

    Attributes:
    auto: A flag for skipping asking for targets. (bool)
    bomb_deaths: Direct deaths from nuclear bombs. (int)
    cities: The data on world cities. (dict of str: dict)
    countries: The data on the nations of the world. (dict of str: dict)
    failure_rate: The chance of a bomb failing. (float)
    fast: A flag for eliminated 'calculation' pauses. (bool)
    human_country: The name of the country the human is playing. (str)
    missiles_flying: Data on missiles fired but landed. (list of tuple)
    missiles_launched: The total number of missiles fired. (int)
    powers: The data on the nuclear powers. (list of dict)
    russia: A flag for the human playing Russia. (bool)
    united_states: A flag for the human playing the United States of America. (bool)

    Class Attributes:
    earth_radius: The radius of the earth in miles. (int)
    world_population: The total population of the planet. (int)

    Methods:
    confirm_target: Confirm the name and distance to a city. (tuple of str, int)
    do_auto: Turn on automatic mode. (bool)
    do_data: Display data on one of the countries in the game. (bool)
    load_cities: Load the city data. (None)
    load_countries: Load the country data. (None)
    new_city: Add a new city to the database. (None)
    update_missiles: Update the tracking of missiles fired. (None)

    Overridden Methods:
    game_over
    player_action
    set_options
    set_up
    """

    categories = ['Simulation Games']
    credits = CREDITS
    earth_radius = 3957
    name = 'Global Thermonuclear War'
    num_options = 2
    options = OPTIONS
    rules = RULES
    world_population = 7700000000

    def confirm_target(self, raw_target):
        """
        Confirm the name and distance to a target city. (tuple of str, int)

        Parameters:
        target: The target as entered by the user. (str)
        """
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
                self.new_city(target, player)
            else:
                # Use the user's choice.
                distance, confirmed = distances[choice - 1]
                country = self.cities[confirmed]['country']
                latitude = self.cities[confirmed]['latitude']
                longitude = self.cities[confirmed]['longitude']
        # Calculate the distance
        start = (self.countries[country.lower()]['latitude'], self.countries[country.lower()]['longitude'])
        end = (latitude, longitude)
        distance = sphere_dist(start, end, self.earth_radius)
        # Return the confirmed name and the distance.
        return confirmed, distance

    def do_auto(self, arguments):
        """
        Turn on automatic mode (does not ask for targets).
        """
        self.auto = True
        return True

    def do_data(self, arguments):
        """
        Display data on one of the countries in the game.
        """
        player = self.players[self.player_index]
        if arguments.lower() in self.countries:
            # Show the city data.
            player.tell('')
            player.tell('data on {}:'.format(arguments).upper())
            data = self.countries[arguments.lower()]
            player.tell('capital: {}.'.format(data['capital']).upper())
            player.tell('largest city: {}.'.format(data['largest']).upper())
            player.tell('other cities: {}'.format(', '.join(data['cities'])).upper())
            # Show enemies and allies for nuclear powers.
            if 'allies' in data:
                player.tell('allies: {}'.format(', '.join(data['allies'])).upper())
                player.tell('enemies: {}'.format(', '.join(data['enemies'])).upper())
        else:
            # Give an error message for unknown countries.
            player.tell('\nI DO NOT RECOGNIZE THAT COUNTRY.')
        return True

    def do_gipf(self, arguments):
        """
        Hamurabi removes the death toll in your own country.

        Gin Rummy give you 108 more bombs.
        """
        game, losses = self.gipf_check(arguments, ('hamurabi', 'gin rummy'))
        go = True
        # Hamurabi removes the death toll in your country.
        if game == 'hamurabi':
            if not losses:
                self.countries[self.human_country.lower()]['death_toll'] = 0
                text = '\nTHE MILITARY HAS CLASSIFIED THE CURRENT DEATH TOLL IN {}.'
                self.human.tell(text.format(self.human_country.upper()))
        # Gin Rummy gives you more bombs.
        elif game == 'gin rummy':
            if not losses:
                self.human.arsenal_left += 108
                text = '\nYOU PRODUCED AN EXTRA 108 MISSILES. YOU NOW HAVE {} MISSILES.'
                self.human.tell(text.format(self.human.arsenal_left))
        # Otherwise I'm confused.
        else:
            self.human.tell("\nI DO NOT RECOGNIZE THAT COUNTRY.")
        return go

    def game_over(self):
        """Check for the end of the world. (bool)"""
        if self.turns >= 9 and not self.missiles_flying:
            # Show death tolls from bombs.
            self.human.tell('')
            text = 'ESTIMATED FATALITIES FOR {}: {:,}'
            for country, data in sorted(self.countries.items()):
                if data['death_toll']:
                    self.human.tell(text.format(country.upper(), data['death_toll']))
                    if data['name'] == self.human_country:
                        self.scores[self.human.name] -= data['death_toll']
                    elif data['name'] in self.countries[self.human_country.lower()]['allies']:
                        self.scores[self.human.name] -= data['death_toll']
            self.human.tell('\nTOTAL ESITMATED FATALITIES FROM BOMBS: {:,}.'.format(self.bomb_deaths))
            # Calcualte deaths from nuclear winter.
            remaining = self.world_population - self.bomb_deaths
            winter_deaths = min(remaining, int(remaining * self.missiles_launched / 3500.0))
            self.human.tell('ESTIMATED FATALITIES FROM NUCLEAR WINTER: {:,}.'.format(winter_deaths))
            self.human.tell('TOTAL ESTIMATED FATALITIES: {:,}.'.format(self.bomb_deaths + winter_deaths))
            # Tell the human they lost.
            self.human.tell('\nWINNER:  NONE')
            self.win_loss_draw = [0, 1, 0]
            return True
        else:
            return False

    def load_cities(self):
        """Load the city data. (None)"""
        self.cities = {}
        # Load the city data.
        with open(os.path.join(utility.LOC, 'other_games', 'city_data.csv')) as city_data:
            city_data.readline()
            for line in city_data:
                # Read the line for the city.
                name, longitude, latitude, country, capital, population = line.split(',')
                # Enter the data in the dictionary.
                name_key, country_key = name.lower(), country.lower()
                self.cities[name_key] = {'name': name, 'latitude': float(latitude),
                    'longitude': float(longitude), 'country': country, 'capital': capital,
                    'population': int(population), 'hits': 0}
                # Update the city's country.
                if country_key not in self.countries:
                    self.countries[country_key] = {'name': country, 'cities': [], 'death_toll': 0}
                self.countries[country_key]['cities'].append(name_key)
                if capital == 'primary':
                    self.countries[country_key]['capital'] = name_key
        # Calculate the largest city and the country's latitude and longitude.
        # (for simplicity's sake, missiles are fired from the 'center' of each country)
        for country_name in self.countries:
            # Initialize the tracking variables.
            max_pop, max_city = 0, ''
            lat_total, long_total = 0, 0
            # Update with the data for each city in the country.
            for city_name in self.countries[country_name]['cities']:
                city_lower = city_name.lower()
                if self.cities[city_lower]['population'] > max_pop:
                    max_pop = self.cities[city_lower]['population']
                    max_city = city_name
                lat_total += self.cities[city_lower]['latitude']
                long_total += self.cities[city_lower]['longitude']
            # Store the largets city.
            self.countries[country_name]['largest'] = max_city
            # Calculate the average longitude/latitude.
            num_cities = len(self.countries[country_name]['cities'])
            self.countries[country_name]['latitude'] = lat_total / num_cities
            self.countries[country_name]['longitude'] = long_total / num_cities

    def load_countries(self):
        """Load the country data. (None)"""
        self.countries = {}
        self.powers = []
        # Read the data for each country (only nuclear powers are stored explicitly).
        with open(os.path.join(utility.LOC, 'other_games', 'country_data.txt')) as country_data:
            num_countries = int(country_data.readline())
            for country in range(num_countries):
                # Get the name and default data.
                name = country_data.readline().strip()
                data = {'name': name, 'cities': [], 'death_toll': 0}
                # Read and parse the data.
                arsenal, paranoia, defense, defense_missiles = country_data.readline().split(',')
                data['arsenal'] = int(arsenal)
                data['paranoia'] = int(paranoia)
                data['defense_rate'] = float(defense)
                data['defense_missiles'] = int(defense_missiles)
                data['allies'] = [country.strip() for country in country_data.readline().split(',')]
                data['enemies'] = [country.strip() for country in country_data.readline().split(',')]
                # Update the data.
                self.countries[name.lower()] = data
                self.powers.append(data)

    def new_city(self, target, player):
        """
        Add a new city to the database. (None)

        Parameters:
        target: The name of the city to add. (str)
        player: The player adding the city. (player.Player)
        """
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
        query = '\nWHAT IS THE POPULATION OF {}?'.format(confirmed).upper()
        population = player.ask_int(query, low = 1, high = 1000000)
        # Enter the new city.
        self.cities[confirmed] = {'name': target, 'population': population, 'country': country,
            'latitude': latitude, 'longitude': longitude, 'hits': 0}
        self.countries[country]['cities'].append(target)

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Check for Chess win or no missiles.
        if self.force_end:
            return False
        # Get the name of the player's country.
        if player == self.human:
            country = self.human_country
        else:
            country = player.name
        # Get the targets (for players with missiles, but skip the human in auto mode).
        primaries = []
        secondaries = []
        if player.arsenal_left > 0:
            for target_list, name in ((primaries, 'PRIMARY'), (secondaries, 'SECONDARY')):
                if player == self.human and self.auto:
                    break
                player.tell('\nPLEASE LIST {} TARGETS:'.format(name))
                while True:
                    city = player.ask('')
                    if city.lower().startswith('cmd:'):
                        # Handle any commands.
                        tag, colon, command = city.partition(':')
                        go = self.handle_cmd(command)
                        if player == self.human and self.auto:
                            break
                        if not go:
                            return False
                        player.tell('\nPLEASE LIST {} TARGETS:'.format(name))
                    elif city:
                        # Add non-commands to the target list.
                        target_list.append(city)
                    else:
                        break
        elif player.arsenal_left <= 0:
            player.ask('\nYOU HAVE NO MISSILES LEFT. PRESS ENTER TO CONTINUE:  ')
        # Update any currently flying missiles
        # (done here to keep missiles in play sequence so bots can tell what's been fired this round)
        self.update_missiles(country)
        # Fire the missiles at the selected targets.
        for missiles, targets in ((5, primaries), (2, secondaries)):
            if targets:
                self.human.tell('')
            for target in targets:
                confirmed, distance = self.confirm_target(target)
                if not confirmed:
                    # Skip unrecognized cities the user didn't add.
                    continue
                target_country = self.cities[confirmed]['country']
                # Tell the human about foreign launches.
                if player != self.human:
                    self.human.tell('{} launches missiles at {}.'.format(player.name, target).upper())
                    if not self.fast:
                        time.sleep(0.5)
                # Update the tracking data.
                self.missiles_flying.append((country, missiles, confirmed, target_country, distance))
                self.missiles_launched += missiles
                player.arsenal_left -= missiles
                # Stop if the player is out of missiles.
                if player.arsenal_left <= 0:
                    player.tell('YOU HAVE RUN OUT OF MISSILES.')
                    break
        return False

    def set_options(self):
        """Define the options for the game. (None)"""
        self.option_set.add_option('united-states', ['us'],
            question = 'Would you like to play the United States? bool')
        self.option_set.add_option('russia', ['r'],
            question = 'Would you like to play Russia? bool')
        self.option_set.add_option('failure_rate', ['fr'], float, 0.07, check = lambda fr: 0 <= fr < 0.5,
            question = 'What should the missile failure rate be (return for 0.07)? ')
        self.option_set.add_option('fast', ['f'],
            question = 'Would you like to remove the pauses during output? bool')

    def set_up(self):
        """Set up the game. (None)"""
        self.players = [self.human]
        self.auto = False
        # Try to play chess instead.
        if self.human.ask("\nWOULDN'T YOU PREFER A GOOD GAME OF CHESS? ") in utility.YES:
            game = self.interface.games['chess'](self.human, 'none', self.interface)
            results = game.play()
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
                        if key != 'name':
                            setattr(self.human, key, value)
                    self.human.arsenal_left = self.human.arsenal
                else:
                    self.players.append(NationBot(**country_data))
                    self.players[-1].game = self

    def update_missiles(self, current_country):
        """
        Update the tracking of missiles fired. (None)

        Parameters:
        current_country: The country that is taking a turn. (None)
        """
        new_missiles = []
        needs_space = True
        # Loop through the missile data.
        for country, missiles, target, target_country, distance in self.missiles_flying:
            # Update missiles fired by the current country.
            if country == current_country:
                # Handle missiles arriving at their target.
                if distance <= 1000:
                    # Check each missile to see if it fails.
                    hits = self.cities[target]['hits']  # Use total hits for calculating deaths.
                    deaths = 0
                    for shot in range(missiles):
                        if random.random() > self.failure_rate:
                            # Calculate deaths on a decreasing scale with a random factor.
                            death_mod = max(0.01, (10 - hits) / 10.0)
                            death_base = int(self.cities[target]['population'] * death_mod)
                            death_range = death_base // 10
                            hits += 1
                            deaths += random.randint(death_base - death_range, death_base + death_range)
                    hits -= self.cities[target]['hits']  # Use this turn's hits for output.
                    if hits:
                        # Inform the human of the death toll from the strike.
                        if needs_space:
                            self.human.tell('')
                            needs_space = False
                        text = '{} IS HIT WITH {} RESULTING IN {:,} ESTIMATED FATALITIES.'
                        hit_text = utility.number_plural(hits, 'missile').upper()
                        self.human.tell(text.format(target.upper(), hit_text, deaths))
                        if not self.fast:
                            time.sleep(0.5)
                        # Update the tracking data.
                        self.countries[target_country.lower()]['death_toll'] += deaths
                        self.bomb_deaths += deaths
                        self.cities[target]['hits'] += hits
                else:
                    # Move other missiles closer to their target.
                    new_missiles.append((country, missiles, target, target_country, distance - 1000))
            else:
                # Do not update missiles for non-current countries.
                new_missiles.append((country, missiles, target, target_country, distance))
        # Reset the missile data.
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
    get_direct: Get a target country based on a direct attack.
    get_indirect: Get a target country based on an indirect attack.
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
            # Output targets by mode.
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
                # Blank line/mode when you run out of the current target list.
                self.output_mode = ''
                return ''
        elif prompt.startswith('\nYOU HAVE NO MISSILES LEFT.'):
            # Carry on.
            return ''
        else:
            # Whoops.
            super(NationBot, self).ask(prompt)

    def get_direct(self, foe):
        """
        Get a target country based on a direct attack.

        Parameters:
        foe: The country that attacked you. (str)
        """
        # Mostly fire right back, but sometimes target an ally.
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
        # Get their allies that are not your allies.
        their_allies = self.game.countries[foe.lower()].get('allies', [])
        targets = [ally for ally in their_allies if ally not in self.allies]
        # Fire on one if you can, otherwise fire right back.
        if targets:
            return random.choice(targets)
        else:
            return foe

    def get_targets(self):
        """Determine who to fire missiles at. (None)"""
        # Get the combined target list.
        targets = self.direct_foes + self.indect_foes
        if self.paranoid:
            targets += self.enemies
        # Loop through the target countries until you run out of missile you want to fire.
        for foe in itertools.cycle(targets):
            if self.num_targets <= 0:
                break
            # Get an appropriate country.
            if foe in self.indirect_foes:
                target_country = self.get_indirect(foe)
            else:
                target_country = self.get_direct(foe)
            # Fire on the capital, then the largest city, then on random cities.
            capital = self.game.countries[target_country.lower()]['capital']
            largest = self.game.countries[target_country.lower()]['largest']
            if not self.game.cities[capital]['hits'] and capital not in self.primary_targets:
                self.primary_targets.append(capital)
            elif not self.game.cities[largest]['hits'] and largest not in self.primary_targets:
                self.primary_targets.append(largest)
            else:
                city = random.choice(self.game.countries[target_country.lower()]['cities'])
                if random.random() < 0.66:
                    self.secondary_targets.append(city)
                else:
                    self.primary_targets.append(city)
            # Update desired missile count.
            self.num_targets -= 1

    def set_strategy(self):
        """Set the strategy for the next round of target selection. (None)"""
        # Base your strategy on what's in the air.
        self.num_targets = 1
        other_missiles = len(self.game.missiles_flying)
        self.direct_foes, self.indirect_foes = [], []
        for country, missiles, target, target_country, distance in self.game.missiles_flying:
            if country == self.name:
                other_missiles -= 1
            # Handle direct attacks.
            elif target_country == self.name:
                self.num_targets += 1
                if country not in self.direct_foes:
                    self.direct_foes.append(country)
            # Handle indirect attacks.
            elif target_country in self.allies:
                self.num_targets += 1
                if country not in self.indirect_foes:
                    self.indirect_foes.append(country)
        # Israel only responds to direct attacks.
        if self.name == 'Israel':
            self.indirect_foes = []
        # Clean up indirect attacks.
        self.indect_foes = [country for country in self.indirect_foes if country not in self.direct_foes]
        # Check for paranoia.
        if self.game.missiles_launched >= self.paranoia or self.arsenal_left * 2 < self.arsenal:
            self.paranoid = True
            self.num_targets = other_missiles * 2 + (self.name == 'North Korea')

    def set_up(self):
        """Set up the bot's tracking variables. (None)"""
        self.paranoid = False

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        # Update targets and output mode when asked for targets.
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
    p1 = [math.radians(x) for x in point_a]
    p2 = [math.radians(x) for x in point_b]
    # Get the differences in the coordinates.
    dlat = p2[0] - p1[0]
    dlon = p2[1] - p1[1]
    # Calculate the arc length.
    a = math.sin(dlat / 2) ** 2 + math.cos(p1[0]) * math.cos(p2[0]) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return c * radius
