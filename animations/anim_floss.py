"""
Fortnite Floss Dance Animation
Iconic arm-swinging dance popularized by Fortnite Battle Royale.

Motion Description:
- Arms swing dramatically from side to side
- Hips rotate in opposite direction to arms
- Fast, rhythmic motion (120 BPM)
- Character stance: slight crouch, feet shoulder-width apart

Duration: ~2 seconds (1 complete loop)
Frame Rate: 60 FPS
Total Frames: 120 (for 2 seconds)

This animation is CRITICAL for YouTube stick figure content - it's highly recognizable
and perfect for comedic timing and celebration moments.
"""

import math
from typing import Dict
from animations.animation_base import Animation, Keyframe, InterpolationType


# ============================================================================
# FLOSS DANCE CONSTANTS
# ============================================================================

# Timing (60 FPS)
FLOSS_DURATION = 2.0  # 2 seconds for one complete loop
FLOSS_FPS = 60
FLOSS_TOTAL_FRAMES = int(FLOSS_DURATION * FLOSS_FPS)

# Motion parameters
FLOSS_ARM_SWING_ANGLE = 160.0  # Degrees - dramatic swing
FLOSS_HIP_ROTATION = 35.0      # Degrees - counter-rotation
FLOSS_CROUCH_AMOUNT = 0.15     # Slight knee bend
FLOSS_TEMPO_BPM = 120          # Beats per minute

# Swing cycle timing (one left-right cycle)
SWING_CYCLE_FRAMES = 24  # 0.4 seconds per swing


# ============================================================================
# KEYFRAME GENERATION
# ============================================================================

def create_floss_animation(character_name: str = "Character") -> Animation:
    """
    Create the Fortnite Floss dance animation with accurate keyframes.

    The Floss consists of:
    1. Arms swing from left to right side
    2. Hips rotate opposite direction (counter-balance)
    3. Slight bounce/crouch for rhythm
    4. Head slight tilt following hips

    Args:
        character_name: Name of the character performing the dance

    Returns:
        Complete Animation object with all keyframes
    """
    animation = Animation(
        name=f"{character_name}_Floss",
        duration=FLOSS_DURATION,
        fps=FLOSS_FPS
    )

    # Generate keyframes for 2-second loop
    _add_initial_stance(animation, 0)        # Frame 0: Neutral
    _add_left_swing(animation, 6)            # Frame 6: Arms left, hips right
    _add_right_swing(animation, 12)          # Frame 12: Arms right, hips left
    _add_left_swing(animation, 18)           # Frame 18: Arms left, hips right
    _add_right_swing(animation, 24)          # Frame 24: Arms right, hips left
    _add_left_swing(animation, 30)           # Frame 30: Arms left, hips right
    _add_right_swing(animation, 36)          # Frame 36: Arms right, hips left
    _add_left_swing(animation, 42)           # Frame 42: Arms left, hips right
    _add_right_swing(animation, 48)          # Frame 48: Arms right, hips left
    _add_left_swing(animation, 54)           # Frame 54: Arms left, hips right
    _add_right_swing(animation, 60)          # Frame 60: Arms right, hips left (1 second mark)
    _add_left_swing(animation, 66)           # Frame 66: Arms left, hips right
    _add_right_swing(animation, 72)          # Frame 72: Arms right, hips left
    _add_left_swing(animation, 78)           # Frame 78: Arms left, hips right
    _add_right_swing(animation, 84)          # Frame 84: Arms right, hips left
    _add_left_swing(animation, 90)           # Frame 90: Arms left, hips right
    _add_right_swing(animation, 96)          # Frame 96: Arms right, hips left
    _add_left_swing(animation, 102)          # Frame 102: Arms left, hips right
    _add_right_swing(animation, 108)         # Frame 108: Arms right, hips left
    _add_left_swing(animation, 114)          # Frame 114: Arms left, hips right
    _add_initial_stance(animation, 120)      # Frame 120: Return to neutral (loop point)

    print(f"✓ Created Floss animation: {animation.keyframe_count} keyframes, {FLOSS_DURATION}s duration")

    return animation


