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

filter_on = False
stop = False
class MyWindow(QMainWindow):
    #PYQT5 TUTORIALS, TECH WITH TIM

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(200, 200, 300, 300)
        self.setWindowTitle("BP Filter")
        self.initUI()

    def initUI(self):
       # self.flabel = QtWidgets.QLabel(self)
        #self.flabel.setText("OFF")

        self.filter = QtWidgets.QRadioButton(self)
        self.filter.setText("Filter")
        self.filter.move(100,150)
      #  self.filter.clicked.connect(self.clicked)
        self.filter.clicked.connect(self.checked)

        self.quit = QtWidgets.QPushButton(self)
        self.quit.setText("Quit")

        self.stop = QtWidgets.QPushButton(self)
        self.stop.setText("STOP")
        self.stop.clicked.connect(self.clicked)

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

#HOW TO MAKE A BANDPASS FILTER IN PYTHON| THE EASY WAY, Leron Julian
samplerate = 22100
lowcut = 20.0
highcut = 2000.0

nyq = 0.5 * samplerate
low = lowcut / nyq
high = highcut / nyq

order = 2

b,a = scipy.signal.butter(order, [low, high], 'bandpass', analog = False)
#y = scipy.signal.filtfilt(b, a, signal, axis= 0)

N=32
bpass = scipy.signal.remez(N, [0.0,0.05,0.1,0.3,0.4,0.5], [0.001,1.0,0.001], weight = [100.0,1.0,100.0])
z = np.zeros(N-1)

def callback(in_data, frame_count, time_info, flag):
    global filter_on, stop, z

    audio_data = np.frombuffer(in_data, dtype=np.float32)
    audio_data_s = audio_data

    time = np.linspace(0,1, 1024)
    print("audio")
  #  plt.plot(time, audio_data_s)
   # plt.show(block = True)
  #  plt.interactive(False)
    if filter_on:
       # filtered = BPfilter(audio_data_s)
        filtered = scipy.signal.filtfilt(b, a, audio_data_s)
        audio_data_s = filtered.astype(np.float32)

    if stop:
        return (audio_data_s, paComplete)
    plt.plot(time, audio_data_s)
    plt.show()
    return (audio_data_s, paContinue)

print("pa")
pa = PyAudio()
print("pa started")
stream = pa.open(format=paFloat32,
                 channels=1,
                 rate=8192,
                 output=True,
                 input=True,
                 frames_per_buffer=1024,
                 stream_callback=callback)

def keep_alive(stop):
    while stream.is_active():

        if stop:
            break
        time.sleep(0.1)

print("ok")
thread = threading.Thread(target=keep_alive, args=(stop,))
stream.start_stream()

print("looped")
thread.start()



window()
