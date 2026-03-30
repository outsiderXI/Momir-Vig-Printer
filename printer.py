from escpos.printer import Usb
from config import *

def print_card(card_id):

    path = IMAGE_DIR / f"{card_id}.jpg"

    p = Usb(PRINTER_VENDOR_ID,PRINTER_PRODUCT_ID)

    p.image(str(path))
    p.cut()
    p.close()
