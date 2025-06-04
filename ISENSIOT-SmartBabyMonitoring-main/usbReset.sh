#!/bin/bash

USB_DEVICE="/dev/ttyUSB0"
BUS="001"
DEVICE="008"

while true; do
    if [ ! -e $USB_DEVICE ]; then
        echo "$USB_DEVICE not found. Resetting USB device."
        # sudo usbreset /dev/bus/usb/$BUS/$DEVICE
        echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/unbind
        sleep 1
        echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/bind
    else
        echo "$USB_DEVICE is present."
        exit
    fi
    sleep 5
done
