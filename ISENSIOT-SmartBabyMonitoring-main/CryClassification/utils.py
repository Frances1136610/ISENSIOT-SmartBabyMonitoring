import librosa
import numpy as np
import pyaudio
import wave
import os
import soundfile as sf
import pyloudnorm as pyln
import pandas as pd
from scipy.io import wavfile
import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore
from datetime import datetime, timezone, timedelta


import sys
script_dir = os.path.dirname( __file__ )
mymodule_dir = os.path.join( script_dir, '..')
sys.path.append( mymodule_dir )
from sensorhub import *

# cred = credentials.Certificate("../cred.json")
# firebase_admin.initialize_app(cred)
# store = fireDb.client()
#       

n_mfcc = 40
n_fft = 1024  #Setting the FFT size to 1024
hop_length = 10*16 #25ms*16khz samples has been taken
win_length = 25*16 #25ms*16khz samples has been taken for window length
window = 'hann' #Hann window used
n_chroma=12
n_mels=128
n_bands=7 #We are extracting the 7 features out of the spectral contrast
fmin=100
bins_per_ocatve=12

form_1 = pyaudio.paInt16
chans = 1
samp_rate = 44100
chunk = 4096
record_secs = 8
#dev_index = 1
wav_output_filename = "baby_recording.wav"

normalized_wav_output_filename = "normalized_audio.wav"

#Extract features to represent an audiofile
def extract_features(file_path):
    try:
        y, sr = librosa.load(file_path, sr=16000)
        #mfcc = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40,n_fft=n_fft,hop_length=hop_length,win_length=win_length,window=window).T,axis=0)
        mel = np.mean(librosa.feature.melspectrogram(y=y, sr=sr,n_fft=n_fft, hop_length=hop_length, win_length=win_length, window='hann',n_mels=n_mels).T,axis=0)
        stft = np.abs(librosa.stft(y))
        chroma = np.mean(librosa.feature.chroma_stft(S=stft, y=y, sr=sr).T,axis=0)
        contrast = np.mean(librosa.feature.spectral_contrast(S=stft, y=y, sr=sr,n_fft=n_fft,
                                                      hop_length=hop_length, win_length=win_length,
                                                      n_bands=n_bands, fmin=fmin).T,axis=0)
        tonnetz =np.mean(librosa.feature.tonnetz(y=y, sr=sr).T,axis=0)
        features = np.concatenate((chroma, mel, contrast, tonnetz))
        return features
    except:
        print("Error: Exception occurred in feature extraction")
        return None

#Record 7 seconds of baby sounds and save to a file
def record_baby_sound():
        p = pyaudio.PyAudio()

        stream = p.open(format=form_1, rate=samp_rate, channels=chans, input=True, frames_per_buffer=chunk)
        frames =[]

        for ii in range(0, int((samp_rate/chunk)*record_secs)):
                data = stream.read(chunk)
                frames.append(data)
                
        stream.stop_stream()
        stream.close()
        p.terminate()

        wavefile = wave.open(wav_output_filename, 'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(p.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close

#Set volume of a soundfile to desired level
def normalize_sound(file_path):
        data, rate = sf.read(file_path)
        meter = pyln.Meter(rate)
        loudness = meter.integrated_loudness(data)
        print(loudness)
        normalized_data = pyln.normalize.loudness(data, loudness, -12)
        normalized_audio = np.int16(normalized_data * 32767)
        wavfile.write(normalized_wav_output_filename, samp_rate, normalized_audio)
        


def send_to_firestore(emotion, isCrying):
        print("SENDING INFLUXDB and firestore")
        # timezone_offset = +2.0
        # tzinfo = timezone(timedelta(hours=timezone_offset))
        # time = datetime.now(tzinfo)
        # data = {'emotion': emotion, 'isCrying': isCrying, 'timestamp': time}
        # doc_ref.add(data)

        fireDb.sendDataEmotion("babyEmotion", emotion, isCrying)
       
        influxDb.sendData("testing", "testing", "isCrying", "bool", bool(isCrying))

def getDeviceIndex():
    p = pyaudio.PyAudio()

    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i))
