"""
TradingView XAGUSD price scraper
Uses TradingView's internal scanner API — no JS rendering needed.

Requirements:
    pip install requests beautifulsoup4
"""

import sys
import requests

SCANNER_URL = "https://scanner.tradingview.com/forex/scan"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.tradingview.com",
    "Referer": "https://www.tradingview.com/",
}

PAYLOAD = {
    "symbols": {
        "tickers": ["OANDA:XAGUSD"],
        "query": {"types": []},
    },
    "columns": ["close", "open", "high", "low", "change_abs", "change"],
}


def fetch_xagusd_price() -> dict:
    """
    Fetch XAGUSD quote data from TradingView's scanner API.

    Returns a dict with keys: price, open, high, low, change, change_pct
    Raises requests.HTTPError on a bad HTTP status.
    """
    resp = requests.post(SCANNER_URL, json=PAYLOAD, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    data = resp.json()

    try:
        row = data["data"][0]["d"]  # [close, open, high, low, change_abs, change_pct]
    except (KeyError, IndexError) as exc:
        raise ValueError(f"Unexpected response structure: {data}") from exc

    close, open_, high, low, change_abs, change_pct = row

    return {
        "symbol": "XAGUSD",
        "price": close,
        "open": open_,
        "high": high,
        "low": low,
        "change": change_abs,
        "change_pct": change_pct,
    }


def main():
    print("Fetching XAGUSD price from TradingView …")
    try:
        q = fetch_xagusd_price()
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        sys.exit(1)

    sign = "+" if q["change"] >= 0 else ""
    print(f"\n  Symbol : {q['symbol']}")
    print(f"  Price  : ${q['price']:.4f}")
    print(f"  Open   : ${q['open']:.4f}")
    print(f"  High   : ${q['high']:.4f}")
    print(f"  Low    : ${q['low']:.4f}")
    print(f"  Change : {sign}{q['change']:.4f}  ({sign}{q['change_pct']:.2f}%)")


if __name__ == "__main__":
    main()
