#!/usr/bin/env python
"""
# Stamper
Does stuff lol idk.
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
LEFT = CLOCKWISE
RIGHT = COUNTER_CLOCKWISE

# Defines board pins
VERTICAL_MOTOR_PINS = (17, 22, 23, 27)
HORIZONTAL_MOTOR_PINS = (5, 6, 12, 13)
STAMPER_WHEEL_PINS = (16, 19, 20, 26)
BUTTON_PIN = 4

# Defines functional constants
HORIZONTAL_SHIFT_STEPS = 1200

# Sets up motors
stepper.board_setup()
VERTICAL_TRAVEL_MOTORS = stepper.Motor(VERTICAL_MOTOR_PINS)
HORIZONTAL_TRAVEL_MOTOR = stepper.Motor(HORIZONTAL_MOTOR_PINS)


def main():
    """
    Runs main stamper actions.
    """
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # type: ignore
    wheel = Wheel("0")

    time.sleep(1)

    wheel.advance()

    time.sleep(1)

    dip_chassis(600)

    # horizontal_shift(LEFT)

    # time.sleep(1)

    # dip_chassis(200)

    # time.sleep(1)

    # horizontal_shift(RIGHT)

    # time.sleep(1)

    stepper.board_cleanup()


def horizontal_shift(direction: int, num_steps: int = HORIZONTAL_SHIFT_STEPS):
    """
    Moves slider horizontally on lead screw.
    """
    stepper.step_motor(HORIZONTAL_TRAVEL_MOTOR, num_steps, direction)


def dip_chassis(num_steps: int, delay: float = 0.5):
    """
    Moves chassis down and then up specified number of steps.
    """
    stepper.step_motor(VERTICAL_TRAVEL_MOTORS, num_steps, DOWN)
    time.sleep(delay)
    stepper.step_motor(VERTICAL_TRAVEL_MOTORS, num_steps, UP)


class Wheel:
    def __init__(self, current_character: str) -> None:
        self.CHARACTERS = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
        ]

        self.NUM_CHARACTERS = len(self.CHARACTERS)

        self._BASE_STEPS = 25

        self.motor = stepper.Motor(STAMPER_WHEEL_PINS)

        self.current_character = current_character

    def advance(self, direction: int = CLOCKWISE):
        """
        Advances wheel one character in specified direction.
        """
        stepper.step_motor(self.motor, self._BASE_STEPS, direction)

    def roll_to_character(self, new_character: str, delay: float = 0.25) -> None:
        """
        Advances wheel from current character to new character.
        """
        # Finds difference between positions
        difference = self._index(new_character) - self._index(self.current_character)
        # Finds sign of difference
        difference_sign = int(copysign(1, difference))
        # Re-assigns current character
        self.current_character = new_character

        # Optimizes difference to take shortest path
        if abs(difference) > self.NUM_CHARACTERS // 2:
            difference = round(-difference_sign * self.NUM_CHARACTERS + difference)
        # Reports amount wheel will advance
        self._report_turn(difference)
        # For each character stage:
        for _ in range(difference):
            # Advances wheel one stage in correct direction
            self.advance(difference_sign)
            time.sleep(delay)

    def _report_turn(self, difference: int) -> None:
        """
        Reports amount wheel will turn for specified difference.
        """
        if not difference:
            print("No turning needed for wheel!")
            return
        # Defines direction
        direction = "forwards" if difference >= 0 else "backwards"
        # Prints statement
        print(f"Turning wheel {direction} {difference} stages!")

    def _index(self, character: str) -> int:
        """
        Finds index of character on wheel.
        """
        # Checks for invalid character
        if character not in self.CHARACTERS:
            raise ValueError("Charater not on wheel!")
        # Returns appropriate index
        return self.CHARACTERS.index(character)

    def get_characters(self) -> list[str]:
        return self.CHARACTERS


def get_code(wheel: Wheel) -> str:
    while True:
        code = input("Please enter a four-character code to print: ")

        if len(code) != 4:
            print("Code must be four characters long.")
            continue
        # CAN'T FIGURE OUT BASIC LOGIC :(
        """
        for character in code:
            if character.upper() not in wheel.get_characters():
                print("One or more characters in code not on wheel.")
                break
        """
        break

    return code


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stepper.board_cleanup()
