"""
Phoneme Library
Mouth shape library for lip-sync animation to voiceovers.

Features:
- Phoneme-to-mouth-shape mapping
- Text-to-phoneme conversion (simple rule-based)
- Automatic lip-sync keyframe generation from text
- Timing adjustment for natural speech
"""

from typing import List, Dict, Tuple
from enum import Enum
import re

from rigging.facial_rig import MouthShape


# ============================================================================
# PHONEME TYPES
# ============================================================================

class Phoneme(Enum):
    """
    Common phonemes (speech sounds) mapped to mouth shapes.
    Based on standard American English pronunciation.
    """
    # Closed sounds
    M = "m"  # M, B, P

    # Open sounds
    AH = "ah"  # A, AH (father, hot)
    AA = "aa"  # A (cat, bat)
    EH = "eh"  # E (bet, get)
    EE = "ee"  # EE (feet, meet)
    IH = "ih"  # I (sit, bit)
    OH = "oh"  # O (go, boat)
    OO = "oo"  # OO (food, moon)
    UH = "uh"  # U (but, cup)

    # Consonants
    F = "f"    # F, V (teeth on lip)
    S = "s"    # S, Z (teeth together)
    TH = "th"  # TH (teeth out)
    L = "l"    # L (tongue up)
    R = "r"    # R (lips rounded)
    W = "w"    # W (lips rounded)

    # Rest/silence
    REST = "rest"


# ============================================================================
# PHONEME TO MOUTH SHAPE MAPPING
# ============================================================================

PHONEME_TO_MOUTH_SHAPE: Dict[Phoneme, MouthShape] = {
    # Closed sounds
    Phoneme.M: MouthShape.CLOSED,

    # Open vowels
    Phoneme.AH: MouthShape.WIDE_OPEN,
    Phoneme.AA: MouthShape.WIDE_OPEN,
    Phoneme.UH: MouthShape.SMALL_OPEN,

    # Narrow vowels
    Phoneme.EH: MouthShape.NARROW_OPEN,
    Phoneme.EE: MouthShape.NARROW_OPEN,
    Phoneme.IH: MouthShape.NARROW_OPEN,

    # Round vowels
    Phoneme.OH: MouthShape.ROUND_OPEN,
    Phoneme.OO: MouthShape.ROUND_OPEN,
    Phoneme.W: MouthShape.ROUND_OPEN,
    Phoneme.R: MouthShape.ROUND_OPEN,

    # Consonants
    Phoneme.F: MouthShape.TEETH,
    Phoneme.S: MouthShape.TEETH,
    Phoneme.TH: MouthShape.TEETH,
    Phoneme.L: MouthShape.NARROW_OPEN,

    # Rest
    Phoneme.REST: MouthShape.CLOSED,
}


# ============================================================================
# TEXT TO PHONEME CONVERSION
# ============================================================================

class PhonemeConverter:
    """
    Converts text to phoneme sequences for lip-sync.
    Uses simple rule-based approach (good enough for stick figures).
    """

    def __init__(self):
        """Initialize phoneme converter."""
        # Letter/pattern to phoneme mapping (simplified)
        self.rules = [
            # Consonant clusters (check these first)
            (r'th', Phoneme.TH),
            (r'sh', Phoneme.S),
            (r'ch', Phoneme.S),

            # Vowels (context-aware)
            (r'oo', Phoneme.OO),
            (r'ee', Phoneme.EE),
            (r'ea', Phoneme.EE),
            (r'oa', Phoneme.OH),
            (r'ai', Phoneme.AA),
            (r'ay', Phoneme.AA),
            (r'ow', Phoneme.OH),

            # Single vowels
            (r'a', Phoneme.AA),
            (r'e', Phoneme.EH),
            (r'i', Phoneme.IH),
            (r'o', Phoneme.OH),
            (r'u', Phoneme.UH),

            # Consonants
            (r'[mbp]', Phoneme.M),
            (r'[fv]', Phoneme.F),
            (r'[sz]', Phoneme.S),
            (r'[lr]', Phoneme.L),
            (r'w', Phoneme.W),
            (r'r', Phoneme.R),

            # Default rest for punctuation/spaces
            (r'[^a-z]', Phoneme.REST),
        ]

    def text_to_phonemes(self, text: str) -> List[Phoneme]:
        """
        Convert text to phoneme sequence.

        Args:
            text: Input text (words)

        Returns:
            List of phonemes in order
        """
        text = text.lower()
        phonemes = []
        i = 0

        while i < len(text):
            matched = False

            for pattern, phoneme in self.rules:
                # Check if pattern matches at current position
                match = re.match(pattern, text[i:])
                if match:
                    matched_text = match.group(0)

                    # Add phoneme (skip if it's whitespace and we already have a REST)
                    if phoneme != Phoneme.REST or not phonemes or phonemes[-1] != Phoneme.REST:
                        phonemes.append(phoneme)

                    i += len(matched_text)
                    matched = True
                    break

            if not matched:
                i += 1  # Skip unknown character

        return phonemes

    def phonemes_to_mouth_shapes(self, phonemes: List[Phoneme]) -> List[MouthShape]:
        """
        Convert phoneme sequence to mouth shapes.

        Args:
            phonemes: List of phonemes

        Returns:
            List of corresponding mouth shapes
        """
        return [PHONEME_TO_MOUTH_SHAPE.get(p, MouthShape.CLOSED) for p in phonemes]


