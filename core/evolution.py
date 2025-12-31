"""
Floob 2.0 Evolution System.

Defines evolution stages, forms, requirements, and the evolution tree.
Pets evolve based on their care style and level.

Full evolution system implementation with:
- 5 stages (EGG, BABY, CHILD, TEEN, ADULT)
- 15+ unique forms across stages
- Care style-based evolution paths
- Special forms (Golden, Ghost, Rainbow)
- Visual properties for each form (colors, size multipliers)
- XP and level calculation functions
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from core.care_tracker import CareTracker


class EvolutionStage(Enum):
    """
    Evolution stages representing pet growth phases.

    Progression: EGG -> BABY -> CHILD -> TEEN -> ADULT
    """

    EGG = 0
    BABY = 1
    CHILD = 2
    TEEN = 3
    ADULT = 4

    def next_stage(self) -> Optional["EvolutionStage"]:
        """
        Get the next evolution stage.

        Returns:
            Next stage, or None if already ADULT.
        """
        if self == EvolutionStage.ADULT:
            return None
        return EvolutionStage(self.value + 1)

    def prev_stage(self) -> Optional["EvolutionStage"]:
        """
        Get the previous evolution stage.

        Returns:
            Previous stage, or None if already EGG.
        """
        if self == EvolutionStage.EGG:
            return None
        return EvolutionStage(self.value - 1)

    @property
    def display_name(self) -> str:
        """Get human-readable stage name."""
        return self.name.capitalize()


class CareStyle(Enum):
    """
    Care styles that influence evolution paths.

    Calculated from care patterns over time.
    """

    BALANCED = auto()  # Even care across all stats
    PLAYFUL = auto()  # High play frequency, active
    PAMPERED = auto()  # High feeding, lots of attention
    NEGLECTED = auto()  # Low stats, infrequent care
    SPOILED = auto()  # Overfeeding, always high stats

    @property
    def display_name(self) -> str:
        """Get human-readable care style name."""
        return self.name.capitalize()

    @property
    def description(self) -> str:
        """Get description of this care style."""
        descriptions = {
            CareStyle.BALANCED: "Well-rounded care with attention to all needs",
            CareStyle.PLAYFUL: "Lots of play and activity, energetic lifestyle",
            CareStyle.PAMPERED: "Showered with attention and affection",
            CareStyle.NEGLECTED: "Needs have been overlooked",
            CareStyle.SPOILED: "Never wants for anything, always satisfied",
        }
        return descriptions.get(self, "Unknown care style")


@dataclass
class EvolutionRequirements:
    """
    Requirements that must be met to evolve into a specific form.

    Attributes:
        min_level: Minimum level required.
        care_styles: Allowed care styles (any match triggers evolution).
        from_forms: Forms that can evolve into this one (empty = any).
        special_condition: Optional special requirement description.
    """

    min_level: int = 0
    care_styles: Set[CareStyle] = field(default_factory=set)
    from_forms: Set[str] = field(default_factory=set)
    special_condition: Optional[str] = None

    def can_evolve(
        self,
        level: int,
        care_style: CareStyle,
        current_form: str,
    ) -> bool:
        """
        Check if evolution requirements are met.

        Args:
            level: Current pet level.
            care_style: Current care style.
            current_form: Current form ID.

        Returns:
            True if all requirements are met.
        """
        # Check level
        if level < self.min_level:
            return False

        # Check care style (if specified)
        if self.care_styles and care_style not in self.care_styles:
            return False

        # Check source form (if specified)
        if self.from_forms and current_form not in self.from_forms:
            return False

        return True


@dataclass
class EvolutionForm:
    """
    Represents a specific evolution form.

    Attributes:
        id: Unique identifier for this form.
        name: Display name.
        stage: Evolution stage this form belongs to.
        requirements: Requirements to evolve into this form.
        description: Flavor text describing this form.
        required_level: Level required to reach this form.
        required_care_style: Optional care style name for this evolution path.
        body_color: Primary hex color for the form.
        accent_color: Secondary hex color for accents.
        size_multiplier: Size relative to base (Baby=0.6, Adult=1.2).
        is_special: Whether this is a special/rare form.
        unlock_hint: Optional hint for how to unlock special forms.
    """

    id: str
    name: str
    stage: EvolutionStage
    requirements: EvolutionRequirements
    description: str = ""
    required_level: int = 0
    required_care_style: Optional[str] = None
    body_color: str = "#E8DAEF"
    accent_color: str = "#CDB4DB"
    size_multiplier: float = 1.0
    is_special: bool = False
    unlock_hint: Optional[str] = None

    def __hash__(self) -> int:
        """Hash by form ID for use in sets/dicts."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Compare forms by ID."""
        if isinstance(other, EvolutionForm):
            return self.id == other.id
        return False


