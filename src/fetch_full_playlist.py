#!/usr/bin/env python3

"""
Fetch ALL track links from a public Spotify playlist, without API credentials.

The embed/public pages only expose the first 100 tracks. This script opens the
playlist in a headless browser, scrolls through the virtualized track list and
collects every track link, then writes them to links.txt so that
hitster_card_creator.py can pick them up (Scraper Mode).

Requires Playwright (not in requirements.txt to keep the Streamlit app light):
    pip install playwright
    python -m playwright install chromium

Usage:
    python src/fetch_full_playlist.py https://open.spotify.com/playlist/...
    python src/hitster_card_creator.py --fetch
"""

import os
import sys
import argparse

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
LINKS_FILE = os.path.join(PROJECT_ROOT, "links.txt")

# Collects {rowIndex: trackUrl} for rows of the playlist itself
# (excludes the "Recommended" section Spotify shows below it).
COLLECT_JS = """
(acc) => {
    const list = document.querySelector('[data-testid="playlist-tracklist"]');
    if (!list) return {acc, expected: null, done: false};
    list.querySelectorAll('[data-testid="tracklist-row"]').forEach(row => {
        const a = row.querySelector('a[href*="/track/"]');
        const idx = row.closest('[aria-rowindex]')?.getAttribute('aria-rowindex');
        if (a && idx) acc[idx] = 'https://open.spotify.com/track/' + a.href.split('/track/')[1].split('?')[0];
    });
    const expected = parseInt(list.getAttribute('aria-rowcount') || '0', 10) - 1;  // minus header row
    return {acc, expected};
}
"""

SCROLL_JS = """
() => {
    let el = document.querySelector('[data-testid="tracklist-row"]');
    while (el && !(el.scrollHeight > el.clientHeight + 50 &&
                   /(auto|scroll)/.test(getComputedStyle(el).overflowY))) el = el.parentElement;
    if (!el) { window.scrollBy(0, 600); return false; }
    el.scrollTop += 600;
    return el.scrollTop + el.clientHeight >= el.scrollHeight - 5;
}
"""


def fetch_all_track_links(playlist_url, headless=True, max_steps=2000):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright is not installed. Run:\n"
                 "  pip install playwright\n"
                 "  python -m playwright install chromium")

    playlist_url = playlist_url.split('?')[0]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page(viewport={"width": 1280, "height": 1000}, locale="en-US")
        page.goto(playlist_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector('[data-testid="playlist-tracklist"] [data-testid="tracklist-row"]', timeout=60000)

        acc, expected, stall = {}, None, 0
        for _ in range(max_steps):
            before = len(acc)
            result = page.evaluate(COLLECT_JS, acc)
            acc, expected = result["acc"], result["expected"]
            if expected and len(acc) >= expected:
                break
            at_bottom = page.evaluate(SCROLL_JS)
            page.wait_for_timeout(400)
            stall = stall + 1 if len(acc) == before else 0
            if at_bottom and stall >= 10:
                break
            if len(acc) != before:
                print(f"  collected {len(acc)}/{expected or '?'}", end="\r")
        browser.close()

    links = [acc[k] for k in sorted(acc, key=int)]
    # Deduplicate while keeping playlist order
    links = list(dict.fromkeys(links))
    print()
    return links, expected


def main():
    parser = argparse.ArgumentParser(description="Fetch every track link from a public Spotify playlist")
    parser.add_argument("playlist_url")
    parser.add_argument("-o", "--output", default=LINKS_FILE, help="Output file (default: links.txt in project root)")
    parser.add_argument("--show-browser", action="store_true", help="Run the browser visibly (debugging)")
    args = parser.parse_args()

    print(f"Opening {args.playlist_url} ...")
    links, expected = fetch_all_track_links(args.playlist_url, headless=not args.show_browser)
    if not links:
        sys.exit("No tracks found. Is the playlist public?")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(links) + "\n")

    print(f"✓ Saved {len(links)} track links to {args.output}")
    if expected and len(links) < expected:
        print(f"⚠ Playlist reports {expected} tracks; {expected - len(links)} could not be collected "
              f"(unavailable in your region, local files or duplicates).")
    print("Next: python src/hitster_card_creator.py --fetch")


if __name__ == "__main__":
    main()
