import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console

from ranking import rank_products
from utils import print_products

from vendors.zepto import ZeptoClient
from vendors.blinkit import BlinkitClient
from vendors.instamart import InstamartClient
from vendors.bigbasket import BigBasketClient

console = Console()


def search_vendor(vendor, query):
    """
    Execute one vendor search.

    Returns:
        list[Product]
    """

    try:
        return vendor.search(query)

    except Exception as e:
        console.print(
            f"[red]{vendor.__class__.__name__} failed:[/red] {e}"
        )
        return []


def build_clients():
    return [
        ZeptoClient("config/zepto.json"),
        BlinkitClient("config/blinkit.json"),
        InstamartClient("config/instamart.json"),
        BigBasketClient("config/bigbasket.json"),
    ]


def search_all(query):

    clients = build_clients()

    products = []

    with ThreadPoolExecutor(max_workers=len(clients)) as executor:

        futures = [
            executor.submit(search_vendor, client, query)
            for client in clients
        ]

        for future in as_completed(futures):
            try:
                products.extend(future.result())
            except Exception as e:
                console.print(f"[red]{e}[/red]")

    return products


def main():

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Search grocery products across vendors"
    )

    parser.add_argument(
        "query",
        nargs="*",
        help="Search text"
    )

    parser.add_argument(
        "--min-size", "-s",
        type=float,
        default=None,
        help="Minimum product size in grams/ml (optional)"
    )

    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="Number of results to pick from each vendor (default: 10)"
    )

    parser.add_argument(
        "--max-price", "-p",
        type=float,
        default=5000.0,
        help="Maximum product price in rupees (default: 5000)"
    )

    args = parser.parse_args()

    if args.query:
        query = " ".join(args.query)
    else:
        query = input("Search Product: ").strip()

    if not query:
        console.print("[red]Search query cannot be empty.[/red]")
        sys.exit(1)

    console.print(
        f"\n[cyan]Searching:[/cyan] {query}\n"
    )

    products = search_all(query)

    if not products:
        console.print(
            "[yellow]No products found.[/yellow]"
        )
        return

    ranked = rank_products(products, query, min_size=args.min_size, limit_per_vendor=args.limit, max_price=args.max_price)

    print_products(ranked)


if __name__ == "__main__":
    main()