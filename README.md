# Smart-Detection-G36
For IoT Project Submission.

# Introduction
At times of emergency like fire outbreak which may be cause by electrical appliances or etc, staffs are required to perform a manual and visual check and clear all the laboratories, tutorial rooms, meeting rooms, conference rooms and other areas/spaces to ensure everyone is evacuated. But at a certain time, there might be some people whether intentionally or not intentionally (like taking naps) may be hiding somewhere and even return back to the rooms/laboratories without anyone noticing. 

Every late evening time where technical/security staffs required to petrol around to clear and close all the laboratories, tutorial rooms, meeting rooms, conference rooms and other areas/spaces of schools, industrial or companies. Sometimes, some people may hide inside the any rooms or other places of schools, industrial or company to perform some mischievous or criminal acts, taking a nap at hidden/blind spots or etc which will prevent been spotted by technical/security staffs.  Quoting from Murphy’s Law, “Anything that can go wrong will go wrong”.

#motionV2.py file

PS: There are AWS rules enabled in AWS IoT Cloud to help to actuate the LED and Buzzer which in turn help to trigger the script, photo taking, update tweets to twitter and emailing.

This file is the main program which will send the sensor data periodically to AWS IoT. Based on the AWS IoT rules we created, the program will process actuation commands received. If motion detected, LED will flash once, web camera will take a photo and the photo will be uploaded to twitter. This photo will be send to user via email. When the flame sensor sensed fire, the Buzzer will sound and LED will flash twice,  it will also trigger the relay script to cut off the electricity.

#relayoff.py file

This file will be triggered by an AWS rule with act of actuating of buzzer.

#Fire.py file

This file will be triggered by an AWS rule with act of actuating of buzzer.
