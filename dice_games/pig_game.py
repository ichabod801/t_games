"""
pig_game.py

Pig and related variants.

If you write a new kind of bot, it will not be usable unless you:
    1. Put it before the Pig class definition.
    2. Make all of the parameters integer parameters.
    3. Give a list of paramter descriptions as a class attribute.
    4. Put it in the general bots class attribute of the Pig Class.

Constants:
CREDITS: The credits for the game, progamming, and bots. (str)
RULES: The rules of Pig. (str)
SATAN_NAMES: Some names for Satan from the Bible. (str)

Classes:
PigBot: A bot for playing the game of Pig. (player.Bot)
PigBotBasePaceRace: A bot w/ min score, max behind, + when to go nuts. (PigBot)
PigBotPaceRace: A bot with  min score, modifier, and when to go nuts. (PigBot)
PigBotRolls: A Pig bot that stops after a set number of rolls. (PigBot)
PigBotScoringTurns: A Pig bot that tries to win in t scoring turns. (PigBot)
PigBotValue: A Pig bot that rolls until it exceeds a certain value. (PigBot)
Pig: A game of Pig. (game.Game)
"""


from __future__ import print_function

import random

import tgames.dice as dice
import tgames.game as game
import tgames.player as player
import tgames.utility as utility


# The credits for the game, progamming, and bots.
CREDITS = """
Game Design: Traditional
Game/Bot Programming: Craig "Ichabod" O'Brien
Bot Design: Roger Johnson, Reiner Knizia, Todd Neller, Craig O'Brien, 
    Clifton Presser
"""

# The rules of Pig.
RULES = """
On your turn, you roll one die. If you roll a one your turn is over and you
score nothing. Otherwise, you can choose to score what your rolled (ending 
your turn) or to continue rolling. If you continue to roll, any roll of a one
ends your turn without scoring. On any other roll you can stop and score the
total of all your rolls that turn.

The first player to score 100 or more wins.

OPTIONS:
six-bad: Turns end with no score on a six instead of a one.

BOT OPTIONS:
Bots can be preset bots or general bots that you must define parameters for.
Parameters for general bots are separeted by slashes. For example, you could
have 'pace-race=21/8/19'. If you do not specify all of the parameters, the
defaults will be used for later parameters. The default values can be selected
by specifying the bot type without an equals sign.

The general bots are:
    base-pace-race=: This bot tries to score at least base, stay no more than
        pace points behind the lead, and tries to win if anyone is over the
        race parameter. (alias: bpr, defaults=19/14/31)
    pace-race: This bot tries to score at least base, +/-1 for every modifer
        it's behind/ahead, and tries to win if in anyone is over the race
        parameter. (alias: pr, defaults=21/8/29)
    rolls: This bot stops after a given number of rolls. (defaults=5)
    scoring-turns: This bot tries to win in t scoring turns. (alias: t,
        defaults=4)
    value: This bot stops after reaching a given value. (defaults=25)

The preset bots are:
    stupid: A default value bot.
    easy: A default scoring-turns bot.
    medium: A default base-pace-race bot.
    hard: A default pace-race bot.
    knizia: A value bot with a value of 20.
    satan: A base-pace-race bot with parameters 6/6/6
    x: A rolls bot with 3 rolls.

The overall default is to have one medium bot.
"""

# Some names for Satan from the Bible.
SATAN_NAMES = ['Abbadon', 'Apollyon', 'Beast', 'Beelzebub', 'Belial', 'Devil', 'Lucifer', 'Satan']


