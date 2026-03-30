import difflib
import time
import json
from pathlib import Path

from config import DATA_DIR
from input_utils import esc_input
from printer import print_image

TOKEN_FILE = DATA_DIR / "tokens.json"


# ---------------- LOAD TOKENS ----------------

def load_tokens():

    if not TOKEN_FILE.exists():
        print("Token database missing.")
        return []

    with TOKEN_FILE.open() as f:
        return json.load(f)


# ---------------- MATCHING ----------------

def smart_match(tokens, name):

    name = name.lower().strip()

    exact = [t for t in tokens if t["name"].lower() == name]
    if exact:
        return exact

    exact_token = [t for t in tokens if t["name"].lower() == f"{name} token"]
    if exact_token:
        return exact_token

    substring = [t for t in tokens if name in t["name"].lower()]
    if substring:
        return substring

    names = [t["name"] for t in tokens]

    close = difflib.get_close_matches(name, names, n=10, cutoff=0.7)

    return [t for t in tokens if t["name"] in close]


# ---------------- PT FILTER ----------------

def filter_pt(tokens, pt):

    try:
        p, t = pt.split("/")
        return [
            c for c in tokens
            if c.get("power") == p and c.get("toughness") == t
        ]

    except:
        return tokens


# ---------------- COLOR FILTER ----------------

def filter_color(tokens, text):

    color_map = {
        "white": "W",
        "blue": "U",
        "black": "B",
        "red": "R",
        "green": "G"
    }

    desired = set(
        color_map.get(c)
        for c in text.split()
        if c in color_map
    )

    return [
        t for t in tokens
        if set(t.get("colors", [])) == desired
    ]


# ---------------- KEYWORD EXTRACTION ----------------

def extract_keywords(card):

    text = card.get("oracle_text", "")

    if not text:
        return "No abilities"

    keywords = [
        "flying",
        "trample",
        "vigilance",
        "haste",
        "deathtouch",
        "lifelink",
        "first strike",
        "double strike",
        "menace",
        "reach",
        "hexproof",
        "indestructible",
        "ward"
    ]

    found = [
        k for k in keywords
        if k in text.lower()
    ]

    if found:
        return ", ".join(found)

    return text.split("\n")[0][:60]


# ---------------- USER SELECTION ----------------

def choose_from_list(matches):

    print("\nMultiple matches found:")

    for i, m in enumerate(matches[:10]):

        pt = f"{m.get('power','?')}/{m.get('toughness','?')}"
        colors = "".join(m.get("colors", []))
        abilities = extract_keywords(m)

        print(f"{i+1}: {m['name']} ({pt}) [{colors}]")
        print(f"    → {abilities}")

    while True:

        choice = esc_input("Select number: ")

        if choice is None:
            return None

        if choice.isdigit():

            idx = int(choice) - 1

            if 0 <= idx < len(matches[:10]):
                return matches[idx]

        print("Invalid selection.")


# ---------------- PRINT MULTIPLE ----------------

def print_multiple(path):

    count_input = esc_input("How many copies? (default 1): ")

    if count_input is None:
        return

    count_input = count_input.strip()

    if count_input == "":
        count = 1

    elif count_input.isdigit() and int(count_input) > 0:
        count = int(count_input)

    else:
        print("Invalid input, printing 1 copy.")
        count = 1

    for i in range(count):

        print(f"Printing copy {i+1}/{count}")

        print_image(path)

        time.sleep(0.3)


# ---------------- TOKEN MODE ----------------

def token_mode():

    tokens = load_tokens()

    if not tokens:
        return

    while True:

        name = esc_input("\nToken name (ESC to return): ")

        if name is None:
            return

        matches = smart_match(tokens, name)

        if not matches:
            print("No matches found.")
            continue

        if len(matches) == 1:

            card = matches[0]

        else:

            pt_input = esc_input("Optional PT (e.g. 3/3): ")

            if pt_input is None:
                return

            if pt_input:

                filtered = filter_pt(matches, pt_input)

                if filtered:
                    matches = filtered

            if len(matches) > 1:

                color_input = esc_input("Optional color(s): ")

                if color_input is None:
                    return

                color_input = color_input.strip().lower()

                if color_input:

                    filtered = filter_color(matches, color_input)

                    if filtered:
                        matches = filtered

            if len(matches) > 1:

                card = choose_from_list(matches)

                if card is None:
                    return

            else:

                card = matches[0]

        print("Printing:", card["name"])

        path = card["local_image"]

        if path:
            print_multiple(path)
        else:
            print("Image missing.")
