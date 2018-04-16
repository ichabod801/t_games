"""
craps_game.py

A game of Craps.

!! look into the standard casino play order, and try to mimic that.
!! standard order is anyone can bet, shooter rolls, bets payed out.

Classes:
Craps: A game of Craps. (game.Game)
"""


import tgames.dice as dice
import tgames.game as game


class Craps(game.Game):
    """
    A game of Craps. (game.Game)

    Basic play is that every one gets a chance to bet, then the shooter throws,
    and then bets are resolved.

    Attributes:
    bets: The bets the players have made this round. (dict of str: dict)
    dice: The dice that get rolled. (dice.Pool)
    limit: The maximum bet that can be made. (int)
    point: The point to be made, or zero if no point yet. (int)
    shooter_index: Index of the current shooter in self.players. (int)
    stake: How much money the players start with. (int)

    Class Attributes:
    bet_aliases: Different names for the various bets. (dict of str: str)

    Methods:
    do_done: Finish the player's turn. (bool)

    Overridden Methods:
    set_options
    set_up
    """

    def do_done(self, argument):
        """
        Finish the player's turn. (bool)

        Parameters:
        argument: The (ignored) argument to the done command. (str)
        """
        player = self.players[self.player_index]
        if self.player_index == self.shooter_index:
            player.error('You are the shooter. You must roll before ending your turn.')
            return True
        else:
            return False

    def player_action(self, player):
        """
        Handle any actions by the current player. (bool)

        Parameters:
        player: The current player. (player.Player)
        """
        bet = player.ask('What sort of bet would you like to make? ')
        if bet.lower() in self.bet_alliases:
            bet = self.bet_alliases[bet.lower()]
            if bet in ('pass', "don't pass") and point:
                player.error('That bet cannot be made after the point has been established.')
            elif bet in ('come', "don't come") and not point:
                player.error('That bet cannot be made before the point has been established.')
            else:
                wager = player.ask_int('How much would you like to wager? ')
                # !! not sure about maximums.

    def set_options(self):
        """Set the game options. (None)"""
        # Betting options.
        self.option_set.add_option('stake', [], int, 100, check = lambda bucks: bucks > 0,
            question = 'How much money would you like to start with (return for 100)? ')
        self.option_set.add_option('limit', [], int, 8, check = lambda bucks: 0 < bucks,
            question = 'What should the maximum bet be (return for 8)? ')

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the tracking variables.
        self.scores = {player.name: self.stake for player in self.players}
        self.bets = {player.name: {} for player in self.players}
        self.shooter_index = len(self.players) - 1
        self.point = 0
        # Set up the dice.
        self.dice = dice.Pool()