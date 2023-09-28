import RPi.GPIO as GPIO
import time as time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LED = 26

GPIO.setup(LED, GPIO.OUT, initial=0)

from flask import Flask, render_template, request, url_for, flash, redirect
app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html')

@app.route("/toggle_light", methods=["POST"])
def toggle_light():
    time.sleep(0.1)
    GPIO.output(LED, not(bool(GPIO.input(LED))))  #on off the light
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
