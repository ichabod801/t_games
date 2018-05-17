"""
craps_game.py

A game of Craps.

To Do:
comment check
more options
more bots
    remove bots with 0 dollars.
    max_players option

Constants:
BUY_ODDS: The odds for buy bets. (dict of int: tuple of int)
CREDITS: The credits for Craps. (str)
PLACE_ODDS: The odds for place bets. (dict of int: tuple of int)

Classes:
Craps: A game of Craps. (game.Game)
CrapsBot: A bot to play Craps against. (player.Bot)
PoliteBot: A bot that roots for the shooter. (CrapsBot)
CrapsBet: A bet in a game of craps. (object)
HardWayBet: A bet that a number will come up as a pair first. (CrapsBet)
OddsBet: An odds bet on a do/don't pass/come bet. (CrapsBet)
PassBet: A bet that the shooter will win. (CrapsBet)
ComeBet: A pass-style bet after the come out roll. (PassBet)
DontComeBet: A don't-pass-style bet after the come out roll. (ComeBet)
DontPassBet: A bet that the shooter will lose. (PassBet)
PlaceBet: A bet that a particular number will come up before a 7. (CrapsBet)
BuyBet: A place bet with better odds and a commission. (PlaceBet)
LayBet: A buy bet that a seven will come before a given number. (BuyBet)
PropositionBet: A single-roll bet on one or more specific numbers. (CrapsBet)
"""


from __future__ import division

import math
import re

import tgames.dice as dice
import tgames.game as game
import tgames.player as player

# The odds for buy bets.
BUY_ODDS = {4: (2, 1), 5: (3, 2), 6: (6, 5), 8: (6, 5), 9: (3, 2), 10: (2, 1)}

# The credits for Craps.
CREDITS = """
Game Design: Barnard Xavier Phillippe de Marigny de Mandeville
Game Programming: Craig "Ichabod" O'Brien
"""

# The odds for place bets.
PLACE_ODDS = {4: (9, 5), 5: (7, 5), 6: (7, 6), 8: (7, 6), 9: (7, 5), 10: (9, 5)}