# ============================================================================
# EVOLUTION FORMS DEFINITIONS
# ============================================================================

# EGG Stage (1 form)
FORM_EGG = EvolutionForm(
    id="egg",
    name="Egg",
    stage=EvolutionStage.EGG,
    requirements=EvolutionRequirements(min_level=0),
    description="A mysterious wobbling egg",
    required_level=0,
    body_color="#FFF8F0",
    accent_color="#FFE4E1",
    size_multiplier=0.7,
)

# BABY Stage (1 form)
FORM_BLOBLET = EvolutionForm(
    id="bloblet",
    name="Bloblet",
    stage=EvolutionStage.BABY,
    requirements=EvolutionRequirements(
        min_level=1,
        from_forms={"egg"},
    ),
    description="A tiny, wobbly baby blob",
    required_level=1,
    body_color="#E8DAEF",
    accent_color="#CDB4DB",
    size_multiplier=0.6,
)

# CHILD Stage (3 forms)
FORM_BOUNCY = EvolutionForm(
    id="bouncy",
    name="Bouncy",
    stage=EvolutionStage.CHILD,
    requirements=EvolutionRequirements(
        min_level=5,
        care_styles={CareStyle.PLAYFUL, CareStyle.SPOILED},
        from_forms={"bloblet"},
    ),
    description="An energetic, springy blob",
    required_level=5,
    required_care_style="playful",
    body_color="#FFD6E0",
    accent_color="#FFB6C1",
    size_multiplier=0.8,
)

FORM_MELLOW = EvolutionForm(
    id="mellow",
    name="Mellow",
    stage=EvolutionStage.CHILD,
    requirements=EvolutionRequirements(
        min_level=5,
        care_styles={CareStyle.BALANCED},
        from_forms={"bloblet"},
    ),
    description="A calm, content blob",
    required_level=5,
    required_care_style="balanced",
    body_color="#B5E48C",
    accent_color="#95D5B2",
    size_multiplier=0.8,
)

FORM_DROWSY = EvolutionForm(
    id="drowsy",
    name="Drowsy",
    stage=EvolutionStage.CHILD,
    requirements=EvolutionRequirements(
        min_level=5,
        care_styles={CareStyle.PAMPERED, CareStyle.NEGLECTED},
        from_forms={"bloblet"},
    ),
    description="A sleepy, dreamy blob",
    required_level=5,
    required_care_style="pampered",
    body_color="#A2D2FF",
    accent_color="#BDE0FE",
    size_multiplier=0.8,
)

# Legacy aliases for backward compatibility
FORM_BALANCED = FORM_MELLOW
FORM_SLEEPY = FORM_DROWSY

# TEEN Stage (5 forms)
FORM_SPARKY = EvolutionForm(
    id="sparky",
    name="Sparky",
    stage=EvolutionStage.TEEN,
    requirements=EvolutionRequirements(
        min_level=15,
        care_styles={CareStyle.PLAYFUL},
        from_forms={"bouncy"},
    ),
    description="Electric and excitable!",
    required_level=15,
    required_care_style="playful",
    body_color="#FFF3B0",
    accent_color="#FFE66D",
    size_multiplier=1.0,
)

FORM_CHILL = EvolutionForm(
    id="chill",
    name="Chill",
    stage=EvolutionStage.TEEN,
    requirements=EvolutionRequirements(
        min_level=15,
        care_styles={CareStyle.BALANCED},
        from_forms={"mellow", "balanced"},
    ),
    description="Cool and collected",
    required_level=15,
    required_care_style="balanced",
    body_color="#99E2B4",
    accent_color="#88D4AB",
    size_multiplier=1.0,
)

