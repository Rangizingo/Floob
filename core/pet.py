"""
Floob 2.0 Pet Core Module.

Contains the Pet class with stats, evolution, and care tracking.
Maintains backwards compatibility with Floob 1.0 save format.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Any
import time
import random

from core.config import Stats, Timing, Evolution as EvolutionConfig, XP
from core.evolution import (
    EvolutionStage,
    CareStyle,
    EvolutionForm,
    EVOLUTION_FORMS,
    check_evolution,
    get_form_by_id,
)
from core.care_tracker import CareTracker


class PetState(Enum):
    """Enumeration of possible pet states."""

    IDLE = auto()
    WALKING = auto()
    EATING = auto()
    PLAYING = auto()
    SLEEPING = auto()
    HAPPY = auto()
    TRICK = auto()
    EVOLVING = auto()  # New state for evolution animation


class Mood(Enum):
    """Pet mood based on overall stats."""

    ECSTATIC = auto()
    HAPPY = auto()
    CONTENT = auto()
    NEUTRAL = auto()
    SAD = auto()
    MISERABLE = auto()


class EarStyle(Enum):
    """Available ear styles for customization (legacy)."""

    CAT = "cat"
    BUNNY = "bunny"
    BEAR = "bear"
    ANTENNA = "antenna"


class TailStyle(Enum):
    """Available tail styles for customization (legacy)."""

    CAT = "cat"
    BUNNY = "bunny"
    DOG = "dog"
    NONE = "none"


class Accessory(Enum):
    """Available accessories for customization."""

    NONE = "none"
    BOW = "bow"
    HAT = "hat"
    GLASSES = "glasses"


# Legacy color palette (kept for backwards compatibility)
COLOR_PALETTE = {
    "pink": "#FFB6C1",
    "blue": "#87CEEB",
    "purple": "#7B68EE",
    "green": "#90EE90",
    "orange": "#FFA07A",
    "yellow": "#FFD700",
}


@dataclass
class PetCustomization:
    """Container for pet customization options (legacy support)."""

    body_color: str = "purple"
    ear_style: EarStyle = EarStyle.ANTENNA
    tail_style: TailStyle = TailStyle.NONE
    accessory: Accessory = Accessory.NONE

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "body_color": self.body_color,
            "ear_style": self.ear_style.value,
            "tail_style": self.tail_style.value,
            "accessory": self.accessory.value,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PetCustomization":
        """Create from dictionary."""
        return cls(
            body_color=data.get("body_color", "purple"),
            ear_style=EarStyle(data.get("ear_style", "antenna")),
            tail_style=TailStyle(data.get("tail_style", "none")),
            accessory=Accessory(data.get("accessory", "none")),
        )


@dataclass
class PetStats:
    """
    Container for pet statistics.

    Attributes:
        hunger: Fullness level (0 = starving, 100 = full).
        happiness: Joy level (0 = miserable, 100 = ecstatic).
        energy: Energy level (0 = exhausted, 100 = energetic).
    """

    hunger: float = Stats.DEFAULT_HUNGER
    happiness: float = Stats.DEFAULT_HAPPINESS
    energy: float = Stats.DEFAULT_ENERGY

    def clamp(self) -> None:
        """Ensure all stats stay within 0-100 range."""
        self.hunger = max(Stats.MIN_STAT, min(Stats.MAX_STAT, self.hunger))
        self.happiness = max(Stats.MIN_STAT, min(Stats.MAX_STAT, self.happiness))
        self.energy = max(Stats.MIN_STAT, min(Stats.MAX_STAT, self.energy))

    def average(self) -> float:
        """Calculate average of all stats."""
        return (self.hunger + self.happiness + self.energy) / 3.0

    def minimum(self) -> float:
        """Get the lowest stat value."""
        return min(self.hunger, self.happiness, self.energy)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
        }


@dataclass
class EvolutionHistoryEntry:
    """
    Records a single evolution event.

    Attributes:
        from_form: Form ID before evolution.
        to_form: Form ID after evolution.
        timestamp: When evolution occurred.
        level_at_evolution: Pet's level at evolution.
    """

    from_form: str
    to_form: str
    timestamp: float
    level_at_evolution: int

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "from_form": self.from_form,
            "to_form": self.to_form,
            "timestamp": self.timestamp,
            "level_at_evolution": self.level_at_evolution,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EvolutionHistoryEntry":
        """Create from dictionary."""
        return cls(
            from_form=data.get("from_form", "egg"),
            to_form=data.get("to_form", "bloblet"),
            timestamp=data.get("timestamp", time.time()),
            level_at_evolution=data.get("level_at_evolution", 1),
        )


class AutonomousAction(Enum):
    """Types of autonomous actions the pet can take."""

    FIND_FOOD = auto()
    TAKE_NAP = auto()
    SELF_PLAY = auto()


@dataclass
class AutoCareCooldowns:
    """Tracks cooldowns for each auto-care action type."""

    feed: float = 0.0
    play: float = 0.0
    sleep_wake_threshold: float = Stats.AUTO_SLEEP_WAKE_THRESHOLD

    def update(self, delta_time: float) -> None:
        """Update cooldown timers."""
        self.feed = max(0.0, self.feed - delta_time)
        self.play = max(0.0, self.play - delta_time)

    def can_auto_feed(self) -> bool:
        """Check if auto-feed is off cooldown."""
        return self.feed <= 0.0

    def can_auto_play(self) -> bool:
        """Check if auto-play is off cooldown."""
        return self.play <= 0.0

    def trigger_feed_cooldown(self) -> None:
        """Start feed cooldown timer."""
        self.feed = Timing.AUTO_FEED_COOLDOWN

    def trigger_play_cooldown(self) -> None:
        """Start play cooldown timer."""
        self.play = Timing.AUTO_PLAY_COOLDOWN

    def reset_feed_cooldown(self) -> None:
        """Reset feed cooldown."""
        self.feed = Timing.AUTO_FEED_COOLDOWN

    def reset_play_cooldown(self) -> None:
        """Reset play cooldown."""
        self.play = Timing.AUTO_PLAY_COOLDOWN


@dataclass
class AutoCareDelayedTrigger:
    """Tracks delayed triggers for auto-care to add natural feel."""

    hunger_triggered_at: Optional[float] = None
    happiness_triggered_at: Optional[float] = None
    energy_triggered_at: Optional[float] = None

    def get_delay(self) -> float:
        """Get a random delay duration."""
        return random.uniform(Timing.AUTO_CARE_DELAY_MIN, Timing.AUTO_CARE_DELAY_MAX)

    def check_hunger_delay(self, current_time: float) -> bool:
        """Check if enough time has passed since hunger threshold was crossed."""
        if self.hunger_triggered_at is None:
            return False
        return current_time - self.hunger_triggered_at >= self.get_delay()

    def check_happiness_delay(self, current_time: float) -> bool:
        """Check if enough time has passed since happiness threshold was crossed."""
        if self.happiness_triggered_at is None:
            return False
        return current_time - self.happiness_triggered_at >= self.get_delay()

    def check_energy_delay(self, current_time: float) -> bool:
        """Check if enough time has passed since energy threshold was crossed."""
        if self.energy_triggered_at is None:
            return False
        return current_time - self.energy_triggered_at >= self.get_delay()

    def reset_hunger(self) -> None:
        """Reset hunger trigger."""
        self.hunger_triggered_at = None

    def reset_happiness(self) -> None:
        """Reset happiness trigger."""
        self.happiness_triggered_at = None

    def reset_energy(self) -> None:
        """Reset energy trigger."""
        self.energy_triggered_at = None


@dataclass
class ThoughtBubble:
    """Represents a thought bubble above the pet."""

    text: str
    icon: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    duration: float = Timing.THOUGHT_BUBBLE_DURATION

    def is_expired(self) -> bool:
        """Check if the thought bubble should disappear."""
        return time.time() - self.start_time >= self.duration

    def get_opacity(self) -> float:
        """Get opacity based on time (fades out near end)."""
        elapsed = time.time() - self.start_time
        fade_start = self.duration - Timing.THOUGHT_BUBBLE_FADE
        if elapsed < fade_start:
            return 1.0
        return max(0.0, (self.duration - elapsed) / Timing.THOUGHT_BUBBLE_FADE)


class Pet:
    """
    Virtual pet with stats, evolution, and personality.

    Floob 2.0 pet with evolution system, care tracking, and
    backwards compatibility with Floob 1.0 saves.

    Attributes:
        name: The pet's name.
        stats: Current hunger, happiness, and energy levels.
        state: Current animation/behavior state.
        experience: Total XP accumulated.
        level: Current level (determines evolution eligibility).
        form_id: Current evolution form identifier.
        evolution_stage: Current evolution stage.
        birth_time: When the pet was created.
        evolution_history: List of past evolutions.
        care_tracker: Tracks care patterns for evolution.
    """

    def __init__(
        self,
        name: str = "Blobby",
        hunger: float = Stats.DEFAULT_HUNGER,
        happiness: float = Stats.DEFAULT_HAPPINESS,
        energy: float = Stats.DEFAULT_ENERGY,
        customization: Optional[PetCustomization] = None,
        creature_type: str = "kibble",
        auto_care_enabled: bool = True,
        # New Floob 2.0 fields
        experience: int = 0,
        level: int = 1,
        form_id: str = "egg",
        birth_time: Optional[float] = None,
        evolution_history: Optional[List[EvolutionHistoryEntry]] = None,
        care_tracker: Optional[CareTracker] = None,
    ) -> None:
        """
        Initialize a new pet.

        Args:
            name: Pet's name.
            hunger: Initial hunger level (0-100).
            happiness: Initial happiness level (0-100).
            energy: Initial energy level (0-100).
            customization: Pet appearance options (legacy).
            creature_type: Type of creature (legacy).
            auto_care_enabled: Whether auto-care is enabled.
            experience: Starting XP.
            level: Starting level.
            form_id: Starting evolution form.
            birth_time: When pet was born.
            evolution_history: Past evolution records.
            care_tracker: Care tracking instance.
        """
        self.name = name
        self.stats = PetStats(hunger=hunger, happiness=happiness, energy=energy)
        self.stats.clamp()
        self.state = PetState.IDLE
        self.customization = customization or PetCustomization()
        self.creature_type = creature_type
        self.last_update = time.time()
        self._state_callbacks: List[Callable[[PetState], None]] = []

        # Evolution system fields
        self.experience = experience
        self.level = level
        self.form_id = form_id
        self.birth_time = birth_time or time.time()
        self.evolution_history = evolution_history or []
        self.care_tracker = care_tracker or CareTracker()

        # XP tracking
        self._last_time_xp_award = time.time()
        self._xp_per_minute_accumulator = 0.0

        # Evolution checking
        self._last_evolution_check = 0.0
        self._evolution_ready = False
        self._pending_evolution: Optional[EvolutionForm] = None

        # Auto-care settings
        self.auto_care_enabled = auto_care_enabled

        # Autonomous behavior state
        self.thought_bubble: Optional[ThoughtBubble] = None
        self.is_performing_autonomous_action = False
        self._last_autonomous_check = time.time()
        self._autonomous_cooldown = 0.0

        # Per-action cooldowns
        self._auto_care_cooldowns = AutoCareCooldowns()

        # Delayed triggers for natural feel
        self._auto_care_triggers = AutoCareDelayedTrigger()

        # Track if currently in auto-sleep
        self._is_auto_sleeping = False

        # Randomized thresholds for natural behavior
        self._current_hunger_threshold = self._get_randomized_threshold(
            Stats.AUTO_HUNGER_THRESHOLD
        )
        self._current_happiness_threshold = self._get_randomized_threshold(
            Stats.AUTO_HAPPINESS_THRESHOLD
        )
        self._current_energy_threshold = self._get_randomized_threshold(
            Stats.AUTO_ENERGY_THRESHOLD
        )

        # Callbacks
        self._on_autonomous_action: Optional[Callable[[AutonomousAction], None]] = None
        self._on_level_up: Optional[Callable[[int], None]] = None
        self._on_evolution_ready: Optional[Callable[[EvolutionForm], None]] = None
        self._on_evolution_complete: Optional[Callable[[EvolutionForm], None]] = None

    # ========================================================================
    # EVOLUTION PROPERTIES
    # ========================================================================

    @property
    def evolution_stage(self) -> EvolutionStage:
        """Get the current evolution stage based on form."""
        form = get_form_by_id(self.form_id)
        if form:
            return form.stage
        return EvolutionStage.EGG

    @property
    def current_form(self) -> Optional[EvolutionForm]:
        """Get the current evolution form object."""
        return get_form_by_id(self.form_id)

    @property
    def care_style(self) -> CareStyle:
        """Get the current care style from tracker."""
        return self.care_tracker.calculate_care_style()

    @property
    def xp_for_next_level(self) -> int:
        """Calculate XP required for next level."""
        base = EvolutionConfig.BASE_XP_PER_LEVEL
        multiplier = EvolutionConfig.XP_LEVEL_MULTIPLIER
        return int(base * (multiplier ** (self.level - 1)))

    @property
    def xp_progress(self) -> float:
        """Get progress toward next level (0.0 to 1.0)."""
        xp_needed = self.xp_for_next_level
        # Calculate XP earned in current level
        xp_for_current = self._get_total_xp_for_level(self.level)
        xp_in_level = self.experience - xp_for_current
        return min(1.0, max(0.0, xp_in_level / xp_needed))

    def _get_total_xp_for_level(self, level: int) -> int:
        """Calculate total XP needed to reach a level."""
        if level <= 1:
            return 0
        total = 0
        base = EvolutionConfig.BASE_XP_PER_LEVEL
        multiplier = EvolutionConfig.XP_LEVEL_MULTIPLIER
        for lvl in range(1, level):
            total += int(base * (multiplier ** (lvl - 1)))
        return total

    # ========================================================================
    # CALLBACK SETTERS
    # ========================================================================

    def set_on_autonomous_action(
        self, callback: Callable[[AutonomousAction], None]
    ) -> None:
        """Set callback for autonomous actions."""
        self._on_autonomous_action = callback

    def set_on_level_up(self, callback: Callable[[int], None]) -> None:
        """Set callback for level up events."""
        self._on_level_up = callback

    def set_on_evolution_ready(
        self, callback: Callable[[EvolutionForm], None]
    ) -> None:
        """Set callback for when evolution becomes available."""
        self._on_evolution_ready = callback

    def set_on_evolution_complete(
        self, callback: Callable[[EvolutionForm], None]
    ) -> None:
        """Set callback for when evolution completes."""
        self._on_evolution_complete = callback

    # ========================================================================
    # XP AND LEVELING
    # ========================================================================

    def add_experience(self, amount: int) -> bool:
        """
        Add experience points and check for level up.

        Args:
            amount: XP to add.

        Returns:
            True if leveled up, False otherwise.
        """
        self.experience += amount
        return self._check_level_up()

    def _check_level_up(self) -> bool:
        """
        Check if pet should level up and apply if so.

        Returns:
            True if leveled up, False otherwise.
        """
        leveled = False
        total_xp_needed = self._get_total_xp_for_level(self.level + 1)

        while self.experience >= total_xp_needed:
            self.level += 1
            leveled = True
            if self._on_level_up:
                self._on_level_up(self.level)
            total_xp_needed = self._get_total_xp_for_level(self.level + 1)

        return leveled

    def _award_time_xp(self, delta_time: float) -> None:
        """Award XP for time alive."""
        self._xp_per_minute_accumulator += delta_time

        # Award XP every 60 seconds
        while self._xp_per_minute_accumulator >= 60.0:
            self._xp_per_minute_accumulator -= 60.0
            self.add_experience(XP.TIME_ALIVE_PER_MINUTE)

    # ========================================================================
    # EVOLUTION
    # ========================================================================

    def check_evolution_ready(self) -> Optional[EvolutionForm]:
        """
        Check if pet is ready to evolve.

        Returns:
            Target EvolutionForm if ready, None otherwise.
        """
        current_time = time.time()

        # Don't check too frequently
        if current_time - self._last_evolution_check < EvolutionConfig.EVOLUTION_CHECK_INTERVAL:
            return self._pending_evolution

        self._last_evolution_check = current_time

        # Check for evolution
        target_form = check_evolution(
            current_form_id=self.form_id,
            level=self.level,
            care_style=self.care_style,
            care_tracker=self.care_tracker,
        )

        if target_form and target_form.id != self.form_id:
            self._evolution_ready = True
            self._pending_evolution = target_form

            if self._on_evolution_ready:
                self._on_evolution_ready(target_form)

        return self._pending_evolution

    def evolve(self, target_form: Optional[EvolutionForm] = None) -> bool:
        """
        Evolve the pet to a new form.

        Args:
            target_form: Form to evolve into (uses pending if not specified).

        Returns:
            True if evolution successful, False otherwise.
        """
        if target_form is None:
            target_form = self._pending_evolution

        if target_form is None:
            return False

        # Record evolution history
        history_entry = EvolutionHistoryEntry(
            from_form=self.form_id,
            to_form=target_form.id,
            timestamp=time.time(),
            level_at_evolution=self.level,
        )
        self.evolution_history.append(history_entry)

        # Update form
        old_form = self.form_id
        self.form_id = target_form.id

        # Award evolution bonus XP
        self.add_experience(XP.EVOLUTION_BONUS)

        # Clear evolution state
        self._evolution_ready = False
        self._pending_evolution = None

        # Trigger callback
        if self._on_evolution_complete:
            self._on_evolution_complete(target_form)

        return True

    # ========================================================================
    # STATS AND MOOD
    # ========================================================================

    def get_mood(self) -> Mood:
        """
        Determine pet's mood based on current stats.

        Returns:
            Current mood enumeration value.
        """
        avg = self.stats.average()
        if avg >= Stats.MOOD_ECSTATIC:
            return Mood.ECSTATIC
        elif avg >= Stats.MOOD_HAPPY:
            return Mood.HAPPY
        elif avg >= Stats.MOOD_CONTENT:
            return Mood.CONTENT
        elif avg >= Stats.MOOD_NEUTRAL:
            return Mood.NEUTRAL
        elif avg >= Stats.MOOD_SAD:
            return Mood.SAD
        else:
            return Mood.MISERABLE

    def is_hungry(self) -> bool:
        """Check if pet is hungry."""
        return self.stats.hunger < Stats.HUNGRY_THRESHOLD

    def is_tired(self) -> bool:
        """Check if pet is tired."""
        return self.stats.energy < Stats.TIRED_THRESHOLD

    def is_sad(self) -> bool:
        """Check if pet is sad."""
        return self.stats.happiness < Stats.SAD_THRESHOLD

    # ========================================================================
    # STATE MANAGEMENT
    # ========================================================================

    def add_state_callback(self, callback: Callable[[PetState], None]) -> None:
        """Register a callback to be called when state changes."""
        self._state_callbacks.append(callback)

    def set_state(self, new_state: PetState) -> None:
        """
        Change the pet's current state.

        Args:
            new_state: The new state to transition to.
        """
        if self.state != new_state:
            self.state = new_state
            for callback in self._state_callbacks:
                callback(new_state)

    # ========================================================================
    # UPDATE LOOP
    # ========================================================================

    def update(self, delta_time: Optional[float] = None) -> None:
        """
        Update pet stats based on elapsed time.

        Args:
            delta_time: Time elapsed in seconds. If None, calculated automatically.
        """
        current_time = time.time()
        if delta_time is None:
            delta_time = current_time - self.last_update
        self.last_update = current_time

        # Apply stat decay
        self.stats.hunger -= Timing.HUNGER_DECAY_RATE * delta_time
        self.stats.happiness -= Timing.HAPPINESS_DECAY_RATE * delta_time

        # Energy behavior depends on state
        if self.state == PetState.SLEEPING:
            self.stats.energy += Timing.ENERGY_REGEN_RATE * delta_time
        else:
            self.stats.energy -= Timing.ENERGY_DECAY_RATE * delta_time

        self.stats.clamp()

        # Record stats snapshot for care tracking
        self.care_tracker.record_snapshot(
            hunger=self.stats.hunger,
            happiness=self.stats.happiness,
            energy=self.stats.energy,
        )

        # Award time-based XP
        self._award_time_xp(delta_time)

        # Auto-wake logic
        if self.state == PetState.SLEEPING:
            if self._is_auto_sleeping:
                if self.stats.energy >= Stats.AUTO_SLEEP_WAKE_THRESHOLD:
                    self._is_auto_sleeping = False
                    self.set_state(PetState.IDLE)
                    self.thought_bubble = ThoughtBubble(
                        text="Feeling rested!",
                        icon="\U0001F31F",
                        duration=2.0,
                    )
                    # Award sleep XP
                    self.add_experience(XP.SLEEP_COMPLETE)
            else:
                if self.stats.energy >= 100:
                    self.set_state(PetState.IDLE)
                    self.add_experience(XP.SLEEP_COMPLETE)

        # Update cooldowns
        if self._autonomous_cooldown > 0:
            self._autonomous_cooldown -= delta_time

        self._auto_care_cooldowns.update(delta_time)
        self._update_auto_care_triggers(current_time)

        # Check for evolution
        self.check_evolution_ready()

    def _get_randomized_threshold(self, base_threshold: float) -> float:
        """Get a threshold with random variance for natural behavior."""
        variance = random.uniform(-Stats.THRESHOLD_VARIANCE, Stats.THRESHOLD_VARIANCE)
        return max(5.0, base_threshold + variance)

    def _refresh_thresholds(self) -> None:
        """Refresh randomized thresholds after an action is taken."""
        self._current_hunger_threshold = self._get_randomized_threshold(
            Stats.AUTO_HUNGER_THRESHOLD
        )
        self._current_happiness_threshold = self._get_randomized_threshold(
            Stats.AUTO_HAPPINESS_THRESHOLD
        )
        self._current_energy_threshold = self._get_randomized_threshold(
            Stats.AUTO_ENERGY_THRESHOLD
        )

    def _update_auto_care_triggers(self, current_time: float) -> None:
        """Update delayed trigger tracking for auto-care."""
        if self.stats.hunger < self._current_hunger_threshold:
            if self._auto_care_triggers.hunger_triggered_at is None:
                self._auto_care_triggers.hunger_triggered_at = current_time
        else:
            self._auto_care_triggers.reset_hunger()

        if self.stats.happiness < self._current_happiness_threshold:
            if self._auto_care_triggers.happiness_triggered_at is None:
                self._auto_care_triggers.happiness_triggered_at = current_time
        else:
            self._auto_care_triggers.reset_happiness()

        if self.stats.energy < self._current_energy_threshold:
            if self._auto_care_triggers.energy_triggered_at is None:
                self._auto_care_triggers.energy_triggered_at = current_time
        else:
            self._auto_care_triggers.reset_energy()

    # ========================================================================
    # AUTO-CARE
    # ========================================================================

    def toggle_auto_care(self) -> bool:
        """Toggle auto-care on/off."""
        self.auto_care_enabled = not self.auto_care_enabled
        return self.auto_care_enabled

    def set_auto_care(self, enabled: bool) -> None:
        """Set auto-care state explicitly."""
        self.auto_care_enabled = enabled

    def autonomous_check(self) -> Optional[AutonomousAction]:
        """Check if pet should take autonomous action."""
        if not self.auto_care_enabled:
            return None

        if self.state not in (PetState.IDLE, PetState.WALKING):
            return None

        if self._autonomous_cooldown > 0:
            return None

        current_time = time.time()

        # Energy check (sleep) - highest priority
        if (
            self.stats.energy < self._current_energy_threshold
            and self._auto_care_triggers.check_energy_delay(current_time)
        ):
            return AutonomousAction.TAKE_NAP

        # Hunger check (eat)
        if (
            self.stats.hunger < self._current_hunger_threshold
            and self._auto_care_cooldowns.can_auto_feed()
            and self._auto_care_triggers.check_hunger_delay(current_time)
        ):
            return AutonomousAction.FIND_FOOD

        # Happiness check (play)
        if (
            self.stats.happiness < self._current_happiness_threshold
            and self._auto_care_cooldowns.can_auto_play()
            and self._auto_care_triggers.check_happiness_delay(current_time)
        ):
            return AutonomousAction.SELF_PLAY

        return None

    def perform_autonomous_action(self, action: AutonomousAction) -> None:
        """Perform an autonomous action."""
        self.is_performing_autonomous_action = True
        self._autonomous_cooldown = 10.0
        self._refresh_thresholds()

        if action == AutonomousAction.FIND_FOOD:
            self._auto_care_cooldowns.trigger_feed_cooldown()
            self._auto_care_triggers.reset_hunger()
            self.thought_bubble = ThoughtBubble(
                text=f"{self.name} is hungry... *munch munch*",
                icon="\U0001F36A",
                duration=2.5,
            )
            self.stats.hunger += Stats.AUTO_FEED_AMOUNT
            self.stats.happiness += 3
            self.stats.clamp()
            self.set_state(PetState.EATING)
            self.care_tracker.record_feed(Stats.AUTO_FEED_AMOUNT)

        elif action == AutonomousAction.TAKE_NAP:
            self._is_auto_sleeping = True
            self._auto_care_triggers.reset_energy()
            self.thought_bubble = ThoughtBubble(
                text=f"{self.name} is sleepy... *yawn*",
                icon="\U0001F4A4",
                duration=2.5,
            )
            self.set_state(PetState.SLEEPING)
            self.care_tracker.record_sleep_start()

        elif action == AutonomousAction.SELF_PLAY:
            self._auto_care_cooldowns.trigger_play_cooldown()
            self._auto_care_triggers.reset_happiness()
            self.thought_bubble = ThoughtBubble(
                text=f"{self.name} wants to play!",
                icon="\U0001F3BE",
                duration=2.5,
            )
            self.stats.happiness += Stats.AUTO_PLAY_AMOUNT
            self.stats.energy -= 5
            self.stats.clamp()
            self.set_state(PetState.PLAYING)
            self.care_tracker.record_play()

        if self._on_autonomous_action:
            self._on_autonomous_action(action)

    def update_thought_bubble(self) -> None:
        """Update thought bubble state, clearing if expired."""
        if self.thought_bubble and self.thought_bubble.is_expired():
            self.thought_bubble = None
            self.is_performing_autonomous_action = False

    # ========================================================================
    # INTERACTIONS (Manual)
    # ========================================================================

    def feed(self, amount: float = Stats.FEED_AMOUNT) -> None:
        """Feed the pet (manual action)."""
        self.stats.hunger += amount
        self.stats.happiness += 5
        self.stats.clamp()
        self.set_state(PetState.EATING)

        self._auto_care_cooldowns.reset_feed_cooldown()
        self._auto_care_triggers.reset_hunger()

        # Track care and XP
        self.care_tracker.record_feed(amount)
        self.add_experience(XP.FEED)

    def play(self, amount: float = Stats.PLAY_HAPPINESS) -> None:
        """Play with the pet (manual action)."""
        if self.stats.energy < 10:
            return

        self.stats.happiness += amount
        self.stats.energy -= Stats.PLAY_ENERGY_COST
        self.stats.hunger -= Stats.PLAY_HUNGER_COST
        self.stats.clamp()
        self.set_state(PetState.PLAYING)

        self._auto_care_cooldowns.reset_play_cooldown()
        self._auto_care_triggers.reset_happiness()

        # Track care and XP
        self.care_tracker.record_play()
        self.add_experience(XP.PLAY)

    def sleep(self) -> None:
        """Put the pet to sleep (manual action)."""
        self._is_auto_sleeping = False
        self._auto_care_triggers.reset_energy()
        self.set_state(PetState.SLEEPING)
        self.care_tracker.record_sleep_start()

    def wake(self) -> None:
        """Wake the pet up."""
        if self.state == PetState.SLEEPING:
            self._is_auto_sleeping = False
            self.set_state(PetState.IDLE)
            self.care_tracker.record_sleep_end()

    def pet(self) -> None:
        """Give the pet attention (clicking on it)."""
        self.stats.happiness += Stats.PET_HAPPINESS
        self.stats.clamp()
        self.set_state(PetState.HAPPY)

        # Track care and XP
        self.care_tracker.record_pet()
        self.add_experience(XP.CLICK)

    def do_trick(self) -> None:
        """Make the pet perform a trick."""
        if self.stats.energy >= Stats.TRICK_ENERGY_COST:
            self.stats.happiness += Stats.TRICK_HAPPINESS
            self.stats.energy -= Stats.TRICK_ENERGY_COST
            self.stats.clamp()
            self.set_state(PetState.TRICK)

            # Track care and XP
            self.care_tracker.record_trick()
            self.add_experience(XP.TRICK)

    def start_walking(self) -> None:
        """Start the pet walking."""
        if self.state not in (PetState.SLEEPING, PetState.EATING, PetState.EVOLVING):
            self.set_state(PetState.WALKING)

    def stop_walking(self) -> None:
        """Stop walking and return to idle."""
        if self.state == PetState.WALKING:
            self.set_state(PetState.IDLE)

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert pet state to dictionary for serialization.

        Includes both legacy fields and new Floob 2.0 fields.

        Returns:
            Dictionary containing pet data.
        """
        return {
            # Legacy fields (backwards compatibility)
            "name": self.name,
            "hunger": self.stats.hunger,
            "happiness": self.stats.happiness,
            "energy": self.stats.energy,
            "customization": self.customization.to_dict(),
            "creature_type": self.creature_type,
            "auto_care_enabled": self.auto_care_enabled,
            "last_save_time": time.time(),
            # Floob 2.0 fields
            "version": "2.0",
            "experience": self.experience,
            "level": self.level,
            "form_id": self.form_id,
            "birth_time": self.birth_time,
            "evolution_history": [e.to_dict() for e in self.evolution_history],
            "care_tracker": self.care_tracker.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pet":
        """
        Create a pet from saved dictionary data.

        Handles migration from Floob 1.0 format.

        Args:
            data: Dictionary containing saved pet data.

        Returns:
            New Pet instance with restored state.
        """
        # Check version for migration
        version = data.get("version", "1.0")

        # Parse customization (legacy)
        customization = None
        if "customization" in data:
            customization = PetCustomization.from_dict(data["customization"])

        # Parse evolution history (2.0)
        evolution_history = []
        if "evolution_history" in data:
            evolution_history = [
                EvolutionHistoryEntry.from_dict(e)
                for e in data["evolution_history"]
            ]

        # Parse care tracker (2.0)
        care_tracker = None
        if "care_tracker" in data:
            care_tracker = CareTracker.from_dict(data["care_tracker"])

        # Determine form_id for migration
        form_id = data.get("form_id", "bloblet")
        if version == "1.0":
            # Migrate old saves: start as baby (bloblet)
            form_id = "bloblet"

        pet = cls(
            name=data.get("name", "Blobby"),
            hunger=data.get("hunger", Stats.DEFAULT_HUNGER),
            happiness=data.get("happiness", Stats.DEFAULT_HAPPINESS),
            energy=data.get("energy", Stats.DEFAULT_ENERGY),
            customization=customization,
            creature_type=data.get("creature_type", "kibble"),
            auto_care_enabled=data.get("auto_care_enabled", True),
            # Floob 2.0 fields
            experience=data.get("experience", 0),
            level=data.get("level", 1),
            form_id=form_id,
            birth_time=data.get("birth_time"),
            evolution_history=evolution_history,
            care_tracker=care_tracker,
        )

        # Apply decay based on time since last save
        last_save = data.get("last_save_time", time.time())
        elapsed = time.time() - last_save
        elapsed = min(elapsed, 86400)  # Cap at 24 hours

        pet.update(elapsed)

        return pet
