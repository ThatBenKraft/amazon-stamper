import itertools
import time

from motors import stepper

stepper.board_setup()

PINS = (17, 22, 23, 27)

combinations = list(itertools.permutations(PINS, 4))

print(f"All combos: {combinations}")

time.sleep(1)


# new_sequence = stepper.Sequences.WHOLESTEP

# for combo in combinations:
#     print(f"Current combo: {combo}")

#     motor = stepper.Motor(combo)  # type: ignore

#     stepper.step_motor(motor, 96, 1, delay=stepper.MINIMUM_STEP_DELAY * 5)

#     stepper.step_motor(motor, 1, 1, stepper.Sequences.UNLOCK)

#     time.sleep(0.5)


LEAD_MOTOR = stepper.Motor(PINS)
print(f"Pins: {LEAD_MOTOR.pins}")

time.sleep(1)

stepper.step_motor(LEAD_MOTOR, 8 * 50, 1, delay=0.01)

time.sleep(1)

stepper.board_cleanup()
