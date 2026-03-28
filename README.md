# Momir-Vig-Printer
This contains the code and instructions on how to use a thermal printer and an old laptop to create a Momir Vig Printer in paper MTG.


1. Install Ubuntu Server (or whichever linux OS you prefer)

2. Install momir_printer.py to the home dir
   
5. Update the server
   Sudo apt update && apt upgrade
   
6. Install dependencies
sudo apt install python3-pip python3-pil
sudo apt install libusb-1.0-0
pip3 install --break-system-packages requests python-escpos
pip3 install --break-system-packages requests python-escpos pillow
pip3 install --break-system-packages pyusb

8. Create USB permissions fix
   sudo nano /etc/udev/rules.d/99-escpos.rules
   SUBSYSTEM=="usb", ATTR{idVendor}=="04b8", ATTR{idProduct}=="0202", MODE="0666"

9. Auto-start the script
   nano /home/momir/.bashrc
# Auto-run Momir Vig printer script on console
if [ -z "$TMUX" ] && [ -z "$SCREEN" ]; then
   clear
   echo "Starting Momir Vig printer..."
   /usr/bin/python3 /home/momir/momir_printer.py
fi

make font larger
  sudo nano /etc/default/console-setup
  FONTFACE="TerminusBold"
  FONTSIZE="32x16"
10. Reboot
  sudo reboot
