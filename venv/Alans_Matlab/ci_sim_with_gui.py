


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

import sys

from insertionDepthGUI import Ui_MainWindow

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)

        def handleiDepthSliderChange(self, value):
            self.iDepthNumBox.setValue(value)

        def handleiDepthNumBoxChange(self, value):
            self.iDepthSlider.setValue(value)

        def get_input_file(self):
            self.inputFile, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open input file",
                                                                      r"C:\\Users\\Kelvin Liu\\PycharmProjects\\CI_Simulator",
                                                                      "input files (*.wav)")

        def get_cf_file(self):
            self.cfFile, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open CF file", "cf files (*.csv)")

        def get_freqs_file(self):
            self.freqsFile, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open frequency file",
                                                                      "frequecy files (*.csv)")

        def retranslateUi(self, MainWindow):
            _translate = QtCore.QCoreApplication.translate
            MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
            self.playButton.setText(_translate("MainWindow", "Play"))
            self.label.setText(_translate("MainWindow", "Insertion Depth (mm)"))
            self.menuFile.setTitle(_translate("MainWindow", "File"))
            self.actionSelect_Input_File.setText(_translate("MainWindow", "Load input file"))
            self.actionSelect_CF_File.setText(_translate("MainWindow", "Load CF file"))
            self.actionLoad_frequency_map.setText(_translate("MainWindow", "Load frequency map"))

        def playClicked(self, file, insertionDepth, cfFile="", freqsFile=""):
            output = executeAce(file, insertionDepth, cfFile=cfFile, freqsFile=freqsFile)
            # what to do with output???

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

        if (cfFile):
            freqs = cfFromCSV(cfFile)
            # atm cf file is formatted in opposite order
            freqs = np.double(freqs[::-1])
        elif (freqsFile):
            freqs = freqsFromCSV(freqsFile, insertionDepth)
        else:
            # use values from map
            freqs = [0] * 22
            for i in range(0, len(m.F_Low)):
                freqs[i] = (m.F_Low[i] + m.F_High[i]) / 2
            # freqs = np.mean([m.F_Low, m.F_High], 2)

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
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())

