"""
Astrolabe Back (Dorsum / ظهر الأسطرلاب).
Renders the back face of the astrolabe: altitude scales, zodiac-calendar scales,
shadow square, unequal hours curves, and astrological triplicities.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe

from .arabic import ArabicFormatter
from .projection import StereographicProjection
from .tympan import Kursi


def get_tangential_rotation(deg_polar):
    """Guaranteed upright tangential rotation along circular arc."""
    deg = deg_polar % 360.0
    if 0.0 <= deg <= 180.0:
        return deg - 90.0
    else:
        return deg - 270.0


class AstrolabeBack:
    """
    Master representation of the Back of the Astrolabe (ظهر الأسطرلاب).
    Authentically incorporates:
    1. Altitude Scale (حافة الزوايا والارتفاع) on the upper quadrants (0° to 90°).
    2. Zodiac Scale (طوق فلك البروج) with 12 signs of 30° each.
    3. Civil Calendar Scale (طوق الشهور والأيام) with 12 months & 365 days.
    4. Equation of Time Scale & Analemma Curve (رسم وسُلّم ومنحنى معادلة الوقت بالدقائق).
    5. Sine Quadrant (ربع المجيب بشبكة الجيوب 60 جزءاً).
    6. Unequal Hours & Prayer Times Arcs (ربع الساعات الزمانية والظهر والعصر).
    7. Shadow Square (مربّع الظلّين المبسوط والمنكوس 12 إصبعاً).
    """
    def __init__(self, proj=None, language='arabic', numeral_system='abjad', latitude=35.78,
                 city="Tangier", show_kursi=False, screen_mode=False):
        self.proj = proj or StereographicProjection()
        self.language = language
        self.numeral_system = numeral_system
        self.latitude_deg = float(latitude)
        self.latitude = np.deg2rad(self.latitude_deg)
        self.city = city
        self.show_kursi = show_kursi
        self.screen_mode = screen_mode
        if self.show_kursi:
            self.kursi = Kursi(self.proj, city=self.city, language=self.language, screen_mode=self.screen_mode)

    def draw(self, ax, color='black'):
        r_cap = self.proj.r_capricorn
        r_outer = r_cap * 1.250
        r_alt_in = r_cap * 1.140
        r_zod_in = r_cap * 1.035
        r_cal_in = r_cap * 0.925
        r_quad_in = r_cal_in

        # Draw Kursi on the back if enabled
        if getattr(self, 'show_kursi', False):
            if not hasattr(self, 'kursi') or self.kursi is None:
                self.kursi = Kursi(self.proj, city=self.city, language=self.language, screen_mode=self.screen_mode)
            self.kursi.draw(ax, side='back', color='#0B3C5D' if self.screen_mode else color)

        # Concentric rings
        rings = [(r_outer, 2.2 if self.screen_mode else 2.0), 
                 (r_alt_in, 1.1 if self.screen_mode else 0.9), 
                 (r_zod_in, 1.1 if self.screen_mode else 0.9), 
                 (r_cal_in, 1.4 if self.screen_mode else 1.2)]
        if not getattr(self, 'show_kursi', False):
            rings.insert(0, (r_outer * 1.008, 0.6))

        for r, lw in rings:
            ax.add_patch(plt.Circle((0, 0), r, color=color, fill=False, linewidth=lw))

        # Main orthogonal axes
        ax.plot([-r_outer, r_outer], [0, 0], color=color, linewidth=1.1 if self.screen_mode else 0.9)
        ax.plot([0, 0], [-r_outer, r_outer], color=color, linewidth=1.1 if self.screen_mode else 0.9)

        # -------------------------------------------------------------
        # 1. ALTITUDE SCALE (حافة الزوايا والارتفاع) on Limb
        # -------------------------------------------------------------
        band_alt = r_outer - r_alt_in
        fs_alt = 8.5 if self.screen_mode else 6.8
        stroke_alt = 2.0 if self.screen_mode else 1.2
        for deg in range(360):
            rad = np.deg2rad(deg)
            cos_a, sin_a = np.cos(rad), np.sin(rad)

            if 0 <= deg < 90:
                alt = deg
            elif 90 <= deg < 180:
                alt = 180 - deg
            elif 180 <= deg < 270:
                alt = deg - 180
            else:
                alt = 360 - deg

            is_major = (alt % 10 == 0)
            is_mid = (alt % 5 == 0) and not is_major

            if is_major:
                r_in = r_alt_in
            elif is_mid:
                r_in = r_alt_in + band_alt * 0.40
            else:
                r_in = r_alt_in + band_alt * 0.68

            ax.plot([r_in * cos_a, r_outer * cos_a], [r_in * sin_a, r_outer * sin_a],
                    color=color, linewidth=1.0 if is_major else (0.5 if is_mid else 0.35))

            if is_major and alt > 0:
                lbl = ArabicFormatter.format_number(alt, self.numeral_system)
                r_txt = r_alt_in + band_alt * 0.45
                rot = get_tangential_rotation(deg)
                ax.text(r_txt * cos_a, r_txt * sin_a, lbl,
                        fontsize=fs_alt, fontweight='bold' if self.screen_mode else 'normal',
                        ha='center', va='center', rotation=rot,
                        color=color, path_effects=[pe.withStroke(linewidth=stroke_alt, foreground='white')])

        # Cardinal Labels on the outer rim
        cardinals = [
            (0, "المغرب"),
            (90, "سمت الرأس"),
            (180, "المشرق"),
            (270, "سمت القدم")
        ] if str(self.language).lower().startswith('ar') else [
            (0, "West"),
            (90, "Zenith"),
            (180, "East"),
            (270, "Nadir")
        ]
        fs_card = 10.5 if self.screen_mode else 8.5
        stroke_card = 2.8 if self.screen_mode else 1.8
        for c_deg, c_txt in cardinals:
            c_rad = np.deg2rad(c_deg)
            c_cos, c_sin = np.cos(c_rad), np.sin(c_rad)
            r_c = r_alt_in + band_alt * 0.48
            t_reshaped = ArabicFormatter.reshape_text(c_txt) if str(self.language).lower().startswith('ar') else c_txt
            rot = get_tangential_rotation(c_deg)
            ax.text(r_c * c_cos, r_c * c_sin, t_reshaped,
                    fontsize=fs_card, fontweight='bold', color='#8B0000',
                    ha='center', va='center', rotation=rot,
                    path_effects=[pe.withStroke(linewidth=stroke_card, foreground='white')])

        # -------------------------------------------------------------
        # 2. ZODIAC SCALE (طوق فلك البروج) (r_zod_in to r_alt_in)
        # -------------------------------------------------------------
        zodiac_names_ar = [
            'الحمل', 'الثور', 'الجوزاء', 'السرطان', 'الأسد', 'السنبلة',
            'الميزان', 'العقرب', 'القوس', 'الجدي', 'الدلو', 'الحوت'
        ]
        zodiac_names_lat = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        z_names = zodiac_names_ar if str(self.language).lower().startswith('ar') else zodiac_names_lat
        band_zod = r_alt_in - r_zod_in
        fs_zod_num = 7.0 if self.screen_mode else 5.5
        fs_zod_name = 9.5 if self.screen_mode else 7.8
        stroke_zod = 2.2 if self.screen_mode else 1.4

        for i in range(12):
            sign_start = i * 30.0
            th_rad = np.deg2rad(sign_start)
            ax.plot([r_zod_in * np.cos(th_rad), r_alt_in * np.cos(th_rad)],
                    [r_zod_in * np.sin(th_rad), r_alt_in * np.sin(th_rad)],
                    color=color, linewidth=1.1 if self.screen_mode else 0.9)

            for d in range(1, 30):
                d_rad = np.deg2rad(sign_start + d)
                c_d, s_d = np.cos(d_rad), np.sin(d_rad)
                if d % 10 == 0:
                    r_tick = r_zod_in + band_zod * 0.45
                    lw_t = 0.8 if self.screen_mode else 0.7
                    num_str = ArabicFormatter.format_number(d, self.numeral_system)
                    r_num = r_zod_in + band_zod * 0.22
                    rot_d = get_tangential_rotation(sign_start + d)
                    ax.text(r_num * c_d, r_num * s_d, num_str,
                            fontsize=fs_zod_num, fontweight='bold' if self.screen_mode else 'normal',
                            ha='center', va='center', rotation=rot_d,
                            color=color, path_effects=[pe.withStroke(linewidth=1.4 if self.screen_mode else 0.8, foreground='white')])
                elif d % 5 == 0:
                    r_tick = r_zod_in + band_zod * 0.65
                    lw_t = 0.55 if self.screen_mode else 0.5
                else:
                    r_tick = r_zod_in + band_zod * 0.82
                    lw_t = 0.35
                ax.plot([r_tick * c_d, r_alt_in * c_d], [r_tick * s_d, r_alt_in * s_d],
                        color=color, linewidth=lw_t)

            mid_deg = sign_start + 15.0
            mid_rad = np.deg2rad(mid_deg)
            r_name = r_zod_in + band_zod * 0.68
            rot_name = get_tangential_rotation(mid_deg)
            z_txt = ArabicFormatter.reshape_text(z_names[i]) if str(self.language).lower().startswith('ar') else z_names[i]
            ax.text(r_name * np.cos(mid_rad), r_name * np.sin(mid_rad), z_txt,
                    fontsize=fs_zod_name, fontweight='bold', color='#4A235A',
                    ha='center', va='center', rotation=rot_name,
                    path_effects=[pe.withStroke(linewidth=stroke_zod, foreground='white')])

        # -------------------------------------------------------------
        # 3. CIVIL CALENDAR SCALE (طوق الشهور والأيام) (r_cal_in to r_zod_in)
        # -------------------------------------------------------------
        month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        month_names_ar = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                          'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        month_names_lat = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        m_names = month_names_ar if str(self.language).lower().startswith('ar') else month_names_lat
        band_cal = r_zod_in - r_cal_in
        fs_cal_num = 6.8 if self.screen_mode else 5.2
        fs_cal_name = 9.2 if self.screen_mode else 7.5
        stroke_cal = 2.2 if self.screen_mode else 1.4

        def day_to_angle(day):
            n = day - 79.25
            L = (n * 0.985647) % 360.0
            g = np.deg2rad((357.528 + 0.9856003 * (day - 1)) % 360.0)
            lam = (L + 1.915 * np.sin(g) + 0.02 * np.sin(2 * g) + 360.0) % 360.0
            return lam

        day_cum = 1
        for m_idx, m_days in enumerate(month_lengths):
            th_m_start = np.deg2rad(day_to_angle(day_cum))
            ax.plot([r_cal_in * np.cos(th_m_start), r_zod_in * np.cos(th_m_start)],
                    [r_cal_in * np.sin(th_m_start), r_zod_in * np.sin(th_m_start)],
                    color=color, linewidth=1.1 if self.screen_mode else 0.9)

            for d in range(1, m_days + 1):
                cur_day = day_cum + d - 1
                th_d = np.deg2rad(day_to_angle(cur_day))
                c_d, s_d = np.cos(th_d), np.sin(th_d)

                if d % 10 == 0:
                    r_tick = r_cal_in + band_cal * 0.48
                    lw_t = 0.75 if self.screen_mode else 0.65
                    num_str = ArabicFormatter.format_number(d, self.numeral_system)
                    r_num = r_cal_in + band_cal * 0.22
                    rot_d = get_tangential_rotation(np.rad2deg(th_d))
                    ax.text(r_num * c_d, r_num * s_d, num_str,
                            fontsize=fs_cal_num, fontweight='bold' if self.screen_mode else 'normal',
                            ha='center', va='center', rotation=rot_d,
                            color=color, path_effects=[pe.withStroke(linewidth=1.4 if self.screen_mode else 0.8, foreground='white')])
                elif d % 5 == 0:
                    r_tick = r_cal_in + band_cal * 0.68
                    lw_t = 0.50 if self.screen_mode else 0.45
                else:
                    r_tick = r_cal_in + band_cal * 0.84
                    lw_t = 0.30

                ax.plot([r_tick * c_d, r_zod_in * c_d], [r_tick * s_d, r_zod_in * s_d],
                        color=color, linewidth=lw_t)

            th_m_mid = np.deg2rad(day_to_angle(day_cum + m_days // 2))
            r_m_name = r_cal_in + band_cal * 0.70
            rot_m = get_tangential_rotation(np.rad2deg(th_m_mid))
            m_txt = ArabicFormatter.reshape_text(m_names[m_idx]) if str(self.language).lower().startswith('ar') else m_names[m_idx]
            ax.text(r_m_name * np.cos(th_m_mid), r_m_name * np.sin(th_m_mid), m_txt,
                    fontsize=fs_cal_name, fontweight='bold', color='#196F3D',
                    ha='center', va='center', rotation=rot_m,
                    path_effects=[pe.withStroke(linewidth=stroke_cal, foreground='white')])

            day_cum += m_days

        # -------------------------------------------------------------
        # 4. SUPERPOSED KIDNEY CAM FOR EQUATION OF TIME (الكامة الكلوية لمعادلة الوقت)
        # -------------------------------------------------------------
        R_base = r_cap * 0.52
        A_kidney = r_cap * 0.31

        # Zero EoT Baseline Circle (دائرة خط الاستواء الزماني / صفر دقيقة)
        ax.add_patch(plt.Circle((0, 0), R_base, color='#D4AC0D', fill=False, 
                                linewidth=1.3 if self.screen_mode else 1.1, linestyle=':', zorder=3))

        days_dense = np.linspace(1, 365, 365)
        kidney_r = []
        kidney_th = []
        for d in days_dense:
            B = 2.0 * np.pi * (d - 81) / 365.0
            eot_min = 9.87 * np.sin(2.0 * B) - 7.53 * np.cos(B) - 1.5 * np.sin(B)
            th = np.deg2rad(day_to_angle(d))
            r_k = R_base + (eot_min / 16.45) * A_kidney
            kidney_r.append(r_k)
            kidney_th.append(th)

        kx = np.array(kidney_r) * np.cos(kidney_th)
        ky = np.array(kidney_r) * np.sin(kidney_th)

        # Bold Kidney Cam contour line (100% transparent interior, plain clean curve)
        ax.plot(kx, ky, color='#B7950B', linewidth=2.8 if self.screen_mode else 2.4, zorder=3)

        # -------------------------------------------------------------
        # 5. UPPER RIGHT QUADRANT: HIGH-PRECISION SINE QUADRANT
        #    (رُبْعُ المُجَيَّبِ السِّتِّينِيّ الكَامِل - ٦٠ قِسْماً)
        # -------------------------------------------------------------
        r_sine = r_quad_in

        # 1. High-Density 60x60 Sexagesimal Grid (الشبكة الستينية التامة)
        for k in range(1, 61):
            frac = k / 60.0
            pos = frac * r_sine
            is_ten = (k % 10 == 0)
            is_five = (k % 5 == 0)

            if is_ten:
                lw_s = 0.85 if self.screen_mode else 0.70
                col_s = '#0B3C5D' # Bold deep lapis
            elif is_five:
                lw_s = 0.50 if self.screen_mode else 0.40
                col_s = '#2980B9' # Medium cyan-blue
            else:
                lw_s = 0.22 if self.screen_mode else 0.18
                col_s = '#A9CCE3' # Fine hairline

            # Horizontal sine lines
            x_max = np.sqrt(max(0, r_sine**2 - pos**2))
            ax.plot([0, x_max], [pos, pos], color=col_s, linewidth=lw_s, zorder=2)

            # Vertical cosine lines
            y_max = np.sqrt(max(0, r_sine**2 - pos**2))
            ax.plot([pos, pos], [0, y_max], color=col_s, linewidth=lw_s, zorder=2)

            # Axis tick marks extending outwards
            t_len = 0.015 * r_sine if is_ten else (0.010 * r_sine if is_five else 0.005 * r_sine)
            ax.plot([-t_len, 0], [pos, pos], color='#0B3C5D' if is_ten else '#2980B9', linewidth=0.7 if is_ten else 0.4, zorder=3)
            ax.plot([pos, pos], [-t_len, 0], color='#0B3C5D' if is_ten else '#2980B9', linewidth=0.7 if is_ten else 0.4, zorder=3)

            # Numerals every 5 units (with prominence for multiples of 10)
            if is_five and k <= 60:
                k_num = ArabicFormatter.format_number(k, self.numeral_system)
                fs_num = (5.8 if is_ten else 4.6) if self.screen_mode else (3.6 if is_ten else 2.8)
                c_num = '#004488' if is_ten else '#2471A3'
                ax.text(-0.025 * r_sine, pos, k_num, fontsize=fs_num,
                        fontweight='bold' if (is_ten or self.screen_mode) else 'normal',
                        ha='right', va='center', color=c_num, zorder=4,
                        path_effects=[pe.withStroke(linewidth=1.2 if self.screen_mode else 0.8, foreground='white')])
                ax.text(pos, -0.025 * r_sine, k_num, fontsize=fs_num,
                        fontweight='bold' if (is_ten or self.screen_mode) else 'normal',
                        ha='center', va='top', color=c_num, zorder=4,
                        path_effects=[pe.withStroke(linewidth=1.2 if self.screen_mode else 0.8, foreground='white')])

        # 2. Radial Altitude Guide Rays (أشعة الارتفاع كل ١٥ درجة)
        for ang_deg in [15, 30, 45, 60, 75]:
            th_r = np.deg2rad(ang_deg)
            c_r, s_r = np.cos(th_r), np.sin(th_r)
            ax.plot([0, r_sine * c_r], [0, r_sine * s_r],
                    color='#5DADE2', linewidth=0.55 if self.screen_mode else 0.45, linestyle=':', zorder=2)

        # 3. Circumference Arc Degree Graduations (تدريجات درجات المحيط من ٠° إلى ٩٠°)
        for deg in range(0, 91):
            th_d = np.deg2rad(deg)
            c_d, s_d = np.cos(th_d), np.sin(th_d)
            is_ten_deg = (deg % 10 == 0)
            is_five_deg = (deg % 5 == 0)
            
            t_in = 0.030 * r_sine if is_ten_deg else (0.018 * r_sine if is_five_deg else 0.009 * r_sine)
            lw_deg = 0.9 if is_ten_deg else (0.55 if is_five_deg else 0.3)
            col_deg = '#111111' if is_ten_deg else ('#2980B9' if is_five_deg else '#7F8C8D')
            
            ax.plot([(r_sine - t_in) * c_d, r_sine * c_d],
                    [(r_sine - t_in) * s_d, r_sine * s_d],
                    color=col_deg, linewidth=lw_deg, zorder=3)

        # 4. Arc of Total Obliquity of the Ecliptic (قوس الميل الأعظم ٢٣° ٢٦')
        th_eps = np.linspace(0, np.pi / 2, 80)
        r_eps = r_sine * np.sin(np.deg2rad(23.44)) # R * sin(23.44°) ≈ 23.86/60
        ax.plot(r_eps * np.cos(th_eps), r_eps * np.sin(th_eps),
                color='#C0392B', linewidth=1.1 if self.screen_mode else 0.9, linestyle='--', zorder=3)
        
        lbl_eps = ArabicFormatter.reshape_text("الميل الأعظم ٢٣° ٢٦'") if str(self.language).lower().startswith('ar') else "Obliquity 23°26'"
        th_eps_lbl = np.deg2rad(65)
        ax.text(r_eps * np.cos(th_eps_lbl) + 0.02, r_eps * np.sin(th_eps_lbl) + 0.02, lbl_eps,
                fontsize=5.5 if self.screen_mode else 3.2, fontweight='bold', color='#C0392B', rotation=-25, zorder=4,
                path_effects=[pe.withStroke(linewidth=1.4 if self.screen_mode else 0.8, foreground='white')])

        # -------------------------------------------------------------
        # 6. UPPER LEFT QUADRANT: Vacant
        # -------------------------------------------------------------
        
        # -------------------------------------------------------------
        # 7. LOWER HALF: SHADOW SQUARE (مربّع الظل المبسوط والمنكوس)
        # -------------------------------------------------------------
        S = r_quad_in * 0.62
        ax.plot([-S, S], [0, 0], color=color, linewidth=1.3 if self.screen_mode else 1.1)
        ax.plot([-S, -S], [0, -S], color=color, linewidth=1.3 if self.screen_mode else 1.1)
        ax.plot([S, S], [0, -S], color=color, linewidth=1.3 if self.screen_mode else 1.1)
        ax.plot([-S, S], [-S, -S], color=color, linewidth=1.3 if self.screen_mode else 1.1)
        ax.plot([0, 0], [0, -S], color=color, linewidth=0.9 if self.screen_mode else 0.8, linestyle=':')

        fs_sh = 6.8 if self.screen_mode else 4.2
        stroke_sh = 1.8 if self.screen_mode else 0.8
        for i in range(1, 13):
            y_i = -(i / 12.0) * S
            ax.plot([-S, -S + 0.025], [y_i, y_i], color=color, linewidth=0.7 if self.screen_mode else 0.6)
            if i % 2 == 0:
                ax.plot([0, -S], [0, y_i], color='#7F8C8D', linewidth=0.5 if self.screen_mode else 0.4, linestyle=':')
                num_i = ArabicFormatter.format_number(i, self.numeral_system)
                ax.text(-S - 0.025, y_i, num_i, fontsize=fs_sh, fontweight='bold' if self.screen_mode else 'normal',
                        ha='right', va='center', color=color,
                        path_effects=[pe.withStroke(linewidth=stroke_sh, foreground='white')])

            ax.plot([S - 0.025, S], [y_i, y_i], color=color, linewidth=0.7 if self.screen_mode else 0.6)
            if i % 2 == 0:
                ax.plot([0, S], [0, y_i], color='#7F8C8D', linewidth=0.5 if self.screen_mode else 0.4, linestyle=':')
                num_i = ArabicFormatter.format_number(i, self.numeral_system)
                ax.text(S + 0.025, y_i, num_i, fontsize=fs_sh, fontweight='bold' if self.screen_mode else 'normal',
                        ha='left', va='center', color=color,
                        path_effects=[pe.withStroke(linewidth=stroke_sh, foreground='white')])

            x_left = -(i / 12.0) * S
            x_right = (i / 12.0) * S
            ax.plot([x_left, x_left], [-S, -S + 0.025], color=color, linewidth=0.7 if self.screen_mode else 0.6)
            ax.plot([x_right, x_right], [-S, -S + 0.025], color=color, linewidth=0.7 if self.screen_mode else 0.6)
            if i % 2 == 0:
                ax.plot([0, x_left], [0, -S], color='#7F8C8D', linewidth=0.5 if self.screen_mode else 0.4, linestyle=':')
                ax.plot([0, x_right], [0, -S], color='#7F8C8D', linewidth=0.5 if self.screen_mode else 0.4, linestyle=':')
                num_i = ArabicFormatter.format_number(i, self.numeral_system)
                ax.text(x_left, -S - 0.025, num_i, fontsize=fs_sh, fontweight='bold' if self.screen_mode else 'normal',
                        ha='center', va='top', color=color,
                        path_effects=[pe.withStroke(linewidth=stroke_sh, foreground='white')])
                ax.text(x_right, -S - 0.025, num_i, fontsize=fs_sh, fontweight='bold' if self.screen_mode else 'normal',
                        ha='center', va='top', color=color,
                        path_effects=[pe.withStroke(linewidth=stroke_sh, foreground='white')])

        box_title = ArabicFormatter.reshape_text("مربع الظل") if str(self.language).lower().startswith('ar') else "Shadow Square (12 digits)"
        fs_sh_title = 8.0 if self.screen_mode else 4.6
        ax.text(0, -S * 0.78, box_title, fontsize=fs_sh_title, fontweight='bold', color='#1B4F72',
                ha='center', va='center',
                path_effects=[pe.withStroke(linewidth=2.0 if self.screen_mode else 1.0, foreground='white')])

        # Central Pivot Hub
        ax.add_patch(plt.Circle((0, 0), 0.04, color=color, fill=True))
        ax.add_patch(plt.Circle((0, 0), 0.08, color=color, fill=False, linewidth=1.0))


