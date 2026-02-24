from entities.Player import Player, InsufficientChipsError
from entities.Dealer import Dealer
from models.Deck import Deck
from managers.ResoureManager import ResourceManager
from managers.UIManager import UIManager
from managers.Slider import Slider
from config import settings
from ai.agent import QLearningAgent
import os, time, pygame

class Game:
    
    def __init__(self):
        self.player = Player(100)
        self.dealer = Dealer()
        self.deck = Deck()

        # Pygame initialization
        pygame.init()
        self.width, self.height = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('BlackJack Game')
        self.clock = pygame.time.Clock()

        # Load resources
        self.resource_manager = ResourceManager()
        self.font_large = self.resource_manager.fonts['primary_large']
        self.font_medium = self.resource_manager.fonts['primary_medium']
        self.font_small = self.resource_manager.fonts['primary_small']
        self.chip_font = self.resource_manager.fonts['chips']
        self.bg = self.resource_manager.images['bg']
        self.tutorial_img = self.resource_manager.images['tutorial_img']
        self.card_back = self.resource_manager.images['card_back']
        self.card_images = self.resource_manager.card_images

        # Load sounds
        self.resource_manager.play_sound('bg_music', loop=True)

        # Load UI
        self.ui_manager = UIManager(self.win, ResourceManager())
        self.WHITE = settings.WHITE
        self.GREEN = settings.GREEN
        self.RED = settings.RED
        self.GOLD = settings.GOLD
        self.GRAY = settings.GRAY
        self.BLUE = settings.BLUE

        # Load slider for betting
        slider_x = (self.width - 400) // 2
        slider_y = 350
        self.bet_slider = Slider(slider_x, slider_y, 400, 20, 1, 100)
        
        # Load AI agent for dealer
        self.dealer_ai = QLearningAgent()
        ai_path = os.path.join('ai', 'data', 'q_table.npy')
        if os.path.exists(ai_path):
            self.dealer_ai.load(ai_path)
            self.use_ai_dealer = True
        else:
            self.use_ai_dealer = False
        
        # Game state
        self.game_message = ""
        self.show_dealer_cards = False
        self.waiting_for_action = False
        self.game_over_state = False
        self.betting_phase = True
        self.bet_input = ""
        self.result_message = ""

    def display_table(self, show_dealer: bool, player_special_case=None, dealer_special_case=None):
        """Draw the game table with pygame"""
        self.win.blit(self.resource_manager.images['bg'], (0, 0))
        
        # Draw dealer's cards
        dealer_x = 100
        dealer_y = 100
        self.ui_manager.draw_text("Dealer's Hand:", self.resource_manager.fonts['primary_small'], self.WHITE, dealer_x, dealer_y - 40)
        
        if not show_dealer:
            # Show only first card, hide second
            if len(self.dealer.hand.cards) > 0:
                self.ui_manager.draw_card(self.dealer.hand.cards[0], dealer_x, dealer_y)
            if len(self.dealer.hand.cards) > 1:
                self.win.blit(self.resource_manager.images['card_back'], (dealer_x + 110, dealer_y))
            # Draw remaining cards if any
            for i in range(2, len(self.dealer.hand.cards)):
                self.win.blit(self.resource_manager.images['card_back'], (dealer_x + 110 * i, dealer_y))
            self.ui_manager.draw_text("Value: ???", self.resource_manager.fonts['primary_small'], self.WHITE, dealer_x, dealer_y + 160)
        else:
            # Show all dealer cards
            for i, card in enumerate(self.dealer.hand.cards):
                self.ui_manager.draw_card(card, dealer_x + 110 * i, dealer_y)
            
            if dealer_special_case:
                self.ui_manager.draw_text(f"Value: {dealer_special_case}", self.resource_manager.fonts['primary_small'], self.GOLD, dealer_x, dealer_y + 160)
            else:
                self.ui_manager.draw_text(f"Value: {self.dealer.get_value()}", self.resource_manager.fonts['primary_small'], self.WHITE, dealer_x, dealer_y + 160)
        
        # Draw player's cards
        player_x = 100
        player_y = 450
        self.ui_manager.draw_text("Your Hand:", self.resource_manager.fonts['primary_small'], self.WHITE, player_x, player_y - 40)
        
        for i, card in enumerate(self.player.hand.cards):
            self.ui_manager.draw_card(card, player_x + 110 * i, player_y)
        
        if player_special_case:
            self.ui_manager.draw_text(f"Value: {player_special_case}", self.resource_manager.fonts['primary_small'], self.GOLD, player_x, player_y + 160)
        else:
            self.ui_manager.draw_text(f"Value: {self.player.get_value()}", self.resource_manager.fonts['primary_small'], self.WHITE, player_x, player_y + 160)
        
        # Draw chip information
        self.ui_manager.draw_text(f"Chips: {self.player.chips}", self.resource_manager.fonts['primary_small'], self.GOLD, self.width - 250, 50)
        self.ui_manager.draw_text(f"Current Bet: {self.current_bet}", self.resource_manager.fonts['primary_small'], self.GOLD, self.width // 2 - 100, 50)
        
        # Draw game message if any
        if self.game_message:
            self.ui_manager.draw_text(self.game_message, self.resource_manager.fonts['primary_small'], self.WHITE, self.width // 2, 350, center=True)
    
    def _get_dealer_state(self):
        """Get dealer state for AI agent (from dealer's perspective)"""
        dealer_value = self.dealer.hand.value
        player_showing = settings.values[self.player.hand.cards[0].rank] if len(self.player.hand.cards) > 0 else 0
        dealer_num_cards = self.dealer.hand.num_of_cards()
        
        usable_ace = 0
        for card in self.dealer.hand.cards:
            if card.rank == 'Ace' and dealer_value - 11 >= 0:
                usable_ace = 1
                break
        
        return (dealer_value, player_showing, dealer_num_cards, usable_ace)
    
    def _dealer_ai_turn(self):
        """Let AI dealer play until it decides to stand or busts/reaches 5 cards"""
        while self.dealer.hand.num_of_cards() < 5 and not self.dealer.is_bust():
            state = self._get_dealer_state()

            valid_actions = []
            if self.dealer.get_value() >= 16:
                valid_actions.append(1)  # Can STAND
            if self.dealer.hand.num_of_cards() < 5 and self.dealer.get_value() <= 21:
                valid_actions.append(0)  # Can HIT
            
            if not valid_actions or self.dealer.get_value() < 16:
                valid_actions = [0]  # Must HIT
            
            # Get AI decision
            action = self.dealer_ai.get_action(state, valid_actions=valid_actions, training=False)
            
            if action == 0:  # HIT
                self.resource_manager.play_sound('hit_card', maxtime=500)
                self.dealer.hit(self.deck)
                self.dealer_special_case = self.dealer.hand.special_cases()
                self.display_table(show_dealer=True, player_special_case=self.player_special_case, dealer_special_case=self.dealer_special_case)
                pygame.display.update()
                pygame.time.wait(1000)
                
                # Check for special cases or bust
                if self.dealer_special_case or self.dealer.is_bust() or self.dealer.hand.num_of_cards() >= 5:
                    break
            else:  # STAND
                break
    
    def play(self):
        """Main game loop with pygame"""
        waiting_start = True
        
        while waiting_start:
            self.win.blit(self.bg, (0, 0))
            self.ui_manager.draw_text('Welcome to BlackJack', self.font_large, self.GOLD, self.width // 2, self.height // 2 - 100, center=True)
            
            start_clicked = self.ui_manager.draw_button("Start Game", self.width // 2 - 100, self.height // 2 + 50, 200, 60, self.GREEN, self.GRAY)
            tutorial_clicked = self.ui_manager.draw_button("Tutorial", self.width // 2 - 100, self.height // 2 + 130, 200, 60, self.BLUE, self.GRAY)
            
            pygame.display.update()

            if start_clicked:
                waiting_start = False
            
            if tutorial_clicked:
                self.ui_manager.show_tutorial()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
        
        running = True
        game_active = True
        
        while running:
            self.clock.tick(60)
            
            # Check if player has chips
            if self.player.chips == 0 and not game_active:
                self.win.blit(self.bg, (0, 0))
                self.ui_manager.draw_text('You do not have any chips.', self.font_large, self.RED, self.width // 2, self.height // 2 - 50, center=True)
                self.ui_manager.draw_text('Game Over', self.font_large, self.RED, self.width // 2, self.height // 2 + 50, center=True)
                quit = self.ui_manager.draw_button("Quit", self.width // 2 - 75, self.height // 2 + 150, 150, 50, self.RED, self.GRAY)
                pygame.display.update()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if (self.width // 2 - 75 <= event.pos[0] <= self.width // 2 + 75 and
                            self.height // 2 + 150 <= event.pos[1] <= self.height // 2 + 200):
                            self.resource_manager.play_sound('button_click', loop=False)
                            running = False
                            game_active = False
                continue
            
            # Start new round
            if game_active and self.betting_phase:
                self.win.blit(self.bg, (0, 0))
                
                # Show betting interface
                self.bet_slider.set_max(self.player.chips)

                self.ui_manager.draw_text(f'Chips: {self.player.chips}', self.font_medium, self.GOLD, self.width // 2, 200, center=True)
                self.ui_manager.draw_text('Select bet amount:', self.font_medium, self.WHITE, self.width // 2, 300, center=True)
                self.bet_input = self.bet_slider.value
                if self.bet_input == self.player.chips:
                    self.ui_manager.draw_text(f'ALL IN', self.font_medium, self.GOLD, self.width // 2, 400, center=True)
                else:
                    self.ui_manager.draw_text(f'{self.bet_input}', self.font_large, self.GOLD, self.width // 2, 400, center=True)

                self.bet_slider.draw(self.win)

                self.ui_manager.draw_button("DEAL", self.width // 2 - 75, 500, 150, 50, self.GREEN, self.GRAY)
                
                if self.game_message:
                    self.ui_manager.draw_text(self.game_message, self.font_small, self.RED, self.width // 2, 450, center=True)
                
                pygame.display.update()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    self.bet_slider.handle_event(event)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if (self.width // 2 - 75 <= event.pos[0] <= self.width // 2 + 75 and
                            500 <= event.pos[1] <= 550):
                            try:
                                chip = int(self.bet_input)
                                self.player.bet(amount=chip)
                                
                                # Start the game round
                                self.current_bet = chip
                                self.betting_phase = False
                                self.game_message = ""
                                
                                # Deal cards
                                self.player.clear_hand()
                                self.dealer.clear_hand()
                                self.deck.shuffle()
                                # self.deck.fake_shuffle()
                                
                                self.resource_manager.play_sound('hit_card', maxtime=500)
                                self.player.hit(self.deck)
                                self.dealer.hit(self.deck)
                                self.player.hit(self.deck)
                                self.dealer.hit(self.deck)
                                
                                self.player_special_case = self.player.hand.special_cases()
                                self.show_dealer_cards = False
                                
                                if self.player_special_case is not None:
                                    # Player wins immediately
                                    self.resource_manager.play_sound('win_sound', maxtime=1000)
                                    self.show_dealer_cards = True
                                    self.dealer_special_case = self.dealer.hand.special_cases()
                                    self.player.earn(int(2.5 * chip))
                                    self.result_message = "Player wins!"
                                    self.game_over_state = True
                                    self.waiting_for_action = False
                                else:
                                    self.waiting_for_action = True
                                    self.game_over_state = False
                                
                                self.bet_input = ""
                                
                            except ValueError:
                                self.game_message = "Invalid value. Try again."
                                self.bet_input = ""
                            except InsufficientChipsError:
                                self.game_message = "Not enough chips. Try again."
                                self.bet_input = ""
            
            # Player's turn
            elif game_active and not self.betting_phase and self.waiting_for_action:
                self.display_table(show_dealer=False, player_special_case=self.player_special_case)
                
                # Draw deck for hitting
                deck_x = self.width - 250
                deck_y = 350
                self.win.blit(self.card_back, (deck_x, deck_y))
                self.ui_manager.draw_text("Click deck", self.font_small, self.WHITE, deck_x + 50, deck_y + 160, center=True)
                self.ui_manager.draw_text("to HIT", self.font_small, self.WHITE, deck_x + 50, deck_y + 185, center=True)
                
                # Draw stand button (only if player value >= 16)
                if self.player.get_value() >= 16:
                    stand_clicked = self.ui_manager.draw_button("STAND", self.width - 250, deck_y + 220, 100, 50, self.RED, self.GRAY)
                else:
                    self.ui_manager.draw_text("Must HIT", self.font_small, self.RED, self.width - 250 + 50, deck_y + 240, center=True)
                    self.ui_manager.draw_text("(Value < 16)", self.font_small, self.RED, self.width - 250 + 50, deck_y + 265, center=True)
                
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        # Check if clicked on deck
                        if deck_x <= mouse_x <= deck_x + 100 and deck_y <= mouse_y <= deck_y + 145:
                            self.resource_manager.play_sound('hit_card', maxtime=500)
                            self.player.hit(self.deck)
                            self.player_special_case = self.player.hand.special_cases()
                            
                            # Check if player bust or reached 5 cards
                            if self.player.is_bust() or self.player.hand.num_of_cards() >= 5:
                                self.waiting_for_action = False
                    
                        # Check if clicked stand button
                        elif (self.player.get_value() >= 16 and 
                            self.width - 250 <= mouse_x <= self.width - 150 and 
                            deck_y + 220 <= mouse_y <= deck_y + 270):
                            self.resource_manager.play_sound('button_click', loop=False)
                            self.waiting_for_action = False
            
            # Dealer's turn
            elif game_active and not self.betting_phase and not self.waiting_for_action and not self.game_over_state:
                self.show_dealer_cards = True
                self.dealer_special_case = self.dealer.hand.special_cases()
                
                # Display current state
                self.display_table(show_dealer=True, player_special_case=self.player_special_case, dealer_special_case=self.dealer_special_case)
                pygame.display.update()
                pygame.time.wait(1000)
                
                player_wins, tie, dealer_wins = False, False, False
                
                if self.dealer_special_case is not None:
                    dealer_wins = True
                else:
                    # Use AI dealer if trained model is available
                    if self.use_ai_dealer:
                        self._dealer_ai_turn()
                    else:
                        # Fallback to rule-based dealer
                        if self.player.is_bust():
                            while self.dealer.get_value() < 17 and self.dealer.hand.num_of_cards() < 5:
                                self.resource_manager.play_sound('hit_card', maxtime=500)
                                self.dealer.hit(self.deck)
                                self.dealer_special_case = self.dealer.hand.special_cases()
                                self.display_table(show_dealer=True, player_special_case=self.player_special_case, dealer_special_case=self.dealer_special_case)
                                pygame.display.update()
                                pygame.time.wait(1000)
                        
                        elif self.player_special_case is None:
                            while self.dealer.get_value() <= self.player.get_value() and self.dealer.hand.num_of_cards() < 5:
                                self.resource_manager.play_sound('hit_card', maxtime=500)
                                self.dealer.hit(self.deck)
                                self.dealer_special_case = self.dealer.hand.special_cases()
                                self.display_table(show_dealer=True, player_special_case=self.player_special_case, dealer_special_case=self.dealer_special_case)
                                pygame.display.update()
                                pygame.time.wait(1000)
                        
                        else:
                            while not self.dealer.is_bust() and self.dealer.hand.num_of_cards() < 5:
                                self.resource_manager.play_sound('hit_card', maxtime=500)
                                self.dealer.hit(self.deck)
                                self.dealer_special_case = self.dealer.hand.special_cases()
                                self.display_table(show_dealer=True, player_special_case=self.player_special_case, dealer_special_case=self.dealer_special_case)
                                pygame.display.update()
                                pygame.time.wait(1000)
                    
                    player_val = self.player.get_value()
                    dealer_val = self.dealer.get_value()

                    player_is_bust = self.player.is_bust()
                    dealer_is_bust = self.dealer.is_bust()

                    player_has_5_charlie = self.player_special_case is not None and '5-Card Charlie' in self.player_special_case
                    dealer_has_5_charlie = self.dealer_special_case is not None and '5-Card Charlie' in self.dealer_special_case

                    # Bust cases
                    if player_is_bust and dealer_is_bust:
                        tie = True
                    elif player_is_bust:
                        dealer_wins = True
                    elif dealer_is_bust:
                        player_wins = True

                    # 5-Card Charlie cases
                    elif player_has_5_charlie and dealer_has_5_charlie:
                        if player_val < dealer_val:
                            player_wins = True
                        elif player_val > dealer_val:
                            dealer_wins = True
                        else:
                            tie = True
                    elif player_has_5_charlie:
                        player_wins = True
                    elif dealer_has_5_charlie:
                        dealer_wins = True

                    # Normal cases
                    else:
                        if player_val > dealer_val:
                            player_wins = True
                        elif dealer_val > player_val:
                            dealer_wins = True
                        else:
                            tie = True
                
                # Determine result
                if player_wins:
                    self.resource_manager.play_sound('win_sound', maxtime=1000)
                    if self.player_special_case:
                        self.player.earn(int(2.5 * self.current_bet))
                    else:
                        self.player.earn(int(2 * self.current_bet))
                    self.result_message = 'Player wins!'
                elif tie:
                    self.resource_manager.play_sound('tie_sound', maxtime=2000)
                    self.player.earn(int(self.current_bet))
                    self.result_message = 'Tie!'
                else:
                    self.resource_manager.play_sound('lose_sound', maxtime=1000)
                    self.result_message = 'Dealer wins!'
                
                self.game_over_state = True
            
            # Show result and ask for new game
            elif game_active and self.game_over_state:
                self.display_table(show_dealer=True, player_special_case=self.player_special_case, dealer_special_case=self.dealer_special_case)
                
                # Draw result message
                result_color = self.GOLD if 'Player wins' in self.result_message else (self.WHITE if 'Tie' in self.result_message else self.RED)
                self.ui_manager.draw_text(self.result_message, self.font_large, result_color, self.width // 2, 350, center=True)
                
                # Draw play again button
                play_again = self.ui_manager.draw_button("Play Again", self.width // 2 - 75, 420, 150, 50, self.GREEN, self.GRAY)
                quit = self.ui_manager.draw_button("Quit", self.width // 2 - 75, 500, 150, 50, self.RED, self.GRAY)
                
                pygame.display.update()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Play again clicked
                        if (self.width // 2 - 75 <= event.pos[0] <= self.width // 2 + 75 and
                            420 <= event.pos[1] <= 470):
                            self.resource_manager.play_sound('button_click', loop=False)
                            if self.player.chips > 0:
                                self.betting_phase = True
                                self.game_over_state = False
                                self.waiting_for_action = False
                                self.result_message = ""
                                self.game_message = ""
                                self.bet_input = ""
                            else:
                                game_active = False
                        # Quit clicked
                        elif (self.width // 2 - 75 <= event.pos[0] <= self.width // 2 + 75 and
                              500 <= event.pos[1] <= 550):
                            self.resource_manager.play_sound('button_click', loop=False)
                            running = False
                            game_active = False
        
        # Game ended
        self.win.blit(self.bg, (0, 0))
        self.ui_manager.draw_text(f'Your total chips: {self.player.chips}', self.font_large, self.GOLD, self.width // 2, self.height // 2 - 50, center=True)
        self.ui_manager.draw_text('Thank you for playing!', self.font_large, self.WHITE, self.width // 2, self.height // 2 + 50, center=True)
        pygame.display.update()
        pygame.time.wait(3000)
        
        pygame.quit()
