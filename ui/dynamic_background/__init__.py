from __future__ import annotations

from core.动态背景 import DynamicBackgroundManager
from .vinyl import VinylDynamicBackground


DynamicBackgroundManager.register_class(
    VinylDynamicBackground,
    "唱片",
    "vinyl",
    "record",
    "disc",
    "网格",
    "透视网格",
    "grid",
    "perspective_grid",
)


__all__ = ["VinylDynamicBackground"]
