"""
Astrolabe Tympan (Plate) Components.
Renders the plate for specific observer latitudes, including Horizons, Almucantars,
Azimuths, Twilight curves, Prayer time arcs, Unequal Hours, Equal Hours Limbus, Kursi, and Mater.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe

from .arabic import ArabicFormatter
from .projection import StereographicProjection, CelestialCircles


class Horizon:
    """The True Horizon (Almucantar 0°)."""
    def __init__(self, lat_rad, proj, language='latin', screen_mode=False):
        self.lat = lat_rad
        self.proj = proj
        self.language = language
        self.screen_mode = screen_mode
        self.y_center = self.proj.R / np.tan(self.lat)
        self.radius = self.proj.R / np.sin(self.lat)

    def draw(self, ax, clip_circle=None, color='#8B0000', lw=1.8):
        c = plt.Circle((0, self.y_center), self.radius, color=color, fill=False, linewidth=lw if not self.screen_mode else lw * 1.25)
        if clip_circle:
            c.set_clip_path(clip_circle)
        ax.add_patch(c)
        
        # East / West labels curved along the Horizon arc
        is_ar = str(self.language).lower().startswith('ar')
        lbl_east = ArabicFormatter.reshape_text('المشرق') if is_ar else 'E'
        lbl_west = ArabicFormatter.reshape_text('المغرب') if is_ar else 'W'
        fs = 4.6 if self.screen_mode else 3.8
        stroke_w = 1.0
        
        x_east = -1.10
        if self.radius**2 > x_east**2:
            y_east = self.y_center - np.sqrt(self.radius**2 - x_east**2)
            rot_east = np.rad2deg(np.arctan(x_east / np.sqrt(self.radius**2 - x_east**2)))
            ax.text(x_east, y_east, lbl_east, fontsize=fs, fontweight='bold', color=color,
                    ha='center', va='center', rotation=rot_east, rotation_mode='anchor',
                    path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])
                    
        x_west = 1.10
        if self.radius**2 > x_west**2:
            y_west = self.y_center - np.sqrt(self.radius**2 - x_west**2)
            rot_west = np.rad2deg(np.arctan(x_west / np.sqrt(self.radius**2 - x_west**2)))
            ax.text(x_west, y_west, lbl_west, fontsize=fs, fontweight='bold', color=color,
                    ha='center', va='center', rotation=rot_west, rotation_mode='anchor',
                    path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])


class Almucantars:
    """
    Circles of constant altitude (almucantars) above the horizon.
    Includes 1° graduations with fine light lines, major circles labeled along meridian.
    """
    def __init__(self, lat_rad, proj, step_deg=1, major_step_deg=10, language='latin', numeral_system='latin', screen_mode=False):
        self.lat = lat_rad
        self.proj = proj
        self.step_deg = step_deg
        self.major_step_deg = major_step_deg
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode

    def draw(self, ax, clip_circle=None, color='#004488'):
        step = self.step_deg
        fs = 3.6 if self.screen_mode else 3.0
        stroke_w = 0.8
        
        for a_deg in range(step, 86, step):
            a = np.deg2rad(a_deg)
            denom = np.sin(self.lat) + np.sin(a)
            yc = self.proj.R * np.cos(self.lat) / denom
            r = self.proj.R * np.cos(a) / denom
            
            is_major_10 = (a_deg % self.major_step_deg == 0)
            is_med_5 = (a_deg % 5 == 0)
            
            if is_major_10:
                lw = 0.80 if self.screen_mode else 0.70
                alpha = 0.88
            elif is_med_5:
                lw = 0.42 if self.screen_mode else 0.36
                alpha = 0.58
            else:
                lw = 0.16 if self.screen_mode else 0.13
                alpha = 0.32
            
            c = plt.Circle((0, yc), r, color=color, fill=False, linewidth=lw, alpha=alpha)
            if clip_circle:
                c.set_clip_path(clip_circle)
            ax.add_patch(c)
            
            # Label major 10° degree indices along the meridian
            if is_major_10 and a_deg in [10, 20, 30, 40, 50, 60, 70, 80]:
                y_lbl = yc - r
                if np.abs(y_lbl) < self.proj.r_capricorn:
                    num_str = ArabicFormatter.format_number(a_deg, self.numeral_system)
                    lbl = f'{num_str}°' if self.numeral_system != 'abjad' else num_str
                    ax.text(0.015, y_lbl, lbl, fontsize=fs, fontweight='bold', color=color,
                            va='center', ha='left',
                            path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])


class AzimuthCircles:
    """
    Vertical circles converging at the Zenith across the full horizon.
    Includes 1° fine graduations, with degree numbering for tens only (العشرات فقط).
    """
    def __init__(self, lat_rad, proj, step_deg=1, language='latin', numeral_system='latin', screen_mode=False):
        self.lat = lat_rad
        self.proj = proj
        self.step_deg = step_deg
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode

    def draw(self, ax, clip_circle=None, color='#1E7B34'):
        altitudes = np.linspace(0.0, np.pi / 2.0, 300)
        step = self.step_deg
        fs_med = 2.8 if self.screen_mode else 2.4
        fs_major = 3.4 if self.screen_mode else 2.8
        stroke_w = 0.8
        
        for A_deg in range(-180, 181, step):
            if A_deg == 0:
                continue
            A = np.deg2rad(A_deg)
            xs, ys = self.proj.horizontal_to_xy(altitudes, A, self.lat)
            
            is_major_30 = (A_deg % 30 == 0)
            is_med_10 = (A_deg % 10 == 0)
            is_sub_5 = (A_deg % 5 == 0)
            
            if is_major_30:
                lw = 0.70 if self.screen_mode else 0.60
                alpha = 0.85
            elif is_med_10:
                lw = 0.42 if self.screen_mode else 0.35
                alpha = 0.62
            elif is_sub_5:
                lw = 0.25 if self.screen_mode else 0.20
                alpha = 0.42
            else:
                lw = 0.14 if self.screen_mode else 0.12
                alpha = 0.28
            
            line, = ax.plot(xs, ys, color=color, linewidth=lw, alpha=alpha)
            if clip_circle:
                line.set_clip_path(clip_circle)
                
            # Degree numbering for tens ONLY (الترقيم لدرجات العشرات فقط)
            if is_med_10:
                inside = np.hypot(xs, ys) <= self.proj.r_capricorn
                if np.any(inside):
                    xs_in = xs[inside]
                    ys_in = ys[inside]
                    deg_val = abs(A_deg)
                    if deg_val < 120:
                        idx = min(5, len(xs_in) - 1)
                    else:
                        idx = min(6, len(xs_in) - 1)
                    xl, yl = xs_in[idx], ys_in[idx]
                    
                    num_str = ArabicFormatter.format_number(deg_val, self.numeral_system)
                    lbl = f'{num_str}°' if str(self.numeral_system).lower() == 'latin' else num_str
                    ax.text(xl, yl, lbl, fontsize=fs_major if is_major_30 else fs_med,
                            color='#0E4B1F', ha='center', va='center',
                            fontweight='bold',
                            path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])


class Twilights:
    """The astronomical twilights (depressions below the horizon)."""
    def __init__(self, lat_rad, proj, language='latin', numeral_system='latin', screen_mode=False):
        self.lat = lat_rad
        self.proj = proj
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode
        
        is_ar = str(self.language).lower().startswith('ar')
        if is_ar:
            # In Islamic astronomy, Fajr (-19°) and Isha (-17°) represent the canonical dawn/dusk curves
            self.twilights = [
                (-5/6, ArabicFormatter.reshape_text('الأفق الحسي'), '#5C2D91'),
                # (-6, ArabicFormatter.reshape_text('الشفق المدني'), '#5C2D91'),
                # (-12, ArabicFormatter.reshape_text('الشفق البحري'), '#4A2373')
            ]
        else:
            self.twilights = [
                (-6, 'Civil -6°', '#5C2D91'),
                (-12, 'Naut -12°', '#4A2373'),
                (-18, 'Astro -18°', '#381759')
            ]

    def draw(self, ax, clip_circle=None):
        fs = 3.2 if self.screen_mode else 2.6
        stroke_w = 0.8
        for alt_deg, name, col in self.twilights:
            alt = np.deg2rad(alt_deg)
            denom = np.sin(self.lat) + np.sin(alt)
            yc = self.proj.R * np.cos(self.lat) / denom
            r = self.proj.R * np.cos(alt) / denom
            
            c = plt.Circle((0, yc), r, color=col, fill=False, linewidth=0.8 if self.screen_mode else 0.65, linestyle='--')
            if clip_circle:
                c.set_clip_path(clip_circle)
            ax.add_patch(c)
            
            # Label in the middle (central meridian below the horizon)
            x_lbl = 0.0
            y_lbl = yc - r
            if np.hypot(x_lbl, y_lbl) <= self.proj.r_capricorn * 0.96:
                ax.text(x_lbl, y_lbl, name, fontsize=fs, color=col,
                        fontweight='bold', ha='center', va='center',
                        path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])


class PrayerTimes:
    """
    Islamic prayer curves according to classical astronomical rules
    and the official Moroccan Ministry of Habous and Islamic Affairs standards:
    - Fajr (الفجر): Solar depression of -19° below horizon (dawn)
    - Shuruk (الشروق): Eastern horizon transit (0°)
    - Zawal / Dhuhr (الزوال / الظهر): Solar meridian transit (noon)
    - Asr (العصر): Maliki standard shadow curve (s = s_0 + 1)
    - Maghrib (المغرب): Western horizon transit (0°)
    - Isha (العشاء): Solar depression of -17° below horizon (nightfall)
    """
    def __init__(self, lat_rad, proj, language='latin', numeral_system='latin', screen_mode=False):
        self.lat = lat_rad
        self.proj = proj
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode

    def draw(self, ax, clip_circle=None):
        is_ar = str(self.language).lower().startswith('ar')
        fs_asr = 3.6 if self.screen_mode else 3.0
        fs_fajr = 3.2 if self.screen_mode else 2.6
        fs_zawal = 4.4 if self.screen_mode else 3.6
        stroke_w = 0.8
        
        # -------------------------------------------------------------
        # 1. Asr (العصر) - Afternoon Shadow Curve
        # -------------------------------------------------------------
        decs = np.linspace(-self.proj.eps, self.proj.eps, 80)
        a_noon = np.pi / 2.0 - np.abs(self.lat - decs)
        
        cot_asr = 1.0 / np.tan(a_noon) + 1.0
        a_asr = np.arctan(1.0 / cot_asr)
        cos_H_asr = (np.sin(a_asr) - np.sin(self.lat) * np.sin(decs)) / (np.cos(self.lat) * np.cos(decs))
        
        cos_H_asr = np.clip(cos_H_asr, -1.0, 1.0)
        valid = np.isfinite(cos_H_asr)
        if np.any(valid):
            H_asr = np.arccos(cos_H_asr[valid])
            r_asr = self.proj.R * np.tan((np.pi / 2.0 - decs[valid]) / 2.0)
            x_asr = r_asr * np.sin(H_asr)
            y_asr = r_asr * np.cos(H_asr)
            
            line, = ax.plot(x_asr, y_asr, color='#C05000', linewidth=1.1 if self.screen_mode else 0.95, linestyle='-.')
            if clip_circle:
                line.set_clip_path(clip_circle)
            mid = len(x_asr) // 2
            
            dx = x_asr[mid + 1] - x_asr[mid - 1]
            dy = y_asr[mid + 1] - y_asr[mid - 1]
            rot_asr = np.rad2deg(np.arctan2(dy, dx))
            if rot_asr < -90:
                rot_asr += 180
            elif rot_asr > 90:
                rot_asr -= 180
                
            lbl_asr = ArabicFormatter.reshape_text('العصر') if is_ar else 'Asr'
            ax.text(x_asr[mid], y_asr[mid], lbl_asr, fontsize=fs_asr, color='#C05000',
                    fontweight='bold', ha='center', va='center',
                    rotation=rot_asr, rotation_mode='anchor',
                    path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])

        # -------------------------------------------------------------
        # 2. Fajr (الفجر) - Morocco Official Ministry Standard (-19°)
        # -------------------------------------------------------------
        alt_f_deg = -19.0
        alt_f = np.deg2rad(alt_f_deg)
        denom_f = np.sin(self.lat) + np.sin(alt_f)
        yc_f = self.proj.R * np.cos(self.lat) / denom_f
        r_f = self.proj.R * np.cos(alt_f) / denom_f
        
        c_f = plt.Circle((0, yc_f), r_f, color='#0B4F6C', fill=False, linewidth=1.0 if self.screen_mode else 0.85, linestyle='--')
        if clip_circle:
            c_f.set_clip_path(clip_circle)
        ax.add_patch(c_f)
        
        # Label Fajr on eastern/morning side below horizon aligned with curve
        x_lf = -1.15
        if r_f**2 > x_lf**2:
            y_lf = yc_f - np.sqrt(r_f**2 - x_lf**2)
            if np.hypot(x_lf, y_lf) <= self.proj.r_capricorn * 0.96:
                rot_f = np.rad2deg(np.arctan(x_lf / np.sqrt(r_f**2 - x_lf**2)))
                if is_ar:
                    lbl_fajr = ArabicFormatter.reshape_text('الفجر (١٩°-)')
                else:
                    lbl_fajr = 'Fajr -19°'
                ax.text(x_lf, y_lf, lbl_fajr, fontsize=fs_fajr, color='#0B4F6C',
                        fontweight='bold', ha='center', va='center',
                        rotation=rot_f, rotation_mode='anchor',
                        path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])

        # -------------------------------------------------------------
        # 3. Isha (العشاء) - Morocco Official Ministry Standard (-17°)
        # -------------------------------------------------------------
        alt_i_deg = -17.0
        alt_i = np.deg2rad(alt_i_deg)
        denom_i = np.sin(self.lat) + np.sin(alt_i)
        yc_i = self.proj.R * np.cos(self.lat) / denom_i
        r_i = self.proj.R * np.cos(alt_i) / denom_i
        
        c_i = plt.Circle((0, yc_i), r_i, color='#5B2C6F', fill=False, linewidth=1.0 if self.screen_mode else 0.85, linestyle='--')
        if clip_circle:
            c_i.set_clip_path(clip_circle)
        ax.add_patch(c_i)
        
        # Label Isha on western/evening side below horizon aligned with curve
        x_li = 1.15
        if r_i**2 > x_li**2:
            y_li = yc_i - np.sqrt(r_i**2 - x_li**2)
            if np.hypot(x_li, y_li) <= self.proj.r_capricorn * 0.96:
                rot_i = np.rad2deg(np.arctan(x_li / np.sqrt(r_i**2 - x_li**2)))
                if is_ar:
                    lbl_isha = ArabicFormatter.reshape_text('العشاء (١٧°-)')
                else:
                    lbl_isha = 'Isha -17°'
                ax.text(x_li, y_li, lbl_isha, fontsize=fs_fajr, color='#5B2C6F',
                        fontweight='bold', ha='center', va='center',
                        rotation=rot_i, rotation_mode='anchor',
                        path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])

        # -------------------------------------------------------------
        # 4. Zawal / Dhuhr (الزوال / الظهر) - Solar Meridian Noon
        # -------------------------------------------------------------
        # Placed precisely in the middle of the upper meridian line (from center to rim)
        y_zawal = self.proj.r_capricorn * 0.5
        lbl_zawal = ArabicFormatter.reshape_text('الزوال') if is_ar else 'Midday'
        ax.text(0.0, y_zawal, lbl_zawal, fontsize=fs_zawal, color='#8B0000',
                fontweight='bold', ha='center', va='center',
                path_effects=[pe.withStroke(linewidth=1.5 if self.screen_mode else 1.1, foreground='white')])


class UnequalHours:
    """
    Temporal / planetary unequal hours:
    - Nocturnal unequal hours (12 hours of the night, below the horizon)
    - Diurnal unequal hours (12 hours of the day, above the horizon)
    """
    def __init__(self, lat_rad, proj, language='latin', numeral_system='latin', screen_mode=False):
        self.lat = lat_rad
        self.proj = proj
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode
        self.numerals = self._build_numerals()

    def _build_numerals(self):
        sys = str(self.numeral_system).lower().strip()
        if sys in ('abjad', 'jummal', 'hisab_al_jummal'):
            # Abjad 1 to 11
            return [ArabicFormatter.reshape_text(ArabicFormatter.to_jummal(i)) for i in range(1, 12)]
        elif sys in ('eastern_arabic', 'eastern', 'arabic_numerals', 'hindi', 'mashriqi'):
            return [ArabicFormatter.to_eastern_arabic(i) for i in range(1, 12)]
        else:
            return ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']

    def draw(self, ax, clip_circle=None, show_diurnal=False, show_nocturnal=True,
             diurnal_color='#6E2C00', nocturnal_color='#333333'):
        decs = np.linspace(-self.proj.eps, self.proj.eps, 80)
        cos_H0 = -np.tan(self.lat) * np.tan(decs)
        H0 = np.arccos(np.clip(cos_H0, -1.0, 1.0))
        r_k = self.proj.R * np.tan((np.pi / 2.0 - decs) / 2.0)
        fs_num = 3.6 if self.screen_mode else 3.0
        stroke_w = 0.8
        
        # 1. Diurnal (Daytime) Unequal Hours (الساعات النهارية غير المتساوية) - Above Horizon
        if show_diurnal:
            for k in range(1, 12):
                H_k = (k - 6) * H0 / 6.0
                x_k = r_k * np.sin(H_k)
                y_k = r_k * np.cos(H_k)
                
                # Draw arc for all daytime hours except meridian (which is already drawn)
                if k != 6:
                    line, = ax.plot(x_k, y_k, color=diurnal_color, linewidth=0.9 if self.screen_mode else 0.75,
                                    linestyle='-.', alpha=0.85)
                    if clip_circle:
                        line.set_clip_path(clip_circle)
                
                # Label along the Celestial Equator (dec = 0, index 40)
                idx = len(decs) // 2
                x_num = x_k[idx]
                y_num = y_k[idx]
                ax.text(x_num, y_num, self.numerals[k - 1], fontsize=fs_num, ha='center', va='center',
                        color=diurnal_color, fontweight='bold',
                        path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])

        # 2. Nocturnal (Nighttime) Unequal Hours (الساعات الليلية غير المتساوية) - Below Horizon
        if show_nocturnal:
            for k in range(1, 12):
                H_k = H0 + k * (np.pi - H0) / 6.0
                x_k = r_k * np.sin(H_k)
                y_k = r_k * np.cos(H_k)
                
                line, = ax.plot(x_k, y_k, color=nocturnal_color, linewidth=0.9 if self.screen_mode else 0.7, linestyle='-')
                if clip_circle:
                    line.set_clip_path(clip_circle)
                    
                # Label along the Celestial Equator (dec = 0)
                idx = len(decs) // 2
                x_num = x_k[idx]
                y_num = y_k[idx]
                ax.text(x_num, y_num, self.numerals[k - 1], fontsize=fs_num, ha='center', va='center',
                        color=nocturnal_color, fontweight='bold',
                        path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])


class EqualHoursLimbus:
    """The outer rim (limbus) graduations (Tangier Civil Time ring, 24 Equal Solar Hours, 360° Degree scale, empty Mater margin collar)."""
    def __init__(self, proj, language='latin', numeral_system='latin', latitude=None, screen_mode=False,
                 r_hours=None, r_outer=None):
        self.proj = proj
        self.language = language
        self.numeral_system = numeral_system
        self.latitude = latitude if latitude is not None else np.deg2rad(35.78)
        self.screen_mode = screen_mode
        self.r_cap = self.proj.r_capricorn
        self.r_inner = self.r_cap * 1.000
        self.r_mid1  = self.r_cap * 1.080  # 360° Degree scale
        self.r_mid2  = self.r_cap * 1.165  # 24 Equal Solar hours
        self.r_hours = r_hours if r_hours is not None else self.r_cap * 1.250  # 24 Civil Hours (Tangier GMT+0)
        self.r_outer = r_outer if r_outer is not None else self.r_cap * 1.330  # Empty Outer Collar of Mater (هامش الأم)

    def draw(self, ax, color='black', zorder=3):
        r_cap = self.r_cap
        r_inner = self.r_inner
        r_mid1  = self.r_mid1
        r_mid2  = self.r_mid2
        r_hours = self.r_hours
        r_outer = self.r_outer
        
        is_ar = str(self.language).lower().startswith('ar')
        
        # Outer concentric boundary rings
        # 1. Outer edge of Mater empty collar (هامش الأم)
        ax.add_patch(plt.Circle((0, 0), r_outer * 1.006, color='#0B3C5D', fill=False, linewidth=0.6, zorder=zorder))
        ax.add_patch(plt.Circle((0, 0), r_outer, color='#0B3C5D', fill=False, linewidth=2.0, zorder=zorder))
        # 2. Outer boundary of 24 Civil Hours (separating hours from the empty collar)
        ax.add_patch(plt.Circle((0, 0), r_hours, color='#0B3C5D', fill=False, linewidth=1.4, zorder=zorder))
        # 3. Intermediate scale rings
        ax.add_patch(plt.Circle((0, 0), r_mid2, color='#1A5276', fill=False, linewidth=1.1, zorder=zorder))
        ax.add_patch(plt.Circle((0, 0), r_mid1, color=color, fill=False, linewidth=0.8, zorder=zorder))
        ax.add_patch(plt.Circle((0, 0), r_inner, color=color, fill=False, linewidth=1.0, zorder=zorder))
        
        # Radial tick batch plotter for high-precision minute graduations
        def plot_radial_ticks(rad_angles, r_start, r_end, c, lw):
            if len(rad_angles) == 0:
                return
            s = np.sin(rad_angles)
            c_arr = np.cos(rad_angles)
            xs = np.empty((len(rad_angles), 3))
            ys = np.empty((len(rad_angles), 3))
            xs[:, 0] = r_start * s
            xs[:, 1] = r_end * s
            xs[:, 2] = np.nan
            ys[:, 0] = r_start * c_arr
            ys[:, 1] = r_end * c_arr
            ys[:, 2] = np.nan
            ax.plot(xs.flatten(), ys.flatten(), color=c, linewidth=lw, solid_capstyle='butt', zorder=zorder)

        # -------------------------------------------------------------
        # 1. 24 TANGIER CIVIL HOURS (طوق التوقيت المدني لطنجة GMT+0)
        # -------------------------------------------------------------
        # Longitude of Tangier: 5°49' W = 5.81° W. Morocco Civil Standard Time: UTC+0 (+0° E).
        # Offset between local solar noon and civil noon: 0° - (-5.81°) = 5.81° = 23m 14s.
        offset_deg = 5.81
        band_civ = r_hours - r_mid2
        
        # 1440 minute graduations across the 24 civil hours
        all_mins = np.arange(1440)
        rad_civ = np.deg2rad(all_mins * 0.25 - offset_deg)

        # - 1-minute ticks (كل دقيقة)
        m_1m = (all_mins % 5 != 0)
        plot_radial_ticks(rad_civ[m_1m], r_hours - band_civ * 0.08, r_hours,
                          '#7FB3D5', 0.26 if self.screen_mode else 0.20)
        # - 5-minute ticks (كل ٥ دقائق)
        m_5m = (all_mins % 5 == 0) & (all_mins % 15 != 0)
        plot_radial_ticks(rad_civ[m_5m], r_hours - band_civ * 0.15, r_hours,
                          '#5499C7', 0.42 if self.screen_mode else 0.35)
        # - 15-minute ticks (كل ربع ساعة)
        m_15m = (all_mins % 15 == 0) & (all_mins % 30 != 0)
        plot_radial_ticks(rad_civ[m_15m], r_hours - band_civ * 0.25, r_hours,
                          '#2980B9', 0.58 if self.screen_mode else 0.50)
        # - 30-minute ticks (نصف ساعة)
        m_30m = (all_mins % 60 == 30)
        plot_radial_ticks(rad_civ[m_30m], r_hours - band_civ * 0.40, r_hours,
                          '#1B4F72', 0.80 if self.screen_mode else 0.70)
        # - 1-hour major lines (خطوط الساعات الرئيسية)
        m_60m = (all_mins % 60 == 0)
        plot_radial_ticks(rad_civ[m_60m], r_mid2, r_hours,
                          '#0E3A5D', 1.20 if self.screen_mode else 1.05)

        # Format numerals for 12-hour civil system (two 12-hour cycles)
        sys_num = str(self.numeral_system).lower().strip()
        if sys_num in ('abjad', 'jummal', 'hisab_al_jummal'):
            hours_12 = ['ا', 'ب', 'ج', 'د', 'ه', 'و', 'ز', 'ح', 'ط', 'ي', 'يا', 'يب']
            civ_labels = [ArabicFormatter.reshape_text(h) for h in (hours_12 * 2)]
        elif sys_num in ('eastern_arabic', 'eastern', 'arabic_numerals', 'hindi', 'mashriqi'):
            hours_12 = ['١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩', '١٠', '١١', '١٢']
            civ_labels = hours_12 * 2
        else:
            civ_labels = [str((h - 1) % 12 + 1) for h in range(1, 25)]

        for h_val in range(1, 25):
            deg_civ_lbl = ((h_val - 1) * 15.0 + 7.5) - offset_deg
            th_mid = np.deg2rad(deg_civ_lbl)
            r_lbl = r_mid2 + band_civ * 0.38
            col_txt = '#7D6608' if 6 <= h_val < 18 else '#1B4F72'
            fs_civ = 8.5 if self.screen_mode else 7.8
            ax.text(r_lbl * np.sin(th_mid), r_lbl * np.cos(th_mid), civ_labels[h_val - 1],
                    fontsize=fs_civ, fontweight='bold', color=col_txt,
                    ha='center', va='center', rotation=-np.rad2deg(th_mid), rotation_mode='anchor',
                    path_effects=[pe.withStroke(linewidth=1.4 if self.screen_mode else 1.1, foreground='white')],
                    zorder=zorder + 1)

        # Civil Noon (الزوال المدني) in the empty margin of the Mater (هامش الأم)
        th_noon = np.deg2rad(-offset_deg)
        noon_str = ArabicFormatter.reshape_text("الزوال المدني") if is_ar else "Civil Noon"
        fs_noon = 6.0 if self.screen_mode else 5.2
        # Center the text inside the margin band between r_hours and r_outer:
        r_noon_txt = r_hours + 0.048 * r_cap
        ax.text(r_noon_txt * np.sin(th_noon), r_noon_txt * np.cos(th_noon), noon_str,
                fontsize=fs_noon, fontweight='bold', color='#B7950B', ha='center', va='center',
                rotation=-np.rad2deg(th_noon), rotation_mode='anchor',
                path_effects=[pe.withStroke(linewidth=1.2 if self.screen_mode else 1.0, foreground='white')],
                zorder=zorder + 1)
        # Golden fiducial triangle in the margin pointing to the civil noon tick on r_hours
        tri_tip_r = r_hours + 0.003 * r_cap
        tri_base_r = r_hours + 0.020 * r_cap
        tri_w = np.deg2rad(0.95)
        t_xs = [tri_tip_r * np.sin(th_noon),
                tri_base_r * np.sin(th_noon - tri_w),
                tri_base_r * np.sin(th_noon + tri_w)]
        t_ys = [tri_tip_r * np.cos(th_noon),
                tri_base_r * np.cos(th_noon - tri_w),
                tri_base_r * np.cos(th_noon + tri_w)]
        ax.fill(t_xs, t_ys, color='#B7950B', zorder=zorder + 1)
                
        # Outer Rim Title Banner (طوق التوقيت المدني لطنجة GMT+0)
        title_str = ArabicFormatter.reshape_text("طوق التوقيت المدني لطنجة (GMT+0)") if is_ar else "Civil Time - Tangier (GMT+0)"
        fs_title = 8.5 if self.screen_mode else 7.8
        ax.text(0, -r_outer - 0.022 * r_cap, title_str, fontsize=fs_title, fontweight='bold', color='#0B3C5D',
                ha='center', va='top', path_effects=[pe.withStroke(linewidth=1.5 if self.screen_mode else 1.2, foreground='white')],
                zorder=zorder + 1)

        # -------------------------------------------------------------
        # 2. 24 EQUAL SOLAR HOURS (الساعات المستوية الشمسية) (r_mid1 to r_mid2)
        # -------------------------------------------------------------
        band_solar = r_mid2 - r_mid1
        rad_solar = np.deg2rad(all_mins * 0.25)

        # - 1-minute ticks (كل دقيقة)
        plot_radial_ticks(rad_solar[m_1m], r_mid2 - band_solar * 0.065, r_mid2,
                          color, 0.24 if self.screen_mode else 0.18)
        # - 5-minute ticks (كل ٥ دقائق)
        plot_radial_ticks(rad_solar[m_5m], r_mid2 - band_solar * 0.13, r_mid2,
                          color, 0.38 if self.screen_mode else 0.30)
        # - 15-minute ticks (كل ربع ساعة)
        plot_radial_ticks(rad_solar[m_15m], r_mid2 - band_solar * 0.22, r_mid2,
                          color, 0.52 if self.screen_mode else 0.42)
        # - 30-minute ticks (نصف ساعة)
        plot_radial_ticks(rad_solar[m_30m], r_mid2 - band_solar * 0.36, r_mid2,
                          color, 0.70 if self.screen_mode else 0.58)
        # - 1-hour major lines (خطوط الساعات الرئيسية)
        plot_radial_ticks(rad_solar[m_60m], r_mid1, r_mid2,
                          color, 0.95 if self.screen_mode else 0.85)

        sys_num = str(self.numeral_system).lower().strip()
        if sys_num in ('abjad', 'jummal', 'hisab_al_jummal'):
            hours_12 = ['ا', 'ب', 'ج', 'د', 'ه', 'و', 'ز', 'ح', 'ط', 'ي', 'يا', 'يب']
            solar_labels = [ArabicFormatter.reshape_text(h) for h in (hours_12 * 2)]
        elif sys_num in ('eastern_arabic', 'eastern', 'arabic_numerals', 'hindi', 'mashriqi'):
            hours_12 = ['١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩', '١٠', '١١', '١٢']
            solar_labels = hours_12 * 2
        else:
            hours_12 = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
            solar_labels = hours_12 * 2
            
        fs_solar = 8.5 if self.screen_mode else 7.8
        for h in range(24):
            deg = h * 15.0
            th_mid = np.deg2rad(deg + 7.5)
            r_lbl = r_mid1 + band_solar * 0.35
            ax.text(r_lbl * np.sin(th_mid), r_lbl * np.cos(th_mid), solar_labels[h],
                    fontsize=fs_solar, fontweight='bold', color='#333333', ha='center', va='center',
                    rotation=-(deg + 7.5), rotation_mode='anchor',
                    path_effects=[pe.withStroke(linewidth=1.4 if self.screen_mode else 1.1, foreground='white')])

        # -------------------------------------------------------------
        # 3. 360 DEGREE TICKS (r_inner to r_mid1)
        # -------------------------------------------------------------
        fs_deg = 5.8 if self.screen_mode else 5.0
        band_deg = r_mid1 - r_inner
        for deg in range(360):
            th = np.deg2rad(deg)
            sin_t, cos_t = np.sin(th), np.cos(th)
            if deg % 10 == 0:
                l_in = r_inner
                l_out = r_mid1
                deg_in_quad = deg % 90
                if deg_in_quad == 0 and deg in (90, 270):
                    deg_in_quad = 90
                num_str = ArabicFormatter.format_number(deg_in_quad, self.numeral_system)
                ax.text((r_inner + band_deg * 0.45) * sin_t, (r_inner + band_deg * 0.45) * cos_t, num_str,
                        fontsize=fs_deg, ha='center', va='center', fontweight='bold',
                        rotation=-deg, rotation_mode='anchor',
                        path_effects=[pe.withStroke(linewidth=1.0 if self.screen_mode else 0.8, foreground='white')])
            elif deg % 5 == 0:
                l_in = r_mid1 - band_deg * 0.45
                l_out = r_mid1
            else:
                l_in = r_mid1 - band_deg * 0.25
                l_out = r_mid1
            ax.plot([l_in * sin_t, l_out * sin_t], [l_in * cos_t, l_out * cos_t],
                    color=color, linewidth=0.35)


# =============================================================================
# ASTROLABE THRONE (KURSI / العرش أو الكرسي) & MATER (UMM / الأم والحجرة)
# =============================================================================

class Kursi:
    """
    Classical Islamic Astrolabe Throne (العرش / الكرسي).
    Sculpted multi-lobed arch attached to the top of the Mater and Back,
    featuring the suspension eyelet (العروة والحلقة) and authentic calligraphic inscriptions.
    """
    def __init__(self, proj, city="Tangier", language="arabic", screen_mode=False, r_outer=None):
        self.proj = proj
        self.city = city
        self.language = language
        self.screen_mode = screen_mode
        self.r_cap = proj.r_capricorn
        self.r_outer = r_outer if r_outer is not None else self.r_cap * 1.330
        
        # Base transition angle (34 degrees on each side of the vertical meridian)
        self.theta_base = np.deg2rad(34.0)
        self.x_base = self.r_outer * np.sin(self.theta_base)
        self.y_base = self.r_outer * np.cos(self.theta_base)
        
        # Eyelet coordinates at the apex
        self.y_eye = self.r_outer + 0.44 * self.r_cap
        self.r_eye_outer = 0.12 * self.r_cap
        self.r_eye_hole = 0.055 * self.r_cap
        
        self.pts_right, self.pts_left = self._build_kursi_lobes(offset_scale=1.0, y_shift=0.0)
        self.pts_in_r, self.pts_in_l = self._build_kursi_lobes(offset_scale=0.91, y_shift=-0.015 * self.r_cap)
        
        # Full perimeter combining circular base arc and Kursi
        circ_angles = np.linspace(np.pi / 2.0 - self.theta_base, -1.5 * np.pi + self.theta_base, 400)
        pts_circ = np.column_stack([self.r_outer * np.cos(circ_angles), self.r_outer * np.sin(circ_angles)])
        self.full_outline = np.vstack([pts_circ, self.pts_right, self.pts_left[::-1]])

    def _build_kursi_lobes(self, offset_scale=1.0, y_shift=0.0):
        xb = self.x_base * offset_scale
        yb = self.y_base * offset_scale + y_shift
        ye = self.y_eye * offset_scale + y_shift
        reo = self.r_eye_outer * offset_scale
        r_c = self.r_cap * offset_scale
        
        pts_r = []
        pts_r.append((xb, yb))
        
        # Lobe 1 (Bottom scallop)
        for a in np.linspace(-np.pi * 0.4, np.pi * 0.45, 25):
            xc1 = xb * 0.88
            yc1 = yb + 0.08 * r_c
            rx1 = 0.16 * r_c
            ry1 = 0.10 * r_c
            pts_r.append((xc1 + rx1 * np.cos(a), yc1 + ry1 * np.sin(a)))
            
        # Cusp 1
        pts_r.append((xb * 0.66, yb + 0.16 * r_c))
        
        # Lobe 2 (Middle scallop)
        for a in np.linspace(-np.pi * 0.4, np.pi * 0.45, 25):
            xc2 = xb * 0.52
            yc2 = yb + 0.23 * r_c
            rx2 = 0.14 * r_c
            ry2 = 0.09 * r_c
            pts_r.append((xc2 + rx2 * np.cos(a), yc2 + ry2 * np.sin(a)))
            
        # Cusp 2
        pts_r.append((xb * 0.32, yb + 0.30 * r_c))
        
        # Lobe 3 (Top scallop)
        for a in np.linspace(-np.pi * 0.35, np.pi * 0.40, 25):
            xc3 = xb * 0.20
            yc3 = yb + 0.35 * r_c
            rx3 = 0.11 * r_c
            ry3 = 0.08 * r_c
            pts_r.append((xc3 + rx3 * np.cos(a), yc3 + ry3 * np.sin(a)))
            
        # Arc to apex circular eyelet
        for a in np.linspace(np.deg2rad(15), np.pi / 2.0, 18):
            pts_r.append((reo * np.cos(a), ye + reo * np.sin(a)))
            
        pts_r = np.array(pts_r)
        pts_l = np.column_stack([-pts_r[:, 0], pts_r[:, 1]])
        return pts_r, pts_l

    def draw(self, ax, side='front', color='#0B3C5D', zorder=1):
        """Draws the Kursi throne arch behind the astrolabe, styled like the website version."""
        is_ar = str(self.language).lower().startswith('ar')
        r_c = self.r_cap
        
        # 1. Closed polygon for solid brass fill extending slightly behind the outer ring
        th_base_arc = np.linspace(np.pi/2 - self.theta_base, np.pi/2 + self.theta_base, 100)
        pts_base_arc = np.column_stack([0.98 * self.r_outer * np.cos(th_base_arc), 0.98 * self.r_outer * np.sin(th_base_arc)])
        kursi_poly = np.vstack([pts_base_arc[::-1], self.pts_right, self.pts_left[::-1]])
        
        # Fill with warm antique brass color matching the website version
        ax.fill(kursi_poly[:, 0], kursi_poly[:, 1], color='#e2bf65', edgecolor=color, linewidth=2.0, zorder=zorder)
        
        # 2. Suspension eyelet (through-hole on the Kursi arch)
        ax.add_patch(plt.Circle((0, self.y_eye), self.r_eye_hole, color='#140d07', fill=True, zorder=zorder + 0.2))
        ax.add_patch(plt.Circle((0, self.y_eye), self.r_eye_hole, color=color, fill=False, linewidth=2.0, zorder=zorder + 0.3))

    def draw_arch(self, ax, side='front', color='#0B3C5D', zorder=1):
        """Alias for draw."""
        return self.draw(ax, side=side, color=color, zorder=zorder)

    def plot_arch_svg(self, filename, side='front'):
        """Draw and export the Kursi arch directly to vector SVG with exact point matching."""
        r_c = self.r_cap
        y_min = 1.05 * r_c
        y_max = 2.25 * r_c
        h_range = y_max - y_min
        
        w_pt = 568.8
        scale = w_pt / (2.90 * r_c)
        h_pt = h_range * scale
        fig_w_in = w_pt / 72.0
        fig_h_in = h_pt / 72.0
        
        fig = plt.figure(figsize=(fig_w_in, fig_h_in))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_aspect('equal')
        ax.set_xlim(-1.45 * r_c, 1.45 * r_c)
        ax.set_ylim(y_min, y_max)
        ax.axis('off')
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        self.draw(ax, side=side, color='#0B3C5D')
        
        plt.savefig(filename, format='svg', transparent=True)
        plt.close(fig)


class Mater:
    """
    Master representation of the Mater (أم الأسطرلاب / الحجرة والعرش).
    The physical chassis housing the interchangeable tympan plates and supporting
    the graduated limbus rings and suspension throne.
    """
    def __init__(self, proj=None, latitude=35.78, city="Tangier",
                 language="arabic", numeral_system="abjad", screen_mode=False):
        self.proj = proj or StereographicProjection()
        self.latitude_deg = float(latitude)
        self.latitude = np.deg2rad(self.latitude_deg)
        self.city = city
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode
        self.r_cap = self.proj.r_capricorn
        self.r_hours = self.r_cap * 1.250
        self.r_outer = self.r_cap * 1.330
        self.limbus = EqualHoursLimbus(self.proj, language=self.language,
                                       numeral_system=self.numeral_system,
                                       latitude=self.latitude, screen_mode=self.screen_mode,
                                       r_hours=self.r_hours, r_outer=self.r_outer)
        self.kursi = Kursi(self.proj, city=self.city, language=self.language,
                           screen_mode=self.screen_mode, r_outer=self.r_outer)

    def draw(self, ax, color='#0B3C5D'):
        # 1. Kursi throne arch rendered behind the astrolabe
        self.kursi.draw(ax, side='front', color=color, zorder=1)
        # 2. Circular astrolabe body (Mater & Limbus) in front
        self.draw_belly(ax, color=color, zorder_base=2)

    def draw_belly(self, ax, color='#0B3C5D', zorder_base=2):
        """Draws the Mater belly (compass rose, notch, pivot drill) and surrounding Limbus in a square canvas."""
        is_ar = str(self.language).lower().startswith('ar')
        
        # 0. Solid circular backing disk placing the astrolabe in front of the Kursi
        ax.add_patch(plt.Circle((0, 0), self.r_outer, facecolor='#fcf4db' if self.screen_mode else '#faf3de',
                                edgecolor='none', zorder=zorder_base))
        
        # 1. Complete 360° outer rim circle in front of the Kursi
        ax.add_patch(plt.Circle((0, 0), self.r_outer, color=color, fill=False, linewidth=2.2, zorder=zorder_base + 1))
        
        # 2. Graduated Limbus rings (Hours & Degrees & Empty Collar)
        self.limbus.draw(ax, color=color, zorder=zorder_base + 2)
        
        # 3. Inner recess (Belly of the Mater - قاع الحجرة) where plates drop in
        ax.add_patch(plt.Circle((0, 0), self.r_cap, color='#8B0000', fill=False, linewidth=1.4, zorder=zorder_base + 2))
        
        # 4. Alignment key notch / lug at (0, r_cap)
        notch_w = 0.035 * self.r_cap
        notch_h = 0.025 * self.r_cap
        rect = patches.Rectangle((-notch_w / 2.0, self.r_cap - notch_h / 2.0), notch_w, notch_h, 
                                 color='#8B0000', fill=True)
        ax.add_patch(rect)
        
        # 5. Center pivot drill mark (Ø 3mm) & crosshair
        ax.plot([-0.06 * self.r_cap, 0.06 * self.r_cap], [0, 0], color='black', linewidth=0.8)
        ax.plot([0, 0], [-0.06 * self.r_cap, 0.06 * self.r_cap], color='black', linewidth=0.8)
        ax.add_patch(plt.Circle((0, 0), 0.02 * self.r_cap, color='black', fill=False, linewidth=0.9))
        ax.text(0.035, -0.035, 'Ø 3mm', fontsize=5.5 if self.screen_mode else 4.5, color='#444444')
        
        # 6. Belly Inscriptions: Classical 16-wind compass rose & Mater designation
        lbl_mater = ArabicFormatter.reshape_text('أم الأسطرلاب - الحجرة') if is_ar else 'Mater (Astrolabe Body)'
        ax.text(0, -0.30 * self.r_cap, lbl_mater, fontsize=12 if self.screen_mode else 10,
                color='#1A5276', ha='center', va='center', fontweight='bold', alpha=0.75)
        
        cardinals = [
            (0, 'المشرق' if is_ar else 'East'),
            (90, 'الشمال' if is_ar else 'North'),
            (180, 'المغرب' if is_ar else 'West'),
            (270, 'الجنوب' if is_ar else 'South')
        ]
        for deg, name in cardinals:
            rad = np.deg2rad(deg)
            r_pos = self.r_cap * 0.72
            x_c = r_pos * np.cos(rad)
            y_c = r_pos * np.sin(rad)
            t_str = ArabicFormatter.reshape_text(name) if is_ar else name
            ax.text(x_c, y_c, t_str, fontsize=7.5 if self.screen_mode else 6.5,
                    color='#666666', ha='center', va='center', fontweight='bold')
            ax.plot([0, r_pos * 0.84 * np.cos(rad)], [0, r_pos * 0.84 * np.sin(rad)],
                    color='#B0C4DE', linewidth=0.7, linestyle='-')
            
        for deg in [45, 135, 225, 315]:
            rad = np.deg2rad(deg)
            r_pos = self.r_cap * 0.58
            ax.plot([0, r_pos * np.cos(rad)], [0, r_pos * np.sin(rad)],
                    color='#E0E0E0', linewidth=0.5, linestyle='--')


class Tympan:
    """The Astrolabe Tympan (Plate) for a given observer latitude."""
    def __init__(self, latitude=35.78, city="Tangier", proj=None, 
                 language='latin', numeral_system='latin', screen_mode=False):
        self.city = city
        self.latitude_deg = float(latitude)
        self.latitude = np.deg2rad(self.latitude_deg)
        self.proj = proj or StereographicProjection()
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode
        
        # Sub-components with screen_mode support
        self.celestial_circles = CelestialCircles(self.proj)
        self.horizon = Horizon(self.latitude, self.proj, language=self.language, screen_mode=self.screen_mode)
        self.almucantars = Almucantars(self.latitude, self.proj, step_deg=1, major_step_deg=10,
                                       language=self.language, numeral_system=self.numeral_system, screen_mode=self.screen_mode)
        self.azimuths = AzimuthCircles(self.latitude, self.proj, step_deg=1,
                                       language=self.language, numeral_system=self.numeral_system, screen_mode=self.screen_mode)
        self.twilights = Twilights(self.latitude, self.proj, language=self.language,
                                   numeral_system=self.numeral_system, screen_mode=self.screen_mode)
        self.prayer_times = PrayerTimes(self.latitude, self.proj, language=self.language,
                                        numeral_system=self.numeral_system, screen_mode=self.screen_mode)
        self.unequal_hours = UnequalHours(self.latitude, self.proj, language=self.language,
                                          numeral_system=self.numeral_system, screen_mode=self.screen_mode)
        self.limbus = EqualHoursLimbus(self.proj, language=self.language, numeral_system=self.numeral_system,
                                       latitude=self.latitude, screen_mode=self.screen_mode)

    def draw(self, ax, show_almucantars=True, show_azimuths=True, 
             show_twilights=True, show_prayers=True, show_unequal_hours=True, 
             show_limbus=True, show_diurnal_hours=False, show_nocturnal_hours=True):
        """Render all tympan components onto ax."""
        clip_circle = plt.Circle((0, 0), self.proj.r_capricorn, transform=ax.transData)
        r_cap = self.proj.r_capricorn
        
        # Meridian & East-West axes
        ax.plot([0, 0], [-r_cap, r_cap], color='#444444', linewidth=0.6)
        ax.plot([-r_cap, r_cap], [0, 0], color='#444444', linewidth=0.6)
        
        self.celestial_circles.draw(ax)
        self.horizon.draw(ax, clip_circle=clip_circle)
        
        if show_almucantars:
            self.almucantars.draw(ax, clip_circle=clip_circle)
        if show_azimuths:
            self.azimuths.draw(ax, clip_circle=clip_circle)
        if show_twilights:
            self.twilights.draw(ax, clip_circle=clip_circle)
        if show_prayers:
            self.prayer_times.draw(ax, clip_circle=clip_circle)
        if show_unequal_hours:
            self.unequal_hours.draw(ax, clip_circle=clip_circle,
                                    show_diurnal=show_diurnal_hours,
                                    show_nocturnal=show_nocturnal_hours)
        if show_limbus:
            self.limbus.draw(ax)
            
        # Center pin & Zenith mark (on positive y-axis, top)
        ax.plot(0, 0, 'k+', markersize=6, markeredgewidth=0.8)
        ax.add_patch(plt.Circle((0, 0), 0.02 * r_cap, color='black', fill=False, linewidth=0.6, linestyle=':'))
        
        # Registration key notch at top rim (0, r_cap) to physically key into Mater
        notch_w = 0.035 * r_cap
        notch_h = 0.025 * r_cap
        rect_notch = patches.Rectangle((-notch_w / 2.0, r_cap - notch_h), notch_w, notch_h, 
                                       color='#8B0000', fill=False, linewidth=1.0)
        ax.add_patch(rect_notch)
        
        y_zenith = self.proj.R * np.tan((np.pi / 2.0 - self.latitude) / 2.0)
        ax.plot(0, y_zenith, 'ro', markersize=3)
        
        is_ar = str(self.language).lower().startswith('ar')
        zenith_str = ArabicFormatter.reshape_text('سمت الرأس') if is_ar else 'Zenith'
        fs_zenith = 3.6 if self.screen_mode else 3.0
        stroke_zenith = 0.8
        ax.text(0.04, y_zenith, zenith_str, fontsize=fs_zenith, color='#8B0000', va='center',
                path_effects=[pe.withStroke(linewidth=stroke_zenith, foreground='white')])
                
        # City & Latitude designation (shifted up with 80% opacity)
        if is_ar:
            # City localization
            city_ar = 'طنجة' if 'tangier' in self.city.lower() or 'طنجة' in self.city else self.city
            sys = str(self.numeral_system).lower().strip()
            if sys in ('abjad', 'jummal', 'hisab_al_jummal'):
                lat_int = int(round(self.latitude_deg))
                lat_str = ArabicFormatter.to_jummal(lat_int)
                city_label_raw = f"{city_ar} عرض {lat_str}° شمال"
            elif sys in ('eastern_arabic', 'eastern', 'arabic_numerals', 'hindi', 'mashriqi'):
                lat_str = ArabicFormatter.to_eastern_arabic(round(self.latitude_deg, 2))
                city_label_raw = f"{city_ar} عرض {lat_str}° شمال"
            else:
                city_label_raw = f"{city_ar} عرض {self.latitude_deg:g}° شمال"
            city_label = ArabicFormatter.reshape_text(city_label_raw)
        else:
            city_label = f'{self.city} {self.latitude_deg:g}° N'
            
        fs_city = 4.8 if self.screen_mode else 4.0
        stroke_city = 1.0
        ax.text(0, -self.proj.r_capricorn * 0.82, city_label,
                fontsize=fs_city, ha='center', va='center', fontweight='bold', color='#222222',
                alpha=0.9,
                path_effects=[pe.withStroke(linewidth=stroke_city, foreground='white', alpha=0.9)])


