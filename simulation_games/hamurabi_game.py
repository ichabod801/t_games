"""
hamurabi_game.py

The computer classic Hamurabi. No, it is not misspelled.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
CREDITS: The credits for Hamurabi. (str)
IMMIGRATION_HELP: Help text for factors driving immigration. (str)
RULES: The basic rules of Hamurabi. (str)
WINNING_HELP: Help text for how winning is calculated. (str)

Classes:
Hamurabi: A game of Humurabi. (game.Game)
"""


import random

from .. import game
from .. import utility


CREDITS = """
Game Design/Original Programming: Doug Dyment
Python Implementation: Craig "Ichabod" O'Brien
"""

IMMIGRATION_HELP = """
The more land you have and the more grain you have in storage, the higher your
immigration will be. The more people you have, the lower your immigration will
be.
"""

RULES = """
You have ten turns to run ancient Sumeria. Each turn you can buy or sell land,
buy or sell grain, decide how much to feed your people, and decide how much
grain to plant. You will have to deal with disasters such as rats and plagues.

Commands:
buy (b): Buy the specified number of acres.
feed (f): Release the specified number of bales of grain to the people.
next (n): Finish your turn and go to the next year.
plant (p): Plant seed in the specified number of acres.
sell (s): Sell the specified number of acres.

Options:
plague-chance= (pc=): The chance of plague. 0 to 100, defaults to 15.
rat-chance= (rc=): The chance of rats eating grain. 0 to 100, defaults to 40.
steady-grain (sg): Grain yields are more likely to be average.
steady-land (sl): Land prices are more likely to be average.
"""

WINNING_HELP = """
To win the game, you need to starve less than 33% of your people per turn on
average, and have at least seven acres of land per person at the end of the
game. Furthermore, if you ever starve 45% of your people in one turn, you get
impeached, and you lose the game immediately. Any result that says you are
impeached counts as a loss.

If you starve more than 10% of your people on average or have less than nine
acres of land at the end of the game, you get a one point win. If you starve
more than 3% of your people on averge per turn or have less than ten acres of
land per person at the end of the game, you get a two point win. Otherwise,
you get a three point win.
"""


