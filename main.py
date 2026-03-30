from rich.console import Console
from rich.table import Table
from tokens import *
from printer import print_image
from downloader import *
from search import search_card
from printer import print_card
from input_utils import esc_input

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

def main():

    while True:

        option = show_menu()

        if option is None:
            break

        if option=="1":
            download_bulk_database()

        elif option=="2":
            build_sqlite_index()

        elif option=="3":
            download_all_images()

        elif option=="4":

            name = esc_input("Card name: ")

            if not name:
                continue

            cid = search_card(name)

            if not cid:
                console.print("Card not found")
                continue

            print_card(cid)

if __name__ == "__main__":
    main()
