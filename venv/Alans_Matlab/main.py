import numpy as np
import soundfile as sf
import ACE
import MAP
import resample_tfm
import sounddevice as sd
#define useful paramters
gain = 0 # input gain in dB

#get audio signal
[stim, fs] = sf.read("tapestry.wav")
stim = np.multiply(np.power(gain/1, 10), stim)

##load map
m = MAP.MAP(sampleRate = fs)

#ACE strategy initialisation
ace = ACE.ACE()
print(type(m), ">>>")
ace.initialise(m,fs)
ace.set_output_mode('matrix')

#run ACE on audio file and get time freq matrix

out = ace.process(stim)

#resample tf matrix

tfm = resample_tfm(out.levels, m.analysisRate, fs)

#create sine wave
t = np.array(arange(0, (np.size(tfm,2))))
t = np.divide(t/fs)
freqs = np.mean([m.F_Low, m.F_High], 2)
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



