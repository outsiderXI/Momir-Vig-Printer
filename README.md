# Momir Vig Printer v2

A polished **Raspberry Pi / Linux MTG thermal card printer** that supports:

* 🎲 **Momir mode** → type `1–16` to print a random creature by mana value
* 🐀 **Smart token mode** → type a token name like `rat`, `treasure`, `soldier`
* 🃏 **Print any exact card** → type `Sol Ring`, `Counterspell`, `Lightning Bolt`
* 💾 **Full offline cache mode** → downloads and stores **all card images locally**
* 🖨️ **Thermal printer optimized** with ESC/POS USB support
* 🧪 **Simic-style kiosk UI** with splash art, boot sequence, cache stats, and card preview panels

---

# Features

## Unified input mode

The app waits for one prompt:

```text
⚡ Input >
```

Then intelligently decides what to do.

### Examples

```text
8
```

Prints a random **8 mana creature**.

```text
rat
```

Enters token mode and resolves PT / color / unique token options.

```text
sol ring
```

Prints the preferred default printing automatically.

```text
jace
```

Shows a smart choice list.

---

# Hardware Requirements

* Raspberry Pi or Linux server
* USB ESC/POS thermal printer - Any Epson TM-T88 themeral printer recommended
* internet connection for first startup
* Aboout 60 GB of free storage for full image cache mode

---

# Installation

## 1) Clone the repo

```bash
git clone https://github.com/outsiderXI/Momir-Vig-Printer.git
cd Momir-Vig-Printer
```

## 2) Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3) Install requirements

```bash
pip install -r requirements.txt
```

# First Startup

Run:

```bash
python3 main.py
```

The first startup will:

1. Download the Scryfall bulk dataset
2. Build the SQLite searchable card database
3. Build the token database
4. Download and cache **all non-token card images**
5. Download token images

## Important

The first startup can take a long time.

The app now displays:

```text
FULL IMAGE CACHE MODE ENABLED
First startup may take a long time while all card images download.
```

After this completes, the printer works **fully offline**.

---

# Raspberry Pi Kiosk Mode

For the best appliance feel:

## Boot directly to console

```bash
sudo raspi-config
```

Choose:

```text
System Options → Boot / Auto Login → Console Autologin
```

## Larger retro Linux console font

```bash
sudo dpkg-reconfigure console-setup
```

Recommended:

```text
Font: TerminusBold
Size: 16x32
```

---

# Auto-start at boot

Create a systemd service:

```bash
sudo nano /etc/systemd/system/momir-printer.service
```

Use:

```ini
[Unit]
Description=Momir Vig Printer
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=momir
WorkingDirectory=/home/momir/Momir-Vig-Printer
ExecStart=/home/momir/Momir-Vig-Printer/venv/bin/python /home/momir/Momir-Vig-Printer/main.py
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

---

# Recommended Workflow

## Daily usage

```text
Boot Pi → splash screen → cache check → ready prompt
```

Then print by:

* mana value
* token name
* exact card name

## Fully offline after first run

Once the cache is complete, no internet is required.

---
