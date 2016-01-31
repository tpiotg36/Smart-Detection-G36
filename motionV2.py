#!/usr/bin/env python
# Group 36 (Ng Chee Ming and Lee Jia En)
# PS: There are AWS rules enabled in AWS IoT Cloud to help to actuate the LED and Buzzer which
# in turn help to trigger the script, photo taking and emailing to indicate Fire or Motion Detected in the room.

# This program is to send the sensor data periodically to AWS IoT.
# Based on the AWS IoT rules we created, the program will process actuation commands received.
# If motion detected, LED will flash once and take a photo. This photo will be send to user via email.
# If Fire detected, LED will flash twice and Buzzer will sound.
# It will also trigger the relay script to switch off the electricity.

import time
import datetime
import ssl
import json
import paho.mqtt.client as mqtt
import grovepi
from grovepi import *
import os
import tweepy
import sys

# TODO: Name of our Raspberry Pi, also known as our "Thing Name"
deviceName = "g36_pi"
# TODO: Public certificate of our Raspberry Pi, as provided by AWS IoT.
deviceCertificate = "7ed56edd7d-certificate.pem.crt"
# TODO: Private key of our Raspberry Pi, as provided by AWS IoT.
devicePrivateKey = "7ed56edd7d-private.pem.key"
# Root certificate to authenticate AWS IoT when we connect to their server.
awsCert = "aws-iot-rootCA.crt"
isConnected = False

# Assume we connected the Grove Digital Humidity/Temperature Sensor (DHT11) to digital port D2,
# Buzzer Sensor to D8, Grove LED to digital port D4.
dht_sensor = 3
led = 4
pir_sensor = 8
light = 0
buzzer = 2
flame_sensor = 5

strTemp = ""

# Consumer keys and access tokens, used for OAuth
consumer_key = 'aghn0y23MUqwtRbo4jiaoNXVI'
consumer_secret = 'kDeVkRrQPYmmYIL2DGJANM63S91l7zzvwooos9tbytmrySK9Yg'
access_token = '4772645473-LY2KfGgSFENWIda2IZL3uTHCOLyO0TDfgIQV23e'
access_token_secret = 'zcAplwlGNE7G6u8yKIEJDqcYen4ZUps7W8suiWeE3i3jO'

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Creation of the actual interface, using authentication
api = tweepy.API(auth)