class Craps(game.Game):
    """
    A game of Craps. (game.Game)

    Basic play is that every one gets a chance to bet, then the shooter throws,
    and then bets are resolved. Basic program flow is player_action gets the bets,
    handles everything else as a command. Done command checks for shooter, if so 
    rolls and resolves bets. Each bet has it's own resolution method, which is 
    found with getattr using the internal bet name from the bet_aliases attribute.

    Attributes:
    bets: The bets the players have made this round. (dict of str: list)
    dice: The dice that get rolled. (dice.Pool)
    limit: The maximum bet that can be made. (int)
    max_payout: The multiple of the limit that can be paid out on one bet. (int)
    point: The point to be made, or zero if no point yet. (int)
    shooter_index: Index of the current shooter in self.players. (int)
    stake: How much money the players start with. (int)

    Class Attributes:
    odds_multiples: The multiples of the max bets for odds bets. (dict)

    Methods:
    do_bets: Show the player's bets. (bool)
    do_done: Finish the player's turn. (bool)
    do_remove: Remove bets that are in play. (bool)
    do_roll: Finish the player's turn and roll. (bool)
    get_wager: Get the ammount to wager on the bet. (int)
    remove_bet: Remove a bet from play. (None)
    resolve_bets: Resolve player bets after a roll. (None)

    Overridden Methods:
    __str__
    default
    do_quit
    game_over
    player_action
    set_options
    set_up
    """

    aliases = {'b': 'bets', 'd': 'done', 'r': 'roll'}
    categories = ['Gambling Games', 'Dice Games']
    name = 'Craps'
    num_options = 3
    odds_multiples = {4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3}

    def __str__(self):
        """Human readable text representation. (str)"""
        player = self.players[self.player_index]
        # Display shooter and point.
        if self.point:
            point_text = 'point = {}'.format(self.point)
        else:
            point_text = 'off'
        lines = ['\nThe shooter is {} ({}).'.format(self.players[self.shooter_index].name, point_text)]
        # Display outstanding bets.
        s = ['s', ''][len(self.bets[player.name]) == 1]
        bet_total = sum(bet.wager for bet in self.bets[player.name])
        message = 'You have {} bet{} in play totalling {} dollars.'
        lines.append(message.format(len(self.bets[player.name]), s, bet_total))
        # Display remaining money.
        lines.append('You have {} dollars remaining to bet.\n'.format(self.scores[player.name]))
        return '\n'.join(lines)

    def default(self, line):
        """
        Handle unknown commands by assuming they are bets. (bool)

        Parameters:
        line: The command entered by the user. (str)
        """
        # Gather useful data.
        player = self.players[self.player_index]
        words = line.lower().split()
        # Check for odds bets.
        if 'odds' in words:
            # Get the base bet and the number.
            odds_index = words.index('odds')
            base_bet = ' '.join(words[:odds_index])
            if odds_index == len(words) - 1:
                number = self.point
            elif words[-1].isdigit():
                number = int(words[-1])
            else:
                player.error('That is an invalid odds bet.')
                return True
            # Find valid base bet.
            possibles = [b for b in self.bets[player.name] if b.match(base_bet, number) and not b.odds_bet]
            if possibles:
                # Make the odds bet.
                bet = OddsBet(player, base_bet + ' odds', number, possibles[0])
                possibles[0].odds_bet = bet
            else:
                # Error if no valid base bet.
                player.error('There is no such base bet to make an odds bet on.')
                return True
        # Check for proposition bets.
        elif words[0] in ('prop', 'proposition'):
            bet = PropositionBet(player, ' '.join(words[1:]))
        # Check for other bets.
        else:
            # Parse the text
            if words[-1].isdigit():
                raw_bet = ' '.join(words[:-1])
                number = int(words[-1])
            else:
                raw_bet = line.lower()
                number = 0
            # Handle valid bets.
            if raw_bet in self.bet_classes:
                bet = self.bet_classes[raw_bet](player, raw_bet, number)
            # Handle invalid bets.
            else:
                player.error('I do not recognize that bet ({!r})'.format(line))
                return True
        # Validate bets.
        errors = bet.validate()
        if errors:
            player.error(errors)
        else:
            # Get wagers for valid bets.
            self.get_wager(bet)
        # Add bets with valid wagers.
        if bet.wager:
            self.bets[player.name].append(bet)
        return True

    def do_bets(self, argument):
        """
        Show the player's bets. (bool)

        Parameters:
        argument: The (ignored) argument to the done command. (str)
        """
        player = self.players[self.player_index]
        player.tell('\n---Your Bets---\n')
        for bet in self.bets[player.name]:
            player.tell('{} bet for {} dollars.'.format(bet, bet.wager).capitalize())
        player.tell()
        return True

    def do_done(self, argument):
        """
        Finish the player's turn. (bool)

        Parameters:
        argument: The argument to the done command. (str)
        """
        player = self.players[self.player_index]
        # Check for shooter's turn.
        if self.player_index == self.shooter_index:
            # Check for a pass or don't pass bet:
            bets = [bet.match_text for bet in self.bets[player.name]]
            if 'pass' not in bets and "don't pass" not in bets:
                player.tell("You must have a pass or a don't pass bet when you are the shooter.")
                return True
            # Have them roll the dice.
            if argument.lower() not in ('r', 'roll'):
                player.ask('You are the shooter. Press enter to roll the dice: ')
            self.dice.roll()
            self.human.tell('\n{} rolled {}.'.format(player.name, self.dice))
            self.resolve_bets()
            self.human.ask('Press enter to continue: ')
            self.human.tell()
        return False

    def do_remove(self, argument):
        """
        Remove bets. (bool)

        Parameters;
        argument: The argument to the remove command. (str)
        """
        player = self.players[self.player_index]
        # Get the removable bets.
        removable = [bet for bet in self.bets[player.name] if bet.removable]
        # Check that there are removable bets.
        if not removable:
            player.tell('You have not made any bets that can be removed.')
        # Check for remove all.
        elif argument.lower() in ('a', 'all'):
            for bet in removable:
                player.tell('Removing your {} bet for {} dollars.'.format(bet, bet.wager))
                self.remove_bet(bet)
        else:
            # Show the bets.
            player.tell('\n---Removable Bets---\n')
            row_text = '{}: {} bet for {} dollars.'
            for bet_index, bet in enumerate(removable):
                player.tell(row_text.format(bet_index, bet, bet.wager))
            # Get the bet to remove.
            query = '\nWhich bet would you like to remove (-1 for none)? '
            choice = player.ask_int(query, low = -1, high = len(removable) - 1)
            # Remove or not as chosen.
            if choice == -1:
                pass
            else:
                bet = removable[choice]
                player.tell('Removing your {} bet for {} dollars.'.format(bet, bet.wager))
                self.remove_bet(bet)
        return True

    def do_roll(self, argument):
        """
        Finish the player's turn and roll. (bool)

        Parameters:
        argument: The argument to the done command. (str)
        """
        return self.do_done('r')

    def do_quit(self, argument):
        """
        Stop playing craps. (bool)

        Parameters:
        argument: The (ignored) argument to the done command. (str)
        """
        self.scores[self.human.name] -= self.stake
        if self.scores[self.human.name] > 0:
            self.win_loss_draw[0] = 1
        if self.scores[self.human.name] > 0:
            self.win_loss_draw[1] = 1
        else:
            self.win_loss_draw[2] = 1
        self.force_end = True

    def game_over(self):
        """Check for the end of the game. (bool)"""
        if self.scores[self.human.name] == 0 and not self.bets[self.human.name]:
            self.win_loss_draw[1] = 1
            self.scores[self.human.name] -= self.stake
            return True
        else:
            return False

    def get_wager(self, bet):
        """
        Get the ammount to wager on the bet. (int)

        Parameters:
        bet: The bet to get the wager for. (CrapsBet)
        """
        max_bet = bet.max_bet(self.limit, self.limit * self.max_payout)
        player_max = int(self.scores[bet.player.name] / (1 + bet.commission))
        max_bet = min(player_max, max_bet)
        if max_bet:
            query = 'How much would you like to bet (max = {})? '.format(max_bet)
            wager = bet.player.ask_int(query, low = 1, high = max_bet, cmd = False)
        else:
            wager = 0
            bet.player.error('That is not a valid bet at this time.')
        bet.set_wager(wager)
        self.scores[bet.player.name] -= wager
        if bet.commission:
            commission = int(math.ceil(wager * bet.commission))
            bet.player.tell('The bank charges a {} dollar commission on that bet.'.format(commission))
            self.scores[bet.player.name] -= commission

    def player_action(self, player):
        """
        Handle any actions by the current player. (bool)

        Parameters:
        player: The current player. (player.Player)
        """
        # Display the game status.
        player.tell(str(self))
        # Get the bet or other command.
        raw_bet = player.ask('What kind of bet would you like to make? ')
        if not raw_bet.strip():
            raw_bet = 'done'
        return self.handle_cmd(raw_bet)

    def remove_bet(self, bet):
        """
        Remove a bet from play. (None)

        Parameters:
        bet: The bet to remove. (CrapsBet)
        """
        player_name = bet.player.name
        bets = self.bets[player_name]
        self.scores[player_name] += bet.wager
        self.scores[player_name] += int(math.ceil(bet.wager * bet.commission))
        bets.remove(bet)
        if bet.odds_bet:
            self.remove_bet(bet.odds_bet)

    def resolve_bets(self):
        """Resolve player bets after a roll. (None)"""
        # Loop through the player bets.
        for player in self.players:
            for bet in self.bets[player.name][:]: # loop through copy to allow changes.
                payout = bet.resolve(self.dice)
                if payout > 0:
                    message = '{} won {} dollars on their {}.'
                    self.human.tell(message.format(player.name, payout, bet))
                    self.scores[player.name] += payout + bet.wager
                    self.bets[player.name].remove(bet)
                elif payout < 0:
                    message = '{} lost {} dollars on their {}.'
                    self.human.tell(message.format(player.name, bet.wager, bet))
                    self.bets[player.name].remove(bet)
        # Set the point and shooter.
        if self.point:
            if sum(self.dice) == self.point:
                self.point = 0
            elif sum(self.dice) == 7:
                self.point = 0
                self.shooter_index = (self.shooter_index + 1) % len(self.players)
                self.player_index = self.shooter_index
        elif sum(self.dice) in (4, 5, 6, 8, 9, 10):
            self.point = sum(self.dice)

    def set_options(self):
        """Set the game options. (None)"""
        # Betting options.
        self.option_set.add_option('stake', [], int, 100, check = lambda bucks: bucks > 0,
            question = 'How much money would you like to start with (return for 100)? ')
        self.option_set.add_option('limit', [], int, 8, check = lambda bucks: 0 < bucks,
            question = 'What should the maximum bet be (return for 8)? ')
        self.option_set.add_option('max-payout', [], int, 3, check = lambda times: 1 <= times,
            question = 'What multiple of the maximum bet should the maximum payout be (return for 3)? ')

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the players.
        self.players = [CrapsBot([self.human.name]), self.human]
        for player in self.players[:-1]:
            player.game = self
        # Set up the tracking variables.
        self.scores = {player.name: self.stake for player in self.players}
        self.bets = {player.name: [] for player in self.players}
        self.shooter_index = len(self.players) - 1
        self.point = 0
        # Set up the dice.
        self.dice = dice.Pool()
        # Set up the bets.
        self.bet_classes = {}
        self.classes = [CrapsBet]
        while self.classes:
            cls = self.classes.pop()
            self.bet_classes[cls.match_text] = cls
            for alias in cls.aliases:
                self.bet_classes[alias] = cls
            self.classes.extend(cls.__subclasses__())


