import os, sys, json

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


# ✅ Define ASSETS_DIR for both Pygbag and PyInstaller compatibility
def get_assets_dir():
    """Returns the correct path for assets, whether running as a script or PyInstaller package."""
    if getattr(
        sys, "frozen", False
    ):  # PyInstaller sets `sys.frozen` when running from .exe
        return os.path.join(sys._MEIPASS, "assets")
    else:
        return os.path.join(os.path.dirname(__file__), "assets")


ASSETS_DIR = get_assets_dir()  # ✅ Use dynamic asset directory

# ✅ Now ASSETS_DIR works in both local and PyInstaller environments


def _load_browser_title(default="Oblique Games"):
    """Try to read 'browser_title' from assets/config.json, else return default."""
    cfg_path = os.path.join(ASSETS_DIR, "config.json")
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("browser_title", default)
    except (IOError, ValueError, KeyError):
        return default


# instead of a constant, load it at import time
BROWSER_TITLE = _load_browser_title()
