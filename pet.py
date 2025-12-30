"""
Pet class with stats system for the Desktop Virtual Pet.

Manages hunger, happiness, and energy stats with decay over time.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable
import time


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


class Pet:
    """
    Virtual pet with stats, state management, and personality.

    Attributes:
        name: The pet's name.
        stats: Current hunger, happiness, and energy levels.
        state: Current animation/behavior state.
        last_update: Timestamp of last stat update.
    """

    # Decay rates per second
    HUNGER_DECAY_RATE = 0.15  # Loses hunger over time
    HAPPINESS_DECAY_RATE = 0.08  # Happiness decays slowly
    ENERGY_DECAY_RATE = 0.05  # Energy decays when awake
    ENERGY_REGEN_RATE = 0.3  # Energy regenerates when sleeping

    def __init__(
        self,
        name: str = "Blobby",
        hunger: float = 80.0,
        happiness: float = 80.0,
        energy: float = 80.0
    ) -> None:
        """
        Initialize a new pet.

        Args:
            name: Pet's name.
            hunger: Initial hunger level (0-100).
            happiness: Initial happiness level (0-100).
            energy: Initial energy level (0-100).
        """
        self.name = name
        self.stats = PetStats(hunger=hunger, happiness=happiness, energy=energy)
        self.stats.clamp()
        self.state = PetState.IDLE
        self.last_update = time.time()
        self._state_callbacks: list[Callable[[PetState], None]] = []

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

        # Auto-wake if fully rested
        if self.state == PetState.SLEEPING and self.stats.energy >= 100:
            self.set_state(PetState.IDLE)

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
        Feed the pet to increase hunger stat.

        Args:
            amount: How much to increase hunger by.
        """
        self.stats.hunger += amount
        self.stats.happiness += 5  # Eating makes pet a bit happier
        self.stats.clamp()
        self.set_state(PetState.EATING)

    def play(self, amount: float = 20.0) -> None:
        """
        Play with the pet to increase happiness.

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

    def sleep(self) -> None:
        """Put the pet to sleep to regenerate energy."""
        self.set_state(PetState.SLEEPING)

    def wake(self) -> None:
        """Wake the pet up."""
        if self.state == PetState.SLEEPING:
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
        pet = cls(
            name=data.get("name", "Blobby"),
            hunger=data.get("hunger", 80.0),
            happiness=data.get("happiness", 80.0),
            energy=data.get("energy", 80.0)
        )

        # Apply decay based on time since last save
        last_save = data.get("last_save_time", time.time())
        elapsed = time.time() - last_save

        # Cap decay at 24 hours worth
        elapsed = min(elapsed, 86400)

        pet.update(elapsed)

        return pet