# This is the main logic of the program.  We connect to AWS IoT via MQTT, send sensor data periodically to AWS IoT,
# and handle any actuation commands received from AWS IoT.
def main():
    global isConnected
    # Create an MQTT client for connecting to AWS IoT via MQTT.
    client = mqtt.Client(deviceName + "_sr")  # Client ID must be unique because AWS will disconnect any duplicates.
    client.on_connect = on_connect  # When connected, call on_connect.
    client.on_message = on_message  # When message received, call on_message.
    client.on_log = on_log  # When logging debug messages, call on_log.

    # Set the certificates and private key for connecting to AWS IoT.  TLS 1.2 is mandatory for AWS IoT and is supported
    # only in Python 3.4 and later, compiled with OpenSSL 1.0.1 and later.
    client.tls_set(awsCert, deviceCertificate, devicePrivateKey, ssl.CERT_REQUIRED, ssl.PROTOCOL_TLSv1_2)

    # Connect to AWS IoT server.  Use AWS command line "aws iot describe-endpoint" to get the address.
    print("Connecting to AWS IoT...")
    client.connect("A1P01IYM2DOZA0.iot.us-west-2.amazonaws.com", 8883, 60)

    # Start a background thread to process the MQTT network commands concurrently, including auto-reconnection.
    client.loop_start()

    # Configure the Grove LED and Buzzer port for output.
    grovepi.pinMode(led, "OUTPUT")
    grovepi.pinMode(pir_sensor,"INPUT")
    grovepi.pinMode(light,"INPUT")
    grovepi.pinMode(buzzer,"OUTPUT")
    #grovepi.pinMode(button,"INPUT")
    grovepi.pinMode(flame_sensor,"INPUT")

    time.sleep(1)

    # Loop forever.
    while True:
        try:
            # If we are not connected yet to AWS IoT, wait 1 second and try again.
            if not isConnected:
                time.sleep(1)
                continue
            #For simulation only
            os.system('/usr/bin/python -W ignore /home/pi/TP-IoT/relayon.py')
            time.sleep(1)
            print("\n======================================================\n")
            print("          Start to collect sensor data...\n")
            print("======================================================\n")
            #if grovepi.digitalRead(button):
             #   os.system('/usr/bin/python -W ignore /home/pi/GrovePi/Software/Python/cheeming/relay.py')
             #   continue
            # Read Grove sensor values. Prepare our sensor data in JSON format.
            payload = {
                "state": {
                    "reported": {
                        # Uncomment the next line if you're using the Grove Analog Temperature Sensor.
                        # "temperature": round(grovepi.temp(temp_sensor, '1.1'), 1),
                        # Comment out the next 2 lines if you're using the Grove Analog Temperature Sensor.
                        "temperature": grovepi.dht(dht_sensor, 0)[0],  # The first 0 means that the DHT module is DHT11.
                        #"humidity": grovepi.dht(dht_sensor, 0)[1],
                        "flame": grovepi.digitalRead(flame_sensor),
                        #"flame": round(0, 1),
                        "motion": grovepi.digitalRead(pir_sensor),
                        #"light": grovepi.analogRead(light),
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                }
            }

            temp = dht(dht_sensor, 0)  # Get the temperature and Humidity from the DHT sensor
            strTemp = str(temp)

            print("Sending sensor data to AWS IoT...\n" +
                  json.dumps(payload, indent=4, separators=(',', ': ')))

            # Publish our sensor data to AWS IoT via the MQTT topic, also known as updating our "Thing Shadow".
            client.publish("$aws/things/" + deviceName + "/shadow/update", json.dumps(payload))
            print("Sent to AWS IoT")

            #print("Sent to Twitter")
            #thetime = datetime.datetime.now().isoformat()
            #statustweet = 'Timestamp: ' + thetime + '   Location: ' + deviceName + '   [Temperature, Humidity]: ' + strTemp
            #api.update_status(status=statustweet)

            # Wait 900 seconds before sending the next set of sensor data.
            time.sleep(10)

        except KeyboardInterrupt:
            break
        except IOError:
            print("Error")


# This is called when we are connected to AWS IoT via MQTT.
# We subscribe for notifications of desired state updates.
def on_connect(client, userdata, flags, rc):
    global isConnected
    isConnected = True
    print("Connected to AWS IoT")
    # Subscribe to our MQTT topic so that we will receive notifications of updates.
    topic = "$aws/things/" + deviceName + "/shadow/update/accepted"
    print("Subscribing to MQTT topic " + topic)
    client.subscribe(topic)


# This is called when we receive a subscription notification from AWS IoT.
# If this is an actuation command, we execute it.
def on_message(client, userdata, msg):
    # Convert the JSON payload to a Python dictionary.
    # The payload is in binary format so we need to decode as UTF-8.
    payload2 = json.loads(msg.payload.decode("utf-8"))
    print("Received message, topic: " + msg.topic + ", payload:\n" +
          json.dumps(payload2, indent=4, separators=(',', ': ')))

    # If there is a desired state in this message, then we actuate, e.g. if we see "led=on", we switch on the LED.
    if payload2.get("state") is not None and payload2["state"].get("desired") is not None:
        # Get the desired state and loop through all attributes inside.
        desired_state = payload2["state"]["desired"]
        for attribute in desired_state:
            # We handle the attribute and desired value by actuating.
            value = desired_state.get(attribute)
            actuate(client, attribute, value)


# Control my actuators based on the specified attribute and value, e.g. "led=on" will switch on my LED.
def actuate(client, attribute, value):
    if attribute == "timestamp":
        # Ignore the timestamp attribute, it's only for info.
        return
    print("Setting " + attribute + " to " + value + "...")
    if attribute == "led":
        # We actuate the LED for "Motion Detected", "flash2 means no motion detected".
        if value == "Motion_Detected":
            # Switch on LED.
            grovepi.digitalWrite(led, 1)
            #send_reported_state(client, "led", "Motion_Detected")
            time.sleep(1)
            grovepi.digitalWrite(led,0)
            send_reported_state(client, "led", "Motion_Detected")
            time1 = time.strftime("%H%M")
            #print (time1)
            date1 = time.strftime("%d%m%Y")
            #print (date1)
            imageName = date1 + "_" + time1 + ".jpg"
            #print (imageName)
            imagePath = '/usr/bin/fswebcam /home/pi/IMAGE/' + imageName
            #Take photo when human motion is detected
            os.system(imagePath)
            #Send the photo via email to the user
            os.system('/usr/bin/mpack -s "Motion Detected Room G36" /home/pi/IMAGE/$(date +%d%m%Y_%H%M).jpg tpiotg36@gmail.com &')
            time.sleep(1)
            photo_path = "/home/pi/IMAGE/" + imageName
            temp = "Motion Detected at location: " + deviceName
            print ("Sending photo to Twitter")
            api.update_with_media(photo_path, status=temp)
            print ("Photo uploaded to Twitter")
            time.sleep(1)
            return
        elif value == "Fire":
            # Switch on LED, wait .5 second, switch it off. Flashing twice to indicate fire present
            #grovepi.digitalWrite(led, 1)
            #send_reported_state(client, "led", "Fire_Detected")
            #time.sleep(.5)

            #grovepi.digitalWrite(led, 0)
            #send_reported_state(client, "led", "Fire_Detected")
            #time.sleep(.5)

            #grovepi.digitalWrite(led,1)
            #send_reported_state(client, "led", "Fire_Detected")
            #time.sleep(.5)

            #grovepi.digitalWrite(led,0)
            #os.system('/usr/bin/python -W ignore /home/pi/TP-IoT/writeToLed.py &')
            send_reported_state(client, "led", "No_Fire_Detected")
            time.sleep(.5)
            return
    # We actuate the buzzer for "on" or "off" when light is switched on.
    #We actuate the buzzer for "on" or "off" when fire is detected.
    # It will trigger the relay python script to switch off the power.
    if attribute == "buzzer":
        if value == "Fire":
            # Switch on Buzzer.
            #rovepi.digitalWrite(buzzer, 1)
            #send_reported_state(client, "buzzer", "buzzy1")
            #os.system('/usr/bin/python -W ignore /home/pi/GrovePi/Software/Python/cheeming/relay.py')
            #time.sleep(.5)
            #grovepi.digitalWrite(buzzer, 0)
            #time.sleep(.5)
            ##grovepi.digitalWrite(buzzer, 1)
            #time.sleep(.5)
            #grovepi.digitalWrite(buzzer, 0)
            #time.sleep(.5)
            #grovepi.digitalWrite(buzzer, 1)
            #time.sleep(.5)
            #grovepi.digitalWrite(buzzer, 0)
            os.system('/usr/bin/python /home/pi/TP-IoT/Fire.py &')
            grovepi.digitalWrite(buzzer, 0)
            grovepi.digitalWrite(led,0)
            os.system('/usr/bin/python -W ignore /home/pi/TP-IoT/relayoff.py &')
            send_reported_state(client, "buzzer and led", "Fire_Detected")
            return
        elif value == "buzzy2": #
            # Switch off Buzzer.
            #grovepi.digitalWrite(buzzer, 1)
            #time.sleep(.5)
            #grovepi.digitalWrite(buzzer, 0)
            #send_reported_state(client, "buzzer", "off")
            #time.sleep(.5)
            #grovepi.digitalWrite(buzzer, 1)
            #send_reported_state(client, "buzzer", "on")
            #time.sleep(.5)
            #grovepi.digitalWrite(buzzer, 0)
            send_reported_state(client, "buzzer", "No_Fire_Detected")
            return
    # Show an error if attribute or value are incorrect.
    print("Error: Don't know how to set " + attribute + " to " + value)


# Send the reported state of our actuator tp AWS IoT after it has been triggered, e.g. "led": "on".
def send_reported_state(client, attribute, value):
    # Prepare our sensor data in JSON format.
    payload = {
        "state": {
            "reported": {
                attribute: value,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    }
    print("Sending sensor data to AWS IoT...\n" +
          json.dumps(payload, indent=4, separators=(',', ': ')))

    # Publish our sensor data to AWS IoT via the MQTT topic, also known as updating our "Thing Shadow".
    client.publish("$aws/things/" + deviceName + "/shadow/update", json.dumps(payload))
    print("Sent to AWS IoT")

    print("Sent to Twitter")
    thetime = datetime.datetime.now().isoformat()
    statustweet = 'Timestamp: ' + thetime + '   Location: ' + deviceName + '   Reported Data From ' + attribute + ': ' + value
    #print (statustweet)
    api.update_status(status=statustweet)
    #path = '/usr/bin/python -W ignore /home/pi/TP-IoT/twitter_Test.py ' + statustweet + ' &'
    #os.system(path)
    time.sleep(.5)
# Print out log messages for tracing.
def on_log(client, userdata, level, buf):
    print("Log: " + buf)


# Start the main program.
main()        
