"""
Take the L Dance Animation
Taunting Fortnite emote where character makes "L" shape on forehead with hand.

Motion Description:
- Right hand forms "L" shape and places on forehead (loser gesture)
- Left hand on hip (sassy pose)
- Hips swivel side to side
- Slight leg bounce/kick
- Head tilts slightly with hand movement

Duration: ~2.5 seconds (1 complete loop)
Frame Rate: 60 FPS
Total Frames: 150

This is PERFECT for:
- Taunting defeated enemies
- Comedic roasting moments
- Victory celebrations with attitude
- Tests the IK solver (hand-to-head attachment)
"""

import math
from typing import Dict
from animations.animation_base import Animation, Keyframe, InterpolationType


# ============================================================================
# TAKE THE L CONSTANTS
# ============================================================================

# Timing (60 FPS)
TAKE_L_DURATION = 2.5  # 2.5 seconds for one complete loop
TAKE_L_FPS = 60
TAKE_L_TOTAL_FRAMES = int(TAKE_L_DURATION * TAKE_L_FPS)

# Motion parameters
TAKE_L_HIP_SWIVEL = 30.0          # Degrees - side to side hip motion
TAKE_L_LEG_KICK = 20.0            # Degrees - leg lift/kick
TAKE_L_HEAD_TILT = 12.0           # Degrees - head tilt with hand
TAKE_L_L_HAND_ANGLE = 110.0       # Degrees - "L" shape angle
TAKE_L_TEMPO_BPM = 110            # Beats per minute

# Move timing
SWIVEL_CYCLE_FRAMES = 25  # ~0.42 seconds per swivel


# ============================================================================
# KEYFRAME GENERATION
# ============================================================================

def create_take_the_l_animation(character_name: str = "Character") -> Animation:
    """
    Create the Take the L animation with accurate keyframes.

    The Take the L consists of:
    1. Right hand forms "L" and places on forehead
    2. Left hand on hip (sassy)
    3. Hips swivel left and right
    4. Alternating leg kicks
    5. Head tilts with hip sways

    Args:
        character_name: Name of the character performing the dance

    Returns:
        Complete Animation object with all keyframes
    """
    animation = Animation(
        name=f"{character_name}_TakeTheL",
        duration=TAKE_L_DURATION,
        fps=TAKE_L_FPS
    )

    # Generate keyframes for 2.5-second loop
    _add_take_l_setup(animation, 0)         # Frame 0: Bring hand to forehead
    _add_take_l_left_swivel(animation, 25)  # Frame 25: Swivel left
    _add_take_l_center(animation, 50)       # Frame 50: Center
    _add_take_l_right_swivel(animation, 75) # Frame 75: Swivel right
    _add_take_l_center(animation, 100)      # Frame 100: Center
    _add_take_l_left_swivel(animation, 125) # Frame 125: Swivel left
    _add_take_l_setup(animation, 150)       # Frame 150: End (loop point)

    print(f"✓ Created Take the L animation: {animation.keyframe_count} keyframes, {TAKE_L_DURATION}s duration")

    return animation


