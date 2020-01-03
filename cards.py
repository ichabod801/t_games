"""
cards.py

Cards and decks of cards for tgames.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
Card: A standard playing card, with a suit and a rank. (object)
CRand: Implementation of C's rand function. (object)
Deck: A standard deck of cards. (object)
Hand: A hand of cards held by a player. (object)
TrackingCard: A card that tracks it's location. (Card)
TrackOneSuit: A tracking card with only one suit. (TrackingCard)
TrackTwoSuit: A tracking card with only two suits. (TrackingCard)
TrackingDeck: A deck that keeps track of the location of its cards. (Deck)
MultiTrackingDeck: A deck that keeps track of multiple duplicate cards. (Deck)
"""


from __future__ import print_function

import collections
import random
import re

from . import utility


class Card(object):
    """
    A standared playing card, with a suit and a rank. (object)

    The color, rank, and suit attributes are length 1.

    Class Attributes:
    an_ranks: Ranks whose name uses 'an' rather than 'a'. (str)
    card_re: A regular expression to match a card.
    rank_names: The names of the ranks. (list of str)
    ranks: The rank characters. (str)
    suit_names: The names of the suits. (list of str)
    suits: The suit characters. (str)

    Attributes:
    color: The color of the card. ('R' or 'B')
    name: The full name of the card. (str)
    rank: The rank of the card. (str)
    suit: The suit of the card. (str)
    up: A flag for the card being face up. (str)

    Methods:
    above: Check that this card is n ranks above another card. (bool)
    below: Check that this card is n ranks below another card. (bool)

    Overridden Methods:
    __init__
    __eq__
    __format__
    __hash__
    __lt__
    __repr__
    __str__
    """

    an_ranks = 'A8'
    suits = 'CDHS'
    suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    ranks = 'XA23456789TJQK'
    rank_names = ['Joker', 'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']
    rank_names += ['Jack', 'Queen', 'King']
    card_re = re.compile('[{}][{}]'.format(ranks, suits), re.IGNORECASE)

    def __init__(self, rank, suit, down_text = '??', ace_high = False):
        """
        Set up the card. (None)

        Parameters:
        rank: The rank of the card. (str)
        suit: The suit of the card. (str)
        down_text: How the card looks when face down. (str)
        ace_high: Treat the ace as higher than a king. (bool)
        """
        # Set the specified paramters.
        self.rank = rank[0]
        self.suit = suit[0]
        # Calculate the rank number.
        self.rank_num = self.ranks.index(self.rank)
        if self.rank_num == 1 and ace_high:
            self.rank_num = len(self.ranks)
        # Calculated the color of the card.
        if self.suit in 'DH':
            self.color = 'R'
        else:
            self.color = 'B'
        # Calcuate the text attributes of the card.
        rank_name = self.rank_names[self.ranks.index(self.rank)]
        suit_name = self.suit_names[self.suits.index(self.suit)]
        self.name = '{} of {}'.format(rank_name, suit_name)
        self.up_text = self.rank + self.suit
        self.down_text = down_text
        if self.rank in self.an_ranks:
            a_text = 'an {}'.format(self.name.lower())
        else:
            a_text = 'a {}'.format(self.name.lower())
        self.format_types = {'a': a_text, 'd': self.down_text, 'n': self.name, 'u': self.up_text}
        # Default face down.
        self.up = False

    def __eq__(self, other):
        """
        Equality comparison, by rank and suit. (bool)

        Note that str(card) == card to match user input.

        Parameters:
        other: The card to compare to.
        """
        # Compare cards by rank and suit.
        if isinstance(other, Card):
            return (self.rank_num, self.suit) == (other.rank_num, other.suit)
        # Compare strings by str.
        elif isinstance(other, str):
            return self.rank + self.suit == other.upper()
        # The rest is not implementd.
        else:
            return NotImplemented

    def __hash__(self):
        """The hash is the card text. (hash)"""
        return hash(self.rank + self.suit)

    def __format__(self, format_spec):
        """
        Return a formatted text version of the card. (str)

        The additional recognized format types are:
            d: The face down two-letter abbreviation.
            n: The full name.
            u: The face up two-letter abbreviation.

        Parameters:
        format_spec: The format specification. (str)
        """
        # Use and remove format type if given.
        if format_spec and format_spec[-1] in self.format_types:
            target = self.format_types[format_spec[-1]]
            format_spec = format_spec[:-1]
        else:
            target = str(self)
        # Return the text based on type with the rest of the format spec applied.
        format_text = '{{:{}}}'.format(format_spec)
        return format_text.format(target)

    def __lt__(self, other):
        """For sorting by rank. (bool)"""
        if isinstance(other, Card):
            return self.rank_num < other.rank_num
        else:
            return self.rank_num < other

    def __repr__(self):
        """Generate computer readable text representation. (str)"""
        return 'Card({!r}, {!r})'.format(self.rank, self.suit)

    def __str__(self):
        """Generate human readable text representation. (str)"""
        if self.up:
            return self.up_text
        else:
            return self.down_text

    def above(self, other, n = 1, wrap_ranks = False):
        """
        Check that this card is n ranks above another card. (bool)

        Parameters:
        other: The card to compare with. (Card)
        wrap_ranks: A flag for K-A-2 wrapping. (bool)
        """
        # Do the standard caculation
        diff = self.rank_num - other.rank_num
        # Account for wrap ranks.
        if wrap_ranks and diff < 0:
            diff += len(self.ranks) - 1
        return diff == n

    def below(self, other, n = 1, wrap_ranks = False):
        """
        Check that this card is n ranks below another card. (bool)

        Parameters:
        other: The card to compare with. (Card)
        wrap_ranks: A flag for K-A-2 wrapping. (bool)
        """
        # Do the standard caculation
        diff = other.rank_num - self.rank_num
        # Account for wrap ranks.
        if wrap_ranks and diff < 0:
            diff += len(self.ranks) - 1
        return diff == n


