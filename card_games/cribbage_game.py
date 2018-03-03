"""
cribbage_game.py

A game of Cribbage.

Constants:
Credits: The credits for Cribbage. (str)

Classes:
Cribbage: A game of Cribbage. (game.Game)
"""


import tgames.game as game
import tgames.cards as cards


CREDITS = """
Game Design: John Suckling
Game Programming: Craig "Ichabod" O'Brien
"""


class Cribbage(game.Game):
	"""
	A game of Cribbage. (game.Game)

	Attributes:
	deck: The deck of cards used in the game. (cards.Deck)
	hands: The player's hands in the game. (dict of str: cards.Hand)
	starter: The starter card. (cards.Card)
	"""

	aka = ['Crib']
	categories = ['Card Game', 'Matching Game']
	credits = CREDITS
	name = 'Cribbage'

	def deal(self):
		"""Deal the cards. (None)"""
		# Find the dealer and the player on their left.
		self.dealer_index = (self.dealer_index + 1) % len(self.players)
		dealer = dealer
		self.player_index = (self.dealer_index + 1) % len(self.players)
		print('The current dealer is {}.'.format(dealer.name))
		# Deal the cards
		hand_size = [0, 0, 6, 5, 5][len(self.players)]
		for card in range(hand_size):
			for player in self.players:
				self.hands[player.hand].draw()
		if len(self.players) == 3:
			self.hands['The Crib'].draw()
		self.starter = self.deck.deal(up = True)
		# Check for heels.
		if self.starter.rank == 'J':
			print ('The dealer got his heels.')
			self.scores[dealer.name] += 2
			if self.scores[dealer.name] >= self.target_score:
				self.force_win
				return False

	def player_action(self, player):
		"""
		Allow the player to do something.

		Parameters:
		player: The current player. (player.Player)
		"""
		if self.phase == 'discard':
			answer = player.ask('Which two cards would you like to discard? ')
			discards = cards.Card.care_re.findall(answer)

	def set_up(self):
		"""Set up the game. (None)"""
		# Set up the deck.
		self.deck = cards.Deck()
		self.deck.shuffle()
		# Set up the hands.
		self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
		self.hands['The Crib'] = cards.Hand(self.deck)
		self.deal()
		# set up the game
		self.phase = 'Discard'
		self.discard_size = [0, 0, 2, 1, 1][len(self.players)]
		self.dealer_index = -1
		self.target_score = 161
