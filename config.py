from dataclasses import dataclass
from typing import Literal


@dataclass
class MonitorConfig:
    width_cm: float = 31.26
    viewing_distance_cm: float = 57
    resolution_px: tuple[int, int] = (1512, 982)


@dataclass
class DisplayConfig:
    screen: int = 0
    units: Literal["deg", "rad"] = "deg"
    bg_color: str = "black"
    full_screen: bool = True
    center_deg: tuple[float, float] = (0, 0)
    allow_gui: bool = False
    mouse_visible: bool = False


@dataclass
class WolfConfig:
    count: int = 8
    speed: float = 0.1
    color: str = "red"
    size: float = 1.5
    vertices: list[tuple[float, float]] | None = None
    direction_noise: float = 0.1

    def __post_init__(self):
        if self.vertices is None:
            self.vertices = [
                (-0.5, -0.5),  # Bottom-left
                (0, 0.5),  # Top-center
                (0.5, -0.5),  # Bottom-right
                (0, -0.2),  # Inner bottom-center
                (-0.5, -0.5),  # Back to start
            ]


@dataclass
class SheepConfig:
    color: str = "white"
    radius: float = 0.5


@dataclass
class KeyConfig:
    quit: list[str] = None
    toggle_condition: list[str] = None

    def __post_init__(self):
        if self.quit is None:
            self.quit = ["escape"]
        if self.toggle_condition is None:
            self.toggle_condition = ["space"]


@dataclass
class Config:
    monitor: MonitorConfig = None
    display: DisplayConfig = None
    wolf: WolfConfig = None
    sheep: SheepConfig = None
    keys: KeyConfig = None

    def __post_init__(self):
        if self.monitor is None:
            self.monitor = MonitorConfig()
        if self.display is None:
            self.display = DisplayConfig()
        if self.wolf is None:
            self.wolf = WolfConfig()
        if self.sheep is None:
            self.sheep = SheepConfig()
        if self.keys is None:
            self.keys = KeyConfig()


# Create the configuration instance
config = Config()
