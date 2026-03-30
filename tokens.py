import json
from rapidfuzz import process
from pathlib import Path
from config import DATA_DIR

TOKEN_FILE = DATA_DIR / "tokens.json"


def load_tokens():
    if not TOKEN_FILE.exists():
        return []

    with TOKEN_FILE.open() as f:
        return json.load(f)


def smart_token_match(tokens, name):

    names = [t["name"] for t in tokens]

    result = process.extract(name, names, limit=5)

    matches = []

    for r in result:
        for t in tokens:
            if t["name"] == r[0]:
                matches.append(t)

    return matches
