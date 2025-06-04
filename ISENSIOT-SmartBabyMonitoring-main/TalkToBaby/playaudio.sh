#!/usr/bin/bash

ffmpeg -y -i /home/pi/Documents/playSound.3gpp -filter:a "volume=5" /home/pi/Documents/test.mp3 && mpg321 -g 100 /home/pi/Documents/test.mp3
