import numpy as np
from psychopy import core, event, monitors, visual
from psychopy.tools.monitorunittools import pix2deg

from config import config

# Constants
WINDOW_SIZE = config["monitor"]["resolution_px"]
CENTER = config["display"]["center_deg"]
NUM_WOLVES = config["wolf"]["count"]

# set up monitor
mon = monitors.Monitor("testMonitor")
mon.setSizePix(WINDOW_SIZE)
mon.setWidth(config["monitor"]["width_cm"])
mon.setDistance(config["monitor"]["viewing_distance_cm"])
mon.saveMon()

width_pix, height_pix = mon.getSizePix()
width_deg = pix2deg(width_pix, mon)
height_deg = pix2deg(height_pix, mon)

# make sure that the wolves don't go out of bounds and bounce off the edges
HORIZONTAL_BOUNDARY = width_deg / 2 - config["wolf"]["size"] / 2
VERTICAL_BOUNDARY = height_deg / 2 - config["wolf"]["size"] / 2


class Wolf:
    def __init__(
        self,
        window,
        speed=config["wolf"]["speed"],
        color=config["wolf"]["color"],
        size=config["wolf"]["size"],
        vertices=config["wolf"]["vertices"],
        direction_noise=config["wolf"]["direction_noise"],
        pos=None,
    ):
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

    def calculate_facing_angle(self, target_pos, units="deg"):
        # Calculate angle to the target in radians
        # 0° is horizontal, 90° is vertical (counter-clockwise)
        dx = target_pos[0] - self.stimulus.pos[0]
        dy = target_pos[1] - self.stimulus.pos[1]
        angle = np.degrees(np.arctan2(dy, dx))

        # Convert to PsychoPy's clockwise orientation system
        angle = (90 - angle) % 360  # 0° is vertical, clockwise is positive
        return angle if units == "deg" else np.radians(angle)

    def update(self, target_pos, face_sheep):
        new_pos = self.stimulus.pos + np.array(
            [np.cos(self.direction) * self.speed, np.sin(self.direction) * self.speed]
        )

        if abs(new_pos[0]) > HORIZONTAL_BOUNDARY:
            self.direction = np.pi - self.direction
            new_pos[0] = np.clip(new_pos[0], -HORIZONTAL_BOUNDARY, HORIZONTAL_BOUNDARY)

        if abs(new_pos[1]) > VERTICAL_BOUNDARY:
            self.direction = -self.direction
            new_pos[1] = np.clip(new_pos[1], -VERTICAL_BOUNDARY, VERTICAL_BOUNDARY)

        self.stimulus.pos = new_pos

        # Gradually adjust direction with some randomness
        self.direction += np.random.normal(0, self.direction_noise)

        angle_to_sheep_deg = self.calculate_facing_angle(target_pos, units="deg")
        self.stimulus.ori = (
            angle_to_sheep_deg if face_sheep else angle_to_sheep_deg + 90
        )

    def draw(self):
        self.stimulus.draw()


class Sheep:
    def __init__(self, window):
        self.window = window
        self.stimulus = visual.Circle(
            window,
            radius=config["sheep"]["radius"],
            fillColor=config["sheep"]["color"],
            pos=CENTER,
        )
        self.mouse = event.Mouse(win=window)

    def update(self):
        self.position = self.mouse.getPos()
        self.stimulus.pos = self.position

    def draw(self):
        self.stimulus.draw()

    @property
    def pos(self):
        return self.stimulus.pos


def main(face_sheep=True):
    win = visual.Window(
        size=WINDOW_SIZE,
        color=config["display"]["bg_color"],
        units=config["display"]["units"],
        allowGUI=config["display"]["allow_gui"],
        monitor=mon,
        screen=config["display"]["screen"],
        fullscr=config["display"]["full_screen"],
    )

    # have to set mouse visibility after creating the window
    # __init__ doesn't take it as an argument
    win.mouseVisible = config["display"]["mouse_visible"]

    sheep = Sheep(win)
    wolves = [Wolf(win) for _ in range(NUM_WOLVES)]

    while not event.getKeys(keyList=config["keys"]["quit"]):
        if event.getKeys(keyList=config["keys"]["toggle_condition"]):
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
