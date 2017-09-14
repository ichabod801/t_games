"""
hamurabi_game.py

The computer classic Hamurabi.

!! check that all attributes need to be attributes.

Constants:
CREDITS: The credits for Hamurabi. (str)
RULES: The basic rules of Hamurabi. (str)

Classes:
Hamurabi: A game of Humurabi. (game.Game)
"""


import random

import tgames.game as game


# The credits for Hamurabi.
CREDITS = """
Game Design/Original Programming: Doug Dyment
Python Implementation: Craig "Ichabod" O'Brien
"""

# The basic rules of Hamurabi.
RULES = """
You have ten turns to run ancient Sumeria. Each turn you can buy or sell land,
buy or sell grain, how much to feed your people, and how much grain to plant.
You will have to deal with disasters such as rats and plagues.
"""


class Hamurabi(game.Game):
    """
    A game of Hamurabi. (game.Game)

    Attributes:
    acres: The current size of the city. (int)
    average_starved: The number of people starved per year. (int)
    bushels_per_acre: How much grain can grow in an acre. (int)
    feed: How many bushels were given to the people this year. (int)
    game_length: The number of turns in the game. (int)
    immigration: The immigration modifier. (int)
    impeachment: The impeachment modifier. (int)
    plague_chance: The yearly chance of plague. (int)
    population: The current population. (int)
    rat_chance: The yearly chance of rats. (int)
    rats: The current rat damage. (int)
    seed: The current amount planted. (int)
    start_acres: The starting acreage for the city state. (int)
    start_population: The starting population for the city state. (int)
    start_rats: The starting rat damage. (int)
    starved: The number of people starved this year. (int)
    storage: How many bushels of grain are in storage. (int)
    total_starved: The number of people starved in all years. (int)

    Methods:
    show_status: Show the current game status. (None)

    Overridden Methods:
    game_over
    handle_options
    set_up
    """

    aka = ['The Sumer Game']
    credits = CREDITS
    categories = ['Other Games', 'Simulation Games']
    name = 'Hamurabi'
    rules = RULES

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # check for impeachment
        if self.feed // 20 < self.population:
            self.starved = self.population - feed // 20
            self.total_starved += self.starved
            self.average_starved += self.starved / self.population / self.game_length
            if self.starved > self.impeachment * self.population / 100.0:
                message = 'You starved {} people in one year!!\n'.format(self.starved)
                message += 'Due to this extreme mismanagement, you have not only been impeached and\n'
                message += 'thrown out of office, but you have also been declared a national fink!!!!'
                self.human.tell(message)
                self.win_loss_draw[1] = 1
        elif self.turns == self.game_length:
            # show end of game summary
            land_per = self.acres // self.population
            status = "In your 10-year term of office {:.2f} percent of the population starved per year\n"
            status += "on average. That is a total of {} people died!!\n"
            status.format(self.average_starved, self.total_starved)
            status += '\nYou started with {} acres per person and ended with {} acres per person.\n'
            status.format(10, land_per) + '\n'
            # check for impeachment
            if self.average_starved > 0.33 or land_per < 7:
                status += 'Due to this extreme mismanagement, you have not only been impeached and\n'
                status += 'thrown out of office, but you have also been declared a national fink!!!!'
                self.win_loss_draw[1] = 1
            elif no self.win_loss_draw[1]:
                # check for level of win
                self.win_loss_draw[0] = 1
                if self.average_starved > 0.10 or land_per < 9:
                    status += "Your heavy-handed performance smacks of Nero and Ivan IV.\n"
                    status += "The (remaining) people find you an unpleasant ruler, and, frankly,\n"
                    status += "hate your guts!!"
                    self.scores[self.human.name] = 1
                elif self.average_starved > 0.03 or land_per < 10:
                    hate = int(self.population * 0.8 * random.random())
                    status += "Your performance could have been somewhat better, but really wasn't too\n"
                    status += "bad at all. {} people would dearly like to see you assassinated, but we\n"
                    status += "all have our trivial problems."
                    status.format(hate)
                    self.scores[self.human.name] = 2
                else:
                    status += "A fantastic performance!!! Charlemange, Disreli, and Jefferson combined\n"
                    status += "could not have done better!"
                    self.scores = [3]
            self.human.tell(status)
        else:
            self.starved = 0
            return False
        return True

    def handle_options(self):
        """Handle the game options. (None)"""
        # Set default options.
        self.game_length = 10
        self.immigration = 20
        self.impeachment = 45
        self.plague_chance = 15
        self.rat_chance = 40
        self.start_acres = 1000
        self.start_population = 95
        self.start_rats = 200

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        self.show_status()
        # Get the player choices.
        # Get acres to buy.
        buy = self.human.ask_int('How many acres would you like to buy? ', 0, self.storage / acre_cost)
        self.storage -= buy * acre_cost
        self.acres += buy
        # Get acres to sell.
        sell = self.human.ask_int('How many acres would you like to sell? ', 0, self.acres)
        self.acres -= sell
        self.storage += sell * acre_cost
        # Get bushels to release.
        bushel_question = 'How many bushels would you like to feed to your people? '
        self.feed = self.human.ask_int(bushel_question, 0, self.storage)
        self.acres -= self.feed
        self.storage += self.feed * acre_cost
        # Get seed to plant.
        max_seed = min(self.acres, self.storage * 2, self.population * 10)
        if max_seed:
            self.seed = self.human.ask_int('How many acres do you wish to plant with seed? ', 0, max_seed)
            self.seed = int(self.seed)
            self.storage -= self.seed // 2
        # determine values for next turn
        self.bushels_per_acre = random.randint(1, 5)
        if random.random() <= self.rat_chance / 100.0:
            self.rats = int(self.storage / 2 / random.randint(1, 2))
        else:
            self.rats = 0
        self.immigrants = random.randint(1, 5)
        self.immigrants *= (self.immigration * self.acres + self.storage)
        self.immigrants = int((self.immigrants / float(self.population) / 100.0) + 1)
        # check for impeachment
        if feed // 20 < self.population:
            self.starved = self.population - feed // 20
            self.total_starved += self.starved
            self.average_starved += self.starved / self.population / self.game_length
            if self.starved > self.impeachment * self.population / 100.0:
                message = 'You starved {} people in one year!!\n'.format(self.starved)
                message += 'Due to this extreme mismanagement, you have not only been impeached and thrown\n'
                message += 'out of office, but you have also been declared a national fink!!!!'
                self.human.tell(message)
                # self.game_over = True
        else:
            self.starved = 0

    def set_up(self):
        """Set up the game. (None)"""
        # Set non-optional parameters
        self.bushels_per_acre = 3
        # Set tracking based on optional parameters
        self.population = self.start_population
        self.acres = self.start_acres
        self.seed = self.start_acres
        self.rats = self.start_rats
        self.game_length = float(self.game_length)
        # Set other tracking variables
        self.starved = 0
        self.total_starved = 0
        self.average_starved = 0
        self.immigrants = 5
        self.storage = 0
        # Display the introduction.
        intro = 'Try your hand at ruling ancient Sumeria for a {}-year term of office.'
        self.human.tell(intro.format(self.game_length))

    def show_status(self):
        """Show the current game status. (None)"""
        # Start with the overviewl
        status += '\nHamurabi, I beg to report to you, in year {}, {} people starved and {} came to the '
        status += 'city.\n'
        status.format(self.turn, self.starved, self.imigrants)
        self.population += self.immigrants - self.starved
        # Check for plague.
        if self.turn > 1 and random.random() <= self.plague_chance / 100.0:
            status += 'A horrible plague struck! Half the people died.\n'
            self.population = self.population // 2
        # Add general stats.
        status += 'The population is now {}.\n'.format(self.population)
        status += 'The city now owns {} acres.\n'.format(self.acres)
        status += 'You harvested {} bushels per acre.\n'.format(self.bushels_per_acre)
        status += 'Rats ate {} bushels.\n'.format(self.rats)
        self.storage += self.seed * self.bushels_per_acre - self.rats
        status += 'You now have {} bushels in storage.\n'.format(self.storage)
        acre_cost = random.randint(17,26)
        status += 'Land is trading at {} bushels per acre.'.format(acre_cost)
        # Tell the human.
        self.human.tell(status)