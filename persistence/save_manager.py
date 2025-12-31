"""
Floob 2.0 Save Manager.

Handles saving and loading of:
- Pet data (stats, level, XP, form)
- Evolution history
- Care tracker data
- Settings (auto-care toggle)
- Migration from old save formats

Save Format Versions:
    1: Original Floob format (flat structure, no evolution)
    2: Floob 2.0 with evolution system
    3: Floob 2.0 with integrated EvolutionManager (Phase 4)

The save manager integrates with:
    - EvolutionManager: XP, levels, and evolution state
    - CareTracker: Care patterns for evolution calculation
    - Special evolution flags (golden, ghost, rainbow eligibility)
"""

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import time

from core.config import Evolution as EvolutionConfig, XP as XPConfig, Stats as StatsConfig
from core.evolution import EvolutionStage, CareStyle, get_form_by_id
from core.care_tracker import CareTracker


logger = logging.getLogger(__name__)


# Current save version for migration
SAVE_VERSION = 3


class SaveVersion(Enum):
    """Save format version identifiers."""
    V1_LEGACY = 1       # Original Floob (flat structure)
    V2_EVOLUTION = 2    # Basic evolution system
    V3_INTEGRATED = 3   # Full Phase 4 integration


CURRENT_SAVE_VERSION = SaveVersion.V3_INTEGRATED


@dataclass
class SaveData:
    """
    Complete save data structure for Floob 2.0.

    Contains all data needed to fully restore game state.

    Attributes:
        version: Save format version number.
        timestamp: When the save was created (Unix timestamp).
        pet: Pet stats and basic data.
        evolution: Evolution manager state.
        care_tracker: Care tracker state.
        settings: Game settings.
        special_flags: Special evolution tracking flags.
    """
    version: int = SAVE_VERSION
    timestamp: float = field(default_factory=time.time)
    pet: Dict[str, Any] = field(default_factory=dict)
    evolution: Dict[str, Any] = field(default_factory=dict)
    care_tracker: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    special_flags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "pet": self.pet,
            "evolution": self.evolution,
            "care_tracker": self.care_tracker,
            "settings": self.settings,
            "special_flags": self.special_flags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SaveData":
        """Create from dictionary."""
        return cls(
            version=data.get("version", SAVE_VERSION),
            timestamp=data.get("timestamp", time.time()),
            pet=data.get("pet", {}),
            evolution=data.get("evolution", data.get("evolution_data", {})),
            care_tracker=data.get("care_tracker", data.get("care_tracker_data", {})),
            settings=data.get("settings", {}),
            special_flags=data.get("special_flags", {}),
        )


