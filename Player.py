from Deck import Deck
from Hand import Hand
from Bot import Bot
import variables

class InsufficientChipsError(Exception):
    """Raised when the player doesn't have enough chips to bet"""
    pass

class Player(Bot):

    def __init__(self, chips: int):
        super().__init__()
        self.chips = chips
    
    def bet(self, amount: int):
        if amount > self.chips:
            raise InsufficientChipsError
        self.chips -= amount

    def earn(self, amount: int):
        self.chips += amount