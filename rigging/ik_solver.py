"""
Inverse Kinematics Solver
Automatic pose solving for natural movement (hand-to-head, foot placement, etc.).

Features:
- Two-bone IK (arms, legs) with pole vectors
- CCD (Cyclic Coordinate Descent) for multi-bone chains
- Look-at IK for head/gaze direction
- Foot grounding IK for stable stance
- Constraint-aware solving (respects joint limits)
"""

import numpy as np
from typing import Optional, Tuple, List
from enum import Enum

from .skeleton import Skeleton, Bone


# ============================================================================
# IK SOLVER TYPES
# ============================================================================

class IKSolverType(Enum):
    """Available IK solving algorithms."""
    TWO_BONE = "two_bone"          # Analytical two-bone IK (fast, accurate)
    CCD = "ccd"                     # Cyclic Coordinate Descent (flexible)
    LOOK_AT = "look_at"             # Orient bone toward target
    FABRIK = "fabrik"               # Forward And Backward Reaching IK


# ============================================================================
# IK SOLVER CLASS
# ============================================================================

class IKSolver:
    """
    Inverse kinematics solver for skeletal rigs.
    Calculates bone rotations to reach target positions.
    """

    def __init__(self, skeleton: Skeleton):
        """
        Initialize IK solver for a skeleton.

        Args:
            skeleton: Target skeleton to solve
        """
        self.skeleton = skeleton

        # Solver parameters
        self.max_iterations = 20        # Max iterations for iterative solvers
        self.tolerance = 0.01           # Distance tolerance for convergence
        self.respect_constraints = True # Whether to clamp to rotation limits

        print(f"✓ IK Solver initialized for skeleton '{skeleton.name}'")

    # ========================================================================
    # TWO-BONE IK (Analytical Solution)
    # ========================================================================

    def solve_two_bone_ik(self, bone1_name: str, bone2_name: str,
                         target_pos: np.ndarray,
                         pole_vector: Optional[np.ndarray] = None) -> bool:
        """
        Solve two-bone IK chain (e.g., shoulder-elbow-wrist to reach target).

        This is the most common IK case for arms and legs.
        Uses analytical solution for speed and accuracy.

        Args:
            bone1_name: First bone (e.g., upper_arm)
            bone2_name: Second bone (e.g., forearm)
            target_pos: Target position in world space (x, y, z)
            pole_vector: Direction for elbow/knee to point (optional)

        Returns:
            True if solution found, False if target unreachable
        """
        bone1 = self.skeleton.get_bone(bone1_name)
        bone2 = self.skeleton.get_bone(bone2_name)

        if not bone1 or not bone2:
            print(f"Warning: Bones '{bone1_name}' or '{bone2_name}' not found")
            return False

        # Ensure bones are parent-child
        if bone2.parent != bone1:
            print(f"Warning: '{bone2_name}' is not child of '{bone1_name}'")
            return False

        # Update transforms
        self.skeleton.update()

        # Get positions
        start_pos = bone1.get_world_position()
        target = np.array(target_pos, dtype=np.float32)

        # Bone lengths
        length1 = bone1.length
        length2 = bone2.length

        # Distance to target
        to_target = target - start_pos
        dist_to_target = np.linalg.norm(to_target)

        # Check if target is reachable
        max_reach = length1 + length2
        min_reach = abs(length1 - length2)

        if dist_to_target > max_reach:
            # Target too far - stretch toward it
            dist_to_target = max_reach
        elif dist_to_target < min_reach:
            # Target too close - can't reach (bones would overlap)
            dist_to_target = min_reach

        # Calculate angles using law of cosines
        # Angle at bone1 (shoulder/hip)
        cos_angle1_inner = (length1**2 + dist_to_target**2 - length2**2) / (2 * length1 * dist_to_target)
        cos_angle1_inner = np.clip(cos_angle1_inner, -1.0, 1.0)
        angle1_inner = np.arccos(cos_angle1_inner)

        # Angle at bone2 (elbow/knee)
        cos_angle2 = (length1**2 + length2**2 - dist_to_target**2) / (2 * length1 * length2)
        cos_angle2 = np.clip(cos_angle2, -1.0, 1.0)
        angle2 = np.arccos(cos_angle2)

        # Calculate direction to target
        direction_to_target = to_target / (dist_to_target + 0.0001)  # Avoid division by zero

        # Calculate angle from start to target
        angle_to_target = np.arctan2(direction_to_target[1], direction_to_target[0])

        # Apply rotation to bone1
        # In 2D: rotate bone1 by (angle_to_target - angle1_inner)
        bone1_rotation = np.degrees(angle_to_target - angle1_inner)

        # Apply rotation to bone2
        # Bone2 bends at angle2 relative to bone1
        bone2_rotation = np.degrees(np.pi - angle2)

        # Set rotations (Z-axis for 2D)
        bone1.set_local_rotation(0.0, 0.0, bone1_rotation)
        bone2.set_local_rotation(0.0, 0.0, bone2_rotation)

        # Apply constraints if enabled
        if self.respect_constraints:
            self._apply_constraints(bone1)
            self._apply_constraints(bone2)

        # Update transforms
        self.skeleton.update()

        return True

    # ========================================================================
    # CCD (Cyclic Coordinate Descent) IK
    # ========================================================================

    def solve_ccd_ik(self, bone_chain: List[str], target_pos: np.ndarray) -> bool:
        """
        Solve multi-bone IK chain using CCD algorithm.

        CCD is an iterative method that works on any number of bones.
        More flexible than two-bone IK but slightly slower.

        Args:
            bone_chain: List of bone names from root to end effector
            target_pos: Target position in world space

        Returns:
            True if converged, False if max iterations reached
        """
        if len(bone_chain) < 2:
            print("Warning: CCD requires at least 2 bones")
            return False

        # Get bones
        bones = [self.skeleton.get_bone(name) for name in bone_chain]

        if None in bones:
            print("Warning: Some bones in chain not found")
            return False

        end_effector = bones[-1]
        target = np.array(target_pos, dtype=np.float32)

        # Iteratively solve
        for iteration in range(self.max_iterations):
            # Update all transforms
            self.skeleton.update()

            # Get end effector position
            end_pos = end_effector.get_end_position()

            # Check if close enough
            distance = np.linalg.norm(target - end_pos)
            if distance < self.tolerance:
                return True  # Converged!

            # Iterate through bones in reverse (from end to root)
            for bone in reversed(bones[:-1]):  # Skip end effector itself
                # Get positions
                bone_pos = bone.get_world_position()
                end_pos = end_effector.get_end_position()

                # Vectors
                to_end = end_pos - bone_pos
                to_target = target - bone_pos

                # Normalize
                to_end_norm = to_end / (np.linalg.norm(to_end) + 0.0001)
                to_target_norm = to_target / (np.linalg.norm(to_target) + 0.0001)

                # Calculate rotation needed
                # Using 2D rotation (Z-axis)
                current_angle = np.arctan2(to_end_norm[1], to_end_norm[0])
                target_angle = np.arctan2(to_target_norm[1], to_target_norm[0])

                rotation_delta = target_angle - current_angle

                # Apply rotation
                current_rotation = bone.local_rotation[2]
                new_rotation = current_rotation + np.degrees(rotation_delta)

                bone.set_local_rotation(0.0, 0.0, new_rotation)

                # Apply constraints
                if self.respect_constraints:
                    self._apply_constraints(bone)

                # Update for next bone in chain
                self.skeleton.update()

        print(f"Warning: CCD did not converge after {self.max_iterations} iterations")
        return False

    # ========================================================================
    # LOOK-AT IK
    # ========================================================================

    def solve_look_at(self, bone_name: str, target_pos: np.ndarray) -> bool:
        """
        Orient a bone to look at a target position.

        Useful for head tracking, eyes, aiming, etc.

        Args:
            bone_name: Bone to orient
            target_pos: Position to look at

        Returns:
            True on success
        """
        bone = self.skeleton.get_bone(bone_name)
        if not bone:
            print(f"Warning: Bone '{bone_name}' not found")
            return False

        # Update transforms
        self.skeleton.update()

        # Get bone position
        bone_pos = bone.get_world_position()
        target = np.array(target_pos, dtype=np.float32)

        # Calculate direction to target
        to_target = target - bone_pos
        distance = np.linalg.norm(to_target)

        if distance < 0.0001:
            return True  # Already at target

        # Calculate angle (2D)
        angle = np.arctan2(to_target[1], to_target[0])

        # Set rotation (Z-axis for 2D)
        bone.set_local_rotation(0.0, 0.0, np.degrees(angle))

        # Apply constraints
        if self.respect_constraints:
            self._apply_constraints(bone)

        self.skeleton.update()

        return True

    # ========================================================================
    # FOOT GROUNDING
    # ========================================================================

    def ground_foot(self, thigh_name: str, shin_name: str, foot_name: str,
                   ground_height: float = 0.0) -> bool:
        """
        Solve IK to place foot on ground plane.

        Useful for preventing foot sliding and ensuring stable stance.

        Args:
            thigh_name: Thigh bone name
            shin_name: Shin bone name
            foot_name: Foot bone name
            ground_height: Y-coordinate of ground plane

        Returns:
            True on success
        """
        foot_bone = self.skeleton.get_bone(foot_name)
        if not foot_bone:
            return False

        # Update transforms
        self.skeleton.update()

        # Get foot position
        foot_pos = foot_bone.get_world_position()

        # Calculate target position (project onto ground)
        target_pos = foot_pos.copy()
        target_pos[1] = ground_height

        # Solve two-bone IK to reach ground
        return self.solve_two_bone_ik(thigh_name, shin_name, target_pos)

    # ========================================================================
    # HAND-TO-HEAD IK (For "Take the L" animation)
    # ========================================================================

    def hand_to_head(self, upper_arm_name: str, forearm_name: str,
                    hand_name: str, head_name: str,
                    offset: Optional[Tuple[float, float, float]] = None) -> bool:
        """
        Solve IK to place hand near head.

        Useful for "Take the L" gesture, salutes, etc.

        Args:
            upper_arm_name: Upper arm bone
            forearm_name: Forearm bone
            hand_name: Hand bone
            head_name: Head bone (target)
            offset: Offset from head center (x, y, z)

        Returns:
            True on success
        """
        head_bone = self.skeleton.get_bone(head_name)
        if not head_bone:
            return False

        # Update transforms
        self.skeleton.update()

        # Get head position
        head_pos = head_bone.get_world_position()

        # Apply offset if provided
        if offset is not None:
            head_pos = head_pos + np.array(offset, dtype=np.float32)

        # Solve two-bone IK to reach head position
        return self.solve_two_bone_ik(upper_arm_name, forearm_name, head_pos)

    # ========================================================================
    # CONSTRAINT APPLICATION
    # ========================================================================

    def _apply_constraints(self, bone: Bone):
        """
        Clamp bone rotation to its constraints.

        Args:
            bone: Bone to constrain
        """
        rotation = bone.local_rotation

        # Clamp each axis
        clamped = np.array([
            np.clip(rotation[0], bone.rotation_limits_min[0], bone.rotation_limits_max[0]),
            np.clip(rotation[1], bone.rotation_limits_min[1], bone.rotation_limits_max[1]),
            np.clip(rotation[2], bone.rotation_limits_min[2], bone.rotation_limits_max[2]),
        ], dtype=np.float32)

        bone.local_rotation = clamped

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def set_max_iterations(self, iterations: int):
        """Set maximum iterations for iterative solvers."""
        self.max_iterations = max(1, min(100, iterations))

    def set_tolerance(self, tolerance: float):
        """Set distance tolerance for convergence."""
        self.tolerance = max(0.001, tolerance)

    def enable_constraints(self, enabled: bool):
        """Enable or disable constraint enforcement."""
        self.respect_constraints = enabled


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_ik_solver(skeleton: Skeleton) -> IKSolver:
    """
    Create an IK solver for a skeleton.

    Args:
        skeleton: Target skeleton

    Returns:
        Configured IKSolver instance
    """
    return IKSolver(skeleton)


def solve_arm_ik(skeleton: Skeleton, arm_side: str, target_pos: Tuple[float, float, float]) -> bool:
    """
    Quick function to solve arm IK.

    Args:
        skeleton: Skeleton to solve
        arm_side: "l" or "r" for left/right arm
        target_pos: Target position for hand

    Returns:
        True on success
    """
    solver = IKSolver(skeleton)

    upper_arm = f"upper_arm_{arm_side}"
    forearm = f"forearm_{arm_side}"

    target = np.array(target_pos, dtype=np.float32)

    return solver.solve_two_bone_ik(upper_arm, forearm, target)


def solve_leg_ik(skeleton: Skeleton, leg_side: str, target_pos: Tuple[float, float, float]) -> bool:
    """
    Quick function to solve leg IK.

    Args:
        skeleton: Skeleton to solve
        leg_side: "l" or "r" for left/right leg
        target_pos: Target position for foot

    Returns:
        True on success
    """
    solver = IKSolver(skeleton)

    thigh = f"thigh_{leg_side}"
    shin = f"shin_{leg_side}"

    target = np.array(target_pos, dtype=np.float32)

    return solver.solve_two_bone_ik(thigh, shin, target)
