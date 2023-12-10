from flask import Flask, render_template, request

# from stamper import CHARACTERS

CHARACTERS = [character for character in "0123456789ABCDEF"]

app = Flask(__name__)

FILENAME = "new_code.txt"


class LineNumbers:
    CODE = 2


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    text_input = request.form["textInput"]

    error_message = valid_code(text_input)

    if not error_message:
        return render_template("success.html", text_input=text_input)
    else:
        return render_template("index.html", error_message=error_message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)


def valid_code(code: str) -> str:
    if len(code) != 4:
        return "Code must be four characters long."
    elif any(character.upper() not in CHARACTERS for character in code):
        return "One or more characters in code not on wheel."
    return ""
