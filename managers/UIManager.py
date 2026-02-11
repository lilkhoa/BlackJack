import pygame
from config import settings

class UIManager:
    def __init__(self, window, resource_manager):
        self.window = window
        self.resource_manager = resource_manager
        self.colors = {
            'GREEN': settings.GREEN,
            'WHITE': settings.WHITE,
            'BLACK': settings.BLACK,
            'GOLD': settings.GOLD,
            'GRAY': settings.GRAY,
            'BLUE': settings.BLUE,
            'RED': settings.RED
        }

    def draw_card(self, card, x, y):
        """Draw a card at specified position"""
        card_str = str(card)
        if card_str in self.resource_manager.card_images:
            self.window.blit(self.resource_manager.card_images[card_str], (x, y))

    def draw_text(self, text, font, color, x, y, center=False):
        """Draw text at specified position"""
        text_surface = font.render(text, True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            self.window.blit(text_surface, text_rect)
        else:
            self.window.blit(text_surface, (x, y))

    def draw_button(self, text, x, y, width, height, color, hover_color, action=None):
        """Draw a button and check if it's clicked"""
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        button_rect = pygame.Rect(x, y, width, height)
        
        if button_rect.collidepoint(mouse):
            pygame.draw.rect(self.window, hover_color, button_rect, border_radius=10)
            if click[0] == 1:
                if action:
                    action()
                return True
        else:
            pygame.draw.rect(self.window, color, button_rect, border_radius=10)
        
        pygame.draw.rect(self.window, self.colors['BLACK'], button_rect, 3, border_radius=10)
        self.draw_text(text, self.resource_manager.fonts['primary_small'], self.colors['WHITE'], x + width//2, y + height//2, center=True)
        
        return False

    def show_tutorial(self):
        viewing_tutorial = True
        
        while viewing_tutorial:
            self.window.blit(self.resource_manager.images['tutorial_img'], (0, 0))
            back_clicked = self.draw_button("Back", 50, 50, 150, 50, self.colors['RED'], self.colors['GRAY'])
            
            pygame.display.update()
            
            if back_clicked:
                viewing_tutorial = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return