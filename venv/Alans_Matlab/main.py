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
print(stim, "X")
out = ace.process(stim)

#resample tf matrix
print(type(out.levels))
tfm = resample_tfm(out.levels, m.AnalysisRate, fs)

#create sine wave
t = np.array(range(0, (np.size(tfm,2))))
t = np.divide(t,fs)
print(len(m.F_Low))
freqs = [0] * 22
for i in range (0,len(m.F_Low)):
    print(i)
    freqs[i] =( m.F_Low[i] + m.F_High[i] )/ 2
#freqs = np.mean([m.F_Low, m.F_High], 2)
print(t, np.size(t))
sine_component = np.sin( np.multiply((2 * np.pi * freqs), t))

#modulate tf matrix onto sine wave carriers

mod_tfm = np.matmul(sine_component, tfm)

# sum bands  together to create the audio signal
voc_stim = np.sum(mod_tfm)
voc_stim.reshape(-1,1)


#play
#sd.play(voc_stim, fs)
#status = sd.wait()

# matlab soundsc normalises audio between -1 and 1
sf.write('myfile.wav', voc_stim, fs)



