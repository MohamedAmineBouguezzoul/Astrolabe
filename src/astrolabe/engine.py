"""
Astrolabe Core Engine & Facade.
Coordinates all astrolabe components (Tympan, Rete, Rule, Back, Alidade)
and provides high-resolution rendering, export, and screen assets generation.
"""

import os
import sys
import json
import shutil
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe

if not __package__:
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    __package__ = 'astrolabe'

from .arabic import ArabicFormatter
from .projection import StereographicProjection, CelestialCircles
from .tympan import (
    Horizon,
    Almucantars,
    AzimuthCircles,
    Twilights,
    PrayerTimes,
    UnequalHours,
    EqualHoursLimbus,
    Kursi,
    Mater,
    Tympan,
)
from .rete import Ecliptic, Star, Rete
from .rules import Rule, Alidade
from .back import get_tangential_rotation, AstrolabeBack

__all__ = [
    'ArabicFormatter',
    'StereographicProjection',
    'CelestialCircles',
    'Horizon',
    'Almucantars',
    'AzimuthCircles',
    'Twilights',
    'PrayerTimes',
    'UnequalHours',
    'EqualHoursLimbus',
    'Kursi',
    'Mater',
    'Tympan',
    'Ecliptic',
    'Star',
    'Rete',
    'Rule',
    'Alidade',
    'get_tangential_rotation',
    'AstrolabeBack',
    'Astrolabe',
]