class CRand(object):
    """
    Implementation of C's rand function. (object)

    Attributes:
    state: The current state of the PRNG. (int)

    Overridden Methods:
    __init__
    __call__
    __repr__
    """

    def __init__(self, seed = None):
        """
        Set up the pseudo-random number generator. (None)

        Parameters:
        seed: The initial state of the PRNG. (int)
        """
        # Use a random seed if none is given.
        if seed is None:
            seed = random.randint(0, 32767)
        self.state = seed

    def __call__(self):
        """Get the next number from the PRNG. (int)"""
        self.state = (214013 * self.state + 2531011) % (2 ** 31)
        return self.state // (2 ** 16)

    def __repr__(self):
        """Computer readable text representation. (str)"""
        return 'CRand({})'.format(self.state)


class Deck(object):
    """
    A standard deck of cards. (object)

    Attributes:
    card_re: A regular expression to match a card.
    cards: The cards in the deck. (list of card)
    discards: The cards in the discard pile. (list of card)
    ranks: The possible ranks for cards in the deck. (str)
    shuffle_size: The number of cards left that triggers a shuffle. (int)
    suits: The possible suits for cards in the deck. (str)

    Methods:
    cut: Cut the deck. (None)
    deal: Deal a card from the deck. (Card)
    discard: Discard a card to the discard pile. (None)
    force: Remove a particular card from the deck. (Card)
    pick: Pick a card from the deck. (Card)
    shuffle: Shuffle the discards back into the deck. (None)

    Overridden Methods:
    __init__
    __repr__
    """

    def __init__(self, jokers = 0, decks = 1, shuffle_size = 0, card_class = Card, ace_high = False):
        """
        Fill the deck with a standard set of cards. (None)

        Parameters:
        jokers: The number of jokers in the deck. (int)
        decks: The number of idential decks shuffled together. (int)
        shuffle_size: The number of cards left that triggers a shuffle. (int)
        card_class: The type of cards that go into the deck. (type)
        """
        # Set the specified attribute.
        self.shuffle_size = shuffle_size
        # Extract attributes from the card class.
        self.card_re = card_class.card_re
        self.ranks = card_class.ranks
        self.suits = card_class.suits
        # Add the standard cards.
        self.cards = []
        for deck in range(decks):
            for rank in card_class.ranks[1:]:
                for suit in card_class.suits:
                    self.cards.append(card_class(rank, suit, ace_high = ace_high))
        # Add any requested jokers.
        joker_rank = card_class.ranks[0]
        for deck in range(decks):
            for suit_index in range(jokers):
                suit = card_class.suits[suit_index % len(card_class.suits)]
                self.cards.append(card_class(joker_rank, suit))
        # Start with an empty discard pile.
        self.discards = []

    def __repr__(self):
        """Create a debugging text representation. (str)"""
        card_text = utility.plural(len(self.cards), 'card')
        return '<{} with {} {} remaining>'.format(self.__class__.__name__, len(self.cards), card_text)

    def cut(self, card_index):
        """
        Cut the deck. (None)

        Parameters:
        card_index: A number indicating where to cut the deck. (int)
        """
        card_index %= len(self.cards)
        self.cards = self.cards[card_index:] + self.cards[:card_index]

    def deal(self, up = False):
        """
        Deal a card from the deck. (Card)

        Parameters:
        up: A flag for dealing the card face up. (bool)
        """
        # Check for early reshuffle.
        if len(self.cards) <= self.shuffle_size:
            self.shuffle()
        # Deal the card.
        card = self.cards.pop()
        card.up = up
        return card

    def discard(self, card, up = False):
        """
        Discard a card to the discard pile. (None)

        Parameters:
        card: The card to discard. (Card)
        up: A flag for discarding face up. (bool)
        """
        self.discards.append(card)
        card.up = up

    def force(self, card_text, up = True):
        """
        Remove a particular card from the deck. (Card)

        Parameters:
        card_text: The string version of the card. (str)
        up = Flag for dealing the card face up. (bool)
        """
        card = self.cards[self.cards.index(card_text)]
        self.cards.remove(card)
        card.up = up
        return card

    def pick(self, card_index, up = True):
        """
        Pick a card from the deck. (Card)

        Parameters:
        card_index: A number to determine the card picked. (int)
        up: Flag for picking the card face up. (bool)
        """
        card = self.cards.pop(card_index % len(self.cards))
        card.up = up
        return card

    def shuffle(self, number = None):
        """
        Shuffle the discards back into the deck. (None)

        Parameters:
        number: The number of the shuffle, the seed for the PRNG. (int)
        """
        # Gather the discards.
        self.cards.extend(self.discards)
        if number is None:
            # Do a standard shuffle.
            random.shuffle(self.cards)
        else:
            # Do a C-style shuffle.
            rand = CRand(number)
            self.cards.sort(key = lambda card: (card.ranks.index(card.rank), card.suit))
            while self.cards:
                swap = rand() % len(self.cards)
                self.cards[swap], self.cards[-1] = self.cards[-1], self.cards[swap]
                self.discards.append(self.cards.pop())
            self.cards = self.discards[::-1]
        self.discards = []


