#!/bin/bash

ssh hoyga '(cd /usr/lib/emailrobot; git pull)'
scp config.py configbr.py hoyga:/usr/lib/emailrobot

