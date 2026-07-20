import copy
import requests
from typing import List

from models import Product
from vendors.base import VendorClient


class BlinkitClient(VendorClient):

    def __init__(self, config_file):
        super().__init__(config_file)

    def search(self, query: str) -> List[Product]:

        config = copy.deepcopy(self.config)

        #
        # Replace the search term everywhere Blinkit expects it
        #
        config["params"]["actual_query"] = query
        config["params"]["q"] = query

        try:
            response = requests.request(
                method=config["method"],
                url=config["url"],
                headers=config["headers"],
                cookies=config.get("cookies", {}),
                params=config["params"],
                json=config.get("payload", {}),
                timeout=10,
            )

            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict) or "response" not in data:
                raise Exception("Invalid Blinkit response format")
        except Exception as e:
            raise e

        return self._parse(data)

    def _parse(self, data) -> List[Product]:

        products = []

        snippets = (
            data.get("response", {})
                .get("snippets", [])
        )

        for snippet in snippets:

            #
            # Ignore banners, dividers, headings, etc.
            #
            if snippet.get("widget_type") != "product_card_snippet_type_2":
                continue

            item = snippet.get("data", {})

            try:

                company = (
                    item.get("display_name", {})
                        .get("text")
                    or item.get("name", {})
                        .get("text")
                    or ""
                )

                size = (
                    item.get("variant", {})
                        .get("text", "")
                )

                #
                # Prices are already in rupees.
                #
                price_text = (
                    item.get("normal_price", {})
                        .get("text", "")
                )

                mrp_text = (
                    item.get("mrp", {})
                        .get("text", "")
                )

                price = float(
                    price_text.replace("₹", "")
                              .replace(",", "")
                )

                mrp = 0

                if mrp_text:
                    mrp = float(
                        mrp_text.replace("₹", "")
                                .replace(",", "")
                    )

                products.append(
                    Product(
                        vendor="Blinkit",
                        company=company,
                        size=size,
                        price=price,
                        mrp=mrp,
                    )
                )

            except Exception:
                continue

        return products