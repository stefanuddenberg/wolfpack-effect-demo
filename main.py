from psychopy import event, visual

from config import config
from agents import Sheep, Wolf


def main(face_sheep: bool = True) -> None:
    """The main function that runs the demo."""
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

    sheep = Sheep(win)
    wolves = [Wolf(win) for _ in range(config.wolf.count)]

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
