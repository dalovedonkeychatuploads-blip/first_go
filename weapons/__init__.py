"""
Weapons Package
Contains all procedural weapon generators with flame effect attachment points.
Each weapon is its own module for maximum modularity and AAA quality geometry.
"""

from .weapon_base import WeaponBase, FlameAttachmentPoint

__all__ = ['WeaponBase', 'FlameAttachmentPoint']
