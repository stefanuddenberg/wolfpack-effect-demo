from psychopy import visual, core, event, monitors
import numpy as np

# If the window is not square, the "norm" units will lead to the stimuli
# having the aspect ratio of the window.
WINDOW_SIZE = [800, 800]
CENTER = [0, 0]
BOUNDARY = 0.9  # 1 is max, but we should account for the size of the stimuli
NUM_WOLVES = 8

mon = monitors.Monitor("testMonitor")
mon.setSizePix(WINDOW_SIZE)
mon.setWidth(52)  # Physical width of monitor in cm
mon.setDistance(57)  # Viewing distance in cm
mon.saveMon()  # Save the monitor configuration


class Wolf:
    def __init__(self, window, pos=None):
        if pos is None:
            pos = [np.random.uniform(-0.8, 0.8), np.random.uniform(-0.8, 0.8)]

        self.stimulus = visual.ShapeStim(
            window,
            vertices=[
                (-0.05, -0.05),  # Bottom-left
                (0, 0.05),  # Top-center (point of the chevron)
                (0.05, -0.05),  # Bottom-right
                (0, -0.02),  # Inner bottom-center
                (-0.05, -0.05),  # Back to start to close the shape
            ],  # Chevron shape
            fillColor="red",
            pos=pos,
        )
        self.speed = 0.008
        self.direction = np.random.uniform(0, 2 * np.pi)  # Random initial direction

    def calculate_facing_angle(self, target_pos, units="deg"):
        # Calculate angle to the target in radians
        dx = target_pos[0] - self.stimulus.pos[0]
        dy = target_pos[1] - self.stimulus.pos[1]
        angle = np.degrees(np.arctan2(dy, dx))

        # Convert to PsychoPy's clockwise orientation system
        angle = (90 - angle) % 360  # 0° is vertical, clockwise is positive
        return angle if units == "deg" else np.radians(angle)

    def update(self, target_pos, face_sheep):
        # Smooth movement in current direction
        # Calculate new position
        new_pos = self.stimulus.pos + np.array(
            [np.cos(self.direction) * self.speed, np.sin(self.direction) * self.speed]
        )

        # Check for collisions with boundaries and bounce
        if abs(new_pos[0]) > BOUNDARY:  # Hit left or right wall
            self.direction = np.pi - self.direction  # Reverse x direction
            new_pos[0] = np.clip(new_pos[0], -BOUNDARY, BOUNDARY)

        if abs(new_pos[1]) > BOUNDARY:  # Hit top or bottom wall
            self.direction = -self.direction  # Reverse y direction
            new_pos[1] = np.clip(new_pos[1], -BOUNDARY, BOUNDARY)

        self.stimulus.pos = new_pos

        # Gradually adjust direction with some randomness
        self.direction += np.random.normal(0, 0.1)

        # Point either at sheep or away from sheep based on face_sheep parameter
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
            window, radius=0.05, fillColor="white", pos=CENTER
        )
        self.mouse = event.Mouse(win=window)  # Create mouse object

    def update(self):
        # Update position based on current mouse location
        self.position = self.mouse.getPos()
        self.stimulus.pos = self.position

    def draw(self):
        self.stimulus.draw()

    @property
    def pos(self):
        return self.stimulus.pos


def main(face_sheep=True):
    win = visual.Window(
        WINDOW_SIZE,
        color="gray",
        units="norm",
        allowGUI=False,
        monitor=mon,
        screen=0,
        fullscr=False,
    )

    win.mouseVisible = False

    sheep = Sheep(win)
    wolves = [Wolf(win) for _ in range(NUM_WOLVES)]

    while not event.getKeys(keyList=["escape"]):
        sheep.update()

        for wolf in wolves:
            wolf.update(sheep.pos, face_sheep)

        sheep.draw()
        for wolf in wolves:
            wolf.draw()
        win.flip()

    win.close()


if __name__ == "__main__":
    main(face_sheep=True)