class Hand(object):
    """
    A hand of cards held by a player. (object)

    Attributes:
    cards: The cards in the hand. (list of Card)
    deck: The deck the cards in the hand come from. (Deck)

    Methods:
    discard: Discard a card back to the deck. (None)
    draw: Draw a card from the deck. (None)
    score: Score the hand. (int)
    shift: Pass a card to another hand. (None)
    show_player: Show the hand to the player playing it. (str)

    Overridden Methods:
    __init__
    __bool__
    __contains__
    __iter__
    __len__
    __repr__
    __str__
    """

    def __init__(self, deck):
        """
        Set up the link to the deck. (None)

        Parameters:
        deck: The deck the hand is dealt from. (Deck)
        """
        self.deck = deck
        self.cards = []

    def __bool__(self):
        """Hands are True if they have cards in them. (None)"""
        return bool(self.cards)

    def __contains__(self, item):
        """
        Check for a card being in the hand. (None)

        Parameters:
        item: The card to check for existince. (object)
        """
        return item in self.cards

    def __eq__(self, other):
        """
        Check for equality with another hand. (bool)

        Two hands are equal if they have the same cards, regardless of order.

        Parameters:
        other: The hand to check against. (Hand)
        """
        # !! needs unit testing.
        if isinstance(other, Hand):
            return sorted(self.cards) == sorted(other.cards)
        else:
            return False

    def __iter__(self):
        """Iterate over the cards in hand. (iterator)"""
        return iter(self.cards)

    def __len__(self):
        """Return the number of cards in the hand. (int)"""
        return len(self.cards)

    def __repr__(self):
        """Debugging text representation. (str)"""
        # !! check unittesting
        text = '<Hand: {}>'.format(', '.join([card.up_text for card in self.cards]))
        if text.endswith(': >'):
            return '<Hand: (empty)>'
        else:
            return text

    def __str__(self):
        """Human readable text representation. (str)"""
        return ', '.join([str(card) for card in self.cards])

    def deal(self, card):
        """
        Add a card to the hand. (None)

        card: The card to add to the hand. (Card)
        """
        self.cards.append(card)

    def draw(self, up = True):
        """
        Draw a card from the deck. (None)

        Parameters:
        up: A flag for dealing the card face up. (None)
        """
        self.cards.append(self.deck.deal(up = up))

    def discard(self, card = None):
        """
        Discard a card back to the deck. (None)

        Parameters:
        card: The card to discard, or None to discard all cards. (Card or None)
        """
        # Discard all cards.
        if card is None:
            for card in self.cards:
                self.deck.discard(card)
            self.cards = []
        # Discard a specified card.
        else:
            card_index = self.cards.index(card)
            self.deck.discard(self.cards[card_index])
            del self.cards[card_index]

    def score(self):
        """Score the hand. (int)"""
        # Default score is high card.
        return max([Card.ranks.index(card.rank) for card in self.cards])

    def shift(self, card, hand):
        """
        Pass a card to another hand. (None)

        card: The card to pass. (str)
        hand: The hand to pass it to. (Hand)
        """
        card_index = self.cards.index(card)
        hand.cards.append(self.cards.pop(card_index))

    def show_player(self):
        """Show the hand to the player playing it. (str)"""
        return ', '.join([card.rank + card.suit for card in self.cards])


