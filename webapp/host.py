# Dependencies: flask, flask-wtf, wtforms

import os
import signal
import time
from threading import Thread

import requests
from flask import Flask, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from storage import Cells, get_cell, set_cell
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length

from ..stamper import CHARACTERS

# set FLASK_APP=webapp_testing.py
app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5000

server_running = False


def AlphaNumeric(form: FlaskForm, field: StringField) -> None:
    """
    Custom validator used for checking if code is alphanumeric.
    """
    for character in field.data:  # type:ignore
        if character.upper() not in CHARACTERS:
            raise ValidationError("Field must be alpha-numeric.")


class CodeForm(FlaskForm):
    """
    Class for site code entry form.
    """

    code = StringField(
        "Code",
        validators=[
            DataRequired(),
            Length(min=4, max=4),
            AlphaNumeric,
        ],
    )
    submit = SubmitField("Submit")


@app.route("/home")
@app.route("/", methods=["GET", "POST"])
def home():
    form = CodeForm()
    # Gets states
    stamper_running = get_cell(Cells.RUNNING)
    valid_submit = form.validate_on_submit()

    if stamper_running:
        print("Flashing running")
        flash("Stamper already running!", "danger")
    elif valid_submit:
        code = form.code.data.upper()  # type:ignore
        flash(f"Code entered: {code}", "success")
        set_cell(Cells.CODE, code)
    else:
        flash("Invalid code entered!", "danger")
        return redirect(url_for("home"))
    return render_template("home.html", form=form)


@app.route("/about")
def about() -> str:
    return render_template("about.html", title="About")


@app.route("/shutdown", methods=["POST"])
def shutdown() -> str:
    print("Shutting down gracefully...")
    os.kill(os.getpid(), signal.SIGINT)
    return "Server shutting down..."


def run_flask(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """
    Runs webapp on specified host and port.
    """
    global server_running
    app.run(host, port)
    server_running = True


def stop_flask() -> None:
    """
    Posts shutdown to host.
    """
    global server_running
    if server_running:
        requests.post("http://127.0.0.1:5000/shutdown")
        server_running = False


if __name__ == "__main__":
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    time.sleep(5)
    stop_flask()
