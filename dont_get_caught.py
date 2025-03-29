import math

import numpy as np
from psychopy import core, event, visual
from psychopy.visual import Window

from src.agents import Sheep, Wolf
from src.config import get_config
from src.utils import create_window

config = get_config(config_type="dont_get_caught")
SCORE_MULTIPLIER = 10
TIME_TO_SURVIVE = 10
TEXT_HEIGHT = 0.7


def main() -> None:
    """Don't Get Caught game based on Gao et al. 2010 Experiment 2."""
    clock = core.Clock()

    win: Window = create_window(config=config)

    # Display instructions
    instructions = visual.TextStim(
        win,
        text="Don't get caught by the circle that is hunting you!\n\n"
        f"Survive for {TIME_TO_SURVIVE} seconds to win!\n\n"
        "Press SPACE to toggle whether the blue darts face you.\n\n"
        "Press any key to begin.",
        color="white",
        height=TEXT_HEIGHT,
    )
    instructions.draw()
    win.flip()
    event.waitKeys(timeStamped=True)

    # Game state
    game_over = False
    win_game = False
    score = 0
    target_score = TIME_TO_SURVIVE * SCORE_MULTIPLIER
    score_text = visual.TextStim(win, text=f"Score: {score}", pos=(-8, 8), height=0.7)

    # Timer display
    timer_text = visual.TextStim(
        win,
        text=f"Time: 0.0 / {TIME_TO_SURVIVE}",
        pos=(8, 8),
        height=TEXT_HEIGHT,
        anchorHoriz="right",
    )

    # Player (sheep) that follows the mouse cursor
    player = Sheep(win, agent_config=config.sheep)

    # Create the hunter (wolf) - a nondescript circle that follows the player/cursor
    hunters = [Wolf(win, agent_config=config.wolf)]

    # Distractor setup
    dart_distractors = [
        Wolf(win, agent_config=config.dart_distractors)
        for _ in range(config.dart_distractors.count)
    ]
    circle_distractors = [
        Wolf(win, agent_config=config.circle_distractors)
        for _ in range(config.circle_distractors.count)
    ]

    # All distractors in one list
    distractors = dart_distractors + circle_distractors

    # Start clock
    clock.reset()

    # Main game loop
    while (
        not event.getKeys(keyList=config.keys.quit) and not game_over and not win_game
    ):
        if event.getKeys(keyList=config.keys.toggle_condition):
            config.dart_distractors.face_target = (
                not config.dart_distractors.face_target
            )
            for distractor in dart_distractors:
                if hasattr(distractor, "face_target"):
                    distractor.face_target = config.dart_distractors.face_target

        player.update()

        # Update hunting wolf or wolves (always pursue the player in a heat-seeking fashion)
        for hunter in hunters:
            dx = player.pos[0] - hunter.pos[0]
            dy = player.pos[1] - hunter.pos[1]
            hunter.direction = np.arctan2(dy, dx)

            hunter.update(player.pos)

            # Check collision with player (if so, game over)
            dx = hunter.pos[0] - player.pos[0]
            dy = hunter.pos[1] - player.pos[1]
            distance = math.sqrt(dx**2 + dy**2)

            if distance < (hunter.radius + player.radius):
                game_over = True

        for distractor in distractors:
            distractor.update(player.pos)

        # Update timer and score
        current_time = clock.getTime()
        timer_text.text = f"Time: {current_time:.1f} / {TIME_TO_SURVIVE}"

        score = int(current_time * SCORE_MULTIPLIER)
        score_text.text = f"Score: {score}"

        # Check for win condition (survived for TIME_TO_SURVIVE seconds)
        if score >= target_score:
            win_game = True

        # Draw everything
        for distractor in distractors:
            distractor.draw()
        for hunter in hunters:
            hunter.draw()
        player.draw()  # Draw the player last so it's on top of the others
        score_text.draw()
        timer_text.draw()
        win.flip()

    # Game end screen
    end_text = None
    if win_game:
        end_text = visual.TextStim(
            win,
            text=f"Victory! You survived for {TIME_TO_SURVIVE} seconds!\nYour score: {score}\n\nPress any key to exit.",
            color="green",
            height=TEXT_HEIGHT,
        )
    else:
        end_text = visual.TextStim(
            win,
            text=f"Game Over!\nYou survived for {current_time:.1f} seconds\nYour score: {score}\n\nPress any key to exit.",
            color="red",
            height=TEXT_HEIGHT,
        )

    end_text.draw()
    win.flip()
    event.waitKeys(timeStamped=True)

    win.close()


if __name__ == "__main__":
    main()
