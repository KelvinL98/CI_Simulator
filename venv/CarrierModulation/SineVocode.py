from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import time
import numpy as np
from pyaudio import PyAudio, paFloat32, paContinue, paInt16, paComplete
import threading
import scipy.signal
import matplotlib.pyplot as plt
import matplotlib
#matplotlib.use('TkAgg')

from scipy.io import wavfile
from scipy.io.wavfile import write
import wave

filter_on = False
stop = False

fs = 22050 #sample rate
chunk = 128 #frame size
f = 120 #frequency of sine carrier

carrier = np.nan

record = np.empty([chunk])

class MyWindow(QMainWindow):
    #PYQT5 TUTORIALS, TECH WITH TIM

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("Sine Vocode")
        self.initUI()

    def initUI(self):

        self.vocode = QtWidgets.QRadioButton(self)
        self.vocode.setText("Sine Vocode")
        self.vocode.move(100,150)
      #  self.filter.clicked.connect(self.clicked)
        self.vocode.clicked.connect(self.checked)

        self.stopButton = QtWidgets.QPushButton(self)
        self.stopButton.setText("Stop")
        self.stopButton.clicked.connect(self.stop)

    def stop(self):
        global stop
        stop = True

    def checked(self):
        global filter_on
        if filter_on:
            filter_on = False
        else:
            filter_on = True


    def clicked(self):
        global stop
        stop = True
        stream.stop_stream()
        stream.close()
        pa.terminate()


def window():
    app = QApplication(sys.argv)
    win = MyWindow()

    win.show()
    sys.exit(app.exec_())

def genSine(frequency, samplingFrequency, chunk):
    global carrier
    sine = (np.sin(2 * np.pi * np.arange(chunk) * frequency/ samplingFrequency
                   )).astype(np.float32)
    carrier = sine


def genNoise():
    global carrier
    #return np.random.normal(0, 0.1, chunk)

    
def ampMod(s1, s2):
    return np.multiply(s1, s2)

def filter(signal):
    global fs

    lowcut = 20.0
    highcut = 50.0

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq

    order = 2

    b, a = scipy.signal.butter(order, [low, high], 'bandpass', analog=False)

    return scipy.signal.filtfilt(b, a, signal)

def genFilter(sampleRate):
    # HOW TO MAKE A BANDPASS FILTER IN PYTHON| THE EASY WAY, Leron Julian
    lowcut = 20.0
    highcut = 50.0

    nyq = 0.5 * sampleRate
    low = lowcut / nyq
    high = highcut / nyq

    order = 2

    b, a = scipy.signal.butter(order, [low, high], 'bandpass', analog=False)
    return b, a

def callback(in_data, frame_count, time_info, flag):
    global filter_on, carrier, fs, f, chunk, filters, record

    audio_data = np.frombuffer(in_data, dtype=np.float32)
    audio_data_s = audio_data

    time = np.linspace(0,1, 1024)
    print("audio")

    if filter_on:
       # filtered = BPfilter(audio_data_s)

        #filtered = filter(audio_data_s)
        filtered = ampMod(audio_data_s , carrier)
         
        audio_data_s = filtered.astype(np.float32)
        #append current chunk to record
        record =  np.append(record, audio_data_s)

    if stop:
       # signal_int = np.int16(np.multiply(record, 32767))
        #write record to wav file.
        write(str(f) + ' Hz_sine_vocoded.wav', fs, record)
        print("Stop")
        return (audio_data_s, paComplete)

    return (audio_data_s, paContinue)

print("pa")
pa = PyAudio()
print("pa started")
stream = pa.open(format=paFloat32,
                 channels=1,
                 rate=fs,
                 output=True,
                 input=True,
                 frames_per_buffer=chunk,
                 stream_callback=callback)

def keep_alive(stop):
    while stream.is_active():

        if stop:
            break
        time.sleep(0.1)




genSine(f, fs, chunk)
thread = threading.Thread(target=keep_alive, args=(stop,))
stream.start_stream()
thread.start()
window()
