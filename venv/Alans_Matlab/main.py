

import numpy as np
import soundfile as sf
import ACE
import MAP
from resample_tfm import resample_tfm
import sounddevice as sd
import matplotlib
import matplotlib.pyplot as plt
import scipy
#define useful paramters
gain = 1 # input gain in dB, > 0


#downsample audio signal to 16k


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


freqs = [0] * 22
for i in range (0,len(m.F_Low)):


    freqs[i] =( m.F_Low[i] + m.F_High[i] )/ 2
#freqs = np.mean([m.F_Low, m.F_High], 2)

#Read in freqs from a file.

sine_component = []
for i in range(0, len(freqs)):
    curr = np.sin(2 * np.pi * t * freqs[i])
    sine_component.append(curr)


sine_component = np.asarray(sine_component)
np.savetxt('sine.csv', sine_component, delimiter=',')

#print(tfm)
#modulate tf matrix onto sine wave carriers
mod_tfm = np.multiply(sine_component, tfm)

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
sf.write('myfile.wav', voc_stim, fs)



