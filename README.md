# Amazon Stamper 📦🦺🔠

In collaboration with Amazon’s Robotics Team, this project aims to develop a floor-marking robot to scout and place identifying markers around an Amazon warehouse.

Python dependencies: **`RPi.GPIO`**, **`requests`**, **`flask`**, **`flask_wtf`**, **`wtforms`**, **`openpyxl`**

## 🗺️ Introduction

<img width="350" height="175" alt="warehouse_wide" align="right" src="https://github.com/user-attachments/assets/71442edb-67d7-41ad-a8c3-84db597c64b8" />

This project follows a senior design capstone led by myself, Shiv Khanna, Marc Alenn Jean Mary, and Tristan Martello, under the guidance of Amazon Robotics. Once a new Amazon warehouse is built, thousands of markings must be placed on the floor to indicate the locations and orientations of various systems. Amazon’s current method for placing these markings is slow, expensive, and inefficient, so our goal for this project was to create a robot that can complete this process autonomously, quickly, and consistently.

<br clear="right"/>

## 👥 User Needs & Engineering Requirements

The design process for the autonomous floor marking system needed to prioritize key user needs to address the challenges outlined in the problem statement effectively. Our project had two primary user teams, each with a separate set of needs: the Amazon Robotics team and the fiducial-placing team. The Amazon Robotics team oversees how robots work within the warehouses and manages safety, integration, and feasibility. The fiducial-placing team is currently the group of employees responsible for placing robot fiducials after the floor has been marked by the survey team. The teams' needs, as well as how we interpreted them into engineering requirements, are explored in the tables below.

<div align="center">
  <img width="629" height="329" alt="needs_table" src="https://github.com/user-attachments/assets/239ba482-59c6-40ec-94b3-64b6613d44b4" />
</div>

## 💭 Concept Generation

Since there were no strict limitations from Amazon’s team, we attempted to come up with as many viable material ideas as possible. Our six contenders were spray paint, markers, laser engraving, dust/chalk, stickers, and stamps. We then began a large list of pros and cons, which might have been that the material was cheap and easy to restock, but incredibly difficult conceptually to apply to a concrete surface. The general factors we wanted to keep in mind were: ease of application, ease of refill, price, damage to floor/removability, complexity of surrounding controller mechanism, marking design flexibility, clarity of marking, and safety.

<img width="2300" height="736" alt="Initial Sketch_final" src="https://github.com/user-attachments/assets/ca9aa22e-60b3-4f53-badb-3459637077e6" />

## Finalized Plans

<img width="225" height="335" alt="Z axis Sketch_final" align="left" src="https://github.com/user-attachments/assets/08df8fcb-4c79-41eb-8413-98292f5daf0d" />

Finally, we concluded that stamps would be our best option. We would "print" four hexadecimal digits since it would supply ~65,000 individual codes, surpassing our initial goal of over 10,000. Drafts were made of conveyor designs to rotate the stamps upside-down and then be moved vertically, but we decided to create a “stamper wheel” that would feature 16 stamps placed on the outer edge of a thin disk. The entire wheel would raise and lower for character placement.

We took a lot of inspiration from 3D printers. Primarily, their use of stepper motors and lead screws for precise vertical and horizontal movement. This meant we would have three degrees of motion: vertical movement of a "chassis", horizontal movement of the wheel via a "slider", and the turning of the wheel itself to new letter stamps. Together, this should allow enough freedom to efficiently print the four characters we needed.

<br clear="left"/>

## 🔨 Prototype A

<img width="504" height="378" alt="working" align="right" src="https://github.com/user-attachments/assets/0082911d-1dec-4cad-b779-c657d2f65928" />

I modeled and helped create the chassis with two custom 3D-printed parts that held the opposing motors in place and enabled attachment to the vertical lead screws. Basic attachments were made for the vertical lead screw motors, and I cut 30mm aluminum to length with a miter saw and helped to fasten them together to make a frame.

I created a keyed shaft for the motor from an aluminum rod using a mill, lathe, drill press, and screw tapper. This allowed the stamper wheel to slide horizontally while still being turnable from the rod itself.

I wrote a custom <a href="https://github.com/ThatBenKraft/motors" target="_blank" rel="noopener noreferrer">stepper motor library</a> and stamper protocol in Python to control the main actions and testing, which was run on a Raspberry Pi 4 that was wired to each of the four stepper motors. While wall power was used during much of the testing, an 11.1V LiPo battery was used to power the motor drivers, and a 5V portable battery powered the Pi.

<table align="center" style="margin: 0px auto;">
  <tr>
    <td align="center">
      <img width="1000" height="1000" alt="holder_model_square" src="https://github.com/user-attachments/assets/f693c93d-5765-4008-a730-36b9e7ecf953" /> <br>
      A model of "Holder A" in the chassis
    </td>
    <td align="center">
      <img width="1000" height="1000" alt="prototype_a" src="https://github.com/user-attachments/assets/4dde66bb-e30f-42b5-9a52-dad00aaeab5b" /> <br>
      The completed "Prototype A"
    </td>
    <td align="center">
      <img width="999" height="999" alt="keyed_shaft_square" src="https://github.com/user-attachments/assets/68532623-05d6-4ab6-a202-d1a38be1ec5d" /> <br>
      The keyed shaft on a stepper motor
    </td>
  </tr>
</table>

## 🔄️ Troubleshooting & Designing Prototype B

The first prototype was very helpful in pointing out the problem points with our design. These mainly came down to frame size, stamper wheel size, slider catching, and chassis instability. The stamper wheel size was an easy fix since flatter, larger stamps led to more legible markings, a smaller wheel, and a smaller chassis overall. We again took more inspiration from existing 3D printers to add two additional support rods, which helped to stabilize the now-smaller chassis as it moved vertically. Our second design included a custom-milled keyed shaft since our first iteration had many imperfections that led to increased stamper wheel binding.

<!---
<table align="center" style="margin: 0px auto;">
  <tr>
    <td align="center">
      <img width="1000" height="707" alt="7c910cee-7166-4b94-be38-6c2677931af2_rw_3840" src="https://github.com/user-attachments/assets/700affa8-f435-49ad-96bc-05afd98ca2a6" /> <br>
      First "Prototype B" chassis design
    </td>
    <td align="center">
      <img width="1000" height="773" alt="Chassis Assembly" src="https://github.com/user-attachments/assets/7cb2267d-b090-4efb-a4d7-a2051a896bae" /> <br>
      Final "Prototype B" chassis design
    </td>
    <td align="center">
      <img width="1000" height="624" alt="Movement_Animation_small" src="https://github.com/user-attachments/assets/b0ad4fa9-a181-41be-919e-53df329c4498" /> <br>
      The keyed shaft on a stepper motor
    </td>
  </tr>
</table>
-->

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
