"""
Animation Engine Core for Floob 2.0.

Provides a data-driven keyframe animation system with:
- Time-based keyframe interpolation
- Multiple easing functions for natural motion
- Animation blending for smooth transitions
- Animation queue for chaining animations
- Update method for frame-by-frame advancement

This is the heart of the animation system - all animations are defined
as data (keyframes) and processed uniformly by this engine.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional, Any
import math


class EasingType(Enum):
    """Available easing function types."""
    LINEAR = auto()
    EASE_IN = auto()
    EASE_OUT = auto()
    EASE_IN_OUT = auto()
    BOUNCE = auto()
    ELASTIC = auto()


# ============================================================================
# EASING FUNCTIONS
# ============================================================================

def linear(t: float) -> float:
    """
    Linear interpolation - constant speed.

    Args:
        t: Progress value from 0.0 to 1.0

    Returns:
        Interpolated value (same as input for linear)
    """
    return max(0.0, min(1.0, t))


def ease_in(t: float) -> float:
    """
    Ease-in (quadratic) - starts slow, accelerates.

    Creates a smooth acceleration effect, good for objects
    starting to move from rest.

    Args:
        t: Progress value from 0.0 to 1.0

    Returns:
        Eased value with slow start
    """
    t = max(0.0, min(1.0, t))
    return t * t


def ease_out(t: float) -> float:
    """
    Ease-out (quadratic) - starts fast, decelerates.

    Creates a smooth deceleration effect, good for objects
    coming to rest.

    Args:
        t: Progress value from 0.0 to 1.0

    Returns:
        Eased value with slow end
    """
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_in_out(t: float) -> float:
    """
    Ease-in-out (quadratic) - slow start and end.

    Creates smooth acceleration and deceleration, good for
    natural-looking movement between two points.

    Args:
        t: Progress value from 0.0 to 1.0

    Returns:
        Eased value with slow start and end
    """
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 2.0 * t * t
    else:
        return 1.0 - ((-2.0 * t + 2.0) ** 2) / 2.0


def bounce(t: float) -> float:
    """
    Bounce easing - overshoots and settles.

    Creates a bouncy effect where the value overshoots the
    target and bounces back, like a ball settling.

    Args:
        t: Progress value from 0.0 to 1.0

    Returns:
        Eased value with bounce effect
    """
    t = max(0.0, min(1.0, t))
    if t < 1.0 / 2.75:
        return 7.5625 * t * t
    elif t < 2.0 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


def elastic(t: float) -> float:
    """
    Elastic easing - spring effect with oscillation.

    Creates a springy effect where the value oscillates
    around the target before settling, like a spring.

    Args:
        t: Progress value from 0.0 to 1.0

    Returns:
        Eased value with elastic/spring effect
    """
    t = max(0.0, min(1.0, t))
    if t == 0.0 or t == 1.0:
        return t

    # Elastic parameters
    p = 0.3  # Period
    s = p / 4.0  # Amplitude shift

    return (
        math.pow(2.0, -10.0 * t)
        * math.sin((t - s) * (2.0 * math.pi) / p)
        + 1.0
    )


# Mapping from EasingType to function
EASING_FUNCTIONS: dict[EasingType, Callable[[float], float]] = {
    EasingType.LINEAR: linear,
    EasingType.EASE_IN: ease_in,
    EasingType.EASE_OUT: ease_out,
    EasingType.EASE_IN_OUT: ease_in_out,
    EasingType.BOUNCE: bounce,
    EasingType.ELASTIC: elastic,
}


def get_easing_function(easing: EasingType) -> Callable[[float], float]:
    """
    Get the easing function for a given easing type.

    Args:
        easing: The easing type enum value

    Returns:
        The corresponding easing function
    """
    return EASING_FUNCTIONS.get(easing, linear)


# ============================================================================
# KEYFRAME AND ANIMATION DATA STRUCTURES
# ============================================================================

@dataclass
class Keyframe:
    """
    A single keyframe in an animation.

    Represents a target value at a specific time point with
    an easing function for interpolation to the next keyframe.

    Attributes:
        time: Time in seconds when this keyframe occurs
        value: Target value at this keyframe (can be any numeric type)
        easing: Easing function to use when interpolating TO this keyframe
    """
    time: float
    value: float
    easing: EasingType = EasingType.LINEAR

    def __post_init__(self) -> None:
        """Validate keyframe data."""
        if self.time < 0:
            raise ValueError("Keyframe time cannot be negative")


@dataclass
class Animation:
    """
    A complete animation track for a single property.

    Contains a sequence of keyframes that define how a property
    changes over time. The animation can loop or play once.

    Attributes:
        property_name: Name of the property being animated
        keyframes: List of keyframes in chronological order
        loop: Whether the animation should loop
        duration: Total duration (auto-calculated from keyframes)
    """
    property_name: str
    keyframes: list[Keyframe] = field(default_factory=list)
    loop: bool = False

    @property
    def duration(self) -> float:
        """Get total animation duration."""
        if not self.keyframes:
            return 0.0
        return max(kf.time for kf in self.keyframes)

    def get_value_at(self, time: float) -> float:
        """
        Get interpolated value at a specific time.

        Args:
            time: Time in seconds to sample

        Returns:
            Interpolated value at the given time
        """
        if not self.keyframes:
            return 0.0

        # Handle looping
        if self.loop and self.duration > 0:
            time = time % self.duration

        # Sort keyframes by time (should already be sorted)
        sorted_kf = sorted(self.keyframes, key=lambda kf: kf.time)

        # Before first keyframe
        if time <= sorted_kf[0].time:
            return sorted_kf[0].value

        # After last keyframe
        if time >= sorted_kf[-1].time:
            return sorted_kf[-1].value

        # Find surrounding keyframes
        for i in range(len(sorted_kf) - 1):
            kf_start = sorted_kf[i]
            kf_end = sorted_kf[i + 1]

            if kf_start.time <= time <= kf_end.time:
                # Calculate progress between keyframes
                segment_duration = kf_end.time - kf_start.time
                if segment_duration <= 0:
                    return kf_end.value

                local_t = (time - kf_start.time) / segment_duration

                # Apply easing
                easing_func = get_easing_function(kf_end.easing)
                eased_t = easing_func(local_t)

                # Interpolate
                return kf_start.value + (kf_end.value - kf_start.value) * eased_t

        return sorted_kf[-1].value

    def add_keyframe(self, time: float, value: float, easing: EasingType = EasingType.LINEAR) -> "Animation":
        """
        Add a keyframe to the animation (fluent interface).

        Args:
            time: Time in seconds for the keyframe
            value: Value at the keyframe
            easing: Easing function for interpolation to this keyframe

        Returns:
            Self for method chaining
        """
        self.keyframes.append(Keyframe(time=time, value=value, easing=easing))
        return self


@dataclass
class AnimationSet:
    """
    A collection of animations that play together.

    Groups multiple property animations that should be synchronized,
    like position_x and position_y for a movement animation.

    Attributes:
        name: Name of the animation set
        animations: Dict mapping property names to animations
        priority: Higher priority animations override lower ones
    """
    name: str
    animations: dict[str, Animation] = field(default_factory=dict)
    priority: int = 0

    @property
    def duration(self) -> float:
        """Get the longest duration among all animations."""
        if not self.animations:
            return 0.0
        return max(anim.duration for anim in self.animations.values())

    def add_animation(self, animation: Animation) -> "AnimationSet":
        """
        Add an animation to the set (fluent interface).

        Args:
            animation: Animation to add

        Returns:
            Self for method chaining
        """
        self.animations[animation.property_name] = animation
        return self

    def get_values_at(self, time: float) -> dict[str, float]:
        """
        Get all property values at a specific time.

        Args:
            time: Time in seconds to sample

        Returns:
            Dict mapping property names to interpolated values
        """
        return {
            prop: anim.get_value_at(time)
            for prop, anim in self.animations.items()
        }


# ============================================================================
# ANIMATION ENGINE
# ============================================================================

@dataclass
class QueuedAnimation:
    """An animation waiting in the queue."""
    animation_set: AnimationSet
    on_complete: Optional[Callable[[], None]] = None
    blend_time: float = 0.0  # Seconds to blend from previous animation


class AnimationEngine:
    """
    Core animation engine that manages playback of animations.

    Handles:
    - Playing animations with time-based interpolation
    - Blending between animations for smooth transitions
    - Animation queue for chaining animations
    - Layered animations with priority system
    - Callbacks for animation events

    Usage:
        engine = AnimationEngine()
        engine.play(my_animation_set, blend_time=0.2)

        # In update loop:
        values = engine.update(delta_time)
        # values is dict like {"position_x": 10.5, "scale_y": 1.02}
    """

    def __init__(self) -> None:
        """Initialize the animation engine."""
        # Currently playing animations by layer
        self._active_animations: dict[int, AnimationSet] = {}
        self._animation_times: dict[int, float] = {}
        self._animation_callbacks: dict[int, Optional[Callable[[], None]]] = {}

        # Blending state
        self._blend_from: dict[int, dict[str, float]] = {}
        self._blend_progress: dict[int, float] = {}
        self._blend_duration: dict[int, float] = {}

        # Animation queue (per layer)
        self._queues: dict[int, list[QueuedAnimation]] = {}

        # Current property values (result of all layers combined)
        self._current_values: dict[str, float] = {}

        # Default values for properties (used when no animation is playing)
        self._default_values: dict[str, float] = {
            # Position
            "position_x": 0.0,
            "position_y": 0.0,
            # Scale
            "scale_x": 1.0,
            "scale_y": 1.0,
            # Body deformation
            "squash": 1.0,
            "stretch": 1.0,
            "body_squash": 1.0,
            "body_stretch": 1.0,
            # Rotation
            "rotation": 0.0,
            # Facial expressions
            "eye_openness": 1.0,
            "mouth_openness": 0.0,
            "mouth_curve": 0.0,
            # Eye movement
            "eye_look_x": 0.0,
            "eye_look_y": 0.0,
            # Animation phase
            "limb_phase": 0.0,
            # Visual effects
            "opacity": 1.0,
            "glow_intensity": 0.0,
            "blush": 0.0,
        }

    def set_default(self, property_name: str, value: float) -> None:
        """
        Set default value for a property.

        Args:
            property_name: Name of the property
            value: Default value when no animation is playing
        """
        self._default_values[property_name] = value

    def play(
        self,
        animation_set: AnimationSet,
        layer: int = 0,
        blend_time: float = 0.0,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Start playing an animation set.

        Args:
            animation_set: The animation set to play
            layer: Animation layer (higher layers override lower)
            blend_time: Seconds to blend from current state
            on_complete: Callback when animation completes (non-looping only)
        """
        # Store current values for blending
        if blend_time > 0 and layer in self._active_animations:
            self._blend_from[layer] = self._get_layer_values(layer)
            self._blend_progress[layer] = 0.0
            self._blend_duration[layer] = blend_time
        else:
            self._blend_from.pop(layer, None)
            self._blend_progress.pop(layer, None)
            self._blend_duration.pop(layer, None)

        # Set the new animation
        self._active_animations[layer] = animation_set
        self._animation_times[layer] = 0.0
        self._animation_callbacks[layer] = on_complete

    def queue(
        self,
        animation_set: AnimationSet,
        layer: int = 0,
        blend_time: float = 0.0,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Queue an animation to play after current animation finishes.

        Args:
            animation_set: The animation set to queue
            layer: Animation layer
            blend_time: Seconds to blend from previous animation
            on_complete: Callback when animation completes
        """
        if layer not in self._queues:
            self._queues[layer] = []

        self._queues[layer].append(QueuedAnimation(
            animation_set=animation_set,
            on_complete=on_complete,
            blend_time=blend_time,
        ))

        # If nothing is playing on this layer, start the queued animation
        if layer not in self._active_animations:
            self._play_next_queued(layer)

    def stop(self, layer: int = 0, blend_time: float = 0.0) -> None:
        """
        Stop animation on a layer.

        Args:
            layer: Animation layer to stop
            blend_time: Seconds to blend to default values
        """
        if layer in self._active_animations:
            if blend_time > 0:
                self._blend_from[layer] = self._get_layer_values(layer)
                self._blend_progress[layer] = 0.0
                self._blend_duration[layer] = blend_time

            del self._active_animations[layer]
            self._animation_times.pop(layer, None)
            self._animation_callbacks.pop(layer, None)

    def stop_all(self) -> None:
        """Stop all animations on all layers."""
        self._active_animations.clear()
        self._animation_times.clear()
        self._animation_callbacks.clear()
        self._blend_from.clear()
        self._blend_progress.clear()
        self._blend_duration.clear()
        self._queues.clear()

    def is_playing(self, layer: int = 0) -> bool:
        """
        Check if an animation is playing on a layer.

        Args:
            layer: Animation layer to check

        Returns:
            True if an animation is playing
        """
        return layer in self._active_animations

    def get_value(self, property_name: str) -> float:
        """
        Get current value of a property.

        Args:
            property_name: Name of the property

        Returns:
            Current animated or default value
        """
        return self._current_values.get(
            property_name,
            self._default_values.get(property_name, 0.0)
        )

    def get_all_values(self) -> dict[str, float]:
        """
        Get all current property values.

        Returns:
            Dict mapping property names to current values
        """
        result = self._default_values.copy()
        result.update(self._current_values)
        return result

    def update(self, delta_time: float) -> dict[str, float]:
        """
        Update all animations and return current property values.

        This should be called once per frame with the time elapsed
        since the last frame.

        Args:
            delta_time: Time in seconds since last update

        Returns:
            Dict mapping property names to current animated values
        """
        completed_layers: list[int] = []

        # Update each active animation
        for layer, anim_set in list(self._active_animations.items()):
            self._animation_times[layer] = self._animation_times.get(layer, 0.0) + delta_time

            current_time = self._animation_times[layer]

            # Check for completion (non-looping animations)
            if current_time >= anim_set.duration:
                # Check if any animation in the set loops
                any_looping = any(
                    anim.loop for anim in anim_set.animations.values()
                )

                if not any_looping:
                    completed_layers.append(layer)

        # Update blend progress
        for layer in list(self._blend_progress.keys()):
            self._blend_progress[layer] += delta_time
            if self._blend_progress[layer] >= self._blend_duration.get(layer, 0.0):
                self._blend_from.pop(layer, None)
                self._blend_progress.pop(layer, None)
                self._blend_duration.pop(layer, None)

        # Handle completed animations
        for layer in completed_layers:
            callback = self._animation_callbacks.get(layer)
            self._active_animations.pop(layer, None)
            self._animation_times.pop(layer, None)
            self._animation_callbacks.pop(layer, None)

            # Play next queued animation
            self._play_next_queued(layer)

            # Fire completion callback
            if callback:
                callback()

        # Combine all layers to get final values
        self._current_values = self._combine_layers()

        return self._current_values

    def _get_layer_values(self, layer: int) -> dict[str, float]:
        """Get current values for a specific layer."""
        if layer not in self._active_animations:
            return {}

        anim_set = self._active_animations[layer]
        current_time = self._animation_times.get(layer, 0.0)

        return anim_set.get_values_at(current_time)

    def _combine_layers(self) -> dict[str, float]:
        """Combine values from all layers with blending."""
        result: dict[str, float] = {}

        # Sort layers by priority (lower first, so higher overrides)
        sorted_layers = sorted(self._active_animations.keys())

        for layer in sorted_layers:
            anim_set = self._active_animations[layer]
            current_time = self._animation_times.get(layer, 0.0)
            layer_values = anim_set.get_values_at(current_time)

            # Apply blending if active
            if layer in self._blend_from:
                blend_progress = self._blend_progress.get(layer, 0.0)
                blend_duration = self._blend_duration.get(layer, 1.0)
                blend_t = min(1.0, blend_progress / blend_duration) if blend_duration > 0 else 1.0

                # Smooth blend using ease_in_out
                blend_t = ease_in_out(blend_t)

                from_values = self._blend_from[layer]
                for prop, to_value in layer_values.items():
                    from_value = from_values.get(prop, self._default_values.get(prop, 0.0))
                    layer_values[prop] = from_value + (to_value - from_value) * blend_t

            result.update(layer_values)

        return result

    def _play_next_queued(self, layer: int) -> None:
        """Play the next queued animation on a layer."""
        if layer not in self._queues or not self._queues[layer]:
            return

        queued = self._queues[layer].pop(0)
        self.play(
            queued.animation_set,
            layer=layer,
            blend_time=queued.blend_time,
            on_complete=queued.on_complete,
        )

    def set_state(self, state: Any, blend_time: float = 0.3) -> None:
        """
        Set the animation state, playing appropriate animations.

        This method looks up the animation configuration for the given state
        and plays the associated base animations with blending.

        Args:
            state: The AnimationState enum value to switch to
            blend_time: Seconds to blend from current state (default 0.3)
        """
        # Import here to avoid circular dependency
        from animation.states import STATE_CONFIGS, AnimationState

        # Handle if state is already an AnimationState or convert from value
        if not isinstance(state, AnimationState):
            try:
                state = AnimationState(state)
            except (ValueError, TypeError):
                # Default to IDLE if invalid state
                state = AnimationState.IDLE

        # Get the state configuration
        config = STATE_CONFIGS.get(state)
        if config is None:
            # Fall back to IDLE if state not found
            config = STATE_CONFIGS.get(AnimationState.IDLE)

        if config and config.base_animations:
            # Play the first base animation for this state
            self.play(
                config.base_animations[0],
                layer=0,
                blend_time=blend_time,
            )


# ============================================================================
# ANIMATION BUILDER UTILITIES
# ============================================================================

def create_simple_animation(
    property_name: str,
    start_value: float,
    end_value: float,
    duration: float,
    easing: EasingType = EasingType.EASE_IN_OUT,
    loop: bool = False,
) -> Animation:
    """
    Create a simple two-keyframe animation.

    Args:
        property_name: Property to animate
        start_value: Starting value
        end_value: Ending value
        duration: Animation duration in seconds
        easing: Easing function to use
        loop: Whether to loop the animation

    Returns:
        Animation with two keyframes
    """
    return Animation(
        property_name=property_name,
        keyframes=[
            Keyframe(time=0.0, value=start_value, easing=EasingType.LINEAR),
            Keyframe(time=duration, value=end_value, easing=easing),
        ],
        loop=loop,
    )


def create_pulse_animation(
    property_name: str,
    base_value: float,
    peak_value: float,
    duration: float,
    easing: EasingType = EasingType.EASE_IN_OUT,
) -> Animation:
    """
    Create a pulse animation (base -> peak -> base, looping).

    Args:
        property_name: Property to animate
        base_value: Base/rest value
        peak_value: Peak value at middle of animation
        duration: Full cycle duration in seconds
        easing: Easing function to use

    Returns:
        Looping pulse animation
    """
    half = duration / 2.0
    return Animation(
        property_name=property_name,
        keyframes=[
            Keyframe(time=0.0, value=base_value, easing=EasingType.LINEAR),
            Keyframe(time=half, value=peak_value, easing=easing),
            Keyframe(time=duration, value=base_value, easing=easing),
        ],
        loop=True,
    )


def create_shake_animation(
    property_name: str,
    center_value: float,
    amplitude: float,
    frequency: int,
    duration: float,
) -> Animation:
    """
    Create a shake animation (oscillates around center).

    Args:
        property_name: Property to animate
        center_value: Center value to shake around
        amplitude: Maximum deviation from center
        frequency: Number of shakes
        duration: Total duration in seconds

    Returns:
        Shake animation
    """
    keyframes = [Keyframe(time=0.0, value=center_value, easing=EasingType.LINEAR)]

    interval = duration / (frequency * 2)
    for i in range(frequency * 2):
        t = (i + 1) * interval
        # Alternate between +amplitude and -amplitude
        offset = amplitude if (i % 2 == 0) else -amplitude
        # Decay amplitude over time
        decay = 1.0 - (t / duration) * 0.7
        value = center_value + offset * decay
        keyframes.append(Keyframe(time=t, value=value, easing=EasingType.EASE_OUT))

    # End at center
    keyframes.append(Keyframe(time=duration, value=center_value, easing=EasingType.EASE_OUT))

    return Animation(
        property_name=property_name,
        keyframes=keyframes,
        loop=False,
    )
