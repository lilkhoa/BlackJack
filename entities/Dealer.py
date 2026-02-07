from models.Deck import Deck
from models.Hand import Hand
from entities.Bot import Bot
from config import settings

class Dealer(Bot):

    def __init__(self):
        super().__init__()

    def show_card_first(self):
        hand = self.hand
        print(hand.cards[0], end=', ')
        print('Unknown')