FORM_DREAMY = EvolutionForm(
    id="dreamy",
    name="Dreamy",
    stage=EvolutionStage.TEEN,
    requirements=EvolutionRequirements(
        min_level=15,
        care_styles={CareStyle.PAMPERED, CareStyle.NEGLECTED},
        from_forms={"drowsy", "sleepy"},
    ),
    description="Head in the clouds",
    required_level=15,
    required_care_style="pampered",
    body_color="#CDB4DB",
    accent_color="#E2C2FF",
    size_multiplier=1.0,
)

FORM_HARDY = EvolutionForm(
    id="hardy",
    name="Hardy",
    stage=EvolutionStage.TEEN,
    requirements=EvolutionRequirements(
        min_level=15,
        care_styles={CareStyle.NEGLECTED},
        from_forms={"mellow", "balanced"},
    ),
    description="Tough and resilient",
    required_level=15,
    required_care_style="neglected",
    body_color="#D4C1EC",
    accent_color="#B8A9C9",
    size_multiplier=1.0,
)

FORM_CHONKY = EvolutionForm(
    id="chonky",
    name="Chonky",
    stage=EvolutionStage.TEEN,
    requirements=EvolutionRequirements(
        min_level=15,
        care_styles={CareStyle.SPOILED},
        from_forms={"bouncy", "drowsy", "sleepy"},
    ),
    description="Well-fed and proud",
    required_level=15,
    required_care_style="spoiled",
    body_color="#FFB5A7",
    accent_color="#FFCDB2",
    size_multiplier=1.1,
)

# Legacy aliases for backward compatibility
FORM_ZIPPY = FORM_SPARKY
FORM_COZY = FORM_CHONKY

# ADULT Stage (5 forms)
FORM_ZAPPER = EvolutionForm(
    id="zapper",
    name="Zapper",
    stage=EvolutionStage.ADULT,
    requirements=EvolutionRequirements(
        min_level=30,
        care_styles={CareStyle.PLAYFUL},
        from_forms={"sparky"},
    ),
    description="Crackling with energy!",
    required_level=30,
    required_care_style="playful",
    body_color="#FFF099",
    accent_color="#FFEB3B",
    size_multiplier=1.2,
)

FORM_ZEN = EvolutionForm(
    id="zen",
    name="Zen",
    stage=EvolutionStage.ADULT,
    requirements=EvolutionRequirements(
        min_level=30,
        care_styles={CareStyle.BALANCED},
        from_forms={"chill"},
    ),
    description="Perfectly balanced",
    required_level=30,
    required_care_style="balanced",
    body_color="#A8E6CF",
    accent_color="#88D8B0",
    size_multiplier=1.2,
)

FORM_MYSTIC = EvolutionForm(
    id="mystic",
    name="Mystic",
    stage=EvolutionStage.ADULT,
    requirements=EvolutionRequirements(
        min_level=30,
        care_styles={CareStyle.PAMPERED, CareStyle.BALANCED},
        from_forms={"dreamy"},
    ),
    description="Mysterious and ethereal",
    required_level=30,
    required_care_style="pampered",
    body_color="#DCD0FF",
    accent_color="#C8A2FF",
    size_multiplier=1.2,
)

FORM_SCRAPPER = EvolutionForm(
    id="scrapper",
    name="Scrapper",
    stage=EvolutionStage.ADULT,
    requirements=EvolutionRequirements(
        min_level=30,
        care_styles={CareStyle.NEGLECTED},
        from_forms={"hardy"},
    ),
    description="Battle-hardened survivor",
    required_level=30,
    required_care_style="neglected",
    body_color="#A9A9A9",
    accent_color="#808080",
    size_multiplier=1.1,
)

FORM_FLOOFY = EvolutionForm(
    id="floofy",
    name="Floofy",
    stage=EvolutionStage.ADULT,
    requirements=EvolutionRequirements(
        min_level=30,
        care_styles={CareStyle.PAMPERED, CareStyle.SPOILED},
        from_forms={"chonky", "cozy"},
    ),
    description="Maximum floof achieved",
    required_level=30,
    required_care_style="spoiled",
    body_color="#FFDAB9",
    accent_color="#FFE4C4",
    size_multiplier=1.3,
)

# Legacy aliases for backward compatibility
FORM_DASHER = FORM_ZAPPER
FORM_LOAFER = FORM_ZEN

