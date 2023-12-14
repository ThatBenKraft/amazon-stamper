#!/usr/bin/env python
"""
## Stamper
Allows for full control of stamper robot. Chassis object controls wheel 
position and orientation.
"""

import time
from math import copysign
from threading import Thread
from typing import Callable

import RPi.GPIO as GPIO

import host
from motors import stepper
from storage import Cells, get_cell, set_cell

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.1.1"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"

CHARACTERS = "0123456789ABCDEF"

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


class NumSteps:
    """
    A class used by the chassis to measure distances and angles.
    """

    # Heights for vertical movement
    FLOOR_HEIGHT = 2552
    INK_HEIGHT = 2192
    RESTING_HEIGHT = 1400
    INK_DIP = INK_HEIGHT - RESTING_HEIGHT
    FLOOR_DIP = FLOOR_HEIGHT - RESTING_HEIGHT
    # Counts for horizontal movement
    INK_WIDTH = 1100
    CHARACTER_WIDTH = 400
    # Count for character advancement
    ADVANCE_CHARACTER = 12.5


class Chassis:
    """
    A class for controlling the stamper chassis horizonal, vertical, and wheel
    movements.
    """

    # Defines default sequence and rpm for movement
    SEQUENCE = stepper.Sequences.HALFSTEP
    MOVE_RPM = 80
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
        self.HORIZONTAL_LIMIT_PIN = 18
        self.VERTICAL_LIMIT_PIN = 4
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
        print(f"Difference: {character_difference}")
        print(f"Direction: {difference_direction}")
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
                num_steps=NumSteps.ADVANCE_CHARACTER,
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
            return
        # Optimizes difference to take shortest path
        if abs(character_difference) > len(CHARACTERS) // 2:
            character_difference += len(CHARACTERS) * -difference_direction
            difference_direction *= -1
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
        if character not in CHARACTERS:
            raise ValueError("Charater not on wheel!")
        # Returns appropriate index
        return CHARACTERS.index(character)

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
        # Defines bottom margin variables
        SLOW_STEPS = 192
        SLOW_FACTOR = 0.3
        bottom_margin = SLOW_STEPS if SLOW_STEPS < num_steps else 0
        # Locks character motor
        if lock:
            stepper.lock(self.WHEEL_MOTOR)
        # Moves down in main and bottom stages
        self.move_vertical(num_steps - bottom_margin, Directions.DOWN)
        self.move_vertical(bottom_margin, Directions.DOWN, self.MOVE_RPM * SLOW_FACTOR)
        # Waits at bottom
        time.sleep(delay)
        # Moves up in bottom and main stages
        self.move_vertical(bottom_margin, Directions.UP, self.MOVE_RPM * SLOW_FACTOR)
        self.move_vertical(num_steps - bottom_margin, Directions.UP)
        # Unlocks character motor
        if lock:
            stepper.unlock(self.WHEEL_MOTOR)

    def re_ink(self) -> None:
        """
        Moves to ink pad to resupply and returns to original position.
        """
        # Zeros out and records steps
        steps_taken = self.zero_horizontal()
        # Dips to pad
        self.dip(NumSteps.INK_DIP)
        # Moves back to original position
        self.move_horizontal(steps_taken, Directions.RIGHT)

    def zero_horizontal(self) -> int:
        """
        Zeroes horizontal movement against side limit switch. Returns steps
        taken before stopping.
        """
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
        # Runs zeroing function
        taken_steps = self._zero(
            self.move_vertical,
            Directions.UP,
            self.VERTICAL_LIMIT_PIN,
        )
        # Move down into position
        self.move_vertical(NumSteps.RESTING_HEIGHT, Directions.DOWN)
        # Returns original vertial position
        return taken_steps

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
        MAX_STEPS = 3000
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

    def zero_simultaneous(self) -> None:
        """
        Zeros in both axes at the same time.
        """
        # Creates threads
        horizontal_thread = Thread(target=self.zero_horizontal)
        vertical_thread = Thread(target=self.zero_vertical)
        # Starts threads
        horizontal_thread.start()
        vertical_thread.start()
        # Joins threads
        horizontal_thread.join()
        vertical_thread.join()

    def print_code(self, code: str) -> None:
        """
        Runs main stamper actions.
        """
        # Zeros out horizontal
        print("Zeroing. . .")
        self.zero_simultaneous()
        # Defines starting character
        prev_character = STARTING_CHARACTER
        # For each character in code:
        for index, character in enumerate(code):
            # Reports character
            print(f"Stamping: [ {character} ]...")
            # Moves wheel to character
            self.advance_to_character(character)
            # Re-inks if nessesary
            if not (character == prev_character and index):
                print("Re-inking. . .")
                self.re_ink()
            # Sets previous character to character
            prev_character = character
            # Defines shift amount with exception for first loop
            horizontal_shift = NumSteps.CHARACTER_WIDTH if index else NumSteps.INK_WIDTH
            # Shifts to next position
            self.move_horizontal(horizontal_shift, Directions.RIGHT)
            # Dips chassis
            self.dip(NumSteps.FLOOR_DIP)


def code_input(characters: list[str]) -> str:
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
    return code.upper()


def main() -> None:
    """
    Runs main stamper actions.
    """
    # Creates and starts flask thread
    flask_thread = Thread(target=host.run_flask)
    flask_thread.start()

    def get_code() -> str:
        """
        Helper function for accessing code fom sheet.
        """
        return str(get_cell(Cells.CODE))

    set_cell(Cells.RUNNING, False)
    # Creates chassis object
    chassis = Chassis(STARTING_CHARACTER)
    # Initializes previous code
    previous_code = get_code()
    # Loops stamping actions
    while True:
        time.sleep(1)
        print("Scanning for new code...")
        # Gets code
        current_code = get_code()
        # If code is different:
        if current_code != previous_code:
            print("NEW CODE, SETTING SHEET")
            # Sets sheet running boolean TRUE
            set_cell(Cells.RUNNING, True)
            # Prints
            time.sleep(1)
            print(f"Printing code: {current_code}")
            chassis.print_code(current_code)
            time.sleep(1)
            # Sets sheet running boolean FALSE
            set_cell(Cells.RUNNING, False)
        # Sets previous code for next loop
        previous_code = current_code


if __name__ == "__main__":
    try:
        main()
    # Catches keyboard interrupt
    except KeyboardInterrupt:
        pass
    finally:
        # Stops flask
        host.stop_flask()
        # Cleans up board
        stepper.board_cleanup()
