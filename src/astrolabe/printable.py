"""
Astrolabe Printable A4 Sheet Generator.
========================================
Generates print-ready, precision-calibrated A4 vector PDF sheets for physical 
cutting, crafting, and assembly of the planispheric astrolabe:

1. Mater (أم الأسطرلاب والعرش): Chassis with Kursi suspension throne (heavy paper / cardstock).
2. Tympan Plate & Rule (الصفحة والمري): Circular plate (Tangier 36° N) with horizontal Rule above (cardstock).
3. Back & Alidade (الظهر والعضادة): Circular back dial with horizontal Alidade above (cardstock).
4. Rete (عنكبوت الأسطرلاب): Dedicated page with Rete only for printing on transparent acetate film.

Includes:
- Exact 1:1 physical millimeter scaling across all sheets (limbus outer diameter = 180 mm).
- 50 mm calibration bar on each page to verify printer 100% scale.
- Ø 3mm center pivot drill hole marks.
- Separation cut lines and assembly guides.
- Combined 4-page PDF document (Astrolabe_Complete_A4.pdf) and individual sheet PDFs.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
from matplotlib.backends.backend_pdf import PdfPages

if not __package__:
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    __package__ = 'astrolabe'

from .arabic import ArabicFormatter
from .engine import Astrolabe


class RotatedAxes:
    """
    Transparent adapter that rotates all plotting calls (plots, patches, texts)
    around (0, 0) by a specified angle in degrees.
    Used to lay out vertical instruments (Rule and Alidade) horizontally to optimize paper space.
    """
    def __init__(self, ax, angle_deg=-90):
        self.ax = ax
        self.angle_deg = float(angle_deg)
        self.rad = np.deg2rad(self.angle_deg)
        self.cos_a = np.cos(self.rad)
        self.sin_a = np.sin(self.rad)

    def _rotate_pt(self, x, y):
        xr = x * self.cos_a - y * self.sin_a
        yr = x * self.sin_a + y * self.cos_a
        return xr, yr

    def plot(self, xs, ys, *args, **kwargs):
        xs = np.asarray(xs)
        ys = np.asarray(ys)
        xr = xs * self.cos_a - ys * self.sin_a
        yr = xs * self.sin_a + ys * self.cos_a
        return self.ax.plot(xr, yr, *args, **kwargs)

    def text(self, x, y, s, *args, **kwargs):
        xr, yr = self._rotate_pt(x, y)
        rot = kwargs.get('rotation', 0)
        kwargs['rotation'] = (rot + self.angle_deg) % 360
        return self.ax.text(xr, yr, s, *args, **kwargs)

    def add_patch(self, patch):
        if isinstance(patch, patches.Polygon):
            verts = patch.get_xy()
            new_verts = [self._rotate_pt(x, y) for x, y in verts]
            patch.set_xy(new_verts)
            return self.ax.add_patch(patch)
        elif isinstance(patch, patches.Rectangle):
            x0, y0 = patch.get_xy()
            w = patch.get_width()
            h = patch.get_height()
            corners = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
            rot_corners = [self._rotate_pt(cx, cy) for cx, cy in corners]
            poly = patches.Polygon(
                rot_corners, closed=True,
                facecolor=patch.get_facecolor(),
                edgecolor=patch.get_edgecolor(),
                linewidth=patch.get_linewidth(),
                linestyle=patch.get_linestyle(),
                zorder=patch.get_zorder()
            )
            return self.ax.add_patch(poly)
        elif isinstance(patch, plt.Circle):
            cx, cy = patch.center
            rx, ry = self._rotate_pt(cx, cy)
            patch.center = (rx, ry)
            return self.ax.add_patch(patch)
        return self.ax.add_patch(patch)

    def __getattr__(self, name):
        return getattr(self.ax, name)


class PrintableA4:
    """
    Coordinates creation of print-ready A4 PDF sheets for the astrolabe.
    """
    # A4 dimensions in millimeters
    PAGE_WIDTH_MM = 210.0
    PAGE_HEIGHT_MM = 297.0
    
    # Outer limbus physical diameter: 180.0 mm (18.0 cm)
    LIMBUS_DIAMETER_MM = 180.0

    def __init__(self, astrolabe=None, latitude=35.78, city="Tangier",
                 language="arabic", numeral_system="eastern_arabic", output_dir="printable"):
        if astrolabe is not None:
            self.astrolabe = astrolabe
        else:
            self.astrolabe = Astrolabe(
                latitude=latitude,
                city=city,
                language=language,
                numeral_system=numeral_system,
                screen_mode=False
            )
        if output_dir is None or output_dir == "printable":
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
            self.output_dir = os.path.join(project_root, "printable")
        else:
            self.output_dir = output_dir

        # Calculate exact scale (mm per data unit)
        r_cap = self.astrolabe.proj.r_capricorn
        r_outer = r_cap * 1.330
        self.scale = self.LIMBUS_DIAMETER_MM / (2.0 * r_outer)

    def _create_a4_figure(self):
        """Creates a standard A4 portrait figure (210 x 297 mm)."""
        figsize_in = (self.PAGE_WIDTH_MM / 25.4, self.PAGE_HEIGHT_MM / 25.4)
        fig = plt.figure(figsize=figsize_in)
        fig.patch.set_alpha(0.0)
        return fig

    def _add_page_decorations(self, fig, sheet_num, title, subtitle, instructions=None):
        """Adds page headers, calibration bar, and metadata in millimeter coordinates."""
        ax_p = fig.add_axes([0, 0, 1, 1])
        ax_p.set_xlim(0, self.PAGE_WIDTH_MM)
        ax_p.set_ylim(0, self.PAGE_HEIGHT_MM)
        ax_p.axis('off')

        # Reshape any Arabic text in title, subtitle, and instructions for proper RTL rendering
        title_reshaped = ArabicFormatter.reshape_text(title)
        subtitle_reshaped = ArabicFormatter.reshape_text(subtitle)

        # Header banner
        ax_p.text(self.PAGE_WIDTH_MM / 2.0, 291, title_reshaped,
                  fontsize=9.5, fontweight='bold', color='#0B3C5D', ha='center', va='top')
        ax_p.text(self.PAGE_WIDTH_MM / 2.0, 286.5, subtitle_reshaped,
                  fontsize=7.0, color='#555555', ha='center', va='top')
        
        # Sheet number badge
        ax_p.text(self.PAGE_WIDTH_MM - 14, 291, f"Sheet {sheet_num}/4",
                  fontsize=8.0, fontweight='bold', color='#888888', ha='right', va='top')

        # Specific assembly instructions
        if instructions:
            inst_reshaped = ArabicFormatter.reshape_text(instructions)
            ax_p.text(self.PAGE_WIDTH_MM / 2.0, 282, inst_reshaped,
                      fontsize=6.5, color='#1A5276', ha='center', va='top')

        # 50 mm Calibration Scale Bar at bottom
        cal_len = 50.0
        cal_x0 = (self.PAGE_WIDTH_MM - cal_len) / 2.0
        cal_x1 = cal_x0 + cal_len
        cal_y = 11.0

        ax_p.plot([cal_x0, cal_x1], [cal_y, cal_y], color='#222222', linewidth=1.2)
        ax_p.plot([cal_x0, cal_x0], [cal_y - 2.0, cal_y + 2.0], color='#222222', linewidth=1.2)
        ax_p.plot([cal_x1, cal_x1], [cal_y - 2.0, cal_y + 2.0], color='#222222', linewidth=1.2)
        ax_p.plot([cal_x0 + 25.0, cal_x0 + 25.0], [cal_y - 1.2, cal_y + 1.2], color='#222222', linewidth=0.8)
        
        ax_p.text(self.PAGE_WIDTH_MM / 2.0, cal_y - 3.5,
                  "50 mm Calibration Bar  —  Verify with a physical ruler before cutting (Print at 100% / Actual Size)",
                  fontsize=6.2, color='#444444', ha='center', va='top')
        
        # Corner crop marks (for alignment)
        m_len = 5.0
        for cx, cy in [(12, 12), (self.PAGE_WIDTH_MM - 12, 12),
                       (12, self.PAGE_HEIGHT_MM - 12), (self.PAGE_WIDTH_MM - 12, self.PAGE_HEIGHT_MM - 12)]:
            sx = 1 if cx < self.PAGE_WIDTH_MM / 2 else -1
            sy = 1 if cy < self.PAGE_HEIGHT_MM / 2 else -1
            ax_p.plot([cx, cx + sx * m_len], [cy, cy], color='#CCCCCC', linewidth=0.6)
            ax_p.plot([cx, cx], [cy, cy + sy * m_len], color='#CCCCCC', linewidth=0.6)

        return ax_p

    def _add_component_axes(self, fig, cx_mm, cy_mm, x_range, y_range):
        """
        Creates an axes centered at (cx_mm, cy_mm) on the A4 page (with cx_mm, cy_mm
        corresponding to data point (0, 0)) with exact physical millimeter scaling.
        
        x_range: tuple (x_min, x_max) in data units
        y_range: tuple (y_min, y_max) in data units
        """
        x_min, x_max = x_range
        y_min, y_max = y_range

        w_mm = (x_max - x_min) * self.scale
        h_mm = (y_max - y_min) * self.scale

        left_mm = cx_mm + x_min * self.scale
        bottom_mm = cy_mm + y_min * self.scale

        left = left_mm / self.PAGE_WIDTH_MM
        bottom = bottom_mm / self.PAGE_HEIGHT_MM
        width = w_mm / self.PAGE_WIDTH_MM
        height = h_mm / self.PAGE_HEIGHT_MM

        ax = fig.add_axes([left, bottom, width, height])
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_aspect('equal')
        ax.axis('off')
        return ax

    def render_mater_page(self):
        """
        Page 1: Mater (Chassis + Kursi throne).
        Centered vertically and horizontally on A4 sheet with complete Kursi throne shown.
        """
        fig = self._create_a4_figure()
        self._add_page_decorations(
            fig, sheet_num=1,
            title="ASTROLABE MATER & SUSPENSION THRONE (أم الأسطرلاب والعرش)",
            subtitle="Classical Planispheric Astrolabe • 1:1 Scale Print (A4) • Tangier (طنجة)",
            instructions="Print on heavy cardstock (250-300 gsm). Cut along outer Kursi contour and 180mm outer circular rim."
        )

        # Mater bounds in data units:
        # Origin (0, 0) is the center of the astrolabe circle.
        # X: outer rim is r = 2.0263, safe range [-2.06, 2.06] -> width 183.0 mm (13.5 mm margin left/right)
        # Y: Kursi apex is at y ~ +2.88, safe y_max = 2.96 (reaches Y = 263.5 mm, leaving 33.5 mm top margin)
        #    Bottom rim is y = -2.03, title banner reaches y ~ -2.18, safe y_min = -2.22 (Y = 33.5 mm)
        # Center of circle placed at cx = 105.0 mm, cy = 132.0 mm
        ax_mater = self._add_component_axes(
            fig,
            cx_mm=105.0,
            cy_mm=132.0,
            x_range=(-2.06, 2.06),
            y_range=(-2.22, 2.96)
        )
        self.astrolabe.mater.draw(ax_mater)

        return fig

    def render_plate_and_rule_page(self):
        """
        Page 2: Tympan Plate (circular, lower) + Rule (horizontal, upper).
        Saves paper by packing the Rule above the Plate.
        """
        fig = self._create_a4_figure()
        ax_p = self._add_page_decorations(
            fig, sheet_num=2,
            title="ASTROLABE TYMPAN (PLATE 36° N) & RULE (المسطرة / المري)",
            subtitle="Classical Planispheric Astrolabe • 1:1 Scale Print (A4) • Tangier (طنجة 36°)",
            instructions="Print on cardstock or matte paper. Cut out Rule and Tympan plate along circular/outer contours."
        )

        # Separation cut line between Rule and Plate
        cut_y = 218.0
        ax_p.plot([15, self.PAGE_WIDTH_MM - 15], [cut_y, cut_y], color='#999999', linestyle='--', linewidth=0.7)
        ax_p.text(self.PAGE_WIDTH_MM / 2.0, cut_y + 1.8, "--- CUT LINE ---",
                  fontsize=6.5, color='#777777', ha='center', va='bottom')

        txt_rule = ArabicFormatter.reshape_text("[UP] RULE (OSTENSOR / المري) — Cut along outline and drill center Ø 3mm hole")
        txt_plate = ArabicFormatter.reshape_text("[DOWN] TYMPAN (PLATE 36° N) — Cut along outer circular rim (Ø 180 mm)")

        ax_p.text(self.PAGE_WIDTH_MM / 2.0, cut_y + 8.0, txt_rule,
                  fontsize=6.5, fontweight='bold', color='#1A5276', ha='center', va='bottom')
        ax_p.text(self.PAGE_WIDTH_MM / 2.0, cut_y - 7.5, txt_plate,
                  fontsize=6.5, fontweight='bold', color='#1A5276', ha='center', va='top')

        # 1. Tympan Plate at (105, 110) mm (Ø 180 mm, from Y=18.5 to Y=201.5 mm)
        ax_plate = self._add_component_axes(
            fig, cx_mm=105.0, cy_mm=110.0,
            x_range=(-2.06, 2.06), y_range=(-2.06, 2.06)
        )
        self.astrolabe.tympan.draw(ax_plate)

        # 2. Rule (Ostensor) rotated horizontally at (105, 252) mm
        ax_rule = self._add_component_axes(
            fig, cx_mm=105.0, cy_mm=252.0,
            x_range=(-2.06, 2.06), y_range=(-0.35, 0.35)
        )
        rot_ax = RotatedAxes(ax_rule, angle_deg=-90)
        self.astrolabe.rule.draw(rot_ax)

        return fig

    def render_back_and_alidade_page(self):
        """
        Page 3: Astrolabe Back (circular, lower) + Alidade (horizontal, upper).
        Saves paper by packing the Alidade above the Back.
        """
        fig = self._create_a4_figure()
        ax_p = self._add_page_decorations(
            fig, sheet_num=3,
            title="ASTROLABE BACK (ظهر الأسطرلاب) & ALIDADE (العضادة ذات الشظيتين)",
            subtitle="Classical Planispheric Astrolabe • 1:1 Scale Print (A4) • Solar Calendar, Zodiac & Shadow Square",
            instructions="Print on cardstock. Mount Back onto reverse of Mater. Fold/assemble Alidade sighting vanes."
        )

        # Separation cut line between Alidade and Back
        cut_y = 218.0
        ax_p.plot([15, self.PAGE_WIDTH_MM - 15], [cut_y, cut_y], color='#999999', linestyle='--', linewidth=0.7)
        ax_p.text(self.PAGE_WIDTH_MM / 2.0, cut_y + 1.8, "--- CUT LINE ---",
                  fontsize=6.5, color='#777777', ha='center', va='bottom')

        txt_alidade = ArabicFormatter.reshape_text("[UP] ALIDADE (DIOPTRA / العضادة) — Cut along outline, fold vanes, drill center Ø 3mm hole")
        txt_back = ArabicFormatter.reshape_text("[DOWN] ASTROLABE BACK (الظهر) — Cut along 180mm outer circular guide to match Mater reverse")

        ax_p.text(self.PAGE_WIDTH_MM / 2.0, cut_y + 8.0, txt_alidade,
                  fontsize=6.5, fontweight='bold', color='#1A5276', ha='center', va='bottom')
        ax_p.text(self.PAGE_WIDTH_MM / 2.0, cut_y - 7.5, txt_back,
                  fontsize=6.5, fontweight='bold', color='#1A5276', ha='center', va='top')

        # 1. Back Dial at (105, 110) mm
        ax_back = self._add_component_axes(
            fig, cx_mm=105.0, cy_mm=110.0,
            x_range=(-2.06, 2.06), y_range=(-2.06, 2.06)
        )
        self.astrolabe.back.draw(ax_back)

        # Add matching 180mm outer cutting circle guide around Back so it matches Mater chassis
        r_outer_mater = self.astrolabe.proj.r_capricorn * 1.330
        ax_back.add_patch(plt.Circle((0, 0), r_outer_mater, color='#888888', fill=False,
                                     linestyle='--', linewidth=0.8, zorder=10))

        # 2. Alidade rotated horizontally at (105, 252) mm
        ax_alidade = self._add_component_axes(
            fig, cx_mm=105.0, cy_mm=252.0,
            x_range=(-2.06, 2.06), y_range=(-0.35, 0.35)
        )
        rot_alidade = RotatedAxes(ax_alidade, angle_deg=-90)
        self.astrolabe.alidade.draw(rot_alidade)

        return fig

    def render_rete_page(self):
        """
        Page 4: Rete (عنكبوت الأسطرلاب).
        Kept strictly alone on its own page for printing on transparent acetate film.
        """
        fig = self._create_a4_figure()
        self._add_page_decorations(
            fig, sheet_num=4,
            title="ASTROLABE RETE (عنكبوت الأسطرلاب) — TRANSPARENCY FILM",
            subtitle="Classical Planispheric Astrolabe • 1:1 Scale Print (A4) • 23 Stars & Zodiac Ring",
            instructions="IMPORTANT: Print on clear transparency film (overhead acetate) at 100% scale. Cut along outer Tropic of Capricorn rim."
        )

        # Rete centered on the sheet at (105, 148.5) mm
        ax_rete = self._add_component_axes(
            fig, cx_mm=105.0, cy_mm=148.5,
            x_range=(-1.65, 1.65), y_range=(-1.65, 1.65)
        )
        self.astrolabe.rete.draw(ax_rete)

        return fig

    def export_all(self, dpi=300):
        """
        Exports all printable sheets to the output directory:
        1. 1_Mater_A4.pdf
        2. 2_Plate_and_Rule_A4.pdf
        3. 3_Back_and_Alidade_A4.pdf
        4. 4_Rete_Transparency_A4.pdf
        5. Astrolabe_Complete_A4.pdf (combined 4-page PDF document)
        6. README.md (assembly & printing guide)
        """
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"\n========================================================")
        print(f"  Generating Print-Ready A4 Astrolabe PDFs: {self.output_dir}")
        print(f"========================================================")
        print(f"  • Scale: 1:1 ({self.scale:.4f} mm/unit, Limbus Ø = {self.LIMBUS_DIAMETER_MM:.1f} mm)")
        print(f"  • Format: A4 (210 x 297 mm)")

        combined_path = os.path.join(self.output_dir, "Astrolabe_Complete_A4.pdf")
        
        with PdfPages(combined_path) as multi_pdf:
            # 1. Mater
            print("  [1/4] Generating Sheet 1: Mater & Suspension Throne...")
            fig1 = self.render_mater_page()
            path1 = os.path.join(self.output_dir, "1_Mater_A4.pdf")
            fig1.savefig(path1, format='pdf', dpi=dpi, transparent=False)
            multi_pdf.savefig(fig1, dpi=dpi)
            plt.close(fig1)

            # 2. Plate and Rule
            print("  [2/4] Generating Sheet 2: Tympan Plate & Rule (Packaged)...")
            fig2 = self.render_plate_and_rule_page()
            path2 = os.path.join(self.output_dir, "2_Plate_and_Rule_A4.pdf")
            fig2.savefig(path2, format='pdf', dpi=dpi, transparent=False)
            multi_pdf.savefig(fig2, dpi=dpi)
            plt.close(fig2)

            # 3. Back and Alidade
            print("  [3/4] Generating Sheet 3: Astrolabe Back & Alidade (Packaged)...")
            fig3 = self.render_back_and_alidade_page()
            path3 = os.path.join(self.output_dir, "3_Back_and_Alidade_A4.pdf")
            fig3.savefig(path3, format='pdf', dpi=dpi, transparent=False)
            multi_pdf.savefig(fig3, dpi=dpi)
            plt.close(fig3)

            # 4. Rete (Transparency Film)
            print("  [4/4] Generating Sheet 4: Rete (Isolated for Transparency Film)...")
            fig4 = self.render_rete_page()
            path4 = os.path.join(self.output_dir, "4_Rete_Transparency_A4.pdf")
            fig4.savefig(path4, format='pdf', dpi=dpi, transparent=True)
            multi_pdf.savefig(fig4, dpi=dpi)
            plt.close(fig4)

        # Generate README guide
        self._write_guide()

        print(f"\nAll A4 printable sheets generated successfully in '{self.output_dir}':")
        print(f"  1. {path1}")
        print(f"  2. {path2}")
        print(f"  3. {path3}")
        print(f"  4. {path4}")
        print(f"  ★ Combined: {combined_path}")


    def _write_guide(self):
        """Writes an assembly and printing instruction markdown guide in the printable directory."""
        guide_content = f"""# Astrolabe Print & Assembly Guide (A4 Sheets)