class CrapsBot(player.Bot):
    """
    A bot to play Craps with. (player.Bot)

    Class Attributes:
    bet_type: The main type of bet to make. (str)
    max_re: A regex for getting the max bet from a question. (SRE_Pattern)

    Overridden Methods:
    ask
    ask_int
    tell
    """

    # The main type of bet to make.
    bet_type = "don't pass"
    # A regex for getting the max bet from a question.
    max_re = re.compile('\d+')

    def ask(self, prompt):
        """
        Ask the bot a question. (str)

        Parameters:
        prompt: The queston to ask. (str)
        """
        if prompt.startswith('What kind of bet'):
            # Make pass or don't pass bets, and then odds bets on them.
            my_bets = self.game.bets[self.name]
            if not self.game.scores[self.name]:
                return 'Done'
            elif not my_bets:
                return self.bet_type
            elif my_bets and self.game.point and not my_bets[0].odds_bet:
                return "{} odds {}".format(, self.bet_type, my_bets[0].number)
            else:
                return 'done'
        elif prompt.startswith('You are the shooter.'):
            return 'CrapsBot needs a new pair of shoes!'
        else:
            raise player.BotError('Unexpected question to CrapsBot: {!r}'.format(prompt))

    def ask_int(self, *args, **kwargs):
        """
        Ask the bot for an integer. (int)

        Parameters:
        the parameters are ingored.
        """
        max_bet = int(self.max_re.search(args[0]).group())
        wager = min(max_bet, self.game.scores[self.name])
        if self.game.bets[self.name]:
            odds = 'odds '
        else:
            odds = ''
        message = "{} made a {} {}bet for {} bucks."
        self.game.human.tell(message.format(self.name, self.bet_type, odds, wager))
        return wager

    def tell(self, *args, **kwargs):
        """
        Ask the bot for an integer. (int)

        Parameters:
        the parameters are ingored.
        """
        pass


