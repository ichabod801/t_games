"""
craps_game.py

A game of Craps.

To Do:
more options
bet objects

Constants:
BUY_ODDS: The odds for buy bets. (dict of int: tuple of int)
CREDITS: The credits for Craps. (str)
PLACE_ODDS: The odds for place bets. (dict of int: tuple of int)

Classes:
Craps: A game of Craps. (game.Game)
CrapsBot: A bot to play Craps against. (player.Bot)
"""


from __future__ import division

import math

import tgames.dice as dice
import tgames.game as game
import tgames.player as player


BUY_ODDS = {4: (2, 1), 5: (3, 2), 6: (6, 5), 8: (6, 5), 9: (3, 2), 10: (2, 1)}

CREDITS = """
Game Design: Barnard Xavier Phillippe de Marigny de Mandeville
Game Programming: Craig "Ichabod" O'Brien
"""

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
    point: The point to be made, or zero if no point yet. (int)
    shooter_index: Index of the current shooter in self.players. (int)
    stake: How much money the players start with. (int)

    Class Attributes:
    bet_aliases: Different names for the various bets. (dict of str: str)
    bet_maxes: The multiple of the table max for various bets. (dict of str: int)
    prop_aliases: Different names for the proposition bets. (dict of str: str)
    prop_bets: Winning numbers and payouts for proposition bets. (dict)
    reverse_bet: A mapping for reversing bet results. (dict of str: str)

    Methods:
    do_bets: Show the player's bets. (bool)
    do_done: Finish the player's turn. (bool)
    do_remove: Remove bets that are in play. (bool)
    do_roll: Finish the player's turn and roll. (bool)
    resolve_bets: Resolve player bets after a roll. (None)
    resolve_buy: Resolve buy bets. (None)
    resolve_call: Resolve call bets. (None)
    resolve_dont_buy: Resolve don't buy bets. (None)
    resolve_dont_call: Resolve don't call bets. (None)
    resolve_dont_pass: Resolve don't pass bets. (None)
    resolve_dont_place: Resolve don't place bets. (None)
    resolve_pass: Resolve pass bets. (None)
    resolve_place: Resolve place bets. (None)
    resolve_proposition: Resolve proposition bets. (None)

    Overridden Methods:
    do_quit
    game_over
    player_action
    set_options
    set_up
    """

    aliases = {'b': 'bets', 'd': 'done', 'r': 'roll'}
    bet_aliases = {'buy': 'buy', "don't buy": 'dont_buy', 'come': 'come', 'come odds': 'come_odds', 
        "don't come": "dont_come", "don't come odds": 'dont_come_odds', "don't pass": "dont_pass", 
        "don't pass odds": 'dont_pass_odds', 'field': 'field', 'hard': 'hard', 'hardway': 'hard', 
        'hard way': 'hard', 'lay': 'dont_buy', 'pass': 'pass', 'pass odds': 'pass_odds', 'place': 'place', 
        'prop': 'proposition', 'proposition': 'proposition', 'right': 'pass', 'wrong': 'dont_pass'}
    categories = ['Gambling Games', 'Dice Games']
    name = 'Craps'
    num_options = 3
    odds_multiples = {4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3}
    post_point = ('come', 'dont_come', 'dont_pass_odds', 'pass_odds')
    prop_aliases = {'2': '2', '3': '3', '6': '6', '7': '7', '8': '8', '11': 'yo', '12': '12', 'any 7': '7', 
        'c&e': 'c & e', 'c & e': 'c & e', 'craps': 'craps', 'big 6': '6', 'big 8': '8', 'field': 'field', 
        'hi-lo': 'hi-lo', 'hi-low': 'hi-lo', 'high-lo': 'hi-lo', 'high-low': 'hi-lo', 'horn': 'horn', 
        'whirl': 'whirl', 'world': 'whirl', 'yo': 'yo'}
    prop_bets = {'2': ((2,), 30, 1), '3': ((3,), 15, 1), '6': ((6,), 1, 1), '7': ((7,), 4, 1), 
        '8': ((8,), 1, 1), 'yo': ((11,), 15, 1), '12': ((12,), 30, 1), 'hi-lo': ((2, 12), 15, 1), 
        'craps': ((2, 3, 12), 7, 1), 'c & e': ((2, 3, 11, 12), 3, 1, {11: (7, 1)}), 
        'field': ((2, 3, 4, 9, 10, 11, 12), 1, 1, {2: (2, 1), 12: (2, 1)}),
        'horn': ((2, 3, 11, 12), 3, 1, {2: (27, 4), 12: (27, 4)}),
        'whirl': ((2, 3, 7, 11, 12), 11, 5, {2: (26, 5), 7: (0, 1), 12: (26, 5)})}
    removable = ('come_odds' 'dont_come', 'dont_come_odds', 'dont_pass', 'dont_pass_odds', 'hard', 
        'pass odds', 'proposition')
    reverse_bet = {'win': 'lose', 'lose': 'win', 'hold': 'hold'}

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
        bet_total = sum(wager for bet, wager in self.bets[player.name])
        message = 'You have {} bet{} in play totalling {} dollars.'
        lines.append(message.format(len(self.bets[player.name]), s, bet_total))
        # Display remaining money.
        lines.append('You have {} dollars remaining to bet.\n'.format(self.scores[player.name]))
        return '\n'.join(lines)

    def do_bets(self, argument):
        """
        Show the player's bets. (bool)

        Parameters:
        argument: The (ignored) argument to the done command. (str)
        """
        player = self.players[self.player_index]
        player.tell('\n---Your Bets---\n')
        for raw_bet, wager in self.bets[player.name]:
            if '/' in raw_bet:
                bet_type, number = raw_bet.split('/')
                player.tell('{} bet on {} for {} dollars.'.format(bet_type.capitalize(), number, wager))
            else:
                player.tell('{} bet for {} dollars.'.format(raw_bet.capitalize(), wager))
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
            bets = [self.bet_aliases.get(bet.lower(), 'n/a') for bet, wager in self.bets[player.name]]
            if 'pass' not in bets and 'dont_pass' not in bets:
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
        removable = []
        for bet_index, bet_data in enumerate(self.bets[player.name]):
            bet_text, wager = bet_data
            base_bet, slash, number = bet_text.partition('/')
            if self.bet_aliases[base_bet] not in ('pass', 'come'):
                removable.append((bet_index, bet_text, wager))
        # Check that there are removable bets.
        if not removable:
            player.tell('You have not made any bets that can be removed.')
        # Check for remove all.
        elif argument.lower() in ('a', 'all'):
            for bet_index, bet_text, wager in removable[::-1]:  # Do in reverse so indexes don't change
                player.tell('Removing your {} bet for {} dollars.'.format(bet_text, wager))
                del self.bets[player.name][bet_index]
                self.scores[player.name] += wager
        # Show bets and get one to remove.
        # !! Note that this allows removing a bet with odds on it without removing the odds.
        else:
            player.tell('\n---Removable Bets---\n')
            row_text = '{}: {} bet for {} dollars.'
            for bet_index, bet_data in enumerate(removable):
                player.tell(row_text.format(bet_index, bet_data[1].capitalize(), bet_data[2]))
            query = '\nWhich bet would you like to remove (-1 for none)? '
            choice = player.ask_int(query, low = -1, high = len(removable) - 1)
            if choice == -1:
                pass
            else:
                bet_index, bet_text, wager = bet_data[choice]
                player.tell('Removing your {} bet for {} dollars.'.format(bet_text, wager))
                del self.bets[player.name][bet_index]
                self.scores[player.name] += wager
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
        self.force_win = True

    def game_over(self):
        """Check for the end of the game. (bool)"""
        if self.scores[self.human.name] == 0 and not self.bets[self.human.name]:
            self.win_loss_draw[1] = 1
            self.scores[self.human.name] -= self.stake
            return True
        else:
            return False

    def get_bet(self, player):
        raw_bet = player.ask('What sort of bet would you like to make? ')
        if not raw_bet.strip():
            raw_bet = 'done'
        words = raw_bet.split()
        if words[0].lower() in ('prop', 'proposition'):
            raw_bet = words[0]
            number = ' '.join(words[1:])
            if number.lower() not in self.prop_aliases:
                player.error('{!r} is not a valid proposition bet.'.format(number))
                raw_bet = ''
        elif len(words) > 1 and words[-1].isdigit():
            raw_bet = ' '.join(words[:-1])
            number = words[-1]
        else:
            number = ''
        return raw_bet, number

    def odds_max(self, player, raw_bet, number):
        """
        Determine the maximum bet for an odds bet. (int)

        If it returns 0, you cannot make an odds bet on that number.

        !! This method is such a kludge that I think I should consider redoing bets,
            maybe as objects.

        Parameters:
        player: The player trying to make the bet. (player.Player)
        raw_bet: The bet as the user entered it. (str)
        number: The number the bet is on. (str)
        """
        bet = self.bet_aliases[raw_bet]
        # Determine what the enabling bet looks like.
        if number:
            valid = '{}/{}'.format(bet[:-5], number)
        else:
            valid = bet[:-5]
            #number = str(self.point)
        # Find any enabling bets.
        starters = []
        for prev_bet, wager in self.bets[player.name]:
            # Convert the stored bets to standardized text representations.
            if '/' in prev_bet:
                bet_type, num = prev_bet.split('/')
                prev_bet = '{}/{}'.format(self.bet_aliases[bet_type.lower()], num)
            else:
                prev_bet = self.bet_aliases[prev_bet.lower()]
            if prev_bet == valid:
                starters.append(wager)
        # Determine what a previously made bet would look like.
        if number:
            odds_bet = '{}/{}'.format(bet, number)
        else:
            odds_bet = bet
        # Find previously made bets.
        made = []
        for prev_bet, wager in self.bets[player.name]:
            # Convert the stored bets to standardized text representations.
            if '/' in prev_bet:
                bet_type, num = prev_bet.split('/')
                prev_bet = '{}/{}'.format(self.bet_aliases[bet_type.lower()], num)
            else:
                prev_bet = self.bet_aliases[prev_bet.lower()]
            if prev_bet == odds_bet:
                made.append(wager)
        # Determine max bet remaining.
        if not number:
            multiplier = self.odds_multiples[self.point]
        else:
            multiplier = self.odds_multiples[int(number)]
        #print(valid, odds_bet, starters, multiplier, made)
        return sum(starters) * multiplier - sum(made)

    def player_action(self, player):
        """
        Handle any actions by the current player. (bool)

        Parameters:
        player: The current player. (player.Player)
        """
        # Display the game status.
        player.tell(str(self))
        # Get the player action.
        raw_bet, number = self.get_bet(player)
        bets_made = [bet_type for bet_type, wager in self.bets[player.name]]
        if raw_bet.lower() in self.bet_aliases:
            # Check for bet being valid at this time.
            bet = self.bet_aliases[raw_bet.lower()]
            if bet in ('pass', 'dont_pass') and self.point:
                player.error('That bet cannot be made after the point has been established.')
            elif bet in self.post_point and not self.point:
                player.error('That bet cannot be made before the point has been established.')
            elif bet in ('come', 'dont_come') and bet in bets_made:
                player.error('You can only make that be once each roll.')
            elif bet in ('buy', 'place', 'dont_buy', 'come_odds', 'dont_come_odds') and not number:
                player.error('You must pick a number to play for that bet.')
            elif bet == 'hard' and number not in ('4', '6', '8', '10'):
                player.error('Hard way bets can only be made on 4, 6, 8, or 10.')
            elif bet in ('odds', 'dont_odds') and number not in ('4', '5', '6', '8', '9', '10'):
                player.error('Odds bets can only be made on 4, 5, 6, 8, 9, or 10.')
            else:
                # Get the wager.
                if bet in ('prop', 'proposition'):
                    multiplier, divisor = self.prop_bets[self.prop_aliases[number]][1:3]
                    prop_max = int(self.limit * self.max_payout * divisor / multiplier)
                    max_bet = max(1, min(prop_max, self.scores[player.name]))
                elif bet == 'hard':
                    if number in '68':
                        hard_max = int(self.limit * self.max_payout / 9)
                    else:
                        hard_max = int(self.limit * self.max_payout / 7)
                    max_bet = max(1, min(hard_max, self.scores[player.name]))
                elif 'odds' in bet:
                    max_bet = self.odds_max(player, raw_bet, number)
                    if not max_bet:
                        player.error('You do not have a valid bet to make odds on.')
                        return True
                else:
                    max_bet = min(self.limit, self.scores[player.name])
                query = 'How much would you like to wager (max bet = {})? '.format(max_bet)
                wager = player.ask_int(query, low = 1, high = max_bet, cmd = False)
                if bet in ('buy', 'dont_buy'):
                    cut = int(math.ceil(wager * 0.05))
                    if self.scores[player.name] >= cut + wager:
                        self.scores[player.name] -= cut
                        s = ('s', '')[cut == 1]
                        player.tell('The bank takes a cut of {} dollar{} for the buy bet.'.format(cut, s))
                    else:
                        player.error("You do not have enough money to cover the bank's 5% cut on that bet.")
                        wager = 0
                if wager:
                    # Store the bet.
                    if number:
                        raw_bet = '{}/{}'.format(raw_bet, number)
                    self.bets[player.name].append((raw_bet, wager))
                    self.scores[player.name] -= wager
            return True
        elif raw_bet:
            # Handle other commands
            return self.handle_cmd(raw_bet)

    def resolve_bets(self):
        """Resolve player bets after a roll. (None)"""
        # Loop through the player bets.
        for player in self.players:
            for raw_bet, wager in self.bets[player.name][:]: # loop through copy to allow changes.
                # Get the bet details.
                bet, slash, number = raw_bet.partition('/')
                bet = self.bet_aliases[bet.lower()]
                # Resolve the bet.
                getattr(self, 'resolve_' + bet)(player, raw_bet, wager)
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

    def resolve_buy(self, player, raw_bet, wager, reverse = False):
        """
        Resolve place bets. (None)

        Parameters:
        player: The player who made the pass bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the pass bet. (wager)
        reverse: A flag for handling as a don't pass bet. (bool)
        """
        self.resolve_place(player, raw_bet, wager, odds = BUY_ODDS, reverse = reverse)

    def resolve_come(self, player, raw_bet, wager, reverse = False):
        """
        Resolve come bets. (None)

        Parameters:
        player: The player who made the come bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the come bet. (wager)
        reverse: A flag for handling as a don't come bet. (bool)
        """
        # Get the bet details.
        bet, slash, number = raw_bet.partition('/')
        # Determine the status of the bet.
        status = 'hold'
        if number:
            # Check come bet with a point.
            number = int(number)
            if number == sum(self.dice):
                status = 'win'
            elif sum(self.dice) == 7:
                status = 'lose'
        else:
            # Check come bet without a point.
            if sum(self.dice) in (7, 11):
                status = 'win'
            elif sum(self.dice) in (2, 3, 12):
                status = 'lose'
            else:
                status = 'point'
        # Reverse the status if necessary.
        if reverse and sum(self.dice) == 12:
            status = 'hold'
        elif reverse:
            status = self.reverse_bet.get(status, status)
        # Handle winning the bet.
        if status == 'win':
            self.scores[player.name] += wager * 2
            self.bets[player.name].remove((raw_bet, wager))
            self.human.tell('{} won {} dollars on their {} bet.'.format(player.name, wager, raw_bet))
        # Handle losing the bet.
        elif status == 'lose':
            self.bets[player.name].remove((raw_bet, wager))
            self.human.tell('{} lost {} dollars on their {} bet.'.format(player.name, wager, raw_bet))
        # Handle setting the point.
        elif status == 'point':
            self.bets[player.name].remove((raw_bet, wager))
            message = "The point for {}'s {} bet is set to {}."
            self.human.tell(message.format(player.name, raw_bet, sum(self.dice)))
            self.bets[player.name].append(('{}/{}'.format(raw_bet, sum(self.dice)), wager))

    def resolve_come_odds(self, player, raw_bet, wager):
        """
        Resolve come odds bets. (None)

        Parameters:
        player: The player who made the comeodds bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the don't odds bet. (wager)
        """
        self.resolve_pass_odds(player, raw_bet, wager)

    def resolve_dont_buy(self, player, raw_bet, wager):
        """
        Resolve don't buy bets. (None)

        Parameters:
        player: The player who made the don't buy bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the pass bet. (wager)
        """
        self.resolve_place(player, raw_bet, wager, reverse = True, odds = BUY_ODDS)

    def resolve_dont_come(self, player, raw_bet, wager):
        """
        Resolve don't come bets. (None)

        Parameters:
        player: The player who made the don't come bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the come bet. (wager)
        """
        self.resolve_come(player, raw_bet, wager, reverse = True)

    def resolve_dont_come_odds(self, player, raw_bet, wager):
        """
        Resolve don't odds bets. (None)

        Parameters:
        player: The player who made the don't odds bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the don't odds bet. (wager)
        """
        self.resolve_pass_odds(player, raw_bet, wager, reverse = True)

    def resolve_dont_pass(self, player, raw_bet, wager):
        """
        Resolve don't pass bets. (None)

        Parameters:
        player: The player who made the don't pass bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the pass bet. (wager)
        """
        self.resolve_pass(player, raw_bet, wager, reverse = True)

    def resolve_dont_pass_odds(self, player, raw_bet, wager):
        """
        Resolve don't odds bets. (None)

        Parameters:
        player: The player who made the don't odds bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the don't odds bet. (wager)
        """
        self.resolve_pass_odds(player, raw_bet, wager, reverse = True)

    def resolve_hard(self, player, raw_bet, wager):
        """
        Resolve hard way bets. (None)

        Parameters:
        player: The player who made the hard way bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the pass bet. (wager)
        """
        # Get the bet details.
        bet, slash, number = raw_bet.partition('/')
        number = int(number)
        # Determine the status of the bet.
        if sum(self.dice) == number and self.dice.values[0] == self.dice.values[1]:
            if number in (4, 10):
                payout = 7 * wager
            else:
                payout = 9 * wager
            self.scores[player.name] += payout
            message = '{} won {} dollars on their {} bet. The bet remains in play.'
            self.human.tell(message.format(player.name, payout, raw_bet))
        elif sum(self.dice) in (7, number):
            self.bets[player.name].remove((raw_bet, wager))
            self.human.tell('{} lost {} dollars on their {} bet.'.format(player.name, wager, raw_bet))

    def resolve_pass_odds(self, player, raw_bet, wager, reverse = False):
        """
        Resolve odds bets. (None)

        Parameters:
        player: The player who made the odds bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the odds bet. (wager)
        reverse: A flag for handling as a don't odds bet. (bool)
        """
        # Get the bet details.
        bet, slash, number = raw_bet.partition('/')
        if number:
            number = int(number)
        else:
            number = self.point
        # Determine status of the bet
        status = 'hold'
        if sum(self.dice) == number:
            status = 'win'
        elif sum(self.dice) == 7:
            status = 'lose'
        # Reverse the status if necessary.
        if reverse:
            status = self.reverse_bet[status]
        # Handle winning the bet.
        if status == 'win':
            multiplier, divisor = BUY_ODDS[number]
            if reverse:
                multiplier, divisor = divisor, multiplier
            payout = int(wager * multiplier / divisor)
            self.scores[player.name] += payout + wager
            self.bets[player.name].remove((raw_bet, wager))
            self.human.tell('{} won {} dollars on his {} bet.'.format(player.name, payout, raw_bet))
        # Handle losing the bet.
        elif status == 'lose':
            self.bets[player.name].remove((raw_bet, wager))
            self.human.tell('{} lost {} dollars on their {} bet.'.format(player.name, wager, raw_bet))

    def resolve_pass(self, player, raw_bet, wager, reverse = False):
        """
        Resolve pass bets. (None)

        Parameters:
        player: The player who made the pass bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the pass bet. (wager)
        reverse: A flag for handling as a don't pass bet. (bool)
        """
        # Determine the status of the bet.
        status = 'hold'
        if sum(self.dice) == self.point or (sum(self.dice) in (7, 11) and not self.point):
            status = 'win'
        elif (self.point and sum(self.dice) == 7) or (sum(self.dice) in (2, 3, 12) and not self.point):
            status = 'lose'
        # Reverse the status if necessary.
        if reverse and sum(self.dice) == 12:
            status = 'hold'
        elif reverse:
            status = self.reverse_bet[status]
        # Handle winning the bet.
        if status == 'win':
            self.scores[player.name] += wager * 2
            self.bets[player.name].remove((raw_bet, wager))
            self.human.tell('{} won {} dollars on their {} bet.'.format(player.name, wager, raw_bet))
        # Handle losing the bet.
        elif status == 'lose':
            self.bets[player.name].remove((raw_bet, wager))
            self.human.tell('{} lost {} dollars on their {} bet.'.format(player.name, wager, raw_bet))

    def resolve_place(self, player, raw_bet, wager, reverse = False, odds = PLACE_ODDS):
        """
        Resolve place bets. (None)

        Parameters:
        player: The player who made the pass bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the pass bet. (wager)
        reverse: A flag for handling as a don't pass bet. (bool)
        odds: The odds to use in determining the payout. (dicct of int: tuple of int)
        """
        # Get the bet details.
        bet, slash, number = raw_bet.partition('/')
        number = int(number)
        # Determine the outcome of the bet.
        if not self.point:
            # No valid on come out roll.
            status = 'hold'
        elif sum(self.dice) == number:
            status = 'win'
        elif sum(self.dice) == 7:
            status = 'lose'
        else:
            status = 'hold'
        # Reverse the status if necessary.
        if reverse:
            status = self.reverse_bet[status]
        # Handle resolution of the bret.
        if status == 'win':
            n, to = odds[number]
            if reverse:
                payout = int(wager / n * to)
            else:
                payout = int(wager / to * n)
            self.scores[player.name] += payout
            message = '{} won {} dollars on their {} bet on {}. The bet remains in play.'
            self.human.tell(message.format(player.name, payout, bet, number))
        elif status == 'lose':
            message = '{} lost {} dollars on their {} bet on {}.'
            self.human.tell(message.format(player.name, wager, bet, number))
            self.bets[player.name].remove((raw_bet, wager))

    def resolve_proposition(self, player, raw_bet, wager):
        """
        Resolve proposition bets. (None)

        Parameters:
        player: The player who made the proposition bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the pass bet. (wager)
        """
        # Get bet details.
        prop, slash, prop_type = raw_bet.partition('/')
        prop_data = self.prop_bets[self.prop_aliases[prop_type.lower()]]
        targets, multiplier, divisor = prop_data[:3]
        if len(prop_data) == 4:
            special_odds = prop_data[3]
        else:
            special_odds = {}
        # Check the roll.
        roll = sum(self.dice)
        if roll in targets:
            # Check for special odds for the specific roll.
            if roll in special_odds:
                multiplier, divisor = special_odds[roll]
            # Calculate the payout.
            payout = int(wager * multiplier / divisor)
            self.scores[player.name] += payout
            message = '{} won {} dollars on their {} bet. The bet remains in play.'
            self.human.tell(message.format(player.name, payout, prop_type))
        else:
            # Remove the bet.
            self.bets[player.name].remove((raw_bet, wager))
            self.human.tell('{} lost {} dollars on their {} bet.'.format(player.name, wager, prop_type))

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


class CrapsBot(player.Bot):
    """
    A bot to play Craps with. (player.Bot)

    Overridden Methods:
    ask
    ask_int
    tell
    """

    def ask(self, prompt):
        """
        Ask the bot a question. (str)

        Parameters:
        prompt: The queston to ask. (str)
        """
        if prompt.startswith('What sort of bet'):
            if not self.game.bets[self.name] and self.game.scores[self.name]:
                return "Don't Pass"
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
        wager = min(self.game.limit, self.game.scores[self.name])
        self.game.human.tell("{} made a Don't Pass bet for {} bucks.".format(self.name, wager))
        return wager

    def tell(self, *args, **kwargs):
        """
        Ask the bot for an integer. (int)

        Parameters:
        the parameters are ingored.
        """
        pass

if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    craps = Craps(player.Player(name), '')
    print(craps.play())