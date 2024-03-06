import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager

CURR_DIR = Path(os.path.dirname(os.path.relpath(__file__)))
FONTS_DIR = CURR_DIR / "../../res/fonts"


def set_custom_font(
    font_path: Path = FONTS_DIR / "libertinus",
    font_name: str = "Libertinus Sans",
    font_size: int = 12,
    list_available: bool = False,
):
    """
    Sets a custom font for Matplotlib. Uses all fonts in the given directory.
    """
    # Get all fonts in the given directory
    fonts = font_manager.findSystemFonts(fontpaths=[font_path], fontext="otf")

    # Add all fonts to the font manager
    for font in fonts:
        font_manager.fontManager.addfont(font)

    # List all available font names
    if list_available:
        print("Available fonts:")
        for font in font_manager.fontManager.ttflist:
            print(font.name)

    # Set the custom font
    plt.rcParams["font.family"] = font_name
    plt.rcParams["font.size"] = font_size

    print(f"Font set to {font_name} with size {font_size}")