class PoliteBot(CrapsBot):
    """A bot that roots for the shooter. (CrapsBot)"""

    bet_type = 'pass'


class CrapsBet(object):
    """
    A bet in a game of craps. (object)

    Class Attributes:
    aliases: Other names for the bet. (list of str)
    commission: The commission the bank takes on the bet. (float)
    match_text: The standard name for the bet. (str)
    removable: A flag for being able to take down the bet. (bool)

    Methods:
    match: Does the bet match the given user text? (bool)
    max_bet: Calcualte the maximum wager. (int)
    resolve: Determine if the bet won or lost. (int)
    set_wager: Set the bet's wager and calculate it's payout. (None)
    validate: Check that the bet is valid. (str)

    Overridden Methods:
    __init__
    __repr__
    __str__
    """

    aliases = []
    commission = 0
    match_text = 'not a bet'
    removable = False

    def __init__(self, player, raw_text, number):
        """
        Set up the bet's attributes. (None)

        Parameters:
        player: The player who made the bet. (player.Player)
        raw_text: The user's name for the bet. (str)
        number: The number associated with the bet. (int)
        """
        # Set the specified attributes.
        self.player = player
        self.raw_text = raw_text.capitalize()
        self.number = number
        # Set the calculated attributes.
        self.game = self.player.game
        # Set the default attributes.
        self.ammo = False
        self.odds_bet = None
        self.wager = 0

    def __repr__(self):
        """Computer readable text representation. (str)"""
        text = '<{}'.format(self.__class__.__name__)
        if self.number:
            text += ' on {}'.format(self.number)
        return text + ' for {} bucks>'.format(self.wager)

    def __str__(self):
        """Human readable text representation. (str)"""
        text = self.raw_text.lower() + ' bet'
        if self.number:
            text += ' on {}'.format(self.number)
        return text

    def match(self, text, number = 0):
        """
        Does the bet match the given user text? (bool)

        Paramters:
        text: A user identifier for a bet. (str)
        number: The number the bet is on. (int)
        """
        return (text.lower() == self.match_text or text.lower() in self.aliases) and self.number == number

    def max_bet(self, limit, max_payout):
        """
        Calcualte the maximum wager. (int)

        Parameters:
        limit: The maximum bet in the game. (int)
        max_payout: The maximum payout in the game. (int)
        """
        return limit

    def resolve(self, roll):
        """
        Determine if the bet won or lost. (int)

        Positive return is a win, negative is a loss, zero is working bet.

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        return -self.wager

    def set_wager(self, wager):
        """
        Set the bet's wager and calculate it's payout. (None)

        Parameters:
        wager: The amount of money bet. (int)
        """
        self.wager = wager
        self.payout = wager

    def validate(self):
        """Check that the bet is valid. (str)"""
        return ''


class HardWayBet(CrapsBet):
    """
    A bet that an even number will come up as pair before otherwise. (CrapsBet)

    Overriden Methods:
    max_bet
    resolve
    set_wager
    validate
    """

    aliases = ['hard', 'hard ways']
    match_text = 'hard way'
    removable = True

    def max_bet(self, limit, max_payout):
        """
        Calculate the maximum odds wager. (int)

        Parameters:
        odds_multiples: The multipliers for odds bets. (dict of int: int)
        """
        if self.number in (4, 10):
            max_bet = int(max_payout / 7)
        else:
            max_bet = int(max_payout / 9)
        return max(1, max_bet)

    def resolve(self, roll):
        """
        Determine if the bet won or lost. (int)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        if sum(roll) == self.number:
            if roll.values[0] == roll.values[1]:
                result = self.payout
            else:
                result = self.wager * -1
        else:
            result = 0
        return result

    def set_wager(self, wager):
        """
        Set the bet's wager and calculate it's payout. (None)

        Parameters:
        wager: The amount of money bet. (int)
        """
        self.wager = wager
        if self.number in (4, 10):
            self.payout = 7 * wager
        else:
            self.payout = 9 * wager

    def validate(self):
        """Check that the bet is valid. (str)"""
        errors = []
        bets = self.game.bets[self.player.name]
        made = [bet for bet in bets if bet.match(self.match_text, self.number)]
        if made:
            errors.append('You have already made that bet.')
        if not self.number:
            errors.append('{} bets must be made with a number.'.format(self.raw_text))
        elif self.number not in (4, 6, 8, 10):
            errors.append('{} bets can only be made on 4, 5, 6, 8, 9, or 10.'.format(self.raw_text))
        return ' '.join(errors)


