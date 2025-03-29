from .config import get_config, Config, DemoConfig
from psychopy import visual


def create_window(config: Config) -> visual.Window:
    """Create a window for the demo with the given configuration."""
    win = visual.Window(
        monitor=config.display.monitor,
        size=config.display.resolution_px,
        color=config.display.bg_color,
        units=config.display.units,
        allowGUI=config.display.allow_gui,
        screen=config.display.screen,
        fullscr=config.display.full_screen,
    )

    # Need to set mouse visibility after creating the window
    # __init__ doesn't take it as an argument
    win.mouseVisible = config.display.mouse_visible

    return win
