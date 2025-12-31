"""
Floob 2.0 Evolution Manager.

Handles XP gain, level calculation, and evolution mechanics.
Connects care patterns to actual evolution decisions.

XP System:
    - Feeding: +5 XP
    - Playing: +10 XP
    - Clicking/petting: +1 XP
    - Tricks: +3 XP
    - Time alive: +1 XP per minute (passive)
    - Perfect care bonus: +20 XP daily
    - Evolution bonus: +50 XP

Level Thresholds:
    - Level 1-5: 50 XP each (Baby stage)
    - Level 5: Evolve to Child
    - Level 6-15: 100 XP each (Child stage)
    - Level 15: Evolve to Teen
    - Level 16-30: 150 XP each (Teen stage)
    - Level 30: Evolve to Adult
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple

from core.config import XP as XPConfig, Evolution as EvolutionConfig
from core.evolution import (
    EvolutionStage,
    CareStyle,
    EvolutionForm,
    EVOLUTION_FORMS,
    EVOLUTION_TREE,
    get_form_by_id,
    get_possible_evolutions,
)
from core.care_tracker import CareTracker


logger = logging.getLogger(__name__)


class XPSource(Enum):
    """Sources of XP gain."""
    FEED = auto()
    PLAY = auto()
    CLICK = auto()
    TRICK = auto()
    TIME_ALIVE = auto()
    SLEEP_COMPLETE = auto()
    PERFECT_CARE_BONUS = auto()
    EVOLUTION_BONUS = auto()
    DAILY_LOGIN = auto()


# XP values for each source
XP_VALUES: Dict[XPSource, int] = {
    XPSource.FEED: XPConfig.FEED,
    XPSource.PLAY: XPConfig.PLAY,
    XPSource.CLICK: XPConfig.CLICK,
    XPSource.TRICK: XPConfig.TRICK,
    XPSource.TIME_ALIVE: XPConfig.TIME_ALIVE_PER_MINUTE,
    XPSource.SLEEP_COMPLETE: XPConfig.SLEEP_COMPLETE,
    XPSource.PERFECT_CARE_BONUS: XPConfig.PERFECT_CARE_BONUS,
    XPSource.EVOLUTION_BONUS: XPConfig.EVOLUTION_BONUS,
    XPSource.DAILY_LOGIN: XPConfig.DAILY_LOGIN_STREAK,
}


@dataclass
class LevelThreshold:
    """
    Defines XP requirements for a level range.

    Attributes:
        level_min: Starting level for this threshold.
        level_max: Ending level for this threshold (inclusive).
        xp_per_level: XP required per level in this range.
    """
    level_min: int
    level_max: int
    xp_per_level: int


# Level thresholds as defined in scope
LEVEL_THRESHOLDS: List[LevelThreshold] = [
    LevelThreshold(level_min=1, level_max=5, xp_per_level=50),    # Baby stage
    LevelThreshold(level_min=6, level_max=15, xp_per_level=100),  # Child stage
    LevelThreshold(level_min=16, level_max=30, xp_per_level=150), # Teen stage
    LevelThreshold(level_min=31, level_max=100, xp_per_level=200),# Adult stage
]

# Evolution level thresholds
EVOLUTION_LEVEL_THRESHOLDS: Dict[EvolutionStage, int] = {
    EvolutionStage.EGG: 0,
    EvolutionStage.BABY: 1,
    EvolutionStage.CHILD: 5,
    EvolutionStage.TEEN: 15,
    EvolutionStage.ADULT: 30,
}


@dataclass
class EvolutionHistory:
    """
    Record of a single evolution event.

    Attributes:
        form_id: The form evolved into.
        timestamp: When the evolution occurred (Unix timestamp).
        level: Level at time of evolution.
    """
    form_id: str
    timestamp: float
    level: int

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "form_id": self.form_id,
            "timestamp": self.timestamp,
            "level": self.level,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EvolutionHistory":
        """Create from dictionary."""
        return cls(
            form_id=data.get("form_id", "egg"),
            timestamp=data.get("timestamp", time.time()),
            level=data.get("level", 0),
        )


class EvolutionManager:
    """
    Manages XP, levels, and evolution mechanics.

    Tracks experience points, calculates levels, and determines
    when and how pets should evolve based on care patterns.

    Attributes:
        total_xp: Total accumulated experience points.
        current_form_id: Current evolution form ID.
        evolution_stage: Current evolution stage.
        evolution_history: List of past evolutions.
    """

    def __init__(
        self,
        total_xp: int = 0,
        current_form_id: str = "egg",
        evolution_history: Optional[List[EvolutionHistory]] = None,
    ) -> None:
        """
        Initialize the evolution manager.

        Args:
            total_xp: Starting XP value.
            current_form_id: Starting form ID.
            evolution_history: Previous evolution history.
        """
        self.total_xp = total_xp
        self.current_form_id = current_form_id
        self.evolution_history = evolution_history or []
        self._last_time_xp_update: float = time.time()
        self._pending_evolution: Optional[str] = None

        # Calculate current stage from form
        current_form = get_form_by_id(current_form_id)
        if current_form:
            self.evolution_stage = current_form.stage
        else:
            self.evolution_stage = EvolutionStage.EGG

    def add_xp(self, source: XPSource, multiplier: float = 1.0) -> int:
        """
        Add XP from a specific source.

        Args:
            source: The source of XP gain.
            multiplier: Optional multiplier for the XP amount.

        Returns:
            Amount of XP gained.
        """
        base_xp = XP_VALUES.get(source, 0)
        gained_xp = int(base_xp * multiplier)
        self.total_xp += gained_xp

        logger.debug(f"Gained {gained_xp} XP from {source.name}. Total: {self.total_xp}")

        return gained_xp

    def add_xp_raw(self, amount: int, source_description: str = "unknown") -> int:
        """
        Add a raw XP amount (for custom/special cases).

        Args:
            amount: Amount of XP to add.
            source_description: Description for logging.

        Returns:
            Amount of XP gained.
        """
        self.total_xp += amount
        logger.debug(f"Gained {amount} XP from {source_description}. Total: {self.total_xp}")
        return amount

    def update_passive_xp(self) -> int:
        """
        Update passive XP gain from time alive.

        Should be called periodically (e.g., every update cycle).

        Returns:
            Amount of XP gained this update.
        """
        current_time = time.time()
        elapsed_minutes = (current_time - self._last_time_xp_update) / 60.0

        # Only award XP for whole minutes
        whole_minutes = int(elapsed_minutes)
        if whole_minutes > 0:
            xp_gained = whole_minutes * XP_VALUES[XPSource.TIME_ALIVE]
            self.total_xp += xp_gained
            # Only advance time by the minutes we counted
            self._last_time_xp_update += whole_minutes * 60
            logger.debug(f"Passive XP: +{xp_gained} ({whole_minutes} minutes)")
            return xp_gained

        return 0

    def get_level(self) -> int:
        """
        Calculate current level from total XP.

        Uses tiered thresholds where different level ranges
        require different amounts of XP per level.

        Returns:
            Current level (1-based).
        """
        if self.total_xp <= 0:
            return 0

        remaining_xp = self.total_xp
        level = 0

        for threshold in LEVEL_THRESHOLDS:
            levels_in_range = threshold.level_max - threshold.level_min + 1
            xp_for_range = levels_in_range * threshold.xp_per_level

            if remaining_xp >= xp_for_range:
                level = threshold.level_max
                remaining_xp -= xp_for_range
            else:
                # Partial progress through this range
                levels_gained = remaining_xp // threshold.xp_per_level
                level = threshold.level_min - 1 + levels_gained
                break

        return max(1, level)  # Minimum level 1

    def get_xp_for_level(self, level: int) -> int:
        """
        Get the total XP required to reach a specific level.

        Args:
            level: Target level.

        Returns:
            Total XP required.
        """
        if level <= 0:
            return 0

        total = 0
        remaining_level = level

        for threshold in LEVEL_THRESHOLDS:
            if remaining_level <= 0:
                break

            # How many levels in this range do we need?
            range_start = threshold.level_min
            range_end = min(threshold.level_max, level)

            if level >= range_start:
                levels_in_range = min(remaining_level, range_end - range_start + 1)
                total += levels_in_range * threshold.xp_per_level
                remaining_level -= levels_in_range

        return total

    def get_xp_to_next_level(self) -> Tuple[int, int]:
        """
        Get XP progress toward next level.

        Returns:
            Tuple of (current_xp_in_level, xp_needed_for_level).
        """
        current_level = self.get_level()
        xp_for_current = self.get_xp_for_level(current_level)
        xp_for_next = self.get_xp_for_level(current_level + 1)

        xp_in_level = self.total_xp - xp_for_current
        xp_needed = xp_for_next - xp_for_current

        return (max(0, xp_in_level), xp_needed)

    def get_level_progress(self) -> float:
        """
        Get progress toward next level as a fraction.

        Returns:
            Progress from 0.0 to 1.0.
        """
        current, needed = self.get_xp_to_next_level()
        if needed <= 0:
            return 1.0
        return min(1.0, current / needed)

    def get_stage_for_level(self, level: int) -> EvolutionStage:
        """
        Determine the evolution stage for a given level.

        Args:
            level: The level to check.

        Returns:
            The appropriate EvolutionStage.
        """
        if level < 1:
            return EvolutionStage.EGG
        elif level < 5:
            return EvolutionStage.BABY
        elif level < 15:
            return EvolutionStage.CHILD
        elif level < 30:
            return EvolutionStage.TEEN
        else:
            return EvolutionStage.ADULT

    def check_evolution_ready(self) -> bool:
        """
        Check if the pet is ready to evolve.

        Returns True if the current level exceeds the threshold
        for the current evolution stage.

        Returns:
            True if evolution should be triggered.
        """
        current_level = self.get_level()
        current_form = get_form_by_id(self.current_form_id)

        if not current_form:
            return False

        # Get possible next forms
        possible_evolutions = get_possible_evolutions(self.current_form_id)

        if not possible_evolutions:
            return False  # Already at terminal form

        # Check if we've reached the level threshold for evolution
        target_stage = self.get_stage_for_level(current_level)

        # Should evolve if target stage is higher than current
        return target_stage.value > self.evolution_stage.value

    def calculate_evolution_form(
        self,
        care_tracker: Optional[CareTracker] = None,
    ) -> Optional[str]:
        """
        Determine which form the pet should evolve into.

        Uses care style from CareTracker to select the appropriate
        evolution path. If no care tracker, uses BALANCED style.

        Args:
            care_tracker: Optional care tracker for style calculation.

        Returns:
            Target form_id, or None if cannot evolve.
        """
        if not self.check_evolution_ready():
            return None

        # Get care style
        if care_tracker:
            care_style = care_tracker.calculate_care_style()
        else:
            care_style = CareStyle.BALANCED

        current_level = self.get_level()

        # Get possible evolutions
        possible = get_possible_evolutions(self.current_form_id)

        if not possible:
            return None

        # Find matching form based on care style
        for form in possible:
            reqs = form.requirements
            if care_style in reqs.care_styles:
                if current_level >= reqs.min_level:
                    return form.id

        # Fallback: return first available form
        for form in possible:
            if current_level >= form.requirements.min_level:
                return form.id

        return None

    def get_care_style(self, care_tracker: CareTracker) -> CareStyle:
        """
        Get the current care style from the care tracker.

        Args:
            care_tracker: The care tracker to analyze.

        Returns:
            The calculated CareStyle.
        """
        return care_tracker.calculate_care_style()

    def execute_evolution(self, new_form_id: str) -> bool:
        """
        Execute an evolution to a new form.

        Updates the current form, stage, and records the evolution
        in history. Grants evolution bonus XP.

        Args:
            new_form_id: The form to evolve into.

        Returns:
            True if evolution was successful.
        """
        new_form = get_form_by_id(new_form_id)
        if not new_form:
            logger.error(f"Cannot evolve: form '{new_form_id}' not found")
            return False

        # Record evolution
        history_entry = EvolutionHistory(
            form_id=new_form_id,
            timestamp=time.time(),
            level=self.get_level(),
        )
        self.evolution_history.append(history_entry)

        # Update current state
        old_form = self.current_form_id
        self.current_form_id = new_form_id
        self.evolution_stage = new_form.stage

        # Grant evolution bonus XP
        self.add_xp(XPSource.EVOLUTION_BONUS)

        logger.info(
            f"Evolution complete: {old_form} -> {new_form_id} "
            f"(Stage: {new_form.stage.name}, Level: {self.get_level()})"
        )

        return True

    def get_evolution_preview(
        self,
        care_tracker: Optional[CareTracker] = None,
    ) -> List[Tuple[EvolutionForm, float]]:
        """
        Get preview of possible evolutions with probability.

        Shows which forms are possible and how likely each is
        based on current care patterns.

        Args:
            care_tracker: Optional care tracker for probabilities.

        Returns:
            List of (form, probability) tuples.
        """
        possible = get_possible_evolutions(self.current_form_id)

        if not possible:
            return []

        if care_tracker:
            care_style = care_tracker.calculate_care_style()
        else:
            care_style = CareStyle.BALANCED

        results: List[Tuple[EvolutionForm, float]] = []
        current_level = self.get_level()

        for form in possible:
            # Check if level requirement met
            if current_level < form.requirements.min_level:
                probability = 0.0
            elif care_style in form.requirements.care_styles:
                probability = 0.8  # High probability for matching style
            elif not form.requirements.care_styles:
                probability = 0.5  # Medium for any-style forms
            else:
                probability = 0.1  # Low for non-matching

            results.append((form, probability))

        return results

    def to_dict(self) -> Dict:
        """
        Convert manager state to dictionary for serialization.

        Returns:
            Dictionary containing all state data.
        """
        return {
            "total_xp": self.total_xp,
            "current_form_id": self.current_form_id,
            "evolution_stage": self.evolution_stage.name,
            "evolution_history": [h.to_dict() for h in self.evolution_history],
            "last_time_xp_update": self._last_time_xp_update,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EvolutionManager":
        """
        Create manager from dictionary.

        Args:
            data: Dictionary containing state data.

        Returns:
            New EvolutionManager instance.
        """
        history_data = data.get("evolution_history", [])
        history = [EvolutionHistory.from_dict(h) for h in history_data]

        manager = cls(
            total_xp=data.get("total_xp", 0),
            current_form_id=data.get("current_form_id", "egg"),
            evolution_history=history,
        )

        # Restore stage
        stage_name = data.get("evolution_stage", "EGG")
        try:
            manager.evolution_stage = EvolutionStage[stage_name]
        except KeyError:
            manager.evolution_stage = EvolutionStage.EGG

        # Restore time tracking
        manager._last_time_xp_update = data.get(
            "last_time_xp_update",
            time.time()
        )

        return manager
