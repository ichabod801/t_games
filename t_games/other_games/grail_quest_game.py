"""
grail_quest_game.py

An Oregon Trail style game based on Monty Python and the Holy Grail.

Constants:
CREDITS: The credits for the game. (str)
FINAL_CREDITS: You know, the staff need time to clean the place. (str)
INITIAL_PURCHASES: The text shown before making the initial purchases. (str)
LLAMA_CREDITS: Ay yai yai yipee! (str)
MOOSE_CREDITS: Moose bits can be very serious. (str)
MOOSER_CREDITS: My sister was bitten by a moose once. (str)
RULES: The rules of the game. (str)
SACKED_CREDITS: It's hard to find good people these days. (str)
SACKER_CREDITS: But it's really easy to sack people. (str)
SACKEST_CREDITS: It's also pretty easy to make up new words. (str)

Classes:
GrailQuest: A game of Quest for the Grail. (game.Game)
"""


import datetime
import random

import t_games.game as game
import t_games.utility as utility


CREDITS = """
Original Program and Design: Don Rawitsch, Bill Heinemann, and
    Paul Dillenberger with the Minnesota Educational Computing Consortium.
Python Programming: Craig "Ichabod" O'Brien
Arthurian Content: Monty Python
"""

FINAL_CREDITS = """
You're one of those guys who stays in the theatre until the final credits
are completely done, aren't you?
"""

INITIAL_PURCHASES = """
You have 700 pieces of gold to spend on the following items:

    * Trusty steeds: You can spend 180 to 270 gold on your steeds. The more
      you spend, the faster you'll go, because you have better animals.
    * Coconuts: You can spend 20 to 30 gold on coconuts. Higher quality
      coconuts allow your steeds to travel faster, more dramatically, and in
      the correct idiom.
    * Spam: The more you have, the less chance there is of getting sick.
    * Arrows: 1 gold buys a sheaf of 50 arrows. You will need arrows for
      attacks by animals and bandits, and for hunting food.
    * Clothing: This is especially important for the cold weather you will
      face in the frozen land of Nador.
    * Miscellaneous Supplies: This includes medicine and other things you
      will need for sickness and emergency repairs.
"""

LLAMA_CREDITS = """
Original Program and Design: Don Llamaitsch, Bill Heinellama, and
    Paul Llamaberger with 40 specially trained Ecaudorian mountain llamas.
Python Programming: Craig "Llamabod" O'Llama and 6 Venzeaulan blue llamas.
Arthurian Content: Llama Python and the Red Llama of Brixton.
"""

MOOSE_CREDITS = """
Original Program and Design: Don Rawik, Bill Heinemik, and Paul Dillenbik
    wik the Moose Educational Computing Consortium.
Python Programming: Craig "Moosabod" O'Brien
Arthurian Content: Moosey Python

No moose were harmed in the making of this game. A few of the programmers might
have gotten bit a little, though.
"""

MOOSER_CREDITS = """
Original Moose Coreography: Don Rawitsch, Bill Heinemann, and
    Paul Dillenberger with the Minnesota Educational Computing Consortium.
Moose Training: Craig "Ichabod" O'Brien
Moose Handlers: Monty Python
"""

RULES = """
This program simulates a quest over England from Camelot to the Castle
Aaaaarrrrrrggghhh. You team of five knights will complete the quest in five to
six months -- if you make it alive.

At the beginning you will need to provision for the trip. You can spend all of
your money at the start of the quest, or you can save some of your gold to
spend at castles along the way when you run low on supplies. However, items
cost more at the castles. You can also go hunting along the way to get more
food.

Whenever you have to use your trusty bow and arrow along the way you will see
the words 'type twang'. The faster you type 'twang' and hit the return key, the
better luck you'll have with your bow and arrow.

Signed,
Richard M. Nixon
"""

SACKED_CREDITS = """
We apologize for the problems with the credits. The people responsible have
been sacked.

And don't forget to try a loveli holiday in Sweden.
"""

SACKER_CREDITS = """
We apologize again for the problems with the credits. The people responsible
for sacking the people who have just been sacked, have just been sacked.
"""

SACKEST_CREDITS = """
The programmers of the firm hired to continue the credits after the other
people had be sacked, wish it to be known that they have just been sacked.

The credits have been completed in an entirely different style at great
expense and at the last minute.
"""


