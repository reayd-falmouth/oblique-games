import os

import pygame
import pygame_gui

from oblique_games import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BROWSER_TITLE,
    ASSETS_DIR,
    BLACK,
    TRANSLUCENT,
    FADE_SPEED,
)
from oblique_games.font import load_fonts, render_wrapped_text
from oblique_games.helpers import load_games, process_game
from oblique_games.shader import ShaderRenderer  # Import ShaderRenderer
from oblique_games.sound import SoundManager  # Import the new class
from oblique_games.ui import update_ui


class Game:
    """Encapsulates game state and rendering logic."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL
        )
        pygame.display.set_caption(BROWSER_TITLE)
        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Pause menu
        self.paused = False
        self.pause_menu = load_games(f"{ASSETS_DIR}/img/", shuffle=False)
        self.paused_page = 1

        # Initialize Sound Manager
        self.sound_manager = SoundManager()
        self.sound_manager.play_background()  # Start looping background sound
        self.sound_manager.play_startup()  # Play game startup sound

        # Load assets
        self.games = load_games(f"{ASSETS_DIR}/games", shuffle=True)
        self.total_games = len(self.games)
        self.current_game_index = 0
        self.fonts = load_fonts()

        # Load the icon image
        icon = pygame.image.load(f"{ASSETS_DIR}/img/icon/icon_64x64.png")
        # Set the window icon
        pygame.display.set_icon(icon)

        # UI state
        self.background_x, self.background_y, self.background_image, self.fade_alpha = (
            update_ui(self.games, self.current_game_index)
        )

        # Initialize ShaderRenderer
        self.shader = ShaderRenderer(self.screen, enabled=True)

    def draw_background(self):
        """Draws the background image with a fade effect."""
        self.screen.fill(BLACK)

        if self.background_image:
            faded_image = self.background_image.copy()
            self.fade_alpha = min(150, self.fade_alpha + FADE_SPEED)
            faded_image.set_alpha(self.fade_alpha)
            self.screen.blit(faded_image, (self.background_x, self.background_y))

    def draw_game_info(self):
        """Renders game metadata and branding details dynamically aligning text with wrapping."""
        if not self.games:
            return

        game = self.games[self.current_game_index]
        if self.paused:
            game = self.pause_menu[self.paused_page]

        metadata = game["metadata"]
        title = metadata.get("name", "Unknown Game")
        game_type = f"Game Type: {game.get('type', 'Unknown')}"
        model = f"Model: {game.get('model', 'Unknown')}"
        prompt = f"Prompt: {metadata.get('task', 'Unknown')}"

        branding_data = game.get("branding_data", {})
        short_description = branding_data.get(
            "short_description", "No description available"
        )

        game_info = [
            ("title", title, False),
            ("metadata", game_type, False),
            ("metadata", model, False),
            ("tags", prompt, False),
            ("metadata", short_description, True),
        ]

        x_start = 50
        y_start = 50
        line_spacing = 10
        extra_spacing = 40
        max_width = SCREEN_WIDTH - 100

        for font_key, text, extra_space in game_info:
            font = self.fonts[font_key]
            text_height = self.get_wrapped_text_height(text, font, max_width)

            if extra_space:
                y_start += extra_spacing

            render_wrapped_text(
                self.screen,
                text,
                (x_start, y_start),
                font,
                box_fill=TRANSLUCENT,
                max_width=max_width,
            )
            y_start += text_height + line_spacing

        tags_info = f"Tags: {', '.join(branding_data.get('tags', []))}"
        tags_position = (50, SCREEN_HEIGHT - 100)
        render_wrapped_text(
            self.screen,
            tags_info,
            tags_position,
            self.fonts["tags"],
            box_fill=TRANSLUCENT,
        )

        page_info = f"{self.current_game_index + 1} of {self.total_games}"

        # Pause menu hack
        if self.paused:
            page_info = f"? of ?"

        page_position = (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50)
        render_wrapped_text(
            self.screen,
            page_info,
            page_position,
            self.fonts["metadata"],
            box_fill=TRANSLUCENT,
        )

    @staticmethod
    def get_wrapped_text_height(text, font, max_width):
        """Calculates the height of wrapped text based on the font and max width."""
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            text_width, _ = font.size(test_line)

            if text_width > max_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        return len(lines) * font.get_height()

    def handle_input(self, event):
        """Handles user input for navigation."""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.paused = not self.paused  # Toggle pause state
                self.paused_page = 1
                self.sound_manager.play_click_sound()  # Play sound on button press
                if self.paused:
                    # Stop background music and play pause menu music
                    self.sound_manager.play_pause_menu_music()
                    (
                        self.background_x,
                        self.background_y,
                        self.background_image,
                        self.fade_alpha,
                    ) = update_ui(self.pause_menu, 1)
                    return True

                else:
                    self.sound_manager.mute_pause_menu_music()
            elif event.key == pygame.K_c:
                self.paused = not self.paused  # Toggle pause state
                self.paused_page = 0
                self.sound_manager.play_click_sound()  # Play sound on button press
                if self.paused:
                    # Stop background music and play pause menu music
                    self.sound_manager.play_pause_menu_music()
                    (
                        self.background_x,
                        self.background_y,
                        self.background_image,
                        self.fade_alpha,
                    ) = update_ui(self.pause_menu, 0)
                    return True

                else:
                    self.sound_manager.mute_pause_menu_music()
            elif not self.paused:
                if event.key == pygame.K_RIGHT:
                    self.current_game_index = (self.current_game_index + 1) % len(
                        self.games
                    )
                    self.sound_manager.play_button_sound()  # Play sound on button press
                elif event.key == pygame.K_LEFT:
                    self.current_game_index = (self.current_game_index - 1) % len(
                        self.games
                    )
                    self.sound_manager.play_button_sound()  # Play sound on button press
                else:
                    self.sound_manager.play_buzz_sound()
                    return True
            else:
                return True
            (
                self.background_x,
                self.background_y,
                self.background_image,
                self.fade_alpha,
            ) = update_ui(self.games, self.current_game_index)

        return True


class GameLoop:
    """Manages the main game loop."""

    def __init__(self):
        self.game = Game()
        self.running = True

    def run(self):
        """Executes the main loop."""
        while self.running:
            for event in pygame.event.get():
                self.running = self.game.handle_input(event)

            self.game.draw_background()
            self.game.draw_game_info()

            # Render shader effect before flipping display
            self.game.shader.render(self.game.screen)

        pygame.quit()


if __name__ == "__main__":
    GameLoop().run()
