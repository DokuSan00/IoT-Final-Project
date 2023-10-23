import RPi.GPIO as GPIO
import time as time
import Freenove_DHT as DHT
import mailer
import json
import requests

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#set up variable , instance
LED = 12
DHTPin = 17 #define the pin of DHT11
dht = DHT.DHT(DHTPin)
sender = "ukniot123@outlook.com"
pswd =  "ukniot1029384756"
mailerApp = mailer.Emailer(sender, pswd)

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
def send_mail():
    temp = json.loads(request.form['temp'])
    sendTo = "ukniot123@outlook.com"
    emailSubject = "Hello from automatic service"
    emailContent = "The current temperature " + str(temp) + ". Would you like to turn on the fan?"

    body = {
        "auth": {
            "email": sender,
            "password": pswd,
            "smtpServer": "smtp.office365.com",
            "port": 587
        },
        "message": {
            "to": sendTo,
            "subject": emailSubject,
            "text": emailContent
        }
    }

    # mailerApp.sendmail(sendTo, emailSubject, emailContent)   
    
    # this is api back up if the mailerApp doest works at school (do not erase)  
    #let theem be unrganized for now. will re-organized them later
    r = requests.post('https://iot-email-proxy-aa5866a0f983.herokuapp.com/sendmail', json = body)

    return render_template('index.html')

@app.route("/read_motor_mail", methods=["POST"])
def read_mail_turn_motor():
    #do imap here

    # back up API, if imap doesnt run
    body = {
        "auth": {
            "email": "ukniot123@outlook.com",
            "password": "ukniot1029384756",
            "imapServer": "outlook.office365.com",
            "port": 993
        },
        "filters": {
            "from": "ukniot123@outlook.com",
            "subject": "Re - Hello from automatic service",
            "text": "*"
        },
        "options": {
            "only_unseen": False,
            "delete_email": False
        }
    }

    r = requests.post('https://iot-email-proxy-aa5866a0f983.herokuapp.com/readmail', json = body)
    print(r.text)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
