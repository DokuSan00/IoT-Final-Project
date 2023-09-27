import RPi.GPIO as GPIO

from flask import Flask, render_template, request, url_for, flash, redirect
app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(26, GPIO.OUT, initial=0)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html')

@app.route("/toggle_light", methods=["POST"])
def toggle_light():
    # path = request.form['projectFilePath']
    GPIO.output(26, not(bool(GPIO.input(26))))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
