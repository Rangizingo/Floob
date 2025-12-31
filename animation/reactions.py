"""
Reaction Animations for Floob 2.0.

Defines animation responses to user interactions:
- Click reactions
- Double-click tricks
- Drag effects
- Feeding reactions
- Play reactions
- Sleep/wake transitions
- Level up celebrations
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Callable

from animation.engine import (
    Animation,
    AnimationSet,
    Keyframe,
    EasingType,
    create_shake_animation,
)


class ReactionType(Enum):
    """Types of user interaction reactions."""
    CLICK = auto()           # Single click on pet
    DOUBLE_CLICK = auto()    # Double click (trick)
    DRAG_START = auto()      # Start dragging
    DRAG_MOVE = auto()       # During drag
    DRAG_END = auto()        # Released from drag
    FEED = auto()            # Feeding the pet
    PLAY = auto()            # Playing with pet
    SLEEP_START = auto()     # Going to sleep
    WAKE_UP = auto()         # Waking up
    LEVEL_UP = auto()        # Gained a level
    EVOLUTION = auto()       # Evolving to new form


# ============================================================================
# CLICK REACTION
# ============================================================================

def create_click_reaction() -> AnimationSet:
    """
    Create click reaction animation.

    Jump up 10px, then happy wiggle (3 small bounces).
    Duration: ~1.0 seconds

    Returns:
        AnimationSet for click reaction
    """
    anim_set = AnimationSet(name="click_reaction", priority=20)

    # Jump up then bounce down
    anim_set.add_animation(Animation(
        property_name="position_y",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.15, value=-10.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.35, value=0.0, easing=EasingType.EASE_IN),
            Keyframe(time=0.5, value=-5.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.65, value=0.0, easing=EasingType.EASE_IN),
            Keyframe(time=0.8, value=-2.0, easing=EasingType.EASE_OUT),
            Keyframe(time=1.0, value=0.0, easing=EasingType.EASE_IN),
        ],
        loop=False,
    ))

    # Squash/stretch with bounces
    anim_set.add_animation(Animation(
        property_name="scale_y",
        keyframes=[
            Keyframe(time=0.0, value=0.9, easing=EasingType.LINEAR),  # Initial squash
            Keyframe(time=0.15, value=1.1, easing=EasingType.EASE_OUT),  # Stretch on jump
            Keyframe(time=0.35, value=0.92, easing=EasingType.EASE_IN),  # Squash on land
            Keyframe(time=0.5, value=1.05, easing=EasingType.EASE_OUT),
            Keyframe(time=0.65, value=0.95, easing=EasingType.EASE_IN),
            Keyframe(time=0.8, value=1.02, easing=EasingType.EASE_OUT),
            Keyframe(time=1.0, value=1.0, easing=EasingType.EASE_IN),
        ],
        loop=False,
    ))

    # Happy wiggle
    anim_set.add_animation(Animation(
        property_name="rotation",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.4, value=5.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.55, value=-5.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=0.7, value=3.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=0.85, value=-2.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.0, value=0.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    # Happy eyes
    anim_set.add_animation(Animation(
        property_name="eye_openness",
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.15, value=0.7, easing=EasingType.EASE_OUT),  # Squint on jump
            Keyframe(time=0.5, value=1.0, easing=EasingType.EASE_OUT),
            Keyframe(time=1.0, value=1.0, easing=EasingType.LINEAR),
        ],
        loop=False,
    ))

    return anim_set


# ============================================================================
# DOUBLE-CLICK TRICK (SPIN)
# ============================================================================

def create_double_click_trick() -> AnimationSet:
    """
    Create double-click trick animation.

    360 degree spin with scale pulse. Triggers sparkles.
    Duration: ~1.5 seconds

    Returns:
        AnimationSet for double-click trick
    """
    anim_set = AnimationSet(name="trick_spin", priority=25)

    # Full 360 spin
    anim_set.add_animation(Animation(
        property_name="rotation",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.2, value=-10.0, easing=EasingType.EASE_IN),  # Wind up
            Keyframe(time=1.0, value=360.0, easing=EasingType.EASE_OUT),  # Spin
            Keyframe(time=1.5, value=360.0, easing=EasingType.LINEAR),   # Settle
        ],
        loop=False,
    ))

    # Jump during spin
    anim_set.add_animation(Animation(
        property_name="position_y",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.2, value=3.0, easing=EasingType.EASE_OUT),  # Crouch
            Keyframe(time=0.5, value=-15.0, easing=EasingType.EASE_OUT),  # Jump
            Keyframe(time=1.0, value=-5.0, easing=EasingType.EASE_IN),
            Keyframe(time=1.3, value=0.0, easing=EasingType.BOUNCE),
            Keyframe(time=1.5, value=0.0, easing=EasingType.LINEAR),
        ],
        loop=False,
    ))

    # Scale pulse at peak
    anim_set.add_animation(Animation(
        property_name="scale_x",
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.2, value=1.1, easing=EasingType.EASE_OUT),  # Squash before jump
            Keyframe(time=0.5, value=0.9, easing=EasingType.EASE_OUT),  # Narrow during spin
            Keyframe(time=1.0, value=1.15, easing=EasingType.EASE_OUT),  # Burst
            Keyframe(time=1.3, value=1.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.5, value=1.0, easing=EasingType.LINEAR),
        ],
        loop=False,
    ))

    anim_set.add_animation(Animation(
        property_name="scale_y",
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.2, value=0.9, easing=EasingType.EASE_OUT),  # Squash before jump
            Keyframe(time=0.5, value=1.1, easing=EasingType.EASE_OUT),  # Stretch during spin
            Keyframe(time=1.0, value=1.15, easing=EasingType.EASE_OUT),  # Burst
            Keyframe(time=1.3, value=1.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.5, value=1.0, easing=EasingType.LINEAR),
        ],
        loop=False,
    ))

    # Glow at peak
    anim_set.add_animation(Animation(
        property_name="glow_intensity",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.5, value=0.5, easing=EasingType.EASE_IN),
            Keyframe(time=0.8, value=1.0, easing=EasingType.EASE_OUT),  # Peak glow
            Keyframe(time=1.2, value=0.3, easing=EasingType.EASE_IN),
            Keyframe(time=1.5, value=0.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    return anim_set


# ============================================================================
# DRAG SQUISH
# ============================================================================

def create_drag_squish(direction_x: float = 1.0) -> AnimationSet:
    """
    Create drag squish animation.

    Squash in movement direction (0.8), stretch perpendicular (1.2).
    This is applied continuously during drag.

    Args:
        direction_x: Horizontal drag direction (-1 left, 1 right)

    Returns:
        AnimationSet for drag squish
    """
    anim_set = AnimationSet(name="drag_squish", priority=30)

    # Squash in X (drag direction)
    anim_set.add_animation(Animation(
        property_name="scale_x",
        keyframes=[
            Keyframe(time=0.0, value=0.85, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    # Stretch in Y (perpendicular)
    anim_set.add_animation(Animation(
        property_name="scale_y",
        keyframes=[
            Keyframe(time=0.0, value=1.15, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    # Tilt in drag direction
    rotation = -15.0 if direction_x > 0 else 15.0
    anim_set.add_animation(Animation(
        property_name="rotation",
        keyframes=[
            Keyframe(time=0.0, value=rotation, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    # Worried eyes
    anim_set.add_animation(Animation(
        property_name="eye_openness",
        keyframes=[
            Keyframe(time=0.0, value=1.2, easing=EasingType.LINEAR),  # Wide surprised eyes
        ],
        loop=True,
    ))

    return anim_set


def create_drag_release() -> AnimationSet:
    """
    Create animation for releasing from drag.

    Bounce back to normal with elastic effect.

    Returns:
        AnimationSet for drag release
    """
    anim_set = AnimationSet(name="drag_release", priority=25)

    # Bounce back to normal scale
    anim_set.add_animation(Animation(
        property_name="scale_x",
        keyframes=[
            Keyframe(time=0.0, value=0.85, easing=EasingType.LINEAR),
            Keyframe(time=0.15, value=1.1, easing=EasingType.EASE_OUT),
            Keyframe(time=0.3, value=0.95, easing=EasingType.ELASTIC),
            Keyframe(time=0.5, value=1.0, easing=EasingType.ELASTIC),
        ],
        loop=False,
    ))

    anim_set.add_animation(Animation(
        property_name="scale_y",
        keyframes=[
            Keyframe(time=0.0, value=1.15, easing=EasingType.LINEAR),
            Keyframe(time=0.15, value=0.9, easing=EasingType.EASE_OUT),
            Keyframe(time=0.3, value=1.05, easing=EasingType.ELASTIC),
            Keyframe(time=0.5, value=1.0, easing=EasingType.ELASTIC),
        ],
        loop=False,
    ))

    # Rotation back to center
    anim_set.add_animation(Animation(
        property_name="rotation",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),  # Will be set dynamically
            Keyframe(time=0.3, value=0.0, easing=EasingType.ELASTIC),
        ],
        loop=False,
    ))

    return anim_set


# ============================================================================
# FEED REACTION
# ============================================================================

def create_feed_reaction() -> AnimationSet:
    """
    Create feeding reaction animation.

    Eyes widen, lean forward, single excited chomp.
    Duration: ~0.8 seconds (intro only, eating sequence follows)

    Returns:
        AnimationSet for feed reaction intro
    """
    anim_set = AnimationSet(name="feed_reaction", priority=20)

    # Eyes widen with excitement
    anim_set.add_animation(Animation(
        property_name="eye_openness",
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.15, value=1.3, easing=EasingType.EASE_OUT),  # Wide!
            Keyframe(time=0.5, value=1.2, easing=EasingType.LINEAR),
            Keyframe(time=0.8, value=1.0, easing=EasingType.EASE_IN),
        ],
        loop=False,
    ))

    # Lean forward (negative Y = up, so we tilt forward)
    anim_set.add_animation(Animation(
        property_name="position_y",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.3, value=-5.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.6, value=-3.0, easing=EasingType.LINEAR),
            Keyframe(time=0.8, value=0.0, easing=EasingType.EASE_IN),
        ],
        loop=False,
    ))

    # Slight forward tilt
    anim_set.add_animation(Animation(
        property_name="rotation",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.3, value=5.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.8, value=0.0, easing=EasingType.EASE_IN),
        ],
        loop=False,
    ))

    # Excited anticipation stretch
    anim_set.add_animation(Animation(
        property_name="scale_y",
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.2, value=1.05, easing=EasingType.EASE_OUT),
            Keyframe(time=0.8, value=1.0, easing=EasingType.EASE_IN),
        ],
        loop=False,
    ))

    return anim_set


# ============================================================================
# PLAY REACTION
# ============================================================================

def create_play_reaction() -> AnimationSet:
    """
    Create play reaction animation.

    Excited bounce, zoom left/right, return to center.
    Duration: ~2.0 seconds

    Returns:
        AnimationSet for play reaction
    """
    anim_set = AnimationSet(name="play_reaction", priority=20)

    # Zoom left and right
    anim_set.add_animation(Animation(
        property_name="position_x",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.3, value=-30.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.6, value=30.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=0.9, value=-20.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.2, value=15.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.5, value=-5.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=2.0, value=0.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    # Bouncing while moving
    anim_set.add_animation(Animation(
        property_name="position_y",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.15, value=-12.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.3, value=0.0, easing=EasingType.EASE_IN),
            Keyframe(time=0.45, value=-10.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.6, value=0.0, easing=EasingType.EASE_IN),
            Keyframe(time=0.75, value=-8.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.9, value=0.0, easing=EasingType.EASE_IN),
            Keyframe(time=1.1, value=-5.0, easing=EasingType.EASE_OUT),
            Keyframe(time=1.3, value=0.0, easing=EasingType.EASE_IN),
            Keyframe(time=1.6, value=-3.0, easing=EasingType.EASE_OUT),
            Keyframe(time=2.0, value=0.0, easing=EasingType.EASE_IN),
        ],
        loop=False,
    ))

    # Energetic rotation
    anim_set.add_animation(Animation(
        property_name="rotation",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.3, value=-15.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.6, value=15.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=0.9, value=-10.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.2, value=8.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.5, value=-3.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=2.0, value=0.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    # Scale bursts
    anim_set.add_animation(Animation(
        property_name="scale_y",
        keyframes=[
            Keyframe(time=0.0, value=0.9, easing=EasingType.LINEAR),
            Keyframe(time=0.15, value=1.1, easing=EasingType.EASE_OUT),
            Keyframe(time=0.3, value=0.92, easing=EasingType.EASE_IN),
            Keyframe(time=0.45, value=1.08, easing=EasingType.EASE_OUT),
            Keyframe(time=0.6, value=0.94, easing=EasingType.EASE_IN),
            Keyframe(time=1.0, value=1.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=2.0, value=1.0, easing=EasingType.LINEAR),
        ],
        loop=False,
    ))

    return anim_set


# ============================================================================
# SLEEP TRANSITION
# ============================================================================

def create_sleep_transition() -> AnimationSet:
    """
    Create sleep transition animation.

    Slow droop (scale_y to 0.9), settle down.
    Duration: ~1.5 seconds

    Returns:
        AnimationSet for sleep transition
    """
    anim_set = AnimationSet(name="sleep_transition", priority=20)

    # Slow vertical droop
    anim_set.add_animation(Animation(
        property_name="scale_y",
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.5, value=0.98, easing=EasingType.EASE_IN),
            Keyframe(time=1.0, value=0.92, easing=EasingType.EASE_IN),
            Keyframe(time=1.5, value=0.9, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    # Settle down
    anim_set.add_animation(Animation(
        property_name="position_y",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.8, value=2.0, easing=EasingType.EASE_IN),
            Keyframe(time=1.5, value=5.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    # Eyes slowly close
    anim_set.add_animation(Animation(
        property_name="eye_openness",
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.3, value=0.7, easing=EasingType.EASE_IN),
            Keyframe(time=0.6, value=0.4, easing=EasingType.EASE_IN),
            Keyframe(time=1.0, value=0.1, easing=EasingType.EASE_IN),
            Keyframe(time=1.5, value=0.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    # Slight head droop
    anim_set.add_animation(Animation(
        property_name="rotation",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=1.0, value=3.0, easing=EasingType.EASE_IN),
            Keyframe(time=1.5, value=5.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    return anim_set


# ============================================================================
# WAKE TRANSITION
# ============================================================================

def create_wake_transition() -> AnimationSet:
    """
    Create wake transition animation.

    Stretch (scale_y to 1.1), shake off, normalize.
    Duration: ~1.2 seconds

    Returns:
        AnimationSet for wake transition
    """
    anim_set = AnimationSet(name="wake_transition", priority=20)

    # Big stretch then normalize
    anim_set.add_animation(Animation(
        property_name="scale_y",
        keyframes=[
            Keyframe(time=0.0, value=0.9, easing=EasingType.LINEAR),
            Keyframe(time=0.4, value=1.15, easing=EasingType.EASE_OUT),  # Big stretch
            Keyframe(time=0.7, value=1.0, easing=EasingType.EASE_IN),
            Keyframe(time=0.9, value=1.05, easing=EasingType.EASE_OUT),
            Keyframe(time=1.2, value=1.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=False,
    ))

    # Rise up
    anim_set.add_animation(Animation(
        property_name="position_y",
        keyframes=[
            Keyframe(time=0.0, value=5.0, easing=EasingType.LINEAR),
            Keyframe(time=0.4, value=-3.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.7, value=0.0, easing=EasingType.EASE_IN),
            Keyframe(time=1.2, value=0.0, easing=EasingType.LINEAR),
        ],
        loop=False,
    ))

    # Eyes open
    anim_set.add_animation(Animation(
        property_name="eye_openness",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.2, value=0.3, easing=EasingType.EASE_OUT),
            Keyframe(time=0.4, value=0.8, easing=EasingType.EASE_OUT),
            Keyframe(time=0.7, value=1.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.2, value=1.0, easing=EasingType.LINEAR),
        ],
        loop=False,
    ))

    # Shake off
    anim_set.add_animation(Animation(
        property_name="rotation",
        keyframes=[
            Keyframe(time=0.0, value=5.0, easing=EasingType.LINEAR),
            Keyframe(time=0.4, value=-5.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.55, value=8.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=0.7, value=-6.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=0.85, value=4.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.0, value=-2.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.2, value=0.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    return anim_set


# ============================================================================
# LEVEL UP CELEBRATION
# ============================================================================

def create_level_up_animation() -> AnimationSet:
    """
    Create level up celebration animation.

    Glow pulse, shake, scale burst to 1.3 then back.
    Duration: ~2.0 seconds

    Returns:
        AnimationSet for level up celebration
    """
    anim_set = AnimationSet(name="level_up", priority=30)

    # Glow pulse
    anim_set.add_animation(Animation(
        property_name="glow_intensity",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.3, value=0.5, easing=EasingType.EASE_IN),
            Keyframe(time=0.6, value=1.0, easing=EasingType.EASE_OUT),
            Keyframe(time=1.0, value=0.8, easing=EasingType.LINEAR),
            Keyframe(time=1.5, value=0.3, easing=EasingType.EASE_IN),
            Keyframe(time=2.0, value=0.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    # Shake during buildup
    anim_set.add_animation(Animation(
        property_name="position_x",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.1, value=3.0, easing=EasingType.EASE_OUT),
            Keyframe(time=0.2, value=-3.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=0.3, value=4.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=0.4, value=-4.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=0.5, value=5.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=0.6, value=0.0, easing=EasingType.EASE_OUT),
            Keyframe(time=2.0, value=0.0, easing=EasingType.LINEAR),
        ],
        loop=False,
    ))

    # Scale burst
    anim_set.add_animation(Animation(
        property_name="scale_x",
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.5, value=0.95, easing=EasingType.EASE_IN),  # Compress before burst
            Keyframe(time=0.6, value=1.3, easing=EasingType.EASE_OUT),  # BURST!
            Keyframe(time=0.9, value=1.0, easing=EasingType.ELASTIC),
            Keyframe(time=1.2, value=1.05, easing=EasingType.EASE_OUT),
            Keyframe(time=2.0, value=1.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=False,
    ))

    anim_set.add_animation(Animation(
        property_name="scale_y",
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.5, value=0.95, easing=EasingType.EASE_IN),
            Keyframe(time=0.6, value=1.3, easing=EasingType.EASE_OUT),
            Keyframe(time=0.9, value=1.0, easing=EasingType.ELASTIC),
            Keyframe(time=1.2, value=1.05, easing=EasingType.EASE_OUT),
            Keyframe(time=2.0, value=1.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=False,
    ))

    # Jump at burst
    anim_set.add_animation(Animation(
        property_name="position_y",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.5, value=3.0, easing=EasingType.EASE_IN),  # Crouch
            Keyframe(time=0.7, value=-20.0, easing=EasingType.EASE_OUT),  # Jump!
            Keyframe(time=1.1, value=0.0, easing=EasingType.BOUNCE),
            Keyframe(time=2.0, value=0.0, easing=EasingType.LINEAR),
        ],
        loop=False,
    ))

    # Celebration spin
    anim_set.add_animation(Animation(
        property_name="rotation",
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.6, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=1.0, value=720.0, easing=EasingType.EASE_OUT),  # Double spin!
            Keyframe(time=1.5, value=720.0, easing=EasingType.LINEAR),
            Keyframe(time=2.0, value=720.0, easing=EasingType.LINEAR),
        ],
        loop=False,
    ))

    return anim_set


# ============================================================================
# REACTION ANIMATIONS REGISTRY
# ============================================================================

REACTION_ANIMATIONS: dict[ReactionType, Callable[[], AnimationSet]] = {
    ReactionType.CLICK: create_click_reaction,
    ReactionType.DOUBLE_CLICK: create_double_click_trick,
    ReactionType.DRAG_END: create_drag_release,
    ReactionType.FEED: create_feed_reaction,
    ReactionType.PLAY: create_play_reaction,
    ReactionType.SLEEP_START: create_sleep_transition,
    ReactionType.WAKE_UP: create_wake_transition,
    ReactionType.LEVEL_UP: create_level_up_animation,
}


def get_reaction_animation(reaction_type: ReactionType) -> Optional[AnimationSet]:
    """
    Get an animation set for a reaction type.

    Args:
        reaction_type: The type of reaction

    Returns:
        AnimationSet for the reaction, or None if not defined
    """
    factory = REACTION_ANIMATIONS.get(reaction_type)
    if factory:
        return factory()
    return None


def get_drag_squish_animation(direction_x: float) -> AnimationSet:
    """
    Get drag squish animation with specific direction.

    Args:
        direction_x: Horizontal drag direction (-1 to 1)

    Returns:
        AnimationSet configured for drag direction
    """
    return create_drag_squish(direction_x)
