import difflib
import json
import time

from rich.console import Console
from rich.table import Table

from config import DATA_DIR
from input_utils import esc_input
from printer import print_image

TOKEN_FILE = DATA_DIR / "tokens.json"
console = Console()


def load_tokens():
    if not TOKEN_FILE.exists():
        console.print("[red]Token database missing.[/red]")
        return []

    with TOKEN_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


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


def filter_pt(tokens, pt):
    try:
        p, t = pt.split("/")
        return [c for c in tokens if c.get("power") == p and c.get("toughness") == t]
    except Exception:
        return tokens


def filter_color(tokens, text):
    color_map = {
        "white": "W",
        "blue": "U",
        "black": "B",
        "red": "R",
        "green": "G",
    }
    desired = {color_map.get(c) for c in text.split() if c in color_map}
    desired.discard(None)
    return [t for t in tokens if set(t.get("colors", [])) == desired]


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
        "ward",
    ]
    found = [k for k in keywords if k in text.lower()]
    if found:
        return ", ".join(found)

    return text.split("\n")[0][:60]


def choose_from_list(matches):
    table = Table(title="Multiple token matches", border_style="magenta")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold white")
    table.add_column("PT", style="yellow")
    table.add_column("Colors", style="green")
    table.add_column("Abilities", style="dim")

    limited = matches[:10]
    for i, m in enumerate(limited, start=1):
        pt = f"{m.get('power', '?')}/{m.get('toughness', '?')}"
        colors = "".join(m.get("colors", []))
        abilities = extract_keywords(m)
        table.add_row(str(i), m["name"], pt, colors, abilities)

    console.print()
    console.print(table)

    while True:
        choice = esc_input("Select number: ")
        if choice is None:
            return None

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(limited):
                return limited[idx]

        console.print("[red]Invalid selection.[/red]")


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
        console.print("[yellow]Invalid input, printing 1 copy.[/yellow]")
        count = 1

    for i in range(count):
        console.print(f"[green]Printing copy {i+1}/{count}[/green]")
        print_image(path)
        time.sleep(0.3)


def select_token_from_name(name):
    tokens = load_tokens()
    if not tokens:
        return None

    matches = smart_match(tokens, name)
    if not matches:
        return None

    if len(matches) == 1:
        return matches[0]

    pt_input = esc_input("Optional PT (e.g. 3/3): ")
    if pt_input is None:
        return None

    if pt_input:
        filtered = filter_pt(matches, pt_input)
        if filtered:
            matches = filtered

    if len(matches) > 1:
        color_input = esc_input("Optional color(s): ")
        if color_input is None:
            return None

        color_input = color_input.strip().lower()
        if color_input:
            filtered = filter_color(matches, color_input)
            if filtered:
                matches = filtered

    if len(matches) > 1:
        return choose_from_list(matches)

    return matches[0]


def token_mode_from_name(name):
    card = select_token_from_name(name)
    if not card:
        return False

    console.print(f"[bold magenta]Printing token:[/bold magenta] [bold white]{card['name']}[/bold white]")
    path = card.get("local_image")
    if path:
        print_multiple(path)
        return True

    console.print("[red]Image missing.[/red]")
    return False
