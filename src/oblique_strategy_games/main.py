import asyncio
import pygame

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

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Oblique Strategy Games")

# Load custom pixel fonts
title_font = pygame.font.Font(f"assets/fonts/m6x11.ttf", 48)
description_font = pygame.font.Font(f"assets/fonts/m6x11.ttf", 28)
detailed_description_font = pygame.font.Font(f"assets/fonts/m6x11.ttf", 14)
metadata_font = pygame.font.Font(f"assets/fonts/m6x11.ttf", 24)
tags_font = pygame.font.Font(f"assets/fonts/m6x11.ttf", 20)

# Load the image
image_path = "assets/games/Bomberman/ChaosBomber/cover.png"
image = pygame.image.load(image_path)

# Set display mode to match image size
screen = pygame.display.set_mode(image.get_size())

clock = pygame.time.Clock()

current_game_index = 0
total_games = 0

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


async def main():
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw the image
        screen.blit(image, (0, 0))
        pygame.display.update()

        await asyncio.sleep(0)  # Required for asyncio compatibility
        clock.tick(60)

    # pygame.quit()


asyncio.run(main())
