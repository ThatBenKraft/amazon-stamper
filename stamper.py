#!/usr/bin/env python
"""
# Stamper
Allows for full control of stamper robot. Chassis object controls wheel 
position and orientation.
"""

import time
from math import copysign

import RPi.GPIO as GPIO

from motors import stepper

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.1.0"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"

# Defines directions
CLOCKWISE = stepper.Directions.CLOCKWISE
COUNTER_CLOCKWISE = stepper.Directions.COUNTER_CLOCKWISE
UP = CLOCKWISE
DOWN = COUNTER_CLOCKWISE
LEFT = COUNTER_CLOCKWISE
RIGHT = CLOCKWISE

# Defines board pins
VERTICAL_MOTOR_PINS = (17, 22, 23, 27)
HORIZONTAL_MOTOR_PINS = (5, 6, 12, 13)
STAMPER_WHEEL_PINS = (16, 19, 20, 26)
HORIZONTAL_LIMIT_PIN = 4

SENSOR_DELAY = 0.05

_found_limit = False


# Sets up motors
stepper.board_setup()


class StepCounts:
    """
    A class used by the chassis to measure distances and angles.
    """

    INK_DIP = 950
    FLOOR_DIP = 1200
    INK_WIDTH = 400
    CHARACTER_WIDTH = 500
    ADVANCE_CHARACTER = 12.5


def main():
    """
    Runs main stamper actions.
    """
    # Creates chassis object
    chassis = Chassis("0")
    # Acquires code from command line
    code = get_code(chassis)
    # Zeros out horizontal
    chassis.zero_horizontal()
    # Defines starting character
    prev_character = "0"
    # For each character in code:
    for index, character in enumerate(code):
        # Moves wheel to character
        chassis.advance_to_character(character)
        # Re-inks if nessesary
        if not character == prev_character or not index:
            chassis.re_ink()
        # Advances past ink pad on first character
        if not index:
            chassis.move_horizontal(StepCounts.INK_WIDTH, RIGHT)
        # Shifts to next position
        chassis.move_horizontal(StepCounts.CHARACTER_WIDTH, RIGHT)
        # Dips chassis
        chassis.dip(StepCounts.FLOOR_DIP)


