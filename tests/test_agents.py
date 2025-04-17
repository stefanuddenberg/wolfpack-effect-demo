import pytest
import numpy as np
from src.agents import Agent, Wolf, Sheep
from src.config import config
from unittest.mock import Mock, patch

############################
#### Agent Method Tests ####
############################


def test_agent_get_bounded_pos() -> None:
    """Test the _get_bounded_pos method logic directly."""
    # Because Agent is an abstract class, we need to create a
    # minimal *concrete* subclass instance (e.g., Wolf)
    # In addition, we have to bypass its __init__ because it's
    # way too complicated to set up (lots of PsychoPy dependencies
    # that we just don't care about for these tests)
    agent = object.__new__(Wolf)
    # _get_bounded_pos is inherited from Agent and uses global `config`.
    # on reflection, this is not ideal, but given that the display details
    # (the only ones we care about here) are constant across all config types,
    # it's fine for now.

    horizontal_boundary = config.display.horizontal_boundary
    vertical_boundary = config.display.vertical_boundary

    # Test within bounds
    pos_in = (horizontal_boundary / 2, vertical_boundary / 2)
    assert agent._get_bounded_pos(pos_in) == pos_in, "Position within bounds failed"

    # Test outside bounds (positive)
    pos_out_pos = (horizontal_boundary + 0.1, vertical_boundary + 0.1)
    assert agent._get_bounded_pos(pos_out_pos) == (
        horizontal_boundary,
        vertical_boundary,
    ), "Positive out-of-bounds failed"

    # Test outside bounds (negative)
    pos_out_neg = (-horizontal_boundary - 0.1, -vertical_boundary - 0.1)
    assert agent._get_bounded_pos(pos_out_neg) == (
        -horizontal_boundary,
        -vertical_boundary,
    ), "Negative out-of-bounds failed"

    # Test mixed bounds
    pos_mix1 = (horizontal_boundary + 0.1, -vertical_boundary / 2)
    assert agent._get_bounded_pos(pos_mix1) == (
        horizontal_boundary,
        -vertical_boundary / 2,
    ), "Mixed bounds test 1 failed"
    pos_mix2 = (-horizontal_boundary / 2, vertical_boundary + 0.1)
    assert agent._get_bounded_pos(pos_mix2) == (
        -horizontal_boundary / 2,
        vertical_boundary,
    ), "Mixed bounds test 2 failed"


###########################
#### Wolf Method Tests ####
###########################


def test_wolf_calculate_facing_angle() -> None:
    """Test the calculate_facing_angle method logic."""
    # Create a minimal Wolf instance, bypassing __init__ entirely
    wolf = object.__new__(Wolf)

    # Next, we manually set attributes needed by this particular method
    # This one needs `self.pos`, which itself is a property that reads `self.stimulus.pos`
    # so we need self.stimulus.pos, which means we need a mock stimulus
    # Mock is a class from pytest that allows us to create "dummy" objects
    # that simulate the behavior of real objects. In this case, I don't want to
    # have to create a whole actual visual stimulus, since that will make the
    # tests run slowly. Mock objects will allow us to simulate a stimulus.

    wolf.stimulus = Mock()
    wolf.stimulus.pos = (0.0, 0.0)  # Set initial position for the test

    # Test cases (using np.isclose for float comparison to avoid floating point precision issues)
    # Target directly above (0, 1) -> PsychoPy angle 0 deg, real angle 90 deg
    angle_deg = wolf.calculate_facing_angle(target_pos=(0, 1), units="deg")
    assert np.isclose(angle_deg, 0.0), "Angle to target directly above failed"

    # Target directly right (1, 0) -> PsychoPy angle 90 deg, real angle 0 deg
    angle_deg = wolf.calculate_facing_angle(target_pos=(1, 0), units="deg")
    assert np.isclose(angle_deg, 90.0), "Angle to target directly to the right failed"

    # Target bottom left (-1, -1) -> PsychoPy angle 225 deg, real angle... also 225 deg
    angle_deg = wolf.calculate_facing_angle(target_pos=(-1, -1), units="deg")
    assert np.isclose(angle_deg, 225.0), "Angle to target bottom-left failed"

    # Target bottom right (1, -1) -> PsychoPy angle 135 deg, real angle 315 deg
    angle_deg = wolf.calculate_facing_angle(target_pos=(1, -1), units="deg")
    assert np.isclose(angle_deg, 135.0), "Angle to target bottom-right failed"

    # Test radians
    # Target directly above (0, 1) -> PsychoPy angle 0 rad, real angle pi/2 rad
    angle_rad = wolf.calculate_facing_angle(target_pos=(0, 1), units="rad")
    assert np.isclose(angle_rad, 0.0), "Radians angle to target directly above failed"
    # Target directly right (1, 0) -> PsychoPy angle pi/2 rad, real angle 0 rad
    angle_rad = wolf.calculate_facing_angle(target_pos=(1, 0), units="rad")
    assert np.isclose(
        angle_rad, np.pi / 2
    ), "Radians angle to target directly to the right failed"
    # Target bottom left (-1, -1) -> PsychoPy angle 3pi/4 rad, real angle 3pi/4 rad
    angle_rad = wolf.calculate_facing_angle(target_pos=(-1, -1), units="rad")
    assert np.isclose(
        angle_rad, 5 * np.pi / 4
    ), "Radians angle to target bottom-left failed"

    # Target bottom right (1, -1) -> PsychoPy angle 3pi/4 rad, real angle 7pi/4 rad
    angle_rad = wolf.calculate_facing_angle(target_pos=(1, -1), units="rad")
    print(angle_rad)
    assert np.isclose(
        angle_rad, 3 * np.pi / 4
    ), "Radians angle to target bottom-right failed"
