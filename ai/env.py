import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.Deck import Deck
from models.Hand import Hand
from config import settings


class BlackjackEnv:
    """
    Simplified Blackjack environment
    
    State: (player_value, dealer_showing, player_num_cards, usable_ace)
    Actions: 0 = HIT, 1 = STAND
    """
    
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.done = False
        
    def reset(self):
        """
        Reset the environment and return initial state
        
        Returns:
            tuple: (player_value, dealer_showing, player_num_cards, usable_ace)
        """
        self.player_hand.clear()
        self.dealer_hand.clear()
        self.deck = Deck()
        self.deck.shuffle()
        self.done = False
        
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        
        return self._get_state()
    
    def _get_state(self):
        """
        Get current state representation
        
        Returns:
            tuple: (player_value, dealer_showing, player_num_cards, usable_ace)
        """
        player_value = self.player_hand.value
        dealer_showing = settings.values[self.dealer_hand.cards[0].rank]
        player_num_cards = self.player_hand.num_of_cards()
        
        usable_ace = 0
        num_aces = sum(1 for card in self.player_hand.cards if card.rank == 'Ace')
        if num_aces > 0:
            value_aces_as_1 = sum(
                1 if card.rank == 'Ace' else settings.values[card.rank] 
                for card in self.player_hand.cards
            )
            if player_value > value_aces_as_1:
                usable_ace = 1
        
        return (player_value, dealer_showing, player_num_cards, usable_ace)
    
    def step(self, action):
        """
        Take an action and return the result
        
        Args:
            action (int): 0 = HIT, 1 = STAND
            
        Returns:
            tuple: (state, reward, done)
                - state: new state after action
                - reward: reward for this action (1 = win, 0 = tie, -1 = lose)
                - done: whether the game is over
        """
        if self.done:
            raise Exception("Game is already done. Call reset() to start a new game.")
        
        # Check if player has initial special case
        if self.player_hand.num_of_cards() == 2:
            player_special = self.player_hand.special_cases()
            if player_special is not None:
                self.done = True
                return self._get_state(), 1, self.done
        
        # ACTION: HIT
        if action == 0:
            self.player_hand.add_card(self.deck.deal())
            
            # Check for player special cases after hitting
            player_special = self.player_hand.special_cases()
            
            # Check if player busts
            if self.player_hand.value > 21:
                self.done = True
                reward = self._play_dealer_and_get_reward(player_special_case=player_special)
                return self._get_state(), reward, self.done
            
            # Check if player has 5 cards (will have special case or be over 21)
            if self.player_hand.num_of_cards() >= 5:
                self.done = True
                reward = self._play_dealer_and_get_reward(player_special_case=player_special)
                return self._get_state(), reward, self.done
            
            return self._get_state(), 0, self.done
        
        # ACTION: STAND
        else:
            player_special = self.player_hand.special_cases()
            self.done = True
            reward = self._play_dealer_and_get_reward(player_special_case=player_special)
            return self._get_state(), reward, self.done
    
    def _play_dealer_and_get_reward(self, player_special_case=None):
        """
        Let dealer play and determine the reward
        Matches EXACT logic from Game.py lines 326-414
        
        Returns:
            int: 1 = player wins, 0 = tie, -1 = player loses
        """
        dealer_special = self.dealer_hand.special_cases()
        
        # Dealer has initial special case - dealer wins immediately
        if dealer_special is not None:
            return -1
        
        # Dealer plays based on player's state
        if self.player_hand.value > 21:
            while self.dealer_hand.value < 17 and self.dealer_hand.num_of_cards() < 5:
                self.dealer_hand.add_card(self.deck.deal())
                dealer_special = self.dealer_hand.special_cases()
                if dealer_special:
                    break
        
        elif player_special_case is None:
            while self.dealer_hand.value <= self.player_hand.value and self.dealer_hand.num_of_cards() < 5:
                self.dealer_hand.add_card(self.deck.deal())
                dealer_special = self.dealer_hand.special_cases()
                if dealer_special:
                    break
        
        else:
            while not self.dealer_hand.value > 21 and self.dealer_hand.num_of_cards() < 5:
                self.dealer_hand.add_card(self.deck.deal())
                dealer_special = self.dealer_hand.special_cases()
                if dealer_special:
                    break
        
        player_val = self.player_hand.value
        dealer_val = self.dealer_hand.value
        
        player_is_bust = self.player_hand.value > 21
        dealer_is_bust = self.dealer_hand.value > 21
        
        player_has_5_charlie = player_special_case is not None and '5-Card Charlie' in str(player_special_case)
        dealer_has_5_charlie = dealer_special is not None and '5-Card Charlie' in str(dealer_special)
        
        if player_is_bust and dealer_is_bust:
            return 0
        elif player_is_bust:
            return -1
        elif dealer_is_bust:
            return 1
        
        elif player_has_5_charlie and dealer_has_5_charlie:
            if player_val < dealer_val:
                return 1
            elif player_val > dealer_val:
                return -1
            else:
                return 0
        elif player_has_5_charlie:
            return 1
        elif dealer_has_5_charlie:
            return -1
        
        else:
            if player_val > dealer_val:
                return 1
            elif dealer_val > player_val:
                return -1
            else:
                return 0
    
    def is_action_valid(self, action):
        """
        Check if an action is valid in the current state
        
        Args:
            action (int): 0 = HIT, 1 = STAND
            
        Returns:
            bool: True if action is valid
        """
        if action == 1 and self.player_hand.value < 16:
            return False
        if action == 0 and (self.player_hand.num_of_cards() >= 5 or self.player_hand.value > 21):
            return False
        
        return True
