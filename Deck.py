import random, variables
from Card import Card

class Deck:

    def __init__(self):
        self.cards = []
        for rank in variables.ranks:
            for suit in variables.suits:
                self.cards.append(Card(suit, rank))
    
    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        dealt_card = self.cards.pop(0)
        self.cards.append(dealt_card)
        return dealt_card
    
    def __str__(self):
        return str(self.cards)
