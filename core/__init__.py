"""
Floob 2.0 Core Module.

Contains the foundational data models for the virtual pet system:
- config: Global constants, colors, and timing values
- pet: Pet stats, state, and data model (legacy, from root pet.py)
- evolution: Evolution stages, forms, and requirements
- care_tracker: Care pattern tracking for evolution calculation
- evolution_manager: XP system and level management (Phase 4)
- evolution_events: Evolution event handling (Phase 4)
- evolution_integration: System integration (Phase 4)
"""

from core.config import (
    Colors,
    Timing,
    Evolution as EvolutionConfig,
    XP,
    Stats,
    Sprites,
    FORM_COLORS,
    hex_to_rgb,
    hex_to_rgba,
)
from core.evolution import (
    EvolutionStage,
    CareStyle,
    EvolutionForm,
    EvolutionRequirements,
    EVOLUTION_FORMS,
    EVOLUTION_TREE,
    check_evolution,
    get_form_by_id,
    get_possible_evolutions,
    get_forms_by_stage,
)
from core.care_tracker import (
    CareEvent,
    CareEventType,
    CareTracker,
    StatSnapshot,
)
from core.evolution_manager import (
    EvolutionManager,
    EvolutionHistory,
    XPSource,
    LEVEL_THRESHOLDS,
)
from core.evolution_events import (
    EvolutionEventHandler,
    EvolutionEvent,
    EvolutionEventType,
    EvolutionAnimationType,
)
from core.evolution_integration import (
    EvolutionIntegrator,
    EvolutionState,
    EvolutionStatus,
    process_evolution,
)
from core.pet import (
    Pet,
    PetState,
    PetStats,
    PetCustomization,
    EvolutionHistoryEntry,
    Mood,
    AutonomousAction,
    ThoughtBubble,
    EarStyle,
    TailStyle,
    Accessory,
    COLOR_PALETTE,
)

__all__ = [
    # Config
    "Colors",
    "Timing",
    "EvolutionConfig",
    "XP",
    "Stats",
    "Sprites",
    "FORM_COLORS",
    "hex_to_rgb",
    "hex_to_rgba",
    # Evolution Data Model
    "EvolutionStage",
    "CareStyle",
    "EvolutionForm",
    "EvolutionRequirements",
    "EVOLUTION_FORMS",
    "EVOLUTION_TREE",
    "check_evolution",
    "get_form_by_id",
    "get_possible_evolutions",
    "get_forms_by_stage",
    # Care Tracker
    "CareEvent",
    "CareEventType",
    "CareTracker",
    "StatSnapshot",
    # Evolution Manager (Phase 4)
    "EvolutionManager",
    "EvolutionHistory",
    "XPSource",
    "LEVEL_THRESHOLDS",
    # Evolution Events (Phase 4)
    "EvolutionEventHandler",
    "EvolutionEvent",
    "EvolutionEventType",
    "EvolutionAnimationType",
    # Evolution Integration (Phase 4)
    "EvolutionIntegrator",
    "EvolutionState",
    "EvolutionStatus",
    "process_evolution",
    # Pet (Phase 5 integration)
    "Pet",
    "PetState",
    "PetStats",
    "PetCustomization",
    "EvolutionHistoryEntry",
    "Mood",
    "AutonomousAction",
    "ThoughtBubble",
    "EarStyle",
    "TailStyle",
    "Accessory",
    "COLOR_PALETTE",
]