class OddsBet(PassBet):
    """
    An odds bet on a do/don't pass/come bet. (CrapsBet)

    Methods:
    dont_resolve: Alternate resolve method for don't bets. (int)

    Overridden Methods:
    __init__
    max_bet
    set_wager
    validate
    """

    aliases = []
    match_text = 'odds'
    removable = True

    def __init__(self, player, raw_text, number, parent):
        """
        Set up the bet's attributes. (None)

        Parameters:
        player: The player who made the bet. (player.Player)
        raw_text: The user's name for the bet. (str)
        number: The number associated with the bet. (int)
        """
        super(OddsBet, self).__init__(player, raw_text, number)
        self.parent = parent
        if "don't" in self.parent.match_text:
            self.do_resolve = self.resolve
            self.resolve = self.dont_resolve

    def dont_resolve(self, roll):
        """
        Determine if the bet won or lost. (int)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        if sum(roll) == 12:
            result = 0
        else:
            result = -1 * self.do_resolve(roll)
        return result

    def max_bet(self, limit, max_payout):
        """
        Calculate the maximum odds wager. (int)

        Parameters:
        odds_multiples: The multipliers for odds bets. (dict of int: int)
        """
        if self.number:
            max_bet = self.game.odds_multiples[self.number] * self.parent.wager - self.wager
        else:
            max_bet = 0
        return max_bet

    def set_wager(self, wager):
        """
        Set the bet's wager and calculate it's payout. (None)

        Parameters:
        wager: The amount of money bet. (int)
        """
        self.wager = wager
        multiplier, divisor = BUY_ODDS[self.number]
        if "don't" in self.parent.match_text:
            multiplier, divisor = divisor, multiplier
        self.payout = int(wager * multiplier / divisor)

    def validate(self):
        """Check that the bet is valid. (str)"""
        return ''


class PassBet(CrapsBet):
    """
    A bet that the shooter will win. (CrapsBet)

    Overridden Methods:
    resolve
    validate
    """

    aliases = ['right']
    match_text = 'pass'

    def resolve(self, roll):
        """
        Determine if the bet won or lost. (tuple of int, str)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        result = 0
        roll = sum(roll)
        if self.number:
            if roll == self.number:
                result = self.payout
            elif roll == 7:
                result = -self.payout
        else:
            if roll in (7, 11):
                result = self.payout
            elif roll in (2, 3, 12):
                result = -self.payout
            else:
                self.number = roll
        return result

    def validate(self):
        """Check that the bet is valid. (str)"""
        # !! one per turn, and children
        errors = []
        if self.game.point:
            errors.append('{} bets cannot be made when there is a point.'.format(self.raw_text))
        if self.number:
            errors.append('{} bets are not made with a number.'.format(self.raw_text))
        return ' '.join(errors)


