from Deck import Deck
from Hand import Hand
from Bot import Bot
import variables

class Dealer(Bot):

    def __init__(self):
        super().__init__()

    def show_card_first(self):
        hand = self.hand
        print(hand.cards[0], end=', ')
        print('Unknown')
