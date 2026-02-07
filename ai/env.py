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
        
        # Deal initial cards
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
        
        # Check if player has usable ace (ace counted as 11)
        usable_ace = 0
        for card in self.player_hand.cards:
            if card.rank == 'Ace' and player_value - 11 >= 0:
                usable_ace = 1
                break
        
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
        
        # Check if player has initial special case (2 cards - BlackJack or DoubleAces)
        # This should win immediately before any action
        if self.player_hand.num_of_cards() == 2:
            player_special = self.player_hand.special_cases()
            if player_special is not None:
                # Player wins immediately with 2-card special case
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
            
            # Game continues
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
        Matches the exact logic from Game.py
        
        Returns:
            int: 1 = player wins, 0 = tie, -1 = player loses
        """
        # Check dealer special case first
        dealer_special = self.dealer_hand.special_cases()
        
        if dealer_special is not None:
            # Dealer has special case - dealer wins immediately
            return -1
        
        # Player bust scenario
        if self.player_hand.value > 21:
            # Dealer plays until value >= 17 or reaches 5 cards
            while self.dealer_hand.value < 17 and self.dealer_hand.num_of_cards() < 5:
                self.dealer_hand.add_card(self.deck.deal())
                dealer_special = self.dealer_hand.special_cases()
                if dealer_special:
                    break
            
            if self.dealer_hand.value > 21:
                return 0  # Tie - both bust
            else:
                return -1  # Dealer wins
        
        # Player didn't bust
        elif player_special_case is None:
            # Normal gameplay - dealer tries to beat player's value
            while self.dealer_hand.value <= self.player_hand.value and self.dealer_hand.num_of_cards() < 5:
                self.dealer_hand.add_card(self.deck.deal())
                dealer_special = self.dealer_hand.special_cases()
                if dealer_special:
                    break
            
            # Determine winner
            if self.dealer_hand.value > 21:
                return 1  # Player wins - dealer bust
            else:
                return -1  # Dealer wins (dealer got higher value or tied and won)
        
        else:
            # Player has special case (5-card hand)
            # Dealer hits until bust or reaches 5 cards
            while not self.dealer_hand.value > 21 and self.dealer_hand.num_of_cards() < 5:
                self.dealer_hand.add_card(self.deck.deal())
                dealer_special = self.dealer_hand.special_cases()
                if dealer_special:
                    break
            
            # Special winning logic for 5-card hands (matches Game.py line 393)
            if self.dealer_hand.value > 21 or self.player_hand.value < self.dealer_hand.value:
                return 1  # Player wins
            elif self.dealer_hand.value == self.player_hand.value:
                return 0  # Tie
            else:
                return -1  # Dealer wins
    
    def is_action_valid(self, action):
        """
        Check if an action is valid in the current state
        
        Args:
            action (int): 0 = HIT, 1 = STAND
            
        Returns:
            bool: True if action is valid
        """
        # Can't stand if player value < 16
        if action == 1 and self.player_hand.value < 16:
            return False
        
        # Can't hit if player has 5 cards or is bust
        if action == 0 and (self.player_hand.num_of_cards() >= 5 or self.player_hand.value > 21):
            return False
        
        return True