class ComeBet(PassBet):
    """
    A pass-style bet after the come out roll. (PassBet)

    Overridden Methods:
    resolve
    validate
    """

    aliases = []
    match_text = 'come'

    def resolve(self, roll):
        """
        Determine if the bet won or lost. (tuple of int, str)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        if self.game.point or "don't" in self.match_text:
            number = self.number
            result = super(ComeBet, self).resolve(roll)
            if self.number != number:
                message = "{}'s {} bet's number was set to {}"
                self.player.tell(message.format(self.player.name, self.raw_text, self.number))
        else:
            result = 0
        return result

    def validate(self):
        """Check that the bet is valid. (str)"""
        errors = []
        if not self.game.point:
            errors.append('{} bets cannot be made before there is a point.'.format(self.raw_text))
        if self.number:
            errors.append('{} bets are not made with a number.'.format(self.raw_text))
        return ' '.join(errors)


class DontComeBet(ComeBet):
    """
    A don't-pass-style bet after the come out roll. (ComeBet)

    Overridden Methods:
    resolve
    """

    match_text = "don't come"
    removable = True

    def resolve(self, roll):
        """
        Determine if the bet won or lost. (tuple of int, str)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        if sum(roll) == 12:
            result = 0
        else:
            result = -1 * super(DontComeBet, self).resolve(roll)
        return result


