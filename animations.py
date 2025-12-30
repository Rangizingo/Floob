"""
Animation controller for the Desktop Virtual Pet.

Manages animation states, timing, and transitions.
"""

from enum import Enum, auto
from typing import Callable, Optional
import time
import math
import random


class AnimationState(Enum):
    """Animation states matching pet states."""
    IDLE = auto()
    WALKING = auto()
    EATING = auto()
    PLAYING = auto()
    SLEEPING = auto()
    HAPPY = auto()
    TRICK = auto()


class AnimationController:
    """
    Controls pet animations and transitions between states.

    Handles timing, frame updates, and animation callbacks.
    """

    # Animation durations in seconds
    DURATIONS = {
        AnimationState.EATING: 2.0,
        AnimationState.PLAYING: 2.5,
        AnimationState.HAPPY: 1.5,
        AnimationState.TRICK: 1.5,
    }

    # Frames per second for animations
    FPS = 30

    def __init__(self) -> None:
        """Initialize the animation controller."""
        self.current_state = AnimationState.IDLE
        self.animation_start_time: float = 0
        self.animation_progress: float = 0

        # Idle animation state
        self.idle_bounce: float = 0
        self.blink_timer: float = 0
        self.is_blinking: bool = False

        # Walking state
        self.walk_phase: float = 0
        self.walk_direction: int = 1  # 1 = right, -1 = left
        self.target_x: int = 0
        self.target_y: int = 0
        self.current_x: int = 0
        self.current_y: int = 0
        self.walk_speed: float = 2.0  # pixels per frame

        # General animation phase
        self.phase: float = 0

        # Callbacks
        self._on_animation_complete: Optional[Callable[[], None]] = None
        self._on_position_update: Optional[Callable[[int, int], None]] = None

        # Auto-wander timer
        self.wander_timer: float = 0
        self.wander_interval: float = random.uniform(10, 30)  # seconds between wanders

    def set_on_animation_complete(self, callback: Callable[[], None]) -> None:
        """Set callback for when timed animation completes."""
        self._on_animation_complete = callback

    def set_on_position_update(self, callback: Callable[[int, int], None]) -> None:
        """Set callback for position updates during walking."""
        self._on_position_update = callback

    def set_state(self, state: AnimationState) -> None:
        """
        Set the current animation state.

        Args:
            state: New animation state.
        """
        if state != self.current_state:
            self.current_state = state
            self.animation_start_time = time.time()
            self.animation_progress = 0
            self.phase = 0

    def start_walk(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int
    ) -> None:
        """
        Start walking animation to target position.

        Args:
            from_x: Starting X position.
            from_y: Starting Y position.
            to_x: Target X position.
            to_y: Target Y position.
        """
        self.current_x = from_x
        self.current_y = from_y
        self.target_x = to_x
        self.target_y = to_y
        self.walk_phase = 0

        # Determine direction
        if to_x > from_x:
            self.walk_direction = 1
        elif to_x < from_x:
            self.walk_direction = -1

        self.set_state(AnimationState.WALKING)

    def update(self, delta_time: float) -> dict:
        """
        Update animation state.

        Args:
            delta_time: Time elapsed since last update in seconds.

        Returns:
            Dictionary with animation parameters for rendering.
        """
        result = {
            "state": self.current_state,
            "bounce": 0,
            "blink": False,
            "phase": 0,
            "direction": self.walk_direction,
            "position_changed": False,
            "new_x": self.current_x,
            "new_y": self.current_y,
        }

        if self.current_state == AnimationState.IDLE:
            result.update(self._update_idle(delta_time))
        elif self.current_state == AnimationState.WALKING:
            result.update(self._update_walking(delta_time))
        elif self.current_state == AnimationState.SLEEPING:
            result.update(self._update_sleeping(delta_time))
        elif self.current_state in self.DURATIONS:
            result.update(self._update_timed_animation(delta_time))

        return result

    def _update_idle(self, delta_time: float) -> dict:
        """Update idle animation."""
        # Gentle bounce
        self.idle_bounce += delta_time * 3
        bounce = math.sin(self.idle_bounce) * 2

        # Occasional blink
        self.blink_timer += delta_time
        if not self.is_blinking and self.blink_timer > random.uniform(2, 5):
            self.is_blinking = True
            self.blink_timer = 0
        elif self.is_blinking and self.blink_timer > 0.15:
            self.is_blinking = False
            self.blink_timer = 0

        # Auto-wander check
        self.wander_timer += delta_time
        should_wander = False
        if self.wander_timer >= self.wander_interval:
            self.wander_timer = 0
            self.wander_interval = random.uniform(10, 30)
            should_wander = True

        return {
            "bounce": bounce,
            "blink": self.is_blinking,
            "should_wander": should_wander,
        }

    def _update_walking(self, delta_time: float) -> dict:
        """Update walking animation."""
        self.walk_phase += delta_time * 4
        if self.walk_phase >= 1:
            self.walk_phase = self.walk_phase % 1

        # Move towards target
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y
        distance = math.sqrt(dx * dx + dy * dy)

        position_changed = False

        if distance > self.walk_speed:
            # Normalize and move
            move_x = (dx / distance) * self.walk_speed
            move_y = (dy / distance) * self.walk_speed
            self.current_x = int(self.current_x + move_x)
            self.current_y = int(self.current_y + move_y)
            position_changed = True

            if self._on_position_update:
                self._on_position_update(self.current_x, self.current_y)
        else:
            # Arrived at destination
            self.current_x = self.target_x
            self.current_y = self.target_y
            position_changed = True

            # Transition back to idle
            self.set_state(AnimationState.IDLE)
            if self._on_animation_complete:
                self._on_animation_complete()

        return {
            "phase": self.walk_phase,
            "direction": self.walk_direction,
            "position_changed": position_changed,
            "new_x": self.current_x,
            "new_y": self.current_y,
        }

    def _update_sleeping(self, delta_time: float) -> dict:
        """Update sleeping animation."""
        self.phase += delta_time * 0.5
        if self.phase >= 1:
            self.phase = self.phase % 1

        return {
            "phase": self.phase,
        }

    def _update_timed_animation(self, delta_time: float) -> dict:
        """Update timed animation (eating, playing, etc.)."""
        duration = self.DURATIONS.get(self.current_state, 1.0)
        elapsed = time.time() - self.animation_start_time

        self.phase += delta_time * 2
        self.animation_progress = min(1.0, elapsed / duration)

        if elapsed >= duration:
            # Animation complete
            self.set_state(AnimationState.IDLE)
            if self._on_animation_complete:
                self._on_animation_complete()

        return {
            "phase": self.phase,
            "progress": self.animation_progress,
        }

    def check_wander(self, screen_width: int, screen_height: int, pet_size: int) -> Optional[tuple[int, int]]:
        """
        Check if pet should wander and return target position.

        Args:
            screen_width: Screen width in pixels.
            screen_height: Screen height in pixels.
            pet_size: Size of pet window.

        Returns:
            Tuple of (x, y) target position, or None if not wandering.
        """
        if self.current_state != AnimationState.IDLE:
            return None

        # Random position within screen bounds
        margin = 50
        target_x = random.randint(margin, screen_width - pet_size - margin)
        target_y = random.randint(margin, screen_height - pet_size - margin)

        return (target_x, target_y)
