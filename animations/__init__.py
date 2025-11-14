"""
Animations Package
Preset animations and animation base system.
Each preset dance is its own module with accurate keyframe data.
"""

from .animation_base import Animation, Keyframe, InterpolationType
from .anim_floss import create_floss_animation
from .anim_carlton import create_carlton_animation
from .anim_take_the_l import create_take_the_l_animation
from .anim_moonwalk import create_moonwalk_animation
from .anim_dab import create_dab_animation

__all__ = [
    'Animation',
    'Keyframe',
    'InterpolationType',
    'create_floss_animation',
    'create_carlton_animation',
    'create_take_the_l_animation',
    'create_moonwalk_animation',
    'create_dab_animation'
]
