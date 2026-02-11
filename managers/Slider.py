import pygame
import os
from config import settings

class Slider:

    def __init__(self, x, y, width, height, min_value, max_value, initial_value=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value if initial_value is not None else min_value

        self.handle_size = height * 2 
        y_offset = (self.handle_size - height) // 2
        handle_y = y - y_offset
        self.handle_rect = pygame.Rect(x, handle_y, self.handle_size, self.handle_size)

        self.handle_img = None
        handle_img_path = os.path.join('assets', 'chip.png')
        original_img = pygame.image.load(handle_img_path).convert_alpha()
        scaled_img = pygame.transform.smoothscale(original_img, (self.handle_size, self.handle_size))
        self.handle_img = self._crop_to_circle(scaled_img)
        
        self.dragging = False
        
        self.COLOR_TRACK = settings.GRAY
        self.COLOR_FILL = settings.GOLD
        self.COLOR_HANDLE = settings.WHITE
        self.COLOR_BORDER = settings.BLACK
        
        self.update_handle_position()

    def _crop_to_circle(self, image):
        size = image.get_size()
        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.ellipse(mask, (255, 255, 255), (0, 0, size[0], size[1]))
        masked_image = image.copy()
        masked_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return masked_image

    def update_handle_position(self):
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        self.handle_x = self.rect.x + int(ratio * self.rect.width)
        self.handle_y = self.rect.y + self.rect.height // 2
        self.handle_rect.topleft = (self.handle_x - self.handle_size // 2, self.handle_y - self.handle_size // 2)

    def is_over_handle(self, pos):
        return self.handle_rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_over_handle(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.handle_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            ratio = (self.handle_x - self.rect.x) / self.rect.width
            self.value = int(self.min_value + ratio * (self.max_value - self.min_value))
            self.update_handle_position()
            
    def set_max(self, new_max):
        self.max_value = new_max
        if self.value > self.max_value:
            self.value = self.max_value
        self.update_handle_position()
    
    def draw(self, surface):
        # Draw track
        pygame.draw.rect(surface, self.COLOR_TRACK, self.rect)
        
        # Draw fill
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, self.handle_x - self.rect.x, self.rect.height)
        pygame.draw.rect(surface, self.COLOR_FILL, fill_rect)
        
        # Draw handle
        surface.blit(self.handle_img, self.handle_rect)
        
        # Draw border
        # pygame.draw.rect(surface, self.COLOR_BORDER, self.rect, 2)