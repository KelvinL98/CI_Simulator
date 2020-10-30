# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'insertionDepthGUI.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np
import soundfile as sf
import ACE
import MAP
from resample_tfm import resample_tfm
import sounddevice as sd
import matplotlib
import matplotlib.pyplot as plt
import scipy
from cfFromCSV import cfFromCSV
from mm2hz import mm2hz
from freqsFromCSV import freqsFromCSV


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(210, 246)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(20, 150, 151, 31))
        self.pushButton.setObjectName("pushButton")
        self.idepthverticalSlider = QtWidgets.QSlider(self.centralwidget)
        self.idepthverticalSlider.setGeometry(QtCore.QRect(30, 40, 16, 101))
        self.idepthverticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.idepthverticalSlider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.idepthverticalSlider.setTickInterval(0)
        self.idepthverticalSlider.setObjectName("idepthverticalSlider")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(50, 10, 81, 21))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.iDepthlineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.iDepthlineEdit.setGeometry(QtCore.QRect(80, 80, 51, 21))
        self.iDepthlineEdit.setObjectName("iDepthlineEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 210, 18))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSelect_Input_File = QtWidgets.QAction(MainWindow)
        self.actionSelect_Input_File.setObjectName("actionSelect_Input_File")
        self.actionSelect_CF_File = QtWidgets.QAction(MainWindow)
        self.actionSelect_CF_File.setObjectName("actionSelect_CF_File")
        self.actionLoad_frequency_map = QtWidgets.QAction(MainWindow)
        self.actionLoad_frequency_map.setObjectName("actionLoad_frequency_map")
        self.menuFile.addAction(self.actionSelect_Input_File)
        self.menuFile.addAction(self.actionSelect_CF_File)
        self.menuFile.addAction(self.actionLoad_frequency_map)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Play"))
        self.label.setText(_translate("MainWindow", "Insertion Depth (mm)"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSelect_Input_File.setText(_translate("MainWindow", "Load input file"))
        self.actionSelect_CF_File.setText(_translate("MainWindow", "Load CF file"))
        self.actionLoad_frequency_map.setText(_translate("MainWindow", "Load frequency map"))

    def playClicked(self, file, insertionDepth, cfFile = "", freqsFile = ""):
        output = executeAce(file, insertionDepth, cfFile = cfFile, freqsFile = freqsFile)

def executeAce(input, insertionDepth, cfFile="", freqsFile=""):

    # define useful paramters
    gain = 1  # input gain in dB, > 0

    # downsample audio signal to 16k

    # get audio signal
    [stim, fs] = sf.read(input)

    stim = np.multiply(np.power(gain / 1, 10), stim)

    ##load map
    m = MAP.MAP(sampleRate=fs)

    # ACE strategy initialisation
    ace = ACE.ACE()
    ace.initialise(m, fs)
    ace.set_output_mode('matrix')

    # run ACE on audio file and get time freq matrix

    out = ace.process(stim)
    print(out)
    # resample tf matrix
    tfm = resample_tfm(out.levels, m.AnalysisRate, fs)
    print(np.max(tfm), np.min(tfm))
    # create sine wave

    print(np.size(tfm, 1))
    t = np.array(range(0, (np.size(tfm, 1))))

    t = np.divide(t, fs)
    # numbands = 22

    # Read in cf from a file.
    # depth in mm
    # insertionDepth = 20
    # freqs = freqsFromCSV("CI_spacing.csv", insertionDepth)
    freqs = cfFromCSV("BillsCenterFreqs.csv")
    # flip for cfFromCSV and leave in order for freqsFromCSV
    freqs = np.double(freqs[::-1])

    sine_component = []
    for i in range(0, len(freqs)):
        curr = np.sin(2 * np.pi * t * freqs[i])
        sine_component.append(curr)

    sine_component = np.asarray(sine_component)
    # print(tfm)
    # modulate tf matrix onto sine wave carriers
    mod_tfm = np.multiply(sine_component, tfm)

    # print(mod_tfm)
    # sum bands  together to create the audio signal
    voc_stim = []
    mod_tfm = mod_tfm.T

    print(np.min(mod_tfm), np.max(mod_tfm))

    for i in range(0, np.size(mod_tfm, 0)):
        voc_stim.append(np.sum(mod_tfm[i]))

        # too big, so divided by 12 to 'normalise' values
    voc_stim = np.divide(voc_stim, 12)

    # voc_stim.reshape(-1,1)
    # play
    # sd.play(voc_stim, fs)
    # status = sd.wait()

    # matlab soundsc normalises audio between -1 and 1

    # sf.write("/OutputFiles/myfileDepth" + str(insertionDepth) + "mm.wav", voc_stim, fs)
    return voc_stim


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
