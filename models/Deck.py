import random
from config import settings
from models.Card import Card

class Deck:

    def __init__(self):
        self.cards = []
        for rank in settings.ranks:
            for suit in settings.suits:
                self.cards.append(Card(suit, rank))
    
    def shuffle(self):
        random.shuffle(self.cards)

    def fake_shuffle(self):
        self.cards[0] = Card('Hearts', 'Ace')
        self.cards[1] = Card('Spades', 'King')
        self.cards[2] = Card('Diamonds', 'Five')
        self.cards[3] = Card('Clubs', 'Six')
        self.cards[4] = Card('Hearts', 'Queen')
        random.shuffle(self.cards[5:])

    def deal(self):
        dealt_card = self.cards.pop(0)
        self.cards.append(dealt_card)
        return dealt_card
    
    def __str__(self):
        return str(self.cards)
