#http://web.mit.edu/6.02/www/f2010/handouts/labs/lab7/lab7_1.py
# template tile for Lab #7, Task #1
import numpy
import matplotlib.pyplot as p
import waveforms as w
import lab7

p.ion()

# transmission rate
bits_per_second = 20000

# Convert message bits into samples, then use samples
# to modulate the amplitude of sinusoidal carrier.
# Limit the bandwidth of the transmitted signal to
# bw Hz.  Repeated here for convenience, use the lab7
# version (i.e. lab7.am_transmit).
def am_transmit(bits,samples_per_bit,sample_rate,fc,bw):
    # use helper function to create a sampled_waveform by
    # converting each bit into samples_per_bit samples
    samples = w.symbols_to_samples(bits,samples_per_bit,
                                   sample_rate)
    bandlimited_samples = samples.filter('low-pass',
                                         cutoff=bw)
    # now multiply by sine wave of specified frequency
    return bandlimited_samples.modulate(hz=fc)

# receive amplitude-modulated transmission:
def am_receive(samples,fc,samples_per_bit,channel_bw):
    pass # your code here

if __name__ == '__main__':
    # a random binary message with zeros at both ends to
    # ensure periodicity
    message_size = 30
    message = numpy.zeros(message_size+2,dtype=numpy.int)
    message[1:-1] = numpy.random.randint(2,size=message_size)

    # send it through transmitter, modulate to legal freq near 125 kHz
    samples_per_bit = lab7.samples_per_bit(lab7.sample_rate,
                                           bits_per_second)
    fc = lab7.quantize_frequency(125e3,lab7.sample_rate,
                                 len(message)*samples_per_bit)
    rf = lab7.am_transmit(message,samples_per_bit,lab7.sample_rate,
                     fc,lab7.channel_bw)
    rf.spectrum(title="spectrum after transmission")

    received = am_receive(rf,fc,samples_per_bit,lab7.channel_bw)
    if not numpy.array_equal(message,received):
        print "Error when listening to channel"
        print 'message: ',message
        print 'received:',received
    else:
        print "Message received correctly"