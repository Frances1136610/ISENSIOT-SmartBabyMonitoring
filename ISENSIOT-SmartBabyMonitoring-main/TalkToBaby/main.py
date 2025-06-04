import time

import firebase_admin
from pydub import AudioSegment
from pydub.playback import play
import os

from firebase_admin import credentials, storage, firestore

#Checking if there is a internet connection
import socket

import subprocess

def CheckInternet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False

#Check internet connection
while (CheckInternet() == False):
    time.sleep(2)
    print("No internet connection")

print("Internet connected!")


cred = credentials.Certificate("/home/pi/Documents/ISENSIOT-SmartBabyMonitoring/TalkToBaby/isensiot-b9d43-firebase-adminsdk-qajgx-5e02470718.json")

firebase_admin.initialize_app(cred, {
    'storageBucket': 'isensiot-b9d43.appspot.com'
})

sound_file_name = r"playSound.3gpp"
bucket = storage.bucket()
db = firestore.client()

doc_ref = db.collection('sound').document('playSound')

def play_sound():
    blob = bucket.blob('audio')
    path = os.path.join("/home/pi/Documents/", sound_file_name)
    blob.download_to_filename(path)
    print(path)

    # audio = AudioSegment.from_file(sound_file_name, format="amr")
    # audio.export('playSound.mp3', format='mp3')

    # play(AudioSegment.from_file(path))
    subprocess.run('./playaudio.sh')


    # p = vlc.MediaPlayer('playSound.mp3')
    # p.play()
    # print(p.get_instance())

    doc_ref.set({"playSound": False})

i = 0
while True:
    print(i)
    if doc_ref.get({'playSound'}).to_dict()['playSound']:
        play_sound()
    i += 1
    time.sleep(1)
