"""
Rigging Package
Skeletal rigging system with auto-rig and manual T-pose bone placement.
Includes inverse kinematics solver for natural movement.
"""

from .skeleton import Skeleton, Bone
from .auto_rig import AutoRig
from .manual_rig import ManualRig
from .ik_solver import IKSolver

__all__ = ['Skeleton', 'Bone', 'AutoRig', 'ManualRig', 'IKSolver']
