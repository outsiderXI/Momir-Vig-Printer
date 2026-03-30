Here’s the **typical workflow on Ubuntu** to download your project from GitHub and run the Momir printer application.

I’ll assume the repository is something like:

```
https://github.com/USERNAME/momir-printer
```

---

# 1. Install Required System Packages

Open a terminal and run:

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv
```

If you're using a **USB ESC/POS printer**, also install:

```bash
sudo apt install -y libusb-1.0-0
```

---

# 2. Clone Your GitHub Repository

```bash
git clone https://github.com/USERNAME/momir-printer.git
```

Enter the project folder:

```bash
cd momir-printer
```

---

# 3. Create a Python Virtual Environment (recommended)

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Your terminal should now show:

```
(venv)
```

---

# 4. Install Python Dependencies

Install everything from `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs things like:

* requests
* pillow
* rapidfuzz
* rich
* python-escpos

---

# 5. Run the Application

Start the program:

```bash
python main.py
```

On first run it will automatically:

```
download Scryfall dataset
build creature database
extract tokens
download creature images
download token images
```

This may take **10–30 minutes depending on internet speed**.

After setup finishes you'll see:

```
Momir Printer

1 Momir Vig Mode
2 Token Mode
ESC Exit
```

---

# 6. Printer Permissions (Very Important)

Linux often blocks USB printer access.

Create a **udev rule**:

```bash
sudo nano /etc/udev/rules.d/99-escpos.rules
```

Add:

```bash
SUBSYSTEM=="usb", ATTR{idVendor}=="04b8", ATTR{idProduct}=="0202", MODE="0666"
```

Then reload rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Reconnect the printer.

---

# 7. Test Printing

Run again:

```bash
python main.py
```

Choose:

```
1 → Momir Vig Mode
```

Enter:

```
6
```

It should:

```
select random CMC 6 creature
load local image
print card
```

---

# Optional: Auto-Start on Boot (for dedicated device)

If this will run on a **Raspberry Pi or mini-PC inside the printer**, you can make it auto-start.

Create a systemd service:

```bash
sudo nano /etc/systemd/system/momir-printer.service
```

Example:

```ini
[Unit]
Description=Momir Printer
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/momir-printer
ExecStart=/home/ubuntu/momir-printer/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl enable momir-printer
```

Start it:

```bash
sudo systemctl start momir-printer
```

Now it runs automatically at boot.

---

# Final Workflow on a Fresh Ubuntu Device

```bash
sudo apt install git python3 python3-pip python3-venv
git clone https://github.com/USERNAME/momir-printer.git
cd momir-printer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

If you'd like, I can also show you **one extremely useful thing for this project**:

How to make the entire printer run as a **single executable with PyInstaller**, so the Ubuntu device doesn’t even need Python installed. This is great for **turning the project into a plug-and-play appliance**.
