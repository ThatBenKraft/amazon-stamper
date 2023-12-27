#!/usr/bin/env python
"""
## Timing Tests
Exists to approximate the runtime of `Chassis.print_fast()`.
"""

from stamper import NumSteps

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.0.1"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"

total_steps = (
    NumSteps.INK_POSITION
    - NumSteps.SURFACE_MARGIN
    + (NumSteps.SURFACE_MARGIN * 2 + NumSteps.ADVANCE_CHARACTER * 8) * 4
    + NumSteps.INK_WIDTH
    + NumSteps.FLOOR_POSITION
    - NumSteps.SURFACE_MARGIN
    - NumSteps.INK_POSITION
    + NumSteps.CHARACTER_WIDTH * 3
    + (NumSteps.SURFACE_MARGIN * 2 + NumSteps.ADVANCE_CHARACTER * 8) * 4
)

print(f"Steps: {total_steps}")

MOVE_RPM = 80.0
STEPS_PER_REVOLUTION = 200

REVOLUTIONS_PER_SECOND = MOVE_RPM / 60
STEPS_PER_SECOND = REVOLUTIONS_PER_SECOND * STEPS_PER_REVOLUTION
SECONDS_PER_STEP = 1 / STEPS_PER_SECOND

seconds = total_steps * SECONDS_PER_STEP

print(f"Seconds: {seconds}")
