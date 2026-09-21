"""
Astrolabe Rete (Spider) Components.
Models the rotatable star map, ecliptic zodiac circle, star pointers, and authentic fretwork.
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe

from .arabic import ArabicFormatter
from .projection import StereographicProjection


class Ecliptic:
    """The eccentric ecliptic circle containing astronomical graduations."""
    def __init__(self, proj, language='latin', numeral_system='latin', screen_mode=False):
        self.proj = proj
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode
        self.y_center = -self.proj.R * np.tan(self.proj.eps)
        self.radius = self.proj.R / np.cos(self.proj.eps)
        
        is_ar = str(self.language).lower().startswith('ar')
        if is_ar:
            raw_zodiac = [
                'الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'السنبلة',
                'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت'
            ]
            self.zodiac_names = [ArabicFormatter.reshape_text(z) for z in raw_zodiac]
            
            raw_months = [
                ('يناير', 31), ('فبراير', 28), ('مارس', 31), ('أبريل', 30),
                ('مايو', 31), ('يونيو', 30), ('يوليو', 31), ('أغسطس', 31),
                ('سبتمبر', 30), ('أكتوبر', 31), ('نوفمبر', 30), ('ديسمبر', 31)
            ]
            self.months = [(ArabicFormatter.reshape_text(m), d) for m, d in raw_months]

            raw_mansions = [
                'الشرطان', 'البطين', 'الثريا', 'الدبران', 'الهقعة', 'الهنعة', 'الذراع',
                'النثرة', 'الطرف', 'الجبهة', 'الزبرة', 'الصرفة', 'العواء', 'السماك',
                'الغفر', 'الزبانى', 'الإكليل', 'القلب', 'الشولة', 'النعائم', 'البلدة',
                'سعد الذابح', 'سعد بلع', 'سعد السعود', 'سعد الأخبية', 'المقدم', 'المؤخر', 'الرشاء'
            ]
            self.mansions = [ArabicFormatter.reshape_text(m) for m in raw_mansions]
        else:
            self.zodiac_names = [
                'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagitt.', 'Capric.', 'Aquar.', 'Pisces'
            ]
            self.months = [
                ('JAN', 31), ('FEB', 28), ('MAR', 31), ('APR', 30),
                ('MAY', 31), ('JUN', 30), ('JUL', 31), ('AUG', 31),
                ('SEP', 30), ('OCT', 31), ('NOV', 30), ('DEC', 31)
            ]
            self.mansions = [
                'Sharatan', 'Butayn', 'Thurayya', 'Dabaran', 'Haqah', 'Hanah', 'Dhira',
                'Nathrah', 'Tarf', 'Jabhah', 'Zubrah', 'Sarfah', 'Awwa', 'Simak',
                'Ghafr', 'Zubana', 'Iklil', 'Qalb', 'Shawlah', 'Naayem', 'Baldah',
                'Saad Dhabih', 'Saad Bula', 'Saad Saud', 'Saad Akhbiah', 'Muqaddam', 'Muakhar', 'Risha'
            ]

    def _ecl_to_xy(self, lon_rad):
        sin_d = np.sin(self.proj.eps) * np.sin(lon_rad)
        dec = np.arcsin(sin_d)
        ra = np.arctan2(np.cos(self.proj.eps) * np.sin(lon_rad), np.cos(lon_rad))
        r = self.proj.R * np.tan((np.pi / 2.0 - dec) / 2.0)
        return r * np.cos(ra), r * np.sin(ra)

    def draw(self, ax, color='#8B0000'):
        r0 = self.radius
        r1 = self.radius * 0.968
        r2 = self.radius * 0.936

        ax.add_patch(plt.Circle((0, self.y_center), r0, color=color, fill=False, linewidth=1.3, zorder=5))
        ax.add_patch(plt.Circle((0, self.y_center), r1, color='#555555', fill=False, linewidth=0.5, zorder=5))
        ax.add_patch(plt.Circle((0, self.y_center), r2, color=color, fill=False, linewidth=1.3, zorder=5))

        # 1. Calendar Track (Months & Days)
        accum_day = 0
        for name, num_days in self.months:
            lon_s = np.deg2rad(((accum_day - 80) % 365.25) * (360.0 / 365.25))
            xs, ys = self._ecl_to_xy(lon_s)
            th_s = np.arctan2(ys - self.y_center, xs)

            # Month boundary tick
            ax.plot([r2 * np.cos(th_s), (r0 + 0.006 * self.radius) * np.cos(th_s)],
                    [self.y_center + r2 * np.sin(th_s), self.y_center + (r0 + 0.006 * self.radius) * np.sin(th_s)],
                    color='#111111', linewidth=1.3, zorder=6)

            # Month name
            r_name = (r1 + 1.025*r2) / 2.0
            lon_m = np.deg2rad(((accum_day + num_days / 2.0 - 80) % 365.25) * (360.0 / 365.25))
            xm, ym = self._ecl_to_xy(lon_m)
            th_m = np.arctan2(ym - self.y_center, xm)
            rot_m = np.rad2deg(th_m) - 90
            fs_m = 3.2 if self.screen_mode else 2.6
            stroke_m = 0.7

            ax.text(r_name * np.cos(th_m), self.y_center + r_name * np.sin(th_m), name,
                    fontsize=fs_m, fontweight='bold', color='#111111',
                    ha='center', va='center', rotation=rot_m, rotation_mode='anchor', zorder=7,
                    path_effects=[pe.withStroke(linewidth=stroke_m, foreground='white')])

            # Day ticks
            for d in range(1, num_days):
                d_lon = np.deg2rad(((accum_day + d - 80) % 365.25) * (360.0 / 365.25))
                xd, yd = self._ecl_to_xy(d_lon)
                th_d = np.arctan2(yd - self.y_center, xd)

                if d % 10 == 0:
                    rt = r1
                    lw = 0.65
                    r_num = r1 + (r0 - r1) * 0.45
                    rot_n = np.rad2deg(th_d) - 90
                    d_str = ArabicFormatter.format_number(d, self.numeral_system)
                    fs_d = 2.0 if self.screen_mode else 1.7
                    ax.text(r_num * np.cos(th_d), self.y_center + r_num * np.sin(th_d), d_str,
                            fontsize=fs_d, color='#111111', ha='center', va='center',
                            fontweight='normal',
                            rotation=rot_n, rotation_mode='anchor', zorder=7,
                            path_effects=[pe.withStroke(linewidth=0.5, foreground='white')])
                elif d % 5 == 0:
                    rt = r1 + (r0 - r1) * 0.45
                    lw = 0.4
                else:
                    rt = r1 + (r0 - r1) * 0.70
                    lw = 0.2
                ax.plot([rt * np.cos(th_d), r0 * np.cos(th_d)],
                    [self.y_center + rt * np.sin(th_d), self.y_center + r0 * np.sin(th_d)],
                    color='#222222', linewidth=lw, zorder=6)

            accum_day += num_days


class Star:
    """A named astrolabe star pointer and label with intelligent deconfliction."""
    def __init__(self, name, ra_deg, dec_deg, raw_name="", mag=1.0, screen_mode=False):
        self.name = name
        self.raw_name = raw_name or name
        self.ra = np.deg2rad(ra_deg)
        self.dec = np.deg2rad(dec_deg)
        self.mag = float(mag)
        self.screen_mode = screen_mode
        # Solid circle diameter scaled inversely with visual magnitude
        base_ms = max(1.1, 2.7 - 0.40 * self.mag)
        self.marker_size = (base_ms * 1.1) if self.screen_mode else base_ms

    def draw(self, ax, proj, ecliptic=None, color='black'):
        r = proj.R * np.tan((np.pi / 2.0 - self.dec) / 2.0)
        if r > proj.r_capricorn * 0.96:
            return
            
        # Exact astronomical position for all stars - never shifted
        xp = r * np.cos(self.ra)
        yp = r * np.sin(self.ra)
        
        # Physical radius of star dot in plot units (approx 1 unit = 240 pt)
        r_dot = (self.marker_size / 2.0) / 240.0
        
        if ecliptic is not None:
            y_c = ecliptic.y_center
            r_outer = ecliptic.radius
            
            dx = xp
            dy = yp - y_c
            d_ecl = np.hypot(dx, dy)
            ux, uy = (dx / d_ecl, dy / d_ecl) if d_ecl > 0 else (0.0, 1.0)
            
            # Smart placement of labels only - stars stay at their true coordinates
            if 'قلب الأسد' in self.raw_name or 'Regulus' in self.raw_name:
                xl = ux * (r_outer + 0.08)
                yl = y_c + uy * (r_outer + 0.08)
                ha, va = 'center', 'bottom'
            elif 'السماك الأعزل' in self.raw_name or 'Spica' in self.raw_name:
                xl = xp - (r_dot + 0.04)
                yl = yp
                ha, va = 'right', 'center'
            elif 'الدبران' in self.raw_name or 'Aldebaran' in self.raw_name:
                xl = xp
                yl = yp + (r_dot + 0.04)
                ha, va = 'center', 'bottom'
            elif 'ذنب الأسد' in self.raw_name or 'Denebola' in self.raw_name:
                xl = xp + (r_dot + 0.04)
                yl = yp
                ha, va = 'left', 'center'
            elif yp < -0.6:
                xl = xp
                yl = yp + (r_dot + 0.04)
                ha, va = 'center', 'bottom'
            else:
                xl = xp
                yl = yp - (r_dot + 0.04)
                ha, va = 'center', 'top'
        else:
            xl = xp
            yl = yp - (r_dot + 0.04)
            ha, va = 'center', 'top'

        # Draw solid circle star at exact true astronomical coordinate
        ax.plot(xp, yp, 'o', color=color, markersize=self.marker_size, zorder=3)
        
        # Draw star name with high-contrast text halo
        fs = 3.2 if self.screen_mode else 2.6
        stroke_w = 0.8
        ax.text(xl, yl, self.name, fontsize=fs, fontweight='normal',
                ha=ha, va=va, color=color, zorder=4,
                path_effects=[pe.withStroke(linewidth=stroke_w, foreground='white')])


class Rete:
    """The Rete: rotatable star plate with pointers, constellations, Manazil al-Qamar, and zodiac ring."""
    def __init__(self, proj=None, language='latin', numeral_system='latin', screen_mode=False):
        self.proj = proj or StereographicProjection()
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode
        self.ecliptic = Ecliptic(self.proj, language=self.language, numeral_system=self.numeral_system, screen_mode=self.screen_mode)
        self.constellations = self._build_constellations()
        self.standalone_stars = self._build_standalone_stars()
        self.stars = self._collect_all_stars()

    def _load_label_overrides(self):
        candidates = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'label_overrides.json'),
            os.path.join(os.getcwd(), 'data', 'label_overrides.json'),
            'data/label_overrides.json'
        ]
        for p in candidates:
            if os.path.isfile(p):
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    pass
        return {"stars": {}, "constellations": {}}

    def _build_constellations(self):
        is_ar = str(self.language).lower().startswith('ar')
        data = [
            {
                'id': 'orion',
                'name': ArabicFormatter.reshape_text('الجوزاء') if is_ar else 'Orion',
                'label_pos': (85.0, -15.0),
                'stars': [
                    ('alnitak', 'النطاق' if is_ar else 'Alnitak', 85.19, -1.94, 1.74, False, '', '', 0, 0),
                    ('alnilam', 'النظام' if is_ar else 'Alnilam', 84.05, -1.2, 1.69, False, '', '', 0, 0),
                    ('mintaka', 'المنطقة' if is_ar else 'Mintaka', 83.0, -0.3, 2.25, False, '', '', 0, 0),
                    ('hip_28691', '' if is_ar else 'HIP 28691', 90.86, 19.69, 5.14, False, '', '', 0, 0),
                    ('hip_29426', '' if is_ar else 'HIP 29426', 92.98, 14.21, 4.45, False, '', '', 0, 0),
                    ('hip_29038', '' if is_ar else 'HIP 29038', 91.89, 14.77, 4.42, False, '', '', 0, 0),
                    ('hip_27913', '' if is_ar else 'HIP 27913', 88.6, 20.28, 4.39, False, '', '', 0, 0),
                    ('hip_28614', '' if is_ar else 'HIP 28614', 90.6, 9.65, 4.12, False, '', '', 0, 0),
                    ('betelgeuse', 'يد الجوزاء' if is_ar else 'Betelgeuse', 88.79, 7.41, 0.45, True, 'center', 'center', 0.03, 0.045),
                    ('saiph', 'سيف' if is_ar else 'Saiph', 86.94, -9.67, 2.07, False, '', '', 0, 0),
                    ('rigel', 'رجل الجوزاء' if is_ar else 'Rigel', 78.63, -8.2, 0.18, True, 'center', 'top', 0.0, 0.05),
                    ('bellatrix', 'المرزم' if is_ar else 'Bellatrix', 81.28, 6.35, 1.64, True, 'center', 'bottom', 0.0, 0.035),
                    ('meissa', 'ميسان' if is_ar else 'Meissa', 83.78, 9.93, 3.39, True, 'center', 'top', 0.0, 0.035),
                    ('hip_22449', '' if is_ar else 'HIP 22449', 72.46, 6.96, 3.19, False, '', '', 0, 0),
                    ('hip_22549', '' if is_ar else 'HIP 22549', 72.8, 5.61, 3.68, False, '', '', 0, 0),
                    ('hip_22730', '' if is_ar else 'HIP 22730', 73.34, 2.51, 5.33, False, '', '', 0, 0),
                    ('hip_23123', '' if is_ar else 'HIP 23123', 74.64, 1.71, 4.47, False, '', '', 0, 0),
                    ('hip_22509', '' if is_ar else 'HIP 22509', 72.65, 8.9, 4.35, False, '', '', 0, 0),
                    ('hip_22845', '' if is_ar else 'HIP 22845', 73.72, 10.15, 4.64, False, '', '', 0, 0),
                ],
                'lines': [
                    ('alnitak', 'alnilam'),
                    ('alnilam', 'mintaka'),
                    ('hip_28691', 'hip_29426'),
                    ('hip_29426', 'hip_29038'),
                    ('hip_29038', 'hip_27913'),
                    ('hip_29426', 'hip_28614'),
                    ('hip_28614', 'betelgeuse'),
                    ('betelgeuse', 'alnitak'),
                    ('alnitak', 'saiph'),
                    ('saiph', 'rigel'),
                    ('rigel', 'mintaka'),
                    ('mintaka', 'bellatrix'),
                    ('bellatrix', 'meissa'),
                    ('meissa', 'betelgeuse'),
                    ('bellatrix', 'hip_22449'),
                    ('hip_22449', 'hip_22549'),
                    ('hip_22549', 'hip_22730'),
                    ('hip_22730', 'hip_23123'),
                    ('hip_22449', 'hip_22509'),
                    ('hip_22509', 'hip_22845'),
                    ('hip_29038', 'hip_28614'),
                ]
            },
            {
                'id': 'ursa_major',
                'name': ArabicFormatter.reshape_text('بنات نعش') if is_ar else 'Ursa Major',
                'label_pos': (180.0, 48.0),
                'stars': [
                    ('alkaid', 'القائد' if is_ar else 'Alkaid', 206.89, 49.31, 1.85, True, 'center', 'top', 0.0, 0.04),
                    ('mizar', 'المئزر' if is_ar else 'Mizar', 200.98, 54.93, 2.23, True, 'left', 'center', 0.0, -0.045),
                    ('alioth', 'الجون' if is_ar else 'Alioth', 193.51, 55.96, 1.76, False, '', '', 0, 0),
                    ('megrez', 'المغرز' if is_ar else 'Megrez', 183.86, 57.03, 3.32, False, '', '', 0, 0),
                    ('dubhe', 'الدبة' if is_ar else 'Dubhe', 165.93, 61.75, 1.81, True, 'left', 'center', 0.0, -0.03),
                    ('merak', 'المراق' if is_ar else 'Merak', 165.46, 56.38, 2.34, False, '', '', 0, 0),
                    ('phecda', 'الفخذ' if is_ar else 'Phecda', 178.46, 53.69, 2.41, False, '', '', 0, 0),
                    ('hip_57399', '' if is_ar else 'HIP 57399', 176.51, 47.78, 3.69, False, '', '', 0, 0),
                    ('hip_54539', '' if is_ar else 'HIP 54539', 167.42, 44.5, 3, False, '', '', 0, 0),
                    ('hip_50372', '' if is_ar else 'HIP 50372', 154.27, 42.91, 3.45, False, '', '', 0, 0),
                    ('hip_50801', '' if is_ar else 'HIP 50801', 155.58, 41.5, 3.06, False, '', '', 0, 0),
                    ('hip_48402', '' if is_ar else 'HIP 48402', 148.03, 54.06, 4.55, False, '', '', 0, 0),
                    ('hip_46853', '' if is_ar else 'HIP 46853', 143.21, 51.68, 3.17, False, '', '', 0, 0),
                    ('hip_44471', '' if is_ar else 'HIP 44471', 135.91, 47.16, 3.57, False, '', '', 0, 0),
                    ('hip_44127', '' if is_ar else 'HIP 44127', 134.8, 48.04, 3.12, False, '', '', 0, 0),
                    ('hip_48319', '' if is_ar else 'HIP 48319', 147.75, 59.04, 3.78, False, '', '', 0, 0),
                    ('hip_41704', '' if is_ar else 'HIP 41704', 127.57, 60.72, 3.35, False, '', '', 0, 0),
                    ('hip_46733', '' if is_ar else 'HIP 46733', 142.88, 63.06, 3.65, False, '', '', 0, 0),
                ],
                'lines': [
                    ('alkaid', 'mizar'),
                    ('mizar', 'alioth'),
                    ('alioth', 'megrez'),
                    ('megrez', 'dubhe'),
                    ('dubhe', 'merak'),
                    ('merak', 'phecda'),
                    ('phecda', 'megrez'),
                    ('phecda', 'hip_57399'),
                    ('hip_57399', 'hip_54539'),
                    ('hip_54539', 'hip_50372'),
                    ('hip_54539', 'hip_50801'),
                    ('merak', 'hip_48402'),
                    ('hip_48402', 'hip_46853'),
                    ('hip_46853', 'hip_44471'),
                    ('hip_46853', 'hip_44127'),
                    ('hip_48402', 'hip_48319'),
                    ('hip_48319', 'hip_41704'),
                    ('hip_41704', 'hip_46733'),
                    ('hip_46733', 'dubhe'),
                ]
            },
            {
                'id': 'cassiopeia',
                'name': ArabicFormatter.reshape_text('ذات الكرسي') if is_ar else 'Cassiopeia',
                'label_pos': (0.0, 72.0),
                'stars': [
                    ('ruchbah', 'الركبة' if is_ar else 'Ruchbah', 28.6, 63.67, 3.35, False, '', '', 0, 0),
                    ('hip_6686', '' if is_ar else 'HIP 6686', 21.45, 60.24, 2.66, False, '', '', 0, 0),
                    ('navi', 'الناقة' if is_ar else 'Navi', 14.18, 60.72, 2.15, False, '', '', 0, 0),
                    ('schedar', 'الصدر' if is_ar else 'Schedar', 10.13, 56.54, 2.24, True, 'center', 'top', 0.0, 0.045),
                    ('caph', 'كف الخضيب' if is_ar else 'Caph', 2.29, 59.15, 2.28, True, 'center', 'top', -0.08, -0.045),
                ],
                'lines': [
                    ('ruchbah', 'hip_6686'),
                    ('hip_6686', 'navi'),
                    ('navi', 'schedar'),
                    ('schedar', 'caph'),
                ]
            },
            {
                'id': 'leo',
                'name': ArabicFormatter.reshape_text('الأسد') if is_ar else 'Leo',
                'label_pos': (165.0, 30.0),
                'stars': [
                    ('denebola', 'ذنب الأسد' if is_ar else 'Denebola', 177.26, 14.57, 2.14, True, 'left', 'center', 0.0, -0.045),
                    ('chertan', 'الخرات' if is_ar else 'Chertan', 168.56, 15.43, 3.33, False, '', '', 0, 0),
                    ('regulus', 'قلب الأسد' if is_ar else 'Regulus', 152.09, 11.97, 1.36, True, 'right', 'bottom', 0.0, 0.055),
                    ('hip_49583', '' if is_ar else 'HIP 49583', 151.83, 16.76, 3.48, False, '', '', 0, 0),
                    ('algieba', 'الجبهة' if is_ar else 'Algieba', 154.99, 19.84, 2.01, True, 'left', 'top', 0.0, -0.045),
                    ('zosma', 'الظهر' if is_ar else 'Zosma', 168.53, 20.52, 2.56, False, '', '', 0, 0),
                    ('adhafera', 'الضفيرة' if is_ar else 'Adhafera', 154.17, 23.42, 3.43, False, '', '', 0, 0),
                    ('rasalas', 'رأس الأسد' if is_ar else 'Rasalas', 148.19, 26.01, 3.88, False, '', '', 0, 0),
                    ('subra', 'الطرف' if is_ar else 'Subra', 146.46, 23.77, 2.97, False, '', '', 0, 0),
                ],
                'lines': [
                    ('denebola', 'chertan'),
                    ('chertan', 'regulus'),
                    ('regulus', 'hip_49583'),
                    ('hip_49583', 'algieba'),
                    ('algieba', 'zosma'),
                    ('zosma', 'denebola'),
                    ('algieba', 'adhafera'),
                    ('adhafera', 'rasalas'),
                    ('rasalas', 'subra'),
                    ('zosma', 'chertan'),
                ]
            },
            {
                'id': 'taurus',
                'name': ArabicFormatter.reshape_text('الثور') if is_ar else 'Taurus',
                'label_pos': (58.0, 10.0),
                'stars': [
                    ('elnath', 'النطح' if is_ar else 'Elnath', 81.57, 28.61, 1.65, False, 'center', 'bottom', -0.01, 0.065),
                    ('hip_21881', '' if is_ar else 'HIP 21881', 70.56, 22.96, 4.27, False, '', '', 0, 0),
                    ('ain', 'عين الثور' if is_ar else 'Ain', 67.15, 19.18, 3.53, False, '', '', 0, 0),
                    ('aldebaran', 'الدبران' if is_ar else 'Aldebaran', 68.98, 16.51, 0.87, True, 'center', 'bottom', 0.0, 0.04),
                    ('tianguan', 'قرن الثور' if is_ar else 'Tianguan', 84.41, 21.14, 2.97, False, '', '', 0, 0),
                    ('hyadum1', 'قلاص' if is_ar else 'Hyadum I', 64.95, 15.63, 3.65, False, '', '', 0, 0),
                    ('hyadum2', 'دلتا' if is_ar else 'Hyadum II', 65.73, 17.54, 3.77, False, '', '', 0, 0),
                    ('hip_18724', '' if is_ar else 'HIP 18724', 60.17, 12.49, 3.41, False, '', '', 0, 0),
                    ('hip_15900', '' if is_ar else 'HIP 15900', 51.2, 9.03, 3.61, False, '', '', 0, 0),
                    ('hip_20894', '' if is_ar else 'HIP 20894', 67.17, 15.87, 3.4, False, '', '', 0, 0),
                    ('hip_20648', '' if is_ar else 'HIP 20648', 66.37, 17.93, 4.3, False, '', '', 0, 0),
                    ('hip_17847', '' if is_ar else 'HIP 17847', 57.29, 24.05, 3.62, False, '', '', 0, 0),
                ],
                'lines': [
                    ('elnath', 'hip_21881'),
                    ('hip_21881', 'ain'),
                    ('aldebaran', 'tianguan'),
                    ('hyadum1', 'hyadum2'),
                    ('hyadum1', 'hip_18724'),
                    ('hip_18724', 'hip_15900'),
                    ('aldebaran', 'ain'),
                    ('aldebaran', 'hip_20894'),
                    ('hip_20894', 'hyadum1'),
                    ('ain', 'hip_20648'),
                    ('hip_20648', 'hyadum2'),
                    ('hyadum2', 'hip_17847'),
                ]
            },
            {
                'id': 'scorpius',
                'name': ArabicFormatter.reshape_text('العقرب') if is_ar else 'Scorpius',
                'label_pos': (242.0, -28.0),
                'stars': [
                    ('shaula', 'الشولة' if is_ar else 'Shaula', 263.4, -37.1, 1.62, True, 'center', 'top', 0.0, 0.035),
                    ('hip_86670', '' if is_ar else 'HIP 86670', 265.62, -39.03, 2.39, False, '', '', 0, 0),
                    ('hip_87073', '' if is_ar else 'HIP 87073', 266.9, -40.13, 2.99, False, '', '', 0, 0),
                    ('hip_86228', '' if is_ar else 'HIP 86228', 264.33, -43.0, 1.86, False, '', '', 0, 0),
                    ('hip_84143', '' if is_ar else 'HIP 84143', 258.04, -43.24, 3.32, False, '', '', 0, 0),
                    ('hip_82671', '' if is_ar else 'HIP 82671', 253.5, -42.36, 4.7, False, '', '', 0, 0),
                    ('hip_82514', '' if is_ar else 'HIP 82514', 252.97, -38.05, 3, False, '', '', 0, 0),
                    ('hip_82396', '' if is_ar else 'HIP 82396', 252.54, -34.29, 2.29, False, '', '', 0, 0),
                    ('tau_sco', 'النياط' if is_ar else 'Tau Sco', 248.97, -28.22, 2.82, False, '', '', 0, 0),
                    ('antares', 'قلب العقرب' if is_ar else 'Antares', 247.35, -26.43, 1.06, True, 'left', 'center', 0.03, -0.03),
                    ('dschubba', 'الجبهة' if is_ar else 'Dschubba', 240.08, -22.62, 2.29, True, 'right', 'center', -0.05, 0.0),
                    ('pi_sco', 'العقرب' if is_ar else 'Pi Sco', 239.71, -26.11, 2.89, False, '', '', 0, 0),
                    ('acrab', 'الإكليل' if is_ar else 'Acrab', 241.36, -19.81, 2.56, True, 'center', 'center', -0.01, 0.025),
                ],
                'lines': [
                    ('shaula', 'hip_86670'),
                    ('hip_86670', 'hip_87073'),
                    ('hip_87073', 'hip_86228'),
                    ('hip_86228', 'hip_84143'),
                    ('hip_84143', 'hip_82671'),
                    ('hip_82671', 'hip_82514'),
                    ('hip_82514', 'hip_82396'),
                    ('hip_82396', 'tau_sco'),
                    ('tau_sco', 'antares'),
                    ('antares', 'dschubba'),
                    ('antares', 'pi_sco'),
                    ('antares', 'acrab'),
                ]
            },
            {
                'id': 'ursa_minor',
                'name': ArabicFormatter.reshape_text('الدب الأصغر') if is_ar else 'Ursa Minor',
                'label_pos': (100.0, 105.0),
                'stars': [
                    ('polaris', 'نجم القطب' if is_ar else 'Polaris', 37.95, 89.26, 1.97, True, 'left', 'center', 0.0, 0.085),
                    ('yildun', 'يلدون' if is_ar else 'Yildun', 263.05, 86.59, 4.35, False, '', '', 0, 0),
                    ('hip_82080', '' if is_ar else 'HIP 82080', 251.49, 82.04, 4.21, False, '', '', 0, 0),
                    ('hip_77055', '' if is_ar else 'HIP 77055', 236.01, 77.79, 4.29, False, '', '', 0, 0),
                    ('hip_79822', '' if is_ar else 'HIP 79822', 244.38, 75.76, 4.95, False, '', '', 0, 0),
                    ('pherkad', 'أخفى الفرقدين' if is_ar else 'Pherkad', 230.18, 71.83, 3, False, '', '', 0, 0),
                    ('kochab', 'أنور الفرقدين' if is_ar else 'Kochab', 222.68, 74.16, 2.07, False, 'center', 'top', -0.06, -0.055),
                ],
                'lines': [
                    ('polaris', 'yildun'),
                    ('yildun', 'hip_82080'),
                    ('hip_82080', 'hip_77055'),
                    ('hip_77055', 'hip_79822'),
                    ('hip_79822', 'pherkad'),
                    ('pherkad', 'kochab'),
                    ('kochab', 'hip_77055'),
                ]
            },
            {
                'id': 'cygnus',
                'name': ArabicFormatter.reshape_text('الدجاجة') if is_ar else 'Cygnus',
                'label_pos': (328.0, 42.0),
                'stars': [
                    ('hip_94779', '' if is_ar else 'HIP 94779', 289.28, 53.37, 3.8, False, '', '', 0, 0),
                    ('hip_95853', '' if is_ar else 'HIP 95853', 292.43, 51.73, 3.76, False, '', '', 0, 0),
                    ('hip_97165', '' if is_ar else 'HIP 97165', 296.24, 45.13, 2.86, False, '', '', 0, 0),
                    ('sadr', 'الصدر' if is_ar else 'Sadr', 305.56, 40.26, 2.23, False, '', '', 0, 0),
                    ('deneb', 'ذنب الدجاجة' if is_ar else 'Deneb', 310.36, 45.28, 1.25, True, 'center', 'top', 0.02, -0.05),
                    ('gienah', 'الجناح' if is_ar else 'Gienah', 311.55, 33.97, 2.48, False, '', '', 0, 0),
                    ('hip_104732', '' if is_ar else 'HIP 104732', 318.23, 30.23, 3.21, False, '', '', 0, 0),
                    ('hip_107310', '' if is_ar else 'HIP 107310', 326.04, 28.74, 4.49, False, '', '', 0, 0),
                    ('hip_98110', '' if is_ar else 'HIP 98110', 299.08, 35.08, 3.89, False, '', '', 0, 0),
                    ('albireo', 'منقار الدجاجة' if is_ar else 'Albireo', 292.68, 27.96, 3.05, True, 'center', 'top', 0.0, 0.04),
                ],
                'lines': [
                    ('hip_94779', 'hip_95853'),
                    ('hip_95853', 'hip_97165'),
                    ('hip_97165', 'sadr'),
                    ('sadr', 'deneb'),
                    ('sadr', 'gienah'),
                    ('gienah', 'hip_104732'),
                    ('hip_104732', 'hip_107310'),
                    ('sadr', 'hip_98110'),
                    ('hip_98110', 'albireo'),
                ]
            },
            {
                'id': 'lyra',
                'name': ArabicFormatter.reshape_text('السلياق') if is_ar else 'Lyra',
                'label_pos': (270.0, 52.0),
                'stars': [
                    ('vega', 'النسر الواقع' if is_ar else 'Vega', 279.23, 38.78, 0.03, True, 'center', 'top', 0.0, -0.045),
                    ('hip_91971', '' if is_ar else 'HIP 91971', 281.19, 37.61, 4.34, False, '', '', 0, 0),
                    ('sheliak', 'الشلياق' if is_ar else 'Sheliak', 282.52, 33.36, 3.52, False, '', '', 0, 0),
                    ('sulafat', 'السلحفاة' if is_ar else 'Sulafat', 284.74, 32.69, 3.25, False, '', '', 0, 0),
                    ('hip_92791', '' if is_ar else 'HIP 92791', 283.63, 36.9, 4.22, False, '', '', 0, 0),
                ],
                'lines': [
                    ('vega', 'hip_91971'),
                    ('hip_91971', 'sheliak'),
                    ('sheliak', 'sulafat'),
                    ('sulafat', 'hip_92791'),
                    ('hip_92791', 'hip_91971'),
                ]
            },
            {
                'id': 'aquila',
                'name': ArabicFormatter.reshape_text('العقاب') if is_ar else 'Aquila',
                'label_pos': (295.0, -9.0),
                'stars': [
                    ('alshain', 'شاهين' if is_ar else 'Alshain', 298.83, 6.41, 3.71, False, '', '', 0, 0),
                    ('altair', 'النسر الطائر' if is_ar else 'Altair', 297.7, 8.87, 0.76, True, 'right', 'bottom', 0.0, 0.04),
                    ('tarazed', 'ترزاد' if is_ar else 'Tarazed', 296.56, 10.61, 2.72, False, '', '', 0, 0),
                    ('hip_95501', '' if is_ar else 'HIP 95501', 291.37, 3.11, 3.36, False, '', '', 0, 0),
                    ('hip_97804', '' if is_ar else 'HIP 97804', 298.12, 1.01, 3.87, False, '', '', 0, 0),
                    ('hip_99473', '' if is_ar else 'HIP 99473', 302.83, -0.82, 3.24, False, '', '', 0, 0),
                    ('hip_93747', '' if is_ar else 'HIP 93747', 286.35, 13.86, 2.99, False, '', '', 0, 0),
                    ('hip_93244', '' if is_ar else 'HIP 93244', 284.91, 15.07, 4.02, False, '', '', 0, 0),
                    ('hip_93805', '' if is_ar else 'HIP 93805', 286.56, -4.88, 3.43, False, '', '', 0, 0),
                ],
                'lines': [
                    ('alshain', 'altair'),
                    ('altair', 'tarazed'),
                    ('altair', 'hip_95501'),
                    ('hip_95501', 'hip_97804'),
                    ('hip_99473', 'hip_97804'),
                    ('hip_95501', 'hip_93747'),
                    ('hip_93747', 'hip_93244'),
                    ('hip_95501', 'hip_93805'),
                ]
            },
            {
                'id': 'gemini',
                'name': ArabicFormatter.reshape_text('التوأمان') if is_ar else 'Gemini',
                'label_pos': (100.0, 8.0),
                'stars': [
                    ('alhena', 'الهنعة' if is_ar else 'Alhena', 99.43, 16.4, 1.93, True, 'center', 'bottom', 0.0, 0.035),
                    ('hip_34088', '' if is_ar else 'HIP 34088', 106.03, 20.57, 4.01, False, '', '', 0, 0),
                    ('wasat', 'وسط السماء' if is_ar else 'Wasat', 110.03, 21.98, 3.5, False, '', '', 0, 0),
                    ('hip_35350', '' if is_ar else 'HIP 35350', 109.52, 16.54, 3.58, False, '', '', 0, 0),
                    ('alzirr', 'الزر' if is_ar else 'Alzirr', 101.32, 12.9, 3.35, False, '', '', 0, 0),
                    ('hip_36962', '' if is_ar else 'HIP 36962', 113.98, 26.9, 4.06, False, '', '', 0, 0),
                    ('hip_37740', '' if is_ar else 'HIP 37740', 116.11, 24.4, 3.57, False, '', '', 0, 0),
                    ('pollux', '' if is_ar else 'Pollux', 116.33, 28.03, 1.16, False, '', '', 0, 0),
                    ('hip_36046', '' if is_ar else 'HIP 36046', 111.43, 27.8, 3.78, False, '', '', 0, 0),
                    ('hip_34693', '' if is_ar else 'HIP 34693', 107.78, 30.25, 4.41, False, '', '', 0, 0),
                    ('castor', '' if is_ar else 'Castor', 113.65, 31.89, 1.58, False, '', '', 0, 0),
                    ('hip_33018', '' if is_ar else 'HIP 33018', 103.2, 33.96, 3.6, False, '', '', 0, 0),
                    ('hip_32246', '' if is_ar else 'HIP 32246', 100.98, 25.13, 3.06, False, '', '', 0, 0),
                    ('hip_30883', '' if is_ar else 'HIP 30883', 97.24, 20.21, 4.13, False, '', '', 0, 0),
                    ('mebsuta', 'الذراع المبسوطة' if is_ar else 'Mebsuta', 95.74, 22.51, 2.87, False, '', '', 0, 0),
                    ('hip_29655', '' if is_ar else 'HIP 29655', 93.72, 22.51, 3.31, False, '', '', 0, 0),
                    ('hip_28734', '' if is_ar else 'HIP 28734', 91.03, 23.26, 4.16, False, '', '', 0, 0),
                ],
                'lines': [
                    ('alhena', 'hip_34088'),
                    ('hip_34088', 'wasat'),
                    ('wasat', 'hip_35350'),
                    ('hip_35350', 'alzirr'),
                    ('wasat', 'hip_36962'),
                    ('hip_36962', 'hip_37740'),
                    ('hip_36962', 'pollux'),
                    ('hip_36962', 'hip_36046'),
                    ('hip_36046', 'hip_34693'),
                    ('hip_34693', 'castor'),
                    ('hip_34693', 'hip_33018'),
                    ('hip_34693', 'hip_32246'),
                    ('hip_32246', 'hip_30883'),
                    ('hip_32246', 'mebsuta'),
                    ('mebsuta', 'hip_29655'),
                    ('hip_29655', 'hip_28734'),
                ]
            },
            {
                'id': 'pegasus',
                'name': ArabicFormatter.reshape_text('الفرس الأعظم') if is_ar else 'Pegasus',
                'label_pos': (355.0, 22.0),
                'stars': [
                    ('algenib', 'الجنب' if is_ar else 'Algenib', 3.31, 15.18, 2.83, False, '', '', 0, 0),
                    ('markab', 'منكب الفرس' if is_ar else 'Markab', 346.19, 15.21, 2.49, True, 'center', 'top', 0.0, 0.0),
                    ('scheat', 'الساعد' if is_ar else 'Scheat', 345.94, 28.08, 2.44, False, '', '', 0, 0),
                    ('hip_112158', '' if is_ar else 'HIP 112158', 340.75, 30.22, 2.93, False, '', '', 0, 0),
                    ('hip_109352', '' if is_ar else 'HIP 109352', 332.31, 33.17, 5.58, False, '', '', 0, 0),
                    ('hip_112748', '' if is_ar else 'HIP 112748', 342.5, 24.6, 3.51, False, '', '', 0, 0),
                    ('hip_112440', '' if is_ar else 'HIP 112440', 341.63, 23.57, 3.97, False, '', '', 0, 0),
                    ('hip_109176', '' if is_ar else 'HIP 109176', 331.75, 25.35, 3.77, False, '', '', 0, 0),
                    ('hip_107354', '' if is_ar else 'HIP 107354', 326.16, 25.65, 4.14, False, '', '', 0, 0),
                    ('hip_112447', '' if is_ar else 'HIP 112447', 341.67, 12.17, 4.2, False, '', '', 0, 0),
                    ('hip_112029', '' if is_ar else 'HIP 112029', 340.37, 10.83, 3.41, False, '', '', 0, 0),
                    ('hip_109427', '' if is_ar else 'HIP 109427', 332.55, 6.2, 3.52, False, '', '', 0, 0),
                    ('enif', 'أنف الفرس' if is_ar else 'Enif', 326.05, 9.88, 2.38, True, 'center', 'top', 0.0, 0.0),
                    ('alpheratz', 'سرة الفرس' if is_ar else 'Alpheratz', 2.1, 29.09, 2.07, True, 'center', 'bottom', 0.0, -0.04),
                ],
                'lines': [
                    ('algenib', 'markab'),
                    ('scheat', 'hip_112158'),
                    ('hip_112158', 'hip_109352'),
                    ('scheat', 'hip_112748'),
                    ('hip_112748', 'hip_112440'),
                    ('hip_112440', 'hip_109176'),
                    ('hip_109176', 'hip_107354'),
                    ('markab', 'hip_112447'),
                    ('hip_112447', 'hip_112029'),
                    ('hip_112029', 'hip_109427'),
                    ('hip_109427', 'enif'),
                    ('alpheratz', 'scheat'),
                    ('alpheratz', 'algenib'),
                    ('scheat', 'markab'),
                ]
            },
            {
                'id': 'canis_major',
                'name': ArabicFormatter.reshape_text('الكلب الأكبر') if is_ar else 'Canis Major',
                'label_pos': (105.0, -22.0),
                'stars': [
                    ('hip_33160', '' if is_ar else 'HIP 33160', 103.55, -12.04, 4.08, False, '', '', 0, 0),
                    ('hip_34045', '' if is_ar else 'HIP 34045', 105.94, -15.63, 4.11, False, '', '', 0, 0),
                    ('hip_33347', '' if is_ar else 'HIP 33347', 104.03, -17.05, 4.36, False, '', '', 0, 0),
                    ('sirius', 'الشعرى اليمانية' if is_ar else 'Sirius', 101.29, -16.72, -1.44, True, 'center', 'bottom', 0.0, 0.045),
                    ('hip_33977', '' if is_ar else 'HIP 33977', 105.76, -23.83, 3.02, False, '', '', 0, 0),
                    ('wezen', 'الوزن' if is_ar else 'Wezen', 107.1, -26.39, 1.83, False, '', '', 0, 0),
                    ('hip_35037', '' if is_ar else 'HIP 35037', 108.7, -26.77, 4.01, False, '', '', 0, 0),
                    ('hip_35904', '' if is_ar else 'HIP 35904', 111.02, -29.3, 2.45, False, '', '', 0, 0),
                    ('adhara', 'عذارى' if is_ar else 'Adhara', 104.66, -28.97, 1.5, False, '', '', 0, 0),
                    ('hip_33856', '' if is_ar else 'HIP 33856', 105.43, -27.93, 3.49, False, '', '', 0, 0),
                    ('hip_33152', '' if is_ar else 'HIP 33152', 103.53, -24.18, 3.89, False, '', '', 0, 0),
                    ('hip_31592', '' if is_ar else 'HIP 31592', 99.17, -19.26, 3.95, False, '', '', 0, 0),
                    ('hip_31416', '' if is_ar else 'HIP 31416', 98.76, -22.96, 4.54, False, '', '', 0, 0),
                    ('mirzam', 'مرزم' if is_ar else 'Mirzam', 95.67, -17.96, 1.98, False, '', '', 0, 0),
                    ('hip_30122', '' if is_ar else 'HIP 30122', 95.08, -30.06, 3.02, False, '', '', 0, 0),
                ],
                'lines': [
                    ('hip_33160', 'hip_34045'),
                    ('hip_34045', 'hip_33347'),
                    ('hip_33347', 'sirius'),
                    ('sirius', 'hip_33977'),
                    ('hip_33977', 'wezen'),
                    ('wezen', 'hip_35037'),
                    ('hip_35037', 'hip_35904'),
                    ('adhara', 'hip_33856'),
                    ('hip_33856', 'wezen'),
                    ('hip_33856', 'hip_33152'),
                    ('hip_33152', 'hip_31592'),
                    ('hip_31592', 'hip_31416'),
                    ('sirius', 'mirzam'),
                    ('hip_31592', 'sirius'),
                    ('hip_30122', 'adhara'),
                    ('hip_33347', 'hip_33160'),
                ]
            },
            {
                'id': 'canis_minor',
                'name': ArabicFormatter.reshape_text('الكلب الأصغر') if is_ar else 'Canis Minor',
                'label_pos': (114.0, 0.0),
                'stars': [
                    ('procyon', 'الشعرى الشامية' if is_ar else 'Procyon', 114.83, 5.22, 0.4, True, 'center', 'top', 0.0, 0.045),
                    ('gomeisa', 'الغميصاء' if is_ar else 'Gomeisa', 111.79, 8.29, 2.89, False, '', '', 0, 0),
                ],
                'lines': [
                    ('procyon', 'gomeisa'),
                ]
            },
            {
                'id': 'auriga',
                'name': ArabicFormatter.reshape_text('ممسك الأعنة') if is_ar else 'Auriga',
                'label_pos': (88.0, 54.0),
                'stars': [
                    ('hip_28380', '' if is_ar else 'HIP 28380', 89.93, 37.21, 2.65, False, '', '', 0, 0),
                    ('menkalinan', 'منكب ذي الأعنة' if is_ar else 'Menkalinan', 89.88, 44.95, 1.9, False, '', '', 0, 0),
                    ('capella', 'العيوق' if is_ar else 'Capella', 79.17, 46.0, 0.08, True, 'center', 'top', 0.0, -0.045),
                    ('hip_23453', '' if is_ar else 'HIP 23453', 75.62, 41.08, 3.69, False, '', '', 0, 0),
                    ('hip_23015', '' if is_ar else 'HIP 23015', 74.25, 33.17, 2.69, False, '', '', 0, 0),
                    ('elnath', 'النطح' if is_ar else 'Elnath', 81.57, 28.61, 1.65, False, 'center', 'bottom', -0.01, 0.065),
                ],
                'lines': [
                    ('hip_28380', 'menkalinan'),
                    ('menkalinan', 'capella'),
                    ('capella', 'hip_23453'),
                    ('hip_23453', 'hip_23015'),
                    ('elnath', 'hip_23015'),
                    ('elnath', 'hip_28380'),
                ]
            },
            {
                'id': 'bootes',
                'name': ArabicFormatter.reshape_text('العواء') if is_ar else 'Boötes',
                'label_pos': (219.0, 32.0),
                'stars': [
                    ('hip_71795', '' if is_ar else 'HIP 71795', 220.29, 13.73, 3.78, False, '', '', 0, 0),
                    ('arcturus', 'السماك الرامح' if is_ar else 'Arcturus', 213.92, 19.18, -0.05, True, 'center', 'top', 0.0, 0.045),
                    ('izar', 'الإزار' if is_ar else 'Izar', 221.25, 27.07, 2.35, False, '', '', 0, 0),
                    ('hip_74666', '' if is_ar else 'HIP 74666', 228.88, 33.31, 3.46, False, '', '', 0, 0),
                    ('hip_73555', '' if is_ar else 'HIP 73555', 225.49, 40.39, 3.49, False, '', '', 0, 0),
                    ('hip_71075', '' if is_ar else 'HIP 71075', 218.02, 38.31, 3.04, False, '', '', 0, 0),
                    ('hip_71053', '' if is_ar else 'HIP 71053', 217.96, 30.37, 3.57, False, '', '', 0, 0),
                    ('muphrid', 'مفرد الرامح' if is_ar else 'Muphrid', 208.67, 18.4, 2.68, False, '', '', 0, 0),
                    ('hip_67459', '' if is_ar else 'HIP 67459', 207.37, 15.8, 4.05, False, '', '', 0, 0),
                ],
                'lines': [
                    ('hip_71795', 'arcturus'),
                    ('arcturus', 'izar'),
                    ('izar', 'hip_74666'),
                    ('hip_74666', 'hip_73555'),
                    ('hip_73555', 'hip_71075'),
                    ('hip_71075', 'hip_71053'),
                    ('hip_71053', 'arcturus'),
                    ('arcturus', 'muphrid'),
                    ('muphrid', 'hip_67459'),
                ]
            },
            {
                'id': 'ophiuchus',
                'name': ArabicFormatter.reshape_text('الحواء') if is_ar else 'Ophiuchus',
                'label_pos': (256.0, 5.0),
                'stars': [
                    ('rasalhague', 'رأس الحواء' if is_ar else 'Rasalhague', 263.73, 12.56, 2.08, True, 'center', 'bottom', 0.0, 0.05),
                    ('hip_86742', '' if is_ar else 'HIP 86742', 265.87, 4.57, 2.76, False, '', '', 0, 0),
                    ('hip_84012', '' if is_ar else 'HIP 84012', 257.59, -15.72, 2.43, False, '', '', 0, 0),
                    ('hip_83000', '' if is_ar else 'HIP 83000', 254.42, 9.38, 3.19, False, '', '', 0, 0),
                    ('hip_79882', '' if is_ar else 'HIP 79882', 244.58, -4.69, 3.23, False, '', '', 0, 0),
                    ('hip_81377', '' if is_ar else 'HIP 81377', 249.29, -10.57, 2.54, False, '', '', 0, 0),
                    ('hip_85755', '' if is_ar else 'HIP 85755', 262.85, -23.96, 4.78, False, '', '', 0, 0),
                ],
                'lines': [
                    ('rasalhague', 'hip_86742'),
                    ('hip_84012', 'hip_86742'),
                    ('rasalhague', 'hip_83000'),
                    ('hip_83000', 'hip_79882'),
                    ('hip_79882', 'hip_81377'),
                    ('hip_81377', 'hip_84012'),
                    ('hip_84012', 'hip_85755'),
                ]
            },
            {
                'id': 'hydra',
                'name': ArabicFormatter.reshape_text('الشجاع') if is_ar else 'Hydra',
                'label_pos': (136.0, -14.0),
                'stars': [
                    ('hip_42799', '' if is_ar else 'HIP 42799', 130.81, 3.4, 4.3, False, '', '', 0, 0),
                    ('hip_42402', '' if is_ar else 'HIP 42402', 129.69, 3.34, 4.45, False, '', '', 0, 0),
                    ('hip_42313', '' if is_ar else 'HIP 42313', 129.41, 5.7, 4.14, False, '', '', 0, 0),
                    ('hip_43109', '' if is_ar else 'HIP 43109', 131.69, 6.42, 3.38, False, '', '', 0, 0),
                    ('hip_43234', '' if is_ar else 'HIP 43234', 132.11, 5.84, 4.35, False, '', '', 0, 0),
                    ('hip_43813', '' if is_ar else 'HIP 43813', 133.85, 5.95, 3.11, False, '', '', 0, 0),
                    ('hip_45336', '' if is_ar else 'HIP 45336', 138.59, 2.31, 3.89, False, '', '', 0, 0),
                    ('hip_46776', '' if is_ar else 'HIP 46776', 143.0, -1.18, 4.54, False, '', '', 0, 0),
                    ('hip_46509', '' if is_ar else 'HIP 46509', 142.29, -2.77, 4.59, False, '', '', 0, 0),
                    ('alphard', 'الفرد' if is_ar else 'Alphard', 141.9, -8.66, 1.99, True, 'center', 'bottom', 0.0, 0.045),
                    ('hip_48356', '' if is_ar else 'HIP 48356', 147.87, -14.85, 4.11, False, '', '', 0, 0),
                    ('hip_49841', '' if is_ar else 'HIP 49841', 152.65, -12.35, 3.61, False, '', '', 0, 0),
                    ('hip_51069', '' if is_ar else 'HIP 51069', 156.52, -16.84, 3.83, False, '', '', 0, 0),
                    ('hip_52943', '' if is_ar else 'HIP 52943', 162.41, -16.19, 3.11, False, '', '', 0, 0),
                    ('hip_56343', '' if is_ar else 'HIP 56343', 173.25, -31.86, 3.54, False, '', '', 0, 0),
                    ('hip_57936', '' if is_ar else 'HIP 57936', 178.23, -33.91, 4.29, False, '', '', 0, 0),
                    ('hip_64166', '' if is_ar else 'HIP 64166', 197.26, -23.12, 4.94, False, '', '', 0, 0),
                    ('hip_64962', '' if is_ar else 'HIP 64962', 199.73, -23.17, 2.99, False, '', '', 0, 0),
                ],
                'lines': [
                    ('hip_42799', 'hip_42402'),
                    ('hip_42402', 'hip_42313'),
                    ('hip_42313', 'hip_43109'),
                    ('hip_43109', 'hip_43234'),
                    ('hip_43234', 'hip_42799'),
                    ('hip_43234', 'hip_43813'),
                    ('hip_43813', 'hip_45336'),
                    ('hip_45336', 'hip_46776'),
                    ('hip_46776', 'hip_46509'),
                    ('hip_46509', 'alphard'),
                    ('alphard', 'hip_48356'),
                    ('hip_48356', 'hip_49841'),
                    ('hip_49841', 'hip_51069'),
                    ('hip_51069', 'hip_52943'),
                    ('hip_52943', 'hip_56343'),
                    ('hip_56343', 'hip_57936'),
                    ('hip_57936', 'hip_64166'),
                    ('hip_64166', 'hip_64962'),
                ]
            },
            {
                'id': 'cetus',
                'name': ArabicFormatter.reshape_text('قيطس') if is_ar else 'Cetus',
                'label_pos': (32.0, -18.0),
                'stars': [
                    ('hip_10324', '' if is_ar else 'HIP 10324', 33.25, 8.85, 4.36, False, '', '', 0, 0),
                    ('hip_11484', '' if is_ar else 'HIP 11484', 37.04, 8.46, 4.3, False, '', '', 0, 0),
                    ('hip_8102', '' if is_ar else 'HIP 8102', 26.02, -15.94, 3.49, False, '', '', 0, 0),
                    ('diphda', 'الضفدع الثاني' if is_ar else 'Diphda', 10.9, -17.99, 2.04, True, 'center', 'bottom', 0.0, -0.045),
                    ('hip_1562', '' if is_ar else 'HIP 1562', 4.86, -8.82, 3.56, False, '', '', 0, 0),
                    ('hip_5364', '' if is_ar else 'HIP 5364', 17.15, -10.18, 3.46, False, '', '', 0, 0),
                    ('hip_6537', '' if is_ar else 'HIP 6537', 21.01, -8.18, 3.6, False, '', '', 0, 0),
                    ('hip_8645', '' if is_ar else 'HIP 8645', 27.87, -10.34, 3.74, False, '', '', 0, 0),
                    ('hip_11345', '' if is_ar else 'HIP 11345', 36.49, -12.29, 4.88, False, '', '', 0, 0),
                    ('hip_12390', '' if is_ar else 'HIP 12390', 39.89, -11.87, 4.83, False, '', '', 0, 0),
                    ('hip_12770', '' if is_ar else 'HIP 12770', 41.03, -13.86, 4.24, False, '', '', 0, 0),
                    ('hip_11783', '' if is_ar else 'HIP 11783', 38.02, -15.24, 4.74, False, '', '', 0, 0),
                    ('mira', 'ميرا' if is_ar else 'Mira', 34.84, -2.98, 6.47, False, '', '', 0, 0),
                    ('hip_12387', '' if is_ar else 'HIP 12387', 39.87, 0.33, 4.08, False, '', '', 0, 0),
                    ('hip_12706', '' if is_ar else 'HIP 12706', 40.83, 3.24, 3.47, False, '', '', 0, 0),
                    ('menkar', 'منخر قيطس' if is_ar else 'Menkar', 45.57, 4.09, 2.54, True, 'center', 'top', 0.0, 0.045),
                    ('hip_13954', '' if is_ar else 'HIP 13954', 44.93, 8.91, 4.71, False, '', '', 0, 0),
                    ('hip_12828', '' if is_ar else 'HIP 12828', 41.24, 10.11, 4.27, False, '', '', 0, 0),
                    ('hip_12093', '' if is_ar else 'HIP 12093', 38.97, 5.59, 4.87, False, '', '', 0, 0),
                ],
                'lines': [
                    ('hip_10324', 'hip_11484'),
                    ('hip_8102', 'diphda'),
                    ('diphda', 'hip_1562'),
                    ('diphda', 'hip_5364'),
                    ('hip_5364', 'hip_6537'),
                    ('hip_6537', 'hip_8645'),
                    ('hip_8645', 'hip_11345'),
                    ('hip_11345', 'hip_12390'),
                    ('hip_12390', 'hip_12770'),
                    ('hip_12770', 'hip_11783'),
                    ('hip_11783', 'hip_8102'),
                    ('mira', 'hip_12390'),
                    ('mira', 'hip_12387'),
                    ('hip_12387', 'hip_12706'),
                    ('hip_12706', 'menkar'),
                    ('menkar', 'hip_13954'),
                    ('hip_13954', 'hip_12828'),
                    ('hip_12828', 'hip_11484'),
                    ('hip_11484', 'hip_12093'),
                    ('hip_12093', 'hip_12706'),
                ]
            },
            {
                'id': 'pisces',
                'name': ArabicFormatter.reshape_text('الحوت') if is_ar else 'Pisces',
                'label_pos': (18.0, 2.0),
                'stars': [
                    ('hip_4889', '' if is_ar else 'HIP 4889', 15.7, 31.8, 5.5, False, '', '', 0, 0),
                    ('hip_5742', '' if is_ar else 'HIP 5742', 18.44, 24.58, 4.67, False, '', '', 0, 0),
                    ('hip_6193', '' if is_ar else 'HIP 6193', 19.87, 27.26, 4.74, False, '', '', 0, 0),
                    ('hip_7097', '' if is_ar else 'HIP 7097', 22.87, 15.35, 3.62, False, '', '', 0, 0),
                    ('hip_8198', '' if is_ar else 'HIP 8198', 26.35, 9.16, 4.26, False, '', '', 0, 0),
                    ('alrescha', 'الرشاء' if is_ar else 'Alrescha', 30.51, 2.76, 3.82, True, 'center', 'bottom', 0.0, 0.045),
                    ('hip_8833', '' if is_ar else 'HIP 8833', 28.39, 3.19, 4.61, False, '', '', 0, 0),
                    ('hip_7884', '' if is_ar else 'HIP 7884', 25.36, 5.49, 4.45, False, '', '', 0, 0),
                    ('hip_7007', '' if is_ar else 'HIP 7007', 22.55, 6.14, 4.84, False, '', '', 0, 0),
                    ('hip_4906', '' if is_ar else 'HIP 4906', 15.74, 7.89, 4.27, False, '', '', 0, 0),
                    ('hip_3786', '' if is_ar else 'HIP 3786', 12.17, 7.59, 4.44, False, '', '', 0, 0),
                    ('hip_1645', '' if is_ar else 'HIP 1645', 5.15, 8.19, 5.38, False, '', '', 0, 0),
                    ('hip_118268', '' if is_ar else 'HIP 118268', 359.83, 6.86, 4.03, False, '', '', 0, 0),
                    ('hip_116771', '' if is_ar else 'HIP 116771', 354.99, 5.63, 4.13, False, '', '', 0, 0),
                    ('hip_116928', '' if is_ar else 'HIP 116928', 355.51, 1.78, 4.49, False, '', '', 0, 0),
                    ('hip_115738', '' if is_ar else 'HIP 115738', 351.73, 1.26, 4.95, False, '', '', 0, 0),
                    ('hip_114971', '' if is_ar else 'HIP 114971', 349.29, 3.28, 3.7, False, '', '', 0, 0),
                    ('hip_115830', '' if is_ar else 'HIP 115830', 351.99, 6.38, 4.27, False, '', '', 0, 0),
                ],
                'lines': [
                    ('hip_4889', 'hip_5742'),
                    ('hip_4889', 'hip_6193'),
                    ('hip_6193', 'hip_5742'),
                    ('hip_5742', 'hip_7097'),
                    ('hip_7097', 'hip_8198'),
                    ('hip_8198', 'alrescha'),
                    ('alrescha', 'hip_8833'),
                    ('hip_8833', 'hip_7884'),
                    ('hip_7884', 'hip_7007'),
                    ('hip_7007', 'hip_4906'),
                    ('hip_4906', 'hip_3786'),
                    ('hip_3786', 'hip_1645'),
                    ('hip_1645', 'hip_118268'),
                    ('hip_118268', 'hip_116771'),
                    ('hip_116771', 'hip_116928'),
                    ('hip_116928', 'hip_115738'),
                    ('hip_115738', 'hip_114971'),
                    ('hip_114971', 'hip_115830'),
                    ('hip_115830', 'hip_116771'),
                ]
            },
            {
                'id': 'virgo',
                'name': ArabicFormatter.reshape_text('العذراء') if is_ar else 'Virgo',
                'label_pos': (187.0, -10.0),
                'stars': [
                    ('hip_57380', '' if is_ar else 'HIP 57380', 176.46, 6.53, 4.04, False, '', '', 0, 0),
                    ('hip_60030', '' if is_ar else 'HIP 60030', 184.67, -0.79, 5.9, False, '', '', 0, 0),
                    ('porrima', 'زاوية العذراء' if is_ar else 'Porrima', 190.42, -1.45, 2.74, False, '', '', 0, 0),
                    ('spica', 'السماك الأعزل' if is_ar else 'Spica', 201.3, -11.16, 0.98, True, 'right', 'center', 0.0, 0.045),
                    ('hip_69427', '' if is_ar else 'HIP 69427', 213.22, -10.27, 4.18, False, '', '', 0, 0),
                    ('syrma', 'سرما' if is_ar else 'Syrma', 214.0, -6.0, 4.07, False, '', '', 0, 0),
                    ('hip_71957', '' if is_ar else 'HIP 71957', 220.77, -5.66, 3.87, False, '', '', 0, 0),
                    ('hip_66249', '' if is_ar else 'HIP 66249', 203.67, -0.6, 3.38, False, '', '', 0, 0),
                    ('hip_68520', '' if is_ar else 'HIP 68520', 210.41, 1.54, 4.23, False, '', '', 0, 0),
                    ('hip_72220', '' if is_ar else 'HIP 72220', 221.56, 1.89, 3.73, False, '', '', 0, 0),
                    ('hip_63090', '' if is_ar else 'HIP 63090', 193.9, 3.4, 3.39, False, '', '', 0, 0),
                    ('vindemiatrix', 'مقدم القطاف' if is_ar else 'Vindemiatrix', 195.54, 10.96, 2.85, True, 'center', 'bottom', 0.0, 0.075),
                ],
                'lines': [
                    ('hip_57380', 'hip_60030'),
                    ('hip_60030', 'porrima'),
                    ('porrima', 'spica'),
                    ('spica', 'hip_69427'),
                    ('hip_69427', 'syrma'),
                    ('syrma', 'hip_71957'),
                    ('spica', 'hip_66249'),
                    ('hip_66249', 'hip_68520'),
                    ('hip_68520', 'hip_72220'),
                    ('hip_66249', 'hip_63090'),
                    ('hip_63090', 'vindemiatrix'),
                    ('hip_63090', 'porrima'),
                ]
            },
            {
                'id': 'aries',
                'name': ArabicFormatter.reshape_text('الحمل') if is_ar else 'Aries',
                'label_pos': (33.0, 15.0),
                'stars': [
                    ('botein', 'البطين' if is_ar else 'Botein', 42.5, 27.26, 3.61, True, 'center', 'top', 0.0, 0.035),
                    ('hamal', 'الناطح' if is_ar else 'Hamal', 31.79, 23.46, 2.01, True, 'right', 'top', 0.0, -0.05),
                    ('sheratan', 'الشرطان' if is_ar else 'Sheratan', 28.66, 20.81, 2.64, True, 'center', 'bottom', 0.0, 0.035),
                    ('hip_8832', '' if is_ar else 'HIP 8832', 28.38, 19.29, 3.88, False, '', '', 0, 0),
                ],
                'lines': [
                    ('botein', 'hamal'),
                    ('hamal', 'sheratan'),
                    ('sheratan', 'hip_8832'),
                ]
            },
            {
                'id': 'cancer',
                'name': ArabicFormatter.reshape_text('السرطان') if is_ar else 'Cancer',
                'label_pos': (128.0, 15.0),
                'stars': [
                    ('hip_43103', '' if is_ar else 'HIP 43103', 131.67, 28.76, 4.03, False, '', '', 0, 0),
                    ('hip_42806', '' if is_ar else 'HIP 42806', 130.82, 21.47, 4.66, False, '', '', 0, 0),
                    ('hip_40843', '' if is_ar else 'HIP 40843', 125.02, 27.22, 5.13, False, '', '', 0, 0),
                    ('asellus_aust', 'النثرة' if is_ar else 'Nathrah / Asellus', 131.17, 18.15, 3.94, True, 'center', 'top', 0.0, 0.04),
                    ('acubens', 'الزبانى' if is_ar else 'Acubens', 124.13, 9.19, 3.53, False, '', '', 0, 0),
                    ('hip_44066', '' if is_ar else 'HIP 44066', 134.62, 11.86, 4.26, False, '', '', 0, 0),
                ],
                'lines': [
                    ('hip_43103', 'hip_42806'),
                    ('hip_42806', 'hip_40843'),
                    ('hip_42806', 'asellus_aust'),
                    ('asellus_aust', 'acubens'),
                    ('asellus_aust', 'hip_44066'),
                ]
            },
            {
                'id': 'libra',
                'name': ArabicFormatter.reshape_text('الميزان') if is_ar else 'Libra',
                'label_pos': (228.0, -18.0),
                'stars': [
                    ('hip_77853', '' if is_ar else 'HIP 77853', 238.46, -16.73, 4.13, False, '', '', 0, 0),
                    ('hip_76333', '' if is_ar else 'HIP 76333', 233.88, -14.79, 3.91, False, '', '', 0, 0),
                    ('zubeneschamali', 'الزبانى الشمالي' if is_ar else 'Zubeneschamali', 229.25, -9.38, 2.61, True, 'center', 'top', 0.0, 0.04),
                    ('zubenelgenubi', 'الزبانى الجنوبي' if is_ar else 'Zubenelgenubi', 222.72, -16.04, 2.75, True, 'center', 'bottom', 0.0, -0.04),
                    ('hip_73714', '' if is_ar else 'HIP 73714', 226.02, -25.28, 3.25, False, '', '', 0, 0),
                ],
                'lines': [
                    ('hip_77853', 'hip_76333'),
                    ('hip_76333', 'zubeneschamali'),
                    ('zubeneschamali', 'zubenelgenubi'),
                    ('zubenelgenubi', 'hip_73714'),
                    ('hip_73714', 'hip_76333'),
                ]
            },
            {
                'id': 'sagittarius',
                'name': ArabicFormatter.reshape_text('القوس') if is_ar else 'Sagittarius',
                'label_pos': (285.0, -28.0),
                'stars': [
                    ('hip_89931', '' if is_ar else 'HIP 89931', 275.25, -29.83, 2.72, False, '', '', 0, 0),
                    ('hip_90496', '' if is_ar else 'HIP 90496', 276.99, -25.42, 2.82, False, '', '', 0, 0),
                    ('hip_89642', '' if is_ar else 'HIP 89642', 274.41, -36.76, 3.1, False, '', '', 0, 0),
                    ('kaus_australis', 'قوس جنوبي' if is_ar else 'Kaus Australis', 276.04, -34.38, 1.79, True, 'center', 'bottom', 0.0, 0.04),
                    ('hip_88635', '' if is_ar else 'HIP 88635', 271.45, -30.42, 2.98, False, '', '', 0, 0),
                    ('cebalrai', 'كلب الراعي' if is_ar else 'Cebalrai', 266.89, -27.83, 4.53, False, '', '', 0, 0),
                    ('hip_93506', '' if is_ar else 'HIP 93506', 285.65, -29.88, 2.6, False, '', '', 0, 0),
                    ('hip_92041', '' if is_ar else 'HIP 92041', 281.41, -26.99, 3.17, False, '', '', 0, 0),
                    ('hip_89341', '' if is_ar else 'HIP 89341', 273.44, -21.06, 3.84, False, '', '', 0, 0),
                    ('hip_93864', '' if is_ar else 'HIP 93864', 286.74, -27.67, 3.32, False, '', '', 0, 0),
                    ('nunki', 'النعائم / نونكي' if is_ar else 'Nunki', 283.82, -26.3, 2.05, True, 'center', 'top', 0.0, 0.04),
                    ('hip_93085', '' if is_ar else 'HIP 93085', 284.43, -21.11, 3.52, False, '', '', 0, 0),
                    ('hip_93683', '' if is_ar else 'HIP 93683', 286.17, -21.74, 3.76, False, '', '', 0, 0),
                    ('hip_94820', '' if is_ar else 'HIP 94820', 289.41, -18.95, 4.88, False, '', '', 0, 0),
                    ('hip_95168', '' if is_ar else 'HIP 95168', 290.42, -17.85, 3.92, False, '', '', 0, 0),
                    ('hip_96406', '' if is_ar else 'HIP 96406', 294.01, -24.72, 5.64, False, '', '', 0, 0),
                    ('hip_98688', '' if is_ar else 'HIP 98688', 300.66, -27.71, 4.43, False, '', '', 0, 0),
                    ('hip_98412', '' if is_ar else 'HIP 98412', 299.93, -35.28, 4.37, False, '', '', 0, 0),
                    ('hip_98032', '' if is_ar else 'HIP 98032', 298.82, -41.87, 4.12, False, '', '', 0, 0),
                    ('hip_95347', '' if is_ar else 'HIP 95347', 290.97, -40.62, 3.96, False, '', '', 0, 0),
                    ('hip_95294', '' if is_ar else 'HIP 95294', 290.8, -44.8, 4.27, False, '', '', 0, 0),
                ],
                'lines': [
                    ('hip_89931', 'hip_90496'),
                    ('hip_89642', 'kaus_australis'),
                    ('kaus_australis', 'hip_88635'),
                    ('hip_88635', 'cebalrai'),
                    ('hip_88635', 'hip_89931'),
                    ('hip_89931', 'kaus_australis'),
                    ('kaus_australis', 'hip_93506'),
                    ('hip_93506', 'hip_92041'),
                    ('hip_92041', 'hip_89931'),
                    ('hip_92041', 'hip_90496'),
                    ('hip_90496', 'hip_89341'),
                    ('hip_93506', 'hip_93864'),
                    ('hip_93864', 'nunki'),
                    ('nunki', 'hip_92041'),
                    ('nunki', 'hip_93085'),
                    ('hip_93085', 'hip_93683'),
                    ('hip_93683', 'hip_94820'),
                    ('hip_94820', 'hip_95168'),
                    ('hip_93864', 'hip_96406'),
                    ('hip_96406', 'hip_98688'),
                    ('hip_98688', 'hip_98412'),
                    ('hip_98412', 'hip_98032'),
                    ('hip_98032', 'hip_95347'),
                    ('hip_98032', 'hip_95294'),
                ]
            },
            {
                'id': 'capricornus',
                'name': ArabicFormatter.reshape_text('الجدي') if is_ar else 'Capricornus',
                'label_pos': (315.0, -20.0),
                'stars': [
                    ('algedi', 'الجدي' if is_ar else 'Algedi', 304.51, -12.54, 3.58, True, 'center', 'top', 0.0, 0.04),
                    ('dabih', 'سعد الذابح' if is_ar else 'Dabih', 305.25, -14.78, 3.05, True, 'center', 'bottom', 0.0, -0.04),
                    ('hip_104139', '' if is_ar else 'HIP 104139', 316.49, -17.23, 4.08, False, '', '', 0, 0),
                    ('hip_105515', '' if is_ar else 'HIP 105515', 320.56, -16.83, 4.28, False, '', '', 0, 0),
                    ('hip_106985', '' if is_ar else 'HIP 106985', 325.02, -16.66, 3.69, False, '', '', 0, 0),
                    ('hip_107556', '' if is_ar else 'HIP 107556', 326.76, -16.13, 2.85, False, '', '', 0, 0),
                    ('hip_105881', '' if is_ar else 'HIP 105881', 321.67, -22.41, 3.77, False, '', '', 0, 0),
                    ('hip_102485', '' if is_ar else 'HIP 102485', 311.52, -25.27, 4.13, False, '', '', 0, 0),
                    ('hip_102978', '' if is_ar else 'HIP 102978', 312.96, -26.92, 4.12, False, '', '', 0, 0),
                ],
                'lines': [
                    ('algedi', 'dabih'),
                    ('dabih', 'hip_104139'),
                    ('hip_104139', 'hip_105515'),
                    ('hip_105515', 'hip_106985'),
                    ('hip_106985', 'hip_107556'),
                    ('hip_105515', 'hip_105881'),
                    ('hip_105881', 'hip_104139'),
                    ('dabih', 'hip_102485'),
                    ('hip_104139', 'hip_102978'),
                ]
            },
            {
                'id': 'aquarius',
                'name': ArabicFormatter.reshape_text('الدلو') if is_ar else 'Aquarius',
                'label_pos': (335.0, -10.0),
                'stars': [
                    ('sadalsuud', 'سعد السعود' if is_ar else 'Sadalsuud', 322.89, -5.57, 2.9, True, 'center', 'top', 0.0, 0.04),
                    ('sadalmelik', 'سعد الملك' if is_ar else 'Sadalmelik', 331.45, -0.32, 2.95, False, '', '', 0, 0),
                    ('sadachbia', 'سعد الأخبية' if is_ar else 'Sadachbia', 335.41, -1.39, 3.86, True, 'center', 'bottom', 0.0, -0.04),
                    ('hip_110960', '' if is_ar else 'HIP 110960', 337.21, -0.02, 3.65, False, '', '', 0, 0),
                    ('hip_111497', '' if is_ar else 'HIP 111497', 338.84, -0.12, 4.04, False, '', '', 0, 0),
                    ('hip_112961', '' if is_ar else 'HIP 112961', 343.15, -7.58, 3.73, False, '', '', 0, 0),
                    ('hip_114855', '' if is_ar else 'HIP 114855', 348.97, -9.09, 4.24, False, '', '', 0, 0),
                    ('hip_115438', '' if is_ar else 'HIP 115438', 350.74, -20.1, 3.96, False, '', '', 0, 0),
                    ('hip_110003', '' if is_ar else 'HIP 110003', 334.21, -7.78, 4.17, False, '', '', 0, 0),
                    ('hip_109139', '' if is_ar else 'HIP 109139', 331.61, -13.87, 4.29, False, '', '', 0, 0),
                    ('hip_111123', '' if is_ar else 'HIP 111123', 337.66, -10.68, 4.82, False, '', '', 0, 0),
                    ('hip_112716', '' if is_ar else 'HIP 112716', 342.4, -13.59, 4.05, False, '', '', 0, 0),
                    ('hip_113136', '' if is_ar else 'HIP 113136', 343.66, -15.82, 3.27, False, '', '', 0, 0),
                    ('hip_114341', '' if is_ar else 'HIP 114341', 347.36, -21.17, 3.68, False, '', '', 0, 0),
                    ('albali', 'سعد بلع' if is_ar else 'Albali', 311.92, -9.5, 3.78, True, 'center', 'top', 0.0, 0.035),
                ],
                'lines': [
                    ('sadalsuud', 'sadalmelik'),
                    ('sadalmelik', 'sadachbia'),
                    ('sadachbia', 'hip_110960'),
                    ('hip_110960', 'hip_111497'),
                    ('hip_111497', 'hip_112961'),
                    ('hip_112961', 'hip_114855'),
                    ('hip_114855', 'hip_115438'),
                    ('sadalmelik', 'hip_110003'),
                    ('hip_110003', 'hip_109139'),
                    ('hip_110003', 'hip_111123'),
                    ('hip_111123', 'hip_112716'),
                    ('hip_112716', 'hip_113136'),
                    ('hip_113136', 'hip_114341'),
                    ('albali', 'sadalsuud'),
                ]
            },
            {
                'id': 'pleiades',
                'name': ArabicFormatter.reshape_text('الثريا') if is_ar else 'Pleiades',
                'label_pos': (48.0, 42.0),
                'stars': [
                    ('alcyone', '' if is_ar else 'Alcyone', 56.87, 24.11, 2.85, True, 'center', 'top', 0.0, 0.035),
                    ('electra', 'إلكترا' if is_ar else 'Electra', 56.22, 24.1, 3.72, False, '', '', 0, 0),
                    ('maia', 'مايا' if is_ar else 'Maia', 56.49, 24.37, 3.87, False, '', '', 0, 0),
                    ('merope', 'ميروبي' if is_ar else 'Merope', 56.71, 23.95, 4.14, False, '', '', 0, 0),
                    ('taygeta', 'تايغيتا' if is_ar else 'Taygeta', 56.29, 24.47, 4.3, False, '', '', 0, 0),
                    ('atlas', 'أطلس' if is_ar else 'Atlas', 57.29, 24.05, 3.62, False, '', '', 0, 0),
                ],
                'lines': [
                    ('electra', 'taygeta'),
                    ('taygeta', 'maia'),
                    ('maia', 'alcyone'),
                    ('alcyone', 'atlas'),
                    ('alcyone', 'merope'),
                    ('merope', 'electra'),
                ]
            },
        ]
        overrides = self._load_label_overrides()
        star_ov = overrides.get('stars', {})
        const_ov = overrides.get('constellations', {})
        for c in data:
            cid = c.get('id')
            if cid in const_ov:
                if 'label_pos' in const_ov[cid]:
                    c['label_pos'] = tuple(const_ov[cid]['label_pos'])
            new_stars = []
            for s in c['stars']:
                sid = s[0]
                s_name = s[1]
                ra = s[2]
                dec = s[3]
                mag = s[4]
                show_lbl = s[5] if len(s) > 5 else False
                ha = s[6] if len(s) > 6 else 'center'
                va = s[7] if len(s) > 7 else 'center'
                ox = s[8] if len(s) > 8 else 0.0
                oy = s[9] if len(s) > 9 else 0.0

                if sid in star_ov:
                    ov = star_ov[sid]
                    ox = ov.get('ox', ox)
                    oy = ov.get('oy', oy)
                    ha = ov.get('ha', ha)
                    va = ov.get('va', va)
                    show_lbl = ov.get('show_lbl', show_lbl)
                new_stars.append((sid, s_name, ra, dec, mag, show_lbl, ha, va, ox, oy))
            c['stars'] = new_stars
        return data

    def _build_standalone_stars(self):
        is_ar = str(self.language).lower().startswith('ar')
        stars = [
            ('alphecca', 'الفكة' if is_ar else 'Alphecca', 233.67, 26.71, 2.22, 'center', 'top', 0.0, 0.040),
            ('algol', 'رأس الغول' if is_ar else 'Algol', 47.11, 40.96, 2.12, 'center', 'top', 0.0, 0.040),
        ]
        overrides = self._load_label_overrides()
        star_ov = overrides.get('stars', {})
        res = []
        for sid, s_name, ra, dec, mag, ha, va, ox, oy in stars:
            if sid in star_ov:
                ov = star_ov[sid]
                ox = ov.get('ox', ox)
                oy = ov.get('oy', oy)
                ha = ov.get('ha', ha)
                va = ov.get('va', va)
            res.append((s_name, ra, dec, mag, ha, va, ox, oy))
        return res

    def _collect_all_stars(self):
        stars_list = []
        for c in self.constellations:
            for sid, s_name, ra, dec, mag, show_lbl, ha, va, ox, oy in c['stars']:
                if show_lbl:
                    stars_list.append(Star(s_name, ra, dec, raw_name=s_name, mag=mag, screen_mode=self.screen_mode))
        for s_name, ra, dec, mag, ha, va, ox, oy in self.standalone_stars:
            stars_list.append(Star(s_name, ra, dec, raw_name=s_name, mag=mag, screen_mode=self.screen_mode))
        return stars_list

    def _star_xy(self, ra_deg, dec_deg):
        dec = np.deg2rad(dec_deg)
        r = self.proj.R * np.tan((np.pi / 2.0 - dec) / 2.0)
        ra = np.deg2rad(ra_deg)
        return r * np.cos(ra), r * np.sin(ra)

    def draw(self, ax):
        r_cap = self.proj.r_capricorn
        
        # 1. Constellation Lines (zorder 1, celestial slate blue fine lines)
        line_color = '#385D7A' if self.screen_mode else '#2B4C66'
        lw_line = 0.55 if self.screen_mode else 0.45
        for c in self.constellations:
            c_stars = {s[0]: self._star_xy(s[2], s[3]) for s in c['stars']}
            for id1, id2 in c['lines']:
                if id1 in c_stars and id2 in c_stars:
                    p1 = c_stars[id1]
                    p2 = c_stars[id2]
                    if np.hypot(p1[0], p1[1]) <= r_cap * 1.005 and np.hypot(p2[0], p2[1]) <= r_cap * 1.005:
                        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=line_color, 
                                linewidth=lw_line, linestyle='-', alpha=0.75, zorder=1)

        # 2. Constellation Stars (dots zorder 2, labels zorder 3)
        fs_star = 3.2 if self.screen_mode else 2.6
        stroke_star = 0.8
        for c in self.constellations:
            for sid, s_name, s_ra, s_dec, s_mag, show_lbl, ha, va, ox, oy in c['stars']:
                xp, yp = self._star_xy(s_ra, s_dec)
                r = np.hypot(xp, yp)
                if r <= r_cap * 1.005:
                    ms = max(1.1, 2.7 - 0.40 * s_mag) if self.screen_mode else max(0.9, 2.3 - 0.35 * s_mag)
                    # Subtle celestial glow only for brightest 1st-magnitude stars
                    if s_mag <= 1.2:
                        ax.plot(xp, yp, 'o', color='#385D7A', markersize=ms * 1.35, alpha=0.18, zorder=2)
                    ax.plot(xp, yp, 'o', color='#111111', markersize=ms, zorder=2)
                    if show_lbl:
                        lbl = ArabicFormatter.reshape_text(s_name) if str(self.language).lower().startswith('ar') else s_name
                        th = np.arctan2(yp, xp)
                        rot = np.rad2deg(th) + 90
                        if sid == 'polaris' or 'القطب' in s_name:
                            ax.text(xp + ox, yp + (oy if oy != 0.0 else 0.065), lbl,
                                    fontsize=fs_star + 0.4, fontweight='bold',
                                    ha='center', va='bottom', rotation=0, color='#111111', zorder=3,
                                    path_effects=[pe.withStroke(linewidth=stroke_star, foreground='white')])
                        else:
                            dr = oy if (oy != 0.0 or ox != 0.0) else 0.024
                            dt = ox
                            xl = (r + dr) * np.cos(th) - dt * np.sin(th)
                            yl = (r + dr) * np.sin(th) + dt * np.cos(th)
                            ax.text(xl, yl, lbl, fontsize=fs_star,
                                    fontweight='normal',
                                    ha=ha if ha else 'center', va=va if va else 'center',
                                    rotation=rot, rotation_mode='anchor',
                                    color='#111111', zorder=3,
                                    path_effects=[pe.withStroke(linewidth=stroke_star, foreground='white')])

        # 3. Standalone Astrolabe Stars
        fs_stand = 3.2 if self.screen_mode else 2.6
        for s_name, s_ra, s_dec, s_mag, ha, va, ox, oy in self.standalone_stars:
            xp, yp = self._star_xy(s_ra, s_dec)
            r = np.hypot(xp, yp)
            if r <= r_cap * 1.005:
                ms = max(1.1, 2.7 - 0.40 * s_mag) if self.screen_mode else max(0.9, 2.3 - 0.35 * s_mag)
                if s_mag <= 1.2:
                    ax.plot(xp, yp, 'o', color='#385D7A', markersize=ms * 1.35, alpha=0.18, zorder=2)
                ax.plot(xp, yp, 'o', color='#111111', markersize=ms, zorder=2)
                th = np.arctan2(yp, xp)
                rot = np.rad2deg(th) + 90
                dr = oy if (oy != 0.0 or ox != 0.0) else 0.024
                dt = ox
                xl = (r + dr) * np.cos(th) - dt * np.sin(th)
                yl = (r + dr) * np.sin(th) + dt * np.cos(th)
                lbl = ArabicFormatter.reshape_text(s_name) if str(self.language).lower().startswith('ar') else s_name
                ax.text(xl, yl, lbl, fontsize=fs_stand,
                        fontweight='normal',
                        ha=ha if ha else 'center', va=va if va else 'center',
                        rotation=rot, rotation_mode='anchor',
                        color='#111111', zorder=3,
                        path_effects=[pe.withStroke(linewidth=stroke_star, foreground='white')])

        # 4. Constellation Names in distinct deep lapis lazuli / celestial navy color (zorder 3)
        const_color = '#0B3C5D'
        fs_const = 3.8 if self.screen_mode else 3.2
        stroke_const = 1.0
        for c in self.constellations:
            cra, cdec = c['label_pos']
            cx, cy = self._star_xy(cra, cdec)
            if np.hypot(cx, cy) <= r_cap * 0.96:
                rot = np.rad2deg(np.arctan2(cy, cx)) + 90
                ax.text(cx, cy, c['name'], fontsize=fs_const, fontweight='bold',
                        color=const_color, ha='center', va='center',
                        rotation=rot, rotation_mode='anchor', zorder=3,
                        path_effects=[pe.withStroke(linewidth=stroke_const, foreground='white')])

        # 5. Structural Capricorn outer ring (double rim)
        ax.add_patch(plt.Circle((0, 0), r_cap, color='#111111', fill=False, linewidth=2.0, zorder=4))
        ax.add_patch(plt.Circle((0, 0), r_cap * 0.990, color='#111111', fill=False, linewidth=0.7, zorder=4))
        
        # 6. Central collar around North celestial pole & drill hole for pivot
        ax.add_patch(plt.Circle((0, 0), 0.06, color='#111111', fill=False, linewidth=1.4 if self.screen_mode else 1.2, zorder=4))
        ax.plot([-0.04 * r_cap, 0.04 * r_cap], [0, 0], color='#111111', linewidth=0.6, zorder=4)
        ax.plot([0, 0], [-0.04 * r_cap, 0.04 * r_cap], color='#111111', linewidth=0.6, zorder=4)
        ax.add_patch(plt.Circle((0, 0), 0.02 * r_cap, color='#111111', fill=False, linewidth=0.8, zorder=4))
        
        # 7. Equator structural arc
        th = np.linspace(0, 2 * np.pi, 200)
        ax.plot(self.proj.R * np.sin(th), -self.proj.R * np.cos(th), 
                color='#444444', linewidth=0.7 if self.screen_mode else 0.5, linestyle=':', zorder=3)
        
        # 8. Ecliptic circle with Zodiac (zorder 5 to 7)
        self.ecliptic.draw(ax)



