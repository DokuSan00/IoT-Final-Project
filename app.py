import RPi.GPIO as GPIO
import time as time
import Freenove_DHT as DHT
import mailer
import json
import paho.mqtt.client as mqtt
from threading import Thread
from Data import PINS, MAIL_SERVICE
from User.Client import Client
from datetime import datetime
import pytz

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#set up emailer client and server
client = "ukniot123@outlook.com"
mailerApp = mailer.Emailer(
    MAIL_SERVICE['server'], 
    MAIL_SERVICE['port'], 
    MAIL_SERVICE['email'], 
    MAIL_SERVICE['pswd']
)

#setup DHT
dht = DHT.DHT(PINS['DHTPin'])

#set up database
client = Client()
# client_data = {"23", "Ali", "dubashev@gmail.com", 21, 21, 400}
# client.create(client_data)

#set up MQTT client and connect to the localhost
mqtt_client = mqtt.Client()
mqtt_client.connect("localhost")
#Topics
rfid_topic = "rfid_reader"
pResistorTopic = "ESP/pResistor"

#User values
global tag_id, username, tempThreshold, humidityThreshold
lightIntensity = 0.0 
tag_id = ""
username = ""
tempThreshold = 0.0
lightIntensityThreshold = 0.0

#MQTT broker
mqtt_server = "192.168.0.101"; 
# mqtt_server = "172.168.0.101"; 

#callback functions for the mqtt client
def on_message(client, userdata, msg):
    #set up client credentials
    global lightIntensity
    #mqtt message is a binary payload, decode it to a string and change it to other types if needed
    if (msg.topic == pResistorTopic):
        print(f"Received `{msg.payload.decode()}` from `{msg.pResistorTopic}` topic")
        lightIntensity = float(msg.payload.decode()) or 0.0
    elif(msg.topic == rfid_topic):
        print(f"Received tag: `{msg.payload.decode()}` from `{msg.rfid_topic}` topic")
        tag_id = msg.payload.decode() or ""
        login(tag_id)

def login(tag_id):
    #check the credentials with the rfid
    try:
        client.c.execute("SELECT * FROM users WHERE tag_id = ?", [tag_id])
        user = client.c.fetchone()
        
        if not user:
            print("No such client exists in database, create one if needed")
        else:
            username = user[1]
            tempThreshold = user[2]
            lightIntensityThreshold = user[3]
            print(username, tempThreshold, lightIntensityThreshold)
    
            time = datetime.now(pytz.timezone('America/New_York'))
            currtime = time.strftime("%H:%M")
            mailerApp.sendmail(mailerApp, client, f"`{username}` entered at this time: `{currtime}`", f"`{username}` entered at this time: `{currtime}`")            
    finally:
        client.c.close()
    

def on_connect(client, user_data, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(pResistorTopic)
    client.subscribe(rfid_topic)

mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connect

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
    sendTo = client
    emailSubject = request.form['subject']
    emailContent = request.form['content']

    # mailerApp.sendmail(sendTo, emailSubject, emailContent)

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
    #Start one thread for mqtt client where it will keep reconnecting
    Thread(target=mqtt_client.loop_forever).start()
    #Start another for the whole application
    app.run(host='0.0.0.0', debug=True)