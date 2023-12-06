# Amazon Scouter 📦🤖

In collaboration with Amazon’s Robotics Team, this project aims to develop a floor-marking robot to scout and place identifying stickers around an Amazon warehouse.

## 🔠 Stamper

The `Chassis` class allows for the full control of the stamper robot. This includes horizontal and vertical wheel movement, as well as character wheel controls for choosing specific characters. It takes a string input of the starting character on the wheel.

- `Chassis.advance_wheel()` - Advances wheel one character in specified direction. Takes character difference and direction as parameters. Optional difference delay parameter.
- `Chassis.advance_to_character()` - Advances wheel from current character to new character. Takes current character as input. Optional parameter to report amount moved.
- `Chassis.move_horizontal()` - Moves slider horizontally on lead screw. Takes number of steps and direction as parameters.
- `Chassis.move_vertical()` - Moves chassis vertically on lead screws. Takes number of steps and direction as parameters.
- `Chassis.dip()` - Moves chassis down and then up. Takes number of steps as parameter. Optional delay parameter.
- `Chassis.zero_horizontal()` - Zeroes horizontal movement against ink pad limit switch. Takes number of steps as parameter. Returns steps taken before stopping.
- `Chassis.re_ink()` - Moves to ink pad to resupply and returns to original position.
