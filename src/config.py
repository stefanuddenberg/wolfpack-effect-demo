from dataclasses import dataclass, field
from typing import Literal
from psychopy import monitors
from psychopy.tools.monitorunittools import pix2deg
import math


@dataclass
class ShapeConfig:
    """Base configuration for any shape."""

    color: tuple[float, float, float] | str = "white"
    size: float = 1.0


@dataclass
class CircleConfig(ShapeConfig):
    """Configuration specific to circles."""

    def __post_init__(self):
        self.radius = self.size / 2


@dataclass
class DartConfig(ShapeConfig):
    """Configuration specific to darts (chevrons)."""

    color: tuple[float, float, float] | str = "red"
    size: float = 1.5
    # Chevron vertices
    vertices: list[tuple[float, float]] = field(
        default_factory=lambda: [
            (-0.5, -0.5),  # Bottom-left
            (0, 0.5),  # Top-center
            (0.5, -0.5),  # Bottom-right
            (0, -0.2),  # Inner bottom-center
            (-0.5, -0.5),  # Back to start
        ]
    )


@dataclass
class AgentConfig:
    """Configuration for any agent (wolf or sheep)"""

    speed: float = 0.08
    shape_type: Literal["circle", "dart"] = "circle"
    config: CircleConfig | DartConfig = field(default_factory=lambda: CircleConfig())
    face_target: bool = True  # only relevant for darts
    direction_update_window: float = math.pi / 2  # 90 degrees in radians
    direction_update_interval: tuple[int, int] = (5, 20)  # update every 5-20 frames


@dataclass
class DemoAgentConfig(AgentConfig):
    count: int = 8  # number of wolves for demo


@dataclass
class DisplayConfig:
    width_cm: float = 31.26
    viewing_distance_cm: float = 57
    resolution_px: tuple[int, int] = (1512, 982)
    screen: int = 0
    units: Literal["deg", "rad"] = "deg"
    bg_color: str = "black"
    full_screen: bool = True
    center_deg: tuple[float, float] = (0, 0)
    allow_gui: bool = False
    mouse_visible: bool = False

    def __post_init__(self):
        self.monitor = monitors.Monitor("testMonitor")
        self.monitor.setSizePix(self.resolution_px)
        self.monitor.setWidth(self.width_cm)
        self.monitor.setDistance(self.viewing_distance_cm)
        self.monitor.saveMon()


@dataclass
class KeyConfig:
    quit: list[str] = field(default_factory=lambda: ["escape"])
    toggle_condition: list[str] = field(default_factory=lambda: ["space"])


@dataclass
class Config:
    display: DisplayConfig = DisplayConfig()
    wolf: AgentConfig = field(default_factory=lambda: AgentConfig())
    sheep: AgentConfig = field(default_factory=lambda: AgentConfig())
    keys: KeyConfig = KeyConfig()

    def __post_init__(self):
        width_deg = pix2deg(self.display.resolution_px[0], self.display.monitor)
        height_deg = pix2deg(self.display.resolution_px[1], self.display.monitor)

        # Calculate the boundaries based on the display size
        # Use a default size if wolf is not a dart
        if self.wolf.shape_type == "dart":
            agent_size = self.wolf.config.size
        else:
            agent_size = ShapeConfig().size

        self.display.horizontal_boundary = width_deg / 2 - agent_size / 2
        self.display.vertical_boundary = height_deg / 2 - agent_size / 2


@dataclass
class DemoConfig(Config):
    wolf: DemoAgentConfig = field(
        default_factory=lambda: DemoAgentConfig(
            shape_type="dart", config=DartConfig(color="red")
        )
    )
    sheep: AgentConfig = field(
        default_factory=lambda: AgentConfig(
            shape_type="circle", config=CircleConfig(color="white")
        )
    )


@dataclass
class DontGetCaughtConfig(Config):
    """Configuration for the Don't Get Caught game based on Gao et al. 2010."""

    # Player (green circle following mouse)
    sheep: AgentConfig = field(
        default_factory=lambda: AgentConfig(
            shape_type="circle",
            # make it a little smaller and a different color than the distractors
            config=CircleConfig(color="green", size=0.8),
        )
    )

    # Hunter (nondescript circle that follows player)
    wolf: DemoAgentConfig = field(
        default_factory=lambda: DemoAgentConfig(
            shape_type="circle",
            # keep it the same color as the other distractors
            config=CircleConfig(color="white", size=1.0),
            count=1,
        )
    )

    # Dart distractors (blue darts that may face the player)
    dart_distractors: DemoAgentConfig = field(
        default_factory=lambda: DemoAgentConfig(
            shape_type="dart",
            config=DartConfig(color="#2AB7CA", size=1.2),
            count=7,
            face_target=True,
        )
    )

    # Circle distractors (blue circles that move randomly)
    circle_distractors: DemoAgentConfig = field(
        default_factory=lambda: DemoAgentConfig(
            shape_type="circle",
            config=CircleConfig(color="white", size=1.0),
            count=7,
        )
    )


# Create the configuration instance
config = DemoConfig()


def get_config(config_type: Literal["demo", "dont_get_caught"]) -> Config:
    if config_type == "demo":
        return DemoConfig()
    if config_type == "dont_get_caught":
        return DontGetCaughtConfig()

    return Config()