This folder contains precision print-ready **A4 vector PDF files** to build a fully functional, authentic classical planispheric astrolabe at exact **1:1 scale** (Outer dial diameter: **{self.LIMBUS_DIAMETER_MM:.1f} mm / 18.0 cm**).

---

## File Index

| Sheet | File | Material | Description |
|:-----:|:-----|:---------|:------------|
| **1** | [`1_Mater_A4.pdf`](1_Mater_A4.pdf) | Heavy Cardstock (250-300 gsm) or Wood/MDF | **Mater & Kursi (أم الأسطرلاب والعرش)**: The structural chassis with suspension throne, 24 equal hour limbus, and compass rose belly. |
| **2** | [`2_Plate_and_Rule_A4.pdf`](2_Plate_and_Rule_A4.pdf) | Medium Cardstock / Matte Paper | **Tympan (الصفحة) & Rule (المسطرة)**: Circular plate for Tangier 36° N, packed with the longitudinal Rule horizontally above to save paper. |
| **3** | [`3_Back_and_Alidade_A4.pdf`](3_Back_and_Alidade_A4.pdf) | Heavy Cardstock / Paper (glued to back) | **Back (الظهر) & Alidade (العضادة)**: Circular calendar dial, zodiac & shadow square, packed with the sighting Alidade horizontally above. |
| **4** | [`4_Rete_Transparency_A4.pdf`](4_Rete_Transparency_A4.pdf) | **Clear Transparency Film (Acetate / OHP film)** | **Rete (عنكبوت الأسطرلاب)**: Star pointers and zodiac ring. Isolated on its own sheet with transparent background. |
| **★** | [`Astrolabe_Complete_A4.pdf`](Astrolabe_Complete_A4.pdf) | Combined Multi-page PDF | All 4 sheets above bundled in a single 4-page PDF document. |

