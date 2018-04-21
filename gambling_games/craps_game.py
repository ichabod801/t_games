"""
craps_game.py

A game of Craps.

!! look into the standard casino play order, and try to mimic that.
!! standard order is anyone can bet, shooter rolls, bets payed out.

max bet notes:
line bet: pass/don't pass
proposition bets are one roll bets (for hard or easy?)
field bets: that the next total will be x
place/buy bets: That a given number will show before the next 7
big six and big 8: Bet that a six or eight comes before a 7 (one or two bets? two)
available bets:
    pass/don't pass
    free-odds on line
    come/don't come
    free-odds on come
    place numbers
    buy bets
    lay bets
    field numbers
    big six/big 8
    center or proposition bets.
pass/don't pass: before point
    7 or 11 pass wins even, don'ts lose.
    2, 3, 12 (craps): pass wins, 2 or 12 pushes depending on casino, dont's win.
    other rolls is point, pass/don't pass bets remain.
    pass/don't pass convert to point/seven (?)
    only a 7 after point is made changes the shooter.
odds bet: bet behind pass after point, but only if on pass or don't pass.
    additional bet that the point will be made.
    4/10 pays 2:1
    5/Nine pays 3:2
    Six/8 pays 6:5
    3-4-5x odds tables: 3x for 4/10, 4x for 5/Nine, 5x for Six/8
        multiple of pass bet.
        some casinos offer higher.
        can increase, decrease or remove odds bet at any point.
come/don't come:
    only bet after point is determined.
    must play pass/don't pass to make this bet. Not clear if don't has to match. Assume not.
    if the roll after is 4, 5, six, 8, nine, or 10, your bet gets moved to that number
        this establishes a personal point for you.
    if the shooter rolls that before a seven, you win
    if the shooter rolls a seven, you lose.
    you can place odds on a come bet.
    once your bet is placed on your come point, you can place an additional come bet.
place number bets:
    bet that a particular number will appear before a seven. After come roll.
    placed in the rectangles just below the place-number boxes.
    4/10 pay 9:5, 5/nine pay 7-5; six/8 pay 7-6.
    valid on all rolls except come out rolls.
buy bets:
    as place number bets.
    casino takes 5% on top of the bet, bet pays out true odds.
    placed in upper third of place number boxes.
    valid on all rolls except come out rolls.
lay bets:
    similar to don't-place-number. Betting a seven will come before that number.
    betting and payout as buy bets.
    placed in upper third porthion of the rectangles farthes above the place number boxes, at top of layout
field bets:
    bets that one number will be rolled next.
    can be made on come out roll.
    six/8 pays 7:6.
    4/6/8/10 hard way: Must come up as pair before a seven or a non-pair of that number.
big six/big 8:
    bet on 6 or 8 (either) coming before a seven. Pays even. Play at any time.
center/proposition bets:
    Determined by next roll, except hardways with stay until that number is rolled and lose if not a pair.
    any 7: 4 to 1
    any craps: 7 to 1
    2 or 12: 30 to 1
    3 or 11: 15 to 1
    hardway 4/10: 7 to 1
    hardway 6/8: 9 to 1
    horn: 2, 3, 11, and 12.
    c&e bet: any craps plus 11.

Classes:
Craps: A game of Craps. (game.Game)
CrapsBot: A bot to play Craps against. (player.Bot)
"""


import tgames.dice as dice
import tgames.game as game
import tgames.player as player


