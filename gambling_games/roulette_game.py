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

    aliases = {'double-street': 'double', 'first': 'basket', 'single': 'straight', 'six': 'double', 
        'six-line': 'double'}
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

    def check_two_numbers(self, pair, bet_type):
        """
        Check for two numbers in the layout. (bool)

        Parameters:
        pair: The two numbers separated by a dash. (str)
        bet_type: The type of bet trying to be made. (str)
        """
        pair = pair.split('-')
        if len(pair) != 2:
            self.human.tell('You must enter two numbers for a {} bet.'.format(bet_type))
        elif pair[0] not in self.numbers:
            self.human.tell('{} is not in this layout.'.format(pair[0]))
        elif pair[1] not in self.numbers:
            self.human.tell('{} is not in this layout.'.format(pair[1]))
        else:
            return True
        return False

    def do_basket(self, arguments):
        """
        Make a four number bet incluidng 0. (bool)

        Parameters:
        arguments: The ammount to bet. (str)
        """
        words = arguments.split()
        if words[0].lower() != 'four':
            words = ['basket'] + words
        numbers, bet = self.check_bet(' '.join(words))
        if numbers and self.layout == 'french':
            self.scores[self.human.name] -= bet
            self.bets.append(('basket bet', ('0', '1', '2', '3'), bet))
        elif numbers:
            self.human.tell('That bet can only be made on a French layout.')
        return True

    def do_black(self, arguments):
        """
        Bet on black. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('black {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            self.bets.append(('black bet', self.black, bet))
        return True

    def do_column(self, arguments):
        """
        Bet on a column. (bool)

        Parameters:
        arguments: The column and the bet. (str)
        """
        column, bet = self.check_bet(arguments)
        if column:
            targets = []
            if column.lower() in ('1', 'p', 'f'):
                targets = [str(number) for number in range(1, 37, 3)]
            elif column.lower in ('2', 'm', 's'):
                targets = [str(number) for number in range(2, 37, 3)]
            elif column.lower in ('3', 'd', 't'):
                targets = [str(number) for number in range(2, 37, 3)]
            if targets:
                self.scores[self.human.name] -= bet
                self.bets.append(('column bet on {}'.format(column), targets, bet))
            else:
                self.human.tell('That is not a valid column. Please use 1/2/3, P/M/D, or F/S/T.')
        return True

    def do_corner(self, arguments):
        """
        Make a bet on a square of numbers. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        numbers, bet = self.check_bet(arguments)
        if numbers and self.check_two_numbers(numbers, 'corner'):
            low, high = sorted([int(x) for x in numbers.split('-')])
            if high - low == 4 and low % 3:
                self.scores[self.human.name] -= bet
                targets = [str(number) for number in (low, low + 1, high - 1, high)]
                self.bets.append(('corner bet on {}'.format(numbers), targets, bet))
            else:
                message = '{} and {} are not the low and high of a square of numbers.'
                self.human.tell(message.format(low, high))
        return True

    def do_double(self, arguments):
        """
        Make a bet on two consecutive rows of numbers. (bool)

        Parameters:
        arguments: The range to bet on and the bet. (str)
        """
        words = arguments.lower().split()
        if words[0] in ('street', 'line'):
            arguments = ' '.join(words[1:])
        numbers, bet = self.check_bet(arguments)
        if numbers and self.check_two_numbers(numbers, 'double street'):
            low, high = sorted([int(x) for x in numbers.split('-')])
            if high - low == 5 and not high % 3:
                self.scores[self.human.name] -= bet
                targets = [str(number) for number in range(low, high + 1)]
                self.bets.append(('double street bet on {}'.format(numbers), targets, bet))
        return True

    def do_dozen(self, arguments):
        """
        Bet on a consecutive dozen. (bool)

        Parameters:
        arguments: The column and the bet. (str)
        """
        column, bet = self.check_bet(arguments)
        if column:
            targets = []
            if column.lower() in ('1', 'p', 'f'):
                targets = [str(number) for number in range(1, 13)]
            elif column.lower in ('2', 'm', 's'):
                targets = [str(number) for number in range(12, 25)]
            elif column.lower in ('3', 'd', 't'):
                targets = [str(number) for number in range(24, 37)]
            if targets:
                self.scores[self.human.name] -= bet
                self.bets.append(('dozen bet on {}'.format(column), targets, bet))
            else:
                self.human.tell('That is not a valid dozen. Please use 1/2/3, P/M/D, or F/S/T.')
        return True

    def do_even(self, arguments):
        """
        Bet on the the even numbers. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('even {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            self.bets.append(('even bet', [str(number) for number in range(2, 37, 2)], bet))
        return True

    def do_high(self, arguments):
        """
        Bet on the the high half of the range. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('high {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            self.bets.append(('high bet', [str(number) for number in range(19, 37)], bet))
        return True

    def do_layout(self, arguments):
        """
        Show the current layout. (bool)

        Parameters:
        arguments: The ignored arguments to the command. (str)
        """
        if self.layout == 'american':
            text = '\n  0  |  00  \n'
        else:
            text = '\n      0     \n'
        for number in range(1, 37):
            if str(number) in self.red:
                text += ' {:2} '.format(number)
            else:
                text += '({:2})'.format(number)
            if not number % 3:
                text += '\n'
        self.human.tell(text + '\nred (black)')
        return True

    def do_low(self, arguments):
        """
        Bet on the the low half of the range. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('low {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            self.bets.append(('low bet', [str(number) for number in range(1, 19)], bet))
        return True

    def do_odd(self, arguments):
        """
        Bet on the the odd numbers. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('odd {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            self.bets.append(('odd bet', [str(number) for number in range(1, 37, 2)], bet))
        return True

    def do_prime(self, arguments):
        """
        Make a bet on all but two prime numbers. (bool)

        Parameters:
        arguments: The primes to exclude and the bet. (str)
        """
        numbers, bet = self.check_bet(arguments)
        if numbers and self.check_two_numbers(numbers, 'split'):
            low, high = sorted([int(x) for x in numbers.split('-')])
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
            if low in primes and high in primes and low != high:
                primes.remove(low)
                primes.remove(high)
                self.scores[self.human.name] -= bet
                self.bets.append(('prime bet excluding {}'.format(numbers), primes, bet))
            else:
                self.human.tell('{} and {} are not distinct prime numbers.'.format(low, high))
        return True

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

    def do_red(self, arguments):
        """
        Bet on red. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('red {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            self.bets.append(('red bet', self.red, bet))
        return True

    def do_snake(self, arguments):
        """
        Zig zag bet from 1 to 34. (bool)

        Parameters:
        arguments: The amount to bet. (str)
        """
        numbers, bet = self.check_bet('snake {}'.format(arguments))
        if numbers:
            self.scores[self.human.name] -= bet
            targets = ['1', '5', '9', '12', '14', '16', '19', '23', '27', '30', '32', '34']
            self.bets.append(('snake bet', targets, bet))
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

    def do_split(self, arguments):
        """
        Make a bet on a two adjacent numbers. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        numbers, bet = self.check_bet(arguments)
        if numbers and self.check_two_numbers(numbers, 'split'):
            low, high = sorted([int(x) for x in numbers.split('-')])
            valid = (low and high and abs(high - low) == 1 and min(low, high) % 3)
            valid = valid or (low and high and abs(high - low) == 3)
            valid = valid or (self.layout == 'american' and numbers in ('0-1', '0-2', '00-2', '00-3'))
            valid = valid or (self.layout == 'french' and numbers in ('0-1', '0-2', '0-3'))
            if valid:
                self.scores[self.human.name] -= bet
                self.bets.append(('split bet on {}'.format(numbers), numbers.split('-'), bet))
            else:
                self.human.tell('{} and {} are not adjacent on the layout.'.format(low, high))
        return True

    def do_straight(self, arguments):
        """
        Make a bet on a single number. (bool)

        Parameters:
        arguments: The numbers to bet on and the bet. (str)
        """
        number, bet = self.check_bet(arguments)
        if number:
            if number not in self.numbers:
                self.human.tell('That number is not in this layout.')
            else:
                self.scores[self.human.name] -= bet
                self.bets.append(('straight bet on {}'.format(number), [number], bet))
        return True

    def do_street(self, arguments):
        """
        Make a bet on a three number row. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        number, bet = self.check_bet(arguments)
        if number:
            numbers = number.split('-')
            end = int(numbers[-1])
            if end % 3:
                self.human.tell('A valid street must end in a multiple of three.')
            else:
                text = '{}-{}-{}'.format(end - 2, end - 1, end)
                self.scores[self.human.name] -= bet
                self.bets.append(('street bet on {}'.format(text), text.split('-'), bet))
        return True

    def do_top(self, arguments):
        """
        Make a five number bet incluidng the zeros. (bool)

        Parameters:
        arguments: The ammount to bet. (str)
        """
        words = arguments.split()
        if words[0].lower() != 'line':
            words = ['line'] + words
        numbers, bet = self.check_bet(' '.join(words))
        if numbers and self.layout == 'american':
            self.scores[self.human.name] -= bet
            self.bets.append(('top line bet', ('0', '00', '1', '2', '3'), bet))
        elif numbers:
            self.human.tell('That bet can only be made on an American layout.')
        return True

    def do_trio(self, arguments):
        """
        Make a bet on a zero and two numbers next to it. (bool)

        Parameters:
        arguments: The number to bet on and the bet. (str)
        """
        numbers, bet = self.check_bet(arguments)
        if numbers:
            if self.layout == 'american':
                valid = numbers in ('0-1-2', '0-00-2', '00-2-3')
            else:
                valid = numbers in ('0-1-2', '0-2-3')
            if valid:
                self.scores[self.human.name] -= bet
                self.bets.append(('trio bet on {}'.format(numbers), numbers.split('-'), bet))
            else:
                self.human.tell('That is not a valid trio on this layout.')
        return True

    def game_over(self):
        """Determine the end of game. (bool)"""
        if self.scores[self.human.name] == 0:
            self.win_loss_draw[1] = 1
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options. (None)"""
        self.layout = 'american'
        self.numbers = [str(number) for number in range(37)]
        self.stake = 100
        self.max_bet = 10
        if self.raw_options.lower() == 'none':
            pass
        elif self.raw_options:
            self.flags |= 1
            for word in self.raw_options.lower().split():
                if word == 'american':
                    self.layout = 'american'
                elif word == 'french':
                    self.layout = 'french'
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
        for text, target, bet in self.bets:
            if winner in target:
                self.human.tell('Your {} won!'.format(text))
                winnings = bet * (36 // len(target))
                self.human.tell('You won {} bucks!'.format(winnings))
                self.scores[self.human.name] += winnings
                total_winnings += winnings
            else:
                self.human.tell('Your {} lost.'.format(text, target))
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