class SaveManager:
    """
    Manages saving and loading of all pet-related data.

    Handles:
    - Pet stats, level, XP, form
    - Evolution history
    - Care tracker data
    - Settings
    - Migration from old save formats
    """

    DEFAULT_SAVE_DIR = "data"
    DEFAULT_SAVE_FILE = "pet_state.json"

    def __init__(self, save_dir: Optional[str] = None) -> None:
        """
        Initialize persistence manager.

        Args:
            save_dir: Directory for save files. Defaults to 'data' in script directory.
        """
        if save_dir is None:
            # Get the directory where the Floob project is located
            script_dir = Path(__file__).parent.parent
            save_dir = script_dir / self.DEFAULT_SAVE_DIR
        else:
            save_dir = Path(save_dir)

        self.save_dir = save_dir
        self.save_path = save_dir / self.DEFAULT_SAVE_FILE

        # Ensure save directory exists
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Create save directory if it doesn't exist."""
        os.makedirs(self.save_dir, exist_ok=True)

    def save(
        self,
        pet_data: Dict[str, Any],
        care_tracker: Optional[CareTracker] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Save all pet data to JSON file.

        Args:
            pet_data: Dictionary containing pet information:
                - name: Pet name
                - form_id: Current evolution form ID
                - level: Current level
                - xp: Current XP
                - hunger, happiness, energy: Current stats
                - birth_time: Unix timestamp of birth
                - evolution_history: List of evolution events
            care_tracker: Optional CareTracker instance to save.
            settings: Optional settings dictionary.

        Returns:
            True if save successful, False otherwise.
        """
        try:
            data = {
                "version": SAVE_VERSION,
                "last_save_time": time.time(),
                "pet": pet_data,
            }

            # Include care tracker data
            if care_tracker:
                data["care_tracker"] = care_tracker.to_dict()

            # Include settings
            if settings:
                data["settings"] = settings

            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            return True

        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Error saving pet state: {e}")
            return False

    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load all pet data from JSON file.

        Returns:
            Dictionary containing:
                - pet: Pet data dictionary
                - care_tracker: CareTracker instance (if present)
                - settings: Settings dictionary (if present)
            Or None if load fails.
        """
        if not self.save_exists():
            return None

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Migrate old save format if necessary
            data = self._migrate_save(data)

            result = {
                "pet": data.get("pet", {}),
                "settings": data.get("settings", {}),
            }

            # Restore care tracker
            if "care_tracker" in data:
                result["care_tracker"] = CareTracker.from_dict(data["care_tracker"])
            else:
                result["care_tracker"] = CareTracker()

            # Apply stat decay based on time since last save
            last_save = data.get("last_save_time", time.time())
            elapsed = time.time() - last_save
            result["time_elapsed"] = min(elapsed, 86400)  # Cap at 24 hours

            return result

        except (IOError, OSError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading pet state: {e}")
            return None

    def _migrate_save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate old save format to current version.

        Args:
            data: Raw loaded data.

        Returns:
            Migrated data in current format.
        """
        version = data.get("version", 1)

        if version >= SAVE_VERSION:
            return data

        # Version 1 (old format) -> Version 2 (new format)
        if version == 1 or "version" not in data:
            print("Migrating save from v1 to v2...")

            # Old format had flat structure
            migrated = {
                "version": SAVE_VERSION,
                "last_save_time": data.get("last_save_time", time.time()),
                "pet": {
                    "name": data.get("name", "Blobby"),
                    "form_id": "egg",  # Start as egg
                    "stage": "EGG",
                    "level": 1,
                    "xp": 0,
                    "hunger": data.get("hunger", StatsConfig.DEFAULT_HUNGER),
                    "happiness": data.get("happiness", StatsConfig.DEFAULT_HAPPINESS),
                    "energy": data.get("energy", StatsConfig.DEFAULT_ENERGY),
                    "birth_time": data.get("last_save_time", time.time()) - 86400,  # Assume 1 day old
                    "evolution_history": [
                        {
                            "form_id": "egg",
                            "form_name": "Egg",
                            "stage": "EGG",
                            "timestamp": data.get("last_save_time", time.time()) - 86400,
                        }
                    ],
                },
                "settings": {
                    "auto_care_enabled": data.get("auto_care_enabled", True),
                },
            }

            # Preserve creature_type if present (old system)
            if "creature_type" in data:
                migrated["pet"]["legacy_creature_type"] = data["creature_type"]

            # Preserve customization if present
            if "customization" in data:
                migrated["pet"]["legacy_customization"] = data["customization"]

            return migrated

        return data

    def save_exists(self) -> bool:
        """Check if a save file exists."""
        return self.save_path.exists()

    def delete_save(self) -> bool:
        """
        Delete the save file.

        Returns:
            True if deletion successful or file didn't exist, False on error.
        """
        try:
            if self.save_path.exists():
                os.remove(self.save_path)
            return True
        except OSError as e:
            print(f"Error deleting save file: {e}")
            return False

    def get_quick_info(self) -> Optional[Dict[str, Any]]:
        """
        Get quick pet info without full load (for startup checks).

        Returns:
            Basic pet info or None if no save exists.
        """
        if not self.save_exists():
            return None

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            pet = data.get("pet", {})
            return {
                "name": pet.get("name", "Unknown"),
                "form_id": pet.get("form_id", "egg"),
                "level": pet.get("level", 1),
                "has_save": True,
            }

        except (IOError, OSError, json.JSONDecodeError):
            return None


def create_new_pet(name: str = "Blobby") -> Dict[str, Any]:
    """
    Create data for a new pet (starts as egg).

    Args:
        name: Name for the new pet.

    Returns:
        Dictionary containing new pet data.
    """
    current_time = time.time()

    return {
        "name": name,
        "form_id": "egg",
        "stage": "EGG",
        "level": 0,
        "xp": 0,
        "hunger": StatsConfig.DEFAULT_HUNGER,
        "happiness": StatsConfig.DEFAULT_HAPPINESS,
        "energy": StatsConfig.DEFAULT_ENERGY,
        "birth_time": current_time,
        "evolution_history": [
            {
                "form_id": "egg",
                "form_name": "Egg",
                "stage": "EGG",
                "timestamp": current_time,
            }
        ],
    }


def calculate_xp_for_level(level: int) -> int:
    """
    Calculate total XP needed to reach a level.

    Uses exponential scaling based on config.

    Args:
        level: Target level.

    Returns:
        Total XP needed.
    """
    if level <= 0:
        return 0

    total_xp = 0
    for lvl in range(1, level + 1):
        xp_for_lvl = int(
            EvolutionConfig.BASE_XP_PER_LEVEL *
            (EvolutionConfig.XP_LEVEL_MULTIPLIER ** (lvl - 1))
        )
        total_xp += xp_for_lvl

    return total_xp


def calculate_xp_to_next_level(current_level: int) -> int:
    """
    Calculate XP needed for the next level.

    Args:
        current_level: Current level.

    Returns:
        XP needed to level up.
    """
    return int(
        EvolutionConfig.BASE_XP_PER_LEVEL *
        (EvolutionConfig.XP_LEVEL_MULTIPLIER ** current_level)
    )


def get_next_evolution_level(current_stage: str) -> Optional[int]:
    """
    Get the level at which next evolution occurs.

    Args:
        current_stage: Current evolution stage name.

    Returns:
        Level for next evolution, or None if at max stage.
    """
    stage_levels = {
        "EGG": 1,
        "BABY": EvolutionConfig.BABY_TO_CHILD_LEVEL,
        "CHILD": EvolutionConfig.CHILD_TO_TEEN_LEVEL,
        "TEEN": EvolutionConfig.TEEN_TO_ADULT_LEVEL,
        "ADULT": None,
    }
    return stage_levels.get(current_stage, None)


def migrate_save(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate save data from old format to current version.

    Standalone function for use outside SaveManager class.

    Args:
        data: Raw save data dictionary.

    Returns:
        Migrated data in current format.
    """
    version = data.get("version", 1)

    if version >= SAVE_VERSION:
        return data

    # Version 1 (old format) -> Version 2 (evolution system)
    if version == 1 or "version" not in data:
        logger.info("Migrating save from v1 to v2/v3...")

        migrated = {
            "version": SAVE_VERSION,
            "last_save_time": data.get("last_save_time", time.time()),
            "pet": {
                "name": data.get("name", "Blobby"),
                "form_id": "bloblet",  # Start as baby for migrated saves
                "stage": "BABY",
                "level": 1,
                "experience": 0,
                "hunger": data.get("hunger", StatsConfig.DEFAULT_HUNGER),
                "happiness": data.get("happiness", StatsConfig.DEFAULT_HAPPINESS),
                "energy": data.get("energy", StatsConfig.DEFAULT_ENERGY),
                "birth_time": data.get("last_save_time", time.time()) - 86400,
                "evolution_history": [
                    {
                        "from_form": "egg",
                        "to_form": "bloblet",
                        "timestamp": data.get("last_save_time", time.time()) - 86400,
                        "level_at_evolution": 1,
                    }
                ],
            },
            "settings": {
                "auto_care_enabled": data.get("auto_care_enabled", True),
            },
        }

        # Preserve creature_type if present (old system)
        if "creature_type" in data:
            migrated["pet"]["legacy_creature_type"] = data["creature_type"]

        return migrated

    # Version 2 -> Version 3 (add special_flags and evolution structure)
    if version == 2:
        logger.info("Migrating save from v2 to v3...")
        data["version"] = SAVE_VERSION

        # Add special_flags if missing
        if "special_flags" not in data:
            data["special_flags"] = {
                "has_fainted": False,
                "was_revived": False,
                "perfect_care_streak": 0,
            }

        # Restructure evolution data if needed
        pet = data.get("pet", {})
        if "evolution" not in data and ("xp" in pet or "level" in pet):
            data["evolution"] = {
                "total_xp": pet.get("xp", 0),
                "current_form_id": pet.get("form_id", "bloblet"),
                "evolution_stage": pet.get("stage", "BABY"),
                "evolution_history": pet.get("evolution_history", []),
                "last_time_xp_update": time.time(),
            }

        return data

    return data


# =============================================================================
# Phase 4 Integration Methods
# =============================================================================

def get_evolution_manager_from_save(
    save_manager: SaveManager,
) -> "EvolutionManager":
    """
    Get or create an EvolutionManager from save data.

    Convenience function for Phase 4 integration.

    Args:
        save_manager: The SaveManager instance.

    Returns:
        EvolutionManager instance.
    """
    from core.evolution_manager import EvolutionManager

    loaded = save_manager.load()
    if loaded is None:
        return EvolutionManager()

    pet = loaded.get("pet", {})
    evolution = loaded.get("evolution", {})

    # Build evolution data from pet and evolution sections
    evolution_data = {
        "total_xp": evolution.get("total_xp", pet.get("xp", 0)),
        "current_form_id": evolution.get(
            "current_form_id",
            pet.get("form_id", "egg")
        ),
        "evolution_stage": evolution.get(
            "evolution_stage",
            pet.get("stage", "EGG")
        ),
        "evolution_history": evolution.get(
            "evolution_history",
            pet.get("evolution_history", [])
        ),
        "last_time_xp_update": evolution.get(
            "last_time_xp_update",
            time.time()
        ),
    }

    return EvolutionManager.from_dict(evolution_data)


def get_care_tracker_from_save(
    save_manager: SaveManager,
) -> CareTracker:
    """
    Get or create a CareTracker from save data.

    Args:
        save_manager: The SaveManager instance.

    Returns:
        CareTracker instance.
    """
    loaded = save_manager.load()
    if loaded is None:
        return CareTracker()

    care_data = loaded.get("care_tracker", {})
    if isinstance(care_data, CareTracker):
        return care_data

    return CareTracker.from_dict(care_data)


def save_with_evolution(
    save_manager: SaveManager,
    pet_data: Dict[str, Any],
    evolution_manager: "EvolutionManager",
    care_tracker: CareTracker,
    settings: Optional[Dict[str, Any]] = None,
    special_flags: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Save complete game state with Phase 4 integration.

    Args:
        save_manager: The SaveManager instance.
        pet_data: Pet stats dictionary.
        evolution_manager: EvolutionManager instance.
        care_tracker: CareTracker instance.
        settings: Optional settings dictionary.
        special_flags: Optional special flags.

    Returns:
        True if save successful.
    """
    from core.evolution_manager import EvolutionManager

    # Build complete save data
    full_pet_data = {
        **pet_data,
        # Include evolution info in pet for compatibility
        "form_id": evolution_manager.current_form_id,
        "stage": evolution_manager.evolution_stage.name,
        "level": evolution_manager.get_level(),
    }

    # Build evolution section
    evolution_data = evolution_manager.to_dict()

    # Build special flags from care tracker
    if special_flags is None:
        special_flags = {}

    special_flags.setdefault("has_fainted", care_tracker.was_revived)
    special_flags.setdefault("was_revived", care_tracker.was_revived)
    special_flags.setdefault("consecutive_perfect_days", care_tracker.consecutive_perfect_days)
    special_flags.setdefault("perfect_care_streak", care_tracker.consecutive_perfect_days)

    # Create complete save data
    save_data = {
        "version": SAVE_VERSION,
        "timestamp": time.time(),
        "pet": full_pet_data,
        "evolution": evolution_data,
        "care_tracker": care_tracker.to_dict(),
        "settings": settings or {},
        "special_flags": special_flags,
    }

    try:
        with open(save_manager.save_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2)
        logger.debug(f"Game saved with evolution data to {save_manager.save_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving game: {e}")
        return False


def load_complete_state(
    save_manager: SaveManager,
) -> Optional[Dict[str, Any]]:
    """
    Load complete game state with Phase 4 components.

    Reads directly from the save file to get all evolution data.

    Args:
        save_manager: The SaveManager instance.

    Returns:
        Dictionary with pet_data, evolution_manager, care_tracker, settings,
        special_flags, and time_elapsed. None if load fails.
    """
    from core.evolution_manager import EvolutionManager

    if not save_manager.save_exists():
        return None

    try:
        with open(save_manager.save_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # Migrate if needed
        raw_data = migrate_save(raw_data)

        pet = raw_data.get("pet", {})
        evolution = raw_data.get("evolution", {})
        care_tracker_data = raw_data.get("care_tracker", {})
        settings = raw_data.get("settings", {})
        special_flags = raw_data.get("special_flags", {})
        timestamp = raw_data.get("timestamp", raw_data.get("last_save_time", time.time()))

        # Restore care tracker
        if isinstance(care_tracker_data, dict):
            care_tracker = CareTracker.from_dict(care_tracker_data)
        else:
            care_tracker = CareTracker()

        # Build evolution data from both evolution and pet sections
        evolution_data = {
            "total_xp": evolution.get("total_xp", pet.get("xp", 0)),
            "current_form_id": evolution.get(
                "current_form_id",
                pet.get("form_id", "egg")
            ),
            "evolution_stage": evolution.get(
                "evolution_stage",
                pet.get("stage", "EGG")
            ),
            "evolution_history": evolution.get(
                "evolution_history",
                pet.get("evolution_history", [])
            ),
            "last_time_xp_update": evolution.get(
                "last_time_xp_update",
                time.time()
            ),
        }

        evolution_manager = EvolutionManager.from_dict(evolution_data)

        # Calculate time elapsed
        elapsed = time.time() - timestamp
        time_elapsed = min(elapsed, 86400)  # Cap at 24 hours

        return {
            "pet_data": pet,
            "evolution_manager": evolution_manager,
            "care_tracker": care_tracker,
            "settings": settings,
            "special_flags": special_flags,
            "time_elapsed": time_elapsed,
        }

    except Exception as e:
        logger.error(f"Error loading complete state: {e}")
        return None
