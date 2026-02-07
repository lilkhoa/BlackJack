# Blackjack Game

A Python-based Blackjack game with pygame GUI and AI-powered dealer using Q-learning reinforcement learning.

## Features

- **Pygame GUI**: Full graphical interface with card images and interactive gameplay
- **AI Dealer**: Trained using Q-learning on 100,000+ games
- **"House" Blackjack Rules**: Standard 21-point gameplay with special mechanics
- **Special Cases**: 
  - BlackJack (21 with 2 cards: 10/J/Q/K + Ace)
  - Double Aces (2 Aces)
  - 5-card Charlie (5 cards totaling 21 or less)
- **Chip System**: Betting system starting with 100 chips

## Game Structure

### Core Components

**Models**
- **Card**: Individual playing cards with suit and rank
- **Deck**: 52-card deck with shuffle and deal functionality
- **Hand**: Card collection with automatic value calculation and Ace adjustment

**Entities**
- **Bot**: Base class for game participants
- **Player**: Player with chip management and betting
- **Dealer**: Dealer with AI or rule-based behavior

**Game**
- **Game**: Main controller with pygame GUI and game loop

**AI System**
- **env.py**: Simplified Blackjack environment for fast training (no graphics)
- **agent.py**: Q-learning agent with epsilon-greedy exploration
- **train.py**: Training script for the AI dealer

### Configuration

- **settings.py**: Global game constants (suits, ranks, values)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Play

1. Run the game:
   ```bash
   python main.py
   ```

2. **Starting**: 
   - Click "Start Game" on the welcome screen
   - You begin with 100 chips
   - AI Dealer mode activates if trained model exists

3. **Betting**: Type your bet amount and press Enter

4. **Gameplay**:
   - You and dealer each receive 2 cards
   - Dealer's second card is hidden initially
   - Click the deck to Hit (take another card)
   - Click Stand button when ready (only if value >= 16)
   - If your value is under 16, you must hit

5. **Winning Conditions**:
   - **Blackjack/Double Aces**: Win immediately with 2.5x payout
   - **5-Card Charlie**: 5 cards totaling 21 or less
   - **Regular Win**: Closer to 21 than dealer (2x payout)
   - **Tie**: Same value as dealer (bet returned)

## Training the AI Dealer

The game includes a Q-learning AI that learns optimal Blackjack strategy:

1. Train the AI (takes a few minutes):
   ```bash
   python ai/train.py
   ```

2. Training details:
   - Runs 100,000 episodes
   - Learns state-action values for all game situations
   - Saves trained model to `ai/data/q_table.npy`
   - Tests performance on 10,000 additional games

3. The trained AI dealer will be automatically loaded when you run the game

## Special Rules

- **Ace Value**: Automatically adjusted between 1 and 11 for optimal hand value
- **Face Cards**: Jack, Queen, King all worth 10 points
- **Must Hit Rule**: Cannot stand if hand value is below 16
- **Dealer AI**: Uses learned strategy from training (or rule-based if not trained)
- **Bust Tie**: Both player and dealer bust results in a tie

## File Structure

```
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── README.md               # This file
├── game/
│   ├── Game.py             # Main game controller with pygame GUI
├── entities/
│   ├── Bot.py              # Base class for players
│   ├── Player.py           # Player with chip management
│   └── Dealer.py           # Dealer behavior
├── models/
│   ├── Card.py             # Card representation
│   ├── Deck.py             # Deck operations
│   └── Hand.py             # Hand management and value calculation
├── config/
│   └── settings.py         # Game constants
├── ai/
│   ├── env.py              # Training environment (no graphics)
│   ├── agent.py            # Q-learning agent
│   ├── train.py            # Training script
│   └── data/
│       └── q_table.npy     # Trained model (generated after training)
└── assets/
    ├── bg.jpg              # Background image
    ├── tutorial.png        # Tutorial screen
    └── cards/              # Card images organized by rank
```

Made by lilkhoa
