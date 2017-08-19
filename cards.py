"""
cards.py

Cards and decks of cards for tgames.

Classes:
Card: A standard playing card, with a suit and a rank. (object)
Deck: A standard deck of cards. (object)
TrackingCard: A card that tracks it's location. (Card)
"""

class Card(object):
    """
    A standared playing card, with a suit and a rank. (object)

    The color, rank, and suit attributes are length 1.

    Class Attributes:
    suits: The suit characters. (str)
    suit_names: The names of the suits. (list of str)
    ranks: The rank characters. (str)
    rank_names: The names of the ranks. (list of str)

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
    __repr__
    __str__
    """

    suits = 'CDHS'
    suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades']
    ranks = 'XA23456789TJQK'
    rank_names = ['Joker', 'Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']
    rank_names += ['Jack', 'Queen', 'King']

    def __init__(self, rank, suit):
        """
        Set up the card. (None)

        Parameters:
        rank: The rank of the card. (str)
        suit: The suit of the card. (str)
        """
        # Set the pecified paramters.
        self.rank = rank[0]
        self.suit = suit[0]
        # Calculated the color of the card.
        if self.suit in 'DH':
            self.color = 'R'
        else:
            self.color = 'B'
        # Calcuate the full name of the card.
        rank_name = self.rank_names[self.ranks.index(self.rank)]
        suit_name = self.suit_names[self.suits.index(self.suit)]
        self.name = '{} of {}'.format(rank_name, suit_name)
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
            return (self.rank, self.suit) == (other.rank, other.suit)
        # Compare strings by str
        elif isinstance(other, str):
            return str(self) == other.upper()
        else:
            return NotImplemented
        
    def __lt__(self, other):
        """For sorting by rank. (bool)"""
        if isinstance(other, Card):
            return self.ranks.index(rank) < other.rank.index(rank)
        else:
            return self.rank < other  # ?? do I want this? from class where rank is int.

    def __repr__(self):
        """Debugging text representation. (str)"""
        return 'Card({}, {})'.format(self.rank, self.suit)

    def __str__(self):
        """Human readable text representation. (str)"""
        if self.up:
            text = self.rank + self.suit
        else:
            text = '??'
    
    def above(self, other, n = 1, wrap_ranks = False):
        """
        Check that this card is n ranks above another card. (bool)
        
        Parameters:
        other: The card to compare with. (Card)
        wrap_ranks: A flag for K-A-2 wrapping. (bool)
        """
        diff = self.rank - other.rank
        if wrap_ranks and diff < 0:
            diff += self.deck.max_rank
        return diff == n
    
    def below(self, other, n = 1, wrap_ranks = False):
        """
        Check that this card is n ranks below another card. (bool)
        
        Parameters:
        other: The card to compare with. (Card)
        wrap_ranks: A flag for K-A-2 wrapping. (bool)
        """
        diff = other.rank - self.rank
        if wrap_ranks and diff < 0:
            diff += self.deck.max_rank
        return diff == n

class Deck(object):
    """
    A standard deck of cards. (object)

    Attributes:
    cards: The cards in the deck. (list of card)
    discards: The cards in the discard pile. (list of card)

    Methods:
    deal: Deal a card from the deck. (Card)
    discard: Discard a card to the discard pile. (None)
    shuffle: Shuffle the discards back into the deck. (None)
    """

    def __init__(self, jokers = 0):
        """
        Fill the deck with a standard set of cards. (None)

        Parameters:
        jokers: The number of jokers in the deck.
        """
        # Add the standard cards.
        self.cards = []
        for rank in Card.ranks:
            for suit in Card.suit:
                self.cards.append(Card(rank, suit))
        # Add any requested jokers.
        for suit_index in range(jokers):
            self.cards.append(Card('X', Card.suits[suit_index % len(Card.suits)]))
        # Start with an empty discard pile.
        self.discards = []

    def deal(self, up = False):
        """
        Deal a card from the deck. (Card)

        Parameters:
        up: A flag for dealing the card face up. (bool)
        """
        card = self.cards.pop()
        card.up = up
        return card

    def discard(self, card):
        """
        Discard a card to the discard pile. (None)

        Parameters:
        card: The card to discard. (Card)
        """
        self.discards.append(card)
        card.up = False

    def shuffle(self):
        """Shuffle the discards back into the deck. (None)"""
        self.cards.extend(self.discards)
        random.shuffle(self.cards)
        self.discards = []


class TrackingCard(Card):
    """
    A card that tracks it's location. (Card)

    Attributes:
    deck: The deck the card is a part of. (Deck)
    deck_location: The location of the card in the deck. (list of Card)
    game_location: The location of the card in the game. (list of Card)

    Methods:
    discard: Discard the card. (None)

    Overridden Methods:
    __init__
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
        if self.deck is not None:
            self.deck_location = self.deck.cards
            self.game_location = self.deck.cards
        else:
            self.deck_location = None
            self.game_location = None

    def above(self, other, n = 1):
        """
        Check that this card is n ranks above another card. (bool)
        
        Parameters:
        other: The card to compare with. (Card)
        """
        super(TrackingCard, self).above(other, n, self.deck.game.wrap_ranks)

    def below(self, other, n = 1):
        """
        Check that this card is n ranks below another card. (bool)
        
        Parameters:
        other: The card to compare with. (Card)
        """
        super(TrackingCard, self).below(other, n, self.deck.game.wrap_ranks)
        
    def discard(self):
        """
        Discard the card. (None)
        """
        self.deck.discard(self)


class TrackingDeck(Deck):
    """
    A deck that keeps track of the location of the cards in it.

    !! max_rank works differently, and may cause a problem in solitaire games.
    !! left implementing some solitaire methods until proven necessary.

    Attributes:
    card_map: A map for finding cards in the deck. (dict of str(card): card}
    game: The game the deck is a part of. (Solitaire)
    in_play: The cards currently in play. (list of Card)
    last_order: The order of the deck at the last shuffle. (list of int)
    max_rank: The highest rank in the deck. (int)
    ranks: The ranks available to cards in the deck. (list of int)
    suits: The suits available to cards in the deck. (list of str)
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
        self.suits = card_calss.suits
        # Fill the deck.
        self.cards = []
        self.card_map = {}
        card_number = 0
        for rank in self.ranks:
            for suit in self.suits:
                card = card_class(rank, suit, self)
                self.cards.append(card)
                self.card_map[str(card)] = card
        self.max_rank = self.ranks[-1]
        # set the default attributes
        self.in_play = []
        self.discards = []
        self.last_order = [card.number for card in self.cards]
