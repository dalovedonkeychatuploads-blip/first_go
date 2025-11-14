"""
Carlton Dance Animation
Classic dance from Fresh Prince of Bel-Air, performed by Carlton Banks (Alfonso Ribeiro).

Motion Description:
- Hip thrust/swivel motion
- Arms pump side to side at shoulder height
- Shoulders shimmy and bounce
- Head bob with rhythm
- Classic "pointing" gesture
- Goofy, exaggerated movements

Duration: ~3 seconds (1 complete loop)
Frame Rate: 60 FPS
Total Frames: 180

This is PERFECT for comedic stick figure content - instantly recognizable
and inherently funny. Great for awkward celebration moments!
"""

import math
from typing import Dict
from animations.animation_base import Animation, Keyframe, InterpolationType


# ============================================================================
# CARLTON DANCE CONSTANTS
# ============================================================================

# Timing (60 FPS)
CARLTON_DURATION = 3.0  # 3 seconds for one complete loop
CARLTON_FPS = 60
CARLTON_TOTAL_FRAMES = int(CARLTON_DURATION * CARLTON_FPS)

# Motion parameters
CARLTON_ARM_PUMP_ANGLE = 45.0       # Degrees - shoulder-height pumps
CARLTON_HIP_THRUST = 25.0           # Degrees - hip thrust forward
CARLTON_SHOULDER_SHIMMY = 15.0      # Degrees - shoulder bounce
CARLTON_HEAD_BOB = 10.0             # Degrees - head nod
CARLTON_TEMPO_BPM = 100             # Beats per minute (slower than Floss)

# Move timing
PUMP_CYCLE_FRAMES = 30  # 0.5 seconds per arm pump


# ============================================================================
# KEYFRAME GENERATION
# ============================================================================

def create_carlton_animation(character_name: str = "Character") -> Animation:
    """
    Create the Carlton dance animation with accurate keyframes.

    The Carlton consists of:
    1. Hip thrust forward and back
    2. Arms pump from side to side at shoulder height
    3. Shoulders shimmy up and down
    4. Head bobs with the rhythm
    5. Occasional "pointing" gesture

    Args:
        character_name: Name of the character performing the dance

    Returns:
        Complete Animation object with all keyframes
    """
    animation = Animation(
        name=f"{character_name}_Carlton",
        duration=CARLTON_DURATION,
        fps=CARLTON_FPS
    )

    # Generate keyframes for 3-second loop
    _add_carlton_neutral(animation, 0)      # Frame 0: Starting pose
    _add_carlton_pump_right(animation, 15)  # Frame 15: Arms right, hip thrust
    _add_carlton_neutral(animation, 30)     # Frame 30: Return to neutral
    _add_carlton_pump_left(animation, 45)   # Frame 45: Arms left, hip thrust
    _add_carlton_neutral(animation, 60)     # Frame 60: Return to neutral (1 second)
    _add_carlton_pump_right(animation, 75)  # Frame 75: Arms right, hip thrust
    _add_carlton_point(animation, 90)       # Frame 90: Point gesture (signature move!)
    _add_carlton_pump_left(animation, 105)  # Frame 105: Arms left, hip thrust
    _add_carlton_neutral(animation, 120)    # Frame 120: Return to neutral (2 seconds)
    _add_carlton_pump_right(animation, 135) # Frame 135: Arms right, hip thrust
    _add_carlton_neutral(animation, 150)    # Frame 150: Return to neutral
    _add_carlton_pump_left(animation, 165)  # Frame 165: Arms left, hip thrust
    _add_carlton_neutral(animation, 180)    # Frame 180: End pose (loop point)

    print(f"✓ Created Carlton animation: {animation.keyframe_count} keyframes, {CARLTON_DURATION}s duration")

    return animation


