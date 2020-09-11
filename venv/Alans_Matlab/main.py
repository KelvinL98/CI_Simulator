import numpy as np
import soundfile as sf
import ACE
import MAP

#define useful paramters
gain = 0 # input gain in dB

#get audio signal
[stim, fs] = sf.read('tapesty.wav')
stim = np.multiply(np.power(gain/1, 10), stim)

##load map
m = MAP(sampleRate = fs)

#ACE strategy initialisation
ace = ACE()
ace.initialise(m,fs)
ace.set_output_mode('matrix')

#run ACE on audio file and get time freq matrix

out = ace.process(stim)

#resample tf matrix

tfm = resample_tfm



