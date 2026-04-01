import random
import shutil
import sys
import time
from pathlib import Path

from PIL import Image
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

MOMIR_QUOTES = [
    "Consult the Simic Combine...",
    "Evolving the battlefield...",
    "Sequencing creature genomes...",
    "Mutating battlefield organisms...",
    "Stabilizing mana matrix...",
    "Summoning creature prototype...",
    "Calculating mana value distributions...",
    "Breeding new evolutionary forms...",
    "Initializing biomantic protocols...",
    "The experiment begins...",
]


def type_text(text, speed=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()


def show_quote():
    quote = random.choice(MOMIR_QUOTES)
    console.print(
        Align.center(
            Text(quote, style="italic bright_black")
        )
    )
    console.print()


def show_splash():
    console.clear()

    image_path = Path("assets/momir_vig.png")
    if not image_path.exists():
        console.print(
            Panel(
                Align.center(Text("MOMIR VIG PRINTER", style="bold bright_green")),
                border_style="green",
            )
        )
        return

    term_width = shutil.get_terminal_size().columns
    img = Image.open(image_path)
    scale = min((term_width - 10) / img.width, 1)
    new_w = max(20, int(img.width * scale))
    new_h = max(8, int(img.height * scale * 0.5))
    img = img.resize((new_w, new_h))
    img = img.convert("L")

    pixels = img.load()
    chars = " .:-=+*#%@"

    lines = []
    for y in range(img.height):
        row = ""
        for x in range(img.width):
            brightness = pixels[x, y]
            row += chars[min(len(chars) - 1, int(brightness / 256 * len(chars)))]
        lines.append(row)

    art = "\n".join(lines)

    console.print(
        Panel(
            Align.center(Text(art, style="green")),
            border_style="bright_green",
            padding=(0, 1),
        )
    )