class TrackingCard(Card):
    """
    A card that tracks its location. (Card)

    Attributes:
    deck: The deck the card is a part of. (Deck)
    deck_location: The location of the card in the deck. (list of Card)
    game_location: The location of the card in the game. (list of Card)
    loc_txt: The location identifier for abbreviated card text. (str)
    location_text: The location identifier for full card text. (str)
    rank_num: The numeric rank of the card. (int)

    Methods:
    discard: Discard the card. (None)

    Overridden Methods:
    __init__
    __eq__
    above
    below
    """

    def __init__(self, rank, suit, deck):
        """
        Set up the card. (None)

        Initialization converts the suit to a single uppercase character.

        Parameters:
        rank: The rank of the card. (int)
        suit: The suit of the card. (str)
        deck: The deck the card comes from. (TrackingDeck)
        """
        super(TrackingCard, self).__init__(rank, suit)
        self.deck = deck
        self.rank_num = self.ranks.index(self.rank)
        if self.deck is not None:
            self.deck_location = self.deck.cards
            self.game_location = self.deck.cards
        else:
            self.deck_location = None
            self.game_location = None
        self.loc_txt = ''
        self.location_text = ''

    def __eq__(self, other):
        """
        Check equality with another card. (bool)

        Equality between tracking cards is by identity. Otherwise it's as a standard
        Card.

        Parameters:
        other: The card to compare with. (Card or str)
        """
        if isinstance(other, TrackingCard):
            return id(self) == id(other)
        else:
            return super(TrackingCard, self).__eq__(other)

    def __format__(self, format_spec):
        """
        Return a formatted text version of the card. (str)

        The additional recognized format types are:
            d: The face down two-letter abbreviation.
            n: The full name.
            u: The face up two-letter abbreviation.

        Parameters:
        format_spec: The format specification. (str)
        """
        # Use and remove format type if given.
        format_type = format_spec[-1] if format_spec else ''
        if format_type in self.format_types:
            target = self.format_types[format_type]
            format_spec = format_spec[:-1]
        else:
            target = str(self)
        # Add the location text based on the format type.
        if format_type == 'u':
            target += self.loc_txt
        elif format_type != 'd':
            target += self.location_text
        # Return the text based on type with the rest of the format spec applied.
        format_text = '{{:{}}}'.format(format_spec)
        return format_text.format(target)

    def __repr__(self):
        """Create a debugging text representation."""
        return '<TrackingCard {}{}>'.format(self.rank, self.suit)

    def above(self, other, card_index = 1):
        """
        Check that this card is n ranks above another card. (bool)

        Parameters:
        other: The card to compare with. (Card)
        card_index: How many ranks above you are checking for. (int)
        """
        return super(TrackingCard, self).above(other, card_index, self.deck.game.wrap_ranks)

    def below(self, other, card_index = 1):
        """
        Check that this card is n ranks below another card. (bool)

        Parameters:
        other: The card to compare with. (Card)
        card_index: How many ranks below you are checking for. (int)
        """
        return super(TrackingCard, self).below(other, card_index, self.deck.game.wrap_ranks)

    def discard(self):
        """Discard the card. (None)"""
        self.deck.discard(self)


