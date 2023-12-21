class NumSteps:
    """
    A class used by the chassis to measure distances and angles.
    """

    # Heights for vertical movement
    FLOOR_POSITION = 2552.0
    INK_POSITION = 2192.0
    SURFACE_SPACING = 200.0
    # Counts for horizontal movement
    PRINT_START = 1100.0
    CHARACTER_WIDTH = 400.0
    # Count for character advancement
    ADVANCE_CHARACTER = 12.5
    # Maximum positions
    HORIZONTAL_MAX = 2300.0
    VERTICAL_MAX = FLOOR_POSITION


total_steps = (
    NumSteps.INK_POSITION
    - NumSteps.SURFACE_SPACING
    + (NumSteps.SURFACE_SPACING * 2 + NumSteps.ADVANCE_CHARACTER * 8) * 4
    + NumSteps.PRINT_START
    + NumSteps.FLOOR_POSITION
    - NumSteps.SURFACE_SPACING
    - NumSteps.INK_POSITION
    + NumSteps.CHARACTER_WIDTH * 3
    + (NumSteps.SURFACE_SPACING * 2 + NumSteps.ADVANCE_CHARACTER * 8) * 4
)

print(f"Steps: {total_steps}")

MOVE_RPM = 80.0
STEPS_PER_REVOLUTION = 200

REVOLUTIONS_PER_SECOND = MOVE_RPM / 60
STEPS_PER_SECOND = REVOLUTIONS_PER_SECOND * STEPS_PER_REVOLUTION
SECONDS_PER_STEP = 1 / STEPS_PER_SECOND

seconds = total_steps * SECONDS_PER_STEP

print(f"Seconds: {seconds}")
