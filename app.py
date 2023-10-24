import RPi.GPIO as GPIO
import time as time
import Freenove_DHT as DHT
import mailer
import json
import requests
import imaplib

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#set up variable , instance
LED = 12
DHTPin = 21 #define the pin of DHT11
dht = DHT.DHT(DHTPin)

#set up emailer server
server = 'smtp-mail.outlook.com'  #Email Server (don't change!)
port = 587  #Server Port (don't change!)
sender = "ukniot123@outlook.com"
pswd =  "ukniot1029384756"
mailerApp = mailer.Emailer(server, port, sender, pswd)

#set up motor
Motor1 = 22 # Enable Pin
Motor2 = 27 # Input Pin
Motor3 = 17 # Input Pin
motorStateOn = False # bool to record motor state, avoiding repeatly set mode

GPIO.setup(Motor1,GPIO.OUT, initial=0)
GPIO.setup(Motor2,GPIO.OUT, initial=0)
GPIO.setup(Motor3,GPIO.OUT, initial=0) 


GPIO.setup(LED, GPIO.OUT, initial=0)

from flask import Flask, render_template, request, url_for, flash, redirect
app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html')

@app.route("/toggle_light", methods=["POST"])
def toggle_light():
    # isOn = json.loads(request.form['isOn'])
    # GPIO.output(LED, isOn)  #flip the current state 0->1 | 1->0
    return render_template('index.html')

@app.route("/get_data", methods=["GET"])
def get_data():
    res = {"temp":0,"humid":0}
    try:
        chk = dht.readDHT11()
        if (chk is dht.DHTLIB_OK):
            res["humid"] = dht.humidity
            res["temp"] = dht.temperature
    except:
        return res
    return res

@app.route("/send_motor_mail", methods=["POST"])
def send_mail():
    temp = json.loads(request.form['temp'])

    sendTo = "ukniot123@outlook.com"
    emailSubject = "Hello from automatic service"
    emailContent = "The current temperature " + str(temp) + ". Would you like to turn on the fan?"

    mailerApp.sendmail(sendTo, emailSubject, emailContent)

    return render_template('index.html')

@app.route("/read_motor_mail", methods=["POST"])
def read_motor_mail():
    #do imap here
    server = "outlook.office365.com" #do not change
    subject = "Re: Hello from automatic service"
    resp = mailerApp.read_mail(server, None, subject)
    check_motor_resp(resp)

    return render_template('index.html')

def check_motor_resp(msg):
    #guard
    if msg is None or msg.lower() != 'yes':
        return
    # -- turn on motor when "yes"
    set_motor_on()
    return

def set_motor_on():
    #guard: if already on, do nothing
    if (motorStateOn):
        return
    GPIO.output(Motor1, 1)
    GPIO.output(Motor2, 0)
    GPIO.output(Motor3, 1)
    motorStateOn = True
    return


def set_motor_off():
    #guard: if already off, do nothing
    if (not motorStateOn):
        return
    GPIO.output(Motor1, 1)
    GPIO.output(Motor2, 0)
    GPIO.output(Motor3, 0)
    motorStateOn = False
    return

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