class TrackOneSuit(TrackingCard):
    """A tracking card with only one suit. (TrackingCard)"""

    ranks = 'XA23456789TJQK'
    suits = 'S'
    suit_names = ['Spades']
    card_re = re.compile('[{}][{}]'.format(ranks, suits), re.IGNORECASE)


class TrackTwoSuit(TrackingCard):
    """A tracking card with only two suits. (TrackingCard)"""

    ranks = 'XA23456789TJQK'
    suits = 'HS'
    suit_names = ['Hearts', 'Spades']
    card_re = re.compile('[{}][{}]'.format(ranks, suits), re.IGNORECASE)


class TrackingDeck(Deck):
    """
    A deck that keeps track of the location of the cards in it. (Deck)

    Attributes:
    card_map: A map for finding cards in the deck. (dict of str: card}
    card_re: A regular expression to match a card.
    game: The game the deck is a part of. (Solitaire)
    in_play: The cards currently in play. (list of Card)
    last_order: The order of the deck at the last shuffle. (list of int)
    max_rank: The highest rank in the deck. (int)

    Methods:
    find: Find a card in the deck. (Card)
    gather: Gather cards back into the deck. (None)
    stack: Put the stack in a specified order. (None)

    Overridden Methods:
    __init__
    __repr__
    __str__
    deal
    discard
    force
    """

    def __init__(self, game, card_class = TrackingCard):
        """
        Set up the deck of cards. (None)

        Parameters:
        game: The game the card is a part of. (game.Game)
        card_class: The type of card in the deck. (TrackingCard)
        """
        # Set the general attributes.
        self.game = game
        self.ranks = card_class.ranks
        self.suits = card_class.suits
        self.card_re = card_class.card_re
        # Fill the deck.
        self.cards = []
        self.card_map = {}
        card_number = 0
        for rank in self.ranks[1:]:
            for suit in self.suits:
                card = card_class(rank, suit, self)
                self.cards.append(card)
                self.card_map[card.rank + card.suit] = card
        # Set the calcuated attribute.
        self.max_rank = self.ranks[-1]
        # Set the default attributes.
        self.in_play = []
        self.discards = []
        self.last_order = self.cards[:]

    def __repr__(self):
        """Generate a computer readable text representation. (str)"""
        # Get a card.
        if self.in_play:
            card = self.in_play[0]
        elif self.cards:
            card = self.cards[0]
        else:
            card = self.discards[0]
        # Get the class names.
        class_name = self.__class__.__name__
        card_class_name = card.__class__.__name__
        return '<{} of {}s for {!r}>'.format(class_name, card_class_name, self.game)

    def __str__(self):
        """Generate a human readable text representation. (str)"""
        # Get the relevant counts.
        cards = len(self.cards)
        in_play = len(self.in_play)
        discards = len(self.discards)
        # Get the relevant plurals.
        card_text = utility.plural(cards, 'card')
        play_text = utility.plural(in_play, 'card')
        discard_text = utility.plural(discards, 'card')
        # Generate the text.
        text = 'Deck of cards with {} {}, plus {} {} in play and {} {} discarded'
        return text.format(cards, card_text, in_play, play_text, discards, discard_text)

    def deal(self, game_location, up = True, card_index = -1):
        """
        Deal a card from the deck. (Card)

        Parameters:
        game_location: The new location of card in the game. (list of Card)
        up: Flag for dealing the card face up. (bool)
        card_index: The location of the card to deal. (int)
        """
        # move the card
        card = self.cards.pop(card_index)
        self.in_play.append(card)
        game_location.append(card)
        # change the cards attributes
        card.game_location = game_location
        card.deck_location = self.in_play
        card.up = up
        # return the card
        return card

    def discard(self, card):
        """
        Discard the game from play. (None)

        Parameters:
        card: The card to discard. (Card)
        """
        # move the card in the deck
        self.in_play.remove(card)
        self.discards.append(card)
        # remove the card from the game
        card.game_location.remove(card)
        # reset the card status
        card.game_location = self.game.deck.discards
        card.deck_location = self.discards

    def find(self, card_text):
        """
        Find a card in the deck. (Card)

        Paramters:
        card_text: The string version of the card. (str)
        """
        return self.card_map[card_text.upper()]

    def force(self, card_text, game_location, up = True):
        """
        Remove a particular card from the deck. (Card)

        Parameters:
        card_text: The string version of the card. (str)
        game_location: The new location of card in the game. (list of Card)
        up = Flag for dealing the card face up. (bool)
        """
        return self.deal(game_location, up = up, card_index = self.cards.index(card_text))

    def shuffle(self, number = None):
        """Shuffle the discards back into the deck. (None)"""
        # Shuffle the cards.
        super(TrackingDeck, self).shuffle(number = number)
        # Reset the card tracking.
        for card in self.cards:
            card.deck_location = self.cards
            card.game_location = self.cards


