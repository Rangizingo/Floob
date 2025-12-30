"""
Pet class with stats system for the Desktop Virtual Pet.

Manages hunger, happiness, and energy stats with decay over time.
Includes customization options and autonomous behavior system.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional
import time
import random


class PetState(Enum):
    """Enumeration of possible pet states."""
    IDLE = auto()
    WALKING = auto()
    EATING = auto()
    PLAYING = auto()
    SLEEPING = auto()
    HAPPY = auto()
    TRICK = auto()


class Mood(Enum):
    """Pet mood based on overall stats."""
    ECSTATIC = auto()
    HAPPY = auto()
    CONTENT = auto()
    NEUTRAL = auto()
    SAD = auto()
    MISERABLE = auto()


class EarStyle(Enum):
    """Available ear styles for customization."""
    CAT = "cat"
    BUNNY = "bunny"
    BEAR = "bear"
    ANTENNA = "antenna"


class TailStyle(Enum):
    """Available tail styles for customization."""
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


# Color palette for body customization
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
    """Container for pet customization options."""
    body_color: str = "purple"
    ear_style: EarStyle = EarStyle.ANTENNA
    tail_style: TailStyle = TailStyle.NONE
    accessory: Accessory = Accessory.NONE

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "body_color": self.body_color,
            "ear_style": self.ear_style.value,
            "tail_style": self.tail_style.value,
            "accessory": self.accessory.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PetCustomization":
        """Create from dictionary."""
        return cls(
            body_color=data.get("body_color", "purple"),
            ear_style=EarStyle(data.get("ear_style", "antenna")),
            tail_style=TailStyle(data.get("tail_style", "none")),
            accessory=Accessory(data.get("accessory", "none")),
        )


@dataclass
class PetStats:
    """Container for pet statistics."""
    hunger: float = 80.0  # 0 = starving, 100 = full
    happiness: float = 80.0  # 0 = miserable, 100 = ecstatic
    energy: float = 80.0  # 0 = exhausted, 100 = energetic

    def clamp(self) -> None:
        """Ensure all stats stay within 0-100 range."""
        self.hunger = max(0.0, min(100.0, self.hunger))
        self.happiness = max(0.0, min(100.0, self.happiness))
        self.energy = max(0.0, min(100.0, self.energy))

    def average(self) -> float:
        """Calculate average of all stats."""
        return (self.hunger + self.happiness + self.energy) / 3.0


class AutonomousAction(Enum):
    """Types of autonomous actions the pet can take."""
    FIND_FOOD = auto()
    TAKE_NAP = auto()
    SELF_PLAY = auto()


@dataclass
class AutoCareCooldowns:
    """Tracks cooldowns for each auto-care action type."""
    feed: float = 0.0  # Time remaining until can auto-feed again
    play: float = 0.0  # Time remaining until can auto-play again
    sleep_wake_threshold: float = 80.0  # Energy level required to wake from auto-sleep

    # Cooldown durations in seconds
    FEED_COOLDOWN: float = 30.0
    PLAY_COOLDOWN: float = 45.0

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
        self.feed = self.FEED_COOLDOWN

    def trigger_play_cooldown(self) -> None:
        """Start play cooldown timer."""
        self.play = self.PLAY_COOLDOWN

    def reset_feed_cooldown(self) -> None:
        """Reset feed cooldown (e.g., after manual feeding)."""
        self.feed = self.FEED_COOLDOWN

    def reset_play_cooldown(self) -> None:
        """Reset play cooldown (e.g., after manual playing)."""
        self.play = self.PLAY_COOLDOWN


@dataclass
class AutoCareDelayedTrigger:
    """Tracks delayed triggers for auto-care to add natural feel."""
    hunger_triggered_at: Optional[float] = None
    happiness_triggered_at: Optional[float] = None
    energy_triggered_at: Optional[float] = None

    # Random delay range before acting (seconds)
    MIN_DELAY: float = 2.0
    MAX_DELAY: float = 5.0

    def get_delay(self) -> float:
        """Get a random delay duration."""
        return random.uniform(self.MIN_DELAY, self.MAX_DELAY)

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
    icon: Optional[str] = None  # Unicode icon
    start_time: float = field(default_factory=time.time)
    duration: float = 3.0  # seconds

    def is_expired(self) -> bool:
        """Check if the thought bubble should disappear."""
        return time.time() - self.start_time >= self.duration

    def get_opacity(self) -> float:
        """Get opacity based on time (fades out near end)."""
        elapsed = time.time() - self.start_time
        if elapsed < self.duration - 0.5:
            return 1.0
        return max(0.0, (self.duration - elapsed) / 0.5)


class Pet:
    """
    Virtual pet with stats, state management, and personality.

    Attributes:
        name: The pet's name.
        stats: Current hunger, happiness, and energy levels.
        state: Current animation/behavior state.
        customization: Pet appearance customization.
        creature_type: Type of creature (e.g., "sparkit", "fumewl", etc.).
        last_update: Timestamp of last stat update.
    """

    # Decay rates per second
    HUNGER_DECAY_RATE = 0.15  # Loses hunger over time
    HAPPINESS_DECAY_RATE = 0.08  # Happiness decays slowly
    ENERGY_DECAY_RATE = 0.05  # Energy decays when awake
    ENERGY_REGEN_RATE = 0.3  # Energy regenerates when sleeping

    # Autonomous action thresholds (base values, randomness applied)
    AUTO_HUNGER_THRESHOLD = 30
    AUTO_ENERGY_THRESHOLD = 20
    AUTO_HAPPINESS_THRESHOLD = 25

    # Threshold randomness range (+/- this value)
    THRESHOLD_VARIANCE = 5

    # Autonomous action restore amounts (less than manual)
    AUTO_FEED_AMOUNT = 15  # Manual is 25
    AUTO_ENERGY_AMOUNT = 20  # Manual restores more
    AUTO_PLAY_AMOUNT = 12  # Manual is 20

    # Auto-sleep wake threshold
    AUTO_SLEEP_WAKE_THRESHOLD = 80

    def __init__(
        self,
        name: str = "Blobby",
        hunger: float = 80.0,
        happiness: float = 80.0,
        energy: float = 80.0,
        customization: Optional[PetCustomization] = None,
        creature_type: str = "kibble",
        auto_care_enabled: bool = True
    ) -> None:
        """
        Initialize a new pet.

        Args:
            name: Pet's name.
            hunger: Initial hunger level (0-100).
            happiness: Initial happiness level (0-100).
            energy: Initial energy level (0-100).
            customization: Pet appearance options.
            creature_type: Type of creature.
            auto_care_enabled: Whether auto-care is enabled.
        """
        self.name = name
        self.stats = PetStats(hunger=hunger, happiness=happiness, energy=energy)
        self.stats.clamp()
        self.state = PetState.IDLE
        self.customization = customization or PetCustomization()
        self.creature_type = creature_type
        self.last_update = time.time()
        self._state_callbacks: list[Callable[[PetState], None]] = []

        # Auto-care settings
        self.auto_care_enabled = auto_care_enabled

        # Autonomous behavior state
        self.thought_bubble: Optional[ThoughtBubble] = None
        self.is_performing_autonomous_action = False
        self._last_autonomous_check = time.time()
        self._autonomous_cooldown = 0.0  # Cooldown between autonomous actions

        # Per-action cooldowns
        self._auto_care_cooldowns = AutoCareCooldowns()

        # Delayed triggers for natural feel
        self._auto_care_triggers = AutoCareDelayedTrigger()

        # Track if currently in auto-sleep (vs manual sleep)
        self._is_auto_sleeping = False

        # Randomized thresholds for more natural behavior
        self._current_hunger_threshold = self._get_randomized_threshold(
            self.AUTO_HUNGER_THRESHOLD
        )
        self._current_happiness_threshold = self._get_randomized_threshold(
            self.AUTO_HAPPINESS_THRESHOLD
        )
        self._current_energy_threshold = self._get_randomized_threshold(
            self.AUTO_ENERGY_THRESHOLD
        )

        # Callbacks for autonomous actions
        self._on_autonomous_action: Optional[Callable[[AutonomousAction], None]] = None

    def set_on_autonomous_action(self, callback: Callable[[AutonomousAction], None]) -> None:
        """Set callback for autonomous actions."""
        self._on_autonomous_action = callback

    def _get_randomized_threshold(self, base_threshold: float) -> float:
        """
        Get a threshold with random variance for natural behavior.

        Args:
            base_threshold: The base threshold value.

        Returns:
            Threshold with random variance applied.
        """
        variance = random.uniform(-self.THRESHOLD_VARIANCE, self.THRESHOLD_VARIANCE)
        return max(5.0, base_threshold + variance)

    def _refresh_thresholds(self) -> None:
        """Refresh randomized thresholds after an action is taken."""
        self._current_hunger_threshold = self._get_randomized_threshold(
            self.AUTO_HUNGER_THRESHOLD
        )
        self._current_happiness_threshold = self._get_randomized_threshold(
            self.AUTO_HAPPINESS_THRESHOLD
        )
        self._current_energy_threshold = self._get_randomized_threshold(
            self.AUTO_ENERGY_THRESHOLD
        )

    def toggle_auto_care(self) -> bool:
        """
        Toggle auto-care on/off.

        Returns:
            New auto-care state (True = enabled).
        """
        self.auto_care_enabled = not self.auto_care_enabled
        return self.auto_care_enabled

    def set_auto_care(self, enabled: bool) -> None:
        """
        Set auto-care state explicitly.

        Args:
            enabled: Whether auto-care should be enabled.
        """
        self.auto_care_enabled = enabled

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

    def update(self, delta_time: float | None = None) -> None:
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
        self.stats.hunger -= self.HUNGER_DECAY_RATE * delta_time
        self.stats.happiness -= self.HAPPINESS_DECAY_RATE * delta_time

        # Energy behavior depends on state
        if self.state == PetState.SLEEPING:
            self.stats.energy += self.ENERGY_REGEN_RATE * delta_time
        else:
            self.stats.energy -= self.ENERGY_DECAY_RATE * delta_time

        self.stats.clamp()

        # Auto-wake logic: different thresholds for auto-sleep vs manual sleep
        if self.state == PetState.SLEEPING:
            if self._is_auto_sleeping:
                # Auto-sleep: wake when energy > 80
                if self.stats.energy >= self.AUTO_SLEEP_WAKE_THRESHOLD:
                    self._is_auto_sleeping = False
                    self.set_state(PetState.IDLE)
                    self.thought_bubble = ThoughtBubble(
                        text="Feeling rested!",
                        icon="\U0001F31F",  # Star
                        duration=2.0
                    )
            else:
                # Manual sleep: wake when fully rested (100)
                if self.stats.energy >= 100:
                    self.set_state(PetState.IDLE)

        # Update autonomous cooldowns
        if self._autonomous_cooldown > 0:
            self._autonomous_cooldown -= delta_time

        # Update per-action cooldowns
        self._auto_care_cooldowns.update(delta_time)

        # Update delayed triggers based on current stats
        self._update_auto_care_triggers(current_time)

    def _update_auto_care_triggers(self, current_time: float) -> None:
        """
        Update delayed trigger tracking for auto-care.

        This tracks when stats cross thresholds so we can add a delay
        before the pet "decides" to take action.

        Args:
            current_time: Current timestamp.
        """
        # Check hunger threshold
        if self.stats.hunger < self._current_hunger_threshold:
            if self._auto_care_triggers.hunger_triggered_at is None:
                self._auto_care_triggers.hunger_triggered_at = current_time
        else:
            self._auto_care_triggers.reset_hunger()

        # Check happiness threshold
        if self.stats.happiness < self._current_happiness_threshold:
            if self._auto_care_triggers.happiness_triggered_at is None:
                self._auto_care_triggers.happiness_triggered_at = current_time
        else:
            self._auto_care_triggers.reset_happiness()

        # Check energy threshold
        if self.stats.energy < self._current_energy_threshold:
            if self._auto_care_triggers.energy_triggered_at is None:
                self._auto_care_triggers.energy_triggered_at = current_time
        else:
            self._auto_care_triggers.reset_energy()

    def autonomous_check(self) -> Optional[AutonomousAction]:
        """
        Check if pet should take autonomous action.

        Returns:
            The autonomous action to take, or None if no action needed.
        """
        # Auto-care disabled
        if not self.auto_care_enabled:
            return None

        # Don't interrupt if already doing something
        if self.state not in (PetState.IDLE, PetState.WALKING):
            return None

        # Don't act if on general cooldown
        if self._autonomous_cooldown > 0:
            return None

        current_time = time.time()

        # Check stats in priority order with delays and per-action cooldowns

        # Energy check (sleep) - highest priority
        if (self.stats.energy < self._current_energy_threshold and
                self._auto_care_triggers.check_energy_delay(current_time)):
            return AutonomousAction.TAKE_NAP

        # Hunger check (eat) - second priority
        if (self.stats.hunger < self._current_hunger_threshold and
                self._auto_care_cooldowns.can_auto_feed() and
                self._auto_care_triggers.check_hunger_delay(current_time)):
            return AutonomousAction.FIND_FOOD

        # Happiness check (play) - third priority
        if (self.stats.happiness < self._current_happiness_threshold and
                self._auto_care_cooldowns.can_auto_play() and
                self._auto_care_triggers.check_happiness_delay(current_time)):
            return AutonomousAction.SELF_PLAY

        return None

    def perform_autonomous_action(self, action: AutonomousAction) -> None:
        """
        Perform an autonomous action.

        Args:
            action: The autonomous action to perform.
        """
        self.is_performing_autonomous_action = True
        self._autonomous_cooldown = 10.0  # Short general cooldown between any auto actions

        # Refresh thresholds for next time (adds variety)
        self._refresh_thresholds()

        if action == AutonomousAction.FIND_FOOD:
            # Trigger feed-specific cooldown
            self._auto_care_cooldowns.trigger_feed_cooldown()
            self._auto_care_triggers.reset_hunger()

            self.thought_bubble = ThoughtBubble(
                text=f"{self.name} is hungry... *munch munch*",
                icon="\U0001F36A",  # Cookie
                duration=2.5
            )
            self.stats.hunger += self.AUTO_FEED_AMOUNT
            self.stats.happiness += 3
            self.stats.clamp()
            self.set_state(PetState.EATING)

        elif action == AutonomousAction.TAKE_NAP:
            # Mark as auto-sleep so we use different wake threshold
            self._is_auto_sleeping = True
            self._auto_care_triggers.reset_energy()

            self.thought_bubble = ThoughtBubble(
                text=f"{self.name} is sleepy... *yawn*",
                icon="\U0001F4A4",  # ZZZ
                duration=2.5
            )
            self.set_state(PetState.SLEEPING)

        elif action == AutonomousAction.SELF_PLAY:
            # Trigger play-specific cooldown
            self._auto_care_cooldowns.trigger_play_cooldown()
            self._auto_care_triggers.reset_happiness()

            self.thought_bubble = ThoughtBubble(
                text=f"{self.name} wants to play!",
                icon="\U0001F3BE",  # Tennis ball
                duration=2.5
            )
            self.stats.happiness += self.AUTO_PLAY_AMOUNT
            self.stats.energy -= 5
            self.stats.clamp()
            self.set_state(PetState.PLAYING)

        if self._on_autonomous_action:
            self._on_autonomous_action(action)

    def update_thought_bubble(self) -> None:
        """Update thought bubble state, clearing if expired."""
        if self.thought_bubble and self.thought_bubble.is_expired():
            self.thought_bubble = None
            self.is_performing_autonomous_action = False

    def get_mood(self) -> Mood:
        """
        Determine pet's mood based on current stats.

        Returns:
            Current mood enumeration value.
        """
        avg = self.stats.average()
        if avg >= 90:
            return Mood.ECSTATIC
        elif avg >= 70:
            return Mood.HAPPY
        elif avg >= 50:
            return Mood.CONTENT
        elif avg >= 30:
            return Mood.NEUTRAL
        elif avg >= 15:
            return Mood.SAD
        else:
            return Mood.MISERABLE

    def feed(self, amount: float = 25.0) -> None:
        """
        Feed the pet to increase hunger stat (manual action).

        Args:
            amount: How much to increase hunger by.
        """
        self.stats.hunger += amount
        self.stats.happiness += 5  # Eating makes pet a bit happier
        self.stats.clamp()
        self.set_state(PetState.EATING)

        # Reset auto-care cooldown for feeding (manual action resets it)
        self._auto_care_cooldowns.reset_feed_cooldown()
        self._auto_care_triggers.reset_hunger()

    def play(self, amount: float = 20.0) -> None:
        """
        Play with the pet to increase happiness (manual action).

        Args:
            amount: How much to increase happiness by.
        """
        if self.stats.energy < 10:
            # Too tired to play
            return

        self.stats.happiness += amount
        self.stats.energy -= 10  # Playing uses energy
        self.stats.hunger -= 5  # Playing makes pet hungry
        self.stats.clamp()
        self.set_state(PetState.PLAYING)

        # Reset auto-care cooldown for playing (manual action resets it)
        self._auto_care_cooldowns.reset_play_cooldown()
        self._auto_care_triggers.reset_happiness()

    def sleep(self) -> None:
        """Put the pet to sleep to regenerate energy (manual action)."""
        self._is_auto_sleeping = False  # Manual sleep, will wake at 100 energy
        self._auto_care_triggers.reset_energy()
        self.set_state(PetState.SLEEPING)

    def wake(self) -> None:
        """Wake the pet up."""
        if self.state == PetState.SLEEPING:
            self._is_auto_sleeping = False
            self.set_state(PetState.IDLE)

    def pet(self) -> None:
        """Give the pet attention (clicking on it)."""
        self.stats.happiness += 3
        self.stats.clamp()
        self.set_state(PetState.HAPPY)

    def do_trick(self) -> None:
        """Make the pet perform a trick."""
        if self.stats.energy >= 5:
            self.stats.happiness += 10
            self.stats.energy -= 5
            self.stats.clamp()
            self.set_state(PetState.TRICK)

    def start_walking(self) -> None:
        """Start the pet walking."""
        if self.state not in (PetState.SLEEPING, PetState.EATING):
            self.set_state(PetState.WALKING)

    def stop_walking(self) -> None:
        """Stop walking and return to idle."""
        if self.state == PetState.WALKING:
            self.set_state(PetState.IDLE)

    def is_hungry(self) -> bool:
        """Check if pet is hungry (hunger below 30)."""
        return self.stats.hunger < 30

    def is_tired(self) -> bool:
        """Check if pet is tired (energy below 30)."""
        return self.stats.energy < 30

    def is_sad(self) -> bool:
        """Check if pet is sad (happiness below 30)."""
        return self.stats.happiness < 30

    def to_dict(self) -> dict:
        """
        Convert pet state to dictionary for serialization.

        Returns:
            Dictionary containing pet data.
        """
        return {
            "name": self.name,
            "hunger": self.stats.hunger,
            "happiness": self.stats.happiness,
            "energy": self.stats.energy,
            "customization": self.customization.to_dict(),
            "creature_type": self.creature_type,
            "auto_care_enabled": self.auto_care_enabled,
            "last_save_time": time.time()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """
        Create a pet from saved dictionary data.

        Args:
            data: Dictionary containing saved pet data.

        Returns:
            New Pet instance with restored state.
        """
        customization = None
        if "customization" in data:
            customization = PetCustomization.from_dict(data["customization"])

        pet = cls(
            name=data.get("name", "Blobby"),
            hunger=data.get("hunger", 80.0),
            happiness=data.get("happiness", 80.0),
            energy=data.get("energy", 80.0),
            customization=customization,
            creature_type=data.get("creature_type", "kibble"),
            auto_care_enabled=data.get("auto_care_enabled", True)
        )

        # Apply decay based on time since last save
        last_save = data.get("last_save_time", time.time())
        elapsed = time.time() - last_save

        # Cap decay at 24 hours worth
        elapsed = min(elapsed, 86400)

        pet.update(elapsed)

        return pet
