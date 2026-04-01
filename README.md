# Momir Vig Printer (v2)

A **fully offline-capable Magic: The Gathering thermal printer app** for **Linux servers and Raspberry Pi**.

This project supports **three unified print modes from a single prompt**:

* **Momir Mode** → enter a number `1–16` to print a random creature with that mana value
* **Token Mode** → enter a token name like `treasure`, `zombie`, or `rat`
* **Any Card Mode** → enter any card name like `Lightning Bolt` or `Jace, the Mind Sculptor`

The application automatically decides which mode to use based on your input.

---

# Features

* ✅ Unified input system (no mode menu required)
* ✅ Fully offline after first sync
* ✅ SQLite searchable local database
* ✅ Random Momir creature printing by mana value
* ✅ Token disambiguation (PT, color, choose list)
* ✅ Print any card by exact or fuzzy name
* ✅ Automatic image caching
* ✅ Token image caching
* ✅ Rich progress bars for downloads
* ✅ Automatic startup on Raspberry Pi / Linux boot
* ✅ Works great with USB thermal printers

---

# Hardware Requirements

Recommended:

* Raspberry Pi 4 / Pi Zero 2 W
* Debian / Raspberry Pi OS
* USB thermal printer (ESC/POS compatible)
* Stable SD card (16GB+ recommended)

---

# Software Requirements

Install system packages:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-tqdm python3-rich git
```

Install Python dependencies:

```bash
pip3 install escpos pillow requests rapidfuzz
```

If your distro blocks pip globally:

```bash
python3 -m venv venv
source venv/bin/activate
pip install escpos pillow requests rapidfuzz
```

---

# Installation

Clone the repo:

```bash
git clone https://github.com/outsiderXI/Momir-Vig-Printer.git
cd Momir-Vig-Printer
git checkout v2
```

Run the application:

```bash
python3 main.py
```

---

# First Startup (Important)

The **first run takes several minutes**.

During startup the app will:

1. Download the full Scryfall bulk dataset
2. Build a local SQLite database
3. Extract all tokens
4. Download all Momir creature images (CMC 0–16)
5. Download all token images

You will see progress bars for:

* dataset download
* creature image download
* token image download

After this finishes, the app becomes **fully offline capable**.

---

# How To Use

After boot, the prompt waits for input.

## 1) Momir Mode

Enter a mana value:

```text
> 7
```

This prints a **random 7-drop creature**.

Supported values:

```text
1–16
```

---

## 2) Token Mode

Enter a token name:

```text
> treasure
> zombie
> rat
```

If multiple versions exist, the app will ask for:

* optional power/toughness
* optional colors
* numbered selection list

Example:

```text
> zombie
Optional PT: 2/2
Optional colors: black
```

---

## 3) Any Card Mode

Enter any card name:

```text
> Lightning Bolt
> Sol Ring
> Atraxa, Praetors' Voice
```

The app will:

* exact match first
* then fuzzy search
* ask you to choose if multiple matches exist
* download image if missing
* cache for future offline use

---

# Offline Mode

After first startup, the app stores:

```text
data/
cache/
```

This includes:

* local SQLite card database
* token database
* cached creature images
* cached token images
* lazily cached non-creature card images

Once cached, all future prints work **without internet**.

---

# Automatic Launch On Boot (Recommended)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/momir-printer.service
```

Paste:

```ini
[Unit]
Description=Momir Vig Printer
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=momir
WorkingDirectory=/home/momir/Momir-Vig-Printer
ExecStart=/usr/bin/python3 /home/momir/Momir-Vig-Printer/main.py
Restart=always
RestartSec=3
StandardInput=tty
TTYPath=/dev/tty1

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable momir-printer.service
sudo systemctl start momir-printer.service
```

Check status:

```bash
sudo systemctl status momir-printer.service
```

---

# Raspberry Pi Kiosk / Arcade Mode

For a console-appliance feel:

```bash
sudo raspi-config
```

Go to:

```text
System Options → Boot / Auto Login → Console Autologin
```

This makes the Pi boot directly into the app.

---

# Project Structure

```text
Momir-Vig-Printer/
├── main.py
├── downloader.py
├── printer.py
├── search.py
├── tokens.py
├── config.py
├── data/
│   ├── cards.sqlite
│   ├── default_cards.json
│   └── tokens.json
└── cache/
    └── *.jpg
```

---

# Troubleshooting

## No printer found

Check USB device:

```bash
lsusb
```

Update `config.py` with correct:

* vendor ID
* product ID

---

## Download stalls

Check internet:

```bash
ping api.scryfall.com
```

---

## Missing tqdm or rich

Install Debian packages:

```bash
sudo apt install python3-tqdm python3-rich
```

---

## Permission denied on printer

Run with proper USB permissions or add user to `lp` group:

```bash
sudo usermod -aG lp momir
```

Then reboot.

---

# Recommended SD Card Size

Recommended minimum:

```text
16GB
```

Typical usage:

* DB + metadata: ~400MB
* creatures + tokens: ~1GB
* lazy printed cards: grows over time