class Chassis:
    """
    A class for controlling the stamper chassis horizonal, vertical, and wheel
    movements.
    """

    # Constants for number of steps

    # Characters in wheel
    CHARACTERS = [character for character in "0123456789ABCDEF"]
    NUM_CHARACTERS = len(CHARACTERS)
    # Defines default sequence and rpm for movement
    SEQUENCE = stepper.Sequences.HALFSTEP
    TRAVEL_RPM = 70
    WHEEL_RPM = 20
    # Creates motor object
    CHARACTER_MOTOR = stepper.Motor(STAMPER_WHEEL_PINS)
    HORIZONTAL_MOTOR = stepper.Motor(HORIZONTAL_MOTOR_PINS)
    VERTICAL_MOTOR = stepper.Motor(VERTICAL_MOTOR_PINS)

    def __init__(self, current_character: str) -> None:
        """
        A class for controlling the stamper chassis horizonal, vertical, and wheel
        movements.
        """
        self.character_index = self._index(current_character)
        # Sets up limit switches
        GPIO.setup(HORIZONTAL_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # type: ignore

    def advance_wheel(
        self,
        character_difference: int = 1,
        difference_direction: int = 0,
        delay: float = 0,
    ):
        """
        Advances wheel one character in specified direction.
        """
        # Acquires direction from difference
        if not difference_direction:
            direction = int(copysign(1, character_difference))
        else:
            direction = difference_direction
        # For each difference:
        for _ in range(abs(character_difference)):
            # Advances wheel one character in direction
            stepper.step_motor(
                motor=self.CHARACTER_MOTOR,
                num_steps=StepCounts.ADVANCE_CHARACTER,
                direction=-direction,
                sequence=stepper.Sequences.HALFSTEP,
                rpm=self.WHEEL_RPM,
            )
            time.sleep(delay)

    def advance_to_character(self, new_character: str, report: bool = False) -> None:
        """
        Advances wheel from current character to new character.
        """
        # Finds index of new character
        new_index = self._index(new_character)
        # Finds difference between positions
        character_difference = new_index - self.character_index
        # Re-assigns current character
        self.character_index = new_index
        # Defines direction of wheel movement
        difference_direction = int(copysign(1, character_difference))
        # Checks that character movement is needed
        if not character_difference:
            print("No turning needed for wheel!")
            return

        print(f"Old difference: {character_difference}")
        # Optimizes difference to take shortest path
        if abs(character_difference) > self.NUM_CHARACTERS // 2:
            character_difference += self.NUM_CHARACTERS * -difference_direction
        print(f"New difference: {character_difference}")
        # Reports amount wheel will advance
        if report:
            # Defines direction name
            direction_name = "forwards" if character_difference > 0 else "backwards"
            # Prints statement
            print(f"Turning wheel {direction_name} {character_difference} stages!")
        # Advances
        self.advance_wheel(character_difference, difference_direction)

    def _index(self, character: str) -> int:
        """
        Finds index of character on wheel.
        """
        # Checks for invalid character
        if character not in self.CHARACTERS:
            raise ValueError("Charater not on wheel!")
        # Returns appropriate index
        # print(f"Index of {character}: {self.CHARACTERS.index(character)}")
        return self.CHARACTERS.index(character)

    def re_ink(self) -> None:
        """
        Gets ink from pad and returns to original position.
        """
        # Zeros out and records steps
        steps_taken = self.zero_horizontal()
        # Dips to pad
        self.dip(StepCounts.INK_DIP)
        # Moves back to original position
        self.move_horizontal(steps_taken, RIGHT)

    def zero_horizontal(self, num_steps: int = 4) -> int:
        """
        Zeroes horizontal movement against ink pad limit switch. Returns steps
        to the left taken before stopping.
        """
        # Defines variables for loop
        MAX_STEPS = 5000
        steps_taken = 0
        # Reports
        print("Zeroing ...")
        # While pin is not active and number of steps is under max:
        while (
            GPIO.input(HORIZONTAL_LIMIT_PIN) and steps_taken < MAX_STEPS  # type:ignore
        ):
            # Moves horizontally number of steps
            self.move_horizontal(num_steps, LEFT)
            # Adds steps taken
            steps_taken += num_steps
        # Returns total steps taken before stopping
        return steps_taken

    def move_horizontal(self, num_steps: float, direction: int):
        """
        Moves slider horizontally on lead screw.
        """
        stepper.step_motor(self.HORIZONTAL_MOTOR, num_steps, direction)

    def move_vertical(self, num_steps: float, direction: int):
        """
        Moves chassis vertically on lead screws.
        """
        time.sleep(0.5)

        stepper.step_motor(self.VERTICAL_MOTOR, num_steps, direction)

    def dip(self, num_steps: float, delay=0.5):
        """
        Moves chassis down and then up specified number of steps.
        """
        # Locks character motor
        stepper.lock(self.CHARACTER_MOTOR)
        time.sleep(delay)
        self.move_vertical(num_steps, DOWN)
        time.sleep(delay)
        self.move_vertical(num_steps, UP)
        # Unlocks character motor
        stepper.unlock(self.CHARACTER_MOTOR)


def get_code(chassis: Chassis) -> str:
    """
    Gets code from command line.
    """
    while True:
        code = input("Please enter a four-character code to print: ")
        # If code isn't four characters:
        if len(code) != 4:
            print("Code must be four characters long.")
            continue
        # If the code has characters not in list:
        elif any(character.upper() not in chassis.CHARACTERS for character in code):
            print("One or more characters in code not on wheel.")
            continue
        break
    # Returns valid code
    return code


def test_actions(chassis: Chassis) -> None:
    chassis.re_ink()

    chassis.move_horizontal(1000, RIGHT)

    chassis.advance_wheel(3)

    chassis.dip(StepCounts.FLOOR_DIP)

    chassis.move_horizontal(StepCounts.CHARACTER_WIDTH, RIGHT)

    chassis.advance_wheel(-5)

    time.sleep(1)

    chassis.re_ink()

    stepper.board_cleanup()


if __name__ == "__main__":
    try:
        main()
        # test_actions(Chassis("0"))
    except KeyboardInterrupt:
        stepper.board_cleanup()
