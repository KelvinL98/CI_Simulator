import numpy as np
import soundfile as sf
import ACE
import MAP

import sounddevice as sd
import matplotlib
import matplotlib.pyplot as plt
import scipy

from resample_tfm import resample_tfm
from cfFromCSV import cfFromCSV
from mm2hz import mm2hz
from freqsFromCSV import freqsFromCSV
from freqsToDepth import freqsToDepth
from freqsFromSpacing import freqsFromSpacing


#define useful paramters
gain = 1 # input gain in dB, > 0


#need to downsample audio signal to 16k

#get audio signal
[stim, fs] = sf.read("camping16k.wav")


stim = np.multiply(np.power(gain/1, 10), stim)

##load map
m = MAP.MAP(sampleRate = fs)

#ACE strategy initialisation
ace = ACE.ACE()
ace.initialise(m,fs)
ace.set_output_mode('matrix')

#run ACE on audio file and get time freq matrix

out = ace.process(stim)
print(out)
#resample tf matrix
tfm = resample_tfm(out.levels, m.AnalysisRate, fs)
print(np.max(tfm), np.min(tfm))
#create sine wave

print(np.size(tfm,1))
t = np.array(range(0, (np.size(tfm,1))))

t = np.divide(t,fs)
#numbands = 22


#Read in cf from a file.
    #depth in mm
insertionDepth = 30
#freqs = freqsFromCSV("CI_spacing.csv", insertionDepth)


# use cfFromCSV to read CSV
    #then flip the array as cfFromCSV has reversed order.
freqs = cfFromCSV("BillsCenterFreqs.csv")
#get depth and spacings from frequencies
insertionDepth, spacing = freqsToDepth(freqs)
#get frequencies from spacing and depth
freqs = freqsFromSpacing(spacing, insertionDepth)
freqs = np.multiply(freqs, 2)
print("insertion depth: " + str(insertionDepth))


sine_component = []
for i in range(0, len(freqs)):
    curr = np.sin(2 * np.pi * t * freqs[i])
    sine_component.append(curr)




sine_component = np.asarray(sine_component)
#print(sine_component)


noise_component = np.random.normal(0,5,size=(sine_component.shape))
for i in range(0, len(freqs)):
    low = m.F_Low[i]/(fs/2)
    high = m.F_High[i]/(fs/2)

    currFilter = scipy.signal.butter(3, (low, high), btype = 'bandpass')
    noise_component[i] = scipy.signal.filtfilt(currFilter[0], currFilter[1], noise_component[i])
#print(tfm)
#modulate tf matrix onto sine wave carriers
#mod_tfm = np.multiply(sine_component, tfm)

#modulate tf onto noise
mod_tfm = np.multiply(noise_component,tfm)

#print(mod_tfm)
#sum bands  together to create the audio signal
voc_stim = []
mod_tfm = mod_tfm.T

print(np.min(mod_tfm), np.max(mod_tfm))

for i in range(0, np.size(mod_tfm,0)):
    voc_stim.append(np.sum(mod_tfm[i]))

    #too big, so divided by 12 to 'normalise' values
voc_stim = np.divide(voc_stim, 12)

#voc_stim.reshape(-1,1)
#play
#sd.play(voc_stim, fs)
#status = sd.wait()

# matlab soundsc normalises audio between -1 and 1

sf.write("./OutputFiles/myfileDepth" + str(insertionDepth) + "mm.wav", voc_stim, fs)



