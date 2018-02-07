"""
pig_game.py

Pig.

If you write a new kind of bot, it will not be usable unless you:
    1. Put it before the Pig class definition.
    2. Make all of the parameters integer parameters.
    3. Give a list of paramter descriptions as a class attribute.
    4. Put it in the general bots class attribute of the Pig Class.

!! Piglet: coin tosses to 10 points, heads = 1, tails = turn end.
    Dan Fendel, Diane Resek, Lynne Alper, and Sherry Fraser.
!! Two die pig, seven ends turn.
!! New roll-n bot: rolls n times and stops, ignoring ones.
    So if the third roll is 1, the next turn he'll roll twice and stop.

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
even-turns: Everyone gets the same number of turns.
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
        return random.choice(('roll', 'stop'))

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
        if (base, pace, race) == (6, 6, 6):
            while True:
                name = random.choice(SATAN_NAMES)
                if name not in taken_names:
                    self.name = name
                    break
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
        # Last chance:
        if max_score > 99 and my_score + turn_score <= max_score:
            return 'roll'
        # Stop if you've won.
        if my_score + turn_score > 99:
            return 'stop'
        # Roll until the base is met.
        elif turn_score < self.base:
            return 'roll'
        # Roll until I'm as close as the pace.
        elif self.pace < max_score - my_score - turn_score:
            return 'roll'
        # Roll to win if someone is within race.
        elif 100 - max_score <= self.race:
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
        max_other = max([score for name, score in self.game.scores.items() if name != self.name])
        my_score = self.game.scores[self.name]
        hold_value = round(self.pace + (max_other - my_score) / self.modifier, 0)
        # Last chance:
        if max_other > 99 and my_score + turn_score <= max_other:
            return 'roll'
        # Stop if you've won.
        elif my_score + turn_score > 99:
            return 'stop'
        # Roll until the base is met.
        elif turn_score < hold_value:
            return 'roll'
        # Roll to win if someone is within race.
        elif 100 - max_other <= self.race:
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
        max_score = max(self.game.scores.values())
        # Last chance:
        if max_score > 99 and my_score + turn_score <= max_score:
            return 'roll'
        # Stop if you've won.
        elif my_score + turn_score > 99:
            return 'stop'
        # Stop if the number of rolls is met.
        if self.rolls == self.max_rolls:
            self.rolls = 0
            return 'stop'
        else:
            return 'roll'

    def tell(self, text):
        """
        Give information to the player. (None)

        Parameters:
        text: The information from the game. (str)
        """
        super(PigBotRolls, self).tell(text)
        # Catch turn endings.
        if 'turn is over' in text:
            self.rolls = 0


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
        # Calculate values.
        my_score = self.game.scores[self.name]
        turn_score = self.game.turn_score
        max_score = max(self.game.scores.values())
        hold_at = (100 - my_score) // self.scoring_turns
        # Last chance:
        if max_score > 99 and my_score + turn_score <= max_score:
            return 'roll'
        # Stop if you've won.
        elif my_score + turn_score > 99:
            return 'stop'
        # Stop if the hold value is met or exceeded.
        elif self.game.turn_score < hold_at:
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
        max_score = max(self.game.scores.values())
        # Last chance:
        if max_score > 99 and my_score + turn_score <= max_score:
            return 'roll'
        # Stop if you've won.
        elif my_score + turn_score > 99:
            return 'stop'
        # Stop if the value is met or exceeded.
        elif self.game.turn_score < self.value:
            return 'roll'
        else:
            return 'stop'


class Pig(game.Game):
    """
    A game of pig. (Game)

    Class Attributes:
    general_bots: The bot classes, for options with =. (dict of str: PigBot)
    present_bots: The bots with preset parameters. (dict of str: tuple)

    Attributes:
    die: The die that is rolled. (dice.Die)
    turn_score: The current player's turn score. (int)

    Methods:
    ask_options: Get options from the user. (None)
    do_scores: Show the current scores. (None)
    parse_options: Parse options from the play command. (None)

    Overridden Methods:
    clean_up
    game_over
    handle_options
    set_up
    player_action
    """

    name = 'Pig'
    categories = ['Dice Games', 'Jeopardy Games']
    credits = CREDITS
    bot_classes = {'value': PigBotValue, 'base-pace-race': PigBotBasePaceRace, 
        'scoring-turns': PigBotScoringTurns, 'pace-race': PigBotPaceRace, 'rolls': PigBotRolls}
    num_options = 3
    rules = RULES

    def clean_up(self):
        """Set the loser to go first next round. (None)"""
        self.players.sort(key = lambda player: self.scores[player.name])

    def do_gipf(self, arguments):
        """
        Gipf

        Parameters:
        arguments: The name of the game to gipf to. (str)
        """
        game, losses = self.gipf_check(arguments, ('battleships', 'wumpus', 'solitaire dice'))
        # Battleships.
        if game == 'battleships':
            if not losses:
                self.turn_score += 2
                self.human.tell('You rolled a 2. Your turn score is now {}.'.format(self.turn_score))
            go = True
        # Hunt the Wumpus
        elif game == 'wumpus':
            if not losses:
                roll = self.die.roll()
                question = 'Your next roll will be a {}. Would you like to roll or stop? '
                move = self.human.ask(question.format(roll))
                move = move.strip().lower()
                if move in ('s', 'stop', 'whoa'):
                    self.scores[self.human.name] += self.turn_score
                    go = False
                elif move in ('r', 'roll', 'go'):
                    if roll == self.bad:
                        go = False
                    else:
                        self.turn_score += roll
                        self.human.tell('Your turn score is {}.'.format(self.turn_score))
                        go = True
            else:
                go = True
        elif game == 'solitaire dice':
            if not losses:
                first = self.die.roll()
                while True:
                    second = self.die.roll()
                    if second != first:
                        break
                prompt = 'Do you want to roll a {} or a {}? '.format(first, second)
                choice = self.human.ask_int(prompt, valid = [first, second], cmd = False)
                self.turn_score += choice
                message = 'You rolled a {}. Your turn score is now {}.'
                self.human.tell(message.format(choice, self.turn_score))
                go = True
        else:
            self.human.error('Say what?')
            go = True
        return go

    def do_scores(self, arguments):
        """
        Show the current scores. (None)

        Parameters:
        arguments: The (ignored) arguments to the score command. (str)
        """
        scores = sorted([(score, name) for name, score in self.scores.items()], reverse = True)
        self.human.tell()
        for score, name in scores:
            self.human.tell('{}: {}'.format(name, score))
        self.human.tell()
        return True

    def game_over(self):
        """Check a score being over 100. (bool)"""
        # Check for win.
        if max(self.scores.values()) > 99:
            # Check for even turns option.
            if self.even_turns and self.turns % len(self.players):
                return False
            # Update win/loss/draw.
            human_score = self.scores[self.human.name]
            winning_score = max(self.scores.values())
            for name, score in self.scores.items():
                if name != self.human.name:
                    if score > human_score:
                        self.win_loss_draw[1] += 1
                    elif score < human_score:
                        self.win_loss_draw[0] += 1
                    else:
                        self.win_loss_draw[2] += 1
                # Declare the winner when found.
                if score == winning_score:
                    self.human.tell('{} won with {} points.'.format(name, score))
            return True

    def handle_options(self):
        """Handle game options and set up players. (None)"""
        self.option_set.handle_settings(self.raw_options)
        random.shuffle(self.players)

    def player_action(self, player):
        """
        Have one player roll until terminal number or they choose to stop. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        if self.turn_score:
            move = player.ask('Would you like to roll or stop? ')
        else:
            move = 'roll'
        if move.lower() in ('s', 'stop', 'whoa'):
            self.scores[player.name] += self.turn_score
            go = False
        elif move.lower() in ('r', 'roll', 'go'):
            roll = self.die.roll()
            if roll == self.bad:
                player.tell('You rolled a {}, your turn is over.'.format(self.bad))
                go = False
            else:
                self.turn_score += roll
                player.tell('You rolled a {}, your turn score is {}'.format(roll, self.turn_score))
                go = True
        else:
            go = self.handle_cmd(move)
        if not go:
            player.tell("{}'s score is now {}.\n".format(player.name, self.scores[player.name]))
            self.turn_score = 0
        return go

    def set_options(self):
        """Set up the game options. (None)"""
        # Game rule options.
        self.option_set.add_option(name = 'six-bad', target = 'bad', value = 6, default = 1,
            question = 'Should six be the number that ends the turn? bool')
        self.option_set.add_option(name = 'even-turns', target = 'even_turns',
            question = 'Should each player get the same number of turns? bool')
        # Parameterized bots.
        self.option_set.add_option(name = 'value', action = 'bot', default = None, converter = int, 
            check = lambda params: len(params) <= 1 and max(params) <= 100)
        self.option_set.add_option(name = 'base-pace-race', aliases = ['bpr'], action = 'bot', 
            default = None, check = lambda params: len(params) <= 3 and max(params) <= 100, 
            converter = int)
        self.option_set.add_option(name = 'scoring-turns', aliases = ['t'], action = 'bot', default = None,
            check = lambda params: len(params) <= 1 and max(params) <= 100, converter = int)
        self.option_set.add_option(name = 'pace-race', aliases = ['pr'], action = 'bot', default = None,
            check = lambda params: len(params) <= 2 and max(params) <= 100, converter = int)
        self.option_set.add_option(name = 'rolls', action = 'bot', default = None,
            check = lambda params: len(params) <= 1 and max(params) <= 100, converter = int)
        # Pre-set bots.
        self.option_set.add_option(name = 'stupid', action = 'bot', target = 'value', value = (), 
            default = None)
        self.option_set.add_option(name = 'easy', action = 'bot', target = 'scoring-turns', value = (), 
            default = None)
        self.option_set.add_option(name = 'medium', action = 'bot', target = 'base-pace-race', value = (), 
            default = None)
        self.option_set.add_option(name = 'hard', action = 'bot', target = 'pace-race', value = (), 
            default = None)
        self.option_set.add_option(name = 'knizia', action = 'bot', target = 'value', value = (20,), 
            default = None)
        self.option_set.add_option(name = 'satan', action = 'bot', target = 'base-pace-race', 
            value = (6, 6, 6), default = None)
        self.option_set.add_option(name = 'x', action = 'bot', target = 'rolls', value = (3,), 
            default = None)
        # Default bots.
        self.option_set.default_bots = [(PigBotBasePaceRace, ())]

    def set_up(self):
        """Set up the game. (None)"""
        self.die = dice.Die()
        self.turn_score = 0


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    pig = Pig(player.Player(name), '')
    pig.play()