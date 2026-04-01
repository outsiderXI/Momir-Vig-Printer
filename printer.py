from pathlib import Path
from escpos.printer import Usb
from config import IMAGE_DIR, PRINTER_PRODUCT_ID, PRINTER_VENDOR_ID


def print_image(card_id_or_path):
    path = Path(card_id_or_path)

    if not path.exists():
        path = IMAGE_DIR / f"{card_id_or_path}.jpg"

    if not path.exists():
        print(f"Image not found: {path}")
        return False

    p = Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID)
    p.image(str(path))
    return True
