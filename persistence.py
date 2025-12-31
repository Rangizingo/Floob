"""
JSON persistence for the Desktop Virtual Pet.

Handles saving and loading pet state to/from files.
"""

import json
import os
from pathlib import Path
from typing import Optional

from pet import Pet


class PetPersistence:
    """
    Manages saving and loading pet state to JSON files.

    Attributes:
        save_path: Path to the save file.
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
            # Get the directory where this script is located
            script_dir = Path(__file__).parent
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

    def save(self, pet: Pet) -> bool:
        """
        Save pet state to JSON file.

        Args:
            pet: Pet instance to save.

        Returns:
            True if save successful, False otherwise.
        """
        try:
            data = pet.to_dict()

            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            return True
        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Error saving pet state: {e}")
            return False

    def load(self) -> Optional[Pet]:
        """
        Load pet state from JSON file.

        Returns:
            Pet instance if load successful, None otherwise.
        """
        if not self.save_path.exists():
            return None

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return Pet.from_dict(data)
        except (IOError, OSError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading pet state: {e}")
            return None

    def load_or_create(self, name: str = "Fennix", creature_type: str = "fennix") -> Pet:
        """
        Load existing pet or create a new one.

        Args:
            name: Name for new pet if creating.
            creature_type: Type of creature for new pet.

        Returns:
            Pet instance, either loaded or newly created.
        """
        pet = self.load()
        if pet is None:
            pet = Pet(name=name, creature_type=creature_type)
        return pet

    def has_creature_type(self) -> bool:
        """
        Check if saved pet has a creature_type field.

        Returns:
            True if creature_type exists in save, False otherwise.
        """
        if not self.save_path.exists():
            return False

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return "creature_type" in data
        except (IOError, OSError, json.JSONDecodeError):
            return False

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

    def save_exists(self) -> bool:
        """Check if a save file exists."""
        return self.save_path.exists()
