# Blackjack Game

A Python-based Blackjack game with both console and GUI elements, featuring object-oriented design and classic blackjack gameplay mechanics.

## Features

- **Classic Blackjack Rules**: Standard 21-point gameplay with dealer AI
- **Special Cases**: 
  - BlackJack (21 with 2 cards)
  - Double Aces handling
  - 5-card Charlie (5 cards under 21)
- **Player Management**: Chip-based betting system with insufficient funds handling
- **Interactive Gameplay**: Console-based interface with clear display
- **Pygame Integration**: Basic GUI setup (expandable)

## Game Structure

### Core Classes

- **[Card](Card.py)**: Represents individual playing cards with suit and rank
- **[Deck](Deck.py)**: Manages the deck of cards with shuffle and deal functionality
- **[Hand](Hand.py)**: Handles card collections and value calculations with Ace adjustment
- **[Bot](Bot.py)**: Base class for game participants with common card operations
- **[Player](Player.py)**: Extends Bot with chip management and betting functionality
- **[Dealer](Dealer.py)**: Extends Bot with dealer-specific card display methods
- **[Game](Game.py)**: Main game controller managing gameplay flow and user interaction

### Configuration

- **[variables.py](variables.py)**: Global game constants including card suits, ranks, and values

## Installation

1. Clone the repository
2. Ensure you have Python 3.x installed
3. Install pygame dependency:
   ```bash
   pip install pygame
   ```
4. Ensure you have the background image at `assets/bg.jpg` (or update the path in [`Game.py`](Game.py))

## How to Play

1. Run the game:
   ```bash
   python main.py
   ```

2. **Starting**: You begin with 100 chips

3. **Betting**: Enter your bet amount (cannot exceed available chips)

4. **Gameplay**:
   - You and the dealer each receive 2 cards
   - Dealer's second card is hidden initially
   - Choose to **Hit** (take another card) or **Stand** (keep current hand)
   - If your value is under 16, you must hit
   - Try to get as close to 21 as possible without going over

5. **Winning Conditions**:
   - **Blackjack**: 21 with first 2 cards (10/J/Q/K + Ace)
   - **5-Card Charlie**: 5 cards totaling 21 or less
   - **Regular Win**: Closer to 21 than dealer without busting
   - **Tie**: Same value as dealer (get your bet back)

## Special Rules

- **Ace Value**: Automatically adjusted between 1 and 11 for optimal hand value
- **Face Cards**: Jack, Queen, King all worth 10 points
- **Dealer Logic**: Must hit until reaching 17 or higher
- **Bust**: Both player and dealer bust results in a tie

## Code Architecture

The game uses inheritance with [`Bot`](Bot.py) as the base class for both [`Player`](Player.py) and [`Dealer`](Dealer.py), ensuring shared functionality while allowing for specialized behavior. The [`Hand`](Hand.py) class manages complex card value calculations, including Ace adjustments and special case detection.

## Future Enhancements

- Complete pygame GUI implementation
- Multiple player support  
- Advanced betting options (double down, split)
- Card counting statistics
- Sound effects and animations
- Save/load game progress

## File Structure

```
├── main.py           # Entry point
├── Game.py           # Game controller
├── Player.py         # Player class with betting
├── Dealer.py         # Dealer class  
├── Bot.py            # Base class for players
├── Hand.py           # Hand management
├── Deck.py           # Deck operations
├── Card.py           # Card representation
├── variables.py      # Game constants
└── assets/           # Game assets (images)
```

## Requirements

- Python 3.x
- pygame library
- Standard library modules: `os`, `time`, `random`

Enjoy the game! 🃏♠️♥️♦️♣️
