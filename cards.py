"""
cards.py

Cards and decks of cards for tgames.

Copyright (C) 2018-2020 by Craig O'Brien and the t_games contributors.
See the top level __init__.py file for details on the t_games license.

Constants:
STANDARD_RANKS: The standard Western card ranks. (FeatureSet)
STANDARD_SUITS: The standard Western card suits. (FeatureSet)
STANDARD_WRAP_RANKS: The standard card ranks with wrapping. (FeatureSet)

Classes:
CRand: Implementation of C's rand function. (object)
FeatureSet: A set of valid values for a feature (rank/suit) of a Card. (object)
Card: A standard playing card, with a suit and a rank. (object)
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
try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence
import random
import re

from . import utility


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


class FeatureSet(object):
    """
    A set of valid values for a feature (rank/suit) of a Card. (object)

    Attributes:
    an_chars: The characters for ranks using 'an' instead of 'a'. (str)
    chars: The characters for the feature values. (str)
    colors: The colors associated with the feature values. (str)
    names: The names of the feature values. (dict of str: str)
    skip: The number of values to skip when iterating. (int)
    values: Numeric values associated with feature values. (dict of str: int)
    wrap: A flag for ranks being wrappable. (bool)

    Methods:
    index: Give the feature index of a character. (int)
    item: Iterate over all the items in the feature set. (iterator)

    Overwritten Methods
    __init__
    __iter__
    __len__
    __repr__
    """

    def __init__(self, chars, names, values = None, colors = None, skip = 0, wrap = False, an_chars = ''):
        """
        Set up the feature set. (None)

        Parameters:
        chars: The characters for the feature values. (str)
        names: The names of the feature values. (list of str)
        values: Numeric values associated with feature values. (list of int)
        colors: The colors associated with the feature values. (str)
        skip: The number of values to skip when iterating. (int)
        wrap: A flag for ranks being wrappable. (bool)
        an_chars: The characters for ranks using 'an' instead of 'a'. (str)
        """
        # Set default values.
        if values is None:
            values = [0] * len(chars)
        if colors is None:
            colors = 'X' * len(chars)
        # Check length of secondary attributes.
        if len(names) != len(chars):
            raise ValueError('Names and characters of feature sets must have the same length.')
        if len(values) != len(chars):
            raise ValueError('Values and characters of feature sets must have the same length.')
        if len(colors) != len(chars):
            raise ValueError('Colors and characters of feature sets must have the same length.')
        # Set the attributes.
        self.chars = chars
        self.names = dict(zip(chars, names))
        self.values = dict(zip(chars, values))
        self.colors = dict(zip(chars, colors))
        self.skip = skip
        self.wrap = wrap
        self.an_chars = an_chars

    def __contains__(self, char):
        """
        Check for a valid rank. (bool)

        Parameters:
        char: The rank character to check validity of. (str)
        """
        return char in self.names

    def __iter__(self):
        """Iterate over the characters. (iterator)"""
        return iter(self.chars[self.skip:])

    def __len__(self):
        """The number of possible feature values. (int)"""
        return len(self.chars) - self.skip

    def __repr__(self):
        """Debugging text representation. (str)"""
        return '<FeatureSet {!r}>'.format(self.chars)

    def above(self, char, other_char, n = 1):
        """
        Check that this card is n ranks above another card. (bool)

        Parameters:
        char: The feature character of the first card. (str)
        other_char: The feature character of the second card. (str)
        """
        # Do the standard caculation
        diff = self.ranks.index(char) - self.ranks.index(other_char)
        # Account for wraping.
        if self.wrap and diff < 0:
            diff += len(self) - self.skip
        return diff == n

    def below(self, char, other_char, n = 1):
        """
        Check that this card is n ranks below another card. (bool)

        Parameters:
        char: The feature character of the first card. (str)
        other_char: The feature character of the second card. (str)
        """
        # Do the standard caculation
        diff = self.ranks.index(other_char) - self.ranks.index(char)
        # Account for wraping.
        if self.wrap and diff < 0:
            diff += len(self) - self.skip
        return diff == n

    def index(self, char):
        """Give the feature index of a character. (int)"""
        return self.chars.index(char)

    def items(self):
        """
        Iterate over all the items in the feature set. (iterator)

        Each interation is a tuple of (index, character, name, value)
        """
        # ?? Can I simplify this by removing the def and the return?
        def iter_items():
            for index, char in enumerate(self.chars):
                if index < self.skip:
                    continue
                yield (index, char, self.names[char], self.values[char], self.colors[char])
        return iter_items()

STANDARD_RANKS = FeatureSet('XA23456789TJQK',
    ['Joker', 'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack',
        'Queen', 'King'],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10],
    skip = 1, an_chars = 'A8')

STANDARD_SUITS = FeatureSet('CDHS', ['Clubs', 'Diamonds', 'Hearts', 'Spades'], colors = 'RRBB')

STANDARD_WRAP_RANKS = FeatureSet('XA23456789TJQK',
    ['Joker', 'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack',
        'Queen', 'King'],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10],
    skip = 1, wrap = True, an_chars = 'A8')


class Card(object):
    """
    A standared playing card, with a suit and a rank. (object)

    The color, rank, and suit attributes are length 1.

    Attributes:
    color: The color of the card. ('R' or 'B')
    format_types: Extra types used for the format method. (dict of str: str)
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

    def __init__(self, rank, suit, down_text = '??', ace_high = False, rank_set = STANDARD_RANKS,
        suit_set = STANDARD_SUITS):
        """
        Set up the card. (None)

        Parameters:
        rank: The rank of the card. (str)
        suit: The suit of the card. (str)
        down_text: How the card looks when face down. (str)
        ace_high: Treat the ace as higher than a king. (bool)
        rank_set: The ranks set the card is part of. (FeatureSet)
        suit_set: The suit set the card is part of. (FeatureSet)
        """
        # Set the specified paramters.
        self.rank = rank[0]
        self.suit = suit[0]
        self.rank_set = rank_set
        self.suit_set = suit_set
        # Calculate the numeric values of the card.
        self.rank_num = self.rank_set.index(self.rank)
        self.suit_num = self.suit_set.index(self.suit)
        self.value = self.rank_set.values[self.rank] + self.suit_set.values[self.suit]
        self.color = self.suit_set.colors[self.suit]
        # Calcuate the text attributes of the card.
        self.name = '{} of {}'.format(self.rank_set.names[self.rank], self.suit_set.names[self.suit])
        self.up_text = self.rank + self.suit
        self.down_text = down_text
        if self.rank in self.rank_set.an_chars:
            a_text = 'an {}'.format(self.name.lower())
        else:
            a_text = 'a {}'.format(self.name.lower())
        format_types = {'a': a_text, 'd': self.down_text, 'n': self.name, 'u': self.up_text}
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
            return (self.rank_num, self.suit_num) == (other.rank_num, other.suit_num)
        # Compare strings by str.
        elif isinstance(other, str):
            return self.up_text == other.upper()
        # The rest is not implementd.
        else:
            return NotImplemented

    def __hash__(self):
        """The hash is the card text. (hash)"""
        return hash(self.up_text)

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
            return (self.suit_num, self.rank_num) < (self.suit_num, other.rank_num)
        else:
            return (self.suit_num, self.rank_num) < other

    def __repr__(self):
        """Generate computer readable text representation. (str)"""
        return 'Card({!r}, {!r})'.format(self.rank, self.suit)

    def __str__(self):
        """Generate human readable text representation. (str)"""
        if self.up:
            return self.up_text
        else:
            return self.down_text

    def above(self, other, n = 1):
        """
        Check that this card is n ranks above another card. (bool)

        Parameters:
        other: The card to compare with. (Card)
        """
        return self.rank_set.above(self.rank, other.rank)

    def below(self, other, n = 1):
        """
        Check that this card is n ranks below another card. (bool)

        Parameters:
        other: The card to compare with. (Card)
        """
        return self.rank_set.below(self.rank, other.rank)


