#!/usr/bin/env python
"""
# Stamper
Allows for full control of stamper robot. Chassis object controls wheel 
position and orientation.
"""

import time
from threading import Thread

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


class StageCounts:
    INK_DIP = 1200
    FLOOR_DIP = 1900
    INK_HORIZONTAL = 1800
    CHARACTER_HORIZONTAL = 1000
    ADVANCE_CHARACTER = 25


# Sets up motors
stepper.board_setup()


def main():
    """
    Runs main stamper actions.
    """
    # GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # type: ignore
    chassis = Chassis("0")

    GPIO.setup(HORIZONTAL_LIMIT_PIN, GPIO.IN)  # type: ignore

    level = GPIO.input(HORIZONTAL_LIMIT_PIN)  # type: ignore

    while True:
        print(level)
        time.sleep(0.5)

    # chassis.travel_vertical(200, UP)

    # chassis.advance(-3)

    # time.sleep(1)

    # # chassis.advance(-4)

    # chassis.roll_to_character("A")

    # time.sleep(1)

    # chassis.roll_to_character("B")

    # time.sleep(1)

    # chassis.roll_to_character("D")

    # time.sleep(1)

    # chassis.roll_to_character("0")

    # stepper.board_cleanup()


class Chassis:
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

        self.character_motor = stepper.Motor(STAMPER_WHEEL_PINS)
        self.horizontal_motor = stepper.Motor(HORIZONTAL_MOTOR_PINS)
        self.vertical_motors = stepper.Motor(VERTICAL_MOTOR_PINS)

        self.current_character_index = self._index(current_character)

    def advance(self, difference: int = 1, delay: float = 0.25):
        """
        Advances wheel one character in specified direction.
        """
        for _ in range(abs(difference)):
            # Advances wheel one stage in correct direction
            stepper.step_motor(
                self.character_motor,
                StageCounts.ADVANCE_CHARACTER,
                -difference // abs(difference),
                rpm=20,
            )
            time.sleep(delay)

    def roll_to_character(self, new_character: str) -> None:
        """
        Advances wheel from current character to new character.
        """
        # Finds index of new character
        new_index = self._index(new_character)
        # Finds difference between positions
        difference = new_index - self.current_character_index
        # Checks that character movement is needed
        if not difference:
            print("No turning needed for wheel!")
            return
        # Re-assigns current character
        self.current_character_index = new_index

        print(f"Old difference: {difference}")
        # Optimizes difference to take shortest path
        if abs(difference) > self.NUM_CHARACTERS // 2:
            # difference += self.NUM_CHARACTERS * (difference // abs(difference))
            if difference < 0:
                difference += self.NUM_CHARACTERS
            else:
                difference -= self.NUM_CHARACTERS
        print(f"New difference: {difference}")
        # Reports amount wheel will advance
        self._report_turn(difference)
        # For each character stage:
        self.advance(difference)

    def _index(self, character: str) -> int:
        """
        Finds index of character on wheel.
        """
        # Checks for invalid character
        if character not in self.CHARACTERS:
            raise ValueError("Charater not on wheel!")
        # Returns appropriate index
        print(f"Index of {character}: {self.CHARACTERS.index(character)}")
        return self.CHARACTERS.index(character)

    def _report_turn(self, difference: int) -> None:
        """
        Reports amount wheel will turn for specified difference.
        """
        # Defines direction
        direction = "forwards" if difference >= 0 else "backwards"
        # Prints statement
        print(f"Turning wheel {direction} {difference} stages!")

    def zero_horizontal(self) -> None:
        pass

    def travel_horizontal(self, num_steps, direction: int):
        """
        Moves slider horizontally on lead screw.
        """
        time.sleep(0.5)

        stepper.step_motor(self.horizontal_motor, num_steps, direction)

    def travel_vertical(self, num_steps: int, direction: int):
        """
        Moves chassis vertically on lead screws.
        """
        time.sleep(0.5)

        stepper.step_motor(self.vertical_motors, num_steps, direction)

    def dip(self, num_steps, delay=0.5):
        """
        Moves chassis down and then up specified number of steps.
        """
        # stepper.lock(self.motor)
        time.sleep(0.5)
        self.travel_vertical(num_steps, DOWN)
        time.sleep(delay)
        self.travel_vertical(num_steps, UP)
        # stepper.unlock(self.motor)

    def get_characters(self) -> list[str]:
        return self.CHARACTERS


def get_code(wheel: Chassis) -> str:
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
