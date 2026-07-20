import re
from rapidfuzz import fuzz


def parse_size_in_grams(size_str: str) -> float:
    if not size_str:
        return 0.0

    size_str = size_str.lower().strip()

    # Match patterns like "6 x 35 g" or "6 x 35g"
    mult_match = re.search(r'(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*(g|gm|gram|kg|ml|l|litre)', size_str)
    if mult_match:
        qty = float(mult_match.group(1))
        val = float(mult_match.group(2))
        unit = mult_match.group(3)
        total = qty * val
        if unit in ('kg', 'l', 'litre'):
            return total * 1000.0
        return total

    # Match standard single quantity and unit: e.g. "500 g", "1 kg", "500ml", "1.5 l"
    match = re.search(r'(\d+(?:\.\d+)?)\s*(g|gm|gram|kg|ml|l|litre)', size_str)
    if match:
        val = float(match.group(1))
        unit = match.group(2)
        if unit in ('kg', 'l', 'litre'):
            return val * 1000.0
        return val

    # Handle cases like "1 pack (500 ml)" or "1 pack (1 L)"
    paren_match = re.search(r'\(\s*(\d+(?:\.\d+)?)\s*(g|gm|gram|kg|ml|l|litre)\s*\)', size_str)
    if paren_match:
        val = float(paren_match.group(1))
        unit = paren_match.group(2)
        if unit in ('kg', 'l', 'litre'):
            return val * 1000.0
        return val

    return 0.0


def rank_products(products, query, min_size=None, limit_per_vendor=10, max_price=5000.0):

    query = query.lower()

    # Filter out products smaller than min_size (if specified)
    if min_size is not None:
        filtered_by_size = []
        for product in products:
            if parse_size_in_grams(product.size) >= min_size:
                filtered_by_size.append(product)
        products = filtered_by_size

    # Filter out products more expensive than max_price
    if max_price is not None:
        products = [p for p in products if p.price <= max_price]

    for product in products:

        score = fuzz.token_sort_ratio(
            query,
            product.company.lower()
        )

        if query in product.company.lower():
            score += 30

        product.score = score

    # Group products by vendor
    by_vendor = {}
    for product in products:
        by_vendor.setdefault(product.vendor, []).append(product)

    # Take top results for each vendor based on limit_per_vendor
    filtered = []
    for vendor_products in by_vendor.values():
        vendor_products.sort(
            key=lambda x: (
                x.score,
                -x.price
            ),
            reverse=True
        )
        filtered.extend(vendor_products[:limit_per_vendor])

    # Sort the combined top results from all vendors
    filtered.sort(
        key=lambda x: (
            x.score,
            -x.price
        ),
        reverse=True
    )

    return filtered