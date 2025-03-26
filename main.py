import numpy as np
from psychopy import core, event, monitors, visual
from psychopy.tools.monitorunittools import pix2deg
from typing import Literal

from config import config

# Constants
WINDOW_SIZE = config.monitor.resolution_px
CENTER = config.display.center_deg
NUM_WOLVES = config.wolf.count

# set up monitor
mon = monitors.Monitor("testMonitor")
mon.setSizePix(WINDOW_SIZE)
mon.setWidth(config.monitor.width_cm)
mon.setDistance(config.monitor.viewing_distance_cm)
mon.saveMon()

width_pix, height_pix = mon.getSizePix()
width_deg = pix2deg(width_pix, mon)
height_deg = pix2deg(height_pix, mon)

# make sure that the wolves don't go out of bounds and bounce off the edges
HORIZONTAL_BOUNDARY = width_deg / 2 - config.wolf.size / 2
VERTICAL_BOUNDARY = height_deg / 2 - config.wolf.size / 2


class Wolf:
    """The wolf is a chevron that moves randomly (but smoothly) and either
    faces towards the sheep or 90 degrees away from the sheep.
    """

    def __init__(
        self,
        window: visual.Window,
        pos: tuple[float, float] | None = None,
        speed: float = config.wolf.speed,
        color: tuple[float, float, float] = config.wolf.color,
        size: float = config.wolf.size,
        vertices: list[tuple[float, float]] = config.wolf.vertices,
        direction_noise: float = config.wolf.direction_noise,
    ) -> None:
        if pos is None:
            pos = [
                np.random.uniform(-HORIZONTAL_BOUNDARY, HORIZONTAL_BOUNDARY),
                np.random.uniform(-VERTICAL_BOUNDARY, VERTICAL_BOUNDARY),
            ]

        self.stimulus = visual.ShapeStim(
            window,
            vertices=vertices,
            fillColor=color,
            pos=pos,
            size=size,
        )
        self.speed = speed

        # initialize direction with random value in radians
        self.direction = np.random.uniform(0, 2 * np.pi)
        self.direction_noise = direction_noise

    def calculate_facing_angle(
        self,
        target_pos: tuple[float, float],
        units: Literal["deg", "rad"] = config.display.units,
    ) -> float:
        """Calculates the angle to the target in radians.

        Args:
            target_pos (tuple): The x, y coordinate of the target
            units (Literal["deg", "rad"]): The angle's units

        Returns:
            float: The angle to the target (degrees or radians)
        """
        # Calculate angle to the target and convert to degrees
        # 0° is horizontal, 90° is vertical (counter-clockwise)
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]

        angle = np.degrees(np.arctan2(dy, dx))

        # Convert to PsychoPy's clockwise orientation system
        angle = (90 - angle) % 360  # 0° is vertical, clockwise is positive

        # Output in desired units
        return angle if units == "deg" else np.radians(angle)

    def update(
        self,
        target_pos: tuple[float, float],
        face_sheep: bool,
    ) -> None:
        """Updates the wolf's position and direction for the current frame.

        Args:
            target_pos (tuple): The x, y coordinate of the target
            face_sheep (bool): Whether the wolf should face the sheep or 90 degrees away
        """
        new_pos = self.pos + np.array(
            [np.cos(self.direction) * self.speed, np.sin(self.direction) * self.speed]
        )

        self.pos = new_pos  # automatically keeps within bounds!

        # Gradually adjust direction with some randomness
        self.direction += np.random.normal(0, self.direction_noise)

        angle_to_sheep_deg = self.calculate_facing_angle(
            target_pos, units=config.display.units
        )
        self.ori = angle_to_sheep_deg if face_sheep else angle_to_sheep_deg + 90

    def draw(self) -> None:
        self.stimulus.draw()

    # We use properties for convenience
    @property
    def pos(self) -> tuple[float, float]:
        return self.stimulus.pos

    @pos.setter
    def pos(self, new_pos: tuple[float, float]) -> None:
        """Sets the position of the wolf, keeping it within bounds.

        Args:
            new_pos (tuple): The new position of the wolf
        """

        # Check if we hit a boundary and need to bounce off in the opposite direction
        if abs(new_pos[0]) > HORIZONTAL_BOUNDARY:
            self.direction = np.pi - self.direction

        if abs(new_pos[1]) > VERTICAL_BOUNDARY:
            self.direction = -self.direction

        # Keep in bounds
        bounded_x = np.clip(new_pos[0], -HORIZONTAL_BOUNDARY, HORIZONTAL_BOUNDARY)
        bounded_y = np.clip(new_pos[1], -VERTICAL_BOUNDARY, VERTICAL_BOUNDARY)

        self.stimulus.pos = (bounded_x, bounded_y)

    @property
    def ori(self) -> float:
        return self.stimulus.ori

    @ori.setter
    def ori(self, new_ori: float) -> None:
        self.stimulus.ori = new_ori


