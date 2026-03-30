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

TOKEN_FILE = DATA_DIR / "tokens.json"

SESSION = requests.Session()

def initialize_database():

    """
    Ensures database and card data exist.
    Runs automatically at program startup.
    """

    import os

    if not BULK_JSON.exists():
        print("Downloading Scryfall database...")
        download_bulk_database()

    if not DB_FILE.exists():
        print("Building SQLite index...")
        build_sqlite_index()

    if not IMAGE_DIR.exists():
        IMAGE_DIR.mkdir(parents=True)

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

        if "image_uris" not in card:
            continue

        cid = card["id"]
        name = card["name"]

        insert_cards.append((
            cid,
            name,
            int(card.get("cmc",0)),
            card.get("type_line",""),
            card["image_uris"]["normal"]
        ))

        insert_fts.append((name,cid))

    cur.executemany("INSERT INTO cards VALUES (?,?,?,?,?)", insert_cards)
    cur.executemany("INSERT INTO cards_fts VALUES (?,?)", insert_fts)

    conn.commit()
    conn.close()

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

def download_all_images():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT id,image FROM cards")
    rows = cur.fetchall()

    conn.close()

    with ThreadPoolExecutor(max_workers=12) as pool:
        for cid,url in rows:
            pool.submit(download_card_image,cid,url)

def download_token_images():

    with TOKEN_FILE.open() as f:
        tokens = json.load(f)

    for token in tokens:

        path = IMAGE_DIR / f"{token['id']}.jpg"

        if path.exists():
            token["local_image"] = str(path)
            continue

        try:

            r = requests.get(token["image"], timeout=30)

            with open(path, "wb") as img:
                img.write(r.content)

            token["local_image"] = str(path)

        except:
            print("Failed:", token["name"])

    with TOKEN_FILE.open("w") as f:
        json.dump(tokens, f)
