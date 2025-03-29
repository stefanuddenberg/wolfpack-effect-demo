from abc import ABC, abstractmethod
import numpy as np
from .config import config, AgentConfig, CircleConfig, DartConfig, ShapeConfig
from psychopy import visual, event
from typing import Callable, Literal


class Agent(ABC):
    """The base class for all agents. It is a circle by default."""

    def __init__(
        self,
        window: visual.Window,
        agent_config: AgentConfig,
        pos: tuple[float, float] | None = None,
    ):
        if pos is None:
            pos = config.display.center_deg

        self.window: visual.Window = window
        self.stimulus: visual.BaseVisualStim = self._create_stimulus(
            window, agent_config, pos
        )
        self.frames_until_direction_update: int = (
            self._generate_random_frames_until_direction_update(
                *agent_config.direction_update_interval
            )
        )
        self.frame_counter: int = 0

    def _generate_random_frames_until_direction_update(
        self, min_interval: int, max_interval: int
    ) -> int:
        return np.random.randint(min_interval, max_interval)

    def _create_stimulus(
        self, window: visual.Window, config: AgentConfig, pos: tuple[float, float]
    ) -> visual.BaseVisualStim:
        """Creates the appropriate stimulus based on the shape type.

        Args:
            window: The window to draw the stimulus onto
            config: The agent's configuration
            pos: The stimulus's position

        Returns:
            The created stimulus

        Raises:
            ValueError: If the shape type is unknown
        """
        shape_creators: dict[str, Callable] = {
            "circle": self._create_circle,
            "dart": self._create_dart,
        }

        shape_configs: dict[str, ShapeConfig] = {
            "circle": CircleConfig(),
            "dart": DartConfig(),
        }

        creator: Callable | None = shape_creators.get(config.shape_type)
        if creator is None:
            raise ValueError(f"Unknown shape type: {config.shape_type}")

        config: ShapeConfig | None = shape_configs.get(config.shape_type)
        if config is None:
            raise ValueError(f"Unknown shape type: {config.shape_type}")

        return creator(window, config, pos)

    def _create_circle(
        self, window: visual.Window, config: CircleConfig, pos: tuple[float, float]
    ) -> visual.Circle:
        return visual.Circle(
            window,
            radius=config.radius,
            fillColor=config.color,
            pos=pos,
        )

    def _create_dart(
        self, window: visual.Window, config: DartConfig, pos: tuple[float, float]
    ) -> visual.ShapeStim:
        return visual.ShapeStim(
            window,
            vertices=config.vertices,
            fillColor=config.color,
            size=config.size,
            pos=pos,
        )

    @abstractmethod
    def update(self) -> None:
        """Updates the agent's position and/or other properties
        for the current frame."""
        pass

    def draw(self) -> None:
        self.stimulus.draw()

    @property
    def direction_in_deg(self) -> float:
        """The direction of the agent in degrees."""
        return np.degrees(self.direction)

    @property
    def direction_in_rad(self) -> float:
        """The direction of the agent in radians."""
        return self.direction

    @property
    def pos(self) -> tuple[float, float]:
        """The position of the agent (aka its stimulus's position)."""
        return self.stimulus.pos

    @pos.setter
    def pos(self, new_pos: tuple[float, float]) -> None:
        """Sets the position of the agent, keeping it within bounds."""
        self.stimulus.pos = self._get_bounded_pos(new_pos)

    def _get_bounded_pos(self, new_pos: tuple[float, float]) -> tuple[float, float]:
        """For a given position, returns a valid position that is within bounds."""

        x, y = new_pos
        bounded_x = np.clip(
            x,
            -config.display.horizontal_boundary,
            config.display.horizontal_boundary,
        )
        bounded_y = np.clip(
            y,
            -config.display.vertical_boundary,
            config.display.vertical_boundary,
        )

        return (bounded_x, bounded_y)

    @property
    def ori(self) -> float:
        """The orientation of the agent (aka its stimulus's orientation)."""
        if not hasattr(self.stimulus, "ori"):
            raise AttributeError("Agent has no orientation.")
        return self.stimulus.ori

    @ori.setter
    def ori(self, new_ori: float) -> None:
        """Sets the orientation of the agent."""
        if not hasattr(self.stimulus, "ori"):
            raise AttributeError("Agent has no orientation.")
        self.stimulus.ori = new_ori

    @property
    def color(self) -> tuple[float, float, float] | str:
        """The color of the agent (aka its stimulus's color)."""
        if not hasattr(self.stimulus, "fillColor"):
            raise AttributeError("Agent has no color.")
        return self.stimulus.fillColor

    @color.setter
    def color(self, new_color: tuple[float, float, float] | str) -> None:
        """Sets the color of the agent."""
        if not hasattr(self.stimulus, "fillColor"):
            raise AttributeError("Agent has no color.")
        self.stimulus.fillColor = new_color

    @property
    def radius(self) -> float:
        """The radius of the agent (aka its stimulus's radius)."""
        if not hasattr(self.stimulus, "radius"):
            raise AttributeError("Agent has no radius.")
        return self.stimulus.radius

    @radius.setter
    def radius(self, new_radius: float) -> None:
        """Sets the radius of the agent."""
        if not hasattr(self.stimulus, "radius"):
            raise AttributeError("Agent has no radius.")
        self.stimulus.radius = new_radius


