import json
import requests


class VendorClient:

    def __init__(self, config_file):

        with open(config_file, encoding="utf8") as f:
            self.config = json.load(f)

        # Normalize config keys to prevent KeyErrors in subclasses
        if "url" not in self.config and "base_url" in self.config and "search_endpoint" in self.config:
            self.config["url"] = f"{self.config['base_url']}{self.config['search_endpoint']}"

        if "method" not in self.config:
            if "zepto" in config_file.lower() or "instamart" in config_file.lower():
                self.config["method"] = "POST"
            else:
                self.config["method"] = "GET"

        if "params" not in self.config:
            self.config["params"] = self.config.get("query_params", {})

        if "payload" not in self.config:
            self.config["payload"] = self.config.get("body_template", self.config.get("body", {}))

    def request(self):

        return requests.request(
            method=self.config["method"],
            url=self.config["url"],
            headers=self.config.get("headers", {}),
            cookies=self.config.get("cookies", {}),
            params=self.config.get("params", {}),
            json=self.config.get("payload", {}),
            timeout=30,
        )

    def search(self, query):
        raise NotImplementedError