# SPECIAL Forms (can appear at any stage after requirements met)
FORM_GOLDEN = EvolutionForm(
    id="golden",
    name="Golden",
    stage=EvolutionStage.ADULT,
    requirements=EvolutionRequirements(
        min_level=30,
        special_condition="7 consecutive days of perfect care (all stats above 80)",
    ),
    description="A legendary golden blob!",
    required_level=30,
    body_color="#FFD700",
    accent_color="#FFF8DC",
    size_multiplier=1.2,
    is_special=True,
    unlock_hint="Perfect care for 7 days...",
)

FORM_GHOST = EvolutionForm(
    id="ghost",
    name="Ghost",
    stage=EvolutionStage.ADULT,
    requirements=EvolutionRequirements(
        min_level=30,
        care_styles={CareStyle.NEGLECTED},
        special_condition="Revived from critical neglect (all stats below 10)",
    ),
    description="Returned from beyond...",
    required_level=30,
    body_color="#E8E8E8",
    accent_color="#FFFFFF",
    size_multiplier=1.0,
    is_special=True,
    unlock_hint="What doesn't kill you...",
)

FORM_RAINBOW = EvolutionForm(
    id="rainbow",
    name="Rainbow",
    stage=EvolutionStage.ADULT,
    requirements=EvolutionRequirements(
        min_level=30,
        special_condition="Born or evolved on a special date",
    ),
    description="A prismatic wonder!",
    required_level=30,
    body_color="#FF69B4",
    accent_color="#87CEEB",
    size_multiplier=1.2,
    is_special=True,
    unlock_hint="Special occasions bring special forms...",
)


# ============================================================================
# EVOLUTION DATA STRUCTURES
# ============================================================================

# All evolution forms indexed by ID
EVOLUTION_FORMS: Dict[str, EvolutionForm] = {
    # Standard forms
    "egg": FORM_EGG,
    "bloblet": FORM_BLOBLET,
    # CHILD forms
    "bouncy": FORM_BOUNCY,
    "mellow": FORM_MELLOW,
    "drowsy": FORM_DROWSY,
    # Legacy CHILD aliases
    "balanced": FORM_MELLOW,
    "sleepy": FORM_DROWSY,
    # TEEN forms
    "sparky": FORM_SPARKY,
    "chill": FORM_CHILL,
    "dreamy": FORM_DREAMY,
    "hardy": FORM_HARDY,
    "chonky": FORM_CHONKY,
    # Legacy TEEN aliases
    "zippy": FORM_SPARKY,
    "cozy": FORM_CHONKY,
    # ADULT forms
    "zapper": FORM_ZAPPER,
    "zen": FORM_ZEN,
    "mystic": FORM_MYSTIC,
    "scrapper": FORM_SCRAPPER,
    "floofy": FORM_FLOOFY,
    # Legacy ADULT aliases
    "dasher": FORM_ZAPPER,
    "loafer": FORM_ZEN,
    # Special forms
    "golden": FORM_GOLDEN,
    "ghost": FORM_GHOST,
    "rainbow": FORM_RAINBOW,
}

# Evolution paths: maps form_id -> list of possible evolution form_ids
EVOLUTION_PATHS: Dict[str, List[str]] = {
    "egg": ["bloblet"],
    "bloblet": ["bouncy", "mellow", "drowsy"],
    # CHILD -> TEEN paths
    "bouncy": ["sparky", "chonky"],
    "mellow": ["chill", "hardy"],
    "drowsy": ["dreamy", "chonky"],
    # TEEN -> ADULT paths
    "sparky": ["zapper"],
    "chill": ["zen"],
    "dreamy": ["mystic"],
    "hardy": ["scrapper"],
    "chonky": ["floofy"],
    # Adults don't evolve further (except to special forms)
    "zapper": [],
    "zen": [],
    "mystic": [],
    "scrapper": [],
    "floofy": [],
    # Special forms
    "golden": [],
    "ghost": [],
    "rainbow": [],
}

# Legacy alias for backward compatibility
EVOLUTION_TREE = EVOLUTION_PATHS


# ============================================================================
# EVOLUTION FUNCTIONS
# ============================================================================


def get_form_by_id(form_id: str) -> Optional[EvolutionForm]:
    """
    Get an evolution form by its ID.

    Args:
        form_id: The form's unique identifier.

    Returns:
        The EvolutionForm, or None if not found.
    """
    return EVOLUTION_FORMS.get(form_id)


