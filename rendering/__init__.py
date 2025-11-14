"""
Rendering Package
Modular rendering pipeline with vector (default) and HD (optional) modes.
Optimized for 60 FPS on RTX 3060M.
"""

from .vector_renderer import VectorRenderer
from .hd_renderer import HDRenderer

__all__ = ['VectorRenderer', 'HDRenderer']
