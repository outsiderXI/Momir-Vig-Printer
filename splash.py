from rich.console import Console
from rich.progress import Progress
from PIL import Image
from pathlib import Path
import shutil

console = Console()


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
