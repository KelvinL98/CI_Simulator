import numpy as np
import soundfile as sf
import ACE
import MAP
from resample_tfm import resample_tfm
import sounddevice as sd
#define useful paramters
gain = 1 # input gain in dB, > 0

#get audio signal
[stim, fs] = sf.read("tapestry.wav")
stim = np.multiply(np.power(gain/1, 10), stim)

##load map
m = MAP.MAP(sampleRate = fs)

#ACE strategy initialisation
ace = ACE.ACE()
ace.initialise(m,fs)
ace.set_output_mode('matrix')

#run ACE on audio file and get time freq matrix

out = ace.process(stim)

#resample tf matrix
tfm = resample_tfm(out.levels, m.AnalysisRate, fs)

#create sine wave

print(np.size(tfm,1))
t = np.array(range(0, (np.size(tfm,1))))

t = np.divide(t,fs)
freqs = [0] * 22
for i in range (0,len(m.F_Low)):

    freqs[i] =( m.F_Low[i] + m.F_High[i] )/ 2
#freqs = np.mean([m.F_Low, m.F_High], 2)

sine_component = []
for i in range(0, len(freqs)):
    curr = np.sin(2 * np.pi * t * freqs[i])
    sine_component.append(curr)

sine_component = np.array(sine_component)
#modulate tf matrix onto sine wave carriers
mod_tfm = np.multiply(sine_component, tfm)


# sum bands  together to create the audio signal
voc_stim = []
mod_tfm = mod_tfm.T
for i in range(0, np.size(mod_tfm,0)):
    voc_stim.append(np.sum(mod_tfm[i]))
print(voc_stim)
#voc_stim.reshape(-1,1)
#play
#sd.play(voc_stim, fs)
#status = sd.wait()

# matlab soundsc normalises audio between -1 and 1
sf.write('myfile.wav', voc_stim, fs)



