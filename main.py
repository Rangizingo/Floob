"""
Desktop Virtual Pet - Main Entry Point

A charming virtual pet that lives on your desktop.
Features:
- Transparent overlay window
- 15 unique creature types to choose from
- Customizable cute creatures with ears, tail, and accessories
- Stats system (hunger, happiness, energy)
- Multiple animation states
- Autonomous behavior (pet takes care of itself)
- Thought bubbles for autonomous actions
- Right-click context menu for interactions
- JSON persistence for saving/loading state
- Random wandering behavior

Usage:
    python main.py
"""

import time
import random
import sys
from typing import Optional

from pet import Pet, PetState, PetCustomization, AutonomousAction
from window import PetWindow
from graphics import PetGraphics
from animations import AnimationController, AnimationState
from menu import PetMenu
from persistence import PetPersistence
from selection import show_selection_screen, CREATURES


class DesktopPet:
    """
    Main application class that coordinates all components.

    Brings together the pet, window, graphics, animations,
    menu, and persistence systems.
    """

    # Update intervals in milliseconds
    RENDER_INTERVAL = 33  # ~30 FPS
    STAT_UPDATE_INTERVAL = 1000  # 1 second
    AUTOSAVE_INTERVAL = 60000  # 1 minute
    AUTONOMOUS_CHECK_INTERVAL = 3000  # 3 seconds

    def __init__(self, creature_type: str = "kibble") -> None:
        """
        Initialize the desktop pet application.

        Args:
            creature_type: The type of creature to use.
        """
        # Create window first
        self.window = PetWindow()

        # Load or create pet with creature type
        self.persistence = PetPersistence()
        self.pet = self.persistence.load_or_create(
            name=CREATURES.get(creature_type, {}).get("name", "Blobby"),
            creature_type=creature_type
        )

        # If loaded pet doesn't have creature_type, update it
        if not hasattr(self.pet, 'creature_type') or self.pet.creature_type != creature_type:
            self.pet.creature_type = creature_type
            self.pet.name = CREATURES.get(creature_type, {}).get("name", "Blobby")

        # Create graphics system with pet's customization and creature type
        self.graphics = PetGraphics(
            self.window.canvas,
            center_x=PetWindow.WIDTH // 2,
            center_y=PetWindow.HEIGHT // 2,
            customization=self.pet.customization,
            creature_type=self.pet.creature_type
        )

        # Create animation controller
        self.animation = AnimationController()
        self.animation.set_on_animation_complete(self._on_animation_complete)
        self.animation.set_on_position_update(self._on_position_update)

        # Initialize animation position
        x, y = self.window.get_position()
        self.animation.current_x = x
        self.animation.current_y = y

        # Create context menu
        self.menu = PetMenu(
            self.window.root,
            self.pet,
            on_feed=self._handle_feed,
            on_play=self._handle_play,
            on_sleep=self._handle_sleep,
            on_customize=self._handle_customize,
            on_auto_care_toggle=self._handle_auto_care_toggle,
            on_quit=self._handle_quit
        )

        # Connect pet state changes to animation
        self.pet.add_state_callback(self._on_pet_state_change)

        # Bind window events
        self.window.set_on_left_click(self._handle_click)
        self.window.set_on_double_click(self._handle_double_click)
        self.window.set_on_right_click(self._handle_right_click)

        # Timing
        self._last_render_time = time.time()
        self._last_stat_time = time.time()

        # Start update loops
        self._schedule_render()
        self._schedule_stat_update()
        self._schedule_autosave()
        self._schedule_autonomous_check()

        # Initial render
        self._render()

    def _schedule_render(self) -> None:
        """Schedule the next render frame."""
        self.window.schedule(self.RENDER_INTERVAL, self._render_loop)

    def _schedule_stat_update(self) -> None:
        """Schedule the next stat update."""
        self.window.schedule(self.STAT_UPDATE_INTERVAL, self._stat_update_loop)

    def _schedule_autosave(self) -> None:
        """Schedule the next autosave."""
        self.window.schedule(self.AUTOSAVE_INTERVAL, self._autosave_loop)

    def _schedule_autonomous_check(self) -> None:
        """Schedule the next autonomous behavior check."""
        self.window.schedule(self.AUTONOMOUS_CHECK_INTERVAL, self._autonomous_check_loop)

    def _render_loop(self) -> None:
        """Main render loop."""
        current_time = time.time()
        delta_time = current_time - self._last_render_time
        self._last_render_time = current_time

        # Update animation
        anim_data = self.animation.update(delta_time)

        # Check for auto-wander (only if not doing autonomous action)
        if (anim_data.get("should_wander") and
            not self._is_busy() and
            not self.pet.is_performing_autonomous_action):
            self._start_random_walk()

        # Update thought bubble
        self.pet.update_thought_bubble()

        # Render current state
        self._render(anim_data)

        # Schedule next frame
        self._schedule_render()

    def _stat_update_loop(self) -> None:
        """Update pet stats periodically."""
        self.pet.update()

        # Check for state changes based on stats
        self._check_stat_based_state()

        self._schedule_stat_update()

    def _autosave_loop(self) -> None:
        """Autosave pet state periodically."""
        self.persistence.save(self.pet)
        self._schedule_autosave()

    def _autonomous_check_loop(self) -> None:
        """Check for autonomous behavior."""
        # Check if pet should take autonomous action
        action = self.pet.autonomous_check()
        if action:
            self.pet.perform_autonomous_action(action)
            print(f"{self.pet.name} is taking autonomous action: {action.name}")

        self._schedule_autonomous_check()

    def _render(self, anim_data: Optional[dict] = None) -> None:
        """
        Render the pet based on current state.

        Args:
            anim_data: Animation data from controller.
        """
        if anim_data is None:
            anim_data = {
                "state": self.animation.current_state,
                "bounce": 0,
                "blink": False,
                "phase": 0,
                "direction": 1,
            }

        # Update graphics blink state
        self.graphics.blink_state = anim_data.get("blink", False)

        state = anim_data["state"]
        phase = anim_data.get("phase", 0)
        bounce = anim_data.get("bounce", 0)
        direction = anim_data.get("direction", 1)

        # Choose drawing method based on state
        if state == AnimationState.IDLE:
            # Check for negative stat displays
            if self.pet.is_hungry():
                self.graphics.draw_hungry(bounce)
            elif self.pet.is_tired():
                self.graphics.draw_tired(bounce)
            elif self.pet.is_sad():
                # Sad uses hungry visual
                self.graphics.draw_hungry(bounce)
            else:
                self.graphics.draw_idle(bounce)

        elif state == AnimationState.WALKING:
            self.graphics.draw_walking(phase, direction)

        elif state == AnimationState.EATING:
            self.graphics.draw_eating(phase)

        elif state == AnimationState.PLAYING:
            self.graphics.draw_playing(phase)

        elif state == AnimationState.SLEEPING:
            self.graphics.draw_sleeping(phase)

        elif state == AnimationState.HAPPY:
            self.graphics.draw_happy(bounce)

        elif state == AnimationState.TRICK:
            self.graphics.draw_trick(phase)

        # Draw thought bubble if present
        if self.pet.thought_bubble:
            self.graphics.draw_thought_bubble(self.pet.thought_bubble)

    def _check_stat_based_state(self) -> None:
        """Check if pet state should change based on stats."""
        # Auto-sleep if exhausted (only if not already sleeping)
        if self.pet.stats.energy <= 5 and self.pet.state != PetState.SLEEPING:
            self.pet.sleep()

    def _is_busy(self) -> bool:
        """Check if pet is in a state that shouldn't be interrupted."""
        busy_states = {
            AnimationState.EATING,
            AnimationState.PLAYING,
            AnimationState.TRICK,
            AnimationState.SLEEPING,
            AnimationState.WALKING,
        }
        return self.animation.current_state in busy_states

    def _start_random_walk(self) -> None:
        """Start the pet walking to a random location."""
        screen_width, screen_height = self.window.get_screen_size()
        current_x, current_y = self.window.get_position()

        # Random target position
        margin = 50
        target_x = random.randint(margin, screen_width - PetWindow.WIDTH - margin)
        target_y = random.randint(margin, screen_height - PetWindow.HEIGHT - margin)

        # Don't walk if already close
        distance = ((target_x - current_x) ** 2 + (target_y - current_y) ** 2) ** 0.5
        if distance < 100:
            return

        self.animation.start_walk(current_x, current_y, target_x, target_y)
        self.pet.start_walking()

    def _on_animation_complete(self) -> None:
        """Called when a timed animation completes."""
        if self.pet.state != PetState.SLEEPING:
            self.pet.set_state(PetState.IDLE)

    def _on_position_update(self, x: int, y: int) -> None:
        """Called when pet position changes during walking."""
        self.window.set_position(x, y)

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
        }

        anim_state = state_map.get(new_state, AnimationState.IDLE)
        self.animation.set_state(anim_state)

    def _handle_click(self) -> None:
        """Handle left click on pet."""
        if not self._is_busy():
            self.pet.pet()

    def _handle_double_click(self) -> None:
        """Handle double-click on pet."""
        if not self._is_busy():
            self.pet.do_trick()

    def _handle_right_click(self, x: int, y: int) -> None:
        """Handle right-click to show menu."""
        self.menu.show(x, y)

    def _handle_feed(self) -> None:
        """Handle feed action from menu."""
        if self.pet.state == PetState.SLEEPING:
            self.pet.wake()
        self.pet.feed()

    def _handle_play(self) -> None:
        """Handle play action from menu."""
        if self.pet.state == PetState.SLEEPING:
            self.pet.wake()
        self.pet.play()

    def _handle_sleep(self) -> None:
        """Handle sleep action from menu."""
        self.pet.sleep()

    def _handle_customize(self, customization: PetCustomization) -> None:
        """Handle customization changes."""
        # Update graphics with new customization
        self.graphics.set_customization(customization)

        # Save immediately
        self.persistence.save(self.pet)

        print(f"Customization updated: color={customization.body_color}, "
              f"ears={customization.ear_style.value}, "
              f"tail={customization.tail_style.value}, "
              f"accessory={customization.accessory.value}")

    def _handle_auto_care_toggle(self, enabled: bool) -> None:
        """Handle auto-care toggle changes."""
        # Save preference immediately
        self.persistence.save(self.pet)

        status = "enabled" if enabled else "disabled"
        print(f"Auto-care {status} for {self.pet.name}")

    def _handle_quit(self) -> None:
        """Handle quit action from menu."""
        # Save before quitting
        self.persistence.save(self.pet)
        self.window.close()

    def run(self) -> None:
        """Start the application."""
        creature_name = CREATURES.get(self.pet.creature_type, {}).get("name", "Unknown")
        creature_desc = CREATURES.get(self.pet.creature_type, {}).get("description", "")

        print(f"Starting Desktop Pet: {self.pet.name} the {creature_name}")
        print(f"Type: {creature_desc}")
        print("Right-click for menu, left-click to pet, double-click for tricks!")
        print("Drag to move the pet around.")

        try:
            self.window.run()
        except KeyboardInterrupt:
            self._handle_quit()


