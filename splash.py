from rich.console import Console
from rich.progress import Progress
from PIL import Image
from pathlib import Path
import shutil
import random
import sys
import time
from rich.console import Console

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
    "The experiment begins..."
]


def type_text(text, speed=0.03):

    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)

    print()


def show_quote():

    quote = random.choice(MOMIR_QUOTES)

    console.print()

    type_text(quote)

    console.print()


def show_splash():

    console.clear()

    image_path = Path("assets/momir_vig.png")

    if not image_path.exists():
        console.print("[bold green]Momir Vig Printer[/bold green]")
        return

    # Resize image to fit terminal
    term_width = shutil.get_terminal_size().columns

    img = Image.open(image_path)

    scale = min(term_width / img.width, 1)
    new_w = int(img.width * scale)
    new_h = int(img.height * scale * 0.5)

    img = img.resize((new_w, new_h))
    img = img.convert("L")

    pixels = img.load()

    chars = " .:-=+*#%@"

    for y in range(img.height):
        row = ""
        for x in range(img.width):
            brightness = pixels[x, y]
            row += chars[int(brightness / 256 * len(chars))]
        console.print(row)


def loading_bar():

    with Progress() as progress:

        task = progress.add_task("Initializing Momir Printer...", total=100)

        yield progress, task
