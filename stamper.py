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

import webapp
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

STARTING_CHARACTER = "0"

# Sets up board with BCM
stepper.board_setup()


class Directions:
    """
    Establishes stamper movement directions.
    """

    DOWN = stepper.Directions.COUNTER_CLOCKWISE
    UP = stepper.Directions.CLOCKWISE
    LEFT = stepper.Directions.COUNTER_CLOCKWISE
    RIGHT = stepper.Directions.CLOCKWISE


class Pins:
    """
    Establishes extra BCM pins used in stamper.
    """

    HORIZONTAL_LIMIT = 18
    VERTICAL_LIMIT = 4


# Sets up limit switches with internal pull up resistor
for pin in (Pins.HORIZONTAL_LIMIT, Pins.VERTICAL_LIMIT):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # type: ignore


class Motors:
    """
    Establishes motor objects used in stamper.
    """

    STAMPER_WHEEL = stepper.Motor((16, 19, 20, 26))
    HORIZONTAL_MOVE = stepper.Motor((5, 6, 12, 13))
    VERTICAL_MOVE = stepper.Motor((17, 22, 23, 27))


class NumSteps:
    """
    A class used by the chassis to measure distances and angles.
    """

    # Heights for vertical movement
    FLOOR_POSITION = 2552.0
    INK_POSITION = 2192.0
    SURFACE_MARGIN = 200.0
    # Counts for horizontal movement
    INK_WIDTH = 1100.0
    CHARACTER_WIDTH = 400.0
    # Count for character advancement
    ADVANCE_CHARACTER = 12.5
    # Maximum positions
    HORIZONTAL_MAX = 2300.0
    VERTICAL_MAX = FLOOR_POSITION


