#!/usr/bin/env python3

"""
Build the print-ready PDF from an existing songs.json (e.g. one whose years
were corrected by hand), without scraping anything again.

Usage:
    python src/build_pdf.py playlists/rockola/songs.json output/rockola.pdf
    python src/build_pdf.py playlists/rockola/songs.json output/rockola.pdf --ink-save-mode --card-draw-border
"""

import os
import json
import argparse
import utils
from hitster_card_creator import db  # sets utils.db (fonts, colours, card size)


def main():
    parser = argparse.ArgumentParser(description="Build Hitster PDF from a songs.json file")
    parser.add_argument("songs_json")
    parser.add_argument("output_pdf")
    parser.add_argument("--ink-save-mode", action="store_true", help="White background, black QR code")
    parser.add_argument("--card-draw-border", action="store_true", help="Draw cutting borders")
    parser.add_argument("--card-label", default=None, help="Small label printed on each card")
    args = parser.parse_args()

    with open(args.songs_json, encoding="utf-8") as f:
        songs = json.load(f)

    missing = [s for s in songs if not s.get("year")]
    if missing:
        print(f"⚠ {len(missing)} song(s) without year will show '????':")
        for s in missing:
            print(f"  - {s['artist']} — {s['name']}")

    settings = {
        "ink_saving_mode": args.ink_save_mode,
        "card_draw_border": args.card_draw_border,
        "card_background_color": "white" if args.ink_save_mode else "black",
        "card_border_color": "black" if args.ink_save_mode else "white",
        "card_label": args.card_label,
    }

    print(f"Building {len(songs)} cards...")
    pdf = utils.create_pdf_in_memory(songs, settings_override=settings)
    os.makedirs(os.path.dirname(os.path.abspath(args.output_pdf)), exist_ok=True)
    with open(args.output_pdf, "wb") as f:
        f.write(pdf.getvalue() if hasattr(pdf, "getvalue") else pdf)
    print(f"✓ PDF ready at: {args.output_pdf}")


if __name__ == "__main__":
    main()
