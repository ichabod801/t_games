"""
craps_game.py

A game of Craps.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
BUY_ODDS: The odds for buy bets. (dict of int: tuple of int)
CREDITS: The credits for Craps. (str)
HOUSE_HELP: Help text for the house edge. (str)
PLACE_ODDS: The odds for place bets. (dict of int: tuple of int)
RULES: The rules for Craps. (str)

Classes:
Craps: A game of Craps. (game.Game)
CrapsBet: A bet in a game of craps. (object)
HardWayBet: A bet that a number will come up as a pair first. (CrapsBet)
PassBet: A bet that the shooter will win. (CrapsBet)
ComeBet: A pass-style bet after the come out roll. (PassBet)
DontComeBet: A don't-pass-style bet after the come out roll. (ComeBet)
DontPassBet: A bet that the shooter will lose. (PassBet)
OddsBet: An odds bet on a do/don't pass/come bet. (PassBet)
PlaceBet: A bet that a particular number will come up before a 7. (CrapsBet)
BuyBet: A place bet with better odds and a commission. (PlaceBet)
LayBet: A buy bet that a seven will come before a given number. (BuyBet)
PropositionBet: A single-roll bet on one or more specific numbers. (CrapsBet)
CrapsBot: A bot to play Craps against. (player.Bot)
OverBot: A bot that slowly puts its whole stake on the table. (CrapsBot)
OverPoliteBot: A bot that politely puts its whole stake out. (OverBot)
OverSemiPoliteBot: A bot that kinda politely puts all its stake out. (OverBot)
PoliteBot: A bot that roots for the shooter. (CrapsBot)
Randy: A bot that bets completely randomly. (CrapsBot)
"""


from __future__ import division

import math
import random
import re

import t_games.dice as dice
import t_games.game as game
import t_games.player as player
import t_games.utility as utility


BUY_ODDS = {4: (2, 1), 5: (3, 2), 6: (6, 5), 8: (6, 5), 9: (3, 2), 10: (2, 1)}

CREDITS = """
Game Design: Barnard Xavier Phillippe de Marigny de Mandeville
Game Programming: Craig "Ichabod" O'Brien
"""

HOUSE_HELP = """
The house edge for each bet is:

Pass or Come                         1.41%
Don't Pass or Don't Come             1.36%
Pass Odds or Come Odds               0.00%
Don't Pass Odds or Don't Come Odds   0.00%
Proposition 2 or 12                 13.89%
Proposition 3 or 11 (Yo)            11.11%
Proposition Hi-Lo (2 or 12)         11.11%
Proposition Craps (2, 3, or 12)     11.11%
Proposition Any 7                   16.67%
Proposition Field                    5.56%
Proposition Horn                    12.50%
Proposition Whirl/World             13.33%
Hard 4 or 10                        11.11%
Hard 6 or 8                          9.09%
Big 6/8                              9.09%
Place 4 or 10                        6.67%
Place 5 or 9                         4.00%
Place 6 or 8                         1.52%
Buy (Any Number)                     4.76%
Lay 4 or 10                          2.44%
Lay 5 or 9                           3.23%
Lay 6 or 8                           4.00%

tl;dr: Odds bets are the best, and proposition bets on 2, 7, or 12 are the
worst. The best strategy is obviously to make Don't Pass bets with odds.
However, Don't Pass bets are considered rude. Stick to don't come bets, or
the bots will cry.
"""

PLACE_ODDS = {4: (9, 5), 5: (7, 5), 6: (7, 6), 8: (7, 6), 9: (7, 5), 10: (9, 5)}