class Chassis:
    """
    A class for controlling the stamper chassis horizonal, vertical, and wheel
    movements. Poop
    """

    # Defines default sequence and rpm for movement
    SEQUENCE = stepper.Sequences.HALFSTEP
    MOVE_RPM = 80.0
    WHEEL_RPM = 20.0
    CHARACTERS = "0123456789ABCDEF"
    NUM_CHARACTERS = len(CHARACTERS)

    def __init__(self, starting_character: str, zero: bool = True) -> None:
        """
        A class for controlling the stamper chassis horizonal, vertical, and
        wheel movements. Takes starting character as parameter.
        """
        # Sets current character index
        if starting_character.upper() not in self.CHARACTERS:
            raise ValueError("Starting character must be in hexadecimal.")
        else:
            self.current_character = starting_character.upper()
        # Sets current position to max for zeroing
        self.horizontal_position = NumSteps.HORIZONTAL_MAX
        self.vertical_position = NumSteps.VERTICAL_MAX
        # Zeros
        if zero:
            self.zero_vertical()
            self.zero_horizontal()

    def _index_of(self, character: str) -> int:
        """
        Finds index of character on wheel.
        """
        # Checks for invalid character
        if character.upper() not in self.CHARACTERS:
            raise ValueError(f"Charater [ {character} ] not on wheel!")
        # Returns appropriate index
        return self.CHARACTERS.index(character.upper())

    def advance_character_to(self, new_character: str, report: bool = False) -> None:
        """
        Advances wheel from current character to new character. Takes current
        character as input. Optional parameter to report amount moved.
        """
        # Finds distance between positions
        character_distance = self._index_of(new_character) - self._index_of(
            self.current_character
        )
        # Checks that character movement is needed
        if not character_distance:
            if report:
                print(f'Wheel is already on "{new_character}"!')
            return
        # Corrects for large distances
        if abs(character_distance) > self.NUM_CHARACTERS // 2:
            character_distance -= int(copysign(self.NUM_CHARACTERS, character_distance))
        # Reports amount wheel will advance
        if report:
            # Defines direction name
            direction_name = "forwards" if character_distance > 0 else "backwards"
            # Prints statement
            print(f"Turning wheel {direction_name} {abs(character_distance)} stages!")
        # Advances
        self.advance_wheel(character_distance)
        # Re-assigns current character
        self.current_character = new_character

    def advance_wheel(self, character_distance: int = 1, delay: float = 0) -> None:
        """
        Advances wheel one character in specified direction. Takes character
        distance as parameter. Optional delay parameter.
        """
        # Defines direction from sign
        direction = int(copysign(1, character_distance))
        # For each stage:
        for _ in range(abs(character_distance)):
            # Advances wheel one character in direction
            stepper.step_motor(
                motor=Motors.STAMPER_WHEEL,
                num_steps=NumSteps.ADVANCE_CHARACTER,
                direction=direction,
                sequence=self.SEQUENCE,
                rpm=self.WHEEL_RPM,
            )
            time.sleep(delay)

    def move_horizontal(
        self, num_steps: float, direction: int, rpm: float = MOVE_RPM
    ) -> float:
        """
        Moves slider horizontally on lead screw. Takes number of steps and
        direction as parameters. Optional RPM parameter.
        """
        # Defines number of steps moving to the right
        steps_right = num_steps * direction * Directions.RIGHT
        # If steps to the right would not exceed minimum or maximum:
        if 0 <= self.horizontal_position + steps_right <= NumSteps.HORIZONTAL_MAX:
            # Steps in direction
            steps_taken = stepper.step_motor(
                Motors.HORIZONTAL_MOVE,
                num_steps,
                direction,
                self.SEQUENCE,
                rpm,
            )
            # Addes to current position
            self.horizontal_position += steps_taken
        else:
            # Reports invalid movement
            raise ValueError(
                f"Invalid horizontal movement position! Destination must lie between 0 and {NumSteps.HORIZONTAL_MAX}."
            )
        # Returns number of steps taken
        return steps_taken

    def move_vertical(
        self, num_steps: float, direction: int, rpm: float = MOVE_RPM
    ) -> float:
        """
        Moves chassis vertically on lead screws. Takes number of steps and
        direction as parameters. Optional RPM parameter.
        """
        # Defines number of positive steps moving to the right
        steps_down = num_steps * direction * Directions.DOWN
        # If steps to the right would not exceed minumum or maximum:
        if 0 < self.vertical_position + steps_down <= NumSteps.VERTICAL_MAX:
            # Steps in direction
            steps_taken = stepper.step_motor(
                Motors.VERTICAL_MOVE,
                num_steps,
                direction,
                self.SEQUENCE,
                rpm,
            )
            # Addes to current position
            self.vertical_position += steps_taken
        else:
            # Reports invalid movement
            raise ValueError(
                f"Invalid vertical movement position! Destination must lie between 0 and {NumSteps.VERTICAL_MAX}."
            )
        # Returns number of steps taken
        return steps_taken

    def move_horizontal_to(self, step_position: float, rpm: float = MOVE_RPM) -> float:
        """
        Moves slider horizontally on lead screw to desired step position. Takes
        horizontal step position as parameter. Optional RPM parameter.
        """
        # If position is zero:
        if not step_position:
            # Zeros horizontally
            return self.zero_horizontal()
        # Moves difference between new and current position and returns steps taken
        return self.move_horizontal(
            step_position - self.horizontal_position,
            Directions.RIGHT,
            rpm,
        )

    def move_vertical_to(self, step_position: float, rpm: float = MOVE_RPM) -> float:
        """
        Moves slider vertically on lead screw to desired step position. Takes
        vertical step position as parameter. Optional RPM parameter.
        """
        # If position is zero:
        if not step_position:
            # Zeros horizontally
            return self.zero_vertical()
        # Moves difference between new and current position and returns steps taken
        return self.move_horizontal(
            step_position - self.horizontal_position,
            Directions.DOWN,
            rpm,
        )

    def zero_horizontal(self) -> float:
        """
        Zeroes horizontal movement against side limit switch. Returns steps
        taken before stopping.
        """
        print("Zeroing horizontally. . .")
        # Runs zeroing function
        steps_taken = self._zero(
            self.move_horizontal,
            Directions.LEFT,
            Pins.HORIZONTAL_LIMIT,
            self.horizontal_position,
        )
        # Sets position to zero
        self.horizontal_position = 0
        # Returns original horizontal position
        return steps_taken

    def zero_vertical(self) -> float:
        """
        Zeroes vertical movement against top limit switch. Returns steps
        taken before stopping.
        """
        print("Zeroing vertically. . .")
        # Runs zeroing function
        steps_taken = self._zero(
            self.move_vertical,
            Directions.UP,
            Pins.VERTICAL_LIMIT,
            self.vertical_position,
        )
        # Sets position to zero
        self.vertical_position = 0
        # Returns original vertial position
        return steps_taken

    def _zero(
        self,
        move_function: Callable[[float, int], float],
        direction: int,
        limit_pin: int,
        position_guess: float,
    ) -> float:
        """
        Zeroes movement against specified limit switch. Takes moving function,
        direction, and limit switch pin as paramters. Returns steps taken
        before stopping.
        """
        # Defines variables for loop
        STEP_BUFFER = 400
        STEP_INTERVAL = 4
        steps_taken = 0.0
        # While pin is not active and number of steps is under position guess
        # plus max:
        while (
            GPIO.input(limit_pin)  # type:ignore
            and steps_taken < position_guess + STEP_BUFFER
        ):
            # Moves number of steps
            move_function(STEP_INTERVAL, direction)
            # Adds steps taken
            steps_taken += STEP_INTERVAL
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
        # Waits until both threads are finished
        horizontal_thread.join()
        vertical_thread.join()

    def dip(
        self,
        num_steps: float,
        slow_step_fraction: float = 0.5,
        slow_rpm_fraction: float = 0.3,
    ) -> None:
        """
        Moves chassis down and then up. Takes number of steps as parameter.
        Optional slowed number of steps fraction and slowed speed parameters.
        """
        # Calculates new number of steps and rpm for bottom margin
        slow_num_steps = num_steps * slow_step_fraction
        slow_rpm = self.MOVE_RPM * slow_rpm_fraction
        # Moves down and up with a slower bottom portion
        self.move_vertical(num_steps - slow_num_steps, Directions.DOWN)
        self.move_vertical(slow_num_steps, Directions.DOWN, slow_rpm)
        time.sleep(0.5)
        self.move_vertical(slow_num_steps, Directions.UP, slow_rpm)
        self.move_vertical(num_steps - slow_num_steps, Directions.UP)

    def print_slow(self, code: str) -> None:
        """
        Runs main stamper actions, inking between all characters.
        """
        # Zeros out horizontal
        print("Zeroing. . .")
        self.zero_simultaneous()
        self.move_vertical(
            NumSteps.INK_POSITION - NumSteps.SURFACE_MARGIN, Directions.DOWN
        )
        # Defines starting character
        prev_character = STARTING_CHARACTER
        # For each character in code:
        for index, character in enumerate(code):
            # Reports character
            print(f"Stamping: [ {character} ]...")
            # Moves wheel to character
            self.advance_character_to(character)
            # Re-inks if nessesary
            if not (character == prev_character and index):
                print("Re-inking. . .")
                # Zeros out and records steps
                steps_taken = self.zero_horizontal()
                # Dips to pad
                self.dip(NumSteps.SURFACE_MARGIN)
                # Moves back to original position
                self.move_horizontal(steps_taken, Directions.RIGHT)
            # Sets previous character to character
            prev_character = character
            # Defines shift amount with exception for first loop
            horizontal_shift = NumSteps.CHARACTER_WIDTH if index else NumSteps.INK_WIDTH
            # Shifts to next position
            self.move_horizontal(horizontal_shift, Directions.RIGHT)
            # Dips chassis to floor
            self.dip(
                NumSteps.FLOOR_POSITION
                - NumSteps.INK_POSITION
                + NumSteps.SURFACE_MARGIN,
                slow_step_fraction=0.25,
            )

    def print_fast(self, code: str) -> None:
        """
        Runs main stamper actions, inking all characters once at start.
        """
        # Zeros out horizontal
        self.zero_simultaneous()
        # Moves ready to ink
        self.move_vertical_to(NumSteps.INK_POSITION - NumSteps.SURFACE_MARGIN)
        # For each character:
        for character in code:
            print(f"Inking: [ {character} ]...")
            # Advances to character, inks and waits
            self.advance_character_to(character)
            # Inks
            self.dip(NumSteps.SURFACE_MARGIN)
        # Moves away from ink pad
        self.move_horizontal(NumSteps.INK_WIDTH, Directions.RIGHT)
        # Moves ready to print
        self.move_vertical_to(NumSteps.FLOOR_POSITION - NumSteps.SURFACE_MARGIN)
        # For each character
        for index, character in enumerate(code):
            print(f"Printing: [ {character} ]...")
            # If not first loop:
            if index:
                # Shift to next floor posiiton
                self.move_horizontal(NumSteps.CHARACTER_WIDTH, Directions.RIGHT)
            # Advances to character
            self.advance_character_to(character)
            # Prints
            self.dip(NumSteps.SURFACE_MARGIN)


def main() -> None:
    """
    Runs main stamper actions.
    """
    # Creates and starts flask thread
    flask_thread = Thread(target=webapp.run_flask)
    flask_thread.start()
    # Helper function for accessing code fom sheet.
    get_code = lambda: str(get_cell(Cells.CODE))
    # Sets running state to false
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
            chassis.print_fast(current_code)
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
        # Stops flask
        webapp.stop_flask()
        # Cleans up board
        stepper.board_cleanup()