CREDITS = """
Game Design: Barnard Xavier Phillippe de Marigny de Mandeville
Game Programming: Craig "Ichabod" O'Brien
"""


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

    Methods:
    do_done: Finish the player's turn. (bool)
    resolve_bets: Resolve player bets after a roll. (None)
    resolve_call: Resolve call bets. (None)
    resolve_dont_call: Resolve don't call bets. (None)
    resolve_dont_pass: Resolve don't pass bets. (None)
    resolve_pass: Resolve pass bets. (None)

    Overridden Methods:
    game_over
    player_action
    set_options
    set_up
    """

    bet_aliases = {'come': 'come', "don't come": "dont_come", "don't pass": "dont_pass", 
        'pass': 'pass', 'right': 'pass', 'wrong': 'dont_pass'}
    bet_maxes = {'come': 1, "dont_come": 1, "dont_pass": 1, 'pass': 1}
    categories = ['Gambling Games', 'Dice Games']
    name = 'Craps'
    num_options = 2
    reverse_bet = {'win': 'lose', 'lose': 'win', 'hold': 'hold'}

    def do_done(self, argument):
        """
        Finish the player's turn. (bool)

        Parameters:
        argument: The (ignored) argument to the done command. (str)
        """
        player = self.players[self.player_index]
        if self.player_index == self.shooter_index:
            # If it's the shooter's turn, have them roll the dice.
            player.ask('You are the shooter. Press enter to roll the dice: ')
            self.dice.roll()
            self.human.tell('\n{} rolled {}.'.format(player.name, self.dice))
            self.resolve_bets()
        return False

    def game_over(self):
        """Check for the end of the game. (bool)"""
        if self.scores[self.human.name] == 0 and not self.bets[self.human.name]:
            self.win_loss_draw[1] = 1
            return True
        else:
            return False

    def player_action(self, player):
        """
        Handle any actions by the current player. (bool)

        Parameters:
        player: The current player. (player.Player)
        """
        # Display the game status.
        # Display shooter and point.
        if self.point:
            point_text = 'point = {}'.format(self.point)
        else:
            point_text = 'off'
        player.tell('\nThe shooter is {} ({}).'.format(self.players[self.shooter_index].name, point_text))
        # Display outstanding bets.
        s = ['s', ''][len(self.bets[player.name]) == 1]
        bet_total = sum(wager for bet, wager in self.bets[player.name])
        message = 'You have {} bet{} in play totalling {} dollars.'
        player.tell(message.format(len(self.bets[player.name]), s, bet_total))
        # Display remaining money.
        player.tell('You have {} dollars remaining to bet.\n'.format(self.scores[player.name]))
        # Get the player action.
        raw_bet = player.ask('What sort of bet would you like to make? ')
        if raw_bet.lower() in self.bet_aliases:
            # Check for bet being valid at this time.
            bet = self.bet_aliases[raw_bet.lower()]
            if bet in ('pass', 'dont_pass') and self.point:
                player.error('That bet cannot be made after the point has been established.')
            elif bet in ('come', 'dont_come') and not self.point:
                player.error('That bet cannot be made before the point has been established.')
            else:
                # Get the wager.
                max_bet = min(self.limit * self.bet_maxes[bet], self.scores[player.name])
                wager = player.ask_int('How much would you like to wager? ', low = 1, high = max_bet)
                # Store the bet.
                self.bets[player.name].append((raw_bet, wager))
                self.scores[player.name] -= wager
            return True
        else:
            # Handle other commands
            return self.handle_cmd(raw_bet)

    def resolve_bets(self):
        """Resolve player bets after a roll. (None)"""
        # Loop through the player bets.
        for player in self.players:
            for raw_bet, wager in self.bets[player.name][:]: # loop through copy to allow changes.
                # Get the bet details.
                raw_bet, slash, number = raw_bet.partition('/')
                bet = self.bet_aliases[raw_bet.lower()]
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
            number = int(number)
            if number == sum(self.dice):
                status = 'win'
            elif sum(self.dice) == 7:
                status = 'lose'
        else:
            status = 'point'
        # Reverse the status if necessary.
        if reverse:
            status = self.reverse_bet.get(status, status)
        # Handle winning the bet.
        if status == 'win':
            self.scores[player.name] += wager * 2
            self.bets[player.name].remove((bet, wager))
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

    def resolve_dont_come(self, player, raw_bet, wager):
        """
        Resolve don't come bets. (None)

        Parameters:
        player: The player who made the don't come bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the come bet. (wager)
        """
        self.resolve_call(player, raw_bet, wager, reverse = True)

    def resolve_dont_pass(self, player, raw_bet, wager):
        """
        Resolve don't pass bets. (None)

        Parameters:
        player: The player who made the don't pass bet. (player.Player)
        raw_bet: The name used for the bet. (str)
        wager: The amount of the pass bet. (wager)
        """
        self.resolve_pass(player, raw_bet, wager, reverse = True)

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
        if reverse:
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

    def set_options(self):
        """Set the game options. (None)"""
        # Betting options.
        self.option_set.add_option('stake', [], int, 100, check = lambda bucks: bucks > 0,
            question = 'How much money would you like to start with (return for 100)? ')
        self.option_set.add_option('limit', [], int, 8, check = lambda bucks: 0 < bucks,
            question = 'What should the maximum bet be (return for 8)? ')

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
        return min(self.game.limit, self.game.scores[self.name])

if __name__ == '__main__':
    import tgames.player as player
    try:
        input = raw_input
    except NameError:
        pass
    name = input('What is your name? ')
    craps = Craps(player.Player(name), '')
    print(craps.play())