class GrailQuest(game.Game):
    """
    A game of Quest for the Grail. (game.Game)

    Note: the film starts in 932 AD

    Class Attributes:
    credits_order: The various credits texts in the order to show them. (list of str)

    Attributes:
    arrows: The number of arrows left. (int)
    clothes: The quality of the clothing. (int)
    coconuts: The quality of the coconuts. (int)
    credits_index: The index of the next credits text to show. (int)
    gold: How much money the player has left. (int)
    mileage: The total miles travelled. (int)
    miscellaneous: The quality of the miscellaneous goods. (int)
    spam: The amount of spam left. (int)
    steeds: The quality of the steeds. (int)

    Overridden Methods:
    do_credits
    set_up
    """

    aka = ['I seek the Holy Grail!', 'qftg']
    categories = ['Adventure Games']
    credits = CREDITS
    credits_order = [CREDITS, MOOSE_CREDITS, SACKED_CREDITS, SACKER_CREDITS, MOOSER_CREDITS,
        SACKEST_CREDITS, LLAMA_CREDITS, FINAL_CREDITS]
    name = 'Quest for the Grail'

    def do_credits(self):
        """
        Show the credits for the game.
        """
        try:
            print(self.credits_order[self.credits_index].rstrip())
            self.credits_index += 1
            return True
        except IndexError:
            print("Sorry, sir. The movie's over. You'll have to leave.")
            self.force_end = 'loss'
            return False

    def initial_purchases(self):
        """Make the initial purchases. (None)"""
        print(INITIAL_PURCHASES)
        # Purchase steeds.
        query = 'How much would you like to spend on steeds? '
        self.steeds = self.human.ask_int(query, min = 180, max = 270, cmd = False)
        self.gold -= self.steeds
        # Purchase coconuts.
        query = 'How much would you like to spend on coconuts? '
        self.coconuts = self.human.ask_int(query, min = 20, max = 30, cmd = False)
        self.gold -= self.coconuts
        # Purchase spam.
        query = 'How much would you like to spend on spam? '
        self.spam = self.human.ask_int(query, min = 0, max = self.gold, cmd = False)
        self.gold -= self.spam
        # Purchase arrows.
        query = 'How much would you like to spend on arrows? '
        self.arrows = self.human.ask_int(query, min = 0, max = self.gold, cmd = False)
        self.gold -= self.arrows
        self.arrows *= 50
        # Purchase clothing.
        query = 'How much would you like to spend on clothing? '
        self.clothing = self.human.ask_int(query, min = 0, max = self.gold, cmd = False)
        self.gold -= self.clothing
        # Purchase miscellaneous supplies.
        query = 'How much would you like to spend on miscellaneous supplies? '
        self.miscellaneous = self.human.ask_int(query, min = 0, max = self.gold, cmd = False)
        self.gold -= self.miscellaneous
        # Inform the player of the balance.
        self.human.tell('After all of your purchases, you have {} pieces of gold left.'.format(self.gold))

    def player_action(self, player):
        """
        Handle a player's action during a turn. (bool)

        Parameters:
        player: The player whose turn it is. (player.Player)
        """
        # Check for initial purchases.
        if not self.turns:
            self.initial_purchases()
        # Update the date.
        self.human.tell('\n{}'.format(self.date).replace(' 0', ' '))
        # Make any necessary alerts.
        if self.spam < 12:
            self.human.tell('You better do some hunting or buy food soon!')
        if self.coconuts < 11:
            self.human.tell('Your steeds have just about beaten those coconuts to death.')
        if self.fort_option:
            self.human.tell('You can see a castle in the distance.')
        # Update the human and get the action.
        self.show_status()
        action = self.human.ask('\nWhat would you like to do? ')
        go = self.handle_cmd(action)
        if not go and not self.force_end:
            self.fort_option = not self.fort_option

    def set_up(self):
        """Set up the game. (None)"""
        self.credits_index = 0
        # Set purchasables.
        self.arrows = 0
        self.clothes = 0
        self.coconuts = 0
        self.miscellaneous = 0
        self.spam = 0
        self.steeds = 0
        # Set tracking variables.
        self.date = datetime.date(932, 4, 12)
        self.fortnight = datetime.timedelta(days = 14)
        self.fort_option = True
        self.gold = 700
        self.mileage = 0

    def show_status(self):
        """Show the current consumables. (None)"""
        self.human.tell('You have travelled {} miles.'.format(self.mileage))
        self.human.tell('You have:')
        self.human.tell('{} cans of spam,'.format(self.spam))
        self.human.tell('{} arrows,'.format(self.arrows))
        self.human.tell('{} gold pieces worth of clothing,'.format(self.clothing))
        self.human.tell('{} gold pieces worth of miscellaneous supplies,'.format(self.miscellaneous))
        self.human.tell('{} coconuts, and'.format(self.coconuts))
        self.huamn.tell('{} pieces of gold.'.format(self.gold))
