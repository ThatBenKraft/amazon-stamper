#!/usr/bin/env python
"""
## Host
Allows for the hosting of stamper site on local device. Code entry is stored in
spreadsheet to be accessed externally.

Dependencies: flask, flask-wtf, wtforms

To check PID processes on port, run:
$ lsof -wni tcp:<PORT>

To kill PID process:
$ kill -9 <PID>
"""

import os
import signal

import requests
from flask import Flask, flash, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length

from stamper import CHARACTERS
from storage import Cells, get_cell, set_cell

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "Apache"
__version__ = "0.1.0"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5000

INVALID_BANNER = False

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)

server_running = False


def _ValidCharacters(form: FlaskForm, field: StringField) -> None:
    """
    Custom validator used for checking if code is in hexadecimal.
    """
    # For each character in code
    for character in field.data:  # type:ignore
        # If character is not in characters:
        if character.upper() not in CHARACTERS:
            # Raises error
            raise ValidationError("Field must be in hexadecimal.")


class CodeForm(FlaskForm):
    """
    Class for site code entry form.
    """

    code = StringField(
        "Code",
        validators=[
            DataRequired(),
            Length(min=4, max=4),
            _ValidCharacters,
        ],
    )
    submit = SubmitField("Submit")


@app.route("/home")
@app.route("/", methods=["GET", "POST"])
def home():
    """
    Stamper home page. Includes code form.
    """
    form = CodeForm()
    # Gets states
    stamper_running = get_cell(Cells.RUNNING)
    valid_submit = form.validate_on_submit()
    # Reports states
    print(f"Running: {stamper_running}\nValid submit: {valid_submit}")
    # If valid code submission:
    if valid_submit:
        # Acquires code from form
        code = form.code.data.upper()  # type:ignore
        # Reports
        print(f"Setting code to: {code}")
        flash(f"Code entered: {code}", "success")
        # Sets spreadsheet code
        set_cell(Cells.CODE, code)
    # If stamper is already running:
    elif stamper_running:
        # Reports
        print("Error flashing 'running'")
        flash("Stamper already running!", "danger")
    # If invalid banner is activated:
    elif INVALID_BANNER:
        # Reports
        print("Error flashing 'entry error'")
        flash("Invalid code entered!", "danger")
    # Returns html front page
    return render_template("home.html", form=form)


@app.route("/about")
def about() -> str:
    """
    Stamper about page.
    """
    return render_template("about.html", title="About")


@app.route("/shutdown", methods=["POST"])
def shutdown() -> str:
    """
    Stamper shutdown page.
    """
    # Reports
    print("Shutting down gracefully...")
    # Shuts down server
    os.kill(os.getpid(), signal.SIGINT)
    return "Server shutting down..."


def run_flask(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """
    Runs webapp on specified host and port.
    """
    global server_running
    # If server is not running:
    if not server_running:
        # Starts server
        app.run(host, port)
        server_running = True


def stop_flask() -> None:
    """
    Posts shutdown to host.
    """
    global server_running
    # If server is running:
    if server_running:
        # Posts to server for shutdown
        requests.post("http://127.0.0.1:5000/shutdown")
        server_running = False


if __name__ == "__main__":
    run_flask()
