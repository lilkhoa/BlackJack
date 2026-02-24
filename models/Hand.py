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
        if len(self.cards) >= 4:
            self.value = sum(settings.values[card.rank] for card in self.cards)
        else:
            total = 0
            aces = 0
            
            for card in self.cards:
                if card.rank == 'Ace':
                    aces += 1
                else:
                    total += settings.values[card.rank]

            if aces == 0:
                self.value = total
            elif aces == 1:
                if total + 11 <= 21:
                    self.value = total + 11
                elif total + 10 <= 21:
                    self.value = total + 10
                else:
                    self.value = total + 1
            else:
                self.value = total + aces
            
    
    def clear(self):
        self.cards = []
        self.value = 0