"""
Animation State Definitions for Floob 2.0.

Defines the animatable properties and states for the pet animation system.
Includes:
- AnimationProperty enum for all animatable properties
- AnimationState enum for behavioral states
- Base animation parameters for each state
- Idle animation definitions (breathing, blinking, etc.)
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
import random

from animation.engine import (
    Animation,
    AnimationSet,
    Keyframe,
    EasingType,
    create_pulse_animation,
    create_simple_animation,
)


class AnimationProperty(Enum):
    """
    Enumeration of all animatable properties.

    These properties can be animated by the animation engine
    and are used by the renderer to draw the pet.
    """
    # Position (aliases for compatibility)
    POSITION_X = "position_x"
    POSITION_Y = "position_y"
    OFFSET_X = "position_x"   # Alias for POSITION_X
    OFFSET_Y = "position_y"   # Alias for POSITION_Y

    # Scale (for squash and stretch effects)
    SCALE_X = "scale_x"
    SCALE_Y = "scale_y"

    # Body deformation (multipliers, 1.0 = normal)
    SQUASH = "squash"                   # Vertical compression (0.5 = half height)
    STRETCH = "stretch"                 # Horizontal stretch
    BODY_SQUASH = "body_squash"         # Legacy alias for SQUASH
    BODY_STRETCH = "body_stretch"       # Legacy alias for STRETCH

    # Rotation (in degrees)
    ROTATION = "rotation"

    # Facial expressions (0.0 to 1.0)
    EYE_OPENNESS = "eye_openness"       # 0 = closed, 1 = fully open
    MOUTH_OPENNESS = "mouth_openness"   # 0 = closed, 1 = wide open
    MOUTH_CURVE = "mouth_curve"         # -1 = sad, 0 = neutral, 1 = happy

    # Eye movement (offset from center, -1 to 1)
    EYE_LOOK_X = "eye_look_x"           # Alias: EYE_OFFSET_X
    EYE_LOOK_Y = "eye_look_y"           # Alias: EYE_OFFSET_Y
    EYE_OFFSET_X = "eye_look_x"         # Alias for EYE_LOOK_X
    EYE_OFFSET_Y = "eye_look_y"         # Alias for EYE_LOOK_Y

    # Animation cycle phase (0.0 to 1.0)
    LIMB_PHASE = "limb_phase"           # Phase for walk cycle, etc.

    # Visual effects
    OPACITY = "opacity"                 # 0 = transparent, 1 = opaque
    GLOW_INTENSITY = "glow_intensity"   # 0 = no glow, 1 = full glow
    BLUSH = "blush"                     # Blush intensity (0 to 1)
    BLUSH_OPACITY = "blush"             # Alias for BLUSH


class AnimationState(Enum):
    """
    Behavioral animation states for the pet.

    Each state has associated base animations and can trigger
    specific particle effects.
    """
    IDLE = auto()
    WALKING = auto()
    EATING = auto()
    PLAYING = auto()
    SLEEPING = auto()
    HAPPY = auto()
    SAD = auto()
    TIRED = auto()
    EXCITED = auto()
    SCARED = auto()
    TRICK = auto()
    EVOLVING = auto()
    LEVEL_UP = auto()


@dataclass
class AnimationStateConfig:
    """
    Configuration for an animation state.

    Defines the base animations, particle effects, and
    transition parameters for a behavioral state.

    Attributes:
        state: The animation state this config is for
        base_animations: Animation sets that loop while in this state
        enter_animation: Optional animation to play on state entry
        exit_animation: Optional animation to play on state exit
        allow_idle_variations: Whether to add random idle behaviors
        particle_types: Particle effects to spawn in this state
    """
    state: AnimationState
    base_animations: list[AnimationSet] = field(default_factory=list)
    enter_animation: Optional[AnimationSet] = None
    exit_animation: Optional[AnimationSet] = None
    allow_idle_variations: bool = True
    particle_types: list[str] = field(default_factory=list)


# ============================================================================
# IDLE ANIMATIONS
# ============================================================================

def create_breathing_animation() -> AnimationSet:
    """
    Create a gentle breathing animation.

    Subtle scale pulse that makes the pet look alive even when idle.
    Cycles over 2 seconds with slight vertical expansion.

    Returns:
        AnimationSet with breathing scale animation
    """
    anim_set = AnimationSet(name="breathing", priority=0)

    # Gentle vertical scale (0.98 to 1.02)
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.SCALE_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=1.0, value=1.02, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=2.0, value=1.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    # Slight horizontal compression during inhale
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.SCALE_X.value,
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=1.0, value=0.99, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=2.0, value=1.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    return anim_set


def create_blinking_animation(blink_duration: float = 0.15) -> AnimationSet:
    """
    Create a quick blink animation.

    Fast close and open of eyes. This is NOT looping - it should be
    triggered randomly by the animation controller.

    Args:
        blink_duration: Total duration of the blink (close + open)

    Returns:
        AnimationSet with blinking eye animation
    """
    anim_set = AnimationSet(name="blink", priority=10)

    half = blink_duration / 2.0

    anim_set.add_animation(Animation(
        property_name=AnimationProperty.EYE_OPENNESS.value,
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=half, value=0.0, easing=EasingType.EASE_IN),
            Keyframe(time=blink_duration, value=1.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    return anim_set


def create_looking_around_animation() -> AnimationSet:
    """
    Create a looking around animation.

    Eyes shift position and slight head rotation to simulate
    the pet looking at different things in its environment.

    Returns:
        AnimationSet with eye movement and rotation
    """
    anim_set = AnimationSet(name="look_around", priority=5)

    # Random-ish eye movement pattern (3 second cycle)
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.EYE_LOOK_X.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.8, value=0.5, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.5, value=0.3, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=2.2, value=-0.4, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=3.0, value=0.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    anim_set.add_animation(Animation(
        property_name=AnimationProperty.EYE_LOOK_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.6, value=-0.2, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=1.2, value=0.3, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=2.0, value=-0.1, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=3.0, value=0.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    # Slight head tilt
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.ROTATION.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=1.0, value=3.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=2.0, value=-2.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=3.0, value=0.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    return anim_set


def create_fidgeting_animation() -> AnimationSet:
    """
    Create a small fidgeting animation.

    Small random position offsets to make the pet seem restless
    or curious. Very subtle movement.

    Returns:
        AnimationSet with small position shifts
    """
    anim_set = AnimationSet(name="fidget", priority=1)

    # Small horizontal shifts (4 second cycle)
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.POSITION_X.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=1.0, value=2.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=2.0, value=-1.5, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=3.0, value=1.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=4.0, value=0.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    return anim_set


def create_yawning_animation() -> AnimationSet:
    """
    Create a yawning animation.

    Mouth opens wide, eyes squint, slight body stretch.
    Plays once when triggered (not looping).

    Returns:
        AnimationSet with yawning animation
    """
    anim_set = AnimationSet(name="yawn", priority=15)

    duration = 2.0

    # Mouth opens wide
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.MOUTH_OPENNESS.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.3, value=0.3, easing=EasingType.EASE_IN),
            Keyframe(time=0.6, value=1.0, easing=EasingType.EASE_OUT),  # Wide open
            Keyframe(time=1.4, value=0.9, easing=EasingType.LINEAR),     # Hold
            Keyframe(time=1.8, value=0.2, easing=EasingType.EASE_IN),
            Keyframe(time=duration, value=0.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    # Eyes squint during peak
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.EYE_OPENNESS.value,
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.5, value=0.3, easing=EasingType.EASE_IN),
            Keyframe(time=1.5, value=0.2, easing=EasingType.LINEAR),
            Keyframe(time=1.8, value=0.5, easing=EasingType.EASE_OUT),
            Keyframe(time=duration, value=1.0, easing=EasingType.EASE_OUT),
        ],
        loop=False,
    ))

    # Body stretches vertically
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.SCALE_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=1.0, easing=EasingType.LINEAR),
            Keyframe(time=0.6, value=1.08, easing=EasingType.EASE_OUT),
            Keyframe(time=1.4, value=1.06, easing=EasingType.LINEAR),
            Keyframe(time=duration, value=1.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=False,
    ))

    # Slight head tilt back
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.ROTATION.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=0.6, value=-5.0, easing=EasingType.EASE_OUT),
            Keyframe(time=1.4, value=-4.0, easing=EasingType.LINEAR),
            Keyframe(time=duration, value=0.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=False,
    ))

    return anim_set


# ============================================================================
# IDLE ANIMATIONS COLLECTION
# ============================================================================

IDLE_ANIMATIONS = {
    "breathing": create_breathing_animation,
    "blink": create_blinking_animation,
    "look_around": create_looking_around_animation,
    "fidget": create_fidgeting_animation,
    "yawn": create_yawning_animation,
}


# ============================================================================
# STATE ANIMATION CONFIGURATIONS
# ============================================================================

def create_walking_animation() -> AnimationSet:
    """Create walking animation with bounce and limb phase."""
    anim_set = AnimationSet(name="walking", priority=5)

    # Walking bounce (0.4 second cycle for energetic walk)
    cycle = 0.4

    anim_set.add_animation(Animation(
        property_name=AnimationProperty.POSITION_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=cycle * 0.25, value=-3.0, easing=EasingType.EASE_OUT),
            Keyframe(time=cycle * 0.5, value=0.0, easing=EasingType.EASE_IN),
            Keyframe(time=cycle * 0.75, value=-3.0, easing=EasingType.EASE_OUT),
            Keyframe(time=cycle, value=0.0, easing=EasingType.EASE_IN),
        ],
        loop=True,
    ))

    # Limb phase for walk cycle
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.LIMB_PHASE.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=cycle, value=1.0, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    # Slight rotation wobble
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.ROTATION.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=cycle * 0.25, value=2.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=cycle * 0.5, value=0.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=cycle * 0.75, value=-2.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=cycle, value=0.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    return anim_set


def create_sleeping_animation() -> AnimationSet:
    """Create sleeping animation with slow breathing and closed eyes."""
    anim_set = AnimationSet(name="sleeping", priority=5)

    # Slow breathing (3 second cycle)
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.SCALE_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=0.95, easing=EasingType.LINEAR),
            Keyframe(time=1.5, value=1.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=3.0, value=0.95, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    # Eyes closed
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.EYE_OPENNESS.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    # Settled lower position
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.POSITION_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=5.0, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    # Squashed body (curled up)
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.BODY_SQUASH.value,
        keyframes=[
            Keyframe(time=0.0, value=0.9, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    return anim_set


def create_happy_animation() -> AnimationSet:
    """Create happy animation with bouncing and big eyes."""
    anim_set = AnimationSet(name="happy", priority=10)

    # Happy bounce (0.6 second cycle)
    cycle = 0.6

    anim_set.add_animation(Animation(
        property_name=AnimationProperty.POSITION_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=cycle * 0.3, value=-8.0, easing=EasingType.EASE_OUT),
            Keyframe(time=cycle * 0.6, value=0.0, easing=EasingType.EASE_IN),
            Keyframe(time=cycle, value=0.0, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    # Squash and stretch
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.SCALE_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=0.95, easing=EasingType.LINEAR),  # Squash before jump
            Keyframe(time=cycle * 0.15, value=1.1, easing=EasingType.EASE_OUT),  # Stretch during jump
            Keyframe(time=cycle * 0.3, value=1.05, easing=EasingType.LINEAR),
            Keyframe(time=cycle * 0.6, value=0.92, easing=EasingType.EASE_IN),  # Squash on land
            Keyframe(time=cycle * 0.8, value=1.0, easing=EasingType.EASE_OUT),
            Keyframe(time=cycle, value=0.95, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    anim_set.add_animation(Animation(
        property_name=AnimationProperty.SCALE_X.value,
        keyframes=[
            Keyframe(time=0.0, value=1.05, easing=EasingType.LINEAR),  # Wide before jump
            Keyframe(time=cycle * 0.15, value=0.95, easing=EasingType.EASE_OUT),  # Narrow during jump
            Keyframe(time=cycle * 0.3, value=0.97, easing=EasingType.LINEAR),
            Keyframe(time=cycle * 0.6, value=1.08, easing=EasingType.EASE_IN),  # Wide on land
            Keyframe(time=cycle * 0.8, value=1.0, easing=EasingType.EASE_OUT),
            Keyframe(time=cycle, value=1.05, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    # Happy eyes (curved up)
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.EYE_OPENNESS.value,
        keyframes=[
            Keyframe(time=0.0, value=0.8, easing=EasingType.LINEAR),  # Happy squint
        ],
        loop=True,
    ))

    # Slight blush
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.BLUSH.value,
        keyframes=[
            Keyframe(time=0.0, value=0.5, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    return anim_set


def create_sad_animation() -> AnimationSet:
    """Create sad animation with droopy posture."""
    anim_set = AnimationSet(name="sad", priority=10)

    # Droopy position
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.POSITION_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=3.0, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    # Slow, heavy breathing
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.SCALE_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=0.95, easing=EasingType.LINEAR),
            Keyframe(time=2.0, value=0.98, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=4.0, value=0.95, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    # Droopy eyes
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.EYE_OPENNESS.value,
        keyframes=[
            Keyframe(time=0.0, value=0.5, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    # Looking down
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.EYE_LOOK_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=0.3, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    return anim_set


def create_tired_animation() -> AnimationSet:
    """Create tired animation with droopy eyes and slow movement."""
    anim_set = AnimationSet(name="tired", priority=8)

    # Heavy, slow breathing
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.SCALE_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=0.96, easing=EasingType.LINEAR),
            Keyframe(time=1.5, value=1.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=3.0, value=0.96, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    # Droopy eyelids (half closed)
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.EYE_OPENNESS.value,
        keyframes=[
            Keyframe(time=0.0, value=0.4, easing=EasingType.LINEAR),
            Keyframe(time=2.0, value=0.3, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=4.0, value=0.4, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    # Slight slump
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.POSITION_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=2.0, easing=EasingType.LINEAR),
        ],
        loop=True,
    ))

    return anim_set


def create_excited_animation() -> AnimationSet:
    """Create excited animation with rapid bouncing."""
    anim_set = AnimationSet(name="excited", priority=12)

    # Fast bouncing (0.3 second cycle)
    cycle = 0.3

    anim_set.add_animation(Animation(
        property_name=AnimationProperty.POSITION_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=0.0, easing=EasingType.LINEAR),
            Keyframe(time=cycle * 0.4, value=-10.0, easing=EasingType.EASE_OUT),
            Keyframe(time=cycle, value=0.0, easing=EasingType.BOUNCE),
        ],
        loop=True,
    ))

    # Rapid scale changes
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.SCALE_Y.value,
        keyframes=[
            Keyframe(time=0.0, value=0.9, easing=EasingType.LINEAR),
            Keyframe(time=cycle * 0.2, value=1.15, easing=EasingType.EASE_OUT),
            Keyframe(time=cycle * 0.4, value=1.05, easing=EasingType.LINEAR),
            Keyframe(time=cycle * 0.7, value=0.85, easing=EasingType.EASE_IN),
            Keyframe(time=cycle, value=0.9, easing=EasingType.EASE_OUT),
        ],
        loop=True,
    ))

    # Wiggle rotation
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.ROTATION.value,
        keyframes=[
            Keyframe(time=0.0, value=-5.0, easing=EasingType.LINEAR),
            Keyframe(time=cycle * 0.5, value=5.0, easing=EasingType.EASE_IN_OUT),
            Keyframe(time=cycle, value=-5.0, easing=EasingType.EASE_IN_OUT),
        ],
        loop=True,
    ))

    # Wide eyes
    anim_set.add_animation(Animation(
        property_name=AnimationProperty.EYE_OPENNESS.value,
        keyframes=[
            Keyframe(time=0.0, value=1.2, easing=EasingType.LINEAR),  # Extra wide
        ],
        loop=True,
    ))

    return anim_set


# ============================================================================
# STATE CONFIGURATIONS
# ============================================================================

STATE_CONFIGS: dict[AnimationState, AnimationStateConfig] = {
    AnimationState.IDLE: AnimationStateConfig(
        state=AnimationState.IDLE,
        base_animations=[create_breathing_animation()],
        allow_idle_variations=True,
        particle_types=[],
    ),
    AnimationState.WALKING: AnimationStateConfig(
        state=AnimationState.WALKING,
        base_animations=[create_walking_animation()],
        allow_idle_variations=False,
        particle_types=["dust"],
    ),
    AnimationState.SLEEPING: AnimationStateConfig(
        state=AnimationState.SLEEPING,
        base_animations=[create_sleeping_animation()],
        allow_idle_variations=False,
        particle_types=["zzz"],
    ),
    AnimationState.HAPPY: AnimationStateConfig(
        state=AnimationState.HAPPY,
        base_animations=[create_happy_animation()],
        allow_idle_variations=False,
        particle_types=["heart"],
    ),
    AnimationState.SAD: AnimationStateConfig(
        state=AnimationState.SAD,
        base_animations=[create_sad_animation()],
        allow_idle_variations=False,
        particle_types=["sweat"],
    ),
    AnimationState.TIRED: AnimationStateConfig(
        state=AnimationState.TIRED,
        base_animations=[create_tired_animation()],
        allow_idle_variations=True,
        particle_types=[],
    ),
    AnimationState.EXCITED: AnimationStateConfig(
        state=AnimationState.EXCITED,
        base_animations=[create_excited_animation()],
        allow_idle_variations=False,
        particle_types=["sparkle", "star"],
    ),
}