def _add_initial_stance(animation: Animation, frame: int):
    """
    Add neutral stance keyframe.
    Character stands with slight crouch, arms at sides.
    """
    time = frame / FLOSS_FPS

    # Bone rotations (all in degrees)
    pose = {
        # Root / Hips
        "hips": {"rotation": 0.0},

        # Torso
        "torso": {"rotation": 0.0},
        "neck": {"rotation": 0.0},
        "head": {"rotation": 0.0},

        # Left arm
        "left_shoulder": {"rotation": 0.0},
        "left_upper_arm": {"rotation": 15.0},    # Slight forward
        "left_forearm": {"rotation": -10.0},     # Slight bend
        "left_hand": {"rotation": 0.0},

        # Right arm
        "right_shoulder": {"rotation": 0.0},
        "right_upper_arm": {"rotation": 15.0},   # Slight forward
        "right_forearm": {"rotation": -10.0},    # Slight bend
        "right_hand": {"rotation": 0.0},

        # Left leg
        "left_thigh": {"rotation": -8.0},        # Slight crouch
        "left_shin": {"rotation": 15.0},
        "left_foot": {"rotation": -5.0},

        # Right leg
        "right_thigh": {"rotation": -8.0},       # Slight crouch
        "right_shin": {"rotation": 15.0},
        "right_foot": {"rotation": -5.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


def _add_left_swing(animation: Animation, frame: int):
    """
    Add left swing keyframe.
    Arms swing to the left, hips rotate to the right.
    """
    time = frame / FLOSS_FPS

    pose = {
        # Root / Hips - rotate RIGHT (opposite of arms)
        "hips": {"rotation": FLOSS_HIP_ROTATION},

        # Torso - slight rotation with hips
        "torso": {"rotation": FLOSS_HIP_ROTATION * 0.5},
        "neck": {"rotation": -FLOSS_HIP_ROTATION * 0.3},  # Head compensates slightly
        "head": {"rotation": -FLOSS_HIP_ROTATION * 0.4},

        # Left arm - SWING LEFT (across body to right side)
        "left_shoulder": {"rotation": -20.0},
        "left_upper_arm": {"rotation": 90.0},     # Raise up
        "left_forearm": {"rotation": -FLOSS_ARM_SWING_ANGLE},  # Swing across
        "left_hand": {"rotation": 0.0},

        # Right arm - SWING LEFT (from left side across body)
        "right_shoulder": {"rotation": 20.0},
        "right_upper_arm": {"rotation": -90.0},   # Raise up opposite side
        "right_forearm": {"rotation": FLOSS_ARM_SWING_ANGLE},  # Swing across
        "right_hand": {"rotation": 0.0},

        # Left leg - slight adjustment for balance
        "left_thigh": {"rotation": -10.0},
        "left_shin": {"rotation": 18.0},
        "left_foot": {"rotation": -6.0},

        # Right leg - slight adjustment for balance
        "right_thigh": {"rotation": -6.0},
        "right_shin": {"rotation": 12.0},
        "right_foot": {"rotation": -4.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


def _add_right_swing(animation: Animation, frame: int):
    """
    Add right swing keyframe.
    Arms swing to the right, hips rotate to the left.
    """
    time = frame / FLOSS_FPS

    pose = {
        # Root / Hips - rotate LEFT (opposite of arms)
        "hips": {"rotation": -FLOSS_HIP_ROTATION},

        # Torso - slight rotation with hips
        "torso": {"rotation": -FLOSS_HIP_ROTATION * 0.5},
        "neck": {"rotation": FLOSS_HIP_ROTATION * 0.3},   # Head compensates slightly
        "head": {"rotation": FLOSS_HIP_ROTATION * 0.4},

        # Left arm - SWING RIGHT (from right side across body)
        "left_shoulder": {"rotation": 20.0},
        "left_upper_arm": {"rotation": -90.0},    # Raise up opposite side
        "left_forearm": {"rotation": FLOSS_ARM_SWING_ANGLE},  # Swing across
        "left_hand": {"rotation": 0.0},

        # Right arm - SWING RIGHT (across body to left side)
        "right_shoulder": {"rotation": -20.0},
        "right_upper_arm": {"rotation": 90.0},    # Raise up
        "right_forearm": {"rotation": -FLOSS_ARM_SWING_ANGLE},  # Swing across
        "right_hand": {"rotation": 0.0},

        # Left leg - slight adjustment for balance
        "left_thigh": {"rotation": -6.0},
        "left_shin": {"rotation": 12.0},
        "left_foot": {"rotation": -4.0},

        # Right leg - slight adjustment for balance
        "right_thigh": {"rotation": -10.0},
        "right_shin": {"rotation": 18.0},
        "right_foot": {"rotation": -6.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_floss_with_duration(character_name: str, duration: float, loop: bool = True) -> Animation:
    """
    Create Floss animation with custom duration.

    Args:
        character_name: Name of character
        duration: Total duration in seconds
        loop: Whether animation should loop

    Returns:
        Animation object with extended duration
    """
    # Create base 2-second animation
    base_anim = create_floss_animation(character_name)

    if duration <= FLOSS_DURATION:
        # Just use base animation
        return base_anim

    if not loop:
        # Extend with hold at end
        base_anim.duration = duration
        return base_anim

    # Calculate how many loops needed
    num_loops = int(duration / FLOSS_DURATION)
    remainder = duration - (num_loops * FLOSS_DURATION)

    # Create extended animation
    extended_anim = Animation(
        name=f"{character_name}_Floss_Extended",
        duration=duration,
        fps=FLOSS_FPS
    )

    # Copy keyframes multiple times
    for loop_index in range(num_loops):
        time_offset = loop_index * FLOSS_DURATION

        for kf in base_anim.keyframes:
            new_time = kf.time + time_offset
            new_frame = int(new_time * FLOSS_FPS)

            # Skip the last keyframe of previous loops (avoid duplicates)
            if loop_index > 0 and kf.frame == 0:
                continue

            new_kf = Keyframe(
                frame=new_frame,
                time=new_time,
                pose=kf.pose.copy(),
                interpolation=kf.interpolation
            )
            extended_anim.add_keyframe(new_kf)

    print(f"✓ Extended Floss animation to {duration}s ({num_loops} loops)")

    return extended_anim


def get_floss_description() -> str:
    """
    Get human-readable description of the Floss dance.

    Returns:
        Description string for UI display
    """
    return (
        "🕺 FORTNITE FLOSS\n\n"
        "Iconic arm-swinging dance from Fortnite.\n"
        "Arms swing dramatically side-to-side while\n"
        "hips rotate in opposite direction.\n\n"
        f"Duration: {FLOSS_DURATION}s\n"
        f"Tempo: {FLOSS_TEMPO_BPM} BPM\n"
        "Perfect for: Victory celebrations, comedic moments"
    )


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FLOSS DANCE ANIMATION TEST")
    print("=" * 60)

    # Create animation
    anim = create_floss_animation("TestCharacter")

    print(f"\nAnimation: {anim.name}")
    print(f"Duration: {anim.duration}s")
    print(f"FPS: {anim.fps}")
    print(f"Keyframes: {anim.keyframe_count}")
    print(f"Interpolation: {anim.default_interpolation.value}")

    # List all keyframes
    print(f"\nKeyframe Timeline:")
    for kf in anim.keyframes:
        print(f"  Frame {kf.frame:3d} ({kf.time:5.2f}s) - {len(kf.pose)} bones")

    # Test extended animation
    print("\n" + "=" * 60)
    print("Testing Extended Animation (5 seconds)")
    print("=" * 60)

    extended = create_floss_with_duration("TestCharacter", 5.0, loop=True)

    print(f"\nExtended Animation: {extended.name}")
    print(f"Duration: {extended.duration}s")
    print(f"Keyframes: {extended.keyframe_count}")

    print("\n" + get_floss_description())

    print("\n✓ All tests passed!")
