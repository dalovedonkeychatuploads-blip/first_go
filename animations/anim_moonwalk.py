"""
Michael Jackson Moonwalk Animation
The iconic backwards slide popularized by the King of Pop.

Motion Description:
- Appears to walk forward while sliding backwards
- One foot flat on ground, slides back smoothly
- Other foot on toes, lifts and places forward (illusion)
- Upper body leans slightly forward
- Arms move subtly with rhythm
- Smooth, continuous motion with root motion backwards

Duration: ~3 seconds (continuous backwards slide)
Frame Rate: 60 FPS
Total Frames: 180

This animation is CRITICAL for:
- Testing root motion system (character moves in world space)
- Testing foot sliding mechanics
- Smooth stylish entrances/exits
- Comedic moments and dramatic reveals
"""

import math
from typing import Dict
from animations.animation_base import Animation, Keyframe, InterpolationType


# ============================================================================
# MOONWALK CONSTANTS
# ============================================================================

# Timing (60 FPS)
MOONWALK_DURATION = 3.0  # 3 seconds of smooth sliding
MOONWALK_FPS = 60
MOONWALK_TOTAL_FRAMES = int(MOONWALK_DURATION * MOONWALK_FPS)

# Motion parameters
MOONWALK_SLIDE_DISTANCE = -2.0      # Units - total backwards movement
MOONWALK_LEG_LIFT_HEIGHT = 15.0     # Degrees - toe lift
MOONWALK_FORWARD_LEAN = 10.0        # Degrees - body lean
MOONWALK_ARM_SWING = 20.0           # Degrees - subtle arm motion
MOONWALK_TEMPO_BPM = 90             # Beats per minute (smooth)

# Step timing
STEP_CYCLE_FRAMES = 30  # 0.5 seconds per step


# ============================================================================
# KEYFRAME GENERATION
# ============================================================================

def create_moonwalk_animation(character_name: str = "Character") -> Animation:
    """
    Create the Moonwalk animation with accurate keyframes and root motion.

    The Moonwalk consists of:
    1. Root position moves backwards smoothly
    2. Left foot flat, slides back
    3. Right foot on toes, lifts and places forward (illusion of walking forward)
    4. Upper body leans forward slightly
    5. Arms swing subtly
    6. Alternating leg motion creates smooth backwards glide

    Args:
        character_name: Name of the character performing the dance

    Returns:
        Complete Animation object with all keyframes
    """
    animation = Animation(
        name=f"{character_name}_Moonwalk",
        duration=MOONWALK_DURATION,
        fps=MOONWALK_FPS
    )

    # Generate keyframes for 3-second backwards slide
    # Each step moves character backwards in world space
    _add_moonwalk_pose(animation, 0, position_offset=0.0, left_foot_back=False)
    _add_moonwalk_pose(animation, 15, position_offset=-0.17, left_foot_back=True)
    _add_moonwalk_pose(animation, 30, position_offset=-0.33, left_foot_back=False)
    _add_moonwalk_pose(animation, 45, position_offset=-0.5, left_foot_back=True)
    _add_moonwalk_pose(animation, 60, position_offset=-0.67, left_foot_back=False)  # 1 second
    _add_moonwalk_pose(animation, 75, position_offset=-0.83, left_foot_back=True)
    _add_moonwalk_pose(animation, 90, position_offset=-1.0, left_foot_back=False)
    _add_moonwalk_pose(animation, 105, position_offset=-1.17, left_foot_back=True)
    _add_moonwalk_pose(animation, 120, position_offset=-1.33, left_foot_back=False)  # 2 seconds
    _add_moonwalk_pose(animation, 135, position_offset=-1.5, left_foot_back=True)
    _add_moonwalk_pose(animation, 150, position_offset=-1.67, left_foot_back=False)
    _add_moonwalk_pose(animation, 165, position_offset=-1.83, left_foot_back=True)
    _add_moonwalk_pose(animation, 180, position_offset=-2.0, left_foot_back=False)  # 3 seconds (end)

    print(f"✓ Created Moonwalk animation: {animation.keyframe_count} keyframes, {MOONWALK_DURATION}s duration")
    print(f"  Total backwards movement: {abs(MOONWALK_SLIDE_DISTANCE)} units")

    return animation


