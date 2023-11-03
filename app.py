import RPi.GPIO as GPIO
import time as time
import Freenove_DHT as DHT
import mailer
import json
import requests
import imaplib
import paho.mqtt.client as mqtt
from threading import Thread

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#set up variable , instance
LED = 12
DHTPin = 21 #define the pin of DHT11
dht = DHT.DHT(DHTPin)

#MQTT code
mqtt_client = mqtt.Client()
mqtt_client.connect("localhost")
pResistorTopic = "ESP/pResistor"
lightIntensity = 0.0

def on_message(client, userdata, msg):
    global lightIntensity
    lightIntensity = float(msg.payload.decode())

def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(pResistorTopic)

mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connect

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
    GPIO.output(LED, state)
    return render_template('index.html')

@app.route("/get_data", methods=["GET"])
def get_data():
    res = {"light": lightIntensity or None}
    try:
        chk = dht.readDHT11()
        if (chk is dht.DHTLIB_OK):
            res["humid"] = dht.humidity or None
            res["temp"] = dht.temperature or None
    except:
        pass
    
    return res

@app.route("/send_motor_mail", methods=["POST"])
def send_mail():
    sendTo = client
    emailSubject = request.form['subject']
    emailContent = request.form['content']

    mailerApp.sendmail(sendTo, emailSubject, emailContent)

    return '', 200

@app.route("/read_motor_mail", methods=["POST"])
def read_motor_mail():        
    #do imap here
    server = "outlook.office365.com" #do not change
    subject = "Re: Hello from automatic service - Fans Service"
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
    Thread(target=mqtt_client.loop_forever).start()
    app.run(host='0.0.0.0', debug=True)
