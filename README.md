# Amazon Stamper 📦🦺🔠

In collaboration with Amazon’s Robotics Team, this project aims to develop a floor-marking robot to scout and place identifying markers around an Amazon warehouse.

Python dependencies: **`RPi.GPIO`**, **`requests`**, **`flask`**, **`flask_wtf`**, **`wtforms`**, **`openpyxl`**

## Stamper Classes

### ↔️ Directions

The `Directions` class contains constants for which way motors should turn so that they result in the corresponding stamper wheel movement. These include `Directions.DOWN`, `Directions.UP`, `Directions.LEFT`, and `Directions.RIGHT`.

### ⚙️ Motors

The `Motors` class contains stepper motor objects used for chassis movement. These include `Motors.STAMPER_WHEEL`, `Motors.HORIZONTAL_MOVE`, and `Motors.VERTICAL_MOVE`.

### 🧮 NumSteps

The `NumSteps` class contains constants corresponding to the number of steps a stepper motor should take for a specific movement type.

### 🔠 Chassis

The `Chassis` class allows for the full control of the stamper capabilities of the robot. This includes horizontal and vertical wheel movement, as well as character wheel controls for choosing specific characters.

- `Chassis.advance_wheel()` - Advances wheel one character in specified direction. Takes character difference and direction as parameters. Optional difference delay parameter.
- `Chassis.advance_character_to()` - Advances wheel from current character to new character. Takes current character as input. Optional parameter to report amount moved.
- `Chassis.move_horizontal()` - Moves slider horizontally on lead screw. Takes number of steps and direction as parameters. Optional RPM parameter.
- `Chassis.move_horizontal_to()` - Moves slider horizontally on lead screw to desired step position. Takes horizontal step position as parameter. Optional RPM parameter.
- `Chassis.move_vertical()` - Moves chassis vertically on lead screws. Takes number of steps and direction as parameters.
- `Chassis.move_vertical_to()` - Moves slider vertically on lead screw to desired step position. Takes vertical step position as parameter. Optional RPM parameter.
- `Chassis.dip()` - Moves chassis down and then up. Takes number of steps as parameter. Optional slowed proportion parameter.
- `Chassis.zero_horizontal()` - Zeroes horizontal movement against side limit switch. Returns steps taken before stopping.
- `Chassis.zero_vertical()` - Zeroes vertical movement against top limit switch. Returns steps taken before stopping.
- `Chassis.re_ink()` - Moves to ink pad to resupply and returns to original position.
- `Chassis.zero_simultaneous()` - Zeros in both axes at the same time.

There are also two methods `Chassis.print_slow` and `Chassis.print_fast`, that attempt two different styles of the code stamping process. The former takes into account the slow-drying ink used and applies ink only directly before each character is printed, meaning the horizontal position changes often. The latter inks all characters that will be needed once before printing begings.

## 💻 Webapp

`webapp.py` uses Flask to locally-host a web interface that takes in all code inputs. This can be accessed by visiting the computer running the script's IP address on its network, or locally at 127.0.0.1:5000. It includes a basic home page, with a form for code entry. Input validation is perfored to ensure the code is 4 characters long, as well as hexadecimal.

Its methods include `run_flask()` and `stop_flask()`.

## 📂 Storage

A small module to allow for small data storage for transfer between the webapp and the stamper within an Excel sheet. Includes constant cells within `Cells`, and has two main methods, `get_cell() and set_cell()`.

## ▶️ Running Stamper

All main actions are run from `stamper.py` By default, it will run `main()`, which starts the webapp, and will run `Chassis.print_fast()` if it detects a new, valid code has been submitted.

## 🎛️ Miscellaneous Testing

`timing_tests.py` exists to approximate the runtime of `Chassis.print_fast()`.
