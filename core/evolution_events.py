"""
Floob 2.0 Evolution Events Module.

Handles evolution event detection, triggering, and state transitions.
Provides pre-evolution signs, evolution sequences, and post-evolution handling.

Pre-Evolution Signs:
    - Glowing/shimmering when within 10 XP of threshold
    - Excited idle behavior when evolution imminent

Evolution Trigger:
    - Starts evolution animation sequence
    - Updates pet form and stage
    - Records evolution in history

Post-Evolution:
    - Resets certain state
    - Adds to evolution history with timestamp
    - Triggers celebration effects
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, TYPE_CHECKING

from core.config import Timing
from core.evolution import (
    EvolutionStage,
    EvolutionForm,
    get_form_by_id,
    FORM_GOLDEN,
    FORM_GHOST,
    FORM_RAINBOW,
)

if TYPE_CHECKING:
    from core.evolution_manager import EvolutionManager
    from core.care_tracker import CareTracker


logger = logging.getLogger(__name__)


class EvolutionEventType(Enum):
    """Types of evolution-related events."""
    EVOLUTION_IMMINENT = auto()      # Within threshold of evolving
    EVOLUTION_READY = auto()         # Ready to evolve
    EVOLUTION_STARTED = auto()       # Evolution animation beginning
    EVOLUTION_COMPLETE = auto()      # Evolution finished
    SPECIAL_EVOLUTION = auto()       # Special form achieved


class EvolutionAnimationType(Enum):
    """Types of evolution animations."""
    STANDARD = "evolution_standard"      # Normal stage evolution
    SPECIAL_GOLDEN = "evolution_golden"  # Golden form transformation
    SPECIAL_GHOST = "evolution_ghost"    # Ghost form emergence
    SPECIAL_RAINBOW = "evolution_rainbow" # Rainbow shimmer transformation


@dataclass
class EvolutionEvent:
    """
    Represents an evolution event.

    Attributes:
        event_type: Type of evolution event.
        timestamp: When the event occurred.
        old_form_id: Previous form ID (for transitions).
        new_form_id: New form ID (for transitions).
        animation_type: Animation to play.
        metadata: Additional event data.
    """
    event_type: EvolutionEventType
    timestamp: float = field(default_factory=time.time)
    old_form_id: Optional[str] = None
    new_form_id: Optional[str] = None
    animation_type: EvolutionAnimationType = EvolutionAnimationType.STANDARD
    metadata: Dict = field(default_factory=dict)


class EvolutionEventHandler:
    """
    Handles evolution event detection and triggering.

    Monitors evolution manager state and fires appropriate events
    when evolution conditions are met.

    Attributes:
        evolution_manager: Reference to the evolution manager.
        care_tracker: Reference to the care tracker.
        on_evolution_event: Callback for evolution events.
    """

    # XP threshold for "imminent" evolution detection
    IMMINENT_XP_THRESHOLD: int = 10

    def __init__(
        self,
        evolution_manager: "EvolutionManager",
        care_tracker: Optional["CareTracker"] = None,
    ) -> None:
        """
        Initialize the evolution event handler.

        Args:
            evolution_manager: The evolution manager to monitor.
            care_tracker: Optional care tracker for special evolution checks.
        """
        self.evolution_manager = evolution_manager
        self.care_tracker = care_tracker
        self._callbacks: List[Callable[[EvolutionEvent], None]] = []
        self._evolution_in_progress: bool = False
        self._last_imminent_check: float = 0.0
        self._imminent_notified: bool = False
        self._pending_evolution: Optional[EvolutionEvent] = None

    def add_callback(self, callback: Callable[[EvolutionEvent], None]) -> None:
        """
        Add a callback for evolution events.

        Args:
            callback: Function to call when evolution events occur.
        """
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[EvolutionEvent], None]) -> None:
        """
        Remove an evolution event callback.

        Args:
            callback: The callback to remove.
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _emit_event(self, event: EvolutionEvent) -> None:
        """
        Emit an evolution event to all callbacks.

        Args:
            event: The event to emit.
        """
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Evolution callback error: {e}")

    def is_evolution_imminent(self) -> bool:
        """
        Check if evolution is imminent (within threshold).

        Returns True when the pet is close to evolving,
        allowing for pre-evolution visual effects.

        Returns:
            True if within IMMINENT_XP_THRESHOLD of evolution.
        """
        if not self.evolution_manager.check_evolution_ready():
            # Check if we're close to the next level that would trigger evolution
            current_xp, needed_xp = self.evolution_manager.get_xp_to_next_level()
            remaining = needed_xp - current_xp

            # Check if next level would trigger evolution
            next_level = self.evolution_manager.get_level() + 1
            next_stage = self.evolution_manager.get_stage_for_level(next_level)

            if next_stage.value > self.evolution_manager.evolution_stage.value:
                # Evolution would happen at next level
                if remaining <= self.IMMINENT_XP_THRESHOLD:
                    return True

        return False

    def is_evolution_ready(self) -> bool:
        """
        Check if evolution is ready to trigger.

        Returns:
            True if pet should evolve now.
        """
        return self.evolution_manager.check_evolution_ready()

    def check_special_evolution_eligibility(
        self,
        care_tracker: Optional["CareTracker"] = None,
    ) -> Optional[EvolutionForm]:
        """
        Check if special evolution conditions are met.

        Checks in priority order: Golden > Rainbow > Ghost.

        Args:
            care_tracker: Care tracker for checking conditions.

        Returns:
            Special EvolutionForm if eligible, None otherwise.
        """
        tracker = care_tracker or self.care_tracker

        if not tracker:
            return None

        # Must be at least level 5 for special evolutions
        if self.evolution_manager.get_level() < 5:
            return None

        # Check Golden (highest priority)
        if self._check_golden_eligibility(tracker):
            return FORM_GOLDEN

        # Check Rainbow (second priority)
        if self._check_rainbow_eligibility():
            return FORM_RAINBOW

        # Check Ghost (third priority)
        if self._check_ghost_eligibility(tracker):
            return FORM_GHOST

        return None

    def _check_golden_eligibility(self, care_tracker: "CareTracker") -> bool:
        """
        Check Golden form eligibility.

        Requirement: Perfect care (all stats > 80) for 7 consecutive days.

        Args:
            care_tracker: Care tracker to check.

        Returns:
            True if eligible for Golden form.
        """
        return care_tracker.check_perfect_care_streak(days=7, min_stat=80.0)

    def _check_ghost_eligibility(self, care_tracker: "CareTracker") -> bool:
        """
        Check Ghost form eligibility.

        Requirement: Pet fainted (any stat hit 0), then was revived.

        Args:
            care_tracker: Care tracker to check.

        Returns:
            True if eligible for Ghost form.
        """
        return care_tracker.was_critically_neglected()

    def _check_rainbow_eligibility(self, current_date: Optional[str] = None) -> bool:
        """
        Check Rainbow form eligibility.

        Requirement: Evolve on a special date (holidays) or rare random chance.

        Args:
            current_date: Optional date string for testing.

        Returns:
            True if eligible for Rainbow form.
        """
        if self.care_tracker and self.care_tracker.is_special_date():
            return True

        # Fallback: 1% random chance on any evolution
        # Note: This would be checked differently in a real implementation
        # to ensure determinism. For now, we skip the random element
        # and only use special dates.
        return False

    def get_animation_for_form(self, form_id: str) -> EvolutionAnimationType:
        """
        Get the appropriate animation type for a form.

        Args:
            form_id: The form being evolved into.

        Returns:
            The animation type to use.
        """
        form = get_form_by_id(form_id)
        if not form:
            return EvolutionAnimationType.STANDARD

        if form.id == "golden":
            return EvolutionAnimationType.SPECIAL_GOLDEN
        elif form.id == "ghost":
            return EvolutionAnimationType.SPECIAL_GHOST
        elif form.id == "rainbow":
            return EvolutionAnimationType.SPECIAL_RAINBOW
        else:
            return EvolutionAnimationType.STANDARD

    def trigger_evolution(self, new_form_id: str) -> Optional[EvolutionEvent]:
        """
        Trigger an evolution to a new form.

        Starts the evolution process, emitting appropriate events.
        Does not complete the evolution - that requires calling
        complete_evolution() after the animation finishes.

        Args:
            new_form_id: The form to evolve into.

        Returns:
            The evolution event, or None if evolution cannot proceed.
        """
        if self._evolution_in_progress:
            logger.warning("Evolution already in progress")
            return None

        new_form = get_form_by_id(new_form_id)
        if not new_form:
            logger.error(f"Cannot trigger evolution: form '{new_form_id}' not found")
            return None

        old_form_id = self.evolution_manager.current_form_id
        animation_type = self.get_animation_for_form(new_form_id)

        # Create the evolution event
        event = EvolutionEvent(
            event_type=EvolutionEventType.EVOLUTION_STARTED,
            old_form_id=old_form_id,
            new_form_id=new_form_id,
            animation_type=animation_type,
            metadata={
                "old_stage": self.evolution_manager.evolution_stage.name,
                "new_stage": new_form.stage.name,
                "level": self.evolution_manager.get_level(),
                "is_special": new_form.is_special,
            }
        )

        self._evolution_in_progress = True
        self._pending_evolution = event

        logger.info(
            f"Evolution triggered: {old_form_id} -> {new_form_id} "
            f"(Animation: {animation_type.name})"
        )

        # Emit the event
        self._emit_event(event)

        return event

    def complete_evolution(self) -> Optional[EvolutionEvent]:
        """
        Complete a pending evolution.

        Called after the evolution animation finishes.
        Updates the evolution manager and emits completion event.

        Returns:
            The completion event, or None if no evolution was pending.
        """
        if not self._evolution_in_progress or not self._pending_evolution:
            logger.warning("No evolution in progress to complete")
            return None

        pending = self._pending_evolution
        new_form_id = pending.new_form_id

        if not new_form_id:
            logger.error("Pending evolution has no target form")
            self._evolution_in_progress = False
            self._pending_evolution = None
            return None

        # Execute the evolution in the manager
        success = self.evolution_manager.execute_evolution(new_form_id)

        if not success:
            logger.error(f"Evolution execution failed for form '{new_form_id}'")
            self._evolution_in_progress = False
            self._pending_evolution = None
            return None

        # Create completion event
        new_form = get_form_by_id(new_form_id)
        event = EvolutionEvent(
            event_type=(
                EvolutionEventType.SPECIAL_EVOLUTION
                if new_form and new_form.is_special
                else EvolutionEventType.EVOLUTION_COMPLETE
            ),
            old_form_id=pending.old_form_id,
            new_form_id=new_form_id,
            animation_type=pending.animation_type,
            metadata={
                "form_name": new_form.name if new_form else "Unknown",
                "form_description": new_form.description if new_form else "",
                "stage": self.evolution_manager.evolution_stage.name,
                "level": self.evolution_manager.get_level(),
                "total_evolutions": len(self.evolution_manager.evolution_history),
            }
        )

        self._evolution_in_progress = False
        self._pending_evolution = None
        self._imminent_notified = False

        logger.info(
            f"Evolution completed: Now a {new_form.name if new_form else new_form_id} "
            f"(Level {self.evolution_manager.get_level()})"
        )

        # Emit the event
        self._emit_event(event)

        return event

    def cancel_evolution(self) -> None:
        """
        Cancel a pending evolution.

        Use if the evolution animation is interrupted.
        """
        if self._evolution_in_progress:
            logger.info("Evolution cancelled")
            self._evolution_in_progress = False
            self._pending_evolution = None

    def update(self) -> Optional[EvolutionEvent]:
        """
        Update evolution state and check for events.

        Should be called regularly to detect evolution conditions.

        Returns:
            An evolution event if one should be triggered, None otherwise.
        """
        if self._evolution_in_progress:
            return None  # Wait for current evolution to complete

        # Check for imminent evolution (for visual effects)
        if self.is_evolution_imminent() and not self._imminent_notified:
            self._imminent_notified = True
            event = EvolutionEvent(
                event_type=EvolutionEventType.EVOLUTION_IMMINENT,
                old_form_id=self.evolution_manager.current_form_id,
                metadata={
                    "xp_remaining": self.evolution_manager.get_xp_to_next_level()[1]
                    - self.evolution_manager.get_xp_to_next_level()[0]
                }
            )
            self._emit_event(event)
            return event

        # Check if evolution should happen
        if self.is_evolution_ready():
            # Check for special evolutions first
            special_form = self.check_special_evolution_eligibility()

            if special_form:
                target_form_id = special_form.id
            else:
                # Get normal evolution target
                target_form_id = self.evolution_manager.calculate_evolution_form(
                    self.care_tracker
                )

            if target_form_id:
                event = EvolutionEvent(
                    event_type=EvolutionEventType.EVOLUTION_READY,
                    old_form_id=self.evolution_manager.current_form_id,
                    new_form_id=target_form_id,
                    metadata={
                        "is_special": get_form_by_id(target_form_id).is_special
                        if get_form_by_id(target_form_id)
                        else False
                    }
                )
                self._emit_event(event)
                return event

        return None

    @property
    def is_in_progress(self) -> bool:
        """Check if an evolution is currently in progress."""
        return self._evolution_in_progress

    @property
    def pending_form_id(self) -> Optional[str]:
        """Get the pending evolution form ID, if any."""
        if self._pending_evolution:
            return self._pending_evolution.new_form_id
        return None
