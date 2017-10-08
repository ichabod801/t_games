"""
roulette_game.py

Classes:
Roulette: A game of roulette. (game.Game)
"""


import random
import time

import tgames.game as game
import tgames.utility as utility


class Roulette(game.Game):
    """
    A game of roulette.

    Class Attributes:
    black: The black numbers. (list of str)
    red: The red numbers. (list of str)

    Attributes
    bets: Bets made this round. (list of tuple)
    layout: American or French layout. (str)
    numbers: The numbers on the wheel. (list of str)
    stake: The starting money the player gets. (int)

    Methods:
    check_bet: Do common checking for valid bets. (str, int)
    do_spin: Spin the wheel. (bool)
    do_straight: Make a bet on a single number. (bool)

    Overridden Methods:
    handle_options
    player_turn
    set_up
    """

    aliases = {'single': 'straight'}
    black = ['2', '4', '6', '8', '10', '11', '13', '15', '17', '20', '22', '24', '26', '28', '29', '31',
        '33', '35']
    categories = ['Gambling Games', 'Other Games']
    name = 'Roulette'
    num_options = 2
    red = ['1', '3', '5', '7', '9', '12', '14', '16', '18', '19', '21', '23', '25', '27', '30', '32', '34', 
        '36']

    def check_bet(self, arguments):
        """
        Do common checking for valid bets. (str, int)

        This checks the valid number of arguments and a valid bet amount. The
        specific bet method will need to check that the thing being bet on is valid.

        Parameters:
        arguments: The arguments to the bet command. (str)
        """
        args = arguments.split()
        if len(args) != 2:
            self.human.tell('Invalid number of arguments to a bet command.')
        else:
            target, bet = args
            if bet.isdigit():
                bet = int(bet)
                max_bet = min(self.max_bet, self.scores[self.human.name])
                if 1 <= bet <= max_bet:
                    return target, bet
                else:
                    self.human.tell('That bet is too large. You may only bet {} bucks.'.format(max_bet))
            else:
                self.human.tell('All bets must be decimal integers.')
        return '', 0

    def do_quit(self, arguments):
        """
        Stop playing before losing all your money. (bool)

        Parameters:
        arguments: The number of the hand to hit. (str)
        """
        self.flags |= 4
        if self.scores[self.human.name] > self.stake:
            self.win_loss_draw[0] = 1
            self.force_end = 'win'
        elif self.scores[self.human.name] < self.stake:
            self.win_loss_draw[1] = 1
            self.force_end = 'draw'
        else:
            self.win_loss_draw[2] = 1
            self.force_end = 'loss'
        return False

    def do_split(self, arguments):
        """
        Make a bet on a two adjacent numbers. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        numbers, bet = self.check_bet(arguments)
        if numbers:
            pair = numbers.split('-')
            if len(pair) != 2:
                self.human.tell('You must enter two numbers for a split bet.')
            elif pair[0] not in numbers:
                self.human.tell('{} is not in this layout.'.format(pair[0]))
            elif pair[1] not in numbers:
                self.human.tell('{} is not in this layout.'.format(pair[1]))
            else:
                low = int(pair[0])
                high = int(pair[1])
                if low and high and abs(high - low) in (1, 3):
                    self.scores[self.human.name] -= bet
                    self.bets.append(('split', pair, bet))
                else:
                    self.human.tell('{} and {} are not adjacent on the layout.'.format(low, high))
        return True

    def do_straight(self, arguments):
        """
        Make a bet on a single number. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        number, bet = self.check_bet(arguments)
        if number:
            if number not in self.numbers:
                self.human.tell('That number is not in this layout.')
            else:
                self.scores[self.human.name] -= bet
                self.bets.append(('straight', number, bet))
        return True

    def do_spin(self, arguments):
        """
        Spin the wheel. (bool)

        Parameters:
        arguments: The ignored arguments to the command. (str)
        """
        for spin in range(random.randint(3, 5)):
            self.human.tell('Spinning...')
            time.sleep(1)
        self.human.tell('Clickety clackity...')
        time.sleep(1)
        winner = random.choice(self.numbers)
        self.human.tell('The winning number is {}.'.format(winner))
        self.pay_out(winner)

    def game_over(self):
        """Determine the end of game. (bool)"""
        if self.scores[self.human.name] == 0:
            self.win_loss_draw[1] = 1
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options. (None)"""
        self.layout = 'American'
        self.numbers = [str(number) for number in range(37)]
        self.stake = 100
        self.max_bet = 10
        if self.raw_options.lower() == 'none':
            pass
        elif self.raw_options:
            self.flags |= 1
            for word in self.raw_options.lower().split():
                if word == 'american':
                    self.layout = 'American'
                elif word == 'french':
                    self.layout = 'French'
                elif '=' in word:
                    option, value = word.split('=')
                    if option == 'stake':
                        if value.isdigit():
                            self.stake = int(value)
                        else:
                            self.human.tell('Invalid value for stake= option: {!r}'.format(value))
                    elif option == 'max-bet':
                        if value.isdigit():
                            self.stake = int(value)
                        else:
                            self.human.tell('Invalid value for max-bet= option: {!r}'.format(value))
                    else:
                        self.human.tell('Invalid option for roulette: {}=.'.format(option))
                else:
                    self.human.tell('Invalid option for roulette: {}.'.format(word))
        else:
            if self.human.ask('Would you like to change the options? ') in utility.YES:
                self.flags |= 1
                query = 'French or American (return for American)? '
                layouts = ['french', 'american']
                self.layout = self.human.ask_valid(query, valid = layouts, default = 'american')
                query = 'What stake do you want to start with? '
                self.stake = self.human.ask_int(query, low = 1, default = 100, cmd = False)
        if self.layout == 'american':
            self.numbers.append('00')

    def pay_out(self, winner):
        """
        Payout all bets. (None)

        Parameters:
        winner: The winning number. (str)
        """
        total_winnings = 0
        for bet_type, target, bet in self.bets:
            winning = getattr(self, 'winning_{}'.format(bet_type))
            payout = winning(target)
            if payout:
                self.human.tell('Your {} bet on {} won!'.format(bet_type, target))
                winnings = payout * bet
                self.human.tell('You won {} bucks!'.format(winnings))
                self.scores[self.human.name] += winnings
                total_winnings += winnings
            else:
                self.human.tell('Your {} bet on {} lost.'.format(bet_type, target))
        self.bets = []
        if total_winnings:
            self.human.tell('Your total winnings this spin were {} bucks.'.format(total_winnings))
        else:
            self.human.tell('You did not win anything this spin.')

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        player.tell('\nYou have {} bucks.'.format(self.scores[player.name]))
        move = player.ask('Enter a bet or spin: ')
        return self.handle_cmd(move)

    def set_up(self):
        """Set up the game. (None)"""
        self.scores = {self.human.name: self.stake}
        self.bets = []

    def winning_split(tself, arget, winner):
        """
        Check a split bet for winning. (int)

        Parameters:
        target: The two numbers being bet on. (tuple of str)
        winner: The winning number. (str)
        """
        if winner in target:
            return 17
        else:
            return 0

    def winning_straight(self, target, winner):
        """
        Check a straight bet for winning. (int)

        Parameters:
        target: The number being bet on. (str)
        winner: The winning number. (str)
        """
        if winner == target:
            return 35
        else:
            return 0

