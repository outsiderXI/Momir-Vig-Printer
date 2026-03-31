from pathlib import Path
from escpos.printer import Usb
from config import IMAGE_DIR

def print_image(card_id):

    path = IMAGE_DIR / f"{card_id}.jpg"

    if not path.exists():
        print(f"Image not found: {path}")
        return

    p = Usb(0x04b8,0x0202)
    p.image(str(path))
