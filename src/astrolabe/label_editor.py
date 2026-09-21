#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Astrolabe Visual Drag-and-Drop Label Editor Server
=================================================
Provides a local interactive web editor allowing the user to visually position
star labels and constellation titles on the Rete plate by clicking and dragging.
Saves positions permanently to `data/label_overrides.json` and automatically
re-exports vector SVGs and PDFs.
"""

import os
import sys
import json
import webbrowser
import threading
import subprocess
import importlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Ensure src is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src_dir = os.path.join(project_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import astrolabe.engine
from astrolabe.engine import StereographicProjection, Rete, Astrolabe


def run_regenerate_assets(screen_mode=True):
    """Run fresh subprocess to regenerate assets, completely immune to in-memory module caching."""
    flag = '--screen' if screen_mode else '--export'
    cmd = [sys.executable, os.path.join(project_root, 'main.py'), flag]
    subprocess.run(cmd, cwd=project_root, check=True)


def get_overrides_filepath():
    return os.path.join(project_root, 'data', 'label_overrides.json')


def load_overrides():
    path = get_overrides_filepath()
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[LabelEditor] Error reading overrides: {e}")
    return {"stars": {}, "constellations": {}}


def save_overrides_to_file(overrides_dict):
    path = get_overrides_filepath()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(overrides_dict, f, indent=2, ensure_ascii=False)


def collect_labels_data():
    """Extract all stars, constellations, and stereographic coordinates for visual editor."""
    importlib.reload(astrolabe.engine)
    proj = astrolabe.engine.StereographicProjection()
    rete_ar = astrolabe.engine.Rete(proj=proj, language='arabic')
    rete_lat = astrolabe.engine.Rete(proj=proj, language='latin')
    
    overrides = load_overrides()
    
    # Map latin stars and constellations for multilingual display
    lat_const_map = {c['id']: c for c in rete_lat.constellations}
    lat_star_map = {}
    for c in rete_lat.constellations:
        for s in c['stars']:
            lat_star_map[s[0]] = s
            
    constellations_data = []
    all_stars_data = []

    for c_ar in rete_ar.constellations:
        cid = c_ar['id']
        c_lat = lat_const_map.get(cid, {})
        cra, cdec = c_ar['label_pos']
        cx, cy = rete_ar._star_xy(cra, cdec)
        
        c_stars_data = []
        for s in c_ar['stars']:
            sid, s_name_ar, ra, dec, mag, show_lbl, ha, va, ox, oy = s
            s_lat = lat_star_map.get(sid, (sid, sid))
            s_name_lat = s_lat[1] if len(s_lat) > 1 and s_lat[1] else sid
            
            xp, yp = rete_ar._star_xy(ra, dec)
            r_val = float((xp**2 + yp**2)**0.5)
            th_deg = float(np.rad2deg(np.arctan2(yp, xp))) if 'np' in globals() else 0.0
            
            # True label position
            import numpy as np
            th = np.arctan2(yp, xp)
            dr = oy if (oy != 0.0 or ox != 0.0) else 0.024
            dt = ox
            xl = float((r_val + dr) * np.cos(th) - dt * np.sin(th))
            yl = float((r_val + dr) * np.sin(th) + dt * np.cos(th))
            
            star_obj = {
                "id": sid,
                "constellation_id": cid,
                "name_ar": s_name_ar,
                "name_lat": s_name_lat,
                "ra": round(float(ra), 3),
                "dec": round(float(dec), 3),
                "mag": round(float(mag), 2),
                "show_lbl": bool(show_lbl),
                "ha": ha or "center",
                "va": va or "center",
                "ox": round(float(ox), 4),
                "oy": round(float(oy), 4),
                "xp": round(float(xp), 5),
                "yp": round(float(yp), 5),
                "xl": round(float(xl), 5),
                "yl": round(float(yl), 5),
                "r": round(r_val, 5),
                "th_rad": round(float(th), 5),
                "is_standalone": False
            }
            c_stars_data.append(star_obj)
            all_stars_data.append(star_obj)

        constellations_data.append({
            "id": cid,
            "name_ar": c_ar['name'],
            "name_lat": c_lat.get('name', cid),
            "label_pos": [round(float(cra), 2), round(float(cdec), 2)],
            "cx": round(float(cx), 5),
            "cy": round(float(cy), 5),
            "lines": c_ar['lines'],
            "stars": c_stars_data
        })

    # Standalone stars (Alphecca, Algol)
    standalone_defs = [
        ('alphecca', 'الفكة', 'Alphecca', 233.67, 26.71, 2.22),
        ('algol', 'رأس الغول', 'Algol', 47.11, 40.96, 2.12),
    ]
    for s_id, s_name_ar, s_name_lat, ra, dec, mag in standalone_defs:
        s_ov = overrides.get('stars', {}).get(s_id, {})
        ox = s_ov.get('ox', 0.0)
        oy = s_ov.get('oy', 0.040)
        ha = s_ov.get('ha', 'center')
        va = s_ov.get('va', 'top')
        
        xp, yp = rete_ar._star_xy(ra, dec)
        r_val = float((xp**2 + yp**2)**0.5)
        th = float(np.arctan2(yp, xp))
        dr = oy if (oy != 0.0 or ox != 0.0) else 0.024
        dt = ox
        xl = float((r_val + dr) * np.cos(th) - dt * np.sin(th))
        yl = float((r_val + dr) * np.sin(th) + dt * np.cos(th))
        
        star_obj = {
            "id": s_id,
            "constellation_id": "standalone",
            "name_ar": s_name_ar,
            "name_lat": s_name_lat,
            "ra": round(float(ra), 3),
            "dec": round(float(dec), 3),
            "mag": round(float(mag), 2),
            "show_lbl": True,
            "ha": ha,
            "va": va,
            "ox": round(float(ox), 4),
            "oy": round(float(oy), 4),
            "xp": round(float(xp), 5),
            "yp": round(float(yp), 5),
            "xl": round(float(xl), 5),
            "yl": round(float(yl), 5),
            "r": round(r_val, 5),
            "th_rad": round(th, 5),
            "is_standalone": True
        }
        all_stars_data.append(star_obj)

    return {
        "constants": {
            "R": float(proj.R),
            "r_capricorn": float(proj.r_capricorn),
            "r_equator": float(proj.r_equator),
            "r_cancer": float(proj.r_cancer),
        },
        "constellations": constellations_data,
        "stars": all_stars_data,
        "overrides": overrides
    }


class LabelEditorHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler serving the Label Editor single page app and JSON API."""

    def log_message(self, format, *args):
        # Clean logging
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ('/', '/index.html'):
            editor_html_path = os.path.join(os.path.dirname(__file__), 'editor', 'index.html')
            if not os.path.isfile(editor_html_path):
                self.send_error(404, "Editor HTML not found")
                return
            with open(editor_html_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if path == '/api/data':
            data = collect_labels_data()
            body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_len).decode('utf-8') if content_len > 0 else "{}"

        if path == '/api/save':
            try:
                payload = json.loads(post_body)
                save_overrides_to_file(payload)
                
                # Automatically regenerate screen assets via fresh subprocess (Plate.svg, Rete.svg, web, android)
                run_regenerate_assets(screen_mode=True)
                
                resp = {"status": "ok", "message": "Overrides saved permanently and vector assets refreshed!"}
            except Exception as e:
                resp = {"status": "error", "message": str(e)}

            body = json.dumps(resp).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == '/api/export_pdf':
            try:
                run_regenerate_assets(screen_mode=False)
                resp = {"status": "ok", "message": "High-resolution PDFs exported to exports/pdf/!"}
            except Exception as e:
                resp = {"status": "error", "message": str(e)}

            body = json.dumps(resp).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == '/api/reset':
            try:
                save_overrides_to_file({"stars": {}, "constellations": {}})
                run_regenerate_assets(screen_mode=True)
                resp = {"status": "ok", "message": "Reset all label offsets to default."}
            except Exception as e:
                resp = {"status": "error", "message": str(e)}

            body = json.dumps(resp).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404, "Not Found")


def start_label_editor(port=8088, open_browser=True):
    """Starts the label editor HTTP server and opens the browser."""
    server_address = ('127.0.0.1', port)
    try:
        httpd = HTTPServer(server_address, LabelEditorHandler)
    except OSError:
        # Fallback to next port if occupied
        port += 1
        server_address = ('127.0.0.1', port)
        httpd = HTTPServer(server_address, LabelEditorHandler)

    url = f"http://127.0.0.1:{port}"
    print("\n" + "=" * 60)
    print("  Classical Astrolabe - Visual Drag & Drop Label Editor")
    print("=" * 60)
    print(f"  Editor URL:       {url}")
    print(f"  Storage Target:   {get_overrides_filepath()}")
    print("  Controls:")
    print("    - Click and drag any star or constellation label")
    print("    - Use Arrow keys for 0.002 precision nudging")
    print("    - Click 'Save & Apply' to write permanently to project")
    print("  Press Ctrl+C in terminal to stop the editor.")
    print("=" * 60 + "\n")

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Label Editor server...")
        httpd.server_close()


if __name__ == '__main__':
    start_label_editor()
