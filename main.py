from rich.console import Console
from rich.table import Table
from tokens import *
from printer import print_image
from downloader import *
from search import search_card
from printer import print_image
from input_utils import esc_input
from downloader import initialize_database
from search import search_card
from tokens import load_tokens, smart_match
from search import random_creature_by_cmc
from tokens import token_mode
from splash import show_splash, show_quote, type_text
import time

console = Console()

import time
from rich.console import Console

console = Console()


def startup():

    console.clear()

    show_splash()

    console.print()

    type_text("Booting Momir Vig Printer...", 0.04)

    time.sleep(0.5)

    show_quote()

    type_text("Checking creature database...", 0.03)

    from downloader import initialize_database
    initialize_database()

    time.sleep(0.5)

    show_quote()

    type_text("Preparing evolutionary matrices...", 0.03)

    time.sleep(1)

    show_quote()

    console.print()
    console.print("[bold green]System Ready[/bold green]")
    console.print()
def show_menu():

    table = Table(title="Momir Printer")

    table.add_column("Option")
    table.add_column("Mode")

    table.add_row("1", "Momir Vig Mode")
    table.add_row("2", "Token Mode")
    table.add_row("ESC", "Exit")

    console.print(table)

    return esc_input()


def momir_mode():

    console.print("Momir Vig Mode")

    while True:

        value = esc_input("Discard mana value (1-16): ")

        if value is None:
            return

        try:
            cmc = int(value)
        except:
            console.print("Enter a number")
            continue

        cid = random_creature_by_cmc(cmc)

        if not cid:
            console.print("No creature with that mana value")
            continue

        print_image(cid)

def token_mode():

    console.print("Token Mode")

    tokens = load_tokens()

    while True:

        name = esc_input("Token name: ")

        if name is None:
            return

        matches = smart_token_match(tokens, name)

        if not matches:
            console.print("Token not found")
            continue

        token = matches[0]

        print_image(token["local_image"])

def main():

    startup()

    while True:

        option = show_menu()

        if option is None:
            break

        if option == "1":
            momir_mode()

        elif option == "2":
            token_mode()

if __name__ == "__main__":
    main()
