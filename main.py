#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Astrolabe Suite - Unified Command Line Interface
================================================
Modern CLI launcher for the classical planispheric astrolabe:
- Launch interactive HTML5 web simulation in browser
- Generate high-precision vector plates (PDF and SVG) for CNC / laser engraving
- Generate and synchronize screen-optimized assets for Web and Android
- Launch interactive visual label editor to tune star and constellation placements
- Synchronize web application assets to Android mobile app

Usage:
    python main.py                  # Launch interactive web app (default)
    python main.py --web            # Launch interactive web app with optional port
    python main.py --export         # Generate print & laser vector plates (exports/)
    python main.py --screen         # Generate and sync screen vector assets
    python main.py --edit-labels    # Launch visual label editor in browser
    python main.py --sync           # Sync web app files to Android assets
    python main.py --help           # Show all available options
"""

import sys
import os
import shutil
import argparse
import http.server
import socketserver
import threading
import webbrowser

# Add src to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from astrolabe.engine import Astrolabe


def sync_web_to_android():
    """Synchronizes web app files (HTML, CSS, JS modules, SVG assets) to Android assets."""
    web_dir = os.path.join(project_root, 'web')
    android_assets = os.path.join(project_root, 'android', 'app', 'src', 'main', 'assets')
    if not os.path.isdir(android_assets):
        print(f"[Warning] Android assets directory not found at: {android_assets}")
        return False

    # Sync top-level files
    files_to_sync = ['app.js', 'index.html', 'style.css']
    synced = []
    for f in files_to_sync:
        src_path = os.path.join(web_dir, f)
        dst_path = os.path.join(android_assets, f)
        if os.path.isfile(src_path):
            shutil.copyfile(src_path, dst_path)
            synced.append(f)

    # Sync js/ directory
    src_js = os.path.join(web_dir, 'js')
    dst_js = os.path.join(android_assets, 'js')
    if os.path.isdir(src_js):
        os.makedirs(dst_js, exist_ok=True)
        for f in os.listdir(src_js):
            if f.endswith('.js'):
                shutil.copyfile(os.path.join(src_js, f), os.path.join(dst_js, f))
                synced.append(f"js/{f}")

    # Sync assets/ directory (e.g. Kursi.svg and any new SVG layers)
    src_assets = os.path.join(web_dir, 'assets')
    dst_assets = os.path.join(android_assets, 'assets')
    if os.path.isdir(src_assets):
        os.makedirs(dst_assets, exist_ok=True)
        for f in os.listdir(src_assets):
            if f.endswith('.svg'):
                shutil.copyfile(os.path.join(src_assets, f), os.path.join(dst_assets, f))
                # also ensure Android assets root has SVG copies if loaded flat
                shutil.copyfile(os.path.join(src_assets, f), os.path.join(android_assets, f))

    print(f"Successfully synced web suite {synced} to Android assets: {android_assets}")
    return True



def start_web_server(port=8080, open_browser=True):
    """Launches local HTTP server serving the interactive web application."""
    web_dir = os.path.join(project_root, "web")
    if not os.path.isdir(web_dir):
        print(f"Error: web directory not found at {web_dir}")
        return

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=web_dir, **kwargs)

        def log_message(self, format, *args):
            pass  # Quiet mode

    # Try requested port or fallback to next available ports
    server = None
    active_port = port
    for p in range(port, port + 20):
        try:
            server = socketserver.TCPServer(("", p), QuietHandler)
            active_port = p
            break
        except OSError:
            continue

    if server is None:
        print(f"Error: Could not bind to any port in range {port}-{port+20}")
        return

    url = f"http://localhost:{active_port}/index.html"
    print("\n" + "=" * 60)
    print("  Classical Astrolabe - Interactive Web Application")
    print("=" * 60)
    print(f"  Local Server: {url}")
    print(f"  Directory:    {web_dir}")
    print("=" * 60)

    threading.Thread(target=server.serve_forever, daemon=True).start()
    if open_browser:
        print("Opening web browser...")
        webbrowser.open(url)

    print("\nServer running. Press Ctrl+C to exit.\n")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.shutdown()


def main():
    parser = argparse.ArgumentParser(
        description="Classical Astrolabe - Simulation & Vector Generation Suite",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--web', action='store_true',
        help="Launch the interactive HTML5 simulation in your web browser"
    )
    parser.add_argument(
        '--export', action='store_true',
        help="Generate and export high-resolution plates (Mater, Plate, Rete, Rule, Back, Alidade) to exports/"
    )
    parser.add_argument(
        '--screen', action='store_true',
        help="Generate and sync screen-optimized vector SVGs (large fonts, halos, breathable grids) to web/ and android/"
    )
    parser.add_argument(
        '--edit-labels', action='store_true',
        help="Launch the visual Drag-and-Drop Label Editor in your browser to tune star and constellation positions"
    )
    parser.add_argument(
        '--sync', action='store_true',
        help="Synchronize web application files (HTML, JS, CSS) to Android assets"
    )
    parser.add_argument(
        '--lat', type=float, default=35.78,
        help="Latitude in degrees"
    )
    parser.add_argument(
        '--city', type=str, default="Tangier",
        help="City or location name inscribed on the tympan plate"
    )
    parser.add_argument(
        '--lang', type=str, default='arabic', choices=['arabic', 'latin'],
        help="Inscriptions language"
    )
    parser.add_argument(
        '--num', type=str, default='abjad', choices=['abjad', 'eastern_arabic', 'latin'],
        help="Numeral system: 'abjad' (Hisab al-Jummal), 'eastern_arabic', or 'latin'"
    )
    parser.add_argument(
        '--printable', action='store_true',
        help="Generate 1:1 scale print-ready A4 PDF sheets (printable/) with packaged Rule & Alidade and isolated Rete transparency"
    )
    parser.add_argument(
        '--port', type=int, default=8080,
        help="Local HTTP server port (for --web)"
    )
    parser.add_argument(
        '--output-dir', type=str, default=None,
        help="Custom output directory for --export (defaults to exports/) or --printable (defaults to printable/)"
    )
    args = parser.parse_args()

    if args.sync:
        sync_web_to_android()
        return

    if args.edit_labels:
        from astrolabe.label_editor import start_label_editor
        port = args.port if args.port != 8080 else 8088
        start_label_editor(port=port, open_browser=True)
        return

    if args.printable:
        from astrolabe.printable import PrintableA4
        out_dir = args.output_dir if args.output_dir else os.path.join(project_root, "printable")
        generator = PrintableA4(
            latitude=args.lat,
            city=args.city,
            language=args.lang,
            numeral_system=args.num,
            output_dir=out_dir
        )
        generator.export_all()
        return

    if args.screen:
        print("\n========================================================")
        print("  Classical Astrolabe - Screen Vector Generator")
        print("========================================================")
        print(f"  - Latitude:       {args.lat}° ({args.city})")
        print(f"  - Language:       {args.lang}")
        print(f"  - Numeral System: {args.num}")
        print("========================================================")
        astrolabe = Astrolabe(
            latitude=args.lat,
            city=args.city,
            language=args.lang,
            numeral_system=args.num,
            screen_mode=True
        )
        astrolabe.export_screen_assets()
        print("\nScreen assets generated and synced to web/ and android/ successfully!")
        return

    if args.export:
        print("\n========================================================")
        print("  Classical Astrolabe - Vector Plate Generator")
        print("========================================================")
        print(f"  - Latitude:       {args.lat}° ({args.city})")
        print(f"  - Language:       {args.lang}")
        print(f"  - Numeral System: {args.num}")
        print("========================================================")
        astrolabe = Astrolabe(
            latitude=args.lat,
            city=args.city,
            language=args.lang,
            numeral_system=args.num,
            screen_mode=False
        )
        astrolabe.export_all(output_dir=args.output_dir)
        print("\nExport completed successfully!")
        return

    # Default action: Launch web application
    start_web_server(port=args.port, open_browser=True)


if __name__ == '__main__':
    main()
