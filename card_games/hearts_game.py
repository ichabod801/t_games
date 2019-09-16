"""
hearts_game.py

A game of Hearts.

Classes:
HeartBot: A simple bot for Hearts. (player.Bot)
Hearts: A game of Hearts. (game.Game)
"""


import itertools
import re

from .. import cards
from .. import game
from .. import player
from .. import utility


class HeartBot(player.Bot):
    """
    A simple bot for Hearts. (player.Bot)

    Attribute:
    hand: The player's cards in the game. (cards.Hand)

    Methods:
    pass_cards: Determine which cards to pass. (list of cards.Card)
    play: Play a card to start or add to a trick. (card.Card)

    Overridden Methods:
    ask
    set_up
    tell
    """

    def ask(self, prompt):
        """
        Get a response from the bot. (str)

        Parameters:
        prompt: The question to ask the bot. (str)
        """
        # Handle passing.
        if prompt.startswith('\nWhich three'):
            return ' '.join(str(card) for card in self.pass_cards())
        # Handle passing cards.
        elif prompt.startswith('What is'):
            card = str(self.play())
            return card
        # Handle everything else.
        else:
            return super(HeartBot, self).ask(prompt)

    def pass_cards(self):
        """Determine which cards to pass. (list of card.Card)"""
        # Get rid of high spades.
        to_pass = [card for card in self.hand if card in ('KS', 'AS')]
        # Get rid of high hearts
        hearts = [card for card in self.hand if card.suit == 'H']
        hearts.sort(key = lambda card: card.rank_num, reverse = True)
        to_pass.extend(hearts)
        # If that's not enough, get rid of other high cards.
        if len(to_pass) < 3:
            other = [card for card in self.hand if card not in to_pass]
            other.sort(key = lambda card: card.rank_num, reverse = True)
            to_pass.extend(other)
        return to_pass[:3]

    def play(self):
        """Play a card to start or add to a trick. (card.Card)"""
        # Handle continuing a trick.
        if self.game.trick:
            # Get the cards matching the suit led.
            trick_starter = self.game.trick.cards[0]
            playable = [card for card in self.hand if card.suit == trick_starter.suit]
            if playable:
                # Get the playable cards that lose.
                playable.sort(key = lambda card: card.rank_num)
                losers = [card for card in playable if card.rank_num < trick_starter.rank_num]
                # Play the highest possible loser, or the lowest possible card in hopes of losing.
                # !! needs to avoid playing QS
                if losers:
                    card = losers[-1]
                else:
                    card = playable[0]
            else:
                # Get rid of the queen if you can.
                if 'QS' in self.hand:
                    card = 'QS'
                # Otherwise get rid of hearts if you can.
                hearts = [card for card in self.hand if card.suit == 'H']
                hearts.sort(key = lambda card: card.rank_num)
                if hearts:
                    card = hearts[-1]
                else:
                    # If you have no penalty cards, get rid of the highest card you can.
                    card = sorted(self.hand.cards, key = lambda card: card.rank_num)[-1]
            self.game.human.tell('{} plays the {}.'.format(self.name, card))
        else:
            # Open with the lowest card you have in the hopes of losing.
            self.hand.cards.sort(key = lambda card: card.rank_num)
            card = self.hand.cards[0]
            self.game.human.tell('{} opens with the {}.'.format(self.name, card))
        return card

    def set_up(self):
        """Set up the bot. (None)"""
        # Create a shortcut to your hand for easier programming.
        self.hand = self.game.hands[self.name]

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        # Mute.
        pass


