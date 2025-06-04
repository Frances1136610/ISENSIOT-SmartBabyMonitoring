# Venv needed to be created with "python3 -m venv venv --system-site-packages" otherwise unsolveble errors with libcamera
from picamera2 import Picamera2
from matplotlib import pyplot as plt

import time
import cv2
import numpy as np

picam2 = Picamera2()
picam2.preview_configuration.main.size = (720,480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

while True:
    im= picam2.capture_array()
    im = cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE) #Rotate view 90 degrees so that camera can be rotated to give a portrait view
    cv2.imshow("Camera", im)
    
    if cv2.waitKey(1)==ord('q'):
        break
cv2.destroyAllWindows()