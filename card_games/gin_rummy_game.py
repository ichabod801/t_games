"""
gin_rummy_game.py

A game of Gin Rummy.

To Do:
clean up output
card tracking bot.

Constants:
CREDITS: The credits for Gin Rummy. (str)
RULES: The rules for Gin Rummy. (str)

Classes:
GinBot: A bot that plays Gin Rummy. (player.Bot)
TrackingBot: A bot for Gin Rummy that tracks cards drawn. (GinBot)
GinRummy: A game of Gin Rummy. (game.Game)
"""


import random

from .. import cards
from .. import game
from .. import player
from .. import utility


CREDITS = """
Game Design: Elwood T. Baker and C. Graham Baker
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Gin Rummy is played in a series of hands. Each player is dealt ten cards, and
one card is dealt to the discard pile. The player who didn't deal gets the
first shot at the first discard. If they don't want it, the dealer can take it.
Whoever wants it starts play by drawing it into their hand. If neither player
wants it, the player who didn't deal starts play by taking the top card off of
the deck.

Each turn, you draw a card and discard a card. The idea is to build up runs in
the same suit (3S-4S-5S) or sets of the same rank (8D-8C-8H). These are called
'melds', and must have at least three cards in them.

On any turn you can 'knock' to end the hand. You discard as normal, but then
'spread' you hand by setting aside any melds you have. Then the other player
(the defender) spreads their melds. In addition, the defender can play cards
that match the knocker's melds. This is called 'laying off.'

Any cards that are not in melds are called 'deadwood.' If the knocker has no
deadwood (they melded all ten cards), they have Gin, and the defender may not
lay off. Each player's deadwood is scored by totally the ranks of the cards,
with face cards worth 10 points each. Whichever player has the lowest score
wins the hand, with ties going to the defender. The winner adds the difference
in the hand scores to their game score. If knocker got Gin or the defender beat
the knocker, they score an extra 25 points.

The dealer alternates each hand. If the deck ever gets to two cards and the
current player does not knock, the hand is a draw. It is not scored, and the
same player that dealt the hand deals a new one.

Play continues until someone has 100 game points or more. That player gets a
game bonus of 100 points. If that player won every hand in the game, they get
to double their score. Each player then adds 25 bonus points to their game
score for each hand they won. After all the bonus are added, whoever has the
highest score wins. Their final score is how much higher their game score is
than their opponent's.
"""


