import json
import time
import logging
import sqlite3
import requests
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from PIL import Image

from config import *

SESSION = requests.Session()

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