class Wolf(Agent):
    """The wolf is a chevron that moves randomly (but smoothly) and either
    faces towards the sheep or 90 degrees away from the sheep.
    """

    def __init__(
        self,
        window: visual.Window,
        agent_config: AgentConfig,
        pos: tuple[float, float] | None = None,
    ) -> None:
        if pos is None:
            pos = [
                np.random.uniform(
                    -config.display.horizontal_boundary,
                    config.display.horizontal_boundary,
                ),
                np.random.uniform(
                    -config.display.vertical_boundary,
                    config.display.vertical_boundary,
                ),
            ]
        super().__init__(window=window, agent_config=agent_config, pos=pos)

        # Only darts need to know about facingness
        if agent_config.shape_type == "dart":
            self.speed: float = agent_config.speed
            self.direction: float = np.random.uniform(0, 2 * np.pi)
            self.direction_update_window: float = agent_config.direction_update_window
            self.direction_update_interval: tuple[int, int] = (
                agent_config.direction_update_interval
            )
            self.face_target: bool = agent_config.face_target

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
        x, y = self.pos
        target_x, target_y = target_pos
        dx = target_x - x
        dy = target_y - y

        angle = np.degrees(np.arctan2(dy, dx))

        # Convert to PsychoPy's clockwise orientation system
        angle = (90 - angle) % 360  # 0° is vertical, clockwise is positive

        # Output in desired units
        return angle if units == "deg" else np.radians(angle)

    def _update_direction(self) -> None:
        """Updates the direction within the allowed window."""
        # Random angle within our window (centered on current direction)
        max_deviation = self.direction_update_window / 2
        angle_change = np.random.uniform(-max_deviation, max_deviation)
        self.direction = (self.direction + angle_change) % (2 * np.pi)

        # Reset counter and get new random interval
        min_interval, max_interval = self.direction_update_interval
        self.frames_until_direction_update = (
            self._generate_random_frames_until_direction_update(
                min_interval, max_interval
            )
        )
        self.frame_counter = 0

    def update(
        self,
        target_pos: tuple[float, float],
    ) -> None:
        """Updates the wolf's position and direction for the current frame.

        Args:
            target_pos (tuple): The x, y coordinate of the target
        """
        # Only update position and orientation if it's a dart
        if not hasattr(self, "speed"):
            return

        # Update position
        new_pos = self.pos + np.array(
            [np.cos(self.direction) * self.speed, np.sin(self.direction) * self.speed]
        )
        self.pos = new_pos  # automatically keeps within bounds!

        # Check if it's time to update direction
        self.frame_counter += 1
        if self.frame_counter >= self.frames_until_direction_update:
            self._update_direction()

        # Update orientation if it's a dart
        angle_to_target_deg = self.calculate_facing_angle(
            target_pos, units=config.display.units
        )
        self.ori = angle_to_target_deg if self.face_target else angle_to_target_deg + 90

    @property
    def pos(self) -> tuple[float, float]:
        return super().pos

    @pos.setter
    def pos(self, new_pos: tuple[float, float]) -> None:
        """Sets the position of the wolf, keeping it within bounds.
        If the wolf hits a boundary, it will bounce off in the opposite direction.

        Args:
            new_pos (tuple): The new position of the wolf
        """

        # Check if we hit a boundary and need to bounce off in the opposite direction
        x, y = new_pos
        if abs(x) > config.display.horizontal_boundary:
            self.direction = np.pi - self.direction

        if abs(y) > config.display.vertical_boundary:
            self.direction = -self.direction

        # Keep in bounds
        self.stimulus.pos = self._get_bounded_pos(new_pos)


class Sheep(Agent):
    """The sheep is a circle that tracks the mouse within the boundaries defined."""

    def __init__(
        self,
        window: visual.Window,
        agent_config: AgentConfig = config.sheep,
        pos: tuple[float, float] | None = None,
    ) -> None:
        super().__init__(window=window, agent_config=agent_config, pos=pos)
        self.config = agent_config
        self.mouse = event.Mouse(win=window)
        self.last_mouse_x, self.last_mouse_y = self.mouse.getPos()

        if agent_config.shape_type == "dart":
            self.direction = 0.0  # we will update this based on mouse movement

    def update(self) -> None:
        """Updates the sheep's position based on the mouse's position."""
        current_mouse_x, current_mouse_y = self.mouse.getPos()

        # Get mouse movement since last frame
        delta_x = current_mouse_x - self.last_mouse_x
        delta_y = current_mouse_y - self.last_mouse_y

        # Update position based on movement since last frame
        x, y = self.pos
        new_x = x + delta_x
        new_y = y + delta_y

        self.pos = (new_x, new_y)  # automatically keeps within bounds!

        # Update orientation if it's a dart and there's movement
        if self.config.shape_type == "dart" and (abs(delta_x) > 0 or abs(delta_y) > 0):
            # Calculate angle from movement direction and convert to PsychoPy's orientation system
            angle = np.degrees(np.arctan2(delta_y, delta_x))
            self.ori = (90 - angle) % 360

        # Update last mouse position
        self.last_mouse_x, self.last_mouse_y = current_mouse_x, current_mouse_y
