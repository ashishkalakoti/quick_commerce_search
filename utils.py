from rich.console import Console
from rich.table import Table

console = Console()


def print_products(products):

    table = Table(title="Top Search Results")

    table.add_column("Vendor", style="cyan")
    table.add_column("Product")
    table.add_column("Size")
    table.add_column("Price", justify="right")

    for product in products:
        table.add_row(
            product.vendor,
            product.company,
            product.size,
            f"₹{product.price:.2f}"
        )

    console.print(table)