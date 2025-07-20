from Player import Player, InsufficientChipsError
from Dealer import Dealer
from Deck import Deck
import os, time, pygame

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


class Game:
    
    def __init__(self):
        self.player = Player(100)
        self.dealer = Dealer()
        self.deck = Deck()

        # Pygame
        pygame.init()
        self.size = (800, 600)
        self.win = pygame.display.set_mode((self.size))
        pygame.display.set_caption('BlackJack Game')

        # Background
        self.bg_img = pygame.image.load('D:\\python\\Blackjack\\assets\\bg.jpg')
        self.bg = pygame.transform.scale(self.bg_img, self.size)

    def display_table(self, show_dealer: bool, player_special_case=None, dealer_special_case=None):
        clear_terminal()
        
        print('Dealer Hand: ', end='')
        if not show_dealer:
            self.dealer.show_card_first()
            print('Dealer Value: ???')
        else:
            self.dealer.show_card()
            if dealer_special_case is None:
                print(f'Dealer Value: {self.dealer.get_value()}')
            else:
                print(f'Dealer Value: {dealer_special_case}')
        
        print('\n' * 4)

        print('Your Hand: ', end='')
        self.player.show_card()
        if player_special_case is None:
            print(f'Your value: {self.player.get_value()}')
        else:
            print(f'Your value: {player_special_case}')


    def game_start(self):
        clear_terminal()
        print('Welcome to BlackJack.')


    def game_end(self):
        cont = input('Do you like to play again? (y or n) ')
        while cont not in ['y', 'n']:
            print('Invalid choice. Try again.')
            cont = input('Do you like to play again? (y or n) ')
        return cont
    
    def draw_table(self):
        self.win.blit(self.bg, (0,0))
        pygame.display.update()
    
    def play(self):
        self.game_start()
        time.sleep(2)

        cont = 'y'
        while cont == 'y':

            clear_terminal()

            # Player runs out of chips
            if self.player.chips == 0:
                print('You do not have any chips.')
                break

            player_wins, tie, dealer_wins = False, False, False
            self.player.clear_hand()
            self.dealer.clear_hand()

            # Asks player for his/her bet
            print(f'Chip remaining: {self.player.chips}')
            chip = None
            while True:
                try:
                    chip = int(input('Enter the amount of chips you wanna bet: '))
                    self.player.bet(amount=chip)
                except ValueError:
                    print('Invalid value. Try again.')
                    continue
                except InsufficientChipsError:
                    print('Not enough chips. Try again.')
                    continue
                else:
                    break

            # Deals the cards
            self.deck.shuffle()

            self.player.hit(self.deck)
            self.dealer.hit(self.deck)
            self.player.hit(self.deck)
            self.dealer.hit(self.deck)
            player_special_case = self.player.hand.special_cases()

            self.display_table(show_dealer=False, player_special_case=player_special_case)

            if player_special_case is not None:
                player_wins = True
            else:
                # Player's turn
                while self.player.hand.num_of_cards() < 5:
                    
                    if self.player.get_value() < 16:
                        player_decision = input('Not enough value to stand, press h to hit. ')
                        while player_decision not in ['h']:
                            print('Invalid choice. Try again.')
                            player_decision = input('Not enough value to stand, press h to hit. ')
                        self.player.hit(self.deck)
                    
                    elif self.player.is_bust():
                        break

                    else:
                        player_decision = input('Do you want to hit or stand? (h or s) ')
                        while player_decision not in ['h', 's']:
                            print('Invalid choice. Try again.')
                            player_decision = input('Do you want to hit or stand? (h or s) ')
                        
                        if player_decision == 'h':
                            self.player.hit(self.deck)
                        else:
                            break
                    
                    player_special_case = self.player.hand.special_cases()
                    self.display_table(show_dealer=False)

                
                # Dealer's turn
                dealer_special_case = self.dealer.hand.special_cases() 
                self.display_table(show_dealer=True, player_special_case=player_special_case, dealer_special_case=dealer_special_case)
                time.sleep(2)

                if dealer_special_case is not None:
                    dealer_wins = True
                else:
                    if self.player.is_bust():
                        while self.dealer.get_value() < 17 and self.dealer.hand.num_of_cards() < 5:
                            self.dealer.hit(self.deck)
                            dealer_special_case = self.dealer.hand.special_cases()
                            self.display_table(show_dealer=True, player_special_case=player_special_case, dealer_special_case=dealer_special_case)
                            time.sleep(2) 
                        
                        if self.dealer.get_value() > 21:
                            tie = True
                        else:
                            dealer_wins = True

                        self.display_table(show_dealer=True, player_special_case=player_special_case, dealer_special_case=dealer_special_case)
                    
                    elif player_special_case is None:
                        while self.dealer.get_value() <= self.player.get_value() and self.dealer.hand.num_of_cards() < 5:
                            self.dealer.hit(self.deck)
                            dealer_special_case = self.dealer.hand.special_cases() 
                            self.display_table(show_dealer=True, player_special_case=player_special_case, dealer_special_case=dealer_special_case)
                            time.sleep(2)
                            
                        if self.dealer.get_value() > 21:
                            player_wins = True
                        else:
                            dealer_wins = True

                        self.display_table(show_dealer=True, player_special_case=player_special_case, dealer_special_case=dealer_special_case)

                    else: 
                        while not self.dealer.is_bust() and self.dealer.hand.num_of_cards() < 5:
                            self.dealer.hit(self.deck)
                            dealer_special_case = self.dealer.hand.special_cases() 
                            self.display_table(show_dealer=True, player_special_case=player_special_case, dealer_special_case=dealer_special_case)
                            time.sleep(2)
                        
                        if self.dealer.is_bust() or self.player.get_value() < self.dealer.get_value():
                            player_wins = True
                        elif self.dealer.get_value() == self.player.get_value():
                            tie = True
                        else:
                            dealer_wins = True

                        self.display_table(show_dealer=True, player_special_case=player_special_case, dealer_special_case=dealer_special_case)


            # Decide player's chips
            if player_wins:
                self.player.earn(2 * chip)
                print('\nPlayer wins.')
            elif tie:
                self.player.earn(chip)
                print('\nTie.')
            else:
                print('\nDealer wins.')

            
            # Player decide if he/she want to play again or not.
            cont = self.game_end()

        print(f'Your total chips: {self.player.chips}')
        print('Thank you.')

    pygame.quit()