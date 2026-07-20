import copy
import requests

from typing import List

from models import Product
from vendors.base import VendorClient


class ZeptoClient(VendorClient):

    def __init__(self, config_file):
        super().__init__(config_file)

    def search(self, query: str) -> List[Product]:

        config = copy.deepcopy(self.config)

        config["payload"]["query"] = query

        try:
            response = requests.request(
                method=config["method"],
                url=config["url"],
                headers=config["headers"],
                cookies=config.get("cookies", {}),
                params=config.get("params", {}),
                json=config["payload"],
                timeout=10,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Zepto request failed ({response.status_code})"
                )

            data = response.json()
            if not isinstance(data, dict) or "layout" not in data:
                raise Exception("Invalid Zepto response format")
        except Exception as e:
            raise e

        return self._parse(data)

    def _parse(self, data) -> List[Product]:

        products = []

        layout = data.get("layout", [])

        for widget in layout:

            resolver = (
                widget.get("data", {})
                      .get("resolver", {})
            )

            resolver_data = resolver.get("data", {})

            items = resolver_data.get("items", [])

            if not items:
                continue

            for item in items:

                #
                # New API structure: product data under "productResponse"
                #
                if "productResponse" in item:
                    products.extend(
                        self._parse_products([item["productResponse"]])
                    )
                    continue

                #
                # Old structure: product carousel widgets
                #
                if "data" in item and "product" in item["data"]:
                    products.extend(
                        self._parse_products([item["data"]])
                    )
                    continue

                #
                # Old structure: regular product grids
                #
                if "product" in item:
                    products.extend(
                        self._parse_products([item])
                    )
                    continue

                #
                # Old structure: nested items[]
                #
                nested = item.get("items", [])

                for child in nested:

                    if (
                        child.get("type") == "PRODUCT_ITEM"
                        and "data" in child
                    ):
                        products.extend(
                            self._parse_products(
                                [child["data"]]
                            )
                        )

        return products

    def _parse_products(self, items):
        """
        Convert Zepto product objects into normalized Product objects.
        """

        products = []

        for item in items:

            try:

                product = item.get("product", {})
                variant = item.get("productVariant", {})

                name = product.get("name", "").strip()
                brand = product.get("brand", "").strip()

                company = f"{brand} {name}".strip()

                size = (
                    variant.get("formattedPacksize")
                    or f'{variant.get("packsize", "")} {variant.get("unitOfMeasure", "")}'
                )

                selling_price = (
                    item.get("sellingPrice")
                    or item.get("discountedSellingPrice")
                    or 0
                )

                mrp = item.get("mrp", 0)

                # Zepto prices are returned in paise
                selling_price = float(selling_price) / 100
                mrp = float(mrp) / 100

                products.append(
                    Product(
                        vendor="Zepto",
                        company=company,
                        size=size,
                        price=selling_price,
                        mrp=mrp,
                    )
                )

            except Exception:
                continue

        return products