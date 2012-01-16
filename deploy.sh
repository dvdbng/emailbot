#!/bin/bash

ssh hoyga '(cd /usr/lib/emailrobot; git pull)'
scp config.py hoyga:/usr/lib/emailrobot

