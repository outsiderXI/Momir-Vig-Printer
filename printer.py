import time
from pathlib import Path

from escpos.printer import Usb
from rich.console import Console
from rich.panel import Panel

from config import IMAGE_DIR, PRINTER_PRODUCT_ID, PRINTER_VENDOR_ID

console = Console()


def _open_printer():
    return Usb(PRINTER_VENDOR_ID, PRINTER_PRODUCT_ID)


def _resolve_image_path(card_id_or_path):
    path = Path(card_id_or_path)
    if path.exists():
        return path

    fallback = IMAGE_DIR / f"{card_id_or_path}.jpg"
    if fallback.exists():
        return fallback

    return None


def print_image(card_id_or_path, retries=3, retry_delay=1.0):
    path = _resolve_image_path(card_id_or_path)

    if not path:
        console.print(f"[bold red]Image not found:[/bold red] {card_id_or_path}")
        return False

    last_error = None

    for attempt in range(1, retries + 1):
        try:
            if attempt > 1:
                console.print(
                    Panel(
                        f"[yellow]Printer recovery attempt {attempt}/{retries}...[/yellow]",
                        title="Printer Recovery",
                        border_style="yellow",
                    )
                )

            printer = _open_printer()
            printer.image(str(path))
            printer.close()

            if attempt > 1:
                console.print("[bold green]Printer recovered successfully.[/bold green]")

            return True

        except Exception as e:
            last_error = e
            console.print(
                Panel(
                    f"[red]Printer error:[/red] {e}",
                    title=f"Print Attempt {attempt}/{retries}",
                    border_style="red",
                )
            )

            if attempt < retries:
                console.print("[yellow]Retrying printer connection...[/yellow]")
                time.sleep(retry_delay)

    console.print(
        Panel(
            f"[bold red]Printing failed after {retries} attempts.[/bold red]\n{last_error}",
            title="Printer Offline",
            border_style="bold red",
        )
    )
    return False
