import json
import os
import random
import struct
import pygame
import pygame_gui
import moderngl
from pygame.locals import *

DIRNAME = os.path.dirname(__file__)

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
# VIRTUAL_RES = (160, 120)
VIRTUAL_RES = (SCREEN_WIDTH, SCREEN_HEIGHT)
FPS = 30
WHITE, BLACK, GREY, TRANSLUCENT_BLACK, TRANSLUCENT = (
    (255, 255, 255),
    (0, 0, 0),
    (200, 200, 200),
    (0, 0, 0, 100),
    (0, 0, 0, 0),
)
TEXT_BOX_PADDING = 10
TEXT_BOX_WIDTH = SCREEN_WIDTH - 100
TEXT_BOX_HEIGHT_OFFSET = SCREEN_HEIGHT / 3
# Initialize pygame and OpenGL
pygame.init()
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
ctx = moderngl.create_context()
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Oblique Strategy Games")

# Load Shader
prog = ctx.program(
    vertex_shader=open(f"{DIRNAME}/shaders/vertex.glsl").read(),
    fragment_shader=open(f"{DIRNAME}/shaders/fragment.glsl").read(),
)

# Fullscreen Quad for Shader
texture_coordinates = [0, 1, 1, 1, 0, 0, 1, 0]
world_coordinates = [-1, -1, 1, -1, -1, 1, 1, 1]
render_indices = [0, 1, 2, 1, 2, 3]

vbo = ctx.buffer(struct.pack("8f", *world_coordinates))
uvmap = ctx.buffer(struct.pack("8f", *texture_coordinates))
ibo = ctx.buffer(struct.pack("6I", *render_indices))

vao_content = [(vbo, "2f", "vert"), (uvmap, "2f", "in_text")]
vao = ctx.vertex_array(prog, vao_content, ibo)

# Load custom pixel fonts
BASE_FONT_SIZE = 48
TITLE_FONT_SIZE = BASE_FONT_SIZE
DESCRIPTION_FONT_SIZE = BASE_FONT_SIZE - 20
DETAILED_DESCRIPTION_FONT_SIZE = BASE_FONT_SIZE - 34
METADATA_FONT_SIZE = int(BASE_FONT_SIZE / 2)
TAGS_FONT_SIZE = BASE_FONT_SIZE - 28
title_font = pygame.font.Font(f"{DIRNAME}/fonts/m6x11.ttf", TITLE_FONT_SIZE)
description_font = pygame.font.Font(f"{DIRNAME}/fonts/m6x11.ttf", DESCRIPTION_FONT_SIZE)
detailed_description_font = pygame.font.Font(f"{DIRNAME}/fonts/m6x11.ttf", DETAILED_DESCRIPTION_FONT_SIZE)
metadata_font = pygame.font.Font(f"{DIRNAME}/fonts/m6x11.ttf", METADATA_FONT_SIZE)
tags_font = pygame.font.Font(f"{DIRNAME}/fonts/m6x11.ttf", TAGS_FONT_SIZE)


# Load Games
def load_games(root_dir=f"{DIRNAME}/games", shuffle=False):
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
screen = pygame.Surface(VIRTUAL_RES).convert((255, 65280, 16711680, 0))
screen_texture = ctx.texture(VIRTUAL_RES, 3, pygame.image.tostring(screen, "RGB", 1))
screen_texture.repeat_x = False
screen_texture.repeat_y = False


# Shader Rendering Function
def render_shader():
    texture_data = screen.get_view("1")
    screen_texture.write(texture_data)
    ctx.clear(14 / 255, 40 / 255, 66 / 255)
    screen_texture.use()
    vao.render()
    pygame.display.flip()


# Render Wrapped Text with Shadow
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
    shadow_offset = 5
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
        shadow_surface = font.render(line, True, BLACK)
        text_surface = font.render(line, True, WHITE)
        surface.blit(shadow_surface, (position[0] + shadow_offset, position[1] + y_offset + shadow_offset))
        surface.blit(text_surface, (position[0], position[1] + y_offset))
        y_offset += font.get_height() + 5


# Main Loop
running = True
while running:
    time_delta = clock.tick(FPS) / 1000.0
    screen.fill((0, 0, 0))

    if games:
        game = games[current_game_index]
        cover_path = game["cover"]
        if os.path.exists(cover_path):
            cover_image = pygame.image.load(cover_path).convert()
            cover_image = pygame.transform.scale(cover_image, VIRTUAL_RES)
            screen.blit(cover_image, (0, 0))

        # Render Text
        branding_data = game.get("branding_data", {})
        render_wrapped_text(
            screen,
            f"{game['metadata'].get('name', 'Unknown Game')}",
            (50, 50 + TEXT_BOX_HEIGHT_OFFSET),
            title_font,
        )
        render_wrapped_text(
            screen,
            f"Game Type: {game.get('type', 'Unknown')}",
            (50, 120 + TEXT_BOX_HEIGHT_OFFSET),
            metadata_font,
        )
        render_wrapped_text(screen, f"Model: {game.get('model', 'Unknown')}", (50, 170 + TEXT_BOX_HEIGHT_OFFSET), metadata_font)
        render_wrapped_text(
            screen,
            f"{branding_data.get('short_description', 'No description available')}",
            (50, 230 + TEXT_BOX_HEIGHT_OFFSET),
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
        )

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_RIGHT:
                current_game_index = (current_game_index + 1) % total_games
            elif event.key == K_LEFT:
                current_game_index = (current_game_index - 1) % total_games

    render_shader()

pygame.quit()
