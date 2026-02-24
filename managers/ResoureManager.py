import pygame
import os
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
        primary_font_path = os.path.join('assets', 'fonts', 'primary-font.ttf')
        chip_font_path = os.path.join('assets', 'fonts', 'chips-font.ttf')
        self.fonts['primary_large'] = pygame.font.Font(primary_font_path, 48)
        self.fonts['primary_medium'] = pygame.font.Font(primary_font_path, 36)
        self.fonts['primary_small'] = pygame.font.Font(primary_font_path, 24)
        self.fonts['chips'] = pygame.font.Font(chip_font_path, 24)

        # Load images
        bg_path = os.path.join('assets', 'bg.jpg')
        self.images['bg'] = pygame.image.load(bg_path)
        self.images['bg'] = pygame.transform.scale(self.images['bg'], (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))

        tutorial_path = os.path.join('assets', 'tutorial.jpg')
        self.images['tutorial_img'] = pygame.image.load(tutorial_path)
        self.images['tutorial_img'] = pygame.transform.scale(self.images['tutorial_img'], (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))

        card_back_path = os.path.join('assets', 'cards', 'cardback.png')
        self.images['card_back'] = pygame.image.load(card_back_path)
        self.images['card_back'] = pygame.transform.scale(self.images['card_back'], (100, 145))

        # Load card images
        self._load_card_images()

        # Load sounds
        # Background music
        bg_music_path = os.path.join('assets', 'sounds', 'background', 'bg.mp3')
        bg_music = pygame.mixer.Sound(bg_music_path)
        bg_music.set_volume(0.5)
        self.sounds['bg_music'] = bg_music

        # Button click
        button_click_path = os.path.join('assets', 'sounds', 'button_press.mp3')
        button_click = pygame.mixer.Sound(button_click_path)
        button_click.set_volume(0.7)
        self.sounds['button_click'] = button_click

        # Hit card
        hit_card_path = os.path.join('assets', 'sounds', 'hit_card.mp3')
        hit_card = pygame.mixer.Sound(hit_card_path)
        hit_card.set_volume(0.7)
        self.sounds['hit_card'] = hit_card

        # Win sound
        win_sound_path = os.path.join('assets', 'sounds', 'win.wav')
        win_sound = pygame.mixer.Sound(win_sound_path)
        win_sound.set_volume(0.7)
        self.sounds['win_sound'] = win_sound

        # Lose sound
        lose_sound_path = os.path.join('assets', 'sounds', 'lose.wav')
        lose_sound = pygame.mixer.Sound(lose_sound_path)
        lose_sound.set_volume(0.7)
        self.sounds['lose_sound'] = lose_sound

        # Tie sound
        tie_sound_path = os.path.join('assets', 'sounds', 'tie.wav')
        tie_sound = pygame.mixer.Sound(tie_sound_path)
        tie_sound.set_volume(0.7)
        self.sounds['tie_sound'] = tie_sound

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
                path = os.path.join('assets', 'cards', rank_folder, file_name)
                
                try:
                    img = pygame.image.load(path)
                    img = pygame.transform.scale(img, (100, 145))
                    self.card_images[f"{rank} of {suit}"] = img
                except:
                    print(f"Error loading: {path}")

    def play_sound(self, sound_key, loop=False, maxtime=0):
        """Play a sound effect"""
        if sound_key in self.sounds:
            self.sounds[sound_key].play(-1 if loop else 0, maxtime=maxtime)

    def stop_sound(self, sound_key):
        """Stop a sound effect"""
        if sound_key in self.sounds:
            self.sounds[sound_key].stop()
