"""
Floob 2.0 Configuration Module.

Centralizes all magic numbers, color palettes, timing constants,
and evolution thresholds for easy tuning and consistency.
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class Colors:
    """
    Pastel color palette for Floob 2.0.

    All colors are soft pastels designed to be easy on the eyes
    and create a cohesive, friendly aesthetic.

    Attributes:
        Base colors (10 pastel shades with light/dark variants):
        - SOFT_PINK: Blush, hearts, affection
        - SOFT_BLUE: Water effects, calm states
        - SOFT_PURPLE: Mystic, sleep, dreamy
        - SOFT_GREEN: Nature, health, growth
        - SOFT_YELLOW: Energy, happy, alert
        - SOFT_ORANGE: Warm, food, cozy
        - SOFT_CREAM: Highlights, neutral
        - SOFT_GRAY: Shadows, outlines
        - SOFT_MINT: Fresh, playful
        - SOFT_LAVENDER: Gentle, soothing
    """

    # Base Pastels (from scope document)
    SOFT_PINK: str = "#FFD6E0"
    SOFT_BLUE: str = "#A2D2FF"
    SOFT_PURPLE: str = "#CDB4DB"
    SOFT_GREEN: str = "#B5E48C"
    SOFT_YELLOW: str = "#FFF3B0"
    SOFT_ORANGE: str = "#FFB5A7"
    SOFT_CREAM: str = "#FFF8F0"
    SOFT_GRAY: str = "#E8E8E8"
    SOFT_MINT: str = "#B8E0D2"
    SOFT_LAVENDER: str = "#D8B4E2"

    # Light Variants (for highlights)
    LIGHT_PINK: str = "#FFE8ED"
    LIGHT_BLUE: str = "#C5E4FF"
    LIGHT_PURPLE: str = "#E2D4EA"
    LIGHT_GREEN: str = "#D0F0B8"
    LIGHT_YELLOW: str = "#FFF9D6"
    LIGHT_ORANGE: str = "#FFD6CF"
    LIGHT_CREAM: str = "#FFFCF7"
    LIGHT_GRAY: str = "#F5F5F5"
    LIGHT_MINT: str = "#D4EFE7"
    LIGHT_LAVENDER: str = "#EBD8F0"

    # Dark Variants (for shadows, outlines)
    DARK_PINK: str = "#E8A8B8"
    DARK_BLUE: str = "#7AB8E8"
    DARK_PURPLE: str = "#A890B0"
    DARK_GREEN: str = "#8BC862"
    DARK_YELLOW: str = "#E8D888"
    DARK_ORANGE: str = "#E89080"
    DARK_CREAM: str = "#E8E0D0"
    DARK_GRAY: str = "#C8C8C8"
    DARK_MINT: str = "#90C8B8"
    DARK_LAVENDER: str = "#B890C8"

    # Special Colors
    WHITE: str = "#FFFFFF"
    BLACK: str = "#2D2D2D"
    TRANSPARENT: str = "#00000000"

    # UI Colors
    UI_BACKGROUND: str = "#FEFEFE"
    UI_BORDER: str = "#D0D0D0"
    UI_TEXT: str = "#404040"
    UI_TEXT_LIGHT: str = "#808080"

    # Stat Bar Colors
    HUNGER_BAR: str = "#FFB5A7"  # Soft Orange
    HAPPINESS_BAR: str = "#FFF3B0"  # Soft Yellow
    ENERGY_BAR: str = "#A2D2FF"  # Soft Blue
    XP_BAR: str = "#B5E48C"  # Soft Green

    # Evolution Stage Tints
    EGG_TINT: str = "#FFFAF0"  # Warm white glow
    BABY_TINT: str = "#F8F4FF"  # Extra soft/desaturated
    CHILD_TINT: str = "#FFFFFF"  # Base colors (no tint)
    TEEN_TINT: str = "#FFFBF0"  # Slightly warm
    ADULT_TINT: str = "#FFFFFF"  # Full saturation


# Evolution form color mappings
FORM_COLORS: Dict[str, Dict[str, str]] = {
    # EGG stage
    "egg": {
        "primary": Colors.SOFT_CREAM,
        "secondary": Colors.LIGHT_YELLOW,
        "accent": Colors.SOFT_ORANGE,
    },
    # BABY stage
    "bloblet": {
        "primary": Colors.SOFT_PINK,
        "secondary": Colors.LIGHT_PINK,
        "accent": Colors.SOFT_CREAM,
    },
    # CHILD stage
    "bouncy": {
        "primary": Colors.SOFT_YELLOW,
        "secondary": Colors.LIGHT_YELLOW,
        "accent": Colors.SOFT_ORANGE,
    },
    "balanced": {
        "primary": Colors.SOFT_BLUE,
        "secondary": Colors.LIGHT_BLUE,
        "accent": Colors.SOFT_MINT,
    },
    "sleepy": {
        "primary": Colors.SOFT_LAVENDER,
        "secondary": Colors.LIGHT_LAVENDER,
        "accent": Colors.SOFT_PURPLE,
    },
    # TEEN stage
    "sparky": {
        "primary": Colors.SOFT_YELLOW,
        "secondary": Colors.LIGHT_ORANGE,
        "accent": Colors.SOFT_ORANGE,
    },
    "zippy": {
        "primary": Colors.SOFT_MINT,
        "secondary": Colors.LIGHT_MINT,
        "accent": Colors.SOFT_GREEN,
    },
    "chill": {
        "primary": Colors.SOFT_BLUE,
        "secondary": Colors.LIGHT_BLUE,
        "accent": Colors.SOFT_PURPLE,
    },
    "dreamy": {
        "primary": Colors.SOFT_PURPLE,
        "secondary": Colors.LIGHT_PURPLE,
        "accent": Colors.SOFT_LAVENDER,
    },
    "cozy": {
        "primary": Colors.SOFT_ORANGE,
        "secondary": Colors.LIGHT_ORANGE,
        "accent": Colors.SOFT_CREAM,
    },
    # ADULT stage
    "zapper": {
        "primary": Colors.SOFT_YELLOW,
        "secondary": Colors.LIGHT_YELLOW,
        "accent": "#FFE066",  # Brighter yellow accent
    },
    "dasher": {
        "primary": Colors.SOFT_GREEN,
        "secondary": Colors.LIGHT_GREEN,
        "accent": Colors.SOFT_MINT,
    },
    "loafer": {
        "primary": Colors.SOFT_BLUE,
        "secondary": Colors.LIGHT_BLUE,
        "accent": Colors.SOFT_GRAY,
    },
    "mystic": {
        "primary": Colors.SOFT_PURPLE,
        "secondary": Colors.LIGHT_LAVENDER,
        "accent": "#C8A8E8",  # Deeper purple accent
    },
    "floofy": {
        "primary": Colors.SOFT_PINK,
        "secondary": Colors.SOFT_CREAM,
        "accent": Colors.SOFT_ORANGE,
    },
    # SPECIAL forms
    "golden": {
        "primary": "#FFD700",  # Gold
        "secondary": "#FFF8DC",  # Cornsilk
        "accent": "#FFE066",  # Light gold
    },
    "ghost": {
        "primary": "#E8E8F0",  # Ghostly white
        "secondary": "#D0D0E0",  # Pale blue-gray
        "accent": Colors.SOFT_PURPLE,
    },
    "rainbow": {
        "primary": Colors.SOFT_PINK,  # Cycles through colors
        "secondary": Colors.SOFT_BLUE,
        "accent": Colors.SOFT_GREEN,
    },
}


@dataclass(frozen=True)
class Timing:
    """
    Timing constants for animations, decay rates, and game loop.

    All time values are in seconds unless otherwise noted.
    """

    # Frame rate
    TARGET_FPS: int = 30
    FRAME_TIME: float = 1.0 / 30  # ~33ms per frame

    # Stat decay rates (per second)
    HUNGER_DECAY_RATE: float = 0.15
    HAPPINESS_DECAY_RATE: float = 0.08
    ENERGY_DECAY_RATE: float = 0.05
    ENERGY_REGEN_RATE: float = 0.3  # When sleeping

    # Animation durations
    BLINK_DURATION: float = 0.15
    BLINK_INTERVAL_MIN: float = 2.0
    BLINK_INTERVAL_MAX: float = 6.0

    BREATHING_CYCLE: float = 2.5  # Full inhale/exhale cycle
    IDLE_FIDGET_INTERVAL: float = 8.0
    YAWN_DURATION: float = 1.5

    # Reaction animation durations
    CLICK_REACTION: float = 0.5
    DOUBLE_CLICK_TRICK: float = 1.2
    FEED_ANIMATION: float = 2.0
    PLAY_ANIMATION: float = 3.0
    SLEEP_TRANSITION: float = 1.0
    WAKE_TRANSITION: float = 0.8
    LEVEL_UP_ANIMATION: float = 2.5
    EVOLUTION_ANIMATION: float = 4.0

    # Tween durations
    TWEEN_FAST: float = 0.15
    TWEEN_NORMAL: float = 0.3
    TWEEN_SLOW: float = 0.6
    TWEEN_VERY_SLOW: float = 1.0

    # Particle lifetimes
    HEART_LIFETIME: float = 1.5
    SPARKLE_LIFETIME: float = 0.8
    ZZZ_LIFETIME: float = 2.0
    CONFETTI_LIFETIME: float = 2.5

    # Auto-care timing
    AUTO_CARE_CHECK_INTERVAL: float = 5.0
    AUTO_CARE_DELAY_MIN: float = 2.0
    AUTO_CARE_DELAY_MAX: float = 5.0
    AUTO_FEED_COOLDOWN: float = 30.0
    AUTO_PLAY_COOLDOWN: float = 45.0

    # Thought bubble
    THOUGHT_BUBBLE_DURATION: float = 3.0
    THOUGHT_BUBBLE_FADE: float = 0.5

    # State transition delays
    STATE_RETURN_TO_IDLE: float = 2.0
    WALK_DURATION_MIN: float = 3.0
    WALK_DURATION_MAX: float = 8.0


@dataclass(frozen=True)
class Evolution:
    """
    Evolution system thresholds and requirements.
    """

    # Level thresholds for evolution
    BABY_TO_CHILD_LEVEL: int = 5
    CHILD_TO_TEEN_LEVEL: int = 15
    TEEN_TO_ADULT_LEVEL: int = 30

    # XP required per level (increases each level)
    BASE_XP_PER_LEVEL: int = 100
    XP_LEVEL_MULTIPLIER: float = 1.15  # Each level needs 15% more XP

    # Care style thresholds (for determining evolution path)
    HIGH_STAT_THRESHOLD: float = 70.0  # Stat considered "high"
    LOW_STAT_THRESHOLD: float = 30.0  # Stat considered "low"
    NEGLECT_THRESHOLD: float = 15.0  # Below this is neglect

    # Care tracking periods (in seconds)
    CARE_TRACKING_WINDOW: float = 3600.0  # 1 hour window for care style
    CARE_EVENT_EXPIRY: float = 86400.0  # 24 hours - events older are ignored

    # Special evolution requirements
    GOLDEN_PERFECT_DAYS: int = 7  # Days of perfect care for golden form
    GOLDEN_MIN_STAT: float = 80.0  # Min stat value for "perfect" care

    # Evolution check cooldown
    EVOLUTION_CHECK_INTERVAL: float = 60.0  # Check every minute


@dataclass(frozen=True)
class XP:
    """
    Experience point values for various actions.
    """

    # Interaction XP
    FEED: int = 5
    PLAY: int = 10
    CLICK: int = 1
    TRICK: int = 3
    SLEEP_COMPLETE: int = 5  # When waking from full sleep

    # Passive XP
    TIME_ALIVE_PER_MINUTE: int = 1

    # Bonus XP
    PERFECT_CARE_BONUS: int = 20  # Daily bonus for keeping stats high
    EVOLUTION_BONUS: int = 50  # Bonus for evolving

    # Streak bonuses
    DAILY_LOGIN_STREAK: int = 10  # Per consecutive day
    MAX_STREAK_BONUS: int = 100  # Cap on streak bonus


@dataclass(frozen=True)
class Stats:
    """
    Stat-related constants and thresholds.
    """

    # Initial values
    DEFAULT_HUNGER: float = 80.0
    DEFAULT_HAPPINESS: float = 80.0
    DEFAULT_ENERGY: float = 80.0

    # Boundaries
    MIN_STAT: float = 0.0
    MAX_STAT: float = 100.0

    # Action amounts (manual)
    FEED_AMOUNT: float = 25.0
    PLAY_HAPPINESS: float = 20.0
    PLAY_ENERGY_COST: float = 10.0
    PLAY_HUNGER_COST: float = 5.0
    PET_HAPPINESS: float = 3.0
    TRICK_HAPPINESS: float = 10.0
    TRICK_ENERGY_COST: float = 5.0

    # Auto-care amounts (less than manual)
    AUTO_FEED_AMOUNT: float = 15.0
    AUTO_PLAY_AMOUNT: float = 12.0

    # Thresholds for behavior/mood
    HUNGRY_THRESHOLD: float = 30.0
    TIRED_THRESHOLD: float = 30.0
    SAD_THRESHOLD: float = 30.0

    # Auto-care thresholds
    AUTO_HUNGER_THRESHOLD: float = 30.0
    AUTO_ENERGY_THRESHOLD: float = 20.0
    AUTO_HAPPINESS_THRESHOLD: float = 25.0
    AUTO_SLEEP_WAKE_THRESHOLD: float = 80.0

    # Threshold variance for natural behavior
    THRESHOLD_VARIANCE: float = 5.0

    # Mood thresholds (based on stat average)
    MOOD_ECSTATIC: float = 90.0
    MOOD_HAPPY: float = 70.0
    MOOD_CONTENT: float = 50.0
    MOOD_NEUTRAL: float = 30.0
    MOOD_SAD: float = 15.0
    # Below SAD is MISERABLE


# Sprite sizing constants
@dataclass(frozen=True)
class Sprites:
    """
    Sprite and rendering constants.
    """

    # Base pet sizes (relative units, scaled by window)
    EGG_SCALE: float = 0.7
    BABY_SCALE: float = 0.6
    CHILD_SCALE: float = 0.8
    TEEN_SCALE: float = 0.9
    ADULT_SCALE: float = 1.0

    # Feature proportions (relative to body)
    EYE_SIZE_RATIO: float = 0.15
    EYE_SPACING_RATIO: float = 0.25
    MOUTH_WIDTH_RATIO: float = 0.3
    BLUSH_SIZE_RATIO: float = 0.1

    # Baby stage has larger eyes
    BABY_EYE_MULTIPLIER: float = 1.5

    # Shadow properties
    SHADOW_OPACITY: float = 0.2
    SHADOW_OFFSET_Y: float = 0.1
    SHADOW_SCALE_X: float = 0.8
    SHADOW_SCALE_Y: float = 0.3

    # Outline thickness (pixels)
    OUTLINE_WIDTH: int = 2


# Convenience function to get color tuple from hex
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color string to RGB tuple.

    Args:
        hex_color: Color in "#RRGGBB" format.

    Returns:
        Tuple of (red, green, blue) values 0-255.
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> Tuple[int, int, int, int]:
    """
    Convert hex color string to RGBA tuple.

    Args:
        hex_color: Color in "#RRGGBB" format.
        alpha: Alpha value 0.0-1.0.

    Returns:
        Tuple of (red, green, blue, alpha) values 0-255.
    """
    r, g, b = hex_to_rgb(hex_color)
    return (r, g, b, int(alpha * 255))