class MultiTrackingDeck(TrackingDeck):
    """
    A deck that keeps track of the location of multiple duplicate cards. (Deck)

    Attributes:
    decks: The number of decks shuffled together. (int)
    max_rank: The highest rank in the deck. (int)

    Methods:
    parse_location: Parse a location identifier into type and count. (str, int)

    Overridden Methods:
    __init__
    find
    """

    def __init__(self, game, decks = 2, card_class = TrackingCard):
        """
        Set up the deck of cards. (None)

        Parameters:
        game: The game the card is a part of. (game.Game)
        decks: The number of decks shuffled together. (int)
        card_class: The type of card in the deck. (TrackingCard)
        """
        # Set the specified attributes.
        self.game = game
        self.decks = decks
        # Extract attributes from the card class.
        self.ranks = card_class.ranks
        self.suits = card_class.suits
        reg_text = '[{}][{}](?:-[twrf]?\d*)?'
        self.card_re = re.compile(reg_text.format(self.ranks, self.suits), re.IGNORECASE)
        # Fill the deck.
        self.cards = []
        self.card_map = collections.defaultdict(list)
        card_number = 0
        for deck in range(decks):
            for rank in self.ranks[1:]:
                for suit in self.suits:
                    card = card_class(rank, suit, self)
                    self.cards.append(card)
                    self.card_map[card.rank + card.suit].append(card)
        self.max_rank = self.ranks[-1]
        # set the default attributes
        self.in_play = []
        self.discards = []
        self.last_order = self.cards[:]

    def find(self, card_text):
        """
        Find a card in the deck. (Card)

        Paramters:
        card_text: The string version of the card. (str)
        """
        # Check for a location specifier.
        if '-' in card_text:
            card_text, location = card_text.split('-')
        else:
            location, loc_txt, location_text = '', '', ''
        # Parse the location specifier.
        if location:
            location_type, location_count = self.parse_location(location)
        else:
            # Distinguish no location from an empty location.
            location = None
        if location:
            # Get the location from the game.
            if location_type == 'F':
                location = self.game.cells
                location_text = ' in the free cells'
            elif location_type == 'R':
                try:
                    location = self.game.reserve[location_count]
                    # Distinguish single reserve games from multi-reserve games.
                    if len(self.game.reserve) > 1:
                        text = ' in the {} reserve pile'
                        location_text = text.format(utility.number_word(location_count + 1, ordinal = True))
                    else:
                        location_text = ' in the reserve'
                except IndexError:
                    location = []
            elif location_type == 'T':
                try:
                    location = self.game.tableau[location_count]
                    text = ' in the {} tableau pile'
                    location_text = text.format(utility.number_word(location_count + 1, ordinal = True))
                except IndexError:
                    location = []
            else:
                location = self.game.waste
                location_text = ' in the waste'
            # Set the abbreviated location text.
            loc_txt = '-{}'.format(location_type)
            if location_type in 'RT':
                loc_txt = '{}{}'.format(loc_txt, location_count + 1)
        # Find the cards, filtered by any location specified.
        cards = self.card_map[card_text.upper()]
        if location is not None:
            cards = [card for card in cards if card in location]
        # Set (or unset) location text.
        for card in cards:
            card.loc_txt = loc_txt
            card.location_text = location_text
        return cards

    def parse_location(self, location_text):
        """
        Parse a location identifier into type and count. (str, int)

        Parameters:
        location_text: The location identifier. (str)
        """
        location_text = location_text.upper()
        if location_text.isdigit():
            # Number only locations default to the tableau.
            location_type = 'T'
            location_count = int(location_text) - 1
        elif location_text[-1].isdigit():
            location_type = location_text[0]
            location_count = int(location_text[1:]) - 1
        else:
            # Location count defaults to 0.
            location_type = location_text
            location_count = 0
        return location_type, location_count


if __name__ == '__main__':
    # Run the unit testing.
    from t_tests.cards_test import *
    unittest.main()
