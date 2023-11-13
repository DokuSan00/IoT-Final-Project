import RPi.GPIO as GPIO
import time as time
import Freenove_DHT as DHT
import mailer
import json
import paho.mqtt.client as mqtt
from threading import Thread
from Data import PINS, MAIL_SERVICE

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#setup DHT
dht = DHT.DHT(PINS['DHTPin'])

#MQTT code
mqtt_client = mqtt.Client()
mqtt_client.connect("localhost")
pResistorTopic = "ESP/pResistor"
lightIntensity = 0.0

def on_message(client, userdata, msg):
    global lightIntensity
    lightIntensity = float(msg.payload.decode()) or 0.0

def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(pResistorTopic)

mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connect

#set up emailer server
client = "ukniot123@outlook.com"
mailerApp = mailer.Emailer(
    MAIL_SERVICE['server'], 
    MAIL_SERVICE['port'], 
    MAIL_SERVICE['email'], 
    MAIL_SERVICE['pswd']
)

#setup motor
GPIO.setup(PINS['motor1'], GPIO.OUT, initial=0)
GPIO.setup(PINS['motor2'], GPIO.OUT, initial=0)
GPIO.setup(PINS['motor3'], GPIO.OUT, initial=0) 


GPIO.setup(PINS['LED'], GPIO.OUT, initial=0)

from flask import Flask, render_template, request, url_for, flash, redirect
app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html')

@app.route("/set_light", methods=["POST"])
def set_light():
    state = json.loads(request.form['state'])
    GPIO.output(PINS['LED'], state)
    return render_template('index.html')

@app.route("/get_data", methods=["GET"])
def get_data():
    res = {"light": lightIntensity or None}
    try:
        chk = dht.readDHT11()
        if (chk is dht.DHTLIB_OK):
            res["humid"] = dht.humidity
            res["temp"] = dht.temperature
    except:
        pass
    return res

@app.route("/send_mail", methods=["POST"])
def send_mail():

    print('elo')
    sendTo = client
    emailSubject = request.form['subject']
    emailContent = request.form['content']

    mailerApp.sendmail(sendTo, emailSubject, emailContent)

    return '', 200

@app.route("/read_motor_mail", methods=["POST"])
def read_motor_mail():        
    #do imap here
    subject = "Re: Hello from automatic service - Fans Service"
    resp = None
    try:
        resp = mailerApp.read_mail(MAIL_SERVICE['read_server'], client, subject)
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

    GPIO.output(PINS['motor1'], 1)
    GPIO.output(PINS['motor2'], state * 0)
    GPIO.output(PINS['motor3'], state * 1)
    return '', 200

if __name__ == '__main__':
    Thread(target=mqtt_client.loop_forever).start()
    app.run(host='0.0.0.0', debug=True)