RULES = """
A player is set to be the shooter (the person who rolls the dice). The base
game of craps goes as follows: The first roll in the round is the come out
roll. On the come out roll the shooter "wins" if they roll a 7 or 11 on two
dice. They "lose" on the come out roll if they roll a 2, 3, or 12. Any other
roll sets the point. The shooter continues to roll, "winning" if they re-roll
the point and "losing" if they roll a 7.

At the end of a round where the shooter "wins" or "loses," they start over
again with a new come out roll. The exception is if the shooter gets a point
and then loses with a roll of 7. In that case, the dice pass to the next
player, who becomes the shooter for a new come out roll.

The base game is not really the game. The real game is making various bets on
the die rolls. The shooter can easily bet that they will "lose," and then if
they "lose," they win money. The bets are described below. The only real
restriction that the base game places on betting is that the shooter must
make a pass or a don't pass bet for each come out roll.

To play, specify which bet you want to make. Then you will be asked how much
you want to wager on the bet. When you are done betting on a particular roll,
enter 'done' or just hit return.

Your score in the results and statistics will be how much money you won
(positive) or lost (negative). This means you can calcuate your total winnings
or losses by multiplying you average score times the number of games you have
played.

BETS:
Pass (Right): A bet that the shooter will "win". Pays 1:1
Don't Pass (Wrong): A bet that the shooter will "lose". Note that a don't pass
    bet is not resolved on a 12 on the come out roll. It remains in play for
    the next come out roll. Pays 1:1
Come: This bet is like a pass bet that treats the next roll as a new come out
    roll. So it wins if the next roll is 7 or 11, loses if the next roll is 2,
    3, or 12; and otherwise a point is set and the bet wins if the point is
    rolled before a seven and loses if a seven is rolled first. Pays 1:1
Don't Come: This is the don't pass equivalent of the come bet. Pays 1:1
Odds: Any of the above bets can have an odds bet placed on them after a point
    is set. This pays out at true odds that the point will (or won't for don't
    pass/don't come odds) be rolled before a 7. This is a key bet in craps, as
    it is the only fair bet (no house edge) in the game. To make this bet, bet
    the base bet plus "odds", such as "pass odds" or "don't pass odds." for
    come/don't come odds, you must state the point as well, such as "come odds
    4." Odds bets may be made with a higher maximum, often depending on the
    point the odds are on. Payouts are 2:1 for 4 or 10, 3:2 for 5 or 9, and
    6:5 for 6 or 8. The reverse odds are payed for don't pass/don't come odds.
Place: A bet that a specific number (4, 5, 6, 8, 9, or 10) will be rolled
    before a 7. Pays 9:5 on 4 or 10, 7:5 on 5 or 9, and 7:6 on 6 or 8.
Buy Bet: A place bet that pays true odds. However, you must pay a 5%
    commission to make the bet. Pays out as Odds bet.
Lay Bet: The revers of a buy bet, betting that a 7 will be rolled first. It
    also pays true odds (as a don't pass odds bet), and requires a 5%
    commission to be paid.
Hard Way (Hard): A hard way bet can be played on 4, 6, 8, or 10. It is a bet
    that the number will be rolled as a pair before it is rolled otherwise. It
    pays out 7:1 for 4 or 10, 9:1 for 6 or 8.

PROPOSITION (SINGLE-ROLL) BETS:
(To make a proposition bet, type "prop" or "propositon" and the name of the
    bet.)
2 (snake eyes/aces): Wins if the next roll is a 2. Pays
3 (ace-duece): Wins if the next roll is a 3. Pays
11 (yo): Wins if the next roll is an 11. Pays
12 (boxcars/midnight/cornrows): Wins if the next roll is a 12. Pays
Any 7: Wins if the next roll is a 7. Pays 4:1
Any Craps (craps/three-way): Wins if the next roll is a 2, 3, or 12. Pays
Field: Wins if the next roll is 2, 3, 4, 9, 10, 11, or 12. Pays 1:1, or 2:1
    if the 2 or 12 are rolled.
Hi-lo (2 or 12): Wins if the next roll is either a 2 or a 12. Pays
Horn: Wins if the next roll is 2, 3, 11, or 12. Pays 27:4 if 2 or 12 is
    rolled, 3:1 if 3 or 11 is rolled.
Whirl (world): Wins if the next rolls is a 2, 3, 11, or 12. Pays 26:5 if 2 or
    12 is rolled, 11:5 if 3 or 11 is rolled, and pushes (remains in play) if
    the 7 is rolled.

Some bets, including proposition bets, have their maximum bet determined by
the maximum payout on the table (typically 3 times the maximum bet). You can't
bet so much that you would win more than the maximum payout.

OTHER COMMANDS:
Bets (b): See the bets you currently have in play.
Done (d): Finish betting on the next roll.
Remove (x): Some bets can be taken back after being made. This command will
    show you your removable bets and allow you to take them back.
Roll (r): Finish betting and roll the dice.

OPTIONS:
cars-pay-3 (c3): Make 12 (boxcars) pay 3:1 on a field bet.
lazy-hard (lh): Turns hard way bets on during the come out roll.
limit= (l=): The maximum ammount that can be bet (20).
max-payout= (m$=): The multiple of the limit that is the maximum payout (3).
max-players= (mp=): The maximum number of players at the table (7).
odds-max= (om=): The multiple of the limit for odds bets. If odds-max = 345,
    the maximum is 3x the limit for 4 or 10, 4x the limit for 5 or 9, and 5x
    the limit for 6 or 10. (345)
stake= (s=): The ammount of money the player starts with (250).
yo-pays-2 (y2): Makes 11 (yo) pay 2:1 on a field bet.
"""

