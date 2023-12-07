#!/usr/bin/env python
"""
# Stamper
Allows for full control of stamper robot. Chassis object controls wheel 
position and orientation.
"""

import time
from math import copysign
from typing import Callable

import RPi.GPIO as GPIO

from motors import stepper

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.1.1"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"


STARTING_CHARACTER = "0"


# Defines directions
class Directions:
    """
    Establishes stamper movement directions.
    """

    DOWN = stepper.Directions.COUNTER_CLOCKWISE
    UP = stepper.Directions.CLOCKWISE
    LEFT = stepper.Directions.COUNTER_CLOCKWISE
    RIGHT = stepper.Directions.CLOCKWISE


class StepCounts:
    """
    A class used by the chassis to measure distances and angles.
    """

    INK_DIP = 950
    FLOOR_DIP = 1300
    INK_WIDTH = 1100
    CHARACTER_WIDTH = 400
    ADVANCE_CHARACTER = 12.5


def main():
    """
    Runs main stamper actions.
    """
    # Creates chassis object
    chassis = Chassis(STARTING_CHARACTER)
    # Zeros out horizontal
    chassis.zero_horizontal()
    # Acquires code from command line
    code = get_code(chassis.CHARACTERS)
    # Defines starting character
    prev_character = STARTING_CHARACTER
    # For each character in code:
    for index, character in enumerate(code):
        # Moves wheel to character
        chassis.advance_to_character(character)
        # Re-inks if nessesary
        if not character == prev_character or not index:
            chassis.re_ink()
        # Defines shift amount with exception for first loop
        horizontal_shift = StepCounts.CHARACTER_WIDTH if index else StepCounts.INK_WIDTH
        # Shifts to next position
        chassis.move_horizontal(horizontal_shift, Directions.RIGHT)
        # Dips chassis
        chassis.dip(StepCounts.FLOOR_DIP)


