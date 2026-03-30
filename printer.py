from escpos.printer import Usb
from config import *

def print_image(path):

    p = Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID)

    p.image(str(path))
    p.cut()
    p.close()
