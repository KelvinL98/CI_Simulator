


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

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.setGeometry(200,200,300,300)
        self.setWindowTitle("CI Simulator")
        self.initUI()

    def initUI(self):
        self.iDepthLabel = QtWidgets.QLabel(self)
        self.iDepthLabel.setText("Insertion Depth (mm)")
        self.iDepthLabel.move(100,120)
        self.iDepthNumBox = QtWidgets.QSpinBox(self)
        self.iDepthNumBox.setValue(20)
        self.iDepthNumBox.setMinimum(1)
        self.iDepthNumBox.setMaximum(30)
        self.iDepthNumBox.move(100,150)
        self.playButton = QtWidgets.QPushButton(self)
        self.playButton.setText("Play")
        self.playButton.move(200,150)
        self.iDepthSlider = QtWidgets.QSlider(self)
        self.iDepthSlider.setOrientation(QtCore.Qt.Vertical)
        self.iDepthSlider.setValue(20)
        self.iDepthSlider.setMinimum(1)
        self.iDepthSlider.setMaximum(30)
        self.iDepthSlider.move(50,150)
        self.iDepthSlider.setGeometry(QtCore.QRect(40,60,75,175))

        self.iDepthSlider.valueChanged.connect(self.handleiDepthSliderChange)
        self.iDepthNumBox.valueChanged.connect(self.handleiDepthNumBoxChange)
        self.playButton.clicked.connect(self.play)

    def handleiDepthSliderChange(self, value):
        self.iDepthNumBox.setValue(value)

    def handleiDepthNumBoxChange(self, value):
        self.iDepthSlider.setValue(value)

    def play(self):
        iDepth = self.iDepthSlider.value
        executeAce("camping16k.wav", iDepth, "BillsCenterFreqs.csv")

def executeAce( input, insertionDepth, freqsFile, cfFile=""):

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
    # resample tf matrix
    tfm = resample_tfm(out.levels, m.AnalysisRate, fs)
    # create sine wave

    t = np.array(range(0, (np.size(tfm, 1))))

    t = np.divide(t, fs)

    #assign freqs based off input file or use default values from mapping.
    if (cfFile):
        freqs = cfFromCSV(cfFile)
        #atm cf file is formatted in opposite order
        freqs = np.double(freqs[::-1])
        print("CF file")
    elif (freqsFile):

        freqs = cfFromCSV(freqsFile, insertionDepth)
        # get depth and spacings from frequencies
        insertionDepth, spacing = freqsToDepth(freqs)
        # get frequencies from spacing and depth
        freqs = freqsFromSpacing(spacing, insertionDepth)
        print(insertionDepth + "idepth")
    else:
        #use values from map
        freqs = [0] * 22
        for i in range(0, len(m.F_Low)):
            freqs[i] = (m.F_Low[i] + m.F_High[i]) / 2
        # freqs = np.mean([m.F_Low, m.F_High], 2)
        print("default")

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

    for i in range(0, np.size(mod_tfm, 0)):
        voc_stim.append(np.sum(mod_tfm[i]))

        # too big, so divided by 12 to 'normalise' values
    voc_stim = np.divide(voc_stim, 12)

    # voc_stim.reshape(-1,1)
    # play
    sd.play(voc_stim, fs)
    status = sd.wait()

    # matlab soundsc normalises audio between -1 and 1
    #sf.write("/OutputFiles/myfileDepth" + str(insertionDepth) + "mm.wav", voc_stim, fs)
    #return voc_stim


def window():
    app = QtWidgets.QApplication(sys.argv)
    win = Main()
    win.show()
    sys.exit(app.exec_())

window()
