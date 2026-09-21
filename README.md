# Classical Planispheric Astrolabe (الأسطرلاب الفلكي المستوي)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](LICENSE)
[![Platform: Web | Android | Vector CAD](https://img.shields.io/badge/Platform-Web%20%7C%20Android%20%7C%20Vector%20CAD-green.svg)](#platforms)

An authentic, mathematically rigorous reproduction and interactive simulation suite of the **Classical Islamic Planispheric Astrolabe** (الأسطرلاب المستوي).

This project unites high-resolution mathematical vector CAD generation (ready for precision laser-cutting, CNC machining, or 3D engraving) with a modern, GPU-accelerated interactive experience across **Web (HTML5/Canvas)** and **Android Mobile** devices.

---

## Table of Contents

- [Overview & Architecture](#overview--architecture)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
  - [1. Interactive Web Application](#1-interactive-web-application)
  - [2. Vector Plates Generator & Exporter (CAD)](#2-vector-plates-generator--exporter-cad)
  - [3. Visual Label Tuning Suite](#3-visual-label-tuning-suite)
  - [4. Android Mobile Application](#4-android-mobile-application)
  - [5. Synchronizing Web to Android](#5-synchronizing-web-to-android)
- [CLI Reference](#cli-reference)
- [Component Anatomy](#component-anatomy)
- [Mathematical & Astronomical Principles](#mathematical--astronomical-principles)
- [Customization & Typography](#customization--typography)
- [License](#license)

---

## Overview & Architecture

The astrolabe was the world's most sophisticated astronomical computer for over a millennium. This repository is architected into modular, focused layers:

1. **Interactive Digital Astrolabe (HTML5 / Web & Mobile)**:
   - GPU-accelerated canvas/SVG rendering with smooth drag-and-drop rotation of Rete, Rule, and Alidade.
   - Real-time live ticking clock mode with automatic civil GMT+0 tracking and seamless pause on manual interaction.
   - Comprehensive celestial HUD: Local Sidereal Time (LST), Apparent Solar Time (AST), Equation of Time, and Unequal Hours (*Sa'at Zamaniyya*).
   - Solar altitude, prayer times (Fajr, Shuruq, Zuhr, Asr, Maghrib, Isha), Qibla alignment, and interactive celestial inspector for fixed stars.
   - Front (Tympan & Rete) and Back (Surveying quadrant, Shadow squares, Calendar, Equation of Time) flipping.

2. **Mathematical Vector CAD Engine (`src/astrolabe/engine.py`)**:
   - Exact stereographic projection equations for any terrestrial latitude (default: $35.78^\circ\text{N}$ Tangier, Morocco).
   - Exports multi-layer, print-ready PDF and SVG vector files for physical fabrication (laser cutters, CNC engravers).
   - Standalone, zero-dependency contextual Arabic shaper and classical Abjad numeral system (*Hisab al-Jummal* / حساب الجمل).

3. **Visual Label Editor (`src/astrolabe/label_editor.py`)**:
   - Interactive browser-based drag-and-drop tool to fine-tune star pointers and zodiac labels, persisting coordinates directly to `data/label_overrides.json`.

4. **Native Android Application (`android/`)**:
   - Offline Android app bundling the modern digital astrolabe into a high-performance, touch-optimized mobile APK (`android/release/Astrolabe.apk`).

---

## Repository Structure

```text
Astrolabe/
├── README.md                      # Comprehensive project documentation
├── requirements.txt               # Minimal Python dependencies (matplotlib, numpy)
├── main.py                        # Unified modular CLI launcher
├── .gitignore                     # Git rules for clean workspace
│
├── src/                           # Python Vector Engine & Tools
│   └── astrolabe/
│       ├── __init__.py            # Clean library exports
│       ├── engine.py              # Mathematical stereographic CAD & vector generator
│       ├── label_editor.py        # Visual drag-and-drop label tuning server
│       └── editor/
│           └── index.html         # Label editor web interface
│
├── web/                           # Modern Interactive Web Application
│   ├── index.html                 # Main digital astrolabe application
│   ├── app.js                     # Core simulation logic, live clock, celestial HUD
│   ├── style.css                  # Responsive dark-sky UI styling
│   └── assets/                    # Optimized vector layers (Plate, Rete, Rule, Back, Alidade)
│
├── data/                          # Configuration & Tuning Data
│   └── label_overrides.json       # Visual overrides for star & constellation labels
│
├── exports/                       # Print-Ready Fabrication Files
│   ├── pdf/                       # 300 DPI vector PDFs for high-resolution printing
│   └── svg/                       # Scalable vector graphics for CNC / laser engraving
│
└── android/                       # Native Android Project
    ├── app/                       # Android source code
    │   └── src/main/assets/       # Bundled offline simulation assets
    ├── release/
    │   └── Astrolabe.apk          # Prebuilt, ready-to-install Android APK
    ├── build.gradle.kts           # Gradle configuration
    └── gradlew / gradlew.bat      # Gradle wrappers
```

---

## Quick Start

### Installation
Clone the repository and install the minimal Python dependencies:

```bash
git clone https://github.com/MohamedAmineBouguezzoul/Astrolabe.git
cd Astrolabe
pip install -r requirements.txt
```

### Launch Interactive Astrolabe
Simply run:

```bash
python main.py
```
This automatically starts a local HTTP server and opens the modern interactive astrolabe in your default browser.

*(You can also double-click and open `web/index.html` directly in any web browser without Python installed!)*

---

## Usage Guide

### 1. Interactive Web Application
Launch the web application with a custom port:

```bash
python main.py --web --port 8080
```

**Interactive Controls**:
- **Rotate Rete (الشبكة)**: Click and drag anywhere on the pierced star rete.
- **Rotate Rule (المسطرة)**: Hold `Shift` and drag the mouse, or tap the **Rule Mode** toggle button.
- **Rotate Alidade (العضادة)**: Drag on the back face of the instrument.
- **Flip Face (قلب الأسطرلاب)**: Click the **Face Flip** button or press spacebar to toggle between Front (Tympan/Rete) and Back (Surveying/Calendar).
- **Live Clock Mode**: Displays real-time civil time (GMT+0) and moves continuously. Moving any slider automatically pauses live updates to let you explore freely; click **Resume Clock** to snap back to the present moment.

### 2. Vector Plates Generator & Exporter (CAD)
Generate high-precision vector plates (PDF and SVG) customized for your latitude and city:

```bash
# Export plates for Tangier (lat 35.78°N)
python main.py --export --lat 35.78 --city "Tangier"

# Export plates for Cairo (lat 30.04°N) with Latin numerals
python main.py --export --lat 30.04 --city "Cairo" --lang latin --num latin
```
Outputs are cleanly organized in:
- `exports/pdf/`: Print-ready vector PDF sheets.
- `exports/svg/`: CAD/CAM SVGs for CNC laser cutting and engraving.

To regenerate screen-optimized SVGs for web and mobile assets:
```bash
python main.py --screen
```

You can also run the core vector engine directly:
```bash
python src/astrolabe/engine.py
# Or with screen-optimized assets:
python src/astrolabe/engine.py --screen
```

### 3. Visual Label Tuning Suite
If you want to adjust the position, offset, or rotation of any star pointer or constellation label on the Rete:

```bash
python main.py --edit-labels
```
This launches an interactive drag-and-drop editor in your browser and updates `data/label_overrides.json` in real time.

### 4. Android Mobile Application
Install the standalone mobile application on any Android device:
- Precompiled APK is located at:
  ```text
  android/release/Astrolabe.apk
  ```
- Install via ADB:
  ```bash
  adb install android/release/Astrolabe.apk
  ```
- Or transfer the APK directly to your phone and tap to install.

### 5. Synchronizing Web to Android
When modifying the web application (`web/app.js`, `web/index.html`, or `web/style.css`), sync your changes directly to the Android app assets with a single command:

```bash
python main.py --sync
```

---

## CLI Reference

```text
usage: main.py [-h] [--web] [--export] [--screen] [--edit-labels] [--sync]
               [--lat LAT] [--city CITY] [--lang {arabic,latin}]
               [--num {abjad,eastern_arabic,latin}] [--port PORT]
               [--output-dir OUTPUT_DIR]

Classical Astrolabe - Simulation & Vector Generation Suite

options:
  -h, --help            Show this help message and exit
  --web                 Launch the interactive HTML5 simulation in your web browser (default action)
  --export              Generate and export high-resolution plates (Mater, Plate, Rete, Rule, Back, Alidade) to exports/
  --screen              Generate and sync screen-optimized vector SVGs to web/ and android/
  --edit-labels         Launch the visual Drag-and-Drop Label Editor in your browser
  --sync                Synchronize web application files (HTML, JS, CSS) to Android assets
  --lat LAT             Latitude in degrees (default: 35.78)
  --city CITY           City or location name inscribed on the tympan plate (default: Tangier)
  --lang {arabic,latin}
                        Inscriptions language (default: arabic)
  --num {abjad,eastern_arabic,latin}
                        Numeral system: 'abjad' (Hisab al-Jummal), 'eastern_arabic', or 'latin' (default: abjad)
  --port PORT           Local HTTP server port (default: 8080)
  --output-dir OUTPUT_DIR
                        Custom output directory for --export (defaults to exports/)
```

---

## Component Anatomy

| Component | Arabic Name | Function & Engravings |
| :--- | :--- | :--- |
| **Mater & Limb** | الأم والحجرة | Bounding frame with $360^\circ$ circular scale graduated in degrees and 24 equal civil hours. |
| **Kursi (Throne)** | الكرسي | Triangular decorative bracket and suspension arch atop the Mater, holding the suspension ring (*Halaqa* / الحلقة) and inscribed with city and dedication details. |
| **Tympan (Plate)** | الصفيحة | Stereographic projection of local celestial coordinates: Tropic of Cancer, Equator, Tropic of Capricorn, Horizon, Almucantars ($1^\circ$ to $90^\circ$), Azimuths, Twilight arcs ($18^\circ$ / $15^\circ$), Islamic Prayer curves (Zuhr & Asr), and 12 Unequal Hours. |
| **Rete** | الشبكة | Pierced celestial map rotating about the celestial pole. Features the offset **Ecliptic Ring** (دائرة البروج) divided into 12 zodiac signs, and pointers (*shaziyyah* / شظية) locating major fixed stars (Vega, Altair, Sirius, Arcturus, Aldebaran, Rigel, etc.). |
| **Rule** | المسطرة | Rotating radial arm on the front face used to align solar positions on the ecliptic with plate graduations and limb degrees. |
| **Back Face** | الظهر | Multi-functional scientific calculator: <br>• $360^\circ$ Altitude Limb with quadrant divisions.<br>• Zodiac ring paired with calendar days for solar longitude lookup.<br>• Sine/Cosine quadrant (*Rub' al-Mujayyab* / ربع المجيب).<br>• Unequal Hours curve diagram.<br>• Equation of Time analemma curve.<br>• Dual Shadow Squares (*Umbra Recta* / الظل المبسوط and *Umbra Versa* / الظل المنكوس). |
| **Alidade** | العضادة | Sighting rule on the back with paired pinhole sight vanes (*Hadafah* / الهدف) for measuring celestial altitudes and surveying terrestrial heights. |

---

## Mathematical & Astronomical Principles

### 1. Stereographic Projection
The astrolabe maps points from the celestial sphere $(\alpha, \delta)$ from the South Celestial Pole onto the equatorial plane:
$$R(\delta) = R_{\text{equator}} \cdot \tan\left(\frac{90^\circ - \delta}{2}\right)$$
- **Tropic of Cancer** ($\delta = +23.44^\circ$): Innermost bounding circle.
- **Equator** ($\delta = 0^\circ$): Center reference circle with radius $R_{\text{equator}}$.
- **Tropic of Capricorn** ($\delta = -23.44^\circ$): Outermost boundary circle of the instrument.

### 2. Almucantars (المقنطرات)
Altitude circles for local latitude $\phi$ and celestial altitude $a \in [0^\circ, 90^\circ]$ project onto circles whose centers $y_c$ and radii $r_a$ along the meridian are given by:
$$y_c = R_{\text{equator}} \cdot \frac{\cos\phi}{\sin\phi + \sin a}$$
$$r_a = R_{\text{equator}} \cdot \frac{\cos a}{\sin\phi + \sin a}$$

### 3. Azimuth Circles (دوائر السموت)
Vertical circles perpendicular to the horizon passing through the Zenith and Nadir, enabling azimuth measurements from True North ($0^\circ$) through East ($90^\circ$), South ($180^\circ$), and West ($270^\circ$).

### 4. Shadow Squares (مربع الظل)
Enables direct trigonometric tangent and cotangent calculations for surveying:
- **Umbra Recta (الظل المبسوط)**: Horizontal shadow cast by a 12-digit or 7-foot gnomon: $\text{Shadow} = 12 \cdot \cot(a)$
- **Umbra Versa (الظل المنكوس)**: Vertical shadow cast when the sun exceeds $45^\circ$: $\text{Shadow} = 12 \cdot \tan(a)$

---

## Customization & Typography

The engine includes built-in font fallbacks that prioritize authentic Kufic calligraphy fonts:
- `Noto Kufi Arabic`
- `Diwan Kufi`
- `KufiStandardGK`
- `Arial Unicode MS` / `Geeza Pro`

Numeral systems supported:
1. **`abjad`**: Classical alphanumeric letters (*Hisab al-Jummal*), where $\text{أ}=1, \text{ب}=2, \dots, \text{ي}=10, \text{ك}=20$.
2. **`eastern_arabic`**: Mashriqi numerals ($٠, ١, ٢, ٣, ٤, ٥, ٦, ٧, ٨, ٩$).
3. **`latin`**: Standard Western numerals ($1, 2, 3, \dots$).

---

## Author & Acknowledgements

Developed by **[Mohamed Amine Bouguezzoul](https://github.com/MohamedAmineBouguezzoul)**.

Dedicated to the digital preservation and astronomical revival of classical Islamic mathematical instruments and historical horology.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
