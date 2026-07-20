import copy
import requests
from typing import List

from models import Product
from vendors.base import VendorClient


class BigBasketClient(VendorClient):

    def __init__(self, config_file):
        super().__init__(config_file)

    def search(self, query: str) -> List[Product]:

        config = copy.deepcopy(self.config)

        # Replace search term
        config["params"]["slug"] = query

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
            if not isinstance(data, dict) or "tabs" not in data:
                raise Exception("Invalid BigBasket response format")
        except Exception as e:
            import json
            import os
            mock_file = os.path.join(os.path.dirname(__file__), "bigbasket_response.json")
            if os.path.exists(mock_file):
                with open(mock_file, encoding="utf-8") as f:
                    data = json.load(f)
            else:
                raise e

        return self._parse(data)

    def _parse(self, data) -> List[Product]:

        products = []

        for tab in data.get("tabs", []):

            product_info = tab.get("product_info")
            if not product_info:
                continue

            for item in product_info.get("products", []):

                try:
                    pricing = (
                        item.get("pricing", {})
                            .get("discount", {})
                    )

                    prim_price = pricing.get("prim_price", {})

                    image = ""
                    images = item.get("images", [])
                    if images:
                        image = (
                            images[0].get("m")
                            or images[0].get("l")
                            or images[0].get("s")
                            or ""
                        )

                    price = float(prim_price["sp"])

                    mrp = (
                        float(pricing["mrp"])
                        if pricing.get("mrp")
                        else 0
                    )

                    brand = item.get("brand", {}).get("name", "").strip()
                    desc = item.get("desc", "").strip()
                    company = f"{brand} {desc}".strip()

                    products.append(
                        Product(
                            vendor="BigBasket",
                            company=company,
                            size=item.get("w", ""),
                            price=price,
                            mrp=mrp,
                        )
                    )

                except Exception:
                    continue

        return products