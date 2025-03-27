from psychopy import event, visual

from config import config
from agents import Sheep, Wolf
from utils import create_window


def main(face_sheep: bool = True) -> None:
    """The main function that runs the demo."""
    win = create_window(config=config)

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
