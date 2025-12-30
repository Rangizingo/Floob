"""
Transparent overlay window for the Desktop Virtual Pet.

Creates a frameless, always-on-top window with transparency support.
"""

import tkinter as tk
from typing import Callable, Optional
import ctypes
import sys


class PetWindow:
    """
    Transparent overlay window for displaying the pet.

    Handles window creation, positioning, dragging, and click events.
    """

    # Window size
    WIDTH = 150
    HEIGHT = 150

    # Transparent background color
    TRANSPARENT_COLOR = "white"

    def __init__(self) -> None:
        """Initialize the pet window."""
        self.root = tk.Tk()
        self.root.title("Desktop Pet")

        # Remove window decorations (frameless)
        self.root.overrideredirect(True)

        # Set window attributes
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-transparentcolor", self.TRANSPARENT_COLOR)

        # Set window size
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Position in bottom-right corner initially
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - self.WIDTH - 100
        y = screen_height - self.HEIGHT - 100
        self.root.geometry(f"+{x}+{y}")

        # Create canvas with transparent background
        self.canvas = tk.Canvas(
            self.root,
            width=self.WIDTH,
            height=self.HEIGHT,
            bg=self.TRANSPARENT_COLOR,
            highlightthickness=0
        )
        self.canvas.pack()

        # Drag state
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_dragging = False

        # Click callbacks
        self._on_left_click: Optional[Callable[[], None]] = None
        self._on_double_click: Optional[Callable[[], None]] = None
        self._on_right_click: Optional[Callable[[int, int], None]] = None

        # Bind mouse events
        self._bind_events()

        # Try to enable click-through for transparent areas (Windows)
        self._setup_click_through()

    def _setup_click_through(self) -> None:
        """
        Setup click-through for transparent areas on Windows.

        This allows clicking through transparent parts of the window.
        """
        if sys.platform != "win32":
            return

        try:
            # Get window handle
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())

            # Extended window styles
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x80000
            WS_EX_TRANSPARENT = 0x20

            # Get current style and add layered style
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)

        except Exception:
            # Ignore errors on non-Windows or if API fails
            pass

    def _bind_events(self) -> None:
        """Bind mouse events to the canvas."""
        # Left click
        self.canvas.bind("<Button-1>", self._on_button_press)
        self.canvas.bind("<ButtonRelease-1>", self._on_button_release)
        self.canvas.bind("<Double-Button-1>", self._on_double_button)

        # Drag
        self.canvas.bind("<B1-Motion>", self._on_drag)

        # Right click
        self.canvas.bind("<Button-3>", self._on_right_button)

    def _on_button_press(self, event: tk.Event) -> None:
        """Handle left mouse button press."""
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._is_dragging = False

    def _on_button_release(self, event: tk.Event) -> None:
        """Handle left mouse button release."""
        if not self._is_dragging and self._on_left_click:
            self._on_left_click()
        self._is_dragging = False

    def _on_double_button(self, event: tk.Event) -> None:
        """Handle double-click."""
        if self._on_double_click:
            self._on_double_click()

    def _on_drag(self, event: tk.Event) -> None:
        """Handle dragging the window."""
        self._is_dragging = True

        # Calculate new position
        delta_x = event.x - self._drag_start_x
        delta_y = event.y - self._drag_start_y

        new_x = self.root.winfo_x() + delta_x
        new_y = self.root.winfo_y() + delta_y

        # Keep within screen bounds
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        new_x = max(0, min(new_x, screen_width - self.WIDTH))
        new_y = max(0, min(new_y, screen_height - self.HEIGHT))

        self.root.geometry(f"+{new_x}+{new_y}")

    def _on_right_button(self, event: tk.Event) -> None:
        """Handle right-click."""
        if self._on_right_click:
            # Pass screen coordinates
            self._on_right_click(event.x_root, event.y_root)

    def set_on_left_click(self, callback: Callable[[], None]) -> None:
        """Set callback for left click."""
        self._on_left_click = callback

    def set_on_double_click(self, callback: Callable[[], None]) -> None:
        """Set callback for double-click."""
        self._on_double_click = callback

    def set_on_right_click(self, callback: Callable[[int, int], None]) -> None:
        """Set callback for right-click (receives x, y coordinates)."""
        self._on_right_click = callback

    def get_position(self) -> tuple[int, int]:
        """
        Get current window position.

        Returns:
            Tuple of (x, y) screen coordinates.
        """
        return self.root.winfo_x(), self.root.winfo_y()

    def set_position(self, x: int, y: int) -> None:
        """
        Set window position.

        Args:
            x: Screen X coordinate.
            y: Screen Y coordinate.
        """
        # Keep within screen bounds
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = max(0, min(x, screen_width - self.WIDTH))
        y = max(0, min(y, screen_height - self.HEIGHT))

        self.root.geometry(f"+{x}+{y}")

    def get_screen_size(self) -> tuple[int, int]:
        """
        Get screen dimensions.

        Returns:
            Tuple of (width, height).
        """
        return self.root.winfo_screenwidth(), self.root.winfo_screenheight()

    def schedule(self, delay_ms: int, callback: Callable[[], None]) -> str:
        """
        Schedule a callback to run after a delay.

        Args:
            delay_ms: Delay in milliseconds.
            callback: Function to call.

        Returns:
            Timer ID that can be used to cancel.
        """
        return self.root.after(delay_ms, callback)

    def cancel_schedule(self, timer_id: str) -> None:
        """
        Cancel a scheduled callback.

        Args:
            timer_id: Timer ID from schedule().
        """
        self.root.after_cancel(timer_id)

    def set_on_close(self, callback: Callable[[], None]) -> None:
        """
        Set callback for window close (WM_DELETE_WINDOW).

        Note: Since we use overrideredirect, this won't normally trigger.
        """
        self.root.protocol("WM_DELETE_WINDOW", callback)

    def close(self) -> None:
        """Close the window."""
        self.root.quit()
        self.root.destroy()

    def run(self) -> None:
        """Start the main event loop."""
        self.root.mainloop()
