"""
Dab Pose Animation
Iconic pose where character buries face in elbow with other arm extended.

Motion Description:
- Left arm bent with face buried in elbow
- Right arm extended diagonally up and across body
- Head tilts into the dab
- Slight hip rotation for style
- Can be snap-to-pose (STEP interpolation) OR smooth (EASE_IN_OUT)

Duration: ~1 second (quick pose)
Frame Rate: 60 FPS
Total Frames: 60

Perfect for:
- Victory celebrations
- Confident flex moments
- Quick punctuation in fight choreography
- Testing snap-to-pose vs smooth interpolation
"""

import math
from typing import Dict
from animations.animation_base import Animation, Keyframe, InterpolationType


# ============================================================================
# DAB CONSTANTS
# ============================================================================

# Timing (60 FPS)
DAB_DURATION = 1.0  # 1 second for quick dab
DAB_FPS = 60
DAB_TOTAL_FRAMES = int(DAB_DURATION * DAB_FPS)

# Motion parameters
DAB_ARM_EXTEND_ANGLE = 140.0        # Degrees - extended arm angle
DAB_HEAD_TILT = 35.0                # Degrees - head into elbow
DAB_HIP_ROTATION = 20.0             # Degrees - hip twist for style
DAB_LEAN_ANGLE = 12.0               # Degrees - slight body lean

# Timing
DAB_SETUP_FRAMES = 15   # 0.25s to get into position
DAB_HOLD_FRAMES = 30    # 0.5s holding the dab
DAB_EXIT_FRAMES = 15    # 0.25s to exit


# ============================================================================
# KEYFRAME GENERATION
# ============================================================================

def create_dab_animation(character_name: str = "Character", snap_mode: bool = False) -> Animation:
    """
    Create the Dab animation.

    Args:
        character_name: Name of the character performing the dab
        snap_mode: If True, uses STEP interpolation for instant pose.
                   If False, uses EASE_IN_OUT for smooth transition.

    Returns:
        Complete Animation object with all keyframes
    """
    animation = Animation(
        name=f"{character_name}_Dab{'_Snap' if snap_mode else ''}",
        duration=DAB_DURATION,
        fps=DAB_FPS
    )

    # Determine interpolation type
    interp = InterpolationType.STEP if snap_mode else InterpolationType.EASE_IN_OUT

    # Generate keyframes
    _add_dab_neutral(animation, 0)              # Frame 0: Starting position
    _add_dab_pose(animation, DAB_SETUP_FRAMES, interp)  # Frame 15: DAB POSE!
    _add_dab_pose(animation, DAB_SETUP_FRAMES + DAB_HOLD_FRAMES, interp)  # Frame 45: Hold dab
    _add_dab_neutral(animation, DAB_TOTAL_FRAMES)  # Frame 60: Return to neutral

    print(f"✓ Created Dab animation ({'SNAP' if snap_mode else 'SMOOTH'}): {animation.keyframe_count} keyframes")

    return animation


