# David's Email Robot

This robot is designed to move all those long uninteresting conversations from your inbox

# Usage:

* Create two folders (or tags in gmail) in your E-mail acoount: AddRuido and Ruido
* Install smtplib2
* write a config.py file with HOST, PORT, USER, and PASS variables
* python robot.py
* When you move a message from your inbox to AddRuido the robot will move it to Ruido and remember the e-mail subject as a "noisy" subject.
* Then it will remove new messages from your inbox with the same subject

Note: "Re: " "Re: Re:" etc... is handled correctly.
