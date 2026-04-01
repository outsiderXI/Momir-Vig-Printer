import time

from rich.console import Console

from downloader import ensure_card_image, initialize_database
from input_utils import esc_input
from printer import print_image
from search import random_creature_by_cmc, search_card_candidates
from splash import show_quote, show_splash, type_text
from tokens import token_mode_from_name

console = Console()


def startup():
    console.clear()
    show_splash()
    console.print()
    type_text("Booting Momir Vig Printer...", 0.04)
    time.sleep(0.5)
    show_quote()
    type_text("Checking local card database...", 0.03)
    initialize_database()
    time.sleep(0.5)
    show_quote()
    type_text("Ready for card input...", 0.03)
    time.sleep(0.5)
    console.print()
    console.print("[bold green]System Ready[/bold green]")
    console.print()


def show_prompt():
    console.print("[bold cyan]Enter a CMC 1-16, a token name, or a card name.[/bold cyan]")
    console.print("[dim]Press ESC to exit.[/dim]")
    return esc_input("> ")


def print_random_creature_by_cmc(cmc):
    card_id = random_creature_by_cmc(cmc)
    if not card_id:
        console.print(f"No creature found with mana value {cmc}.")
        return

    path = ensure_card_image(card_id)
    if not path:
        console.print("Creature image missing and could not be downloaded.")
        return

    console.print(f"Printing random creature with mana value {cmc}...")
    print_image(card_id)


def choose_card_candidate(candidates):
    if len(candidates) == 1:
        return candidates[0]

    console.print("\n[bold yellow]Multiple card matches found:[/bold yellow]")
    limited = candidates[:10]
    for i, (_, name, type_line) in enumerate(limited, start=1):
        console.print(f"{i}: {name} — {type_line}")

    while True:
        choice = esc_input("Select number (ESC to cancel): ")
        if choice is None:
            return None
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(limited):
                return limited[idx]
        console.print("Invalid selection.")


def print_named_card(name):
    candidates = search_card_candidates(name, limit=10)
    if not candidates:
        console.print("No matching non-token card found.")
        return False

    selected = choose_card_candidate(candidates)
    if not selected:
        return False

    card_id, card_name, _type_line = selected

    path = ensure_card_image(card_id)
    if not path:
        console.print("Card image missing and could not be downloaded.")
        return False

    console.print(f"Printing card: {card_name}")
    return print_image(card_id)


def handle_input(text):
    raw = text.strip()
    if not raw:
        return

    if raw.isdigit():
        cmc = int(raw)
        if 1 <= cmc <= 16:
            print_random_creature_by_cmc(cmc)
            return

    # token flow first for non-numeric input
    if token_mode_from_name(raw):
        return

    # then regular card flow
    if print_named_card(raw):
        return

    console.print("No token or card match found.")


def main():
    startup()
    while True:
        value = show_prompt()
        if value is None:
            break
        handle_input(value)


if __name__ == "__main__":
    main()
