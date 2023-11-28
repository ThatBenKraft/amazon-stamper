import time
from math import copysign

from motors import stepper

CLOCKWISE = stepper.Directions.CLOCKWISE
COUNTER_CLOCKWISE = stepper.Directions.COUNTER_CLOCKWISE

UP = CLOCKWISE
DOWN = COUNTER_CLOCKWISE
LEFT = CLOCKWISE
RIGHT = COUNTER_CLOCKWISE


def main():
    """
    Runs main stamper actions.
    """
    stepper.board_setup()

    vertical_travel_motors = stepper.Motor((17, 22, 23, 27))

    horizontal_travel_motor = stepper.Motor((29, 31, 32, 33))

    wheel = Wheel("0")

    code = get_code(wheel)

    stepper.board_cleanup()

    time.sleep(1)


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
            ".",
        ]
        self.NUM_CHARACTERS = len(self.CHARACTERS)

        self._BASE_STEPS = 12

        self._added_step = 0

        self.motor = stepper.Motor((35, 36, 37, 38))

        self.current_character = current_character

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
        self.report_turn(difference)
        # For each character stage:
        for _ in range(difference):
            # Advances wheel one stage in correct direction
            stepper.step_motor(self.motor, self._calculate_steps(), difference_sign)
            time.sleep(delay)

    def report_turn(self, difference: int) -> None:
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

    def _calculate_steps(self) -> int:
        # Alternates between 1 and 0
        self._added_step = 0 if self._added_step else 1
        # Adds step to total
        return self._BASE_STEPS + self._added_step

    def get_characters(self) -> list[str]:
        return self.CHARACTERS


def get_code(wheel: Wheel) -> str:
    while True:
        code = input("Please enter a four-character code to print: ")

        if len(code) != 4:
            print("Code must be four characters long.")
            continue

        for character in code:
            if character not in wheel.get_characters():
                print("One or more characters in code not on wheel.")
                continue

        break

    return code


if __name__ == "__main__":
    main()
