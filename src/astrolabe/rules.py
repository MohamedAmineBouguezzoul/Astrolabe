"""
Astrolabe Rule and Alidade Sighting Instruments.
Models the front Rule (Ostensor) and back Alidade (Dioptra) with sighting vanes and scales.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe

from .arabic import ArabicFormatter
from .projection import StereographicProjection


class Rule:
    """The Rule (Ostensor): rotatable longitudinal sighting ruler."""
    def __init__(self, proj=None, language='latin', numeral_system='latin', screen_mode=False):
        self.proj = proj or StereographicProjection()
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode

    def draw(self, ax):
        r_cap = self.proj.r_capricorn * 1.24
        w = 0.08
        lane_x = w * 0.40
        tip_h = 0.05
        r_boss = 0.08
        y_boss_meet = np.sqrt(r_boss**2 - min(w, r_boss * 0.98)**2) if r_boss > w else 0.0
        
        # 0. Solid White Opaque Backing for Rule Arms & Center Boss (Point-Symmetric)
        poly_u = patches.Polygon([[0, 0], [0, r_cap + tip_h], [w, r_cap], [w, y_boss_meet], [0, 0]], 
                                 closed=True, facecolor='#FFFFFF', edgecolor='none', zorder=2)
        poly_l = patches.Polygon([[0, 0], [0, -r_cap - tip_h], [-w, -r_cap], [-w, -y_boss_meet], [0, 0]], 
                                 closed=True, facecolor='#FFFFFF', edgecolor='none', zorder=2)
        boss_fill = plt.Circle((0, 0), r_boss, facecolor='#FFFFFF', edgecolor='none', zorder=2)
        ax.add_patch(poly_u)
        ax.add_patch(poly_l)
        ax.add_patch(boss_fill)
        
        # 1. Central continuous fiducial line (حافة التسديد والتطبيق القطرية)
        ax.plot([0, 0], [-r_cap - tip_h, r_cap + tip_h], color='black', 
                linewidth=1.4 if self.screen_mode else 1.2, zorder=3)
        
        # 2. Upper arm blade (النصف العلوي: المعدن على اليمين فقط [0, w])
        ax.plot([w, w], [y_boss_meet, r_cap], color='black', 
                linewidth=1.0 if self.screen_mode else 0.8, zorder=3)
        ax.plot([w, 0], [r_cap, r_cap + tip_h], color='black', 
                linewidth=1.2 if self.screen_mode else 1.0, zorder=3)
        if y_boss_meet > 0:
            ax.plot([w, np.sqrt(r_boss**2 - y_boss_meet**2)], [y_boss_meet, y_boss_meet], color='black', 
                    linewidth=0.8 if self.screen_mode else 0.6, zorder=3)
        
        # 3. Lower arm blade (النصف السفلي: المعدن على اليسار فقط [-w, 0])
        ax.plot([-w, -w], [-r_cap, -y_boss_meet], color='black', 
                linewidth=1.0 if self.screen_mode else 0.8, zorder=3)
        ax.plot([-w, 0], [-r_cap, -r_cap - tip_h], color='black', 
                linewidth=1.2 if self.screen_mode else 1.0, zorder=3)
        if y_boss_meet > 0:
            ax.plot([-w, -np.sqrt(r_boss**2 - y_boss_meet**2)], [-y_boss_meet, -y_boss_meet], color='black', 
                    linewidth=0.8 if self.screen_mode else 0.6, zorder=3)
        
        # 4. Central hub / collar (الحلقة والقطب)
        ax.add_patch(plt.Circle((0, 0), r_boss, color='black', fill=False, 
                                linewidth=1.6 if self.screen_mode else 1.4, zorder=4))
        ax.add_patch(plt.Circle((0, 0), 0.07, color='black', fill=False, 
                                linewidth=0.8 if self.screen_mode else 0.6, zorder=4))
        ax.add_patch(plt.Circle((0, 0), 0.02, color='black', fill=True, zorder=5))
        
        # 5. Declination scale graduations (تدرج الميل) with 180° Rotational Symmetry
        # Both arms display identical graduations mirrored through the center (0, 0)
        for arm_sign, x_sign in [(1, 1), (-1, -1)]:
            for dec_deg in range(-20, 81, 2):
                dec = np.deg2rad(dec_deg)
                r = self.proj.R * np.tan((np.pi / 2.0 - dec) / 2.0)
                y_pos = arm_sign * r
                if r <= r_cap and r >= r_boss:
                    is_major = (dec_deg % 10 == 0)
                    is_mid = (dec_deg % 5 == 0) and not is_major
                    
                    if is_major:
                        tick_w = lane_x
                    elif is_mid:
                        tick_w = lane_x * 0.65
                    else:
                        tick_w = lane_x * 0.40
                    
                    ax.plot([0, x_sign * tick_w], [y_pos, y_pos], color='black', 
                            linewidth=(1.0 if is_major else 0.5) if self.screen_mode else (0.8 if is_major else 0.4),
                            zorder=4)
                    
                    if is_major:
                        text_x = x_sign * (lane_x + w) / 2.0
                        if self.numeral_system == 'abjad':
                            lbl = "٠" if dec_deg == 0 else ArabicFormatter.format_number(abs(dec_deg), 'abjad')
                        elif self.numeral_system in ('eastern_arabic', 'eastern', 'arabic_numerals', 'hindi'):
                            lbl = "٠" if dec_deg == 0 else ArabicFormatter.to_eastern_arabic(abs(dec_deg))
                        else:
                            lbl = f"{abs(dec_deg)}"
                        
                        reshaped = ArabicFormatter.reshape_text(lbl) if str(self.language).lower().startswith('ar') else lbl
                        fs_rule = 8.0 if self.screen_mode else 5.5
                        stroke_rule = 2.0 if self.screen_mode else 1.0
                        ax.text(text_x, y_pos, reshaped, fontsize=fs_rule, 
                                fontweight='bold' if self.screen_mode else 'normal',
                                va='center', ha='center', color='black', zorder=5,
                                path_effects=[pe.withStroke(linewidth=stroke_rule, foreground='white')])




class Alidade:
    """
    The Sighting Alidade (العضادة ذات الشظيتين والهدفين).
    Equipped with dual sighting vanes near outer ends, and engraved with
    the Equation of Time minute graduation scale on the blade to measure
    the exact minutes (+/-) where the fiducial edge intersects the Kidney Cam.
    """
    def __init__(self, proj=None, language='arabic', numeral_system='abjad', screen_mode=False):
        self.proj = proj or StereographicProjection()
        self.language = language
        self.numeral_system = numeral_system
        self.screen_mode = screen_mode

    def draw(self, ax, color='black'):
        r_cap = self.proj.r_capricorn
        r_len = r_cap * 1.24
        w = 0.076  # Width of alidade blade
        r_boss = 0.085  # Center boss radius
        tip_h = 0.05
        y_boss_meet = np.sqrt(r_boss**2 - min(w, r_boss * 0.98)**2) if r_boss > w else 0.0
        
        # 0. Solid White Opaque Backing for Alidade Arms & Center Boss
        poly_u = patches.Polygon([[0, 0], [0, r_len + tip_h], [w, r_len], [w, y_boss_meet], [0, 0]], 
                                 closed=True, facecolor='#FFFFFF', edgecolor='none', zorder=2)
        poly_l = patches.Polygon([[0, 0], [0, -r_len - tip_h], [-w, -r_len], [-w, -y_boss_meet], [0, 0]], 
                                 closed=True, facecolor='#FFFFFF', edgecolor='none', zorder=2)
        boss_fill = plt.Circle((0, 0), r_boss, facecolor='#FFFFFF', edgecolor='none', zorder=2)
        ax.add_patch(poly_u)
        ax.add_patch(poly_l)
        ax.add_patch(boss_fill)
        
        # 1. Central Sighting & Continuous Fiducial Line (خط التسديد وحافة التطبيق القطرية)
        ax.plot([0, 0], [-r_len - tip_h, r_len + tip_h], color=color, 
                linewidth=1.4 if self.screen_mode else 1.2, zorder=4)
        
        # 2. Upper arm blade (النصف العلوي: المعدن على اليمين فقط [0, w])
        ax.plot([w, w], [y_boss_meet, r_len], color=color, 
                linewidth=1.0 if self.screen_mode else 0.9, zorder=4)
        # Pointed indicator beveled tip (مري العضادة العلوي المشطوف)
        ax.plot([w, 0], [r_len, r_len + tip_h], color=color, 
                linewidth=1.4 if self.screen_mode else 1.3, zorder=4)
        if y_boss_meet > 0:
            ax.plot([w, np.sqrt(r_boss**2 - y_boss_meet**2)], [y_boss_meet, y_boss_meet], color=color, 
                    linewidth=0.8 if self.screen_mode else 0.6, zorder=4)
        
        # 3. Lower arm blade (النصف السفلي: المعدن على اليسار فقط [-w, 0])
        ax.plot([-w, -w], [-r_len, -y_boss_meet], color=color, 
                linewidth=1.0 if self.screen_mode else 0.9, zorder=4)
        # Pointed indicator beveled tip (مري العضادة السفلي المشطوف)
        ax.plot([-w, 0], [-r_len, -r_len - tip_h], color=color, 
                linewidth=1.4 if self.screen_mode else 1.3, zorder=4)
        if y_boss_meet > 0:
            ax.plot([-w, -np.sqrt(r_boss**2 - y_boss_meet**2)], [-y_boss_meet, -y_boss_meet], color=color, 
                    linewidth=0.8 if self.screen_mode else 0.6, zorder=4)
        
        # 4. Center boss & collar (صرة المحور بالمركز)
        ax.add_patch(plt.Circle((0, 0), r_boss, color=color, fill=False, 
                                linewidth=1.6 if self.screen_mode else 1.4, zorder=6))
        ax.add_patch(plt.Circle((0, 0), 0.072, color=color, fill=False, 
                                linewidth=0.8 if self.screen_mode else 0.6, zorder=6))
        ax.add_patch(plt.Circle((0, 0), 0.022, color=color, fill=True, zorder=6))
        
        # 5. Point-Symmetric Sighting Vanes (اللبؤتان / الهدفتان المتقابلتان)
        r_vane = r_cap * 0.95
        vane_w = 0.070
        vane_h = 0.085
        
        # Upper Vane (mounted on upper right blade, sight pinhole on central fiducial line)
        y_vu = r_vane
        rect_u = plt.Rectangle((-0.022, y_vu - vane_h / 2), w + 0.025, vane_h,
                               facecolor='#FFFFFF', edgecolor=color, 
                               linewidth=1.2 if self.screen_mode else 1.1, zorder=7)
        ax.add_patch(rect_u)
        ax.add_patch(plt.Circle((0, y_vu), 0.012, facecolor='white', edgecolor=color, linewidth=0.8, zorder=8))
        ax.add_patch(plt.Circle((w * 0.52, y_vu), 0.018, facecolor='white', edgecolor=color, linewidth=0.8, zorder=8))
        
        # Lower Vane (mounted on lower left blade, sight pinhole on central fiducial line)
        y_vl = -r_vane
        rect_l = plt.Rectangle((-(w + 0.003), y_vl - vane_h / 2), w + 0.025, vane_h,
                               facecolor='#FFFFFF', edgecolor=color, 
                               linewidth=1.2 if self.screen_mode else 1.1, zorder=7)
        ax.add_patch(rect_l)
        ax.add_patch(plt.Circle((0, y_vl), 0.012, facecolor='white', edgecolor=color, linewidth=0.8, zorder=8))
        ax.add_patch(plt.Circle((-w * 0.52, y_vl), 0.018, facecolor='white', edgecolor=color, linewidth=0.8, zorder=8))
        
        # 6. Equation of Time Minute Graduations on Upper Arm (تدريجات دقائق معادلة الوقت)
        R_base = r_cap * 0.52
        A_kidney = r_cap * 0.31
        
        # Zero Line across upper blade at r = R_base
        ax.plot([0, w * 0.90], [R_base, R_base], color='#B7950B', 
                linewidth=1.6 if self.screen_mode else 1.4, zorder=5)
        lbl_zero = "٠" if str(self.language).lower().startswith('ar') else "0 (Zero)"
        fs_zero = 6.5 if self.screen_mode else 3.6
        ax.text(w * 0.50, R_base + 0.012, ArabicFormatter.reshape_text(lbl_zero) if str(self.language).lower().startswith('ar') else lbl_zero,
                fontsize=fs_zero, fontweight='bold', color='#B7950B', ha='center', va='bottom', zorder=6,
                path_effects=[pe.withStroke(linewidth=1.2 if self.screen_mode else 0.8, foreground='white')])
        
        # Minute ticks from -16 to +16 on the upper arm
        for m in range(-16, 17):
            y_m = R_base + (m / 16.45) * A_kidney
            is_major = (m % 2 == 0)
            is_four = (m % 4 == 0)
            tick_len = w * 0.32 if is_major else w * 0.18
            col_t = color if not is_four else ('#8B0000' if m > 0 else '#1B4F72')
            
            # Draw tick from fiducial edge into blade
            ax.plot([0, tick_len], [y_m, y_m], color=col_t, linewidth=0.8 if is_major else 0.4, zorder=5)
            
            # Numeral inside blade
            if is_major and m != 0:
                if str(self.language).lower().startswith('ar'):
                    num_txt = f"{ArabicFormatter.format_number(abs(m), self.numeral_system)}{'+' if m > 0 else '-'}"
                else:
                    num_txt = f"{'+' if m > 0 else ''}{m}"
                
                col_num = '#8B0000' if m > 0 else '#1B4F72'
                fs_m = 5.5 if self.screen_mode else 3.2
                ax.text(w * 0.58, y_m, num_txt, fontsize=fs_m, fontweight='bold',
                        color=col_num, ha='center', va='center', zorder=6,
                        path_effects=[pe.withStroke(linewidth=1.0 if self.screen_mode else 0.6, foreground='white')])
        
        # Engraved titles and indicators on the upper arm
        eot_title = ArabicFormatter.reshape_text("الوقت\nمعادلة") if str(self.language).lower().startswith('ar') else "EoT (min)"
        
        fs_ind = 5.2 if self.screen_mode else 3.0
        fs_title = 5.4 if self.screen_mode else 3.1
        ax.text(w * 0.50, R_base + A_kidney + 0.045, eot_title,
                fontsize=fs_title, fontweight='bold', color='#7D6608', ha='center', va='center', zorder=6,
                path_effects=[pe.withStroke(linewidth=1.2 if self.screen_mode else 0.8, foreground='white')])
        
        # 7. Distance / Altitude graduations on the Lower Arm (المعدن على اليسار [-w, 0])
        for r_mark in np.linspace(r_boss * 1.25, r_cap * 0.88, 20):
            ax.plot([0, -w * 0.35], [-r_mark, -r_mark], color=color, 
                    linewidth=0.5 if self.screen_mode else 0.4, zorder=5)
        
        scale_title = ArabicFormatter.reshape_text("مقياس الارتفاع") if str(self.language).lower().startswith('ar') else "Altitude Scale"
        ax.text(-w * 0.65, -(r_boss + r_cap * 0.88) / 2, scale_title,
                fontsize=fs_title, fontweight='bold', color='#2E4053', ha='center', va='center', rotation=90, zorder=6,
                path_effects=[pe.withStroke(linewidth=1.2 if self.screen_mode else 0.8, foreground='white')])


