import os

BROWSER_TITLE = "Oblique Strategy Games"
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

# ✅ Define ASSETS_DIR for Pygbag compatibility
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
