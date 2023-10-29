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
client = "ukniot123@outlook.com"
pswd =  "ukniot1029384756"
mailerApp = mailer.Emailer(server, port, sender, pswd)

#set up motor
Motor1 = 22 # Enable Pin
Motor2 = 27 # Input Pin
Motor3 = 17 # Input Pin
# bool to record motor state, avoiding repeatly set mode

GPIO.setup(Motor1,GPIO.OUT, initial=0)
GPIO.setup(Motor2,GPIO.OUT, initial=0)
GPIO.setup(Motor3,GPIO.OUT, initial=0) 


GPIO.setup(LED, GPIO.OUT, initial=0)

from flask import Flask, render_template, request, url_for, flash, redirect
app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html')

@app.route("/set_light", methods=["POST"])
def set_light():
    state = json.loads(request.form['state'])
    GPIO.output(LED, state)  #flip the current state 0->1 | 1->0
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

    sendTo = client
    emailSubject = "Hello from automatic service"
    emailContent = "The current temperature is " + str(temp) + ". Would you like to turn on the fan?"

    mailerApp.sendmail(sendTo, emailSubject, emailContent)

    return '', 200

@app.route("/read_motor_mail", methods=["POST"])
def read_motor_mail():        
    #do imap here
    server = "outlook.office365.com" #do not change
    subject = "Re: Hello from automatic service"
    resp = None
    try:
        resp = mailerApp.read_mail(server, client, subject)
    except:
        resp = None

    return {'response': check_motor_resp(resp)}

def check_motor_resp(msg):
    #guard
    if msg is None or msg.lower() != 'yes':
        return 0
    # -- turn on motor when "yes"
    return 1

@app.route("/set_motor", methods=["POST"])
def set_motor():
    state = json.loads(request.form['state'])

    GPIO.output(Motor1, 1)
    GPIO.output(Motor2, state * 0)
    GPIO.output(Motor3, state * 1)
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