class Craps(game.Game):
    """
    A game of Craps. (game.Game)

    Basic play is that every one gets a chance to bet, then the shooter throws,
    and then bets are resolved. Basic program flow is player_action gets the bets,
    handles everything else as a command. Done command checks for shooter, if so
    rolls and resolves bets. Each bet has it's own resolution method, which is
    found with getattr using the internal bet name from the bet_aliases attribute.

    Class Attributes:
    odds_multiples: The multiples of the max bets for odds bets. (dict)

    Attributes:
    bet_classes: A translation of bet names to bet objects. (dict of str: type)
    bets: The bets the players have made this round. (dict of str: list)
    cars_pay_3: A flag for 12 paying at 3:1 on field bets. (bool)
    dice: The dice that get rolled. (dice.Pool)
    force_roll: The number that must be rolled next (0 means no forced roll). (int)
    lazy_hard: A flag for hard ways bets to be off on come out rolls. (bool)
    limit: The maximum bet that can be made. (int)
    max_payout: The multiple of the limit that can be paid out on one bet. (int)
    max_players: The limit on the size of self.players. (int)
    odds_max: The multiple of the max bet for odds bets. (int)
    point: The point to be made, or zero if no point yet. (int)
    shooter_index: Index of the current shooter in self.players. (int)
    stake: How much money the players start with. (int)
    yo_pays_2: A flag for 11 paying at 2:1 on field bets. (bool)

    Methods:
    do_bets: Show the player's bets. (bool)
    do_done: Finish the player's turn. (bool)
    do_remove: Remove bets that are in play. (bool)
    do_roll: Finish the player's turn and roll. (bool)
    get_wager: Get the ammount to wager on the bet. (int)
    next_shooter: Determine the next shooter and the next player (better). (None)
    remove_bet: Remove a bet from play. (None)
    resolve_bets: Resolve player bets after a roll. (None)
    validate_shooter: Make sure the current shooter can make bets. (bool)

    Overridden Methods:
    __str__
    default
    do_quit
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['Crap']
    aliases = {'b': 'bets', 'd': 'done', 'r': 'roll', 'x': 'remove'}
    categories = ['Gambling Games']
    credits = CREDITS
    help_text = {'house-edge': HOUSE_HELP}
    name = 'Craps'
    num_options = 8
    odds_multiples = {4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3}
    rules = RULES

    def __str__(self):
        """Create a human readable text representation. (str)"""
        player = self.players[self.player_index]
        # Display shooter and point.
        if self.point:
            point_text = 'point = {}'.format(self.point)
        else:
            point_text = 'off'
        lines = ['\nThe shooter is {} ({}).'.format(self.players[self.shooter_index].name, point_text)]
        # Display outstanding bets.
        bet_text = utility.number_plural(len(self.bets[player.name]), 'bet')
        total_bet = sum(bet.wager for bet in self.bets[player.name])
        buck_text = utility.plural(total_bet, 'buck')
        lines.append('You have {} in play totalling {} {}.'.format(bet_text, total_bet, buck_text))
        # Display remaining money.
        plural = utility.plural(self.scores[player.name], 'buck')
        lines.append('You have {} {} remaining to bet.'.format(self.scores[player.name], buck_text))
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
            # Parse the text.
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
        Show the player's bets. (b)
        """
        player = self.players[self.player_index]
        player.tell('\n---Your Bets---\n')
        for bet in self.bets[player.name]:
            plural = utility.plural(bet.wager, 'buck')
            player.tell('{} for {} {}.'.format(bet, bet.wager, plural).capitalize())
        player.tell()
        return True

    def do_done(self, argument):
        """
        Finish the player's turn. (d)

        If you finish your turn with the done command and you are the shooter, you
        will be asked to hit enter to roll. You can add the 'roll' or 'r' argument to
        the done command to automatically roll if you are asked to. Or, you can just
        use the roll command to do that.
        """
        player = self.players[self.player_index]
        # Check for shooter's turn.
        if self.player_index == self.shooter_index:
            # Check for a pass or don't pass bet:
            bets = [bet.match_text for bet in self.bets[player.name]]
            if 'pass' not in bets and "don't pass" not in bets:
                player.error("You must have a pass or a don't pass bet when you are the shooter.")
                return True
            # Have them roll the dice.
            if argument.lower() not in ('r', 'roll'):
                player.ask('You are the shooter. Press enter to roll the dice: ')
            self.dice.roll()
            # Handle forced rolls.
            while self.force_roll and sum(self.dice) != self.force_roll:
                self.dice.roll()
            self.force_roll = 0
            # Deal with the results of the roll.
            self.human.tell('\n{} rolled {}.'.format(player.name, self.dice))
            self.resolve_bets()
            self.human.ask('Press enter to continue: ')
            self.human.tell()
        return False

    def do_gipf(self, arguments):
        """
        Look, I only speak two languages: English and Bad English.
        """
        game, losses = self.gipf_check(arguments, ('crazy eights',))
        # Crazy Eights forces the next roll to be an eight.
        if game == 'crazy eights':
            if not losses:
                self.human.tell('The next roll will be an eight.')
                self.force_roll = 8
        # Otherwise I'm confused.
        else:
            self.human.tell('Look, I only speak two languages: English and Bad English.')
        return True

    def do_quit(self, argument):
        """
        Stop playing Craps. (!)
        """
        # Determine overall winnings or losses.
        self.scores[self.human.name] -= self.stake
        # Determine if the game is a win or a loss.
        result = 'won'
        if self.scores[self.human.name] > 0:
            self.win_loss_draw[0] = 1
        elif self.scores[self.human.name] < 0:
            result = 'lost'
            self.win_loss_draw[1] = 1
        else:
            self.win_loss_draw[2] = 1
        # Inform the user.
        plural = utility.plural(abs(self.scores[self.human.name]), 'buck')
        self.human.tell('\nYou {} {} {}.'.format(result, abs(self.scores[self.human.name]), plural))
        # Quit the game.
        self.flags |= 4
        self.force_end = True

    def do_remove(self, argument):
        """
        Remove bets. (x)

        You will be shown a list of removable bets, from which you may pick one to
        remove. To remove all of your removable bets, use 'all' or 'a' as an argument
        to the bet command.
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
                plural = utility.plural(bet.wager, 'buck')
                player.tell('Removing your {} bet for {} {}.'.format(bet, bet.wager, plural))
                self.remove_bet(bet)
        else:
            # Show the bets.
            player.tell('\n---Removable Bets---\n')
            row_text = '{}: {} bet for {} {}.'
            for bet_index, bet in enumerate(removable):
                plural = utility.plural(bet.wager, 'buck')
                player.tell(row_text.format(bet_index, bet, bet.wager, plural))
            # Get the bet to remove.
            query = '\nWhich bet would you like to remove (-1 for none)? '
            choice = player.ask_int(query, low = -1, high = len(removable) - 1)
            # Remove or not as chosen.
            if choice == -1:
                pass
            else:
                bet = removable[choice]
                plural = utility.plural(bet.wager, 'buck')
                player.tell('Removing your {} bet for {} {}.'.format(bet, bet.wager, plural))
                self.remove_bet(bet)
        return True

    def do_roll(self, argument):
        """
        Finish the player's turn and roll. (r)

        If you finish your turn with the done command and you are the shooter, you
        will be asked to hit enter to roll. Using the roll command skips that. If you
        are not the shooter, the roll command. just ends your turn.
        """
        return self.do_done('r')

    def game_over(self):
        """Check for the end of the game. (bool)"""
        # The game is over when the human is out of money (and live bets).
        if self.scores[self.human.name] == 0 and not self.bets[self.human.name]:
            # Set the results.
            self.win_loss_draw[1] = 1
            self.scores[self.human.name] -= self.stake
            self.human.tell('\nYou lost all of your money.')
            return True
        else:
            return False

    def get_wager(self, bet):
        """
        Get the ammount to wager on the bet. (int)

        Parameters:
        bet: The bet to get the wager for. (CrapsBet)
        """
        # Calcuate the maximum allowed bet.
        max_bet = bet.max_bet(self.limit, self.limit * self.max_payout)
        player_max = int(self.scores[bet.player.name] / (1 + bet.commission))
        max_bet = min(player_max, max_bet)
        # Get the bet (or not).
        if max_bet:
            query = 'How much would you like to bet (max = {})? '.format(max_bet)
            wager = bet.player.ask_int(query, low = 1, high = max_bet, cmd = False)
        else:
            wager = 0
            bet.player.error('That is not a valid bet at this time.')
        # Set the bet.
        bet.set_wager(wager)
        self.scores[bet.player.name] -= wager
        if bet.commission:
            commission = int(math.ceil(wager * bet.commission))
            bet.player.tell('The bank charges a {} dollar commission on that bet.'.format(commission))
            self.scores[bet.player.name] -= commission

    def handle_options(self):
        """Handle the specified options. (None)"""
        super(Craps, self).handle_options()
        # Handle maximums for odds bets.
        if self.odds_max != 345:
            self.odds_multiples = {roll: self.odds_max for roll in (4, 5, 6, 8, 9, 10)}
        # Set the field bet payouts.
        new_field = {}
        if self.cars_pay_3:
            new_field[12] = (3, 1)
        if self.yo_pays_2:
            new_field[11] = (2, 1)
        if new_field:
            field_special = {2: (2, 1), 12: (2, 1)}
            field_special.update(new_field)
            PropositionBet.prop_bets['field'] = ((2, 3, 4, 9, 10, 11, 12), 1, 1, field_special)

    def next_shooter(self):
        """"Determine the next shooter and the next player (better). (None)"""
        # Check for new players.
        if len(self.players) < self.max_players and random.random() < (1 / len(self.players)):
            newbie = random.choice(self.bot_classes)(self.scores.keys())
            newbie.game = self
            newbie.set_up()
            self.players.append(newbie)
            self.scores[newbie.name] = self.stake
            self.bets[newbie.name] = []
            self.human.tell('\n{} has joined the game.\n'.format(newbie.name))
        # Go to the next player who has money to bet.
        while True:
            self.shooter_index = (self.shooter_index + 1) % len(self.players)
            if self.scores[self.players[self.shooter_index].name]:
                break
        # Set the next person to the shooter, assuming end of turn will adjust it to the next player.
        self.player_index = self.shooter_index

    def player_action(self, player):
        """
        Handle any actions by the current player. (bool)

        Parameters:
        player: The current player. (player.Player)
        """
        # Check for no output yet.
        if not self.turns and not sum(self.bets.values(), []):
            self.human.tell()
        # Check for removing a player.
        if not (self.scores[player.name] or self.bets[player.name]):
            self.players.remove(player)
            self.human.tell('\n{} dropped out due to lack of funds.\n'.format(player.name))
            self.player_index -= 1
            if self.shooter_index > self.player_index:
                self.shooter_index -= 1
            return False
        # Pass the dice if the shooter has no money for a pass/don't pass bet.
        elif self.shooter_index == self.player_index and not self.validate_shooter(player):
            for bet in self.bets[player.name]:
                if 'pass' in bet.match_text and not bet.number:
                    break
            else:
                self.next_shooter()
                return False
        # Display the game status.
        player.tell(str(self))
        # Get the bet or other command.
        raw_bet = player.ask('\nWhat kind of bet would you like to make? ')
        if not raw_bet.strip():
            raw_bet = 'done'
        return self.handle_cmd(raw_bet)

    def remove_bet(self, bet):
        """
        Remove a bet from play. (None)

        Parameters:
        bet: The bet to remove. (CrapsBet)
        """
        # Find the bet.
        player_name = bet.player.name
        bets = self.bets[player_name]
        # Refund the wager.
        self.scores[player_name] += bet.wager
        self.scores[player_name] += int(math.ceil(bet.wager * bet.commission))
        # Remove the bet and any associated odds bet.
        bets.remove(bet)
        if bet.odds_bet:
            self.remove_bet(bet.odds_bet)

    def resolve_bets(self):
        """Resolve player bets after a roll. (None)"""
        # Loop through the player bets.
        for player in self.players:
            for bet in self.bets[player.name][:]:  # loop through copy to allow changes.
                payout = bet.resolve(self.dice)
                if payout > 0:
                    message = '{} won {} {} on their {}.'
                    plural = utility.plural(payout, 'buck')
                    self.human.tell(message.format(player.name, payout, plural, bet))
                    self.scores[player.name] += payout + bet.wager
                    self.bets[player.name].remove(bet)
                elif payout < 0:
                    message = '{} lost {} {} on their {}.'
                    plural = utility.plural(bet.wager, 'buck')
                    self.human.tell(message.format(player.name, bet.wager, plural, bet))
                    self.bets[player.name].remove(bet)
        # Set the point and shooter.
        if self.point:
            if sum(self.dice) == self.point:
                self.point = 0
            elif sum(self.dice) == 7:
                self.point = 0
                self.next_shooter()
        elif sum(self.dice) in (4, 5, 6, 8, 9, 10):
            self.point = sum(self.dice)

    def set_options(self):
        """Set the game options. (None)"""
        # Set the money options.
        self.option_set.add_option('stake', ['s'], int, 100, check = lambda bucks: bucks > 0,
            question = 'How much money would you like to start with (return for 100)? ')
        self.option_set.add_option('limit', ['l'], int, 8, check = lambda bucks: 0 < bucks,
            question = 'What should the maximum bet be (return for 8)? ')
        # Set the wager options
        self.option_set.add_option('max-payout', ['m$'], int, 3, check = lambda times: 1 <= times,
            question = 'What multiple of the maximum bet should the maximum payout be (return for 3)? ')
        self.option_set.add_option('odds-max', ['om'], int, 345, check = lambda times: 1 <= times,
            question = 'What multiple of the max bet should be the max for odds bets (return for 3-4-5)? ')
        # Set the payout options.
        self.option_set.add_option('lazy-hard', ['lh'],
            question = 'Should hard ways bets be off on the come out roll? bool')
        self.option_set.add_option('cars-pay-3', ['c3'],
            question = 'Should 12 pay 3:1 on field bets? bool')
        self.option_set.add_option('yo-pays-2', ['y2'], question = 'Should 11 pay 2:1 on field bets? bool')
        # Set the bot options.
        self.option_set.add_option('max-players', ['mp'], int, 7, valid = range(1, 21),
            question = 'How many players should be able to play (return for 7)? ')

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the bots.
        self.bot_classes = []
        classes = [CrapsBot]
        while classes:
            cls = classes.pop()
            self.bot_classes.append(cls)
            classes.extend(cls.__subclasses__())
        # Set up the players.
        self.players = []
        taken_names = [self.human.name]
        while True:
            self.players.append(random.choice(self.bot_classes)(taken_names))
            taken_names.append(self.players[-1].name)
            if not random.randrange(self.max_players - len(self.players)):
                break
        for player in self.players:
            player.game = self
        self.players.append(self.human)
        # Set up the tracking variables.
        self.scores = {player.name: self.stake for player in self.players}
        self.bets = {player.name: [] for player in self.players}
        self.shooter_index = len(self.players) - 1
        self.point = 0
        self.force_roll = 0
        # Set up the dice.
        self.dice = dice.Pool()
        # Set up the bets.
        self.bet_classes = {}
        classes = [CrapsBet]
        while classes:
            cls = classes.pop()
            self.bet_classes[cls.match_text] = cls
            for alias in cls.aliases:
                self.bet_classes[alias] = cls
            classes.extend(cls.__subclasses__())

    def validate_shooter(self, player):
        """
        Make sure the current shooter can make the necessary bets. (bool)

        Parameters:
        player: The potential shooter to validate. (player.Player)
        """
        if not self.scores[player.name] and not self.point:
            for bet in self.bets[player.name]:
                if bet.match('pass', 0) or bet.match("don't pass", 0):
                    return True
            return False
        else:
            return True


