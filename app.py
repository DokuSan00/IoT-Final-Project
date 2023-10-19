import RPi.GPIO as GPIO
import time as time
import Freenove_DHT as DHT
import mailer

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#set up variable , instance
LED = 12
DHTPin = 17 #define the pin of DHT11
dht = DHT.DHT(DHTPin)
sender = mailer.Emailer("ukniot123@outlook.com", "ukniot1029384756")


GPIO.setup(LED, GPIO.OUT, initial=0)

from flask import Flask, render_template, request, url_for, flash, redirect
app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html')

@app.route("/toggle_light", methods=["POST"])
def toggle_light():
    time.sleep(0.2)
    GPIO.output(LED, not(bool(GPIO.input(LED))))  #flip the current state 0->1 | 1->0
    return render_template('index.html')

@app.route("/get_data", methods=["GET"])
def get_data():
    res = {"temp":0,"humid":0}
    chk = dht.readDHT11()
    if (chk is dht.DHTLIB_OK):
        res["humid"] = dht.humidity
        res["temp"] = dht.temperature
    return res

@app.route("/motor_mail", methods=["POST"])
def mail():
    sendTo = "ukniot123@outlook.com"
    emailSubject = "Mailling lab test"
    emailContent = "Elo"

    sender.sendmail(sendTo, emailSubject, emailContent)    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
