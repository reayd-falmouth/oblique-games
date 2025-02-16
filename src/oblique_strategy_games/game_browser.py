import json
import os
import random

import pygame
import pygame_gui
import struct
import pygame
from pygame.locals import *

import moderngl

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
VIRTUAL_RES = (160, 120)
REAL_RES = (SCREEN_WIDTH, SCREEN_HEIGHT)
WHITE, BLACK, GREY, TRANSLUCENT_BLACK, TRANSLUCENT = (
    (255, 255, 255),
    (0, 0, 0),
    (200, 200, 200),
    (0, 0, 0, 50),
    (0, 0, 0, 0),
)
IMAGE_SIZE = (300, 300)
COVER_POSITION = (50, 320)
FADE_SPEED = 5  # Speed of background fade effect
TEXT_BOX_PADDING = 10
TEXT_BOX_WIDTH = SCREEN_WIDTH - 100
FPS = 30

# Initialize pygame and pygame_gui
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Browser")
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


# Load custom pixel fonts
title_font = pygame.font.Font(f"fonts/m6x11.ttf", 48)
description_font = pygame.font.Font("fonts/m6x11.ttf", 28)
detailed_description_font = pygame.font.Font("fonts/m6x11.ttf", 14)
metadata_font = pygame.font.Font("fonts/m6x11.ttf", 24)
tags_font = pygame.font.Font("fonts/m6x11.ttf", 20)

# Options
keep_width_mode = True  # Set to False for "Fit to screen" mode, True for "Keep width, clip height"


def load_games(root_dir="./games", shuffle=False):
    games = []
    for game_type in os.listdir(root_dir):
        game_type_path = os.path.join(root_dir, game_type)
        if os.path.isdir(game_type_path):
            for game_name in os.listdir(game_type_path):
                game_path = os.path.join(game_type_path, game_name)
                metadata_file = os.path.join(game_path, "metadata.json")
                cover_file = os.path.join(game_path, "cover.png")

                if os.path.exists(metadata_file) and os.path.exists(cover_file):
                    with open(metadata_file, "r") as f:
                        try:
                            metadata = json.load(f)
                        except json.JSONDecodeError:
                            metadata = {}

                    if isinstance(metadata, dict):
                        branding_data = metadata.get("branding_data", {})
                        if isinstance(branding_data, str):
                            branding_data = {}

                        games.append(
                            {
                                "type": metadata.get("game_type", "Unknown"),
                                "name": metadata.get("name", game_name),
                                "model": metadata.get("model", "Unknown"),
                                "metadata": metadata,
                                "branding_data": branding_data,
                                "cover": cover_file,
                            }
                        )

    if shuffle:
        random.shuffle(games)

    return games


games = load_games(shuffle=True)
current_game_index = 0
total_games = len(games)
cover_image = None
background_image = None
fade_alpha = 0


# Load images dynamically
def load_image(path, size=IMAGE_SIZE):
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, size)
    except pygame.error:
        return None


def render_wrapped_text(surface, text, position, font, box_fill=TRANSLUCENT_BLACK):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= TEXT_BOX_WIDTH:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y_offset = 0
    text_box = pygame.Surface(
        (
            TEXT_BOX_WIDTH + TEXT_BOX_PADDING * 2,
            len(lines) * (font.get_height() + 5) + TEXT_BOX_PADDING * 2,
        ),
        pygame.SRCALPHA,
    )
    text_box.fill(box_fill)
    surface.blit(text_box, (position[0] - TEXT_BOX_PADDING, position[1] - TEXT_BOX_PADDING))

    for line in lines:
        text_surface = font.render(line, True, WHITE)
        surface.blit(text_surface, (position[0], position[1] + y_offset))
        y_offset += font.get_height() + 5


def update_ui():
    global cover_image, background_image, fade_alpha
    if games:
        game = games[current_game_index]
        branding_data = game.get("branding_data", {})

        cover_image = load_image(game["cover"]) if os.path.exists(game["cover"]) else None
        background_image = load_image(game["cover"]) if os.path.exists(game["cover"]) else None
        fade_alpha = 0  # Reset fade effect

        if background_image:
            img_width, img_height = background_image.get_size()
            aspect_ratio = img_width / img_height

            if keep_width_mode:
                # Mode: Keep width, clip height
                new_width = SCREEN_WIDTH
                new_height = int((new_width / img_width) * img_height)

                # Resize the image
                background_image = pygame.transform.smoothscale(background_image, (new_width, new_height))

                # Clip the top and bottom if necessary
                if new_height > SCREEN_HEIGHT:
                    crop_y = (new_height - SCREEN_HEIGHT) // 2
                    background_image = background_image.subsurface((0, crop_y, SCREEN_WIDTH, SCREEN_HEIGHT))

                background_x, background_y = 0, 0

            else:
                # Mode: Fit to screen while maintaining aspect ratio
                if SCREEN_WIDTH / SCREEN_HEIGHT > aspect_ratio:
                    new_height = SCREEN_HEIGHT
                    new_width = int(new_height * aspect_ratio)
                else:
                    new_width = SCREEN_WIDTH
                    new_height = int(new_width / aspect_ratio)

                # Resize while maintaining aspect ratio
                background_image = pygame.transform.smoothscale(background_image, (new_width, new_height))

                # Center the image
                background_x = (SCREEN_WIDTH - new_width) // 2
                background_y = (SCREEN_HEIGHT - new_height) // 2

            return background_x, background_y


background_x, background_y = update_ui()
running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    screen.fill(BLACK)

    if background_image:
        faded_image = background_image.copy()
        fade_alpha = min(150, fade_alpha + FADE_SPEED)
        faded_image.set_alpha(fade_alpha)
        screen.blit(faded_image, (background_x, background_y))

    if games:
        game = games[current_game_index]
        branding_data = game.get("branding_data", {})
        render_wrapped_text(
            screen,
            f"{game['metadata'].get('name', 'Unknown Game')}",
            (50, 50),
            title_font,
        )
        render_wrapped_text(
            screen,
            f"Game Type: {game.get('type', 'Unknown')}",
            (50, 120),
            metadata_font,
        )
        render_wrapped_text(screen, f"Model: {game.get('model', 'Unknown')}", (50, 170), metadata_font)
        render_wrapped_text(
            screen,
            f"{branding_data.get('short_description', 'No description available')}",
            (50, 230),
            metadata_font,
        )
        # render_wrapped_text(screen, f"{branding_data.get('detailed_description', 'No description available')}", (50,
        #                                                                                                         300),
        #                     detailed_description_font)

        # render_wrapped_text(screen, f"Tags: {', '.join(branding_data.get('tags', []))}", (50, 260), tags_font)
        render_wrapped_text(
            screen,
            f"{current_game_index + 1} of {total_games}",
            (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50),
            metadata_font,
            TRANSLUCENT,
        )

    # if cover_image:
    #     screen.blit(cover_image, COVER_POSITION)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                current_game_index = (current_game_index + 1) % len(games)
                update_ui()
            elif event.key == pygame.K_LEFT:
                current_game_index = (current_game_index - 1) % len(games)
                update_ui()

    pygame.display.flip()

pygame.quit()
