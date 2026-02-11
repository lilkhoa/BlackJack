from config import settings

class Hand:
    
    def __init__(self):
        self.cards = []
        self.value = 0
    
    def add_card(self,card):
        self.cards.append(card)
        self._cal_value()
        
    def num_of_cards(self):
        return len(self.cards)
    
    def special_cases(self):
        if self.num_of_cards() == 2:
            first_card, second_card = self.cards[0], self.cards[1]
            if (first_card.rank in settings.ranks[8:12] and second_card.rank == settings.ranks[-1]) or (second_card.rank in settings.ranks[8:12] and first_card.rank == settings.ranks[-1]):
                return 'BlackJack'
            elif first_card.rank == settings.ranks[-1] and second_card.rank == settings.ranks[-1]:
                return 'DoubleAces'
        elif self.num_of_cards() == 5 and self.value <= 21:
            return f'5-Card Charlie ({self.value})'
        return None
    
    def _cal_value(self):
        total = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == 'Ace':
                aces += 1
            total += settings.values[card.rank]
        
        while total > 21 and aces:
            total -= 10
            aces -= 1
        
        self.value = total
    
    def clear(self):
        self.cards = []
        self.value = 0