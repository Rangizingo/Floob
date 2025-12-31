"""
Floob 2.0 Evolution Integration Module.

Connects the evolution system components together and provides
a unified interface for processing evolution in the game loop.

This module integrates:
    - EvolutionManager: XP and level tracking
    - CareTracker: Care pattern analysis
    - EvolutionEventHandler: Event detection and triggering

Main Interface:
    - process_evolution(): Main evolution processing called each update
    - record_interaction(): Record XP-granting interactions
    - get_evolution_status(): Get current evolution state
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

from core.evolution import (
    EvolutionStage,
    EvolutionForm,
    CareStyle,
    get_form_by_id,
    get_possible_evolutions,
)
from core.evolution_manager import (
    EvolutionManager,
    EvolutionHistory,
    XPSource,
)
from core.evolution_events import (
    EvolutionEventHandler,
    EvolutionEvent,
    EvolutionEventType,
    EvolutionAnimationType,
)
from core.care_tracker import CareTracker, CareEventType

if TYPE_CHECKING:
    from core.pet import PetStats


logger = logging.getLogger(__name__)


class EvolutionStatus(Enum):
    """Status of the evolution system."""
    IDLE = auto()               # Normal state, no evolution pending
    IMMINENT = auto()           # Close to evolving (within threshold)
    READY = auto()              # Ready to evolve, waiting for trigger
    EVOLVING = auto()           # Evolution animation in progress
    JUST_EVOLVED = auto()       # Recently evolved (for celebration effects)


@dataclass
class EvolutionState:
    """
    Complete evolution state for the UI and game logic.

    Attributes:
        status: Current evolution status.
        current_form: Current evolution form.
        current_stage: Current evolution stage.
        level: Current level.
        total_xp: Total experience points.
        xp_progress: Tuple of (current_xp_in_level, xp_needed).
        care_style: Current care style.
        possible_evolutions: List of possible next forms with probabilities.
        evolution_history: List of past evolutions.
        pending_evolution: Form ID of pending evolution, if any.
        special_eligible: List of special forms currently eligible for.
    """
    status: EvolutionStatus
    current_form: Optional[EvolutionForm]
    current_stage: EvolutionStage
    level: int
    total_xp: int
    xp_progress: Tuple[int, int]
    care_style: CareStyle
    possible_evolutions: List[Tuple[EvolutionForm, float]]
    evolution_history: List[EvolutionHistory]
    pending_evolution: Optional[str] = None
    special_eligible: List[str] = None

    def __post_init__(self):
        if self.special_eligible is None:
            self.special_eligible = []


class EvolutionIntegrator:
    """
    Main integration point for the evolution system.

    Coordinates between EvolutionManager, CareTracker, and
    EvolutionEventHandler to provide a unified evolution interface.

    Usage:
        integrator = EvolutionIntegrator()

        # In game loop
        result = integrator.process_evolution(pet_stats)
        if result and result.event_type == EvolutionEventType.EVOLUTION_READY:
            # Start evolution animation
            integrator.start_evolution()

        # When animation completes
        integrator.complete_evolution()
    """

    def __init__(
        self,
        evolution_manager: Optional[EvolutionManager] = None,
        care_tracker: Optional[CareTracker] = None,
    ) -> None:
        """
        Initialize the evolution integrator.

        Args:
            evolution_manager: Existing manager, or None to create new.
            care_tracker: Existing tracker, or None to create new.
        """
        self.evolution_manager = evolution_manager or EvolutionManager()
        self.care_tracker = care_tracker or CareTracker()
        self.event_handler = EvolutionEventHandler(
            self.evolution_manager,
            self.care_tracker,
        )

        self._status: EvolutionStatus = EvolutionStatus.IDLE
        self._just_evolved_until: float = 0.0
        self._callbacks: List[Callable[[EvolutionEvent], None]] = []

        # Register internal callback
        self.event_handler.add_callback(self._on_evolution_event)

    def add_callback(self, callback: Callable[[EvolutionEvent], None]) -> None:
        """
        Add a callback for evolution events.

        Args:
            callback: Function to call on evolution events.
        """
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[EvolutionEvent], None]) -> None:
        """
        Remove an evolution callback.

        Args:
            callback: The callback to remove.
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _on_evolution_event(self, event: EvolutionEvent) -> None:
        """Internal handler for evolution events."""
        # Update status
        if event.event_type == EvolutionEventType.EVOLUTION_IMMINENT:
            self._status = EvolutionStatus.IMMINENT
        elif event.event_type == EvolutionEventType.EVOLUTION_READY:
            self._status = EvolutionStatus.READY
        elif event.event_type == EvolutionEventType.EVOLUTION_STARTED:
            self._status = EvolutionStatus.EVOLVING
        elif event.event_type in (
            EvolutionEventType.EVOLUTION_COMPLETE,
            EvolutionEventType.SPECIAL_EVOLUTION,
        ):
            self._status = EvolutionStatus.JUST_EVOLVED
            self._just_evolved_until = time.time() + 5.0  # 5 second celebration

        # Forward to external callbacks
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Evolution callback error: {e}")

    def record_interaction(
        self,
        interaction_type: str,
        stats: Optional["PetStats"] = None,
    ) -> int:
        """
        Record an interaction that grants XP.

        Also records the care event for care style tracking.

        Args:
            interaction_type: Type of interaction (feed, play, click, trick, sleep).
            stats: Optional current stats for snapshot.

        Returns:
            Amount of XP gained.
        """
        xp_source_map = {
            "feed": XPSource.FEED,
            "play": XPSource.PLAY,
            "click": XPSource.CLICK,
            "pet": XPSource.CLICK,
            "trick": XPSource.TRICK,
            "sleep_complete": XPSource.SLEEP_COMPLETE,
        }

        care_event_map = {
            "feed": CareEventType.FEED,
            "play": CareEventType.PLAY,
            "click": CareEventType.PET,
            "pet": CareEventType.PET,
            "trick": CareEventType.TRICK,
            "sleep_start": CareEventType.SLEEP_START,
            "sleep_complete": CareEventType.SLEEP_END,
        }

        xp_gained = 0

        # Add XP
        xp_source = xp_source_map.get(interaction_type.lower())
        if xp_source:
            xp_gained = self.evolution_manager.add_xp(xp_source)

        # Record care event
        care_event = care_event_map.get(interaction_type.lower())
        if care_event:
            self.care_tracker.record_event(care_event)

        # Record stat snapshot if stats provided
        if stats:
            self.care_tracker.record_snapshot(
                hunger=stats.hunger,
                happiness=stats.happiness,
                energy=stats.energy,
            )

        return xp_gained

    def process_evolution(
        self,
        hunger: float,
        happiness: float,
        energy: float,
    ) -> Optional[EvolutionEvent]:
        """
        Main evolution processing method.

        Called each update cycle to:
        1. Update passive XP
        2. Record stat snapshot
        3. Check for evolution conditions
        4. Return any evolution events

        Args:
            hunger: Current hunger stat.
            happiness: Current happiness stat.
            energy: Current energy stat.

        Returns:
            EvolutionEvent if one occurred, None otherwise.
        """
        # Update passive XP
        self.evolution_manager.update_passive_xp()

        # Record stat snapshot
        self.care_tracker.record_snapshot(hunger, happiness, energy)

        # Check if celebration period ended
        if self._status == EvolutionStatus.JUST_EVOLVED:
            if time.time() >= self._just_evolved_until:
                self._status = EvolutionStatus.IDLE

        # Check for evolution events
        event = self.event_handler.update()

        return event

    def start_evolution(self) -> Optional[EvolutionEvent]:
        """
        Start the evolution process.

        Should be called when the game is ready to show
        the evolution animation.

        Returns:
            The evolution started event, or None if cannot start.
        """
        if self._status != EvolutionStatus.READY:
            logger.warning(f"Cannot start evolution: status is {self._status.name}")
            return None

        # Get the target form
        special_form = self.event_handler.check_special_evolution_eligibility()

        if special_form:
            target_form_id = special_form.id
        else:
            target_form_id = self.evolution_manager.calculate_evolution_form(
                self.care_tracker
            )

        if not target_form_id:
            logger.error("Cannot start evolution: no target form found")
            return None

        return self.event_handler.trigger_evolution(target_form_id)

    def complete_evolution(self) -> Optional[EvolutionEvent]:
        """
        Complete the evolution process.

        Should be called when the evolution animation finishes.

        Returns:
            The evolution complete event, or None if no evolution pending.
        """
        return self.event_handler.complete_evolution()

    def cancel_evolution(self) -> None:
        """
        Cancel a pending evolution.

        Use if the evolution animation is interrupted.
        """
        self.event_handler.cancel_evolution()
        self._status = EvolutionStatus.IDLE

    def get_evolution_status(self) -> EvolutionState:
        """
        Get the complete current evolution state.

        Returns:
            EvolutionState with all current evolution information.
        """
        current_form = get_form_by_id(self.evolution_manager.current_form_id)
        care_style = self.care_tracker.calculate_care_style()

        # Get special forms we're eligible for
        special_eligible = []
        if self.event_handler._check_golden_eligibility(self.care_tracker):
            special_eligible.append("golden")
        if self.event_handler._check_rainbow_eligibility():
            special_eligible.append("rainbow")
        if self.event_handler._check_ghost_eligibility(self.care_tracker):
            special_eligible.append("ghost")

        return EvolutionState(
            status=self._status,
            current_form=current_form,
            current_stage=self.evolution_manager.evolution_stage,
            level=self.evolution_manager.get_level(),
            total_xp=self.evolution_manager.total_xp,
            xp_progress=self.evolution_manager.get_xp_to_next_level(),
            care_style=care_style,
            possible_evolutions=self.evolution_manager.get_evolution_preview(
                self.care_tracker
            ),
            evolution_history=self.evolution_manager.evolution_history,
            pending_evolution=self.event_handler.pending_form_id,
            special_eligible=special_eligible,
        )

    def get_care_summary(self) -> Dict:
        """
        Get a summary of care patterns for UI display.

        Returns:
            Dict with care statistics.
        """
        return self.care_tracker.get_care_summary()

    def force_evolution_check(self) -> bool:
        """
        Force an evolution check.

        Useful for testing or after loading a save.

        Returns:
            True if evolution is now ready.
        """
        return self.event_handler.is_evolution_ready()

    def grant_bonus_xp(self, amount: int, reason: str = "bonus") -> int:
        """
        Grant bonus XP outside of normal interactions.

        Args:
            amount: Amount of XP to grant.
            reason: Description for logging.

        Returns:
            Amount of XP granted.
        """
        return self.evolution_manager.add_xp_raw(amount, reason)

    def to_dict(self) -> Dict:
        """
        Convert integration state to dictionary for serialization.

        Returns:
            Dict containing all state data.
        """
        return {
            "evolution_manager": self.evolution_manager.to_dict(),
            "care_tracker": self.care_tracker.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EvolutionIntegrator":
        """
        Create integrator from dictionary.

        Args:
            data: Dict containing state data.

        Returns:
            New EvolutionIntegrator instance.
        """
        em_data = data.get("evolution_manager", {})
        ct_data = data.get("care_tracker", {})

        evolution_manager = EvolutionManager.from_dict(em_data)
        care_tracker = CareTracker.from_dict(ct_data)

        return cls(
            evolution_manager=evolution_manager,
            care_tracker=care_tracker,
        )


def process_evolution(
    integrator: EvolutionIntegrator,
    hunger: float,
    happiness: float,
    energy: float,
) -> Optional[EvolutionEvent]:
    """
    Convenience function for processing evolution.

    Main evolution processing to be called each game update.

    Args:
        integrator: The evolution integrator.
        hunger: Current hunger stat.
        happiness: Current happiness stat.
        energy: Current energy stat.

    Returns:
        EvolutionEvent if one occurred, None otherwise.
    """
    return integrator.process_evolution(hunger, happiness, energy)
