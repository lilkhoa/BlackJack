from models.Deck import Deck
from models.Hand import Hand
from config import settings

class Bot:

    def __init__(self):
        self.hand = Hand()
        pass

    def hit(self, deck: Deck):
        next_card = deck.deal()
        (self.hand).add_card(next_card)
        
    def get_value(self):
        return self.hand.value
    
    def show_card(self):
        for i, card in enumerate(self.hand.cards):
            if i < len(self.hand.cards) - 1:
                print(card, end=', ')
            else:
                print(card)

    def is_bust(self):
        return self.get_value() > 21
    
    def clear_hand(self):
        self.hand.clear()