# ============================================================================
# LIP-SYNC KEYFRAME GENERATOR
# ============================================================================

class LipSyncGenerator:
    """
    Generates animation keyframes for lip-sync from text.
    Creates smooth mouth animations that match speech timing.
    """

    def __init__(self, fps: int = 60):
        """
        Initialize lip-sync generator.

        Args:
            fps: Frames per second for animation
        """
        self.fps = fps
        self.converter = PhonemeConverter()

        # Timing parameters
        self.phoneme_duration = 0.08  # Seconds per phoneme (adjustable)
        self.rest_duration = 0.15     # Pause duration for punctuation

    def generate_lip_sync_keyframes(self, text: str, start_time: float = 0.0) -> List[Tuple[float, MouthShape]]:
        """
        Generate lip-sync keyframes from text.

        Args:
            text: Dialogue text
            start_time: Start time in animation (seconds)

        Returns:
            List of (time, mouth_shape) tuples for keyframing
        """
        # Convert text to phonemes
        phonemes = self.converter.text_to_phonemes(text)

        # Convert phonemes to mouth shapes
        mouth_shapes = self.converter.phonemes_to_mouth_shapes(phonemes)

        # Generate keyframes with timing
        keyframes = []
        current_time = start_time

        for i, mouth_shape in enumerate(mouth_shapes):
            # Add keyframe
            keyframes.append((current_time, mouth_shape))

            # Calculate duration for this phoneme
            if phonemes[i] == Phoneme.REST:
                duration = self.rest_duration
            else:
                duration = self.phoneme_duration

            current_time += duration

        # Add final rest keyframe
        keyframes.append((current_time, MouthShape.CLOSED))

        return keyframes

    def set_speech_speed(self, speed_multiplier: float):
        """
        Adjust speech speed.

        Args:
            speed_multiplier: Speed multiplier (1.0 = normal, 0.5 = slow, 2.0 = fast)
        """
        base_duration = 0.08
        self.phoneme_duration = base_duration / max(0.1, speed_multiplier)


# ============================================================================
# COMMON DIALOGUE PRESETS
# ============================================================================

class DialoguePreset:
    """
    Pre-made dialogue sequences for common fight scenarios.
    Makes it easy to add voiceover to fight animations.
    """

    # Taunts
    TAUNT_1 = "Come on!"
    TAUNT_2 = "Is that all you got?"
    TAUNT_3 = "Bring it!"
    TAUNT_4 = "You cannot defeat me!"

    # Reactions
    HURT_1 = "Ow!"
    HURT_2 = "Ugh!"
    HURT_3 = "Argh!"

    SURPRISE_1 = "What?!"
    SURPRISE_2 = "No way!"
    SURPRISE_3 = "Impossible!"

    # Victory
    VICTORY_1 = "Yeah!"
    VICTORY_2 = "I win!"
    VICTORY_3 = "Too easy!"
    VICTORY_4 = "Victory!"

    # Defeat
    DEFEAT_1 = "No..."
    DEFEAT_2 = "I lost..."
    DEFEAT_3 = "Impossible..."

    @classmethod
    def get_all_taunts(cls) -> List[str]:
        """Get all taunt phrases."""
        return [cls.TAUNT_1, cls.TAUNT_2, cls.TAUNT_3, cls.TAUNT_4]

    @classmethod
    def get_all_reactions(cls) -> List[str]:
        """Get all reaction phrases."""
        return [cls.HURT_1, cls.HURT_2, cls.HURT_3,
                cls.SURPRISE_1, cls.SURPRISE_2, cls.SURPRISE_3]

    @classmethod
    def get_all_victory(cls) -> List[str]:
        """Get all victory phrases."""
        return [cls.VICTORY_1, cls.VICTORY_2, cls.VICTORY_3, cls.VICTORY_4]


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_lip_sync_from_text(text: str, start_time: float = 0.0,
                             fps: int = 60) -> List[Tuple[float, MouthShape]]:
    """
    Quick function to generate lip-sync keyframes from text.

    Args:
        text: Dialogue text
        start_time: Start time in seconds
        fps: Animation FPS

    Returns:
        List of (time, mouth_shape) keyframe tuples
    """
    generator = LipSyncGenerator(fps)
    return generator.generate_lip_sync_keyframes(text, start_time)


def get_mouth_shape_for_text(text: str, time_in_dialogue: float) -> MouthShape:
    """
    Get mouth shape at a specific time during dialogue.

    Args:
        text: Dialogue text
        time_in_dialogue: Time offset into the dialogue (seconds)

    Returns:
        Mouth shape at that time
    """
    keyframes = create_lip_sync_from_text(text, 0.0)

    # Find keyframe at or before this time
    current_shape = MouthShape.CLOSED

    for kf_time, shape in keyframes:
        if kf_time <= time_in_dialogue:
            current_shape = shape
        else:
            break

    return current_shape


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Generate lip-sync for a taunt
    text = "You cannot defeat me!"

    generator = LipSyncGenerator()
    keyframes = generator.generate_lip_sync_keyframes(text, start_time=0.0)

    print(f"Lip-sync keyframes for: '{text}'")
    print(f"Total duration: {keyframes[-1][0]:.2f} seconds")
    print("\nKeyframes:")
    for time, mouth_shape in keyframes:
        print(f"  {time:.3f}s: {mouth_shape.value}")