class Sheep:
    """The sheep is a circle that tracks the mouse within the boundaries defined."""

    def __init__(
        self,
        window: visual.Window,
        pos: tuple[float, float] | None = None,
    ) -> None:
        if pos is None:
            pos = CENTER
        self.window = window
        self.stimulus = visual.Circle(
            window,
            radius=config.sheep.radius,
            fillColor=config.sheep.color,
            pos=CENTER,
        )
        self.mouse = event.Mouse(win=window)
        self.last_mouse_x, self.last_mouse_y = self.mouse.getPos()

    def update(self) -> None:
        """Updates the sheep's position based on the mouse's position."""
        current_mouse_x, current_mouse_y = self.mouse.getPos()

        # Get mouse movement since last frame
        delta_x = current_mouse_x - self.last_mouse_x
        delta_y = current_mouse_y - self.last_mouse_y

        # Update sheep position based on movement since last frame
        new_x = self.pos[0] + delta_x
        new_y = self.pos[1] + delta_y

        self.pos = (new_x, new_y)  # automatically keeps within bounds!

        # Update last mouse position
        self.last_mouse_x, self.last_mouse_y = current_mouse_x, current_mouse_y

    def draw(self) -> None:
        self.stimulus.draw()

    @property
    def pos(self) -> tuple[float, float]:
        return self.stimulus.pos

    @pos.setter
    def pos(self, new_pos: tuple[float, float]) -> None:
        """Sets the position of the sheep within the boundaries defined.

        Args:
            new_pos (tuple): The new position of the sheep
        """
        bounded_x = np.clip(new_pos[0], -HORIZONTAL_BOUNDARY, HORIZONTAL_BOUNDARY)
        bounded_y = np.clip(new_pos[1], -VERTICAL_BOUNDARY, VERTICAL_BOUNDARY)

        self.stimulus.pos = (bounded_x, bounded_y)


def main(face_sheep: bool = True) -> None:
    """The main function that runs the demo."""
    win = visual.Window(
        monitor=mon,
        size=WINDOW_SIZE,
        color=config.display.bg_color,
        units=config.display.units,
        allowGUI=config.display.allow_gui,
        screen=config.display.screen,
        fullscr=config.display.full_screen,
    )

    # Need to set mouse visibility after creating the window
    # __init__ doesn't take it as an argument
    win.mouseVisible = config.display.mouse_visible

    sheep = Sheep(win)
    wolves = [Wolf(win) for _ in range(NUM_WOLVES)]

    while not event.getKeys(keyList=config.keys.quit):
        if event.getKeys(keyList=config.keys.toggle_condition):
            face_sheep = not face_sheep

        sheep.update()

        for wolf in wolves:
            wolf.update(sheep.pos, face_sheep)

        sheep.draw()
        for wolf in wolves:
            wolf.draw()
        win.flip()

    win.close()


if __name__ == "__main__":
    main(face_sheep=False)
