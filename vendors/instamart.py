import copy
import requests
from typing import List

from models import Product
from vendors.base import VendorClient


class InstamartClient(VendorClient):

    def __init__(self, config_file):
        super().__init__(config_file)

    def search(self, query: str) -> List[Product]:

        config = copy.deepcopy(self.config)

        #
        # Update search payload
        #
        config["payload"]["query"] = query

        try:
            response = requests.request(
                method=config["method"],
                url=config["url"],
                headers=config["headers"],
                cookies=config.get("cookies", {}),
                params=config["params"],
                json=config["payload"],
                timeout=10,
            )

            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict) or "data" not in data:
                raise Exception("Invalid Instamart response format")
        except Exception as e:
            raise e

        return self._parse(data)

    def _parse(self, data) -> List[Product]:

        products = []

        cards = data.get("data", {}).get("cards", [])

        for wrapper in cards:

            card = wrapper.get("card", {}).get("card", {})

            items_container = card.get("items")

            if not items_container:
                continue

            if isinstance(items_container, list):
                item_list = items_container
            elif isinstance(items_container, dict):
                item_list = items_container.get("items", [])
            else:
                continue

            for item in item_list:

                #
                # One product may have multiple variants.
                #
                for variant in item.get("variations", []):

                    try:

                        company = (
                            variant.get("displayName")
                            or item.get("displayName")
                            or ""
                        )

                        #
                        # quantityDescription examples:
                        # "500 g"
                        # "1 L"
                        #
                        size = variant.get("quantityDescription", "")

                        price_info = variant.get("price", {})

                        # Extract price units (they are in rupees, as units/nanos structure is used)
                        offer_price_obj = price_info.get("offerPrice") or price_info.get("price") or {}
                        if isinstance(offer_price_obj, dict):
                            selling_price = float(offer_price_obj.get("units", 0)) + float(offer_price_obj.get("nanos", 0)) / 1e9
                        else:
                            selling_price = float(offer_price_obj or 0)

                        mrp_obj = price_info.get("mrp") or offer_price_obj or {}
                        if isinstance(mrp_obj, dict):
                            mrp = float(mrp_obj.get("units", 0)) + float(mrp_obj.get("nanos", 0)) / 1e9
                        else:
                            mrp = float(mrp_obj or selling_price)

                        products.append(
                            Product(
                                vendor="Instamart",
                                company=company,
                                size=size,
                                price=selling_price,
                                mrp=mrp,
                            )
                        )

                    except Exception:
                        continue

        return products