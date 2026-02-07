from entities.Player import Player, InsufficientChipsError
from entities.Dealer import Dealer
from models.Deck import Deck
from config import settings
import os, time, pygame

class Game:
    
    def __init__(self):
        self.player = Player(100)
        self.dealer = Dealer()
        self.deck = Deck()

        # Pygame initialization
        pygame.init()
        self.width, self.height = 1280, 720
        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('BlackJack Game')
        self.clock = pygame.time.Clock()
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 150, 0)
        self.RED = (200, 0, 0)
        self.GOLD = (255, 215, 0)
        self.GRAY = (128, 128, 128)
        
        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)
        
        # Load background
        self.bg_img = pygame.image.load('assets\\bg.jpg')
        self.bg = pygame.transform.scale(self.bg_img, (self.width, self.height))
        
        # Load card images
        self.card_images = {}
        self.load_card_images()
        
        # Load card back
        self.card_back = pygame.image.load('assets\\cards\\cardback.png')
        self.card_back = pygame.transform.scale(self.card_back, (100, 145))
        
        # Game state
        self.game_message = ""
        self.show_dealer_cards = False
        self.waiting_for_action = False
        self.game_over_state = False
        self.betting_phase = True
        self.bet_input = ""
        self.result_message = ""
        
    def load_card_images(self):
        """Load all card images from assets folder"""
        rank_map = {
            'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5',
            'Six': '6', 'Seven': '7', 'Eight': '8', 'Nine': '9',
            'Ten': '10', 'Jack': 'jack', 'Queen': 'queen', 
            'King': 'king', 'Ace': 'ace'
        }
        
        suit_map = {
            'Hearts': 'hearts',
            'Diamonds': 'diamonds',
            'Spades': 'spades',
            'Clubs': 'clubs'
        }
        
        for rank in settings.ranks:
            for suit in settings.suits:
                rank_folder = rank_map[rank]
                file_name = f"{rank_map[rank]}_of_{suit_map[suit]}.png"
                path = f"assets\\cards\\{rank_folder}\\{file_name}"
                
                try:
                    img = pygame.image.load(path)
                    img = pygame.transform.scale(img, (100, 145))
                    self.card_images[f"{rank} of {suit}"] = img
                except:
                    print(f"Error loading: {path}")

    def draw_card(self, card, x, y):
        """Draw a card at specified position"""
        card_str = str(card)
        if card_str in self.card_images:
            self.win.blit(self.card_images[card_str], (x, y))
    
    def draw_text(self, text, font, color, x, y, center=False):
        """Draw text at specified position"""
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            self.win.blit(text_surface, text_rect)
        else:
            self.win.blit(text_surface, (x, y))
    
    def draw_button(self, text, x, y, width, height, color, hover_color, action=None):
        """Draw a button and check if it's clicked"""
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        button_rect = pygame.Rect(x, y, width, height)
        
        if button_rect.collidepoint(mouse):
            pygame.draw.rect(self.win, hover_color, button_rect, border_radius=10)
            if click[0] == 1:
                if action:
                    action()
                return True
        else:
            pygame.draw.rect(self.win, color, button_rect, border_radius=10)
        
        pygame.draw.rect(self.win, self.BLACK, button_rect, 3, border_radius=10)
        self.draw_text(text, self.font_medium, self.WHITE, x + width//2, y + height//2, center=True)
        
        return False
    
    def display_table(self, show_dealer: bool, player_special_case=None, dealer_special_case=None):
        """Draw the game table with pygame"""
        self.win.blit(self.bg, (0, 0))
        
        # Draw dealer's cards
        dealer_x = 100
        dealer_y = 100
        self.draw_text("Dealer's Hand:", self.font_medium, self.WHITE, dealer_x, dealer_y - 40)
        
        if not show_dealer:
            # Show only first card, hide second
            if len(self.dealer.hand.cards) > 0:
                self.draw_card(self.dealer.hand.cards[0], dealer_x, dealer_y)
            if len(self.dealer.hand.cards) > 1:
                self.win.blit(self.card_back, (dealer_x + 110, dealer_y))
            # Draw remaining cards if any
            for i in range(2, len(self.dealer.hand.cards)):
                self.win.blit(self.card_back, (dealer_x + 110 * i, dealer_y))
            self.draw_text("Value: ???", self.font_small, self.WHITE, dealer_x, dealer_y + 160)
        else:
            # Show all dealer cards
            for i, card in enumerate(self.dealer.hand.cards):
                self.draw_card(card, dealer_x + 110 * i, dealer_y)
            
            if dealer_special_case:
                self.draw_text(f"Value: {dealer_special_case}", self.font_small, self.GOLD, dealer_x, dealer_y + 160)
            else:
                self.draw_text(f"Value: {self.dealer.get_value()}", self.font_small, self.WHITE, dealer_x, dealer_y + 160)
        
        # Draw player's cards
        player_x = 100
        player_y = 450
        self.draw_text("Your Hand:", self.font_medium, self.WHITE, player_x, player_y - 40)
        
        for i, card in enumerate(self.player.hand.cards):
            self.draw_card(card, player_x + 110 * i, player_y)
        
        if player_special_case:
            self.draw_text(f"Value: {player_special_case}", self.font_small, self.GOLD, player_x, player_y + 160)
        else:
            self.draw_text(f"Value: {self.player.get_value()}", self.font_small, self.WHITE, player_x, player_y + 160)
        
        # Draw chip information
        self.draw_text(f"Chips: {self.player.chips}", self.font_medium, self.GOLD, self.width - 250, 50)
        
        # Draw game message if any
        if self.game_message:
            self.draw_text(self.game_message, self.font_medium, self.WHITE, self.width // 2, 350, center=True)

    def game_start(self):
        """Display welcome screen"""
        self.win.blit(self.bg, (0, 0))
        self.draw_text('Welcome to BlackJack', self.font_large, self.GOLD, self.width // 2, self.height // 2 - 50, center=True)
        self.draw_text('Click anywhere to start', self.font_medium, self.WHITE, self.width // 2, self.height // 2 + 50, center=True)
        pygame.display.update()


    def game_end(self):
        """Show game end screen and check if player wants to continue"""
        pass
    
    def draw_table(self):
        self.win.blit(self.bg, (0,0))
        pygame.display.update()
    
    def play(self):
        """Main game loop with pygame"""
        # Show welcome screen
        self.game_start()
        waiting_start = True
        
        while waiting_start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    waiting_start = False
        
        running = True
        game_active = True
        
        while running:
            self.clock.tick(60)
            
            # Check if player has chips
            if self.player.chips == 0 and not game_active:
                self.win.blit(self.bg, (0, 0))
                self.draw_text('You do not have any chips.', self.font_large, self.RED, self.width // 2, self.height // 2 - 50, center=True)
                self.draw_text('Game Over', self.font_large, self.RED, self.width // 2, self.height // 2 + 50, center=True)
                quit = self.draw_button("Quit", self.width // 2 - 75, self.height // 2 + 150, 150, 50, self.RED, self.GRAY)
                pygame.display.update()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if (self.width // 2 - 75 <= event.pos[0] <= self.width // 2 + 75 and
                            self.height // 2 + 150 <= event.pos[1] <= self.height // 2 + 200):
                            running = False
                            game_active = False
                continue
            
            # Start new round
            if game_active and self.betting_phase:
                self.win.blit(self.bg, (0, 0))
                
                # Show betting interface
                self.draw_text(f'Chips: {self.player.chips}', self.font_medium, self.GOLD, self.width // 2, 200, center=True)
                self.draw_text('Enter bet amount:', self.font_medium, self.WHITE, self.width // 2, 300, center=True)
                self.draw_text(self.bet_input, self.font_large, self.GOLD, self.width // 2, 360, center=True)
                
                if self.game_message:
                    self.draw_text(self.game_message, self.font_small, self.RED, self.width // 2, 450, center=True)
                
                pygame.display.update()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN and self.bet_input:
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
                                
                                self.player.hit(self.deck)
                                self.dealer.hit(self.deck)
                                self.player.hit(self.deck)
                                self.dealer.hit(self.deck)
                                
                                self.player_special_case = self.player.hand.special_cases()
                                self.show_dealer_cards = False
                                
                                if self.player_special_case is not None:
                                    # Player wins immediately
                                    self.show_dealer_cards = True
                                    self.dealer_special_case = self.dealer.hand.special_cases()
                                    self.player.earn(2 * chip)
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
                        elif event.key == pygame.K_BACKSPACE:
                            self.bet_input = self.bet_input[:-1]
                        elif event.unicode.isdigit():
                            self.bet_input += event.unicode
            
            # Player's turn
            elif game_active and not self.betting_phase and self.waiting_for_action:
                self.display_table(show_dealer=False, player_special_case=self.player_special_case)
                
                # Draw deck for hitting
                deck_x = self.width - 250
                deck_y = 350
                self.win.blit(self.card_back, (deck_x, deck_y))
                self.draw_text("Click deck", self.font_small, self.WHITE, deck_x + 50, deck_y + 160, center=True)
                self.draw_text("to HIT", self.font_small, self.WHITE, deck_x + 50, deck_y + 185, center=True)
                
                # Draw stand button (only if player value >= 16)
                if self.player.get_value() >= 16:
                    stand_clicked = self.draw_button("STAND", self.width - 250, deck_y + 220, 100, 50, self.RED, self.GRAY)
                else:
                    # Show message that player must hit
                    self.draw_text("Must HIT", self.font_small, self.RED, self.width - 250 + 50, deck_y + 240, center=True)
                    self.draw_text("(Value < 16)", self.font_small, self.RED, self.width - 250 + 50, deck_y + 265, center=True)
                
                pygame.display.update()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        
                        # Check if clicked on deck
                        if deck_x <= mouse_x <= deck_x + 100 and deck_y <= mouse_y <= deck_y + 145:
                            self.player.hit(self.deck)
                            self.player_special_case = self.player.hand.special_cases()
                            
                            # Check if player bust or reached 5 cards
                            if self.player.is_bust() or self.player.hand.num_of_cards() >= 5:
                                self.waiting_for_action = False
                    
                        # Check if clicked stand button
                        elif (self.player.get_value() >= 16 and 
                            self.width - 250 <= mouse_x <= self.width - 150 and 
                            deck_y + 220 <= mouse_y <= deck_y + 270):
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
                    if self.player.is_bust():
                        while self.dealer.get_value() < 17 and self.dealer.hand.num_of_cards() < 5:
                            self.dealer.hit(self.deck)
                            self.dealer_special_case = self.dealer.hand.special_cases()
                            self.display_table(show_dealer=True, player_special_case=self.player_special_case, dealer_special_case=self.dealer_special_case)
                            pygame.display.update()
                            pygame.time.wait(1000)
                        
                        if self.dealer.get_value() > 21:
                            tie = True
                        else:
                            dealer_wins = True
                    
                    elif self.player_special_case is None:
                        while self.dealer.get_value() <= self.player.get_value() and self.dealer.hand.num_of_cards() < 5:
                            self.dealer.hit(self.deck)
                            self.dealer_special_case = self.dealer.hand.special_cases()
                            self.display_table(show_dealer=True, player_special_case=self.player_special_case, dealer_special_case=self.dealer_special_case)
                            pygame.display.update()
                            pygame.time.wait(1000)
                        
                        if self.dealer.get_value() > 21:
                            player_wins = True
                        else:
                            dealer_wins = True
                    
                    else:
                        while not self.dealer.is_bust() and self.dealer.hand.num_of_cards() < 5:
                            self.dealer.hit(self.deck)
                            self.dealer_special_case = self.dealer.hand.special_cases()
                            self.display_table(show_dealer=True, player_special_case=self.player_special_case, dealer_special_case=self.dealer_special_case)
                            pygame.display.update()
                            pygame.time.wait(1000)
                        
                        if self.dealer.is_bust() or self.player.get_value() < self.dealer.get_value():
                            player_wins = True
                        elif self.dealer.get_value() == self.player.get_value():
                            tie = True
                        else:
                            dealer_wins = True
                
                # Determine result
                if player_wins:
                    self.player.earn(2 * self.current_bet)
                    self.result_message = 'Player wins!'
                elif tie:
                    self.player.earn(self.current_bet)
                    self.result_message = 'Tie!'
                else:
                    self.result_message = 'Dealer wins!'
                
                self.game_over_state = True
            
            # Show result and ask for new game
            elif game_active and self.game_over_state:
                self.display_table(show_dealer=True, player_special_case=self.player_special_case, dealer_special_case=self.dealer_special_case)
                
                # Draw result message
                result_color = self.GOLD if 'Player wins' in self.result_message else (self.WHITE if 'Tie' in self.result_message else self.RED)
                self.draw_text(self.result_message, self.font_large, result_color, self.width // 2, 350, center=True)
                
                # Draw play again button
                play_again = self.draw_button("Play Again", self.width // 2 - 75, 420, 150, 50, self.GREEN, self.GRAY)
                quit = self.draw_button("Quit", self.width // 2 - 75, 500, 150, 50, self.RED, self.GRAY)
                
                pygame.display.update()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Play again clicked
                        if (self.width // 2 - 75 <= event.pos[0] <= self.width // 2 + 75 and
                            420 <= event.pos[1] <= 470):
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
                            running = False
                            game_active = False
        
        # Game ended
        self.win.blit(self.bg, (0, 0))
        self.draw_text(f'Your total chips: {self.player.chips}', self.font_large, self.GOLD, self.width // 2, self.height // 2 - 50, center=True)
        self.draw_text('Thank you for playing!', self.font_large, self.WHITE, self.width // 2, self.height // 2 + 50, center=True)
        pygame.display.update()
        pygame.time.wait(3000)
        
        pygame.quit()
