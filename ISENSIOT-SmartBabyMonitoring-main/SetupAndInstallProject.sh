#!/usr/bin/bash

#Camera stream on startup
sudo touch /etc/init.d/cameraStream
sudo tee /etc/init.d/cameraStream > /dev/null << 'END'
#!/bin/bash
### BEGIN INIT INFO
# Provides: cameraStream
# Required-Start:    $all
# Required-Stop: 
# Default-Start:     5 
# Default-Stop:      6 
# Short-Description: cameraStream startup on boot
### END INIT INFO


sleep 10
# Function to check internet connection
check_internet() {
    while true; do
        if ping -c 1 8.8.8.8 &> /dev/null; then
            echo "Internet connected!"
	    break
        else
            echo "No internet connection"
        fi
        sleep 2
    done
}

# Call the function
check_internet

sleep 60

libcamera-vid -t 0 --inline --height 360 --width 480 --framerate 24 --codec h264 -o - | ffmpeg -i - -vcodec libx264 -tune zerolatency -b:v 1500k -maxrate 1500k -vf "transpose=1" -bufsize 3000k -pix_fmt yuv420p -g  50 -f flv rtmp://rtmp.livepeer.com/live/bf49-kuqf-2p7f-276j
END

sudo chmod +x /etc/init.d/cameraStream
sudo update-rc.d cameraStream defaults

#Sensorhub on startup
sudo touch /etc/init.d/sensorhub
sudo tee /etc/init.d/sensorhub > /dev/null << 'END'
#!/bin/bash
### BEGIN INIT INFO
# Provides: sensorhub
# Required-Start:    $all
# Required-Stop: 
# Default-Start:     5 
# Default-Stop:      6 
# Short-Description: sensorhub startup on boot
### END INIT INFO

echo "Waiting for timeout for startup"
sleep 70
./home/pi/Documents/ISENSIOT-SmartBabyMonitoring/startupSensorHub.sh >>/dev/null 2>/home/pi/logSensorhub.log
END

sudo chmod +x /etc/init.d/sensorhub
sudo update-rc.d sensorhub defaults



sudo touch /etc/init.d/pushNotifications
sudo tee /etc/init.d/pushNotifications > /dev/null << 'END'
#!/bin/bash
### BEGIN INIT INFO
# Provides: pushNotifications
# Required-Start:    $all
# Required-Stop: 
# Default-Start:     5 
# Default-Stop:      6 
# Short-Description: pushNotifications startup on boot
### END INIT INFO

echo "Waiting for timeout for startup"
sleep 70
./home/pi/Documents/ISENSIOT-SmartBabyMonitoring/PushNotifications/startupPushNotifications.sh >>/dev/null 2>/home/pi/pushNotifications.log
END

sudo chmod +x /etc/init.d/pushNotifications
sudo update-rc.d pushNotifications defaults

# #TalkToBaby on startup
# sudo touch /etc/init.d/talktobaby
# sudo tee /etc/init.d/talktobaby > /dev/null << 'END'
# #!/bin/bash
# ### BEGIN INIT INFO
# # Provides: talktobaby
# # Required-Start:    $all
# # Required-Stop: 
# # Default-Start:     5 
# # Default-Stop:      6 
# # Short-Description: talktobaby startup on boot
# ### END INIT INFO

# echo "Waiting for timeout for startup"
# sleep 2
# ./home/pi/Documents/ISENSIOT-SmartBabyMonitoring/TalkToBaby/startupTalkToBaby.sh
# END

# sudo chmod +x /etc/init.d/talktobaby
# sudo update-rc.d sensorhub defaults

#TalkToBaby on startup
# sudo touch /etc/systemd/system/talktobaby.service
# sudo tee /etc/systemd/system/talktobaby.service > /dev/null << 'END'
# [Unit]
# After=network.target

# [Service]
# ExecStart=sudo ./home/pi/Documents/ISENSIOT-SmartBabyMonitoring/TalkToBaby/startupTalkToBaby.sh

# [Install]
# WantedBy=default.target

# END

# sudo chmod 664 /etc/systemd/system/talktobaby.service
