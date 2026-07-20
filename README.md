# Quick Commerce Search

A Python application to search and compare grocery products across multiple quick commerce vendors (Zepto, Blinkit, Swiggy Instamart, and BigBasket). It ranks the retrieved products by search match relevance and price, displaying the top results in a beautifully formatted table.

The application is robust against network request failures or expired API credentials. If a real network call fails (e.g. due to Cloudflare blocks or expired tokens), it automatically falls back to parsing cached mock responses under the `vendors/` directory.

---

## Setup Instructions

### 1. Prerequisites
Make sure you have Python 3.7+ installed.

### 2. Install Dependencies
Install the required packages using `pip`:
```bash
pip install -r requirements.txt
```

---

## How to Run

You can run the program either by passing the search query as a command-line argument or by entering it interactively.

### 1. Direct Command-Line Search
Pass the product query directly when executing the script:
```bash
python main.py milk
```

### 2. Interactive Search
Run the script without arguments, and it will prompt you for a search term:
```bash
python main.py
Search Product: plant protein
```

---

## Supported Input Parameters

The program supports the following optional command-line arguments to customize your search:

| Argument | Short Flag | Type | Default | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `query` | *None* | `str` | *None* | The product or brand name to search for (positional). | `python main.py protein` |
| `--min-size` | `-s` | `float` | `None` | Minimum size/weight of products to display (in grams or millilitres). If omitted, no size filter is applied. | `python main.py milk -s 500` (filters out items < 500 g/ml) |
| `--limit` | `-l` | `int` | `10` | The maximum number of top results to pick from **each** vendor. | `python main.py milk -l 3` (keeps up to 3 results per vendor) |
| `--max-price` | `-p` | `float` | `5000.0` | Maximum price of products to display (in rupees). | `python main.py protein -p 1200` (filters out items > ₹1200) |

### Combined Example
To search for milk, filtering out items smaller than `500 ml` and keeping only the top `3` results per vendor with a maximum price of `100` rupees:
```bash
python main.py milk -s 500 -l 3 -p 100
```

---

## Project Structure

- `main.py`: Main entry point. Handles arguments, spawns parallel vendor requests, and handles console UI formatting.
- `ranking.py`: Core relevance scoring, size parsing, filtering, and vendor grouping logic.
- `utils.py`: Table printing utility powered by `rich`.
- `models.py`: Normalised dataclass representation of a `Product`.
- `config/`: JSON configuration templates containing headers, URLs, endpoints, cookies, and search bodies for each vendor.
- `vendors/`: Sub-classes implementing parsing logic for each vendor (`zepto.py`, `blinkit.py`, `instamart.py`, `bigbasket.py`), along with cached JSON response files (`<vendor>_response.json`) used as local fallback data.