class DontPassBet(PassBet):
    """
    A bet that the shooter will lose. (PassBet)

    Overridden Methods:
    resolve
    """

    aliases = ['wrong']
    match_text = "don't pass"
    removable = True

    def resolve(self, roll):
        """
        Determine if the bet won or lost. (tuple of int, str)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        if sum(roll) == 12:
            result = 0
        else:
            result = -1 * super(DontPassBet, self).resolve(roll)
        return result


class PlaceBet(CrapsBet):
    """
    A bet that a particular number will come up before a 7. (CrapsBet)

    Overridden Methods:
    resolve
    set_wager
    validate
    """

    match_text = 'place'
    removable = True

    def resolve(self, roll):
        """
        Determine if the bet won or lost. (tuple of int, str)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        result = 0
        if sum(roll) == self.number:
            result = self.payout
        elif sum(roll) == 7:
            result = -1 * self.payout
        if self.match_text == 'lay':
            result *= -1
        return result

    def set_wager(self, wager):
        """
        Set the bet's wager and calculate it's payout. (None)

        Parameters:
        wager: The amount of money bet. (int)
        """
        self.wager = wager
        if self.match_text == 'place':
            odds = PLACE_ODDS
        else:
            odds = BUY_ODDS
        multiplier, divisor = odds[self.number]
        if self.match_text == 'lay':
            multiplier, divisor = divisor, multiplier
        self.payout = int(wager * multiplier / divisor)

    def validate(self):
        """Check that the bet is valid. (str)"""
        errors = []
        bets = self.game.bets[self.player.name]
        made = [bet for bet in bets if bet.match(self.match_text, self.number)]
        if made:
            errors.append('You have already made that bet.')
        if not self.number:
            errors.append('{} bets must be made with a number.'.format(self.raw_text))
        elif self.number not in (4, 5, 6, 8, 9, 10):
            errors.append('{} bets can only be made on 4, 5, 6, 8, 9, or 10.'.format(self.raw_text))
        return ' '.join(errors)


class BuyBet(PlaceBet):
    """A place bet with better odds and a commission. (PlaceBet)"""

    commission = 0.05
    match_text = 'buy'
    removable = True


class LayBet(BuyBet):
    """A buy bet that a seven will come before a given number. (BuyBet)"""

    aliases = ["don't buy"]
    match_text = 'lay'
    removable = True