class Pile(MutableSequence):
    """
    A sequence of cards. (MutableSequence)

    Methods:
    _child: Make a Pile with the same attributes but different cards. (Pile)
    insert: Insert a card into the pile. (None)
    sort: Sort the cards in the pile. (None)

    Overridden Methods:
    __init__
    __add__
    __delitem__
    __getitem__
    __imul__
    __len__
    __mul__
    __repr__
    __rmul__
    __setitem__
    __str__
    """

    def __init__(self, cards = []):
        """
        Put the cards in the pile. (None)

        Parameters:
        cards: The cards to put in the pile. (list of Card)
        """
        self.cards = cards

    def __add__(self, other):
        """Add the pile to another sequence of cards. (Pile)"""
        if isinstance(Pile):
            return self._child(Pile.cards + other.cards)
        else:
            return self._child(Pile.cards + other)

    def __delitem__(self, key):
        """
        Delete a card. (None)

        Parameters:
        key: The item(s) to delete. (int or slice)
        """
        del self.cards[key]

    def __getitem__(self, key):
        """
        Get a card or slice of cards. (Card or Pile)

        Parameters:
        key: The item(s) to delete. (int or slice)
        """
        if isinstance(key, int):
            return self.cards[key]
        else:
            return self._child(self.cards[key])

    def __imul__(self, other):
        """
        Copy the cards in the pile in place. (Pile)

        Parameters:
        other: The number of copies to make. (int)
        """
        self.cards *= other

    def __len__(self):
        """Get the number of cards in the Pile. (int)"""
        return len(self.cards)

    def __mul__(self, other):
        """
        Copy the cards in the pile. (Pile)

        Parameters:
        other: The number of copies to make. (int)
        """
        return self._child(self.cards * other)

    def __repr__(self):
        """Debugging text representation."""
        return '<{} {}>'.format(self.__class__.__name__, self)

    def __rmul__(self, other):
        """
        Copy the cards in the pile. (Pile)

        Parameters:
        other: The number of copies to make. (int)
        """
        return self._child(self.cards * other)

    def __setitem__(self, key, value):
        """
        Set a card in the deck. (None)

        Parameters:
        key: The card(s) to change. (int or slice)
        value: The cards(s) to change to. (Card or list of Cards)
        """
        self.cards[key] = value

    def __str__(self):
        """Human readable text representation. (str)"""
        return '[{}]'.format(', '.join(card.up_text for card in self.cards))

    def _child(self, cards):
        """
        Make a Pile with the same attributes but different cards. (Pile)

        Paramters:
        cards: The cards to make a pile out of. (list of Card)
        """
        return Pile(cards)

    def insert(self, index, card):
        """
        Insert a card in the pile. (None)

        Parameters:
        index: Where to put the card. (int)
        card: The card to put there. (Card)
        """
        self.cards.insert(index, card)

    def sort(self, key = None, reverse = False):
        """
        Sort the cards in the pile. (None)

        Parameters:
        key: A function to get comparison keys for the cards. (callable)
        reverse: A flag for sorting in descending order. (bool)
        """
        self.cards.sort(key = key, reverse = reverse)