class PigBot(player.Bot):
    """
    A bot for playing the game of Pig. (player.Bot)

    Overridden Methods:
    __init__
    __ask__
    __tell__
    """

    def __init__(self, taken_names = [], initial = ''):
        """
        Set the bot's name. (None)

        Parameters:
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        super(PigBot, self).__init__(taken_names, initial)
        self.scores = {}
        self.turn_score = 0

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        return random.choice(('yes', 'no'))

    def tell(self, text):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        out = text.replace('your', 'their').replace('You', self.name)
        print(out)


class PigBotBasePaceRace(PigBot):
    """
    A Pig bot with values for min score, max behind, and when to go nuts. (PigBot)

    Attributes:
    base: The the minimum turn score this bot will stop rolling on. (int)
    pace: The maximum score the bot wants to be behind the leader. (int)
    race: How close the leader can be before it tries to win. (int)
    """

    parameters = ['minimum score', 'maximum behind', 'when to go for it']

    def __init__(self, base = 19, pace = 14, race = 31, taken_names = []):
        """
        Set the bot's value. (None)

        Parameters:
        base: The the minimum turn score this bot will stop rolling on. (int)
        pace: The maximum score the bot wants to be behind the leader. (int)
        race: How close the leader can be before it tries to win. (int)
        taken_names: Names already used by a player. (list of str)
        """
        super(PigBotBasePaceRace, self).__init__(taken_names, 'b')
        self.base = base
        self.pace = pace
        self.race = race

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Calcuate values.
        turn_score = self.game.turn_score
        max_score = max(self.game.scores.values())
        my_score = self.game.scores[self.name]
        # Roll until the base is met.
        if turn_score < self.base or my_score + turn_score > 100:
            return 'roll'
        # Roll until I'm as close as the pace.
        elif self.pace < max_score - my_score:
            return 'roll'
        # Roll to win if someone is within race.
        elif max_score >= self.race:
            return 'roll'
        else:
            return 'stop'


class PigBotPaceRace(PigBot):
    """
    A Pig bot with values for min score, modifier, and when to go nuts. (PigBot)

    Attributes:
    pace: The the minimum turn score this bot will stop rolling on. (int)
    modifier: A modifier to pace based how far behind the bot is (int)
    race: How close the leader can be before it tries to win. (int)
    """

    parameters = ['minimum score', 'score modifier', 'when to go for it']

    def __init__(self, pace = 21, modifier = 8, race = 29, taken_names = []):
        """
        Set the bot's value. (None)

        Parameters:
        pace: The the minimum turn score this bot will stop rolling on. (int)
        modifier: A modifier to pace based how far behind the bot is (int)
        race: How close the leader can be before it tries to win. (int)
        taken_names: Names already used by a player. (list of str)
        """
        super(PigBotPaceRace, self).__init__(taken_names, 'p')
        self.pace = pace
        self.modifier = modifier
        self.race = race

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Calcuate values.
        turn_score = self.game.turn_score
        max_other = max([score for name, score in self.game.score.items() if name != self.name])
        my_score = self.game.scores[self.name]
        hold_value = round(self.pace + (max_other - my_score) / self.modifier, 0)
        # Roll until the base is met.
        if turn_score < hold_value or my_score + turn_score > 99:
            return 'roll'
        # Roll to win if someone is within race.
        elif max_other >= self.race:
            return 'roll'
        else:
            return 'stop'


class PigBotRolls(PigBot):
    """
    A Pig bot that stops after a set number of rolls. (PigBot)

    Attributes:
    rolls: The the number of rolls to make. (int)
    """

    parameters = ['rolls']

    def __init__(self, rolls = 5, taken_names = []):
        """
        Set the bot's value. (None)

        Parameters:
        rolls: The the number of rolls to make. (int)
        taken_names: Names already used by a player. (list of str)
        """
        super(PigBotRolls, self).__init__(taken_names, 'r')
        self.max_rolls = rolls
        self.rolls = 0

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Track rolls.
        self.rolls += 1
        # Calcuate values.
        turn_score = self.game.turn_score
        my_score = self.game.scores[self.name]
        # Stop if the number of rolls is met.
        if self.rolls == self.max_rolls or my_score + turn_score > 99:
            self.rolls = 0
            return 'stop'
        else:
            return 'roll'


class PigBotScoringTurns(PigBot):
    """
    A Pig bot that tries to win in t scoring turns. (PigBot)

    For example, with scoring_turns = 4. To start, they will try to score 
    100 / 4 = 25 points. Say that the first time they score they score 28
    points. The next time they will try to score (100 - 28) / (4 - 1) = 24 
    points. If they then score 26 points, they will try to score
    (100 - 28 - 26) / (4 - 2) = 23 points.

    Attributes:
    scoring_turns: The number of scoring turns to try to win in. (int)
    """

    parameters = ['scoring turns']

    def __init__(self, scoring_turns = 4, taken_names = []):
        """
        Set the bot's scoring_turns. (None)

        Parameters:
        scoring_turns: The number of scoring turns to try to win in. (int)
        taken_names: Names already used by a player. (list of str)
        """
        super(PigBotScoringTurns, self).__init__(taken_names, 't')
        self.scoring_turns = scoring_turns

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Calculate stop value.
        hold_at = (100 - self.game.scores[self.name]) // self.scoring_turns
        # Stop if the hold value is met or exceeded.
        if self.game.turn_score < hold_at:
            return 'roll'
        else:
            self.scoring_turns -= 1
            return 'stop'


class PigBotValue(PigBot):
    """
    A Pig bot that rolls until it exceeds a certain value. (PigBot)

    Attributes:
    value: The the minimum turn score this bot will stop rolling on. (int)
    """

    parameters = ['value']

    def __init__(self, value = 25, taken_names = []):
        """
        Set the bot's value. (None)

        Parameters:
        value: The the minimum turn score this bot will stop rolling on. (int)
        taken_names: Names already used by a player. (list of str)
        """
        super(PigBotValue, self).__init__(taken_names, 'v')
        self.value = value

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        # Calcuate values.
        turn_score = self.game.turn_score
        my_score = self.game.scores[self.name]
        # Stop if the value is met or exceeded.
        if self.game.turn_score < self.value or my_score + turn_score > 99:
            return 'roll'
        else:
            return 'stop'


class Pig(game.Game):
    """
    A game of pig. (Game)

    Attributes:
    die: The die that is rolled. (dice.Die)
    turn_score: The current player's turn score. (int)

    Methods:
    ask_options: Get options from the user. (None)
    parse_options: Parse options from the play command. (None)

    Overridden Methods:
    game_over
    handle_options
    set_up
    player_turn
    """

    name = 'Pig'
    categories = ['Dice Games']
    general_bots = {'value': PigBotValue, 'base-pace-race': PigBotBasePaceRace, 'bpr': PigBotBasePaceRace,
        'scoring-turns': PigBotScoringTurns, 't': PigBotScoringTurns, 'pace-race': PigBotPaceRace,
        'pr': PigBotPaceRace, 'rolls': PigBotRolls}
    preset_bots = {'knizia': (PigBotValue, (20,)),'stupid': (PigBotValue, ()), 'easy': (PigBotScoringTurns, ()),
        'medium': (PigBotBasePaceRace, ()), 'hard': (PigBotPaceRace()), 'satan': (PigBotBasePaceRace, (6, 6, 6)),
        'x': (PigBotRolls, (3,))}
    for bot_type, bot_class in general_bots.items():
        preset_bots[bot_type] = (bot_class, ())

    def ask_options(self):
        """Get options from the user. (None)"""
        if self.human.ask('Would you like to change the options? ').lower() in utility.YES:
            # Six is the turn ender.
            if self.human.ask('Should six be the number that ends the turn? ').lower() in utility.YES:
                self.bad = 6
            # Add bots until the user doesn't want any more.
            while self.human.ask('Would you like to add a bot? ').lower() in utility.YES:
                # Get the bot type.
                bot_type = self.human.ask('What type of bot would you like to add? ').lower()
                # Get the parameters for general bots.
                if bot_type in self.general_bots:
                    bot_class = self.general_bots[bot_type]
                    parameters = []
                    try:
                        for parameter in bot_class.parameters:
                            text = 'What value do you want for the {} parameter? '.format(parameter)
                            parameters.append(int(self.human.ask(text)))
                    except ValueError:
                        self.human.tell('Bot parameters should integers.')
                    self.players.append(bot_class(*parameters, taken_names = taken_names))
                    taken_names.append(self.players[-1].name)
                # Add in preset bots.
                elif bot_type in self.preset_bots:
                    bot_class, parameters = self.preset_bots[bot_type]
                    self.players.append(bot_class(*parameters, taken_names = taken_names))
                    if word = 'satan':
                        name = random.choice([name for name in SATAN_NAMES if name not in taken_names])
                        self.players[-1].name = name
                    taken_names.append(self.players[-1].name)
                # Give an infomative warning.
                else:
                    self.human.tell("I don't know that kind of bot.")
                    known_bots = sorted(self.general_bots.keys(), self.present_bots.keys())
                    self.human.tell('The bots I know are ' + ', '.join(known_bots))

    def clean_up(self):
        """Set the loser to go first next round. (None)"""
        self.players.sort(key = lambda player: self.scores[player.name])

    def game_over(self):
        """Check a score being over 100. (bool)"""
        # Check for win.
        if max(self.scores.values()) > 99:
            # Update win/loss/draw.
            human_score = self.scores[self.human.name]
            for name, score in self.scores.items():
                if name != self.human.name:
                    if score > human_score:
                        self.win_loss_draw[1] += 1
                    elif score < human_score:
                        self.win_loss_draw[0] += 1
                    else:
                        self.win_loss_draw[2] += 1
                # Declare the winner when found.
                if score > 99:
                    self.human.tell('{} won with {} points.'.format(name, score))
            return True

    def handle_options(self):
        """Handle game options and set up players. (None)"""
        # Set the defaults.
        self.players = [self.human]
        self.bad = 1
        # Prep the option loop.
        taken_names = [self.human.name]
        if self.raw_options:
            self.parse_options()
        else:
            self.ask_options()
        # If no optional bots, default to a basic value bot.
        if self.players == [self.human]:
            self.players.append(PigBotValue(taken_names = [self.human.name]))
        # Shuffle the players.
        random.shuffle(self.players)

    def parse_options(self):
        """Parse options from the play command. (None)"""
        for word in self.raw_options().lower().split():
            # Six is the turn ender.
            if word == 'six-bad':
                self.bad = 6
            # Check for preset bots.
            elif word in self.preset_bots:
                bot_class, parameters = self.preset_bots[word]
                self.players.append(bot_class(*parameters, taken_names = taken_names))
                if word = 'satan':
                    new_name = random.choice([name for name in SATAN_NAMES if name not in taken_names])
                    self.players[-1].name = new_name
                taken_names.append(self.palyers[-1].name)
            # Check for general bots.
            elif '=' in word:
                bot_type, values = word.split('=')
                if bot_type in self.general_bots:
                    try:
                        parameters = [int(value) for value in word.split('/')]
                        new_bot = self.general_bots[bot_type](*parameters, taken_names = taken_names)
                        self.players.append(new_bot)
                        taken_names.append(new_bot.name)
                    except ValueError, TypeError:
                        self.human.tell('Invalid {} bot specification.'.format(bot_type))
                else:
                    # Warn about unknown bot types.
                    self.human.tell("I don't know the {} bot.".format(bot_type))
            else:
                # Warn about unknown options.
                self.human.tell("I don't recognize the {} option.".format(word))

    def set_up(self):
        """Set up the game. (None)"""
        self.die = dice.Die()

    def player_turn(self, player):
        """
        Have one player roll until terminal number or they choose to stop. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        self.turn_score = 0
        while True:
            roll = self.die.roll()
            if roll == 1:
                player.tell('You rolled a 1, your turn is over.')
                break
            else:
                self.turn_score += roll
                player.tell('You rolled a {}, your turn score is {}.'.format(roll, self.turn_score))
            move = player.ask('Would you like to roll or stop? ')
            if move.lower() in ('s', 'stop', 'whoa'):
                self.scores[player.name] += self.turn_score
                break
        player.tell("{}'s score is now {}".format(player.name, self.scores[player.name]))
        print()


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    pig = Pig(player.Player(name), '')
    pig.play()