class GinBot(player.Bot):
    """
    A bot that plays Gin Rummy. (player.Bot)

    I took the algorithm for this bot from CS 340 assignment at UIC, apparently
    written by T. Roy (although there is no one by that name currently in the
    CS department at UIC).

    The link is: https://www.cs.uic.edu/~troy/fall01/cs340/mp2.html

    Attributes:
    hand: The bot's hand. (cards.Hand)
    listen: A flag for pulling attacking melds from the tell method. (bool)
    sorted: A flag that the bot has prepped it's hand for play. (bool)
    tracking: A dictionary for tracking cards in the game. (dict of str: list)

    Methods:
    discard_check: Determine if drawing a discard is a good idea. (str)
    find_melds: Find any melds of the specified type. (None)
    knock_check: Determine if it is time to knock or not. (str)
    match_check: Find any match between a card and tracked groups of cards. (list)
    next_spread: Get the next meld or layoff to spread. (str)
    run_pair: Check if two cards can be in the same run. (bool)
    set_pair: Check if two cards can be in the same set. (bool)
    sort_hand: Sort out the melds and potential melds in your hand. (None)

    Overridden Methods:
    ask
    set_up
    tell
    """

    def ask(self, prompt):
        """Answer a question from the game. (str)"""
        # Handle first pick.
        if prompt.startswith('Would you like the top card of the discard pile'):
            discard = self.game.deck.discards[-1]
            move = 'yes' if self.discard_check(discard) else 'no'
            if move == 'no':
                self.game.human.tell('{} rejected the first discard.'.format(self.name))
        # Handle discard vs. deck.
        elif prompt.startswith('Would you like to draw from the diScards'):
            discard = self.game.deck.discards[-1]
            move = 'discards' if self.discard_check(discard) else 'deck'
        # Handle knock vs. discard.
        elif prompt == 'What is your move? ':
            self.sort_hand()
            move = self.knock_check()
            if move.startswith('dis'):
                self.game.human.tell('{} discarded the {}.'.format(self.name, move[-2:]))
            self.untrack(move[-2:])
        # Handle spreading.
        elif prompt.startswith('Enter a set of cards'):
            move = self.next_spread()
        # Handle unforseen questions.
        else:
            move = super(GinBot, self).ask(prompt)
        return move

    def discard_check(self, card):
        """
        Determine if drawing a discard is a good idea. (str)

        Parameters:
        card: The discard to check. (cards.Card)
        """
        # Draw the discard if it creates or adds to a meld.
        if self.match_check(card):
            return True
        # Draw the discard if it creates a partial meld without running out of deadwood to discard.
        elif len(self.tracking['deadwood']) > 1 and self.match_check(card, ('deadwood',)):
            return True
        # Otherwise draw from the deck
        else:
            return False

    def find_melds(self, cards, check_function):
        """
        Find any melds of the specified type. (None)

        Parameters:
        cards: The cards to check for melds. (list of cards.Card)
        check_function: The function that check for the appropriate match. (callable)
        """
        # Handle nothing to look at.
        if not cards:
            return [], []
        # Loop through pairs of cards
        full, part, current = [], [], []
        previous = cards[0]
        for card in cards[1:]:
            if check_function(previous, card):
                # Track melds as they grow.
                if current:
                    current.append(card)
                else:
                    current = [previous, card]
            else:
                # If the current pair is not a meld, store any previous melds and reset.
                if len(current) >= 3:
                    full.append(current)
                elif current:
                    part.append(current)
                current = []
            previous = card
        # Catch the last match, if any.
        if len(current) >= 3:
            full.append(current)
        elif current:
            part.append(current)
        return full, part

    def knock_check(self):
        """Determine if it is time to knock or not. (str)"""
        # Determine discard.
        if self.tracking['deadwood']:
            possibles = self.tracking['deadwood']
        elif self.tracking['part-run'] or self.tracking['part-set']:
            possibles = sum(self.tracking['part-run'] + self.tracking['part-set'], [])
        else:
            melds = self.tracking['full-set'] + self.tracking['full-run']
            possibles = sum([meld for meld in melds if len(meld) > 3], [])
        possibles.sort(key = lambda card: card.rank_num)
        discard = possibles[-1]
        # Determine score.
        dead = sum(self.tracking['part-run'] + self.tracking['part-set'], []) + self.tracking['deadwood']
        score = sum(self.game.card_values[card.rank] for card in dead)
        # Check if possible.
        command = 'discard'
        if score <= self.game.knock_min:
            command = 'knock'
        # Return the chosen command with the discard.
        print(self.hand)
        print(self.tracking)
        return '{} {}'.format(command, discard)

    def match_check(self, card, groups = ('full-run', 'full-set', 'part-run', 'part-set')):
        """
        Find any match between a card and tracked groups of cards. (list)

        If no match is found, the return value is an empty list.

        Parameters:
        card: The card to match. (cards.Card)
        groups: The tracked groups to check against. (tuple of str)
        """
        # Loop through the groups.
        for group_type in groups:
            for group in self.tracking[group_type]:
                if group_type == 'deadwood':
                    group = [group]
                # Check for a run match.
                if group[0].suit == group[-1].suit:
                    if (card.below(group[0]) or card.above(group[0])) and card.suit == group[0].suit:
                        return group
                # Check for a set match.
                if group[0].rank == group[-1].rank == card.rank:
                    return group
        return []

    def next_spread(self):
        """Get the next meld or layoff to spread. (str)"""
        # Check for melds to return
        if self.tracking['full-set']:
            meld = self.tracking['full-set'].pop()
            return ' '.join(str(card) for card in meld)
        if self.tracking['full-run']:
            meld = self.tracking['full-run'].pop()
            return ' '.join(str(card) for card in meld)
        # Check for layoffs to return
        dead = sum(self.tracking['part-run'] + self.tracking['part-set'], []) + self.tracking['deadwood']
        for card in dead:
            if self.match_check(card, groups = ('attacks',)):
                self.untrack(card)
                return str(card)
        # If nothing, return nothing.
        return ''

    def run_pair(self, card1, card2):
        """
        Check if two cards can be in the same run. (bool)

        Parameters:
        card1: The lower card to check. (cards.Card)
        card1: The higher card to check. (cards.Card)
        """
        return card1.suit == card2.suit and card1.below(card2)

    def set_pair(self, card1, card2):
        """
        Check if two cards can be in the same set. (bool)

        Parameters:
        card1: The first card to check. (cards.Card)
        card1: The second card to check. (cards.Card)
        """
        return card1.rank == card2.rank

    def set_up(self):
        """Set up the bot. (None)"""
        self.hand = self.game.hands[self.name]
        self.sorted = False
        self.listen = False
        self.gin = False

    def sort_hand(self):
        """
        Sort out the melds and potential melds in your hand. (None)

        Note that if a card is in a run and a set, this tracks the run as a meld and
        the set as a potential meld.
        """
        # !! seems to have problems tracking deadwood that lead to not knocking when able
        # !! having trouble replicating. Perhaps in partial sets matching full runs?
        cards = self.hand.cards[:]
        # Check for runs.
        cards.sort(key = lambda card: (card.suit, card.rank_num))
        full_runs, part_runs = self.find_melds(cards, self.run_pair)
        # Remove cards in full runs.
        used = set(sum(full_runs, []))
        cards = [card for card in cards if card not in used]
        # Check for sets.
        cards.sort(key = lambda card: card.rank_num)
        full_sets, part_sets = self.find_melds(cards, self.set_pair)
        # Find partial sets matching full runs.
        breaks = []
        for part_set in part_sets:
            for run in full_runs:
                if part_set[0].rank in [card.rank for card in run]:
                    # Compare the score of the broken run to the broken group.
                    rank_score = self.game.card_values[part_set[0].rank]
                    broken_run = [card for card in run if card.rank != part_set[0].rank]
                    remainder, waste = self.find_melds(broken_run, self.run_pair)
                    remainder_score = sum([self.game.card_values[card.rank] for card in sum(remainder, [])])
                    run_score = sum([self.game.card_values[card.rank] for card in run])
                    # If the broken run leaves less points in hand, mark it for breaking.
                    if run_score - remainder_score - rank_score < 2 * rank_score:
                        full_set = part_set + [card for card in run if card.rank == part_set[0].rank]
                        breaks.append((full_set, part_set, run, remainder))
        # Remove and replace any broken runs.
        for full_set, part_set, full_run, remainder in breaks:
            full_sets.append(full_set)
            part_sets.remove(part_set)
            full_runs.remove(full_run)
            full_runs.extend(remainder)
        # Find the partial runs with the remaining cards.
        used = set(sum(full_sets + full_runs + part_sets, []))
        cards = [card for card in self.hand if card not in used]
        cards.sort(key = lambda card: (card.suit, card.rank_num))
        empty, part_runs = self.find_melds(cards, self.run_pair)
        # Calculate deadwood, and store the full and partial melds.
        used.update(*part_runs)
        self.tracking = {'attacks': [], 'full-run': full_runs, 'full-set': full_sets, 'part-run': part_runs,
            'part-set': part_sets, 'deadwood': [card for card in cards if card not in used]}

    def tell(self, *args, **kwargs):
        """
        Recieve informatio from the game. (None)

        The parameters are the same as for the print function.
        """
        # Note when attacking melds are about to be told.
        if args[0] == '\nThe attacking melds:':
            self.listen = True
            self.tracking['attacks'] = []
        # Note when all attacking melds have been told.
        elif 'deadwood' in args[0]:
            self.listen = False
        # Clean up previous attacking melds if your opponent got Gin.
        elif args[0].startswith('Gin!'):
            self.tracking['attacks'] = []
            self.listen = False
        # Store attacking meld information.
        elif self.listen:
            self.tracking['attacks'].append([cards.Card(*word.upper()) for word in args[0].split()])
        elif args[0].endswith('deals.'):
            self.sort_hand()

    def untrack(self, card_text):
        """
        Remove a card from the hand tracking. (None)

        Parameters:
        card_text: The name of the card to be removed. (str)
        """
        for group in ('full-run', 'full-set', 'part-run', 'part-set'):
            self.tracking[group] = [cards for cards in self.tracking[group] if card_text not in cards]
        if card_text in self.tracking['deadwood']:
            self.tracking['deadwood'].remove(card_text)


