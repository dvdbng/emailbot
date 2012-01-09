# David's Email Robot

This robot is designed to move all those long uninteresting conversations from your inbox

# Usage:

* Create two folders (or tags in gmail) in your E-mail account: AddRuido and Ruido
* Install smtplib2
* write a config.py file with HOST, PORT, USER, and PASS variables
* python robot.py
* When you move a message from your inbox to AddRuido the robot will move it to Ruido and remember the e-mail subject as a "noisy" subject.
* Then it will remove new messages from your inbox with the same subject

Note: "Re: " "Re: Re:" etc... is handled correctly.

# Hackers wanted!

If you like my robot, you might want to improve it, some ideas:
* Make folder names configurable (Very easy)
* Add command line parameters (Easy)
* Convert the robot in a daemon and include a rc script (Easy)
* Make it behave more like gmail's mute function: don't filter messages of a conversation when you are CC'd for the first time.
* Implement a whitelist: If a message's body contains certain word (e.g: your name), don't filter it.
* Report statistics about filtered messages

# Contact

Tweet me: @dvdbng
Or send me an e-mail: david at bengoa rocandio dot com (remove the space between my family names)