def get_possible_evolutions(current_form_id: str) -> List[EvolutionForm]:
    """
    Get all possible evolution forms from the current form.

    Args:
        current_form_id: The current form's ID.

    Returns:
        List of possible EvolutionForm objects.
    """
    possible_ids = EVOLUTION_TREE.get(current_form_id, [])
    return [EVOLUTION_FORMS[fid] for fid in possible_ids if fid in EVOLUTION_FORMS]


def get_forms_by_stage(stage: EvolutionStage) -> List[EvolutionForm]:
    """
    Get all forms belonging to a specific evolution stage.

    Args:
        stage: The evolution stage to filter by.

    Returns:
        List of EvolutionForm objects at that stage.
    """
    return [form for form in EVOLUTION_FORMS.values() if form.stage == stage]


def check_evolution(
    current_form_id: str,
    level: int,
    care_style: CareStyle,
    care_tracker: Optional["CareTracker"] = None,
) -> Optional[EvolutionForm]:
    """
    Check if the pet can evolve and determine the target form.

    Args:
        current_form_id: Current form ID.
        level: Current pet level.
        care_style: Current care style.
        care_tracker: Optional care tracker for special evolution checks.

    Returns:
        The EvolutionForm to evolve into, or None if cannot evolve.
    """
    possible_forms = get_possible_evolutions(current_form_id)

    if not possible_forms:
        return None

    # Check special evolutions first
    if care_tracker:
        special_form = _check_special_evolution(level, care_tracker)
        if special_form:
            return special_form

    # Find matching form based on care style
    for form in possible_forms:
        if form.requirements.can_evolve(level, care_style, current_form_id):
            return form

    # If no care style match, check for fallback (any care style allowed)
    for form in possible_forms:
        if not form.requirements.care_styles:
            if form.requirements.can_evolve(level, care_style, current_form_id):
                return form

    return None


def _check_special_evolution(
    level: int,
    care_tracker: "CareTracker",
) -> Optional[EvolutionForm]:
    """
    Check for special evolution conditions.

    Args:
        level: Current pet level.
        care_tracker: Care tracker for history analysis.

    Returns:
        Special EvolutionForm if conditions met, None otherwise.
    """
    # Golden form: 7 days of perfect care
    if level >= 30 and care_tracker.check_perfect_care_streak(days=7, min_stat=80.0):
        return FORM_GOLDEN

    # Ghost form: revived from critical neglect
    if level >= 30 and care_tracker.was_critically_neglected():
        return FORM_GHOST

    # Rainbow form: special date (could be birthday, holiday, etc.)
    if level >= 30 and care_tracker.is_special_date():
        return FORM_RAINBOW

    return None


def get_evolution_progress(
    current_form_id: str,
    level: int,
    care_style: CareStyle,
) -> Dict[str, float]:
    """
    Get progress toward each possible evolution.

    Args:
        current_form_id: Current form ID.
        level: Current pet level.
        care_style: Current care style.

    Returns:
        Dict mapping form_id to progress (0.0-1.0).
    """
    possible_forms = get_possible_evolutions(current_form_id)
    progress: Dict[str, float] = {}

    for form in possible_forms:
        req = form.requirements

        # Level progress
        if req.min_level > 0:
            level_progress = min(1.0, level / req.min_level)
        else:
            level_progress = 1.0

        # Care style match
        if req.care_styles:
            style_match = 1.0 if care_style in req.care_styles else 0.0
        else:
            style_match = 1.0

        # Combined progress (level is primary, care style is binary)
        progress[form.id] = level_progress * 0.7 + style_match * 0.3

    return progress


# ============================================================================
# XP AND LEVEL CALCULATION FUNCTIONS
# ============================================================================


def calculate_level(experience: int) -> int:
    """
    Calculate level from total XP.

    Each level requires progressively more XP:
    - Level 1 = 0 XP
    - Level 2 = 100 XP
    - Level 3 = 250 XP
    - etc.

    Args:
        experience: Total experience points.

    Returns:
        Current level (1+).
    """
    level = 1
    xp_needed = 0
    while experience >= xp_needed:
        level += 1
        xp_needed += level * 50
    return level - 1