class Astrolabe:
    """
    Master Astrolabe class (POO) coordinating Tympan, Rete, Rule, Back, and Alidade.
    
    Supports:
    - language: 'latin' or 'arabic' (full authentic Arabic inscriptions)
    - numeral_system: 
        * 'latin': Western numerals (1, 2, 3...)
        * 'eastern_arabic': Eastern Arabic digits (٠, ١, ٢, ...)
        * 'abjad': Classical Islamic Hisab al-Jummal (ا, ب, ج, ...)
    - screen_mode:
        * False: High-density 1° plates optimized for large physical prints/laser engraving
        * True: Screen-optimized typography (large legible fonts, 5°-10° lines, halos)
    """
    def __init__(self, latitude=35.78, city="Tangier", obliquity=23.44, radius_equator=1.0,
                 language="arabic", numeral_system="abjad", screen_mode=False):
        self.city = city
        self.latitude = np.deg2rad(float(latitude))
        self.latitude_deg = float(latitude)
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode
        self.proj = StereographicProjection(radius_equator, obliquity)
        
        # Configure font family for Arabic rendering (Kufic font prioritized)
        if str(self.language).lower().startswith('ar'):
            import matplotlib.font_manager as fm
            kufi_path = os.path.expanduser('~/Library/Fonts/NotoKufiArabic.ttf')
            if os.path.exists(kufi_path):
                try:
                    fm.fontManager.addfont(kufi_path)
                except Exception:
                    pass
            plt.rcParams['font.sans-serif'] = [
                'Noto Kufi Arabic', 'Diwan Kufi', 'KufiStandardGK',
                'Arial Unicode MS', 'Damascus', 'Geeza Pro', 'Baghdad', 'DejaVu Sans', 'Arial'
            ]
        
        # Create core components
        self.mater = self.make_mater()
        self.tympan = self.make_tympan()
        self.rete = self.make_rete()
        self.rule = self.make_rule()
        self.back = self.make_back()
        self.alidade = self.make_alidade()

    def make_mater(self):
        """Constructs and returns the Mater (أم الأسطرلاب / الحجرة والعرش)."""
        return Mater(self.proj, latitude=self.latitude_deg, city=self.city,
                     language=self.language, numeral_system=self.numeral_system,
                     screen_mode=self.screen_mode)

    def make_tympan(self):
        """Constructs and returns the Tympan (plate)."""
        return Tympan(self.latitude_deg, self.city, self.proj, 
                      language=self.language, numeral_system=self.numeral_system,
                      screen_mode=self.screen_mode)

    def make_rete(self):
        """Constructs and returns the Rete."""
        return Rete(self.proj, language=self.language, numeral_system=self.numeral_system,
                    screen_mode=self.screen_mode)

    def make_rule(self):
        """Constructs and returns the Rule (front ostensor)."""
        return Rule(self.proj, language=self.language, numeral_system=self.numeral_system,
                    screen_mode=self.screen_mode)

    def make_back(self):
        """Constructs and returns the Back of the Astrolabe."""
        return AstrolabeBack(self.proj, language=self.language, 
                             numeral_system=self.numeral_system, latitude=self.latitude_deg,
                             city=self.city, show_kursi=False,
                             screen_mode=self.screen_mode)

    def make_alidade(self):
        """Constructs and returns the Sighting Alidade for the back."""
        return Alidade(self.proj, language=self.language, numeral_system=self.numeral_system,
                       screen_mode=self.screen_mode)

    def _setup_fig(self, figsize=(10, 10), is_mater=False):
        if is_mater:
            figsize = (10, 12)
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_aspect('equal')
        lim_x = self.proj.r_capricorn * 1.45
        if is_mater:
            lim_y_top = self.proj.r_capricorn * 2.25
            lim_y_bottom = self.proj.r_capricorn * 1.45
            ax.set_xlim(-lim_x, lim_x)
            ax.set_ylim(-lim_y_bottom, lim_y_top)
        else:
            lim = lim_x
            ax.set_xlim(-lim, lim)
            ax.set_ylim(-lim, lim)
        ax.axis('off')
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        return fig, ax

    def plot_mater(self, filename='Mater.pdf', dpi=300):
        """Draw and export the Mater to PDF."""
        fig, ax = self._setup_fig(is_mater=True)
        self.mater.draw(ax)
        plt.savefig(filename, format='pdf', dpi=dpi, bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_tympan(self, filename='Plate.pdf', dpi=300):
        """Draw and export the Tympan to PDF."""
        fig, ax = self._setup_fig()
        self.tympan.draw(ax)
        plt.savefig(filename, format='pdf', dpi=dpi, bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_rete(self, filename='Rete.pdf', dpi=300):
        """Draw and export the Rete to PDF."""
        fig, ax = self._setup_fig()
        self.rete.draw(ax)
        plt.savefig(filename, format='pdf', dpi=dpi, bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_rule(self, filename='Rule.pdf', dpi=300):
        """Draw and export the Rule to PDF."""
        fig, ax = self._setup_fig()
        self.rule.draw(ax)
        plt.savefig(filename, format='pdf', dpi=dpi, bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_back(self, filename='Back.pdf', dpi=300):
        """Draw and export the Back to PDF."""
        is_m = getattr(self.back, 'show_kursi', False)
        fig, ax = self._setup_fig(is_mater=is_m)
        self.back.draw(ax)
        plt.savefig(filename, format='pdf', dpi=dpi, bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_alidade(self, filename='Alidade.pdf', dpi=300):
        """Draw and export the Alidade to PDF."""
        fig, ax = self._setup_fig()
        self.alidade.draw(ax)
        plt.savefig(filename, format='pdf', dpi=dpi, bbox_inches='tight', transparent=True)
        plt.close(fig)

    # Native vector SVG export methods
    def plot_mater_svg(self, filename='Mater.svg'):
        """Draw and export the Mater directly to vector SVG."""
        fig, ax = self._setup_fig(is_mater=True)
        self.mater.draw(ax)
        plt.savefig(filename, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_tympan_svg(self, filename='Plate.svg'):
        """Draw and export the Tympan directly to vector SVG."""
        fig, ax = self._setup_fig()
        self.tympan.draw(ax)
        plt.savefig(filename, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_rete_svg(self, filename='Rete.svg'):
        """Draw and export the Rete directly to vector SVG."""
        fig, ax = self._setup_fig()
        self.rete.draw(ax)
        plt.savefig(filename, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_ecliptic_svg(self, filename='Ecliptic.svg'):
        """Draw and export only the Ecliptic (Zodiac ring) directly to vector SVG."""
        fig, ax = self._setup_fig()
        self.rete.ecliptic.draw(ax)
        plt.savefig(filename, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_rule_svg(self, filename='Rule.svg'):
        """Draw and export the Rule directly to vector SVG."""
        fig, ax = self._setup_fig()
        self.rule.draw(ax)
        plt.savefig(filename, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_back_svg(self, filename='Back.svg'):
        """Draw and export the Back directly to vector SVG."""
        is_m = getattr(self.back, 'show_kursi', False)
        fig, ax = self._setup_fig(is_mater=is_m)
        self.back.draw(ax)
        plt.savefig(filename, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_alidade_svg(self, filename='Alidade.svg'):
        """Draw and export the Alidade directly to vector SVG."""
        fig, ax = self._setup_fig()
        self.alidade.draw(ax)
        plt.savefig(filename, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)

    def plot_kursi_svg(self, filename='Kursi.svg'):
        """Draw and export the unified Kursi arch directly to vector SVG."""
        self.mater.kursi.plot_arch_svg(filename, side='front')

    def plot_kursi_front_svg(self, filename='KursiFront.svg'):
        """Draw and export the Kursi front arch directly to vector SVG."""
        self.mater.kursi.plot_arch_svg(filename, side='front')

    def plot_kursi_back_svg(self, filename='KursiBack.svg'):
        """Draw and export the Kursi back arch directly to vector SVG."""
        self.mater.kursi.plot_arch_svg(filename, side='back')

    def plot_mater_belly_svg(self, filename='MaterBelly.svg'):
        """Draw and export the Mater belly (compass rose, notch, drill mark) directly to vector SVG."""
        fig, ax = self._setup_fig()
        self.mater.draw_belly(ax)
        plt.savefig(filename, format='svg', bbox_inches='tight', transparent=True)
        plt.close(fig)

    def export_all(self, output_dir=None):
        """Export Mater, Plate, Rete, Rule, Back, Alidade to PDF and SVG in exports directory."""
        if output_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
            pdf_dir = os.path.join(project_root, 'exports', 'pdf')
            svg_dir = os.path.join(project_root, 'exports', 'svg')
        else:
            pdf_dir = os.path.join(output_dir, 'pdf') if os.path.isdir(os.path.join(output_dir, 'pdf')) else output_dir
            svg_dir = os.path.join(output_dir, 'svg') if os.path.isdir(os.path.join(output_dir, 'svg')) else output_dir
            
        os.makedirs(pdf_dir, exist_ok=True)
        os.makedirs(svg_dir, exist_ok=True)
        
        print(f"Exporting PDF components to: {pdf_dir}")
        self.plot_mater(os.path.join(pdf_dir, 'Mater.pdf'))
        self.plot_tympan(os.path.join(pdf_dir, 'Plate.pdf'))
        self.plot_rete(os.path.join(pdf_dir, 'Rete.pdf'))
        self.plot_rule(os.path.join(pdf_dir, 'Rule.pdf'))
        self.plot_back(os.path.join(pdf_dir, 'Back.pdf'))
        self.plot_alidade(os.path.join(pdf_dir, 'Alidade.pdf'))
        
        print(f"Exporting native vector SVG components to: {svg_dir}")
        self.plot_mater_svg(os.path.join(svg_dir, 'Mater.svg'))
        self.plot_mater_belly_svg(os.path.join(svg_dir, 'MaterBelly.svg'))
        self.plot_tympan_svg(os.path.join(svg_dir, 'Plate.svg'))
        self.plot_rete_svg(os.path.join(svg_dir, 'Rete.svg'))
        self.plot_ecliptic_svg(os.path.join(svg_dir, 'Ecliptic.svg'))
        self.plot_rule_svg(os.path.join(svg_dir, 'Rule.svg'))
        self.plot_back_svg(os.path.join(svg_dir, 'Back.svg'))
        self.plot_alidade_svg(os.path.join(svg_dir, 'Alidade.svg'))
        self.plot_kursi_svg(os.path.join(svg_dir, 'Kursi.svg'))
        self.plot_kursi_front_svg(os.path.join(svg_dir, 'KursiFront.svg'))
        self.plot_kursi_back_svg(os.path.join(svg_dir, 'KursiBack.svg'))

        # Automatically sync updated vector SVGs to web/assets and android assets (excluding standalone Kursi and Mater manufacturing files)
        svg_filenames = ['Plate.svg', 'Rete.svg', 'Ecliptic.svg', 'Rule.svg', 'Back.svg', 'Alidade.svg']
        web_assets = os.path.join(project_root, 'web', 'assets')
        if os.path.isdir(web_assets):
            for f in svg_filenames:
                src_f = os.path.join(svg_dir, f)
                if os.path.exists(src_f):
                    shutil.copyfile(src_f, os.path.join(web_assets, f))
            print(f"Synced latest vector SVGs to web app: {web_assets}")
            
        android_assets = os.path.join(project_root, 'android', 'app', 'src', 'main', 'assets')
        if os.path.isdir(android_assets):
            for f in svg_filenames:
                src_f = os.path.join(svg_dir, f)
                if os.path.exists(src_f):
                    shutil.copyfile(src_f, os.path.join(android_assets, f))
                    sub_f = os.path.join(android_assets, 'assets', f)
                    if os.path.isdir(os.path.dirname(sub_f)):
                        shutil.copyfile(src_f, sub_f)
            print(f"Synced latest vector SVGs to Android assets: {android_assets}")

    def export_screen_assets(self, web_dir=None, android_dir=None):
        """
        Export screen-optimized SVGs directly to web/assets/ and android/app/src/main/assets/.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        
        target_dirs = []
        if web_dir is not None:
            target_dirs.append(web_dir)
        else:
            w_dir = os.path.join(project_root, 'web', 'assets')
            if os.path.isdir(os.path.join(project_root, 'web')):
                os.makedirs(w_dir, exist_ok=True)
                target_dirs.append(w_dir)
                
        if android_dir is not None:
            target_dirs.append(android_dir)
        else:
            a_dir = os.path.join(project_root, 'android', 'app', 'src', 'main', 'assets')
            if os.path.isdir(a_dir):
                target_dirs.append(a_dir)
                a_sub = os.path.join(a_dir, 'assets')
                os.makedirs(a_sub, exist_ok=True)
                target_dirs.append(a_sub)

        print("Generating screen-optimized vector SVGs...")
        temp_dir = os.path.join(project_root, 'exports', 'svg')
        os.makedirs(temp_dir, exist_ok=True)
        pdf_dir = os.path.join(project_root, 'exports', 'pdf')
        os.makedirs(pdf_dir, exist_ok=True)
        
        svg_files = {
            'Plate.svg': lambda p: self.plot_tympan_svg(p),
            'Rete.svg': lambda p: self.plot_rete_svg(p),
            'Ecliptic.svg': lambda p: self.plot_ecliptic_svg(p),
            'Rule.svg': lambda p: self.plot_rule_svg(p),
            'Back.svg': lambda p: self.plot_back_svg(p),
            'Alidade.svg': lambda p: self.plot_alidade_svg(p)
        }
        
        pdf_files = {
            'Mater.pdf': lambda p: self.plot_mater(p),
            'Plate.pdf': lambda p: self.plot_tympan(p),
            'Rete.pdf': lambda p: self.plot_rete(p),
            'Rule.pdf': lambda p: self.plot_rule(p),
            'Back.pdf': lambda p: self.plot_back(p),
            'Alidade.pdf': lambda p: self.plot_alidade(p)
        }
        
        for name, generator in svg_files.items():
            tmp_path = os.path.join(temp_dir, name)
            print(f"  -> Rendering {name}...")
            generator(tmp_path)
            for d in target_dirs:
                dest = os.path.join(d, name)
                shutil.copyfile(tmp_path, dest)
                print(f"     Synced to {dest}")

        print("Generating matching high-resolution vector PDFs...")
        for name, generator in pdf_files.items():
            pdf_path = os.path.join(pdf_dir, name)
            print(f"  -> Rendering {name}...")
            generator(pdf_path)


# =============================================================================
# CLI EXECUTION & DEMONSTRATION
# =============================================================================

if __name__ == '__main__':
    screen = '--screen' in sys.argv
    astrolabe = Astrolabe(
        latitude=35.78,
        city="Tangier",
        language="arabic",
        numeral_system="western_arabic",
        screen_mode=screen
    )
    
    print("Generating Astrolabe with:")
    print(f"  - Latitude: {astrolabe.latitude_deg}° ({astrolabe.city})")
    print(f"  - Language: {astrolabe.language}")
    print(f"  - Numeral System: {astrolabe.numeral_system}")
    print(f"  - Screen Mode: {astrolabe.screen_mode}")
    if screen:
        print("Exporting Screen Assets to web and Android assets...")
        astrolabe.export_screen_assets()
    else:
        print("Exporting Astrolabe components (Mater, Plate, Rete, Rule, Back, Alidade)...")
        astrolabe.export_all()
    print("Astrolabe successfully generated!")