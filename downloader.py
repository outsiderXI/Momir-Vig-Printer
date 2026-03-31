import json
import time
import logging
import sqlite3
import requests
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from PIL import Image
import requests
from pathlib import Path
from config import IMAGE_DIR
from config import *
from config import BULK_JSON, DATA_DIR
from requests.adapters import HTTPAdapter
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from concurrent.futures import as_completed

TOKEN_FILE = DATA_DIR / "tokens.json"
VERSION_FILE = DATA_DIR / "scryfall_version.txt"

adapter = HTTPAdapter(
    pool_connections=50,
    pool_maxsize=50
)

session.mount("https://", adapter)

def has_internet():

    try:
        session.get("https://api.scryfall.com", timeout=5)
        return True
    except:
        return False

def initialize_database():

    if not has_internet():
        print("Offline mode: using local database.")
        return

    print("Checking for card database updates...")

    if not BULK_JSON.exists() or bulk_dataset_updated():

        print("Updating Scryfall database...")
        download_bulk_database()

        print("Rebuilding creature index...")
        build_sqlite_index()

        print("Updating token database...")
        build_token_database()

    if not IMAGE_DIR.exists():
        IMAGE_DIR.mkdir(parents=True)

    print("Checking for missing creature images...")
    download_all_images()

    print("Checking for missing token images...")
    download_token_images()

    # optional: check if images exist
    if len(list(IMAGE_DIR.glob("*.jpg"))) < 1000:
        print("Downloading card images (first run)...")
        download_all_images()

    if not TOKEN_FILE.exists():
        build_token_database()
        download_token_images()

def build_token_database():

    print("Extracting tokens from Scryfall dataset...")

    with BULK_JSON.open() as f:
        cards = json.load(f)

    tokens = []

    for card in cards:

        if card.get("layout") != "token":
            continue

        if "image_uris" not in card:
            continue

        token = {
            "id": card["id"],
            "name": card["name"],
            "power": card.get("power"),
            "toughness": card.get("toughness"),
            "colors": card.get("colors", []),
            "oracle_text": card.get("oracle_text", ""),
            "image": card["image_uris"]["normal"],
            "local_image": None
        }

        tokens.append(token)

    with TOKEN_FILE.open("w") as f:
        json.dump(tokens, f)

    print(f"{len(tokens)} tokens extracted.")
    
def download_bulk_database():

    meta = SESSION.get(SCRYFALL_BULK_URL).json()
    default_cards = next(x for x in meta["data"] if x["type"] == "default_cards")

    r = SESSION.get(default_cards["download_uri"], stream=True)

    with BULK_JSON.open("wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

def build_sqlite_index():

    with BULK_JSON.open() as f:
        cards = json.load(f)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS cards")
    cur.execute("DROP TABLE IF EXISTS cards_fts")

    cur.execute("""
    CREATE TABLE cards (
        id TEXT PRIMARY KEY,
        name TEXT,
        cmc INTEGER,
        type TEXT,
        image TEXT
    )
    """)

    cur.execute("""
    CREATE VIRTUAL TABLE cards_fts USING fts5(name,id UNINDEXED)
    """)

    insert_cards = []
    insert_fts = []

    for card in cards:
    
        # Skip non-creatures
        type_line = card.get("type_line", "")
        if "Creature" not in type_line:
            continue
    
        # Skip cards without images
        if "image_uris" not in card:
            continue
    
        cid = card["id"]
        name = card["name"]
    
        insert_cards.append((
            cid,
            name,
            int(card.get("cmc", 0)),
            type_line,
            card["image_uris"]["small"]
        ))
    
        insert_fts.append((name, cid))

    cur.executemany("INSERT INTO cards VALUES (?,?,?,?,?)", insert_cards)
    cur.executemany("INSERT INTO cards_fts VALUES (?,?)", insert_fts)

    conn.commit()
    conn.close()

def bulk_dataset_updated():

    meta = session.get(SCRYFALL_BULK_URL).json()
    default_cards = next(x for x in meta["data"] if x["type"] == "default_cards")

    new_date = default_cards["updated_at"]

    if VERSION_FILE.exists():
        old_date = VERSION_FILE.read_text().strip()
        if old_date == new_date:
            return False

    VERSION_FILE.write_text(new_date)
    return True

def download_card_image(card_id,url):

    path = IMAGE_DIR / f"{card_id}.jpg"
    if path.exists():
        return

    tmp = path.with_suffix(".tmp")

    r = SESSION.get(url,timeout=30)

    img = Image.open(BytesIO(r.content))

    scale = PRINTER_MAX_WIDTH/img.width

    w = int(img.width*scale*1.2)
    h = int(img.height*scale*1.2)

    img = img.resize((w,h),Image.LANCZOS)

    img = img.convert("L").convert("1",dither=Image.FLOYDSTEINBERG)

    img.save(tmp)
    tmp.rename(path)

from concurrent.futures import as_completed

def download_all_images():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT id,image FROM cards")
    rows = cur.fetchall()

    conn.close()

    total = len(rows)

    with Progress(
        TextColumn("[bold green]Downloading creature images"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeRemainingColumn(),
    ) as progress:

        task = progress.add_task("download", total=total)

        with ThreadPoolExecutor(max_workers=12) as pool:

            futures = [
                pool.submit(download_card_image, cid, url)
                for cid, url in rows
            ]

            for f in as_completed(futures):
                progress.advance(task)

def download_token_images():

    with TOKEN_FILE.open() as f:
        tokens = json.load(f)

    total = len(tokens)

    with Progress(
        TextColumn("[bold cyan]Downloading token images"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeRemainingColumn(),
    ) as progress:

        task = progress.add_task("download", total=total)

        for token in tokens:

            path = IMAGE_DIR / f"{token['id']}.jpg"

            if path.exists():
                token["local_image"] = str(path)
                progress.advance(task)
                continue

            try:

                r = session.get(token["image"], timeout=30)

                with open(path, "wb") as img:
                    img.write(r.content)

                token["local_image"] = str(path)

            except:
                print("Failed:", token["name"])

            progress.advance(task)

    with TOKEN_FILE.open("w") as f:
        json.dump(tokens, f)