class CrapsBet(object):
    """
    A bet in a game of craps. (object)

    The validate method should return the text of any errors with the bet, or a
    blank string if the bet is valid.

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
        """Generate a debugging text representation. (str)"""
        text = '<{}'.format(self.__class__.__name__)
        if self.number:
            text += ' on {}'.format(self.number)
        return text + ' for {} bucks>'.format(self.wager)

    def __str__(self):
        """Generate a human readable text representation. (str)"""
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
        Calculate the maximum wager based on payout. (int)

        Parameters:
        limit: The maximum bet in the game. (int)
        max_payout: The maximum payout in the game. (int)
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
        # Check for lazy hard.
        if self.game.lazy_hard and not self.game.point:
            result = 0
        # Check for resolution.
        elif sum(roll) == self.number:
            if roll.values[0] == roll.values[1]:
                result = self.payout
            else:
                result = self.wager * -1
        # Otherwise play on.
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
            errors.append('{} bets can only be made on 4, 6, 8, or 10.'.format(self.raw_text))
        return ' '.join(errors)


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
        Determine if the bet won or lost. (int)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        result = 0
        roll = sum(roll)
        # Check with a number set.
        if self.number:
            if roll == self.number:
                result = self.payout
            elif roll == 7:
                result = -self.payout
        # Check with no number set.
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
        errors = []
        if self.game.point:
            errors.append('{} bets cannot be made when there is a point.'.format(self.raw_text))
        if self.number:
            errors.append('{} bets are not made with a number.'.format(self.raw_text))
        for bet in self.game.bets[self.player.name]:
            if bet.match(self.match_text, 0):
                errors.append('You can only have one open {} bet at a time.'.format(self.raw_text))
                break
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
        Determine if the bet won or lost. (int)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        # Don't check on come out roll unless it's a don't bet.
        if self.game.point or "don't" in self.match_text:
            # Resolve with parent class.
            number = self.number
            result = super(ComeBet, self).resolve(roll)
            # Catch the parent class setting the number.
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
        for bet in self.game.bets[self.player.name]:
            if bet.match(self.match_text, 0):
                errors.append('You can only have one open {} bet at a time.'.format(self.raw_text))
                break
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
        Determine if the bet won or lost. (int)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        # Push on a 12.
        if sum(roll) == 12:
            result = 0
        # Otherwise, reverse the standard result.
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
        # Push on a 12.
        if sum(roll) == 12:
            result = 0
        # Otherwise, reverse the standard result.
        else:
            result = -1 * super(DontPassBet, self).resolve(roll)
        return result


class OddsBet(PassBet):
    """
    An odds bet on a do/don't pass/come bet. (CrapsBet)

    Methods:
    come_resolve: Alternative resolve method for come bets. (int)
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
        # Set up bet handling based on bet type.
        if "don't" in self.parent.match_text:
            self.do_resolve = self.resolve
            self.resolve = self.dont_resolve
        elif self.parent.match_text == 'come':
            self.resolve = self.come_resolve

    def come_resolve(self, roll):
        """
        Determine if the bet won or lost. (int)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        # Don't resolve during come out roll.
        if self.game.point:
            return super(OddsBet, self).resolve(roll)
        else:
            return 0

    def dont_resolve(self, roll):
        """
        Determine if the bet won or lost. (int)

        Parameters:
        roll: The dice roll this turn. (Pool)
        """
        # Push on box cars.
        if sum(roll) == 12:
            result = 0
        # Otherwise reverse the standard resolution.
        else:
            result = -1 * self.do_resolve(roll)
        return result

    def max_bet(self, limit, max_payout):
        """
        Calculate the maximum odds wager. (int)

        Parameters:
        limit: The maximum bet in the game. (int)
        max_payout: The maximum payout in the game. (int)
        """
        # Get the payout based on parent bet's number.
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
        # Set the odds based on true odds.
        self.wager = wager
        multiplier, divisor = BUY_ODDS[self.number]
        # Reverse the odds for don't bets.
        if "don't" in self.parent.match_text:
            multiplier, divisor = divisor, multiplier
        self.payout = int(wager * multiplier / divisor)

    def validate(self):
        """Check that the bet is valid. (str)"""
        return ''


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
        # Check for the number before a seven.
        if sum(roll) == self.number:
            result = self.payout
        elif sum(roll) == 7:
            result = -1 * self.payout
        # Reverse payouts for lay bets.
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
        # Get odds based on bet type.
        if self.match_text == 'place':
            odds = PLACE_ODDS
        else:
            odds = BUY_ODDS
        multiplier, divisor = odds[self.number]
        # Reverse odds for lay bets.
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

    prop_aliases = {'2': '2', '2 or 12': 'hi-lo', '3': '3', '6': '6', '7': '7', '8': '8', '11': 'yo',
        '12': '12', 'ace-duece': '3', 'aces': '2', 'any 7': '7', 'any craps': 'craps', 'boxcars': '12',
        'c&e': 'c & e', 'c & e': 'c & e', 'cornrows': '12', 'craps': 'craps', 'field': 'field',
        'hi-lo': 'hi-lo', 'hi-low': 'hi-lo', 'high-lo': 'hi-lo', 'high-low': 'hi-lo', 'horn': 'horn',
        'midnight': '12', 'snake-eyes': '2', 'three-way': 'craps', 'whirl': 'whirl', 'world': 'whirl',
        'yo': 'yo'}
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

    def __repr__(self):
        """Generate a computer readable text representation. (str)"""
        return '<PropositionBet ({}) for {} bucks>'.format(self.match_text.capitalize(), self.wager)

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
        # Check for special odds.
        if sum(roll) in self.special_odds:
            multiplier, divisor = self.special_odds[sum(roll)]
            result = int(self.wager * multiplier / divisor)
        # Otherwise check targets.
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


class CrapsBot(player.Bot):
    """
    A bot to play Craps with. (player.Bot)

    Class Attributes:
    bet_type: The main type of bet to make. (str)
    max_re: A regex for getting the max bet from a question. (SRE_Pattern)

    Attributes:
    last_act: The last action taken by the bot. (int)

    Overridden Methods:
    ask
    ask_int
    error
    set_up
    tell
    """

    bet_type = "don't pass"
    max_re = re.compile('\d+')

    def ask(self, prompt):
        """
        Ask the bot a question. (str)

        Parameters:
        prompt: The queston to ask. (str)
        """
        if prompt.startswith('\nWhat kind of bet'):
            # Make pass or don't pass bets, and then odds bets on them.
            my_bets = self.game.bets[self.name]
            # Mandatory actions based on errors.
            if self.last_act[:4] == 'must':
                self.last_act = self.last_act[5:]
            # One bet per round, when you can.
            elif not self.game.scores[self.name] or self.last_act == 'wager':
                self.last_act = 'done'
            # Make the primary bet if no bet.
            elif not my_bets:
                self.last_act = self.bet_type
            # Make an odds bet if there is a bet.
            elif my_bets and self.game.point and not my_bets[0].odds_bet:
                self.last_act = "{} odds {}".format(self.bet_type, my_bets[0].number)
            else:
                return 'done'
            return self.last_act
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
        # Find the maximum possible bet.
        max_bet = int(self.max_re.search(args[0]).group())
        wager = min(max_bet, self.game.scores[self.name])
        # Make that bet.
        message = "{} made a {} bet for {} bucks."
        self.game.human.tell(message.format(self.name, self.last_act, wager))
        # Track making a bet.
        self.last_act = 'wager'
        return wager

    def error(self, message):
        """
        Handle error warnings from the game. (None)

        Parameters:
        message: The error warning. (str)
        """
        # Dictate the next action based on the error.
        if message.startswith('You can only have'):
            self.last_act = 'must done'
        elif message.startswith('You must have a'):
            self.last_act = "must don't pass"
        elif message.startswith('You have already'):
            self.last_act = 'must done'
        else:
            # Raise error on unrecognized errors.
            super(CrapsBot, self).error(message)

    def set_up(self):
        """Set up bot specific attributes."""
        self.last_act = ''

    def tell(self, *args, **kwargs):
        """
        Ask the bot for an integer. (int)

        Parameters:
        the parameters are ingored.
        """
        pass


class OverBot(CrapsBot):
    """
    A bot that slowly puts its whole stake on the table. (CrapsBot)

    Overridden Methods:
    ask
    """

    # The main type of bet to make.
    bet_type = ("don't pass", "don't come")

    def ask(self, prompt):
        """
        Ask the bot a question. (str)

        Parameters:
        prompt: The queston to ask. (str)
        """
        if prompt.startswith('\nWhat kind of bet'):
            # Get bet data for making a decision.
            my_bets = self.game.bets[self.name]
            oddsable = []
            for bet in my_bets:
                if not bet.odds_bet and bet.match_text[-4:] in ('pass', 'come') and bet.number:
                    oddsable.append(bet)
            # Take mandated actions after errors.
            if self.last_act[:4] == 'must':
                self.last_act = self.last_act[5:]
            # One bet per round.
            elif not self.game.scores[self.name] or self.last_act == 'wager':
                self.last_act = 'Done'
            # Make primary bet if not already done when shooting.
            elif not self.game.point and self.game.players[self.game.shooter_index] == self:
                for bet in my_bets:
                    if bet.match(self.bet_type[0], 0):
                        self.last_act = 'done'
                        break
                else:
                    self.last_act = self.bet_type[0]
            # Make an odds bet.
            elif oddsable:
                self.last_act = "{} odds {}".format(oddsable[0].match_text, oddsable[0].number)
            # Otherwise make secondary bet if there is a point.
            elif self.game.point:
                self.last_act = self.bet_type[1]
            # Make the primary bet otherwise.
            else:
                for bet in my_bets:
                    if bet.match(self.bet_type[0], 0):
                        self.last_act = 'done'
                        break
                else:
                    self.last_act = self.bet_type[0]
            return self.last_act
        elif prompt.startswith('You are the shooter.'):
            return '{} needs a new pair of shoes!'.format(self.name)
        else:
            raise player.BotError('Unexpected question to CrapsBot: {!r}'.format(prompt))


class OverPoliteBot(OverBot):
    """A bot that politely puts its whole stake on the board. (OverBot)"""

    # The main type of bet to make.
    bet_type = ('pass', 'come')


class OverSemiPoliteBot(OverBot):
    """A bot that somewhat politely puts its whole stake on the board. (OverBot)"""

    # The main type of bet to make.
    bet_type = ('pass', "don't come")


class PoliteBot(CrapsBot):
    """A bot that roots for the shooter. (CrapsBot)"""

    # The main type of bet to make.
    bet_type = 'pass'


class Randy(CrapsBot):
    """
    A bot that bets completely randomly. (CrapsBot)

    Class Attributes:
    any_times: Names of bets that can be made any time. (tuple of str)
    post_point: Names of bets that can only be made before a point. (tuple of str)
    pre_point: Names of bets that can only be made after a point. (tuple of str)

    Overridden Methods:
    ask
    ask_int
    """

    any_time = ('place x', 'buy x', 'lay x', 'proposition x', 'hard x')
    post_point = ('come', "don't come")
    pre_point = ('pass', "don't pass", 'done')

    def ask(self, prompt):
        """
        Ask the bot a question. (str)

        Parameters:
        prompt: The queston to ask. (str)
        """
        if prompt.startswith('\nWhat kind of bet'):
            # Get data for making a decision.
            my_bets = self.game.bets[self.name]
            oddsable = []
            for bet in my_bets:
                if not bet.odds_bet and bet.match_text[-4:] in ('pass', 'come') and bet.number:
                    oddsable.append(bet)
            # Take mandatory actions from errors.
            if self.last_act[:4] == 'must':
                self.last_act = self.last_act[5:]
            # One bet per roll.
            elif not self.game.scores[self.name] or self.last_act == 'wager':
                self.last_act = 'Done'
            # Make a random required bet if you're the shooter.
            elif not self.game.point and self.game.players[self.game.shooter_index] == self:
                for bet in my_bets:
                    if bet.match('pass', 0) or bet.match("don't pass", 0):
                        self.last_act = 'done'
                        break
                else:
                    self.last_act = random.choice(('pass', "don't pass"))
            # Make an odds bet haflt the time.
            elif oddsable and random.random() > 0.5:
                self.last_act = "{} odds {}".format(oddsable[0].match_text, oddsable[0].number)
            # Make a random bet if there is a point.
            elif self.game.point:
                for bet in my_bets:
                    if bet.match('pass', 0) or bet.match("don't pass", 0):
                        self.last_act = 'done'
                        break
                else:
                    self.last_act = random.choice(self.post_point + self.any_time)
            # Otherwise make a random bet half the time.
            elif random.random() > 0.5:
                self.last_act = random.choice(self.pre_point + self.any_time)
            else:
                self.last_act = 'done'
            # Pick a random number when necessary.
            if self.last_act.endswith('x'):
                if self.last_act.startswith('prop'):
                    prop_bet = random.choice(list(PropositionBet.prop_bets.keys()))
                    self.last_act = self.last_act.replace('x', prop_bet)
                elif self.last_act.startswith('hard'):
                    self.last_act = self.last_act.replace('x', random.choice(('4', '6', '8', '10')))
                else:
                    number = random.choice(('4', '5', '6', '8', '9', '10'))
                    self.last_act = self.last_act.replace('x', number)
            return self.last_act
        elif prompt.startswith('You are the shooter.'):
            return '{} needs a new pair of shoes!'.format(self.name)
        else:
            raise player.BotError('Unexpected question to CrapsBot: {!r}'.format(prompt))

    def ask_int(self, *args, **kwargs):
        """
        Ask the bot for an integer. (int)

        Parameters:
        the parameters are ingored.
        """
        # Make a random bet.
        max_bet = min(int(self.max_re.search(args[0]).group()), self.game.scores[self.name])
        wager = random.randint(1, max_bet)
        # Inform the human.
        message = "{} made a {} bet for {} bucks."
        self.game.human.tell(message.format(self.name, self.last_act, wager))
        # Track making the bet.
        self.last_act = 'wager'
        return wager


if __name__ == '__main__':
    # Play Craps without the full interface.
    import t_games.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    craps = Craps(player.Humanoid(name), '')
    print(craps.play())