class TrackingBot(GinBot):
    """
    A bot for Gin Rummy that tracks cards drawn. (GinBot)
    """
    pass


class GinRummy(game.Game):
    """
    A game of Gin Rummy. (game.Game)

    Attributes:
    card_drawn: A flag for a card having been drawn this turn. (bool)
    deal_cards: A flag for needing to deal cards on the next turn. (bool)
    deck: The deck of cards used in the game. (cards.Deck)
    end: The number of points that signals the end of a game. (int)
    hands: The players' hands of cards. (dict of str: cards.Hand)
    wins: The number of hands each player has won. (dict of str: int)

    Class Attributes:
    card_values: The points per card by rank. (dict of str: int)

    Methods:
    deal: Deal the cards. (None)
    do_discard: Discard a card and end your turn. (bool)
    do_knock: Lay out your cards and attempt to win the hand. (bool)
    do_left: Move cards to the left of another card. (bool)
    do_right: Move cards to the right of another card. (bool)
    do_scores: Show the current scores. (bool)
    move_cards: Arrange cards within a player's hand. (None)
    parse_meld: Determine the cards for a given meld specification. (list of str)
    show_melds: Show the opponent's melds to a player. (None)
    spread: Spread cards from a player's hand. (tuple of list of cards.Card)

    Overridden Methods:
    game_over
    handle_options
    player_action
    set_options
    set_up
    """

    aka = ['Gin', 'Knock Poker', 'Poker Gin', 'Gin Poker']
    aliases = {'d': 'discard', 'l': 'left', 'k': 'knock', 'p': 'pass', 'r': 'right', 's': 'score'}
    card_values = dict(zip('A23456789TJQK', (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10)))
    categories = ['Card Games']
    credits = CREDITS
    name = 'Gin Rummy'
    num_options = 0
    rules = RULES

    def deal(self):
        """Deal the cards. (None)"""
        # Gather and shuffle all the cards.
        for hand in self.hands.values():
            hand.discard()
        self.deck.shuffle()
        # Deal 10 cards to each player.
        for card in range(10):
            for hand in self.hands.values():
                hand.draw()
        for player in self.players:
            player.tell('\n{} deals.'.format(self.dealer.name))
        # Discard one card.
        self.deck.discard(self.deck.deal(), up = True)
        # Handle dibs on the first discard.
        # Non-dealer gets first chance at the discard.
        non_dealer = self.players[0] if self.players[1] == self.dealer else self.players[1]
        self.player_index = self.players.index(non_dealer)
        while True:
            non_dealer.tell('Your hand is {}.'.format(self.hands[non_dealer.name]))
            query = 'Would you like the top card of the discard pile ({})? '.format(self.deck.discards[-1])
            take_discard = non_dealer.ask(query).lower()
            if take_discard in utility.YES or take_discard == self.deck.discards[-1]:
                self.hands[non_dealer.name].deal(self.deck.discards.pop())
                self.player_index = self.players.index(self.dealer)
            elif take_discard.split()[0] in ('g', 'group'):
                self.handle_cmd(take_discard)
                continue
            break
        if self.deck.discards:
            # The dealer then gets a chance at the discard.
            self.player_index = self.players.index(self.dealer)
            while True:
                self.dealer.tell('Your hand is {}.'.format(self.hands[self.dealer.name]))
                take_discard = self.dealer.ask(query).lower()
                if take_discard in utility.YES or take_discard == self.deck.discards[-1]:
                    self.hands[self.dealer.name].deal(self.deck.discards.pop())
                    self.player_index = self.players.index(non_dealer)
                elif take_discard.split()[0] in ('g', 'group'):
                    self.handle_cmd(take_discard)
                    continue
                break
            if self.deck.discards:
                # If no one wants it, non-dealer starts with the top card off the deck.
                self.hands[non_dealer.name].draw()
                self.player_index = self.players.index(self.dealer)
        self.card_drawn = True
        self.deal_cards = False

    def do_discard(self, argument):
        """
        Discard a card from your hand and end your turn. (d)
        """
        # Get the player info.
        player = self.players[self.player_index]
        hand = self.hands[player.name]
        # Validate the card.
        if argument in hand:
            # Discard valid cards.
            hand.discard(argument)
            self.deck.discards[-1].up = True
            return False
        else:
            # Give a warning if the card is not valid.
            player.error('You do not have that card to discard.')
            return True

    def do_knock(self, argument):
        """
        Set out your cards in an attempt to win the hand. (k)
        """
        # Get the players.
        attacker = self.players[self.player_index]
        defender = self.players[1 - self.player_index]
        # Get the attacker's discard.
        discard = self.get_knock_discard(attacker, argument)
        self.hands[attacker.name].discard(discard)
        self.deck.discards[-1].up = True
        # Spread the dealer's hand.
        attack_melds, attack_deadwood = self.spread(attacker)
        attack_score = sum([self.card_values[card.rank] for card in attack_deadwood])
        if attack_score > self.knock_min:
            if attack_melds:
                attacker.error('You do not have a low enough score to knock.')
            return False
        self.show_melds(attack_melds, attack_deadwood, defender, 'attacking')
        # Get the defender's melds.
        if attack_score:
            defense_melds, defense_deadwood = self.spread(defender, attack_melds)
        else:
            defender.tell('Gin! You may not lay off.')
            defense_melds, defense_deadwood = self.spread(defender)
        defense_score = sum([self.card_values[card.rank] for card in defense_deadwood])
        self.show_melds(defense_melds, defense_deadwood, attacker, 'defending')
        # Score the hands.
        score_diff = defense_score - attack_score
        if not attack_score:
            winner, score = attacker, 25 + score_diff
        elif score_diff > 0:
            winner, score = attacker, score_diff
        else:
            winner, score = defender, 25 - score_diff
        # Update the game score.
        self.human.tell('{} scored {} points.'.format(winner.name, score))
        self.scores[winner.name] += score
        self.wins[winner.name] += 1
        self.do_scores('', self.human)
        # Redeal.
        if self.scores[winner.name] < self.end:
            self.dealer, self.deal_cards = winner, True
        return False

    def do_left(self, arguments):
        """
        Move cards to the left of another card in your hand. (l)

        The argument to the left command is one card followed by a slash, followed by a
        space delimited list of one or more cards. The cards after the slash are moved
        to the left of the card before the slash.

        Alternatively, you can list one more cards with no slash. In that case, all of
        the cards listed will be moved to the far left of the hand.
        """
        self.move_cards(0, arguments)
        return True

    def do_right(self, arguments):
        """
        Move cards to the right of another card in your hand. (r)

        The argument to the right command is one card followed by a slash, followed by
        a space delimited list of one or more cards. The cards after the slash are
        moved to the right of the card before the slash.

        Alternatively, you can list one more cards with no slash. In that case, all of
        the cards listed will be moved to the far right of the hand.
        """
        self.move_cards(1, arguments)
        return True

    def do_scores(self, arguments, reciever = None):
        """
        Show the current game scores. (s)
        """
        if reciever is None:
            reciever = self.players[self.player_index]
        reciever.tell('\nCurrent Scores:')
        for player in self.players:
            reciever.tell('{}: {}'.format(player.name, self.scores[player.name]))

    def game_over(self):
        """Check for end of game and calculate the final score. (bool)"""
        if max(self.scores.values()) >= self.end:
            self.human.tell('\nThe game is over.')
            # Give the ender the game bonus.
            ender = self.players[self.player_index]
            self.human.tell('{} scores 100 points for ending the game.'.format(ender.name))
            self.scores[ender.name] += 100
            # Check for a sweep bonus.
            opponent = self.players[1 - self.player_index]
            if not self.wins[opponent.name]:
                self.human.tell('{} doubles their score for sweeping the game.'.format(ender.name))
                self.scores[ender.name] *= 2
            # Give each payer 25 points for each win.
            for player in self.players:
                if self.wins[player.name]:
                    win_points = 25 * self.wins[player.name]
                    text = '{} gets {} extra points for winning {} hands.'
                    self.human.tell(text.format(player.name, win_points, self.wins[player.name]))
            # Determine the winner.
            if self.scores[ender.name] > self.scores[opponent.name]:
                winner = ender
                loser = opponent
            else:
                winner = opponent
                loser = ender
            # Reset the scores.
            for player in self.players:
                self.scores[player.name] -= self.scores[loser.name]
            # Announce the winner.
            self.human.tell('\n{} won the game by {} points.'.format(winner.name, self.scores[winner.name]))
            return True
        else:
            return False

    def get_knock_discard(self, knocker, argument):
        """
        Get the discard from the knocker. (str)

        Parameters:
        knocker: The player who knocked. (player.Player)
        argument: The argument to the discard command. (str)
        """
        # Check for it passed as an argument.
        if argument in self.hands[knocker.name]:
            discard = argument
        else:
            # Warn about invalid arguments.
            if argument:
                knocker.tell('Invalid argument to the knock command: {!r}.'.format(argument))
            # Query the user for the card.
            while True:
                discard = knocker.ask('Which card would you like to discard? ')
                if discard in self.hands[knocker.name]:
                    break
                knocker.tell('You do not have that card to discard.')
                knocker.tell('Your hand is {}.'.format(self.hands[knocker.name]))
        return discard

    def handle_options(self):
        """Handle the option settings for this game. (None)"""
        #self.players = [self.human, player.Cyborg(taken_names = [self.human.name])]
        self.players = [self.human, GinBot(taken_names = [self.human.name])]

    def move_cards(self, mod, arguments):
        """
        Arrange cards within a player's hand. (None)

        Parameters:
        mod: The modifier to the target's index. (int)
        arguments: The arguments to the left or right command. (str)
        """
        # Get the player information
        player = self.players[self.player_index]
        hand = self.hands[player.name]
        # Parse the arguments.
        if '/' in arguments:
            target, slash, arguments = arguments.partition('/')
            target = target.strip()
        else:
            target = ''
        card_text = arguments.split()
        # Make sure the target is in the hand.
        if target and target not in hand:
            player.error('You do not have the target card in your hand.')
            return
        # Make sure the cards to move are in the hand.
        try:
            cards = [hand.cards[hand.cards.index(card_name)] for card_name in card_text]
        except ValueError:
            player.error('You do not have all of those cards in your hand.')
            return
        # Make sure the target is not in the moving cards.
        if target and target in cards:
            player.error('You cannot move the target.')
        else:
            # Remove the cards to be moved.
            single_cards = []
            for card in cards:
                if card in hand:
                    hand.cards.remove(card)
                    single_cards.append(card)
            # Get the location to move the cards to.
            if target:
                index = hand.cards.index(target) + mod
            elif mod:
                index = len(hand.cards)
            else:
                index = 0
            # Move the cards.
            hand.cards[index:index] = single_cards

    def parse_meld(self, meld, cards):
        """
        Determine the cards for a given meld specification. (list of str)

        Parameters:
        meld: The split input from the user. (list of str)
        cards: The cards in hand at the moment. (list of card.Card)
        """
        meld = meld.lower().replace(' -', '-').replace('- ', '-').split()
        # Check for shorthand.
        if len(meld) == 1:
            # Check for run shorthand.
            if '-' in meld[0]:
                # Get the ranks endpoints and the suit.
                try:
                    start, end = [word.strip().upper() for word in meld[0].split('-')]
                    start_rank, end_rank = start[0], end[0]
                    if len(start) > 1:
                        suit = start[1]
                    else:
                        suit = end[1]
                except ValueError, IndexError:
                    meld = ['error']
                else:
                    # Loop through the ranks, creating the card strings.
                    ranks = self.deck.ranks
                    meld = []
                    try:
                        for rank in ranks[ranks.index(start_rank):(ranks.index(end_rank) + 1)]:
                            meld.append(rank + suit)
                    except ValueError:
                        meld = ['error']
            # Check for set shorthand.
            elif len(meld[0]) == 1:
                rank = meld[0].upper()
                if rank in self.deck.ranks:
                    meld = [str(card) for card in cards if card.rank == meld[0].upper()]
                else:
                    meld = ['error']
        # Return other melds unprocessed.
        return meld

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        # Deal the cards if necessary.
        if self.deal_cards:
            self.deal()
            return False
        # Show the game status.
        player.tell('\nDiscard Pile: {}'.format(', '.join([str(card) for card in self.deck.discards])))
        player.tell('Your Hand: {}'.format(self.hands[player.name]))
        # Handle the player action.
        if self.card_drawn:
            # Get a move
            move = player.ask('What is your move? ').lower()
            go = self.handle_cmd(move)
            if not go:
                self.card_drawn = False  # should be true after a knock
        elif len(self.deck.cards) == 2:
            self.human.tell('The hand is a draw.')
            self.draws += 1
            self.deal()
            go = False
        else:
            # Draw a card.
            foe = self.players[0] if player == self.players[1] else self.players[1]
            while True:
                move = player.ask('Would you like to draw from the diScards or the top of the decK? ')
                move = move.lower()
                if move in ('discard', 'discards', self.deck.discards[-1], 's'):
                    draw_text = '{} drew the {} from the discard pile.'
                    foe.tell(draw_text.format(player.name, self.deck.discards[-1]))
                    self.hands[player.name].deal(self.deck.discards.pop())
                    break
                elif move in ('deck', 'top', 'k'):
                    foe.tell('{} drew from the deck.'.format(player.name))
                    self.hands[player.name].draw()
                    break
                else:
                    player.tell('I do not undertand. Please enter "discards" or "deck".')
            self.card_drawn = True
            go = True
        return go

    def set_up(self):
        """Set up the game. (None)"""
        # Set up the cards.
        self.deck = cards.Deck()
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        self.dealer = random.choice(self.players)
        # Set up the tracking variables.
        self.wins = {player.name: 0 for player in self.players}
        self.end = 100
        self.knock_min = 10
        self.draws = 0
        self.deal_cards = True

    def show_melds(self, melds, deadwood, show_to, role):
        """
        Show the opponent's melds to a player. (None)

        Parameters:
        melds: The melds to show. (list of list of card.Card)
        deadwood: The deadwood associated with the melds. (list of card.Card)
        show_to: The player to show the melds to. (player.Player)
        role: The role of the player who spread the melds. (str)
        """
        show_to.tell('\nThe {} melds:'.format(role))
        for meld in melds:
            show_to.tell(', '.join(str(card) for card in meld))
        if deadwood:
            dead_text = ', '.join(str(card) for card in deadwood)
            show_to.tell("The {} deadwood is {}.".format(role, dead_text))

    def spread(self, player, attack = []):
        """
        Spread cards from a player's hand. (tuple of list of cards.Card)

        The return value is the a list of the melds and a list of the deadwood. If the
        attacking player cancels the spread, then the melds are returned empty. This
        signals do_knock to cancel the knock.

        Parameters:
        player: The player who is spreading cards. (player.Player)
        attack: The melds that were spread by the attacking player. (list of list)
        """
        # Get the available cards.
        cards = self.hands[player.name].cards[:]
        # Get the melds and layoffs.
        scoring_sets = []
        while True:
            valid = False
            card_text = ', '.join(str(card) for card in cards)
            player.tell('\nThe following cards are still in your hand: {}'.format(card_text))
            meld_text = player.ask('Enter a set of cards to score (return to finish, cancel to abort): ')
            meld = self.parse_meld(meld_text, cards)
            # Check for no more scoring cards.
            if not meld:
                break
            elif meld == ['cancel']:
                if player == self.players[self.player_index]:
                    return [], self.hands[player.name].cards[:]
                else:
                    player.tell('\nThe defending player may not cancel.')
            elif meld == ['reset']:
                cards = self.hands[player.name].cards[:]
                scoring_sets = []
            elif meld == ['error']:
                player.error('\nInvalid meld specification: {!r}.'.format(meld_text))
            else:
                # Validate cards
                if not all(card in cards for card in meld):
                    player.error('You do not have all of those cards.')
                # Validate melds.
                if len(meld) >= 3:
                    valid = self.validate_meld(meld)
                # Validate layoffs.
                else:
                    for target in attack:
                        valid = self.validate_meld([str(card) for card in target] + meld)
                        if valid:
                            break
                # Handle the cards.
                if valid:
                    # Shift cards out of the temporary hand.
                    scoring_sets.append([])
                    for card in meld:
                        scoring_sets[-1].append(cards.pop(cards.index(card)))
                    if not cards:
                        break
                else:
                    # Warn if the meld or layoff is invalid.
                    layoff = ' or layoff' if attack else ''
                    player.error('That is not a valid meld{}.'.format(layoff))
        # Return the melds and the deadwood.
        return scoring_sets, cards

    def validate_meld(self, meld):
        """
        Validate a meld entered by a user. (bool)

        Parameter:
        meld: The set of cards to validate. (list of str)
        """
        valid = False
        # Sort the cards.
        try:
            meld.sort(key = lambda card: self.deck.ranks.index(card[0].upper()))
        except IndexError:
            return False
        # Check for a set.
        if len(set(card[0].upper() for card in meld)) == 1:
            valid = True
        # Check for a run.
        elif len(set(card[1].upper() for card in meld)) == 1:
            if ''.join(card[0].upper() for card in meld) in self.deck.ranks:
                valid = True
        return valid
