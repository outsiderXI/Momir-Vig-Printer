import random
import sqlite3

from rapidfuzz import fuzz, process

from config import DB_FILE


def random_creature_by_cmc(cmc):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id
        FROM cards
        WHERE is_creature=1 AND cmc=?
        """,
        (cmc,),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    return random.choice(rows)[0]


def exact_card_id_by_name(name):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id
        FROM cards
        WHERE name = ?
          AND is_token = 0
        LIMIT 1
        """,
        (name,),
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def exact_card_row_by_name(name):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, name, type_line
        FROM cards
        WHERE name = ?
          AND is_token = 0
        LIMIT 1
        """,
        (name,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def search_card_candidates(name, limit=10):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # exact first
    cur.execute(
        """
        SELECT id, name, type_line
        FROM cards
        WHERE name = ?
          AND is_token = 0
        LIMIT ?
        """,
        (name, limit),
    )
    exact = cur.fetchall()
    if exact:
        conn.close()
        return exact

    # FTS prefix search
    prefix_query = " ".join(part + "*" for part in name.split() if part.strip())
    if prefix_query:
        cur.execute(
            """
            SELECT c.id, c.name, c.type_line
            FROM cards_fts f
            JOIN cards c ON c.id = f.id
            WHERE f.name MATCH ?
              AND c.is_token = 0
            LIMIT ?
            """,
            (prefix_query, limit),
        )
        fts_rows = cur.fetchall()
        if fts_rows:
            conn.close()
            return fts_rows

    # fuzzy fallback
    cur.execute(
        """
        SELECT name, id, type_line
        FROM cards
        WHERE is_token = 0
        """
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return []

    names = [r[0] for r in rows]
    matches = process.extract(name, names, scorer=fuzz.WRatio, limit=limit)

    out = []
    used = set()
    for matched_name, score, _ in matches:
        if score < 70:
            continue
        for row_name, row_id, type_line in rows:
            if row_name == matched_name and row_id not in used:
                out.append((row_id, row_name, type_line))
                used.add(row_id)
                break

    return out


def search_card(name):
    exact = exact_card_id_by_name(name)
    if exact:
        return exact

    candidates = search_card_candidates(name, limit=1)
    return candidates[0][0] if candidates else None