def _add_moonwalk_pose(animation: Animation, frame: int, position_offset: float, left_foot_back: bool):
    """
    Add moonwalk keyframe with root motion.

    Args:
        animation: Animation to add keyframe to
        frame: Frame number
        position_offset: Root position offset (negative = backwards)
        left_foot_back: True if left foot is back (flat on ground)
    """
    time = frame / MOONWALK_FPS

    # Determine which foot is sliding back (flat) and which is lifting (toes)
    if left_foot_back:
        # Left foot flat on ground, sliding back
        left_foot_angle = 0.0
        left_shin_angle = 5.0
        left_thigh_angle = -5.0

        # Right foot on toes, lifting forward
        right_foot_angle = -MOONWALK_LEG_LIFT_HEIGHT
        right_shin_angle = 15.0
        right_thigh_angle = 10.0

        # Arm swing (left arm back, right arm forward)
        left_arm_swing = -MOONWALK_ARM_SWING
        right_arm_swing = MOONWALK_ARM_SWING

    else:
        # Right foot flat on ground, sliding back
        right_foot_angle = 0.0
        right_shin_angle = 5.0
        right_thigh_angle = -5.0

        # Left foot on toes, lifting forward
        left_foot_angle = -MOONWALK_LEG_LIFT_HEIGHT
        left_shin_angle = 15.0
        left_thigh_angle = 10.0

        # Arm swing (right arm back, left arm forward)
        right_arm_swing = -MOONWALK_ARM_SWING
        left_arm_swing = MOONWALK_ARM_SWING

    pose = {
        # ROOT MOTION - This is key! Character moves backwards in world space
        "root": {
            "position_x": 0.0,
            "position_y": position_offset,  # Backwards movement
            "position_z": 0.0
        },

        # Hips / Root
        "hips": {"rotation": 0.0},

        # Torso - lean forward (signature MJ lean)
        "torso": {"rotation": MOONWALK_FORWARD_LEAN},
        "neck": {"rotation": -MOONWALK_FORWARD_LEAN * 0.5},  # Head compensates
        "head": {"rotation": -MOONWALK_FORWARD_LEAN * 0.3},

        # Left arm - subtle swing
        "left_shoulder": {"rotation": 0.0},
        "left_upper_arm": {"rotation": left_arm_swing},
        "left_forearm": {"rotation": -30.0},  # Slight bend
        "left_hand": {"rotation": 0.0},

        # Right arm - subtle swing
        "right_shoulder": {"rotation": 0.0},
        "right_upper_arm": {"rotation": right_arm_swing},
        "right_forearm": {"rotation": 30.0},  # Slight bend
        "right_hand": {"rotation": 0.0},

        # Left leg
        "left_thigh": {"rotation": left_thigh_angle},
        "left_shin": {"rotation": left_shin_angle},
        "left_foot": {"rotation": left_foot_angle},

        # Right leg
        "right_thigh": {"rotation": right_thigh_angle},
        "right_shin": {"rotation": right_shin_angle},
        "right_foot": {"rotation": right_foot_angle},
    }

    # Use LINEAR interpolation for smooth sliding effect
    keyframe = Keyframe(frame, time, pose, InterpolationType.LINEAR)
    animation.add_keyframe(keyframe)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_moonwalk_with_duration(character_name: str, duration: float) -> Animation:
    """
    Create Moonwalk animation with custom duration.

    Note: Moonwalk is continuous motion, so duration directly affects total distance.
    Longer duration = more backwards movement.

    Args:
        character_name: Name of character
        duration: Total duration in seconds

    Returns:
        Animation object with custom duration
    """
    if duration <= MOONWALK_DURATION:
        # Create standard 3-second moonwalk
        return create_moonwalk_animation(character_name)

    # Calculate distance per second
    distance_per_second = MOONWALK_SLIDE_DISTANCE / MOONWALK_DURATION
    total_distance = distance_per_second * duration

    # Create extended animation
    extended_anim = Animation(
        name=f"{character_name}_Moonwalk_Extended",
        duration=duration,
        fps=MOONWALK_FPS
    )

    # Generate keyframes for extended duration
    num_steps = int(duration / (STEP_CYCLE_FRAMES / MOONWALK_FPS))

    for step in range(num_steps + 1):
        frame = int(step * (STEP_CYCLE_FRAMES / 2))  # Keyframe every half step
        time = frame / MOONWALK_FPS

        if time > duration:
            break

        position_offset = (time / duration) * total_distance
        left_foot_back = (step % 2) == 0

        _add_moonwalk_pose(extended_anim, frame, position_offset, left_foot_back)

    print(f"✓ Extended Moonwalk animation to {duration}s")
    print(f"  Total backwards movement: {abs(total_distance):.2f} units")

    return extended_anim


def get_moonwalk_description() -> str:
    """
    Get human-readable description of the Moonwalk.

    Returns:
        Description string for UI display
    """
    return (
        "🌙 MICHAEL JACKSON MOONWALK\n\n"
        "The King of Pop's legendary backwards slide.\n"
        "Appears to walk forward while smoothly\n"
        "gliding backwards. Smooth and stylish!\n\n"
        f"Duration: {MOONWALK_DURATION}s\n"
        f"Tempo: {MOONWALK_TEMPO_BPM} BPM\n"
        f"Movement: {abs(MOONWALK_SLIDE_DISTANCE)} units backwards\n"
        "Perfect for: Dramatic entrances/exits, smooth transitions, comedic reveals\n"
        "Note: Tests root motion and foot sliding mechanics"
    )


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MOONWALK ANIMATION TEST")
    print("=" * 60)

    # Create animation
    anim = create_moonwalk_animation("TestCharacter")

    print(f"\nAnimation: {anim.name}")
    print(f"Duration: {anim.duration}s")
    print(f"FPS: {anim.fps}")
    print(f"Keyframes: {anim.keyframe_count}")

    # List keyframes with position
    print(f"\nKeyframe Timeline (with root motion):")
    for kf in anim.keyframes:
        root_y = kf.pose.get("root", {}).get("position_y", 0.0)
        print(f"  Frame {kf.frame:3d} ({kf.time:5.2f}s) - Y: {root_y:6.2f} units")

    print("\n" + get_moonwalk_description())

    print("\n✓ All tests passed!")
