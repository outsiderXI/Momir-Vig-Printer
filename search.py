import sqlite3
from rapidfuzz import process
from config import DB_FILE
import sqlite3
import random
from config import DB_FILE


def random_creature_by_cmc(cmc):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
    SELECT id,name
    FROM cards
    WHERE cmc=? AND type LIKE '%Creature%'
    """, (cmc,))

    rows = cur.fetchall()

    conn.close()

    if not rows:
        return None

    return random.choice(rows)[0]

def search_card(name):

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute(
        "SELECT id,name FROM cards_fts WHERE name MATCH ? LIMIT 5",
        (name+"*",)
    )

    rows = cur.fetchall()

    if rows:
        conn.close()
        return rows[0][0]

    cur.execute("SELECT name,id FROM cards")
    rows = cur.fetchall()

    names=[x[0] for x in rows]

    result=process.extractOne(name,names)

    if not result:
        conn.close()
        return None

    match=result[0]

    for n,cid in rows:
        if n==match:
            conn.close()
            return cid

    conn.close()
    return None
