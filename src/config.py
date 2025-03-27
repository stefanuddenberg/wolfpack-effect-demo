from dataclasses import dataclass, field
from typing import Literal
from psychopy import monitors
from psychopy.tools.monitorunittools import pix2deg


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
class WolfConfig:
    count: int = 8
    speed: float = 0.1
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
    direction_noise: float = 0.1


@dataclass
class SheepConfig:
    color: tuple[float, float, float] | str = "white"
    radius: float = 0.5


@dataclass
class KeyConfig:
    quit: list[str] = field(default_factory=lambda: ["escape"])
    toggle_condition: list[str] = field(default_factory=lambda: ["space"])


@dataclass
class Config:
    display: DisplayConfig = DisplayConfig()
    wolf: WolfConfig = WolfConfig()
    sheep: SheepConfig = SheepConfig()
    keys: KeyConfig = KeyConfig()

    def __post_init__(self):
        width_deg = pix2deg(self.display.resolution_px[0], self.display.monitor)
        height_deg = pix2deg(self.display.resolution_px[1], self.display.monitor)

        self.display.horizontal_boundary = width_deg / 2 - self.wolf.size / 2
        self.display.vertical_boundary = height_deg / 2 - self.wolf.size / 2


# Create the configuration instance
config = Config()