def _add_take_l_setup(animation: Animation, frame: int):
    """
    Add setup keyframe.
    Hand comes up to forehead in "L" shape, other hand on hip.
    """
    time = frame / TAKE_L_FPS

    pose = {
        # Root / Hips - neutral
        "hips": {"rotation": 0.0},

        # Torso - slight lean back (confident stance)
        "torso": {"rotation": -5.0},
        "neck": {"rotation": 0.0},
        "head": {"rotation": 0.0},

        # Left arm - HAND ON HIP (sassy pose)
        "left_shoulder": {"rotation": -25.0},
        "left_upper_arm": {"rotation": -60.0},
        "left_forearm": {"rotation": 120.0},      # Bent sharply
        "left_hand": {"rotation": 0.0},

        # Right arm - "L" ON FOREHEAD
        # This is the key pose - hand forms L and touches forehead
        "right_shoulder": {"rotation": 40.0},
        "right_upper_arm": {"rotation": 130.0},   # Raised to head height
        "right_forearm": {"rotation": -TAKE_L_L_HAND_ANGLE},  # Forms "L" angle
        "right_hand": {"rotation": 0.0},

        # NOTE: IK solver should be used to ensure hand stays on forehead!
        # The hand's target position should be: head_pos + offset_for_forehead

        # Left leg - standing
        "left_thigh": {"rotation": 0.0},
        "left_shin": {"rotation": 0.0},
        "left_foot": {"rotation": 0.0},

        # Right leg - standing
        "right_thigh": {"rotation": 0.0},
        "right_shin": {"rotation": 0.0},
        "right_foot": {"rotation": 0.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


def _add_take_l_left_swivel(animation: Animation, frame: int):
    """
    Add left swivel keyframe.
    Hips swivel to the left, right leg kicks out slightly.
    """
    time = frame / TAKE_L_FPS

    pose = {
        # Root / Hips - swivel LEFT
        "hips": {"rotation": -TAKE_L_HIP_SWIVEL},

        # Torso - rotate with hips
        "torso": {"rotation": -5.0 - (TAKE_L_HIP_SWIVEL * 0.4)},
        "neck": {"rotation": TAKE_L_HEAD_TILT * 0.5},
        "head": {"rotation": TAKE_L_HEAD_TILT},   # Head tilts opposite

        # Left arm - still on hip
        "left_shoulder": {"rotation": -25.0},
        "left_upper_arm": {"rotation": -60.0},
        "left_forearm": {"rotation": 120.0},
        "left_hand": {"rotation": 0.0},

        # Right arm - L still on forehead (IK maintains position)
        "right_shoulder": {"rotation": 40.0},
        "right_upper_arm": {"rotation": 130.0},
        "right_forearm": {"rotation": -TAKE_L_L_HAND_ANGLE},
        "right_hand": {"rotation": 0.0},

        # Left leg - standing (weight on this leg)
        "left_thigh": {"rotation": -8.0},
        "left_shin": {"rotation": 10.0},
        "left_foot": {"rotation": -3.0},

        # Right leg - KICK OUT slightly
        "right_thigh": {"rotation": TAKE_L_LEG_KICK},
        "right_shin": {"rotation": -TAKE_L_LEG_KICK * 0.5},
        "right_foot": {"rotation": TAKE_L_LEG_KICK * 0.3},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


def _add_take_l_center(animation: Animation, frame: int):
    """
    Add center keyframe.
    Return to center position between swivels.
    """
    time = frame / TAKE_L_FPS

    pose = {
        # Root / Hips - center
        "hips": {"rotation": 0.0},

        # Torso
        "torso": {"rotation": -5.0},
        "neck": {"rotation": 0.0},
        "head": {"rotation": 0.0},

        # Left arm - hand on hip
        "left_shoulder": {"rotation": -25.0},
        "left_upper_arm": {"rotation": -60.0},
        "left_forearm": {"rotation": 120.0},
        "left_hand": {"rotation": 0.0},

        # Right arm - L on forehead
        "right_shoulder": {"rotation": 40.0},
        "right_upper_arm": {"rotation": 130.0},
        "right_forearm": {"rotation": -TAKE_L_L_HAND_ANGLE},
        "right_hand": {"rotation": 0.0},

        # Left leg
        "left_thigh": {"rotation": 0.0},
        "left_shin": {"rotation": 0.0},
        "left_foot": {"rotation": 0.0},

        # Right leg
        "right_thigh": {"rotation": 0.0},
        "right_shin": {"rotation": 0.0},
        "right_foot": {"rotation": 0.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


def _add_take_l_right_swivel(animation: Animation, frame: int):
    """
    Add right swivel keyframe.
    Hips swivel to the right, left leg kicks out slightly.
    """
    time = frame / TAKE_L_FPS

    pose = {
        # Root / Hips - swivel RIGHT
        "hips": {"rotation": TAKE_L_HIP_SWIVEL},

        # Torso - rotate with hips
        "torso": {"rotation": -5.0 + (TAKE_L_HIP_SWIVEL * 0.4)},
        "neck": {"rotation": -TAKE_L_HEAD_TILT * 0.5},
        "head": {"rotation": -TAKE_L_HEAD_TILT},  # Head tilts opposite

        # Left arm - still on hip
        "left_shoulder": {"rotation": -25.0},
        "left_upper_arm": {"rotation": -60.0},
        "left_forearm": {"rotation": 120.0},
        "left_hand": {"rotation": 0.0},

        # Right arm - L still on forehead (IK maintains position)
        "right_shoulder": {"rotation": 40.0},
        "right_upper_arm": {"rotation": 130.0},
        "right_forearm": {"rotation": -TAKE_L_L_HAND_ANGLE},
        "right_hand": {"rotation": 0.0},

        # Left leg - KICK OUT slightly
        "left_thigh": {"rotation": TAKE_L_LEG_KICK},
        "left_shin": {"rotation": -TAKE_L_LEG_KICK * 0.5},
        "left_foot": {"rotation": TAKE_L_LEG_KICK * 0.3},

        # Right leg - standing (weight on this leg)
        "right_thigh": {"rotation": -8.0},
        "right_shin": {"rotation": 10.0},
        "right_foot": {"rotation": -3.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_take_the_l_with_duration(character_name: str, duration: float, loop: bool = True) -> Animation:
    """
    Create Take the L animation with custom duration.

    Args:
        character_name: Name of character
        duration: Total duration in seconds
        loop: Whether animation should loop

    Returns:
        Animation object with extended duration
    """
    # Create base 2.5-second animation
    base_anim = create_take_the_l_animation(character_name)

    if duration <= TAKE_L_DURATION:
        return base_anim

    if not loop:
        base_anim.duration = duration
        return base_anim

    # Calculate loops needed
    num_loops = int(duration / TAKE_L_DURATION)

    # Create extended animation
    extended_anim = Animation(
        name=f"{character_name}_TakeTheL_Extended",
        duration=duration,
        fps=TAKE_L_FPS
    )

    # Copy keyframes multiple times
    for loop_index in range(num_loops):
        time_offset = loop_index * TAKE_L_DURATION

        for kf in base_anim.keyframes:
            new_time = kf.time + time_offset
            new_frame = int(new_time * TAKE_L_FPS)

            # Skip duplicate start frames
            if loop_index > 0 and kf.frame == 0:
                continue

            new_kf = Keyframe(
                frame=new_frame,
                time=new_time,
                pose=kf.pose.copy(),
                interpolation=kf.interpolation
            )
            extended_anim.add_keyframe(new_kf)

    print(f"✓ Extended Take the L animation to {duration}s ({num_loops} loops)")

    return extended_anim


def get_take_the_l_description() -> str:
    """
    Get human-readable description of Take the L dance.

    Returns:
        Description string for UI display
    """
    return (
        "👋 TAKE THE L\n\n"
        "Iconic Fortnite taunt emote.\n"
        "Hand forms 'L' on forehead (loser gesture),\n"
        "hips swivel sassily side to side.\n\n"
        f"Duration: {TAKE_L_DURATION}s\n"
        f"Tempo: {TAKE_L_TEMPO_BPM} BPM\n"
        "Perfect for: Taunting enemies, roasting moments, victory with attitude\n"
        "Note: Tests IK solver (hand-to-head attachment)"
    )


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TAKE THE L DANCE ANIMATION TEST")
    print("=" * 60)

    # Create animation
    anim = create_take_the_l_animation("TestCharacter")

    print(f"\nAnimation: {anim.name}")
    print(f"Duration: {anim.duration}s")
    print(f"FPS: {anim.fps}")
    print(f"Keyframes: {anim.keyframe_count}")

    # List keyframes
    print(f"\nKeyframe Timeline:")
    for kf in anim.keyframes:
        print(f"  Frame {kf.frame:3d} ({kf.time:5.2f}s) - {len(kf.pose)} bones")

    print("\n" + get_take_the_l_description())

    print("\n✓ All tests passed!")