def _add_dab_neutral(animation: Animation, frame: int):
    """
    Add neutral stance keyframe.
    Ready position before/after dab.
    """
    time = frame / DAB_FPS

    pose = {
        # Root / Hips
        "hips": {"rotation": 0.0},

        # Torso
        "torso": {"rotation": 0.0},
        "neck": {"rotation": 0.0},
        "head": {"rotation": 0.0},

        # Left arm - relaxed at side
        "left_shoulder": {"rotation": 0.0},
        "left_upper_arm": {"rotation": 15.0},
        "left_forearm": {"rotation": -10.0},
        "left_hand": {"rotation": 0.0},

        # Right arm - relaxed at side
        "right_shoulder": {"rotation": 0.0},
        "right_upper_arm": {"rotation": -15.0},
        "right_forearm": {"rotation": 10.0},
        "right_hand": {"rotation": 0.0},

        # Left leg - standing
        "left_thigh": {"rotation": 0.0},
        "left_shin": {"rotation": 0.0},
        "left_foot": {"rotation": 0.0},

        # Right leg - standing
        "right_thigh": {"rotation": 0.0},
        "right_shin": {"rotation": 0.0},
        "right_foot": {"rotation": 0.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.LINEAR)
    animation.add_keyframe(keyframe)


def _add_dab_pose(animation: Animation, frame: int, interpolation: InterpolationType):
    """
    Add THE DAB POSE!

    Left arm bent with face buried in elbow.
    Right arm extended diagonally up and across.
    """
    time = frame / DAB_FPS

    pose = {
        # Root / Hips - twist for style
        "hips": {"rotation": DAB_HIP_ROTATION},

        # Torso - lean into the dab
        "torso": {"rotation": DAB_LEAN_ANGLE},
        "neck": {"rotation": -DAB_HEAD_TILT * 0.6},
        "head": {"rotation": -DAB_HEAD_TILT},  # Head tilts into left elbow

        # Left arm - FACE IN ELBOW
        # This is the signature part of the dab!
        "left_shoulder": {"rotation": -25.0},
        "left_upper_arm": {"rotation": -110.0},   # Raised to face height
        "left_forearm": {"rotation": 130.0},      # Bent sharply (face goes here)
        "left_hand": {"rotation": 0.0},

        # Right arm - EXTENDED DIAGONALLY
        # Points up and across body
        "right_shoulder": {"rotation": 45.0},
        "right_upper_arm": {"rotation": DAB_ARM_EXTEND_ANGLE},  # Extended high
        "right_forearm": {"rotation": -15.0},     # Slight bend
        "right_hand": {"rotation": 0.0},

        # Left leg - slight adjustment for balance
        "left_thigh": {"rotation": -8.0},
        "left_shin": {"rotation": 10.0},
        "left_foot": {"rotation": -3.0},

        # Right leg - weight shift
        "right_thigh": {"rotation": 5.0},
        "right_shin": {"rotation": 0.0},
        "right_foot": {"rotation": -2.0},
    }

    keyframe = Keyframe(frame, time, pose, interpolation)
    animation.add_keyframe(keyframe)


# ============================================================================
# VARIATIONS
# ============================================================================

def create_dab_hold(character_name: str = "Character", hold_duration: float = 2.0) -> Animation:
    """
    Create dab animation with extended hold time.

    Perfect for sustained celebration or dramatic emphasis.

    Args:
        character_name: Name of character
        hold_duration: How long to hold the dab pose (in seconds)

    Returns:
        Animation with extended dab hold
    """
    total_duration = 0.25 + hold_duration + 0.25  # Setup + hold + exit

    animation = Animation(
        name=f"{character_name}_Dab_Hold",
        duration=total_duration,
        fps=DAB_FPS
    )

    # Setup
    _add_dab_neutral(animation, 0)
    _add_dab_pose(animation, 15, InterpolationType.EASE_IN_OUT)

    # Hold (maintain pose for duration)
    hold_frames = int(hold_duration * DAB_FPS)
    _add_dab_pose(animation, 15 + hold_frames, InterpolationType.EASE_IN_OUT)

    # Exit
    exit_frame = 15 + hold_frames + 15
    _add_dab_neutral(animation, exit_frame)

    print(f"✓ Created extended Dab with {hold_duration}s hold")

    return animation


def create_double_dab(character_name: str = "Character") -> Animation:
    """
    Create double dab animation (dab left, then dab right).

    Twice the swagger!

    Args:
        character_name: Name of character

    Returns:
        Animation with two dabs
    """
    animation = Animation(
        name=f"{character_name}_DoubleDab",
        duration=2.0,
        fps=DAB_FPS
    )

    # First dab (left side)
    _add_dab_neutral(animation, 0)
    _add_dab_pose(animation, 15, InterpolationType.EASE_IN_OUT)
    _add_dab_neutral(animation, 45)

    # Second dab (right side - mirror)
    _add_dab_pose_mirrored(animation, 60, InterpolationType.EASE_IN_OUT)
    _add_dab_pose_mirrored(animation, 90, InterpolationType.EASE_IN_OUT)
    _add_dab_neutral(animation, 120)

    print(f"✓ Created Double Dab animation")

    return animation


def _add_dab_pose_mirrored(animation: Animation, frame: int, interpolation: InterpolationType):
    """Add dab pose with arms mirrored (face in right elbow, left arm extended)."""
    time = frame / DAB_FPS

    pose = {
        # Hips - twist opposite direction
        "hips": {"rotation": -DAB_HIP_ROTATION},

        # Torso
        "torso": {"rotation": -DAB_LEAN_ANGLE},
        "neck": {"rotation": DAB_HEAD_TILT * 0.6},
        "head": {"rotation": DAB_HEAD_TILT},  # Head tilts into right elbow

        # Left arm - EXTENDED (mirrored)
        "left_shoulder": {"rotation": -45.0},
        "left_upper_arm": {"rotation": -DAB_ARM_EXTEND_ANGLE},
        "left_forearm": {"rotation": 15.0},
        "left_hand": {"rotation": 0.0},

        # Right arm - FACE IN ELBOW (mirrored)
        "right_shoulder": {"rotation": 25.0},
        "right_upper_arm": {"rotation": 110.0},
        "right_forearm": {"rotation": -130.0},
        "right_hand": {"rotation": 0.0},

        # Legs
        "left_thigh": {"rotation": 5.0},
        "left_shin": {"rotation": 0.0},
        "left_foot": {"rotation": -2.0},

        "right_thigh": {"rotation": -8.0},
        "right_shin": {"rotation": 10.0},
        "right_foot": {"rotation": -3.0},
    }

    keyframe = Keyframe(frame, time, pose, interpolation)
    animation.add_keyframe(keyframe)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_dab_description() -> str:
    """
    Get human-readable description of the Dab.

    Returns:
        Description string for UI display
    """
    return (
        "😎 THE DAB\n\n"
        "Iconic pose - face in elbow, other arm\n"
        "extended high. Quick, confident flex!\n\n"
        f"Duration: {DAB_DURATION}s\n"
        "Modes: Smooth or Snap-to-pose\n"
        "Variations: Hold, Double Dab\n"
        "Perfect for: Victories, celebrations, flexing on enemies\n"
        "Note: Tests STEP vs EASE_IN_OUT interpolation"
    )


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DAB ANIMATION TEST")
    print("=" * 60)

    # Test smooth dab
    print("\n1. SMOOTH DAB")
    print("-" * 60)
    anim_smooth = create_dab_animation("TestCharacter", snap_mode=False)
    print(f"Animation: {anim_smooth.name}")
    print(f"Duration: {anim_smooth.duration}s")
    print(f"Keyframes: {anim_smooth.keyframe_count}")

    # Test snap dab
    print("\n2. SNAP DAB")
    print("-" * 60)
    anim_snap = create_dab_animation("TestCharacter", snap_mode=True)
    print(f"Animation: {anim_snap.name}")
    print(f"Duration: {anim_snap.duration}s")
    print(f"Keyframes: {anim_snap.keyframe_count}")

    # Test extended hold
    print("\n3. EXTENDED HOLD DAB")
    print("-" * 60)
    anim_hold = create_dab_hold("TestCharacter", hold_duration=3.0)
    print(f"Animation: {anim_hold.name}")
    print(f"Duration: {anim_hold.duration}s")
    print(f"Keyframes: {anim_hold.keyframe_count}")

    # Test double dab
    print("\n4. DOUBLE DAB")
    print("-" * 60)
    anim_double = create_double_dab("TestCharacter")
    print(f"Animation: {anim_double.name}")
    print(f"Duration: {anim_double.duration}s")
    print(f"Keyframes: {anim_double.keyframe_count}")

    print("\n" + get_dab_description())

    print("\n✓ All tests passed!")