class Deck(Pile):
    """
    A standard deck of cards. (Pile)

    Attributes:
    card_re: A regular expression to match a card. (SRExpression)
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
    """

    def __init__(self, cards = None, jokers = 0, decks = 1, shuffle_size = 0, rank_set = STANDARD_RANKS,
        suit_set = STANDARD_SUITS):
        """
        Fill the deck with a standard set of cards. (None)

        Parameters:
        cards: The initial cards in the deck. (list of Card)
        jokers: The number of jokers in the deck. (int)
        decks: The number of idential decks shuffled together. (int)
        shuffle_size: The number of cards left that triggers a shuffle. (int)
        rank_set: The rank information for cards in the deck. (FeatureSet)
        suit_set: The suit information for cards in the deck. (FeatureSet)
        """
        # Set the specified attributes.
        self.shuffle_size = shuffle_size
        self.jokers = jokers
        self.rank_set = rank_set
        self.suit_set = suit_set
        # Extract attributes from the feature sets.
        self.ranks = self.rank_set.chars
        self.suits = self.suit_set.chars
        self.card_re = re.compile('[{}][{}]'.format(self.ranks, self.suits), re.IGNORECASE)
        # Add the standard cards.
        if cards is None:
            # !! refactor out to allow for customization.
            # Add the base cards.
            self.cards = []
            for deck in range(decks):
                for rank in self.rank_set:
                    for suit in self.suit_set:
                        self.cards.append(Card(rank, suit, rank_set, suit_set))
            # Get the joker ranks and suits.
            joker_ranks = self.rank_set.chars[:self.rank_set.skip]
            if self.suit_set.skip:
                joker_suits = self.suit_set.chars
            else:
                joker_suits = self.suit_set.chars[:self.suit_set.skip]
            # Add the jokers.
            for deck in range(decks):
                for rank in joker_ranks:
                    for suit_index in range(self.jokers):
                        suit = joker_suits[suit_index % len(card_class.suits)]
                        self.cards.append(Card(joker_rank, suit))
        else:
            self.cards = cards
        # Start with an empty discard pile.
        self.discards = []

    def _child(self, cards):
        """
        Make a Deck with the same attributes but different cards. (Deck)

        Paramters:
        cards: The cards to make a deck out of. (list of Card)
        """
        child = Deck(cards, jokers = self.jokers, decks = self.decks, shuffle_size = self.shuffle_size,
            card_class = self.card_class, ace_high = self.ace_high, rank_set = self.rank_set,
            suit_set = self.suit_set)
        child.discards = self.discards[:]
        return child

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