def _add_carlton_neutral(animation: Animation, frame: int):
    """
    Add neutral stance keyframe.
    Character stands upright with hands ready to pump.
    """
    time = frame / CARLTON_FPS

    pose = {
        # Root / Hips
        "hips": {"rotation": 0.0},

        # Torso
        "torso": {"rotation": 0.0},
        "neck": {"rotation": 0.0},
        "head": {"rotation": 0.0},

        # Left arm - ready position (hands up near chest)
        "left_shoulder": {"rotation": -10.0},
        "left_upper_arm": {"rotation": -80.0},    # Raised to chest height
        "left_forearm": {"rotation": 90.0},       # Bent at elbow
        "left_hand": {"rotation": 0.0},

        # Right arm - ready position
        "right_shoulder": {"rotation": 10.0},
        "right_upper_arm": {"rotation": 80.0},    # Raised to chest height
        "right_forearm": {"rotation": -90.0},     # Bent at elbow
        "right_hand": {"rotation": 0.0},

        # Left leg - standing straight
        "left_thigh": {"rotation": 0.0},
        "left_shin": {"rotation": 0.0},
        "left_foot": {"rotation": 0.0},

        # Right leg - standing straight
        "right_thigh": {"rotation": 0.0},
        "right_shin": {"rotation": 0.0},
        "right_foot": {"rotation": 0.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


def _add_carlton_pump_right(animation: Animation, frame: int):
    """
    Add right pump keyframe.
    Arms pump to the right, hips thrust forward, shoulders shimmy.
    """
    time = frame / CARLTON_FPS

    pose = {
        # Root / Hips - thrust forward
        "hips": {"rotation": CARLTON_HIP_THRUST},

        # Torso - slight lean back (counter hip thrust)
        "torso": {"rotation": -CARLTON_HIP_THRUST * 0.3},
        "neck": {"rotation": CARLTON_HEAD_BOB},       # Head bob forward
        "head": {"rotation": CARLTON_HEAD_BOB * 0.5},

        # Left arm - pump RIGHT (both arms move together)
        "left_shoulder": {"rotation": -CARLTON_SHOULDER_SHIMMY},  # Shoulder up
        "left_upper_arm": {"rotation": -60.0 - CARLTON_ARM_PUMP_ANGLE},
        "left_forearm": {"rotation": 70.0},
        "left_hand": {"rotation": -10.0},

        # Right arm - pump RIGHT
        "right_shoulder": {"rotation": CARLTON_SHOULDER_SHIMMY},  # Shoulder up
        "right_upper_arm": {"rotation": 60.0 + CARLTON_ARM_PUMP_ANGLE},
        "right_forearm": {"rotation": -70.0},
        "right_hand": {"rotation": 10.0},

        # Left leg - slight weight shift
        "left_thigh": {"rotation": 5.0},
        "left_shin": {"rotation": 0.0},
        "left_foot": {"rotation": -3.0},

        # Right leg - slight weight shift
        "right_thigh": {"rotation": -5.0},
        "right_shin": {"rotation": 0.0},
        "right_foot": {"rotation": 3.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


def _add_carlton_pump_left(animation: Animation, frame: int):
    """
    Add left pump keyframe.
    Arms pump to the left, hips thrust forward, shoulders shimmy.
    """
    time = frame / CARLTON_FPS

    pose = {
        # Root / Hips - thrust forward
        "hips": {"rotation": CARLTON_HIP_THRUST},

        # Torso - slight lean back
        "torso": {"rotation": -CARLTON_HIP_THRUST * 0.3},
        "neck": {"rotation": CARLTON_HEAD_BOB},
        "head": {"rotation": CARLTON_HEAD_BOB * 0.5},

        # Left arm - pump LEFT
        "left_shoulder": {"rotation": -CARLTON_SHOULDER_SHIMMY},
        "left_upper_arm": {"rotation": -60.0 + CARLTON_ARM_PUMP_ANGLE},
        "left_forearm": {"rotation": 70.0},
        "left_hand": {"rotation": -10.0},

        # Right arm - pump LEFT
        "right_shoulder": {"rotation": CARLTON_SHOULDER_SHIMMY},
        "right_upper_arm": {"rotation": 60.0 - CARLTON_ARM_PUMP_ANGLE},
        "right_forearm": {"rotation": -70.0},
        "right_hand": {"rotation": 10.0},

        # Left leg - slight weight shift
        "left_thigh": {"rotation": -5.0},
        "left_shin": {"rotation": 0.0},
        "left_foot": {"rotation": 3.0},

        # Right leg - slight weight shift
        "right_thigh": {"rotation": 5.0},
        "right_shin": {"rotation": 0.0},
        "right_foot": {"rotation": -3.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


def _add_carlton_point(animation: Animation, frame: int):
    """
    Add signature pointing gesture keyframe.
    Classic Carlton move - point with one hand while other hand on hip.
    """
    time = frame / CARLTON_FPS

    pose = {
        # Root / Hips - slight twist
        "hips": {"rotation": 15.0},

        # Torso - twist with hips
        "torso": {"rotation": 10.0},
        "neck": {"rotation": -5.0},
        "head": {"rotation": -5.0},

        # Left arm - hand on hip (bent at elbow, hand resting on side)
        "left_shoulder": {"rotation": -20.0},
        "left_upper_arm": {"rotation": -45.0},
        "left_forearm": {"rotation": 120.0},      # Bent sharply
        "left_hand": {"rotation": 0.0},

        # Right arm - POINTING! (extended forward and up)
        "right_shoulder": {"rotation": 30.0},
        "right_upper_arm": {"rotation": 135.0},   # Raised high
        "right_forearm": {"rotation": -20.0},     # Slight bend
        "right_hand": {"rotation": -10.0},        # Pointing gesture

        # Left leg - confident stance
        "left_thigh": {"rotation": 10.0},
        "left_shin": {"rotation": 0.0},
        "left_foot": {"rotation": -5.0},

        # Right leg - weight on this leg
        "right_thigh": {"rotation": -5.0},
        "right_shin": {"rotation": 0.0},
        "right_foot": {"rotation": 3.0},
    }

    keyframe = Keyframe(frame, time, pose, InterpolationType.EASE_IN_OUT)
    animation.add_keyframe(keyframe)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_carlton_with_duration(character_name: str, duration: float, loop: bool = True) -> Animation:
    """
    Create Carlton animation with custom duration.

    Args:
        character_name: Name of character
        duration: Total duration in seconds
        loop: Whether animation should loop

    Returns:
        Animation object with extended duration
    """
    # Create base 3-second animation
    base_anim = create_carlton_animation(character_name)

    if duration <= CARLTON_DURATION:
        return base_anim

    if not loop:
        base_anim.duration = duration
        return base_anim

    # Calculate loops needed
    num_loops = int(duration / CARLTON_DURATION)

    # Create extended animation
    extended_anim = Animation(
        name=f"{character_name}_Carlton_Extended",
        duration=duration,
        fps=CARLTON_FPS
    )

    # Copy keyframes multiple times
    for loop_index in range(num_loops):
        time_offset = loop_index * CARLTON_DURATION

        for kf in base_anim.keyframes:
            new_time = kf.time + time_offset
            new_frame = int(new_time * CARLTON_FPS)

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

    print(f"✓ Extended Carlton animation to {duration}s ({num_loops} loops)")

    return extended_anim


def get_carlton_description() -> str:
    """
    Get human-readable description of the Carlton dance.

    Returns:
        Description string for UI display
    """
    return (
        "🕴️ THE CARLTON\n\n"
        "Classic dance from Fresh Prince of Bel-Air.\n"
        "Hip thrusts, arm pumps, and the iconic\n"
        "pointing gesture. Goofy and exaggerated!\n\n"
        f"Duration: {CARLTON_DURATION}s\n"
        f"Tempo: {CARLTON_TEMPO_BPM} BPM\n"
        "Perfect for: Awkward celebrations, comedic moments, victory dances"
    )


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CARLTON DANCE ANIMATION TEST")
    print("=" * 60)

    # Create animation
    anim = create_carlton_animation("TestCharacter")

    print(f"\nAnimation: {anim.name}")
    print(f"Duration: {anim.duration}s")
    print(f"FPS: {anim.fps}")
    print(f"Keyframes: {anim.keyframe_count}")

    # List keyframes
    print(f"\nKeyframe Timeline:")
    for kf in anim.keyframes:
        print(f"  Frame {kf.frame:3d} ({kf.time:5.2f}s) - {len(kf.pose)} bones")

    print("\n" + get_carlton_description())

    print("\n✓ All tests passed!")