def get_xp_for_level(level: int) -> int:
    """
    Get total XP needed to reach a specific level.

    Args:
        level: Target level.

    Returns:
        Total XP required to reach that level.
    """
    total = 0
    for lv in range(2, level + 1):
        total += lv * 50
    return total


def get_xp_progress(experience: int) -> Tuple[int, int]:
    """
    Get XP progress toward the next level.

    Args:
        experience: Total experience points.

    Returns:
        Tuple of (current_xp_in_level, xp_needed_for_next_level).
    """
    level = calculate_level(experience)
    current_level_xp = get_xp_for_level(level)
    next_level_xp = get_xp_for_level(level + 1)
    return (experience - current_level_xp, next_level_xp - current_level_xp)


def check_evolution_by_level(
    form_id: str,
    level: int,
    care_style: str,
) -> Optional[str]:
    """
    Check if evolution is possible and return next form_id.

    Simplified evolution check using level and care style string.

    Args:
        form_id: Current form identifier.
        level: Current level.
        care_style: Care style as lowercase string.

    Returns:
        Next form_id if evolution is possible, None otherwise.
    """
    current_form = EVOLUTION_FORMS.get(form_id)
    if not current_form:
        return None

    possible_forms = EVOLUTION_PATHS.get(form_id, [])
    if not possible_forms:
        return None

    for next_form_id in possible_forms:
        next_form = EVOLUTION_FORMS.get(next_form_id)
        if not next_form:
            continue

        # Check level requirement
        if level < next_form.required_level:
            continue

        # Check care style if required
        if next_form.required_care_style:
            if care_style.lower() == next_form.required_care_style.lower():
                return next_form_id
        else:
            # No care style required, can evolve
            return next_form_id

    return None


def check_special_evolution(
    form_id: str,
    level: int,
    care_tracker: Optional["CareTracker"],
    consecutive_perfect_days: int,
    was_revived: bool,
) -> Optional[str]:
    """
    Check for special evolution conditions.

    Args:
        form_id: Current form identifier.
        level: Current level.
        care_tracker: Optional care tracker instance.
        consecutive_perfect_days: Number of days with perfect care.
        was_revived: Whether the pet was revived from critical state.

    Returns:
        Special form_id if conditions met, None otherwise.
    """
    # Golden form: 7 days of perfect care
    if consecutive_perfect_days >= 7 and level >= 30:
        return "golden"

    # Ghost form: was revived from critical state
    if was_revived and level >= 30:
        return "ghost"

    return None


# ============================================================================
# EVOLUTION HISTORY TRACKING
# ============================================================================


@dataclass
class EvolutionHistory:
    """
    Tracks all forms the pet has been through.

    Maintains a chronological record of evolution events.

    Attributes:
        forms: List of form IDs in order of evolution.
        evolution_times: List of timestamps when each evolution occurred.
    """

    forms: List[str] = field(default_factory=lambda: ["egg"])
    evolution_times: List[float] = field(default_factory=list)

    def add_evolution(self, form_id: str) -> None:
        """
        Record a new evolution.

        Args:
            form_id: The form evolved into.
        """
        self.forms.append(form_id)
        self.evolution_times.append(time.time())

    def get_current_form(self) -> str:
        """
        Get the current (most recent) form.

        Returns:
            Current form ID.
        """
        return self.forms[-1] if self.forms else "egg"

    def get_evolution_count(self) -> int:
        """
        Get the number of evolutions that have occurred.

        Returns:
            Number of evolution events (excluding initial form).
        """
        return max(0, len(self.forms) - 1)

    def get_time_in_current_form(self) -> float:
        """
        Get how long the pet has been in its current form.

        Returns:
            Time in seconds, or 0 if no evolution times recorded.
        """
        if not self.evolution_times:
            return 0.0
        return time.time() - self.evolution_times[-1]

    def to_dict(self) -> dict:
        """
        Convert to dictionary for serialization.

        Returns:
            Dictionary representation.
        """
        return {
            "forms": self.forms,
            "evolution_times": self.evolution_times,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EvolutionHistory":
        """
        Create from dictionary.

        Args:
            data: Dictionary with forms and evolution_times.

        Returns:
            New EvolutionHistory instance.
        """
        return cls(
            forms=data.get("forms", ["egg"]),
            evolution_times=data.get("evolution_times", []),
        )
