#!/usr/bin/bash
LOGFILE="/home/pi/Documents/ISENSIOT-SmartBabyMonitoring/TalkToBaby/script.log"
# Set the necessary environment variables
export XDG_RUNTIME_DIR="/run/user/$(id -u pi)"
export PULSE_RUNTIME_PATH="/run/user/$(id -u pi)/pulse"
export DISPLAY=:0

sleep 2
echo "Starting talk to baby python script"
#set -e

#source /home/pi/Documents/ISENSIOT-SmartBabyMonitoring/venv/bin/activate
/home/pi/Documents/ISENSIOT-SmartBabyMonitoring/venv/bin/python /home/pi/Documents/ISENSIOT-SmartBabyMonitoring/TalkToBaby/main.py
