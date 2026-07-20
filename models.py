from dataclasses import dataclass


@dataclass
class Product:

    vendor: str
    company: str
    size: str
    price: float

    mrp: float = 0
    score: float = 0

    def row(self):

        return [
            self.vendor,
            self.company,
            self.size,
            f"₹{self.price:.2f}"
        ]