
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import os
import time

TIMEOUT = 60
dir_path = os.path.dirname(os.path.realpath(__file__))
print (dir_path)

db = sqlite3.connect(
        dir_path + "/../instance/flaskr.sqlite", detect_types=sqlite3.PARSE_DECLTYPES
    )
db.row_factory = sqlite3.Row

def build_driver(headless: bool = True) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--lang=en-US")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    service = Service(executable_path='/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver


def fetch_quote(driver: webdriver.Chrome, link) -> dict:
    driver.get(link)

    wait = WebDriverWait(driver, TIMEOUT, poll_frequency=0.5)

    # Wait until the price is present, then grab everything in one JS call.
    wait.until(lambda d: _find_price_element(d))

    return driver.execute_script("""
        // ── Price — use the stable js-symbol-last class ───────────────────
        var priceEl = document.querySelector('.last-fzcYMweq, .js-symbol-last');
        // The element contains a sub-span with just the decimal digits, so
        // grab the parent's full text and strip the sub-span if needed.
        var price = null;
        if (priceEl) {
            // Walk up until we get the full price string (e.g. "76.41900")
            var txt = priceEl.innerText.trim();
            // Remove any pure-digit sub-string that's just the decimal part
            price = txt.replace(/\\n.*/, '').trim();
        }

        // ── Change — stable class js-symbol-change-direction ─────────────
        // The container holds both values; grab each child span directly.
        var changeEl    = document.querySelector('.changeValue-yBgZPU7Y, .js-symbol-change-direction > span:first-child');
        var changePctEl = document.querySelector('.js-symbol-change-pt');

        var change    = changeEl    ? changeEl.innerText.trim()    : null;
        var changePct = changePctEl ? changePctEl.innerText.trim() : null;

        return { price: price, change: change, changePct: changePct };
    """)


def _find_price_element(driver):
    """Poll until the price element exists and contains a digit."""
    return driver.execute_script("""
        var el = document.querySelector('.last-fzcYMweq, .js-symbol-last');
        if (!el) return null;
        return /\d/.test(el.innerText) ? el : null;
    """)



def debug_dump(driver):
    """Print all visible leaf-ish text in the top 600px to help find selectors."""
    items = driver.execute_script("""
        var results = [];
        var all = document.querySelectorAll('div, span');
        for (var i = 0; i < all.length; i++) {
            var el = all[i];
            if (el.children.length > 2) continue;
            var txt = el.innerText ? el.innerText.trim() : '';
            if (!txt || txt.length > 40) continue;
            var rect = el.getBoundingClientRect();
            if (rect.top < 0 || rect.top > 600) continue;
            if (rect.width < 5 || rect.height < 5) continue;
            results.push({
                tag: el.tagName,
                cls: el.className,
                txt: txt,
                top: Math.round(rect.top)
            });
        }
        return results;
    """)
    print("\n--- DEBUG: visible leaf elements in top 600px ---")
    for item in items:
        print(f"  top={item['top']:3d}  {item['tag']:<5}  txt={item['txt']!r:<30}  cls={item['cls'][:60]}")
    print("--- END DEBUG ---\n")


def main():
    headless = "--no-headless" not in sys.argv
    debug = "--debug" in sys.argv
    while (True):
        links = db.execute("SELECT link FROM stock").fetchall()
        print(links)
        for link in links:
            driver = build_driver(headless=headless)
            link = link['link']
            try:
                print(f"Opening {link} (headless={headless}) ...")
                q = fetch_quote(driver, link)
                if debug:
                    debug_dump(driver)
            except TimeoutException:
                print(
                    "\nTimed out. Could not find a price element within "
                    f"{TIMEOUT}s.\nTry running with --no-headless to debug visually.",
                    file=sys.stderr,
                )
            finally:
                driver.quit()

            print(f"\n  {link}")
            print(f"  Price    : {q['price']     or '-'} Change   : {q['change']    or '-'} Change % : {q['changePct'] or '-'}")

            db.execute(
                "UPDATE stock SET latest_price = ?, percentage_change = ? WHERE link = ?",
                (q['price'], q['changePct'], link),
            )
            db.commit()
        time.sleep(2)

if __name__ == "__main__":
    main()