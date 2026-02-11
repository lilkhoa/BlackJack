import numpy as np
import random
import os


class QLearningAgent:
    """
    Q-Learning agent that learns to play Blackjack
    
    State space is discretized:
    - player_value: 4-31 (28 values)
    - dealer_showing: 2-11 (10 values)
    - player_num_cards: 2-5 (4 values)
    - usable_ace: 0-1 (2 values)
    
    Action space:
    - 0: HIT
    - 1: STAND
    """
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=1.0, epsilon_decay=0.9995, epsilon_min=0.01):
        """
        Initialize the Q-learning agent
        
        Args:
            learning_rate (float): Learning rate (alpha)
            discount_factor (float): Discount factor (gamma)
            epsilon (float): Exploration rate
            epsilon_decay (float): Epsilon decay rate per episode
            epsilon_min (float): Minimum epsilon value
        """
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Initialize Q-table: state -> [Q(s,HIT), Q(s,STAND)]
        # State dimensions: [player_value, dealer_showing, num_cards, usable_ace]
        self.q_table = np.zeros((32, 12, 6, 2, 2))
        
    def get_action(self, state, valid_actions=None, training=True):
        """
        Choose an action using epsilon-greedy policy
        
        Args:
            state (tuple): Current state (player_value, dealer_showing, player_num_cards, usable_ace)
            valid_actions (list): List of valid actions (optional)
            training (bool): Whether in training mode (uses epsilon-greedy if True)
            
        Returns:
            int: Action to take (0=HIT, 1=STAND)
        """
        player_value, dealer_showing, num_cards, usable_ace = state
        
        player_value = max(0, min(31, player_value))
        dealer_showing = max(0, min(11, dealer_showing))
        num_cards = max(0, min(5, num_cards))
        usable_ace = int(usable_ace)
        
        if training and random.random() < self.epsilon:
            # Explore: random valid action
            if valid_actions:
                return random.choice(valid_actions)
            return random.randint(0, 1)
        else:
            # Exploit: choose best action from Q-table
            q_values = self.q_table[player_value, dealer_showing, num_cards, usable_ace]
            if valid_actions:
                if len(valid_actions) == 1:
                    return valid_actions[0]
                
                valid_q = [(action, q_values[action]) for action in valid_actions]
                return max(valid_q, key=lambda x: x[1])[0]
            
            return np.argmax(q_values)
    
    def update(self, state, action, reward, next_state, done):
        """
        Update Q-table using Q-learning update rule
        
        Q(s,a) = Q(s,a) + alpha * [reward + gamma * max(Q(s',a')) - Q(s,a)]
        
        Args:
            state (tuple): Current state
            action (int): Action taken
            reward (float): Reward received
            next_state (tuple): Next state
            done (bool): Whether episode is done
        """
        player_value, dealer_showing, num_cards, usable_ace = state
        player_value = max(0, min(31, player_value))
        dealer_showing = max(0, min(11, dealer_showing))
        num_cards = max(0, min(5, num_cards))
        usable_ace = int(usable_ace)
        
        # Current Q-value
        current_q = self.q_table[player_value, dealer_showing, num_cards, usable_ace, action]
        
        # Calculate target Q-value
        if done:
            target_q = reward
        else:
            next_player_value, next_dealer_showing, next_num_cards, next_usable_ace = next_state
            next_player_value = max(0, min(31, next_player_value))
            next_dealer_showing = max(0, min(11, next_dealer_showing))
            next_num_cards = max(0, min(5, next_num_cards))
            next_usable_ace = int(next_usable_ace)
            
            max_next_q = np.max(self.q_table[next_player_value, next_dealer_showing, next_num_cards, next_usable_ace])
            target_q = reward + self.gamma * max_next_q
        
        # Update Q-value
        self.q_table[player_value, dealer_showing, num_cards, usable_ace, action] += self.lr * (target_q - current_q)
    
    def decay_epsilon(self):
        """Decay epsilon after each episode"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def save(self, filepath):
        """
        Save Q-table to file
        
        Args:
            filepath (str): Path to save Q-table
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        np.save(filepath, self.q_table)
        print(f"Q-table saved to {filepath}")
    
    def load(self, filepath):
        """
        Load Q-table from file
        
        Args:
            filepath (str): Path to load Q-table from
        """
        if os.path.exists(filepath):
            self.q_table = np.load(filepath)
            print(f"Q-table loaded from {filepath}")
            return True
        else:
            print(f"No Q-table found at {filepath}")
            return False