class Hamurabi(game.Game):
    """
    A game of Hamurabi. (game.Game)

    Class Attributes:
    year_intro: The text for the game status shown at the start of each turn. (str)

    Attributes:
    acre_cost: The current cost of new land in bushels. (int)
    acres: The current size of the city. (int)
    average_starved: The number of people starved per year. (int)
    bushels_per_acre: How much grain can grow in an acre. (int)
    feed: How many bushels were given to the people this year. (int)
    game_length: The number of turns in the game. (int)
    grain_mod: How many extra bushels will be product per acre next year. (int)
    grain_yields: The distribution of grain yields. (tuple of int)
    immigrants: The number of new immigrants this year. (int)
    immigration: The immigration modifier. (int)
    impeachment: The impeachment modifier. (int)
    land_costs: The distribution of land prices. (tuple of int)
    plague_chance: The yearly chance of plague. (int)
    population: The current population. (int)
    rat_chance: The yearly chance of rats. (int)
    rats: The current rat damage. (int)
    seed: The current amount planted. (int)
    start_acres: The starting acreage for the city state. (int)
    start_population: The starting population for the city state. (int)
    start_rats: The starting rat damage. (int)
    starved: The number of people starved this year. (int)
    steady_grain: A flag for a lower variance of grain yields. (bool)
    steady_land: A flag for a lower variance of land prices. (bool)
    storage: How many bushels of grain are in storage. (int)
    total_starved: The number of people starved in all years. (int)

    Methods:
    do_buy: Buy land with grain. (bool)
    do_feed: Feed the people. (bool)
    do_next: Move on to the next turn. (bool)
    do_plant: Seed the land for the next harvest. (bool)
    do_sell: Sell land for grain. (bool)
    show_status: Show the current game status. (None)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['The Sumer Game', 'Hamu']
    aliases = {'b': 'buy', 'f': 'feed', 'n': 'next', 'p': 'plant', 's': 'sell'}
    credits = CREDITS
    categories = ['Simulation Games']
    help_text = {'immigration': IMMIGRATION_HELP, 'winning': WINNING_HELP}
    name = 'Hamurabi'
    num_options = 4
    rules = RULES
    year_intro = '\nHamurabi, I beg to report to you, in year {}, {} people starved and {} came to the '
    year_intro += 'city.\nYou havested {} bushels per acre.\nRats ate {} bushels.'

    def do_buy(self, arguments):
        """
        Buy land with grain. (b)

        The argument is the number of acres to buy. The average cost of land is 22
        bushels of grain. Anything below that and you can buy low.
        """
        # Check for an integer argument.
        try:
            acres = int(arguments)
        except ValueError:
            self.human.error('Invalid argument to buy: {!r}.'.format(arguments))
            return False
        # Check for a valid argument
        if acres < 0:
            self.human.error("You can't buy negative acres.")
        elif acres > self.storage / self.acre_cost:
            self.human.error("You don't have enough grain to buy that many acres.")
        else:
            # Buy the land.
            self.storage -= acres * self.acre_cost
            self.acres += acres
        return True

    def do_feed(self, arguments):
        """
        Feed the people. (f)

        The argument is the number of bushels of grain to release from storage. It
        takes twenty (20) bushels of grain to feed one person.
        """
        # Check for an integer argument.
        try:
            bales = int(arguments)
        except ValueError:
            self.human.error('Invalid argument to feed: {!r}.'.format(arguments))
            return False
        # Check for a valid argument.
        if bales < 0:
            self.human.error("People vomitting on you is not supported in this version.")
        elif bales > self.storage:
            self.human.error("You don't have that many bales to release.")
        else:
            # Feed the people.
            self.feed += bales
            self.storage -= bales
        return True

    def do_gipf(self, arguments):
        """
        Cribbage cats, who will kill of the next set of rats. Yacht improves the next
        grain yield by one.
        """
        game, losses = self.gipf_check(arguments, ('cribbage', 'yacht'))
        go = True
        # Wins at Cribbage prevent the next set of rats.
        if game == 'cribbage':
            if not losses:
                self.human.tell('\nYou have encouraged a clutter of cats to reside in your granaries.')
                self.cats = True
        # Wins at Yacht add one to the grain yield for next turn.
        elif game == 'yacht':
            if not losses:
                self.human.tell('\nYour offering to the fertility gods has been accepted.')
                self.grain_mod = 1
        # Otherwise I'm confused.
        else:
            self.human.tell('\nThe priests of Gipf reject your offering.')
        return go

    def do_next(self, arguments):
        """
        Move on to the next turn. (n)
        """
        # Check for tasks done.
        if self.feed == 0:
            feed_check = self.human.ask('You have not fed anyone. Are you sure you want to continue? ')
            if feed_check.lower() not in utility.YES:
                return False
        if self.seed == 0:
            seed_check = self.human.ask("No seed has been planted. Are you sure you want to continue? ")
            if seed_check.lower() not in utility.YES:
                return False
        # Determine values for next turn.
        # Update grain values and reset the grain bonus.
        self.bushels_per_acre = random.choice(self.grain_yields) + self.grain_mod
        self.grain_mod = 0
        if random.random() <= self.rat_chance / 100.0:
            if self.cats:
                # If the user got cats, they kill the rats and die.
                self.human.tell('\nA vicious rat vs. cat battle broke out in your granaries.')
                self.human.tell('There are bodies everywhere.')
                self.cats = False
                self.rats = 0
            else:
                # Otherwise the rats each some of the storage (1/2 or 1/4).
                self.rats = int(self.storage / 2 / random.randint(1, 2))
        else:
            self.rats = 0
        self.storage += self.seed * self.bushels_per_acre - self.rats
        # Update population values.
        self.immigrants = random.randint(1, 5)
        self.immigrants *= (self.immigration * self.acres + self.storage)
        self.immigrants = int((self.immigrants / float(self.population) / 100.0) + 1)
        self.starved = max(0, int(self.population - self.feed // 20.0))
        self.total_starved += self.starved
        self.average_starved += self.total_starved / float(self.population) / self.game_length
        self.population += self.immigrants - self.starved
        # Update real estate values.
        self.acre_cost = random.choice(self.land_costs)
        # Update user.
        format_params = (self.turns + 1, self.starved, self.immigrants, self.bushels_per_acre, self.rats)
        self.human.tell(self.year_intro.format(*format_params))
        # Check for plague.
        if self.turns > 1 and random.random() <= self.plague_chance / 100.0:
            self.human.tell('A horrible plague struck! Half the people died.\n')
            self.population = self.population // 2
        # Reset tracking.
        self.feed = 0
        self.seed = 0
        return False

    def do_plant(self, arguments):
        """
        Seed the land for the next harvest. (p)

        The argument is how many acres to plant. You need one bushel of grain to plant
        two acres, and one person to plant ten acres. Costs are rounded up.
        """
        # Check for an integer argument.
        try:
            acres = int(arguments)
        except ValueError:
            self.human.error('Invalid argument to plant: {!r}.'.format(arguments))
            return False
        # Check for a valid argument.
        if acres < 0:
            self.human.error("You can't plant negative acres.")
        elif acres > self.acres - self.seed:
            self.human.error("You don't have that many acres to plant.")
        elif acres > self.storage * 2:
            self.human.error("You don't have enough seed to plant that many acres.")
        elif acres + self.seed > self.population * 10:
            self.human.error("You don't have enough people to plant that much seed.")
        else:
            # Sow your seed upon the dusty earth.
            self.seed += acres
            self.storage -= int(round(acres / 2.0, 0))
        return True

    def do_sell(self, arguments):
        """
        Sell land for grain. (s)

        The argument is how many acres to sell. The average cost of land is 22 bushes
        per acre. Anything above that and you can sell high.
        """
        # Check for an integer argument.
        try:
            sell = int(arguments)
        except ValueError:
            self.human.error('Invalid argument to sell: {!r}.'.format(arguments))
            return False
        # Check for a valid argument.
        if sell < 0:
            self.human.error("You can't sell negative acres.")
        elif sell > self.acres:
            self.human.error("You don't have that many acres to sell.")
        else:
            # Get back in there and sell! Sell! Sell!
            self.acres -= sell
            self.storage += sell * self.acre_cost
        return True

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # check for impeachment
        if self.starved > self.impeachment * self.population / 100.0:
                message = 'You starved {} people in one year!!\n'.format(self.starved)
                message += 'Due to this extreme mismanagement, you have not only been impeached and\n'
                message += 'thrown out of office, but you have also been declared a national fink!!!!'
                self.human.tell(message)
                self.win_loss_draw[1] = 1
        elif self.turns == self.game_length and not self.win_loss_draw[1]:
            # show end of game summary
            land_per = self.acres // self.population
            status = "In your 10-year term of office {:.2f} percent of the population starved per year\n"
            status += "on average. That is a total of {} people died!!\n"
            status = status.format(self.average_starved, self.total_starved)
            status += '\nYou started with {} acres per person and ended with {} acres per person.\n'
            status = status.format(10, land_per)
            # check for impeachment
            if self.average_starved > 0.33 or land_per < 7:
                status += 'Due to this extreme mismanagement, you have not only been impeached and\n'
                status += 'thrown out of office, but you have also been declared a national fink!!!!'
                self.win_loss_draw[1] = 1
            elif not self.win_loss_draw[1]:
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
                    status = status.format(hate)
                    self.scores[self.human.name] = 2
                else:
                    status += "A fantastic performance!!! Charlemange, Disreli, and Jefferson combined\n"
                    status += "could not have done better!"
                    self.scores[self.human.name] = 3
            self.human.tell(status)
        return sum(self.win_loss_draw)

    def handle_options(self):
        """Handle the game options. (None)"""
        # Process the user's choices.
        super(Hamurabi, self).handle_options()
        # Set the land cost distribution.
        if self.steady_land:
            self.land_costs = (17, 18, 19, 19, 20, 20, 21, 21, 21, 22, 22, 22, 22, 23, 23, 23, 24, 24, 25)
            self.land_costs += (25, 26, 27)
        else:
            self.land_costs = tuple(range(17, 28))
        # Set the grain yield distributions.
        if self.steady_grain:
            self.grain_yields = (1, 2, 2, 3, 3, 3, 4, 4, 5)
        else:
            self.grain_yields = (1, 2, 3, 4, 5)

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        self.show_status()
        # Get the player choices.
        return self.handle_cmd(self.human.ask('What would you like to do? '))

    def set_options(self):
        """Set up the options for the game. (None)"""
        # Handle percent chance options.
        self.option_set.add_option('plague-chance', ['pc'], int, default = 15, valid = range(101),
            question = 'What should the percent chance of plague be (return for 15)? ')
        self.option_set.add_option('rat-chance', ['rc'], int, default = 40, valid = range(101),
            question = 'What should the percent chance of rats be (return for 40)? ')
        # Handle distributional options.
        self.option_set.add_option('steady-land', ['sl'],
            question = 'Should land prices be steadier? bool')
        self.option_set.add_option('steady-grain', ['sg'],
            question = 'Should grain yields be steadier? bool')

    def set_up(self):
        """Set up the game. (None)"""
        # Set non-optional parameters
        self.bushels_per_acre = 3
        self.acre_cost = random.randint(17, 26)
        # Set the game parameters.
        self.game_length = 10
        self.immigration = 20
        self.impeachment = 45
        self.start_acres = 1000
        self.start_population = 100
        self.start_rats = 200
        # Set tracking based on other parameters
        self.population = self.start_population
        self.acres = self.start_acres
        self.rats = self.start_rats
        self.game_length = self.game_length
        # Set other tracking variables
        self.starved = 0
        self.total_starved = 0
        self.average_starved = 0
        self.immigrants = 5
        self.storage = min(self.start_acres, self.population * 10) * self.bushels_per_acre - self.rats
        self.seed = 0
        self.feed = 0
        self.cats = False
        self.grain_mod = 0
        # Display the introduction.
        intro = '\nTry your hand at ruling ancient Sumeria for a {}-year term of office.'
        self.human.tell(intro.format(self.game_length))
        format_params = (self.turns + 1, self.starved, self.immigrants, self.bushels_per_acre, self.rats)
        self.human.tell(self.year_intro.format(*format_params))

    def show_status(self):
        """Show the current game status. (None)"""
        # Display general stats.
        if self.feed:
            starving = int(self.population - self.feed // 20.0)
        else:
            starving = self.population
        status = '\nThe population is now {} ({} starving).\n'.format(self.population, starving)
        status += 'The city now owns {} acres ({} planted).\n'.format(self.acres, self.seed)
        status += 'You now have {} bushels in storage.\n'.format(self.storage)
        status += 'Land is trading at {} bushels per acre.\n'.format(self.acre_cost)
        # Tell the human.
        self.human.tell(status)
