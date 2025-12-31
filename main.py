"""
Floob 2.0 - Desktop Virtual Pet

A charming virtual pet that lives on your desktop with evolution system.

Features:
- Evolution system with 5 stages (Egg -> Baby -> Child -> Teen -> Adult)
- XP and leveling system
- Care tracking that affects evolution paths
- Multiple evolution forms based on care style
- Transparent overlay window
- Customizable creatures
- Stats system (hunger, happiness, energy)
- Multiple animation states
- Autonomous behavior
- Right-click context menu
- JSON persistence with migration

Usage:
    python main.py
"""

import time
import sys
from typing import Optional

# Core modules
from core.pet import Pet, PetState
from core.config import Stats as StatsConfig
from core.evolution import get_form_by_id, EvolutionStage
from core.evolution_manager import EvolutionManager
from core.care_tracker import CareTracker

# UI modules
from ui.window import PetWindow
from ui.menu import PetMenu
from ui.dialogs import StatsDialog, EvolutionHistoryDialog, EvolutionNotificationDialog, SettingsDialog

# Animation modules
from animation.engine import AnimationEngine
from animation.states import AnimationState

# Graphics - new blob renderer system
from graphics import BlobRenderer, PetRenderState, RenderState

# Persistence
from persistence.save_manager import (
    SaveManager,
    create_new_pet,
    get_next_evolution_level,
    calculate_xp_to_next_level,
)

# Legacy support
from selection import CREATURES


