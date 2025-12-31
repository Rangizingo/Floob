"""
Test script for Floob 2.0 Graphics Module.

Demonstrates the blob sprite system by rendering different
evolution forms and expressions in a simple Tkinter window.
"""

import tkinter as tk
import math
import time

from graphics import (
    BlobRenderer,
    PetRenderState,
    RenderState,
    create_simple_render_state,
    FORM_APPEARANCES,
    EyeEmotion,
    MouthEmotion,
)


class GraphicsTestApp:
    """Test application for graphics module."""

    def __init__(self) -> None:
        """Initialize the test app."""
        self.root = tk.Tk()
        self.root.title("Floob 2.0 Graphics Test")
        self.root.geometry("800x600")
        self.root.configure(bg="#F0F0F0")

        # Create main frame
        self.main_frame = tk.Frame(self.root, bg="#F0F0F0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=800,
            height=500,
            bg="#FAFAFA",
            highlightthickness=0,
        )
        self.canvas.pack(pady=10)

        # Create controls frame
        self.controls_frame = tk.Frame(self.main_frame, bg="#F0F0F0")
        self.controls_frame.pack(fill=tk.X, padx=10)

        # Form selection
        tk.Label(self.controls_frame, text="Form:", bg="#F0F0F0").pack(side=tk.LEFT)
        self.form_var = tk.StringVar(value="bloblet")
        self.form_menu = tk.OptionMenu(
            self.controls_frame,
            self.form_var,
            *FORM_APPEARANCES.keys(),
            command=self._on_form_change,
        )
        self.form_menu.pack(side=tk.LEFT, padx=5)

        # State selection
        tk.Label(self.controls_frame, text="State:", bg="#F0F0F0").pack(side=tk.LEFT)
        self.state_var = tk.StringVar(value="idle")
        states = ["idle", "walking", "eating", "playing", "sleeping", "happy", "trick"]
        self.state_menu = tk.OptionMenu(
            self.controls_frame,
            self.state_var,
            *states,
            command=self._on_state_change,
        )
        self.state_menu.pack(side=tk.LEFT, padx=5)

        # Mood selection
        tk.Label(self.controls_frame, text="Mood:", bg="#F0F0F0").pack(side=tk.LEFT)
        self.mood_var = tk.StringVar(value="content")
        moods = ["ecstatic", "happy", "content", "neutral", "sad", "miserable"]
        self.mood_menu = tk.OptionMenu(
            self.controls_frame,
            self.mood_var,
            *moods,
            command=self._on_mood_change,
        )
        self.mood_menu.pack(side=tk.LEFT, padx=5)

        # Show all forms button
        self.show_all_btn = tk.Button(
            self.controls_frame,
            text="Show All Forms",
            command=self._show_all_forms,
        )
        self.show_all_btn.pack(side=tk.LEFT, padx=10)

        # Animation toggle
        self.animate_var = tk.BooleanVar(value=True)
        self.animate_check = tk.Checkbutton(
            self.controls_frame,
            text="Animate",
            variable=self.animate_var,
            bg="#F0F0F0",
        )
        self.animate_check.pack(side=tk.LEFT, padx=10)

        # Initialize renderer
        self.renderer = BlobRenderer()

        # Animation state
        self.phase = 0.0
        self.last_time = time.time()
        self.showing_all = False

        # Start animation loop
        self._animate()

    def _on_form_change(self, _: str) -> None:
        """Handle form selection change."""
        self.showing_all = False

    def _on_state_change(self, _: str) -> None:
        """Handle state selection change."""
        self.showing_all = False

    def _on_mood_change(self, _: str) -> None:
        """Handle mood selection change."""
        self.showing_all = False

    def _show_all_forms(self) -> None:
        """Toggle showing all forms at once."""
        self.showing_all = not self.showing_all

    def _animate(self) -> None:
        """Animation loop."""
        # Calculate delta time
        current_time = time.time()
        delta = current_time - self.last_time
        self.last_time = current_time

        # Update phase
        if self.animate_var.get():
            self.phase += delta

        # Clear canvas
        self.canvas.delete("all")

        if self.showing_all:
            self._render_all_forms()
        else:
            self._render_single_form()

        # Schedule next frame (~30 FPS)
        self.root.after(33, self._animate)

    def _render_single_form(self) -> None:
        """Render a single selected form."""
        form_id = self.form_var.get()
        state = self.state_var.get()
        mood = self.mood_var.get()

        # Create render state
        render_state = create_simple_render_state(
            form_id=form_id,
            x=400,
            y=250,
            mood=mood,
            state=state,
            phase=self.phase,
        )

        # Apply animation based on state
        if state == "walking":
            render_state.squash = abs(math.sin(self.phase * 4)) * 0.15
            render_state.offset_y = -abs(math.sin(self.phase * 4)) * 5
        elif state == "happy":
            render_state.offset_y = -abs(math.sin(self.phase * 5)) * 8
            render_state.show_hearts = True
        elif state == "eating":
            render_state.mouth_openness = self.phase
        elif state == "playing":
            render_state.offset_y = -abs(math.sin(self.phase * 6)) * 10
            render_state.show_sparkles = True
        elif state == "sleeping":
            render_state.offset_y = math.sin(self.phase * 0.5) * 2
            render_state.show_zzz = True

        # Add thought bubble for demo
        if state == "idle" and mood in ["sad", "miserable"]:
            render_state.thought_text = "I'm not feeling great..."
            render_state.thought_icon = "\U0001F622"

        # Render
        self.renderer.render(self.canvas, render_state)

        # Draw info text
        self.canvas.create_text(
            400, 480,
            text=f"Form: {form_id} | State: {state} | Mood: {mood}",
            font=("Arial", 12),
            fill="#666666",
        )

    def _render_all_forms(self) -> None:
        """Render all forms in a grid."""
        forms = list(FORM_APPEARANCES.keys())
        cols = 5
        rows = (len(forms) + cols - 1) // cols

        cell_width = 800 // cols
        cell_height = 400 // rows

        for i, form_id in enumerate(forms):
            row = i // cols
            col = i % cols

            x = col * cell_width + cell_width // 2
            y = row * cell_height + cell_height // 2 + 30

            # Create simple render state
            render_state = create_simple_render_state(
                form_id=form_id,
                x=x,
                y=y,
                mood="happy",
                state="idle",
                phase=self.phase + i * 0.3,
            )
            render_state.offset_y = -abs(math.sin(self.phase * 2 + i * 0.5)) * 3

            # Render (create new renderer for each to avoid clearing issues)
            from graphics import EvolutionSpriteRenderer, AnimationParams, EyeParams, MouthParams

            evo_renderer = EvolutionSpriteRenderer()
            animation = AnimationParams(
                wobble_phase=self.phase + i * 0.3,
                offset_y=render_state.offset_y,
            )
            evo_renderer.draw_form(
                self.canvas, x, y, form_id,
                animation=animation,
                eye_params=EyeParams(emotion=EyeEmotion.HAPPY),
                mouth_params=MouthParams(emotion=MouthEmotion.HAPPY),
                phase=self.phase + i * 0.3,
            )

            # Draw form name
            self.canvas.create_text(
                x, y + 45,
                text=form_id,
                font=("Arial", 9),
                fill="#666666",
            )

        # Title
        self.canvas.create_text(
            400, 15,
            text="All Evolution Forms",
            font=("Arial", 14, "bold"),
            fill="#444444",
        )

    def run(self) -> None:
        """Run the test application."""
        self.root.mainloop()


def main() -> None:
    """Main entry point."""
    app = GraphicsTestApp()
    app.run()


if __name__ == "__main__":
    main()
