"""
Astrolabe Package
=================
Core mathematical projection, astronomical algorithms, vector generation,
and interactive simulation suite for classic planispheric astrolabes.
"""

from .engine import (
    Astrolabe,
    ArabicFormatter,
    StereographicProjection,
    Star,
    Tympan,
    Rete,
    Rule,
    AstrolabeBack,
    Alidade,
)

# Convenient alias
Back = AstrolabeBack

__all__ = [
    "Astrolabe",
    "ArabicFormatter",
    "StereographicProjection",
    "Star",
    "Tympan",
    "Rete",
    "Rule",
    "AstrolabeBack",
    "Back",
    "Alidade",
]