class Chassis:
    """
    A class for controlling the stamper chassis horizonal, vertical, and wheel
    movements.
    """

    # Characters in wheel
    CHARACTERS = [character for character in "0123456789ABCDEF"]
    NUM_CHARACTERS = len(CHARACTERS)
    # Defines default sequence and rpm for movement
    SEQUENCE = stepper.Sequences.HALFSTEP
    MOVE_RPM = 75
    WHEEL_RPM = 20

    def __init__(self, current_character: str) -> None:
        """
        A class for controlling the stamper chassis horizonal, vertical, and
        wheel movements.
        """
        self.character_index = self._index(current_character)
        # Sets up motors and limit switch
        stepper.board_setup()

        # Creates motor objects
        self.WHEEL_MOTOR = stepper.Motor((16, 19, 20, 26))
        self.HORIZONTAL_MOTOR = stepper.Motor((5, 6, 12, 13))
        self.VERTICAL_MOTOR = stepper.Motor((17, 22, 23, 27))
        # Assigns limit pins
        self.HORIZONTAL_LIMIT_PIN = 4
        self.VERTICAL_LIMIT_PIN = 0
        # Sets up limit switch with internal pull up resistor
        GPIO.setup(self.HORIZONTAL_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # type: ignore
        GPIO.setup(self.VERTICAL_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # type: ignore

    def advance_wheel(
        self,
        character_difference: int = 1,
        difference_direction: int = 0,
        delay: float = 0,
    ) -> None:
        """
        Advances wheel one character in specified direction. Takes character
        difference and direction as parameters. Optional difference delay
        parameter.
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
                motor=self.WHEEL_MOTOR,
                num_steps=StepCounts.ADVANCE_CHARACTER,
                direction=-direction,
                sequence=stepper.Sequences.HALFSTEP,
                rpm=self.WHEEL_RPM,
            )
            time.sleep(delay)

    def advance_to_character(self, new_character: str, report: bool = False) -> None:
        """
        Advances wheel from current character to new character. Takes current
        character as input. Optional parameter to report amount moved.
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
        # Optimizes difference to take shortest path
        if abs(character_difference) > self.NUM_CHARACTERS // 2:
            character_difference += self.NUM_CHARACTERS * -difference_direction
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
        return self.CHARACTERS.index(character)

    def move_horizontal(
        self, num_steps: float, direction: int, rpm: float = MOVE_RPM
    ) -> None:
        """
        Moves slider horizontally on lead screw. Takes number of steps and
        direction as parameters.
        """
        stepper.step_motor(
            self.HORIZONTAL_MOTOR,
            num_steps,
            direction,
            self.SEQUENCE,
            rpm,
        )

    def move_vertical(
        self, num_steps: float, direction: int, rpm: float = MOVE_RPM
    ) -> None:
        """
        Moves chassis vertically on lead screws. Takes number of steps and
        direction as parameters.
        """
        stepper.step_motor(
            self.VERTICAL_MOTOR,
            num_steps,
            direction,
            self.SEQUENCE,
            rpm,
        )

    def dip(self, num_steps: float, delay=0.5, lock: bool = False) -> None:
        """
        Moves chassis down and then up. Takes number of steps as parameter.
        Optional delay parameter.
        """
        # Locks character motor
        if lock:
            stepper.lock(self.WHEEL_MOTOR)
        # time.sleep(delay)
        self.move_vertical(num_steps, Directions.DOWN)
        time.sleep(delay)
        self.move_vertical(num_steps, Directions.UP)
        # Unlocks character motor
        if lock:
            stepper.unlock(self.WHEEL_MOTOR)

    def zero_horizontal(self) -> int:
        """
        Zeroes horizontal movement against side limit switch. Returns steps
        taken before stopping.
        """
        # Reports
        print("Zeroing horizontally. . .")
        # Runs zeroing function
        return self._zero(
            self.move_horizontal,
            Directions.LEFT,
            self.HORIZONTAL_LIMIT_PIN,
        )

    def zero_vertical(self) -> int:
        """
        Zeroes vertical movement against top limit switch. Returns steps
        taken before stopping.
        """
        # Reports
        print("Zeroing vertically. . .")
        # Runs zeroing function
        return self._zero(
            self.move_horizontal,
            Directions.UP,
            self.VERTICAL_LIMIT_PIN,
        )

    def _zero(
        self,
        move_function: Callable[[int, int], None],
        direction: int,
        limit_pin: int,
        num_steps: int = 4,
    ) -> int:
        """
        Zeroes movement against specified limit switch. Takes moving function,
        direction, and limit switch pin as paramters. Returns steps taken
        before stopping.
        """
        # Defines variables for loop
        MAX_STEPS = 5000
        steps_taken = 0
        # While pin is not active and number of steps is under max:
        while (
            GPIO.input(limit_pin)  # type:ignore
            and steps_taken < MAX_STEPS
        ):
            # Moves horizontally number of steps
            move_function(num_steps, direction)
            # Adds steps taken
            steps_taken += num_steps
        # Returns total steps taken before stopping
        return steps_taken

    def re_ink(self) -> None:
        """
        Moves to ink pad to resupply and returns to original position.
        """
        # Zeros out and records steps
        steps_taken = self.zero_horizontal()
        # Dips to pad
        self.dip(StepCounts.INK_DIP)
        # Moves back to original position
        self.move_horizontal(steps_taken, Directions.RIGHT)


def get_code(characters: list[str]) -> str:
    """
    Gets code from command line. Takes character list as parameter.
    """
    while True:
        code = input("Please enter a four-character code to print: ")
        # If code isn't four characters:
        if len(code) != 4:
            print("Code must be four characters long.")
            continue
        # If the code has characters not in list:
        elif any(character.upper() not in characters for character in code):
            print("One or more characters in code not on wheel.")
            continue
        break
    # Returns valid code
    return code


def test_actions(chassis: Chassis) -> None:
    """
    Runs a series of test actions.
    """
    chassis.advance_to_character("5")

    chassis.zero_horizontal()

    chassis.move_horizontal(StepCounts.INK_WIDTH, Directions.RIGHT)

    chassis.dip(StepCounts.FLOOR_DIP)


if __name__ == "__main__":
    try:
        main()
        # test_actions(Chassis(STARTING_CHARACTER))
        stepper.board_cleanup()
    except KeyboardInterrupt:
        stepper.board_cleanup()
