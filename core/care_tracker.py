"""
Floob 2.0 Care Tracker Module.

Tracks care patterns over time to calculate care style for evolution.
Records feeding, playing, sleeping, and neglect periods.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import time

from core.config import Evolution as EvolutionConfig, Stats


class CareEventType(Enum):
    """Types of care events that can be tracked."""

    FEED = auto()
    PLAY = auto()
    SLEEP_START = auto()
    SLEEP_END = auto()
    PET = auto()  # Click attention
    TRICK = auto()
    NEGLECT_START = auto()  # When any stat drops below threshold
    NEGLECT_END = auto()  # When stats recover
    CRITICAL_NEGLECT = auto()  # All stats below critical threshold


@dataclass
class CareEvent:
    """
    Represents a single care event.

    Attributes:
        event_type: Type of care event.
        timestamp: When the event occurred (Unix timestamp).
        details: Optional additional data about the event.
    """

    event_type: CareEventType
    timestamp: float = field(default_factory=time.time)
    details: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "event_type": self.event_type.name,
            "timestamp": self.timestamp,
            "details": self.details,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CareEvent":
        """Create from dictionary."""
        return cls(
            event_type=CareEventType[data["event_type"]],
            timestamp=data.get("timestamp", time.time()),
            details=data.get("details"),
        )


@dataclass
class StatSnapshot:
    """
    Snapshot of pet stats at a point in time.

    Used for tracking stat trends and neglect detection.
    """

    hunger: float
    happiness: float
    energy: float
    timestamp: float = field(default_factory=time.time)

    @property
    def average(self) -> float:
        """Calculate average of all stats."""
        return (self.hunger + self.happiness + self.energy) / 3.0

    @property
    def minimum(self) -> float:
        """Get the lowest stat value."""
        return min(self.hunger, self.happiness, self.energy)

    def is_neglected(self) -> bool:
        """Check if any stat is below neglect threshold."""
        threshold = EvolutionConfig.LOW_STAT_THRESHOLD
        return self.minimum < threshold

    def is_critical(self) -> bool:
        """Check if all stats are critically low."""
        threshold = EvolutionConfig.NEGLECT_THRESHOLD
        return (
            self.hunger < threshold
            and self.happiness < threshold
            and self.energy < threshold
        )

    def is_perfect(self, min_stat: float = 80.0) -> bool:
        """Check if all stats are above the 'perfect' threshold."""
        return (
            self.hunger >= min_stat
            and self.happiness >= min_stat
            and self.energy >= min_stat
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "StatSnapshot":
        """Create from dictionary."""
        return cls(
            hunger=data.get("hunger", 80.0),
            happiness=data.get("happiness", 80.0),
            energy=data.get("energy", 80.0),
            timestamp=data.get("timestamp", time.time()),
        )


class CareTracker:
    """
    Tracks pet care patterns for evolution calculation.

    Records care events, stat snapshots, and calculates care style
    based on historical patterns.

    Attributes:
        events: List of care events.
        snapshots: Periodic stat snapshots.
        daily_stats: Aggregated daily statistics.
    """

    # Snapshot interval in seconds (every 5 minutes)
    SNAPSHOT_INTERVAL: float = 300.0

    # Maximum events to keep (prevent memory bloat)
    MAX_EVENTS: int = 1000

    # Maximum snapshots to keep
    MAX_SNAPSHOTS: int = 288  # 24 hours at 5-min intervals

    def __init__(self) -> None:
        """Initialize the care tracker."""
        self.events: List[CareEvent] = []
        self.snapshots: List[StatSnapshot] = []
        self.daily_stats: Dict[str, Dict] = {}  # date string -> stats
        self._last_snapshot_time: float = 0.0
        self._is_neglected: bool = False
        self._was_critical: bool = False
        self._perfect_care_days: int = 0
        self._last_perfect_check_date: Optional[str] = None

    def record_event(
        self,
        event_type: CareEventType,
        details: Optional[Dict] = None,
    ) -> None:
        """
        Record a care event.

        Args:
            event_type: Type of care event.
            details: Optional additional data.
        """
        event = CareEvent(
            event_type=event_type,
            timestamp=time.time(),
            details=details,
        )
        self.events.append(event)

        # Trim old events if over limit
        if len(self.events) > self.MAX_EVENTS:
            self.events = self.events[-self.MAX_EVENTS:]

        # Update daily aggregates
        self._update_daily_stats(event)

    def record_feed(self, amount: float = 25.0) -> None:
        """Record a feeding event."""
        self.record_event(CareEventType.FEED, {"amount": amount})

    def record_play(self, duration: float = 0.0) -> None:
        """Record a play session."""
        self.record_event(CareEventType.PLAY, {"duration": duration})

    def record_sleep_start(self) -> None:
        """Record start of sleep."""
        self.record_event(CareEventType.SLEEP_START)

    def record_sleep_end(self, duration: float = 0.0) -> None:
        """Record end of sleep with duration."""
        self.record_event(CareEventType.SLEEP_END, {"duration": duration})

    def record_pet(self) -> None:
        """Record a petting/attention event."""
        self.record_event(CareEventType.PET)

    def record_trick(self) -> None:
        """Record a trick performance."""
        self.record_event(CareEventType.TRICK)

    def record_snapshot(
        self,
        hunger: float,
        happiness: float,
        energy: float,
        force: bool = False,
    ) -> None:
        """
        Record a stat snapshot if enough time has passed.

        Args:
            hunger: Current hunger stat.
            happiness: Current happiness stat.
            energy: Current energy stat.
            force: Force snapshot regardless of timing.
        """
        current_time = time.time()

        # Only snapshot at intervals (unless forced)
        if not force and current_time - self._last_snapshot_time < self.SNAPSHOT_INTERVAL:
            return

        snapshot = StatSnapshot(
            hunger=hunger,
            happiness=happiness,
            energy=energy,
            timestamp=current_time,
        )
        self.snapshots.append(snapshot)
        self._last_snapshot_time = current_time

        # Trim old snapshots
        if len(self.snapshots) > self.MAX_SNAPSHOTS:
            self.snapshots = self.snapshots[-self.MAX_SNAPSHOTS:]

        # Track neglect states
        self._update_neglect_tracking(snapshot)

        # Update perfect care tracking
        self._update_perfect_care_tracking(snapshot)

    def _update_neglect_tracking(self, snapshot: StatSnapshot) -> None:
        """Update neglect state based on snapshot."""
        was_neglected = self._is_neglected

        if snapshot.is_critical():
            self._was_critical = True
            if not self._is_neglected:
                self.record_event(CareEventType.CRITICAL_NEGLECT)
                self._is_neglected = True

        elif snapshot.is_neglected():
            if not self._is_neglected:
                self.record_event(CareEventType.NEGLECT_START)
                self._is_neglected = True

        else:
            if self._is_neglected:
                self.record_event(CareEventType.NEGLECT_END)
                self._is_neglected = False

    def _update_perfect_care_tracking(self, snapshot: StatSnapshot) -> None:
        """Update perfect care day streak."""
        today = date.today().isoformat()

        # Only check once per day
        if self._last_perfect_check_date == today:
            return

        if snapshot.is_perfect(EvolutionConfig.GOLDEN_MIN_STAT):
            # Check if yesterday was also perfect (streak continues)
            yesterday = self._last_perfect_check_date
            if yesterday:
                # Calculate days between
                try:
                    yesterday_date = date.fromisoformat(yesterday)
                    today_date = date.today()
                    diff = (today_date - yesterday_date).days
                    if diff == 1:
                        self._perfect_care_days += 1
                    else:
                        self._perfect_care_days = 1
                except ValueError:
                    self._perfect_care_days = 1
            else:
                self._perfect_care_days = 1
        else:
            self._perfect_care_days = 0

        self._last_perfect_check_date = today

    def _update_daily_stats(self, event: CareEvent) -> None:
        """Update daily aggregate statistics."""
        date_key = datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d")

        if date_key not in self.daily_stats:
            self.daily_stats[date_key] = {
                "feed_count": 0,
                "play_count": 0,
                "pet_count": 0,
                "trick_count": 0,
                "sleep_count": 0,
                "neglect_periods": 0,
            }

        stats = self.daily_stats[date_key]

        if event.event_type == CareEventType.FEED:
            stats["feed_count"] += 1
        elif event.event_type == CareEventType.PLAY:
            stats["play_count"] += 1
        elif event.event_type == CareEventType.PET:
            stats["pet_count"] += 1
        elif event.event_type == CareEventType.TRICK:
            stats["trick_count"] += 1
        elif event.event_type == CareEventType.SLEEP_START:
            stats["sleep_count"] += 1
        elif event.event_type == CareEventType.NEGLECT_START:
            stats["neglect_periods"] += 1

    def get_events_in_window(
        self,
        window_seconds: float = 3600.0,
        event_type: Optional[CareEventType] = None,
    ) -> List[CareEvent]:
        """
        Get events within a time window.

        Args:
            window_seconds: How far back to look.
            event_type: Optional filter for specific event type.

        Returns:
            List of matching events.
        """
        cutoff = time.time() - window_seconds
        events = [e for e in self.events if e.timestamp >= cutoff]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events

    def get_feed_frequency(self, hours: float = 1.0) -> float:
        """
        Get feeding frequency (feeds per hour).

        Args:
            hours: Time window to analyze.

        Returns:
            Feeds per hour.
        """
        events = self.get_events_in_window(
            window_seconds=hours * 3600,
            event_type=CareEventType.FEED,
        )
        return len(events) / hours if hours > 0 else 0.0

    def get_play_frequency(self, hours: float = 1.0) -> float:
        """
        Get play frequency (plays per hour).

        Args:
            hours: Time window to analyze.

        Returns:
            Plays per hour.
        """
        events = self.get_events_in_window(
            window_seconds=hours * 3600,
            event_type=CareEventType.PLAY,
        )
        return len(events) / hours if hours > 0 else 0.0

    def get_attention_frequency(self, hours: float = 1.0) -> float:
        """
        Get total attention frequency (all interaction events per hour).

        Args:
            hours: Time window to analyze.

        Returns:
            Interactions per hour.
        """
        window = hours * 3600
        events = self.get_events_in_window(window_seconds=window)
        interaction_types = {
            CareEventType.FEED,
            CareEventType.PLAY,
            CareEventType.PET,
            CareEventType.TRICK,
        }
        interactions = [e for e in events if e.event_type in interaction_types]
        return len(interactions) / hours if hours > 0 else 0.0

    def get_average_stats(self, hours: float = 1.0) -> Optional[Tuple[float, float, float]]:
        """
        Get average stats over a time window.

        Args:
            hours: Time window to analyze.

        Returns:
            Tuple of (avg_hunger, avg_happiness, avg_energy) or None if no data.
        """
        cutoff = time.time() - (hours * 3600)
        recent = [s for s in self.snapshots if s.timestamp >= cutoff]

        if not recent:
            return None

        avg_hunger = sum(s.hunger for s in recent) / len(recent)
        avg_happiness = sum(s.happiness for s in recent) / len(recent)
        avg_energy = sum(s.energy for s in recent) / len(recent)

        return (avg_hunger, avg_happiness, avg_energy)

    def calculate_care_style(self) -> "CareStyle":
        """
        Calculate the current care style based on patterns.

        Analyzes feeding frequency, play frequency, stat averages,
        and neglect periods to determine care style.

        Returns:
            The calculated CareStyle.
        """
        from core.evolution import CareStyle

        # Get metrics over the tracking window
        window_hours = EvolutionConfig.CARE_TRACKING_WINDOW / 3600

        feed_freq = self.get_feed_frequency(window_hours)
        play_freq = self.get_play_frequency(window_hours)
        attention_freq = self.get_attention_frequency(window_hours)
        avg_stats = self.get_average_stats(window_hours)

        # Check for neglect
        neglect_events = self.get_events_in_window(
            window_seconds=EvolutionConfig.CARE_TRACKING_WINDOW,
            event_type=CareEventType.NEGLECT_START,
        )

        # Neglected: multiple neglect events or currently neglected
        if len(neglect_events) >= 3 or self._is_neglected:
            return CareStyle.NEGLECTED

        if avg_stats is None:
            return CareStyle.BALANCED

        avg_hunger, avg_happiness, avg_energy = avg_stats
        overall_avg = (avg_hunger + avg_happiness + avg_energy) / 3

        # Spoiled: very high stats + high feed frequency
        if overall_avg > 85 and feed_freq > 2.0:
            return CareStyle.SPOILED

        # Playful: high play frequency, happiness is highest stat
        if play_freq > 1.5 and avg_happiness >= avg_hunger and avg_happiness >= avg_energy:
            return CareStyle.PLAYFUL

        # Pampered: high attention, happiness and energy high
        if attention_freq > 4.0 and avg_happiness > 70 and avg_energy > 70:
            return CareStyle.PAMPERED

        # Default to balanced
        return CareStyle.BALANCED

    def check_perfect_care_streak(self, days: int = 7, min_stat: float = 80.0) -> bool:
        """
        Check if there's been a streak of perfect care days.

        Args:
            days: Required number of consecutive days.
            min_stat: Minimum stat value for 'perfect'.

        Returns:
            True if streak requirement met.
        """
        return self._perfect_care_days >= days

    def was_critically_neglected(self) -> bool:
        """
        Check if the pet was ever critically neglected.

        Returns:
            True if critical neglect was ever recorded.
        """
        return self._was_critical

    @property
    def consecutive_perfect_days(self) -> int:
        """
        Get the number of consecutive days with perfect care.

        Returns:
            Number of consecutive perfect care days.
        """
        return self._perfect_care_days

    @property
    def was_revived(self) -> bool:
        """
        Check if the pet was revived from critical state.

        Returns:
            True if pet was ever in critical state and recovered.
        """
        return self._was_critical

    def mark_revived(self) -> None:
        """
        Mark the pet as having been revived from critical state.

        Call this when the pet recovers from all stats being critically low.
        """
        self._was_critical = True

    def reset_perfect_care_streak(self) -> None:
        """
        Reset the perfect care streak counter.

        Call this when care quality drops below perfect threshold.
        """
        self._perfect_care_days = 0

    def is_special_date(self) -> bool:
        """
        Check if today is a special date for rainbow evolution.

        Currently checks for:
        - New Year's Day (Jan 1)
        - Valentine's Day (Feb 14)
        - Halloween (Oct 31)
        - Christmas (Dec 25)

        Returns:
            True if today is a special date.
        """
        today = date.today()
        special_dates = [
            (1, 1),    # New Year
            (2, 14),   # Valentine's
            (10, 31),  # Halloween
            (12, 25),  # Christmas
        ]
        return (today.month, today.day) in special_dates

    def get_care_summary(self) -> Dict:
        """
        Get a summary of care patterns.

        Returns:
            Dict with care statistics.
        """
        from core.evolution import CareStyle

        window_hours = 24.0  # Last 24 hours

        return {
            "care_style": self.calculate_care_style().name,
            "feed_frequency": self.get_feed_frequency(window_hours),
            "play_frequency": self.get_play_frequency(window_hours),
            "attention_frequency": self.get_attention_frequency(window_hours),
            "average_stats": self.get_average_stats(window_hours),
            "is_neglected": self._is_neglected,
            "was_critical": self._was_critical,
            "perfect_care_days": self._perfect_care_days,
            "total_events": len(self.events),
            "total_snapshots": len(self.snapshots),
        }

    def to_dict(self) -> Dict:
        """
        Convert tracker state to dictionary for serialization.

        Returns:
            Dict containing all tracker data.
        """
        return {
            "events": [e.to_dict() for e in self.events[-500:]],  # Keep last 500
            "snapshots": [s.to_dict() for s in self.snapshots],
            "daily_stats": self.daily_stats,
            "is_neglected": self._is_neglected,
            "was_critical": self._was_critical,
            "perfect_care_days": self._perfect_care_days,
            "last_perfect_check_date": self._last_perfect_check_date,
            "last_snapshot_time": self._last_snapshot_time,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CareTracker":
        """
        Create tracker from dictionary.

        Args:
            data: Dict containing tracker data.

        Returns:
            New CareTracker instance.
        """
        tracker = cls()

        # Restore events
        events_data = data.get("events", [])
        tracker.events = [CareEvent.from_dict(e) for e in events_data]

        # Restore snapshots
        snapshots_data = data.get("snapshots", [])
        tracker.snapshots = [StatSnapshot.from_dict(s) for s in snapshots_data]

        # Restore daily stats
        tracker.daily_stats = data.get("daily_stats", {})

        # Restore state flags
        tracker._is_neglected = data.get("is_neglected", False)
        tracker._was_critical = data.get("was_critical", False)
        tracker._perfect_care_days = data.get("perfect_care_days", 0)
        tracker._last_perfect_check_date = data.get("last_perfect_check_date")
        tracker._last_snapshot_time = data.get("last_snapshot_time", 0.0)

        return tracker
