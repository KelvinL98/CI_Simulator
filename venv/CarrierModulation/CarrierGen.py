# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CarrierGen.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import pyaudio
from scipy.io import wavfile
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
import matplotlib
import wave


p = pyaudio.PyAudio()
frequency = 1

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(198, 172)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalSlider = QtWidgets.QSlider(self.centralwidget)
        self.verticalSlider.setGeometry(QtCore.QRect(50, 30, 20, 91))
        self.verticalSlider.setMinimum(1)
        self.verticalSlider.setMaximum(999)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalSlider.setTickInterval(100)
        self.verticalSlider.setObjectName("verticalSlider")
        self.verticalSlider.valueChanged.connect(self.update)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 10, 41, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(90, 60, 35, 10))
        self.label_2.setObjectName("label_2")
        self.radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton.setGeometry(QtCore.QRect(140, 40, 62, 14))
        self.radioButton.setObjectName("radioButton")
        self.radioButton_2 = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton_2.setGeometry(QtCore.QRect(140, 60, 62, 14))
        self.radioButton_2.setObjectName("radioButton_2")

        self.playButton = QtWidgets.QPushButton(self.centralwidget)
        self.playButton.clicked.connect(self.play)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 198, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Frequency"))
        self.radioButton.setText(_translate("MainWindow", "Sine"))
        self.radioButton_2.setText(_translate("MainWindow", "Noise"))


    def update(self):
        x = str(self.verticalSlider.value())
        self.label_2.setText(x + " Hz")
        self.label_2.adjustSize()
        #genSine(self.verticalSlider.value())

    def play(self):
        x = int(self.verticalSlider.value())
        print(x)
        getSine(x)

def genSine(f):
    #1024frames per chunk
    #125ms per chunk
    #8192 sample rate
    fs = 44100
    chunk = 2048
    duration = 100
    samples = np.arange(chunk * duration)
    #samples = np.linspace(0, 1024)
    signal = (np.sin(2 * np.pi * np.arange(chunk * duration) * f/ fs)).astype(np.float32)
    #signal *= 32767
    #signal = np.int16(signal)
   # samples = np.int16(samples)

    print(samples)
    print(len(samples), len(signal))
    print(signal)
    plt.plot(samples, signal)
    plt.show()
    print("getSine")

    stream = p.open(format = pyaudio.paFloat32,
                    channels = 1,
                    rate = 44100,
                    output = True)
    stream.write(signal)
    stream.stop_stream()
    stream.close()
    p.terminate()

    write(str(f) + ' Hz_sine_wave_1.wav', fs, signal)


def genSine2(freq):
    #Python & NumPy Synthesizer 02: Sine wave audio with NumPy
    fs = 44100
    duration = 5.0

    samples = np.arange(fs * duration)
    signal = np.sin(2 * np.pi * samples * freq /fs)
    signal_quiet = signal * 0.3
    signal_int = np.int16(signal_quiet * 32767)
    write(str(freq) + ' Hz_sine_wave.wav', fs, signal_int)

genSine(500)
#genSine2(500)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