class Floob:
    """
    Main Floob 2.0 application class.

    Integrates all components:
    - Pet (core data model)
    - Window (transparent overlay)
    - Graphics (rendering)
    - Animation (state machine)
    - Menu (context menu)
    - Persistence (save/load)
    - Evolution (XP, levels, evolution)
    """

    # Update intervals
    RENDER_INTERVAL = 33  # ~30 FPS
    STAT_UPDATE_INTERVAL = 1000  # 1 second
    AUTOSAVE_INTERVAL = 60000  # 1 minute
    AUTONOMOUS_CHECK_INTERVAL = 3000  # 3 seconds
    EVOLUTION_CHECK_INTERVAL = 5000  # 5 seconds

    def __init__(self) -> None:
        """Initialize the Floob application."""
        # Create window first
        self.window = PetWindow()

        # Load or create pet
        self.save_manager = SaveManager()
        self._load_or_create_pet()

        # Create animation engine
        self.animation = AnimationEngine()

        # Create graphics system - new BlobRenderer
        self.renderer = BlobRenderer()
        self._animation_state = {
            "phase": 0.0,
            "bounce": 0.0,
            "direction": 1,
            "new_x": PetWindow.WIDTH // 2,
            "new_y": PetWindow.HEIGHT // 2,
        }

        # Create context menu
        self._create_menu()

        # Connect pet state changes to animation
        self.pet.add_state_callback(self._on_pet_state_change)

        # Bind window events
        self.window.set_on_left_click(self._handle_click)
        self.window.set_on_double_click(self._handle_double_click)
        self.window.set_on_right_click(self._handle_right_click)
        self.window.set_on_frame_update(self._on_frame_update)

        # Timing
        self._last_stat_time = time.time()
        self._last_evolution_check = time.time()

        # Start update loops
        self._schedule_stat_update()
        self._schedule_autosave()
        self._schedule_autonomous_check()
        self._schedule_evolution_check()

        # Start animation loop
        self.window.start_animation_loop()

        # Check for egg hatch animation
        self._check_initial_evolution()

    def _load_or_create_pet(self) -> None:
        """Load existing pet or create new one."""
        save_data = self.save_manager.load()

        if save_data:
            # Load existing pet
            pet_data = save_data.get("pet", {})
            self.pet = Pet.from_dict(pet_data)
            self.care_tracker = save_data.get("care_tracker", CareTracker())
            self.settings = save_data.get("settings", {})

            # Apply time decay
            time_elapsed = save_data.get("time_elapsed", 0)
            if time_elapsed > 0:
                self.pet.update(time_elapsed)

            print(f"Welcome back, {self.pet.name}!")
            print(f"Level: {self.pet.level}, Form: {self.pet.current_form.name if self.pet.current_form else 'Unknown'}")

        else:
            # Create new pet (starts as egg)
            self.pet = Pet(name="Blobby")
            self.care_tracker = CareTracker()
            self.settings = {"auto_care_enabled": True}
            self._show_egg_hatch = True

            print("Welcome to Floob 2.0!")
            print("Your egg is about to hatch...")

    def _get_creature_type(self) -> str:
        """Get the creature type for graphics."""
        # Use legacy creature type if available
        if hasattr(self.pet, 'creature_type') and self.pet.creature_type:
            return self.pet.creature_type

        # Map evolution form to creature type
        form = self.pet.current_form
        if form:
            # Default mappings based on form name patterns
            form_name = form.name.lower()
            if "blob" in form_name:
                return "kibble"
            elif "spark" in form_name:
                return "sparkrat"
            elif "flame" in form_name or "fire" in form_name:
                return "fennix"
            elif "aqua" in form_name or "water" in form_name:
                return "drizzpup"

        return "kibble"  # Default

    def _create_menu(self) -> None:
        """Create the context menu."""
        form = self.pet.current_form
        form_name = form.name if form else "Unknown"

        self.menu = PetMenu(
            parent=self.window.root,
            pet_name=self.pet.name,
            form_name=form_name,
            auto_care_enabled=self.pet.auto_care_enabled,
            is_sleeping=(self.pet.state == PetState.SLEEPING),
            on_feed=self._handle_feed,
            on_play=self._handle_play,
            on_sleep=self._handle_sleep,
            on_wake=self._handle_wake,
            on_stats=self._handle_stats,
            on_evolution_history=self._handle_evolution_history,
            on_auto_care_toggle=self._handle_auto_care_toggle,
            on_settings=self._handle_settings,
            on_quit=self._handle_quit,
        )

    def _check_initial_evolution(self) -> None:
        """Check if pet should evolve on startup (e.g., egg hatch)."""
        if hasattr(self, '_show_egg_hatch') and self._show_egg_hatch:
            # Schedule egg hatch animation
            self.window.schedule(2000, self._trigger_egg_hatch)
            return

        # Check for pending evolution
        target = self.pet.check_evolution_ready()
        if target:
            self._trigger_evolution(target)

    def _trigger_egg_hatch(self) -> None:
        """Trigger egg hatch animation and evolution."""
        # Find baby form
        from core.evolution import check_evolution

        target = check_evolution(
            current_form_id="egg",
            level=1,
            care_style=self.care_tracker.calculate_care_style(),
            care_tracker=self.care_tracker,
        )

        if target:
            self._trigger_evolution(target)

    def _trigger_evolution(self, target_form) -> None:
        """Trigger evolution animation and update."""
        # Set evolving state
        self.pet.set_state(PetState.EVOLVING)

        # Execute evolution
        old_form_id = self.pet.form_id
        success = self.pet.evolve(target_form)

        if success:
            # BlobRenderer automatically uses form_id for rendering
            # so no need to update graphics explicitly

            # Update menu
            form = self.pet.current_form
            if form:
                self.menu.update_pet_info(
                    form_name=form.name,
                    is_sleeping=False,
                )

            # Show evolution notification
            self._show_evolution_notification(target_form)

            print(f"Evolution! {old_form_id} -> {target_form.id}")

        # Return to idle after animation
        self.window.schedule(2000, lambda: self.pet.set_state(PetState.IDLE))

    def _show_evolution_notification(self, target_form) -> None:
        """Show the evolution notification dialog."""
        EvolutionNotificationDialog(
            parent=self.window.root,
            new_form_name=target_form.name,
            new_stage=target_form.stage.name,
            on_dismiss=None,
        )

    # ==================== SCHEDULING ====================

    def _schedule_stat_update(self) -> None:
        """Schedule stat update."""
        self.window.schedule(self.STAT_UPDATE_INTERVAL, self._stat_update_loop)

    def _schedule_autosave(self) -> None:
        """Schedule autosave."""
        self.window.schedule(self.AUTOSAVE_INTERVAL, self._autosave_loop)

    def _schedule_autonomous_check(self) -> None:
        """Schedule autonomous behavior check."""
        self.window.schedule(self.AUTONOMOUS_CHECK_INTERVAL, self._autonomous_check_loop)

    def _schedule_evolution_check(self) -> None:
        """Schedule evolution check."""
        self.window.schedule(self.EVOLUTION_CHECK_INTERVAL, self._evolution_check_loop)

    # ==================== UPDATE LOOPS ====================

    def _on_frame_update(self, delta_time: float) -> None:
        """Called each animation frame."""
        # Update animation engine - returns dict of animated values
        anim_values = self.animation.update(delta_time)

        # Update animation state from engine values
        self._animation_state["phase"] = anim_values.get("limb_phase", 0.0)
        self._animation_state["bounce"] = anim_values.get("position_y", 0.0)

        # Update thought bubble
        self.pet.update_thought_bubble()

        # Render
        self._render()

    def _stat_update_loop(self) -> None:
        """Update pet stats periodically."""
        current_time = time.time()
        delta = current_time - self._last_stat_time
        self._last_stat_time = current_time

        self.pet.update(delta)

        # Record stats for care tracking
        self.care_tracker.record_snapshot(
            hunger=self.pet.stats.hunger,
            happiness=self.pet.stats.happiness,
            energy=self.pet.stats.energy,
        )

        self._schedule_stat_update()

    def _autosave_loop(self) -> None:
        """Autosave pet state."""
        self._save()
        self._schedule_autosave()

    def _autonomous_check_loop(self) -> None:
        """Check for autonomous behavior."""
        action = self.pet.autonomous_check()
        if action:
            self.pet.perform_autonomous_action(action)

            # Record care action
            from core.care_tracker import CareEventType
            if action.name == "FIND_FOOD":
                self.care_tracker.record_feed()
            elif action.name == "SELF_PLAY":
                self.care_tracker.record_play()
            elif action.name == "TAKE_NAP":
                self.care_tracker.record_sleep_start()

        self._schedule_autonomous_check()

    def _evolution_check_loop(self) -> None:
        """Check for evolution readiness."""
        target = self.pet.check_evolution_ready()
        if target:
            self._trigger_evolution(target)

        self._schedule_evolution_check()

    # ==================== RENDERING ====================

    def _render(self) -> None:
        """Render the pet using the new BlobRenderer."""
        # Use the render_with_animation method which handles
        # building the PetRenderState from pet and animation state
        self.renderer.render_with_animation(
            self.window.canvas,
            self.pet,
            self._animation_state,
        )

    # ==================== EVENT HANDLERS ====================

    def _on_pet_state_change(self, new_state: PetState) -> None:
        """Handle pet state changes."""
        # Map pet state to animation state
        state_map = {
            PetState.IDLE: AnimationState.IDLE,
            PetState.WALKING: AnimationState.WALKING,
            PetState.EATING: AnimationState.EATING,
            PetState.PLAYING: AnimationState.PLAYING,
            PetState.SLEEPING: AnimationState.SLEEPING,
            PetState.HAPPY: AnimationState.HAPPY,
            PetState.TRICK: AnimationState.TRICK,
            PetState.EVOLVING: AnimationState.PLAYING,  # Use playing for evolving
        }

        anim_state = state_map.get(new_state, AnimationState.IDLE)
        self.animation.set_state(anim_state)

        # Update menu sleep state
        self.menu.update_pet_info(is_sleeping=(new_state == PetState.SLEEPING))

    def _handle_click(self) -> None:
        """Handle left click on pet."""
        if self.pet.state not in (PetState.SLEEPING, PetState.EATING, PetState.EVOLVING):
            self.pet.pet()
            self.care_tracker.record_pet()

    def _handle_double_click(self) -> None:
        """Handle double-click on pet."""
        if self.pet.state not in (PetState.SLEEPING, PetState.EATING, PetState.EVOLVING):
            self.pet.do_trick()
            self.care_tracker.record_trick()

    def _handle_right_click(self, x: int, y: int) -> None:
        """Handle right-click to show menu."""
        self.menu.show(x, y)

    def _handle_feed(self) -> None:
        """Handle feed action from menu."""
        if self.pet.state == PetState.SLEEPING:
            self.pet.wake()
        self.pet.feed()
        self.care_tracker.record_feed()

    def _handle_play(self) -> None:
        """Handle play action from menu."""
        if self.pet.state == PetState.SLEEPING:
            self.pet.wake()
        self.pet.play()
        self.care_tracker.record_play()

    def _handle_sleep(self) -> None:
        """Handle sleep action from menu."""
        self.pet.sleep()
        self.care_tracker.record_sleep_start()

    def _handle_wake(self) -> None:
        """Handle wake action from menu."""
        self.pet.wake()
        self.care_tracker.record_sleep_end()

    def _handle_stats(self) -> None:
        """Handle stats action from menu."""
        form = self.pet.current_form
        form_name = form.name if form else "Unknown"
        stage = form.stage.name if form else "Unknown"

        # Calculate XP info
        xp_to_next = self.pet.xp_for_next_level

        pet_data = {
            "name": self.pet.name,
            "form_name": form_name,
            "stage": stage,
            "hunger": self.pet.stats.hunger,
            "happiness": self.pet.stats.happiness,
            "energy": self.pet.stats.energy,
            "level": self.pet.level,
            "xp": self.pet.experience,
            "xp_to_next": xp_to_next,
            "next_evolution_level": get_next_evolution_level(stage),
            "care_style": self.pet.care_style.name if hasattr(self.pet, 'care_style') else "BALANCED",
            "birth_time": self.pet.birth_time,
            "auto_care_enabled": self.pet.auto_care_enabled,
        }

        StatsDialog(
            parent=self.window.root,
            pet_data=pet_data,
        )

    def _handle_evolution_history(self) -> None:
        """Handle evolution history action from menu."""
        # Build history from pet's evolution history
        history_list = []

        for entry in self.pet.evolution_history:
            form = get_form_by_id(entry.to_form)
            if form:
                history_list.append({
                    "form_id": entry.to_form,
                    "form_name": form.name,
                    "stage": form.stage.name,
                    "timestamp": entry.timestamp,
                })

        EvolutionHistoryDialog(
            parent=self.window.root,
            evolution_history=history_list,
            current_form=self.pet.form_id,
        )

    def _handle_settings(self) -> None:
        """Handle settings action from menu."""
        SettingsDialog(
            parent=self.window.root,
            auto_care_enabled=self.pet.auto_care_enabled,
            on_auto_care_toggle=self._handle_auto_care_toggle,
        )

    def _handle_auto_care_toggle(self, enabled: bool) -> None:
        """Handle auto-care toggle."""
        self.pet.set_auto_care(enabled)
        self._save()

    def _handle_quit(self) -> None:
        """Handle quit action."""
        self._save()
        self.window.close()

    # ==================== PERSISTENCE ====================

    def _save(self) -> None:
        """Save current state."""
        pet_data = self.pet.to_dict()
        settings = {"auto_care_enabled": self.pet.auto_care_enabled}

        self.save_manager.save(
            pet_data=pet_data,
            care_tracker=self.care_tracker,
            settings=settings,
        )

    def run(self) -> None:
        """Start the application."""
        form = self.pet.current_form
        form_name = form.name if form else "Unknown"

        print(f"Starting Floob 2.0: {self.pet.name} the {form_name}")
        print("Right-click for menu, left-click to pet, double-click for tricks!")

        try:
            self.window.run()
        except KeyboardInterrupt:
            self._handle_quit()


def main() -> None:
    """Main entry point."""
    print("=" * 50)
    print("  FLOOB 2.0 - Desktop Virtual Pet with Evolution")
    print("=" * 50)

    app = Floob()
    app.run()


if __name__ == "__main__":
    main()