def main() -> None:
    """Main entry point."""
    # Check persistence for existing save
    persistence = PetPersistence()

    # If no save exists or save doesn't have creature_type, show selection screen
    if not persistence.save_exists() or not persistence.has_creature_type():
        selected_creature = [None]  # Use list to allow modification in closure

        def on_creature_selected(creature_type: str) -> None:
            selected_creature[0] = creature_type

        def on_cancelled() -> None:
            print("Selection cancelled. Exiting.")
            sys.exit(0)

        print("Welcome to Floob! Choose your creature...")
        show_selection_screen(on_creature_selected, on_cancelled)

        if selected_creature[0] is None:
            print("No creature selected. Exiting.")
            sys.exit(0)

        creature_type = selected_creature[0]
        print(f"You chose: {CREATURES[creature_type]['name']}!")

        # Delete old save to start fresh with new creature
        if persistence.save_exists():
            persistence.delete_save()

    else:
        # Load existing creature type from save
        pet = persistence.load()
        if pet:
            creature_type = pet.creature_type
            print(f"Welcome back! Loading your {CREATURES.get(creature_type, {}).get('name', 'pet')}...")
        else:
            creature_type = "kibble"

    # Create and run the desktop pet
    app = DesktopPet(creature_type=creature_type)
    app.run()


if __name__ == "__main__":
    main()