class Hand(Pile):
    """
    A hand of cards held by a player. (Pile)

    Attributes:
    deck: The deck the cards in the hand come from. (Deck)

    Methods:
    discard: Discard a card back to the deck. (None)
    draw: Draw a card from the deck. (None)
    score: Score the hand. (int)
    shift: Pass a card to another hand. (None)
    show_player: Show the hand to the player playing it. (str)

    Overridden Methods:
    __init__
    __eq__
    """

    def __init__(self, cards = None, deck = None):
        """
        Set up the link to the deck. (None)

        Parameters:
        deck: The deck the hand is dealt from. (Deck)
        """
        self.deck = deck
        if cards is None:
            self.cards = []
        else:
            self.cards = cards

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

    def __lt__(self, other):
        """
        Sort Hands by score. (bool)

        Parameters:
        other: The other hand to compare with. (Hand)
        """
        if isinstance(other, Pile):
            return self.score() < other.score()
        else:
            return self.cards < other

    def __repr__(self):
        """Debugging text representation."""
        return '<{} [{}]>'.format(self.__class__.__name__, self)

    def __str__(self):
        """Human readable text representation. (str)"""
        return '{}'.format(', '.join(card.up_text for card in self.cards))

    def _child(self, cards):
        """
        Make a Hand with the same attributes but different cards. (Hand)

        Paramters:
        cards: The cards to make a hand out of. (list of Card)
        """
        return Hand(cards, self.deck)

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
        return sum(card.value for card in self.cards)

    def shift(self, card, hand):
        """
        Pass a card to another hand. (None)

        card: The card to pass. (str)
        hand: The hand to pass it to. (Hand)
        """
        card_index = self.cards.index(card)
        hand.append(self.cards.pop(card_index))

    def show_player(self):
        """Show the hand to the player playing it. (str)"""
        return ', '.join([card.up_text for card in self.cards])


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
