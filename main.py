from rich.console import Console
from rich.table import Table
from tokens import *
from printer import print_image
from downloader import *
from search import search_card
from printer import print_card
from input_utils import esc_input
from downloader import initialize_database
from search import search_card
from printer import print_card, print_image
from tokens import load_tokens, smart_token_match

console = Console()

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

        name = esc_input("Creature name: ")

        if name is None:
            return

        cid = search_card(name)

        if not cid:
            console.print("Card not found")
            continue

        print_card(cid)

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

    initialize_database()

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
