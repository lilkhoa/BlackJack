from Deck import Deck
import variables

class Hand:
    
    def __init__(self):
        self.cards = []  # start with an empty list as we did in the Deck class
        self.value = 0   # start with zero value
    
    def add_card(self,card):
        self.cards.append(card)

        if card.rank != variables.ranks[-1]:
            self.value += variables.values[card.rank]
        else:
            self.value += self.adjust_for_ace()
    
    def adjust_for_ace(self):
        if self.value + 11 <= 21:
            return 11
        else:
            return 1
        
    def num_of_cards(self):
        return len(self.cards)
    
    def special_cases(self):
        if self.num_of_cards() == 2:
            first_card, second_card = self.cards[0], self.cards[1]
            if (first_card.rank in variables.ranks[8:12] and second_card.rank == variables.ranks[-1]) or (second_card.rank in variables.ranks[8:12] and first_card.rank == variables.ranks[-1]):
                return 'BlackJack'
            elif first_card.rank == variables.ranks[-1] and second_card.rank == variables.ranks[-1]:
                return 'DoubleAces'
        elif self.num_of_cards() == 5:
            sum = 0
            for card in self.cards:
                sum += variables.values[card.rank]
            if sum <= 21:
                self.value = sum
                return f'5-of-a-kind ({sum})'
        return None
    
    def clear(self):
        self.cards = []
        self.value = 0