---

## Printer Instructions

1. **Paper Size**: Standard **A4** (210 x 297 mm).
2. **Page Scaling**: You **MUST** select **"Actual Size"** or **"Scale: 100%"** in your printer dialog.
   - **Do NOT** select *"Fit to printable area"* or *"Shrink oversized pages"*, as this will distort the scale by ~3-5% and parts will not fit together!
3. **Scale Verification**: Each sheet includes a **50 mm Calibration Bar** at the bottom. Before cutting, measure this line with a physical ruler. It must measure exactly 50 mm (5.0 cm).

---

## Step-by-Step Assembly

### 1. The Chassis (Mater & Back)
- Cut out the **Mater** along the outer contour of the suspension Kursi arch and the outer 180 mm circle.
- Cut out the **Back** along its outer 180 mm dashed cutting circle.
- Glue the Back sheet onto the reverse side of the Mater (or mount both onto a 2-3 mm piece of chipboard, cardboard, or plywood for structural rigidity).

### 2. The Tympan (Latitude Plate)
- Cut out the circular **Tympan Plate** along its outer 180 mm circular line.
- The small registration key notch at (0, r_cap) keys into the Mater belly to keep the plate oriented with the meridian.
- Drop the Tympan plate into the Mater cavity.

### 3. The Rete (Transparency)
- Print Sheet 4 on **transparent acetate/overhead transparency film** using an inkjet or laser transparency sheet.
- Cut carefully around the outer double circular rim (Tropic of Capricorn, diameter 135.3 mm).
- Place the transparent Rete on top of the Tympan plate. The stars and ecliptic will rotate smoothly over the horizon and altitude curves!

### 4. Sighting Sights & Rulers
- Cut out the **Rule** and **Alidade** along their black outlines.
- If you wish, fold or attach paper tabs on the Alidade sighting vanes at the indicated pinhole markings.
- Carefully drill or punch a **diameter 3 mm center pivot hole** through the marked crosshairs of:
  - Alidade
  - Mater chassis
  - Tympan plate
  - Rete transparency
  - Rule

### 5. Final Pin Assembly
Stack the components from back to front using a 3 mm brass split-pin (brad), binding post (Chicago screw), or bolt:
Alidade (Back) -> Mater / Back -> Tympan Plate -> Transparent Rete -> Rule (Front) -> Fastener / Wedge

Tie a suspension cord or ring through the top hole of the Kursi arch to suspend the astrolabe vertically when sighting stars or the sun with the Alidade!
"""
        with open(os.path.join(self.output_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(guide_content)


if __name__ == '__main__':
    generator = PrintableA4(numeral_system="eastern_arabic")
    generator.export_all()

