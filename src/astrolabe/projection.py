"""
Astrolabe Projection & Coordinate Engines.
Mathematical foundation for equatorial stereographic projection and fundamental celestial parallels.
"""

import numpy as np
import matplotlib.pyplot as plt


class StereographicProjection:
    """Mathematical engine for equatorial stereographic projection."""
    def __init__(self, radius_equator=1.0, obliquity=23.44):
        self.R = float(radius_equator)
        self.eps = np.deg2rad(float(obliquity))
        
        # Radii of the three fundamental celestial parallels
        self.r_cancer = self.R * np.tan((np.pi / 2.0 - self.eps) / 2.0)
        self.r_equator = self.R
        self.r_capricorn = self.R * np.tan((np.pi / 2.0 + self.eps) / 2.0)

    def equatorial_to_xy(self, ra, dec):
        """Convert equatorial coordinates to planar stereographic coordinates."""
        r = self.R * np.tan((np.pi / 2.0 - dec) / 2.0)
        x = r * np.cos(ra)
        y = r * np.sin(ra)
        return x, y

    def horizontal_to_xy(self, alt, az, lat):
        """Convert observer horizontal coordinates to planar stereographic coordinates."""
        sin_delta = np.sin(lat) * np.sin(alt) + np.cos(lat) * np.cos(alt) * np.cos(az)
        delta = np.arcsin(np.clip(sin_delta, -1.0, 1.0))
        
        cos_d_cos_H = np.cos(lat) * np.sin(alt) - np.sin(lat) * np.cos(alt) * np.cos(az)
        cos_d_sin_H = np.cos(alt) * np.sin(az)
        H = np.arctan2(cos_d_sin_H, cos_d_cos_H)
        
        r = self.R * np.tan((np.pi / 2.0 - delta) / 2.0)
        x = r * np.sin(H)
        y = r * np.cos(H)
        return x, y


class CelestialCircles:
    """Draws Tropic of Cancer, Celestial Equator, and Tropic of Capricorn."""
    def __init__(self, proj):
        self.proj = proj

    def draw(self, ax, color='black'):
        # Tropic of Cancer (dotted)
        ax.add_patch(plt.Circle((0, 0), self.proj.r_cancer, color=color, fill=False,
                                linestyle=':', linewidth=0.8, alpha=0.7))
        # Celestial Equator (dashed)
        ax.add_patch(plt.Circle((0, 0), self.proj.r_equator, color=color, fill=False,
                                linestyle='--', linewidth=1.0, alpha=0.8))
        # Tropic of Capricorn (outer rim boundary)
        ax.add_patch(plt.Circle((0, 0), self.proj.r_capricorn, color=color, fill=False,
                                linewidth=1.6))
