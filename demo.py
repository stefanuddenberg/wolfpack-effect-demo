from psychopy import event
from psychopy.visual import Window

from src.config import get_config
from src.agents import Sheep, Wolf
from src.utils import create_window

config = get_config(config_type="demo")


def main() -> None:
    """The main function that runs the demo."""
    win: Window = create_window(config=config)

    sheep: Sheep = Sheep(win, agent_config=config.sheep)
    wolves: list[Wolf] = [
        Wolf(win, agent_config=config.wolf) for _ in range(config.wolf.count)
    ]

    while not event.getKeys(keyList=config.keys.quit):
        if event.getKeys(keyList=config.keys.toggle_condition):
            # Toggle face_target for all wolves
            config.wolf.face_target = not config.wolf.face_target
            for wolf in wolves:
                if hasattr(wolf, "face_target"):
                    wolf.face_target = config.wolf.face_target

        sheep.update()

        for wolf in wolves:
            wolf.update(sheep.pos)

        sheep.draw()
        for wolf in wolves:
            wolf.draw()
        win.flip()

    win.close()


if __name__ == "__main__":
    main()