class PropositionBet(CrapsBet):
    """
    A single-roll bet on one or more specific numbers. (CrapsBet)

    Class Attributes:
    prop_aliases: Different names for the various proposition bets. (dict)
    prob_bets: Data defining the various proposition bets. (dict)

    Attributes:
    divisor: The denominator of the bet's odds. (int)
    multiplier: The nominator of the bet's odds. (int)
    special_odds: Different odds for particular rolls. (dict of int: tuple of int)
    targets: The numbers that the bet wins on. (int)

    Overridden Methods:
    __init__
    max_bet
    resolve
    set_wager
    validate
    """

    # Different names for the various proposition bets.
    prop_aliases = {'2': '2', '3': '3', '6': '6', '7': '7', '8': '8', '11': 'yo', '12': '12', 'any 7': '7', 
        'c&e': 'c & e', 'c & e': 'c & e', 'craps': 'craps', 'big 6': '6', 'big 8': '8', 'field': 'field', 
        'hi-lo': 'hi-lo', 'hi-low': 'hi-lo', 'high-lo': 'hi-lo', 'high-low': 'hi-lo', 'horn': 'horn', 
        'whirl': 'whirl', 'world': 'whirl', 'yo': 'yo'}
    # Data defining the various proposition bets.
    prop_bets = {'2': ((2,), 30, 1), '3': ((3,), 15, 1), '6': ((6,), 1, 1), '7': ((7,), 4, 1), 
        '8': ((8,), 1, 1), 'yo': ((11,), 15, 1), '12': ((12,), 30, 1), 'hi-lo': ((2, 12), 15, 1), 
        'craps': ((2, 3, 12), 7, 1), 'c & e': ((2, 3, 11, 12), 3, 1, {11: (7, 1)}), 
        'field': ((2, 3, 4, 9, 10, 11, 12), 1, 1, {2: (2, 1), 12: (2, 1)}),
        'horn': ((2, 3, 11, 12), 3, 1, {2: (27, 4), 12: (27, 4)}),
        'whirl': ((2, 3, 7, 11, 12), 11, 5, {2: (26, 5), 7: (0, 1), 12: (26, 5)})}

    def __init__(self, player, proposition):
        """
        Set up the bet's attributes. (None)

        Parameters:
        player: The player making the bet. (player.Player)
        proposition: The type of proposition bet to make. (str)
        """
        # Set the specified attributes.
        self.player = player
        self.raw_text = proposition.capitalize()
        self.number = 0
        # Set the calculated attributes.
        self.game = self.player.game
        self.match_text = self.prop_aliases.get(proposition, 'n/a')
        bet_data = self.prop_bets.get(self.match_text, ((), 1, 1))
        self.targets, self.multiplier, self.divisor = bet_data[:3]
        if len(bet_data) == 4:
            self.special_odds = bet_data[3]
        else:
            self.special_odds = {}
        # Set the default attributes.
        self.ammo = False
        self.odds_bet = None
        self.wager = 0

    def max_bet(self, limit, max_payout):
        """
        Calculate the maximum odds wager. (int)

        Parameters:
        odds_multiples: The multipliers for odds bets. (dict of int: int)
        """
        return max(1, int(max_payout * self.divisor / self.multiplier))

    def resolve(self, roll):
        """
        Determine if the bet won or lost. (tuple of int, str)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        if sum(roll) in self.special_odds:
            multiplier, divisor = self.special_odds[sum(roll)]
            result = int(self.wager * multiplier / divisor)
        elif sum(roll) in self.targets:
            result = self.payout
        else:
            result = self.wager * -1
        return result

    def set_wager(self, wager):
        """
        Set the bet's wager and calculate it's payout. (None)

        Parameters:
        wager: The amount of money bet. (int)
        """
        self.wager = wager
        self.payout = int(wager * self.multiplier / self.divisor)

    def validate(self):
        """Check that the bet is valid. (str)"""
        errors = []
        if self.match_text == 'n/a':
            errors.append('{!r} is not a recognized proposition bet.'.format(self.raw_text))
        return ' '.join(errors)


if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    craps = Craps(player.Player(name), '')
    print(craps.play())