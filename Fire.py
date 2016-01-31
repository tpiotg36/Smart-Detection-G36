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

# Assume we connected the Grove Digital Humidity/Temperature Sensor (DHT11) to digital port D2,
# Buzzer Sensor to D8, Grove LED to digital port D4.
#dht_sensor = 3
led = 4
#pir_sensor = 8
#light = 0
buzzer = 2
#flame_sensor = 5

#Configure the Grove LED and Buzzer port for output.
grovepi.pinMode(led, "OUTPUT")
#    grovepi.pinMode(pir_sensor,"INPUT")
#    grovepi.pinMode(light,"INPUT")
grovepi.pinMode(buzzer,"OUTPUT")
#grovepi.pinMode(button,"INPUT")
#    grovepi.pinMode(flame_sensor,"INPUT")

grovepi.digitalWrite(buzzer, 1)
grovepi.digitalWrite(led,1)
time.sleep(.5)
grovepi.digitalWrite(buzzer, 0)
grovepi.digitalWrite(led,0)
time.sleep(.5)
grovepi.digitalWrite(buzzer, 1)
grovepi.digitalWrite(led,1)
time.sleep(.5)
grovepi.digitalWrite(buzzer, 0)
grovepi.digitalWrite(led,0)