class Hearts(game.Game):
    """
    A game of Hearts. (game.Game)

    Attributes:
    dealer: The next player to deal cards. (player.Player)
    deck: The deck of cards used in the game. (cards.Deck)
    hands: The players' hands of cards. (dict of str: cards.Hand)
    passes: The cards passed by each player. (dict of str: cards.Hand)
    phase: Whether the players are passing cards or playing tricks. (str)
    taken: The cards from the tricks each player has taken. (dict)
    trick: The cards in the current trick. (cards.Hand)
    tricks: The number of trick played so far. (int)

    Class Attributes:
    card_re: A regular expression detecting cards. (re.SRE_Pattern)

    Methods:
    deal: Deal the cards to the players. (None)
    do_play: Play a card, to either start or contribute to a trick. (bool)
    score_round: Score one deck's worth of tricks. (None)
    set_dealer: Determine the first dealer for the game. (None)
    trick_winner: Determine who won the trick. (None)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_up
    """

    aliases = {'p': 'play'}
    card_re = re.compile(r'\s*[x123456789tjqka][cdhs]\s*', re.IGNORECASE)
    categories = ['Card Games']
    name = 'Hearts'
    pass_aliases = {'l': 'left', 'r': 'right', 'rl': 'right-left', 'lr': 'left-right', 'rl': 'rot-left',
        'c': 'central', 'd': 'dealer', 'n': 'not', 's': 'scatter'}
    pass_dirs = {'left': ('left',), 'right': ('right',), 'left-right': ('left', 'right'),
        'right-left': ('right', 'left'), 'rot-left': (), 'central': ('center',), 'dealer': (),
        'not': ('not',), 'lran': ('left', 'right', 'across', 'not'), 'scatter': ('scatter',)}

    def deal(self):
        """Deal the cards to the players. (None)"""
        # Deal the cards out equally, leaving any extras aside.
        self.deck.shuffle()
        player_index = self.players.index(self.dealer)
        while True:
            player_index = (player_index + 1) % len(self.players)
            self.hands[self.players[player_index].name].draw()
            if self.players[player_index] == self.dealer and len(self.deck.cards) < len(self.players):
                break
        self.human.tell('{} deals.'.format(self.players[player_index]))
        # Eldest hand starts, and is the next dealer.
        self.dealer = self.players[(player_index + 1) % len(self.players)]
        #print('dealer set to {}.'.format(self.dealer))

    def dealers_choice(self):
        """Generator for dealer's choice of passing. (str)"""
        # Set the valid choices.
        valid = ('left', 'right', 'not', 'center', 'scatter', 'across')
        if len(self.players) not in (4, 6):
            valid = valid[:-1]
        valid_text = 'Please choose {}.'.format(utility.oxford(valid, 'or'))
        # Generate the direction and the pass count.
        while True:
            # Get the dealer for this deal (self.dealer is dealer for next deal at this point)
            dealer = self.players[self.players.index(self.dealer) - 1]
            # Get a valid direction.
            while True:
                pass_dir = dealer.ask('What direction shoud cards be passed? ')
                pass_dir = self.pass_aliases.get(pass_dir, pass_dir)
                if pass_dir in valid_dirs:
                    break
                dealer.error('{!r} is not a valid choice.'.format(pass_dir))
                dealer.error(valid_text)
            # Get or calculate the pass count.
            if pass_dir == 'scatter':
                self.num_pass = len(self.players) - 1
            elif pass_dir == 'not':
                self.num_pass = 0
            else:
                self.num_pass = dealer.ask_int('How many cards should be passed? ', low = 1, high = 4)
            # Yield the direction.
            yield pass_dir

    def do_play(self, arguments):
        """
        Play a card, to either start or contribute to a trick.  (p)
        """
        # Get the player and their hand.
        player = self.players[self.player_index]
        hand = self.hands[player.name]
        #print(player.name, hand)
        # Check for a valid card.
        if self.card_re.match(arguments):
            card_text = arguments.upper()
        else:
            player.error('{!r} is not a card in the deck.'.format(arguments))
            return True
        # Check for valid timing.
        if self.phase != 'trick':
            player.error('This is not the right time to play cards.')
            return True
        # Check for possession of the card.
        elif card_text not in hand:
            player.error('You do not have the {} to play.'.format(card_text))
            return True
        if self.trick:
            # Check that the card follows suit, or that the player is void in that suit.
            card = hand.cards[hand.cards.index(card_text)]
            trick_suit = self.trick.cards[0].suit
            if card.suit != trick_suit and list(filter(lambda card: card.suit == trick_suit, hand)):
                player.error('You must play a card of the suit led.')
                return True
            hand.shift(card, self.trick)
        else:
            hand.shift(card_text, self.trick)

    def game_over(self):
        """Determine if the game is over. (bool)"""
        # Check for someone breaking the "winning" score.
        if max(self.scores.values()) > self.win:
            # Get the scores of interest.
            human_score = self.scores[self.human.name]
            winning_score = min(self.scores.values())
            # Calculate the humans win/loss/draw.
            for name, score in self.scores.items():
                if score > human_score:
                    self.win_loss_draw[0] += 1
                elif score < human_score:
                    self.win_loss_draw[1] += 1
                elif name != human_score:
                    self.win_loss_draw[2] += 1
                # Tell the human who won.
                if score == winning_score:
                    self.human.tell('{} wins with {} points.'.format(name, score))
            # Set the number turns to the number of tricks.
            self.turns = self.tricks
            return True
        else:
            return False

    def handle_options(self):
        """Handle the option settings for this game. (None)"""
        super(Hearts, self).handle_options()
        # Handle the player options.
        self.players = [self.human]
        for bot in range(3):
            self.players.append(HeartBot(taken_names = [player.name for player in self.players]))
        # Handle the passing options
        if not self.num_pass:
            self.num_pass = 3 if len(self.players) < 5 else 2
        self.pass_dir = self.pass_aliases.get(self.pass_dir, self.pass_dir)
        self.not_warning = (self.pass_dir != 'not')
        if self.pass_dir == 'scatter':
            self.num_pass = len(self.players) - 1
        if self.pass_dir == 'rot-left':
            dirs = ['left-{}'.format(player_index) for player_index in range(1, len(self.players) + 1)]
            self.pass_dir = tuple(['left'] + dirs[1:-1] + ['not'])
        if self.pass_dir == 'dealer':
            self.pass_dir = self.dealers_choice()
        else:
            self.pass_dir = itertools.cycle(self.pass_dirs[self.pass_dir])
        # Handle the scoring options
        self.max_score = 26
        # Handle the end of game options.
        self.win = 100

    def pass_cards(self):
        """Handle the actual passing of the cards between players. (None)"""
        # self.this_pass is set earlier, so dealer's choice can get the number of cards to pass.
        # Check for not passing.
        if self.this_pass == 'not':
            if self.not_warning:
                self.human.tell('There is no passing this round.')
            return None
        # Get the pass-to list.
        if self.this_pass == 'left':
            pass_to = self.players[1:] + self.players[:1]
        elif self.this_pass == 'right':
            pass_to = self.players[-1:] + self.players[:-1]
        elif self.this_pass == 'across':
            offset = len(self.players) // 2
            pass_to = self.players[offset:] + self.players[:offset]
        elif self.this_pass.startswith('left-'):
            offset = int(this_pass.split('-')[1])
            pass_to = self.players[offset:] + self.players[:offset]
        # Pass the cards.
        # Handle passing to the center.
        if self.this_pass == 'center':
            center = []
            for player in self.players:
                center.extend(self.passes[player.name].cards)
                self.passes[pass_from.name].cards = []
            random.shuffle(center)
            for player in itertools.cycle(self.players):
                self.hands[player.name].append(center.pop())
                if not center:
                    break
        # Handle scatter passing.
        elif self.this_pass == 'scatter':
            for pass_from in self.players:
                for pass_to in self.players:
                    if pass_from != pass_to:
                        self.hands[pass_to.name].cards.append(self.passes[pass_from.name].pop)
        # Handle passing from player to player.
        else:
            for pass_from, pass_to in zip(self.players, pass_to):
                #print('passing from {} to {}'.format(pass_from, pass_to))
                self.hands[pass_to.name].cards.extend(self.passes[pass_from.name].cards)
                self.passes[pass_from.name].cards = []

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Handle passing.
        if self.phase == 'pass':
            # Get the cards to pass.
            player.tell('\nYour hand is: {}.'.format(self.hands[player.name]))
            move = player.ask('\nWhich three cards do you wish to pass? ')
            cards = self.card_re.findall(move)
            # If the correct number of cards are found, pass them.
            if len(cards) == 3:
                #print('{} passes.'.format(player))
                # Get the actual card objects.
                cards = [card.strip().upper() for card in cards]
                hand = self.hands[player.name]
                # Make sure all of the cards are in their hand.
                if all(card in hand for card in cards):
                    # Shift the cards to their passing stack.
                    for card in cards:
                        hand.shift(card, self.passes[player.name])
                    # If everyone has set up a passing stack, actually pass the cards.
                    if all(self.passes.values()):
                        self.pass_cards()
                        self.phase = 'trick'
                        self.player_index = self.players.index(self.dealer) - 1
                else:
                    # Warn if cards not in hand.
                    player.error('You do not have all of those cards.')
            else:
                # If incorrect number of cards, try to run a command.
                return self.handle_cmd(move)
        # Handle playing tricks
        elif self.phase == 'trick':
            # Display the game status.
            if self.trick:
                player.tell('The trick to you is: {}.'.format(self.trick))
            else:
                self.human.tell('')  # Make sure tricks are blocked out in the ouput.
                player.tell('You lead the trick.')
            player.tell('Your hand is: {}.'.format(self.hands[player.name]))
            move = player.ask('What is your play? ')
            if self.card_re.match(move):
                # Handle card text as plays.
                go = self.do_play(move)
                # Check for the trick being finished.
                if len(self.trick) == len(self.players):
                    self.tricks += 1
                    self.trick_winner()
                return go
            else:
                # Handle other text as commands.
                return self.handle_cmd(move)

    def set_options(self):
        """Set the possible options for the game. (None)"""
        # pass options
        # !! I don't have scatter
        self.option_set.add_option('num-pass', ['np'], int, 0, valid = range(5),
            question = 'How many cards should be passed (return for 3, 2 with 5+ players)? ')
        self.option_set.add_option('pass-dir', ['pd'], default = 'right',
            valid = ('r', 'right', 'l', 'left', 'rl', 'right-left', 'lr', 'left-right', 'lran', 'rot-left',
            'rl', 'central', 'c', 'dealer', 'd', 'not', 'n'),
            question = 'In what direction should cards be passed (return for right)? ')

    def score_round(self):
        """Score one deck's worth of tricks. (None)"""
        self.human.tell('')
        # Calculate the points this round for each player.
        round_points = {}
        shooter = ''
        for player in self.players:
            # Count the scoring cards.
            hearts, lady = 0, 0
            for card in self.taken[player.name]:
                if card.suit == 'H':
                    hearts += 1
                elif card == 'QS':
                    lady += 1
            # Calculate and store the unadjusted points.
            player_points = hearts + 13 * lady
            round_points[player.name] = player_points
            # Display the card counts and points.
            score_text = '{} had {} {}'.format(player.name, hearts, utility.plural(hearts, 'heart'))
            lady_text = ' and the Queen of Spades' if lady else ''
            score_text = '{}{}, for {} points this round.'.format(score_text, lady_text, player_points) # !! plural points
            self.human.tell(score_text)
            # Inform and record any sucessful shooter.
            if player_points == self.max_score:
                self.human.tell('{} shot the moon!'.format(player.name))
                shooter = player.name
        # Adjust the round points if anyone shot the moon.
        if shooter:
            for player in round_points:
                if player == shooter:
                    round_points[player] = 0
                else:
                    round_points[player] = self.max_score
        # Adjust and display the overall points.
        self.human.tell('\nOverall Scores:')
        for player in self.players:
            self.scores[player.name] += round_points[player.name]
            self.human.tell('{}: {}'.format(player, self.scores[player.name]))

    def set_dealer(self):
        """Determine the first dealer for the game. (None)"""
        # Deal a card to each player, keeping track of the max rank and who was dealt it.
        self.deck.shuffle()
        max_rank = -1
        players = self.players[:]
        max_players = []
        player_index = 0
        self.human.tell('')
        while True:
            # Deal the card.
            card = self.deck.deal(up = True)
            self.deck.discards.append(card)
            self.human.tell('{} was dealt the {}.'.format(players[player_index], card))
            # Track the max rank.
            if card.rank_num == max_rank:
                max_players.append(players[player_index])
            elif card.rank_num > max_rank:
                max_rank = card.rank_num
                max_players = [players[player_index]]
            player_index += 1
            # Check for unique winner.
            if player_index == len(players):
                if len(max_players) == 1:
                    self.dealer = max_players[0]
                    break
                else:
                    # Redeal to any tied players.
                    self.human.tell("\nThere was a tie with two {}'s.".format(self.deck.ranks[max_rank]))
                    max_rank = -1
                    players = max_players
                    max_players = []
                    player_index = 0

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the deck.
        self.deck = cards.Deck(ace_high = True)
        # Set up hands, including pseudo-hands for holding various sets of cards.
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        self.passes = {player.name: cards.Hand(self.deck) for player in self.players}
        self.taken = {player.name: cards.Hand(self.deck) for player in self.players}
        self.trick = cards.Hand(self.deck)
        # Handle the initial deal
        self.set_dealer()
        self.deal()
        # Set up the tracking variables.
        self.phase = 'pass'
        self.this_pass = next(self.pass_dir)
        self.tricks = 0

    def trick_winner(self):
        """Determine who won the trick. (None)"""
        # Find the winning card.
        trick_suit = self.trick.cards[0].suit
        suit_cards = [card for card in self.trick if card.suit == trick_suit]
        winning_card = sorted(suit_cards, key = lambda card: card.rank_num)[-1]
        card_index = self.trick.cards.index(winning_card)
        # Find the winning player.
        winner_index = (self.player_index + 1 + card_index) % len(self.players)
        winner = self.players[winner_index]
        # Handle the win.
        self.human.tell('\n{} won the trick with the {}.'.format(winner, winning_card))
        self.taken[winner.name].cards.extend(self.trick.cards)
        self.trick.cards = []
        # Check for the end of the round.
        if not self.hands[self.human.name]:
            self.score_round()
            if max(self.scores.values()) < self.win:
                for hand in self.taken.values():
                    hand.discard()
                self.deal()
                self.phase = 'pass'
                self.this_pass = next(self.pass_dir)
        else:
            self.player_index = winner_index - 1
