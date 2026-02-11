import pygame
from config import settings

class ResourceManager:
    def __init__(self):
        self.card_images = {}
        self.fonts = {}
        self.images = {}
        self.sounds = {}
        self.load_resources()

    def load_resources(self):
        # Load fonts 
        self.fonts['primary_large'] = pygame.font.Font('assets\\fonts\\primary-font.ttf', 48)
        self.fonts['primary_medium'] = pygame.font.Font('assets\\fonts\\primary-font.ttf', 36)
        self.fonts['primary_small'] = pygame.font.Font('assets\\fonts\\primary-font.ttf', 24)
        self.fonts['chips'] = pygame.font.Font('assets\\fonts\\chips-font.ttf', 24)

        # Load images
        self.images['bg'] = pygame.image.load('assets\\bg.jpg')
        self.images['bg'] = pygame.transform.scale(self.images['bg'], (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))

        self.images['tutorial_img'] = pygame.image.load('assets\\tutorial.png')
        self.images['tutorial_img'] = pygame.transform.scale(self.images['tutorial_img'], (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))

        self.images['card_back'] = pygame.image.load('assets\\cards\\cardback.png')
        self.images['card_back'] = pygame.transform.scale(self.images['card_back'], (100, 145))

        # Load card images
        self._load_card_images()

        # Load sounds
        # Background music
        bg_music = pygame.mixer.Sound('assets\\sounds\\background\\bg.mp3')
        bg_music.set_volume(0.5)
        self.sounds['bg_music'] = bg_music

    def _load_card_images(self):
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

    def play_sound(self, sound_key, loop=False):
        """Play a sound effect"""
        if sound_key in self.sounds:
            self.sounds[sound_key].play(-1 if loop else 0)

    def stop_sound(self, sound_key):
        """Stop a sound effect"""
        if sound_key in self.sounds:
            self.sounds[sound_key].stop()