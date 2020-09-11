import numpy as np
import numpy.matlib
from scipy.fftpack import fft
import scipy.signal


class ACE(object):

    userMap = None  #map
    framesize = None #no. samples in one frame
    fs = None #sampling rate of audio
    fftsize = None #size of fft
    stimorder = None #order of electrode stim
    windowtype = None #type of window to apply
    outputmode = None #determines output after process step

    #precalculated values for speed
    numbins = None
    window = None
    params = None

    #memory
    bufhistory = None
    z = None

    def __init__(self):
        self.fftsize = 128
        self.stimorder = 'base-to-apex'
        self.windowtype = 'hanning'
        self.outputmode = 'matrix'


    def initialise(self, userMap, fs, framesize = self.fftsize):
        self.userMap = userMap
        self.fs = fs
        self.framesize = framesize

        #precalc params
        self.numbins = self.fftsize/2 + 1
        self.window = set_window(self.windowtype, self.framesize)
        self.userMap.set_stim_orer(self.stimorder)
        self.params = calculate_params(self.userMap, self)

        #preallocate memory buffers
        self.bufhistory = np.zeros(1, self.params.overlap)
        self.z = []

    def set_output_mode(self, mode):
        if lower(mode) == 'vector':
            self.outputmode = lower(mode)
        elif lower(mode) == 'matrix':
            self.outputmode = lower(mode)
        else:
            raise Exception("Supported output modes are vector or matrix")

    def process(self, input):
    #https://stackoverflow.com/questions/38453249/is-there-a-matlabs-buffer-equivalent-in-numpy
        [out, self.z, self.bufhistory] = self.run_ace(
            input, self.userMap, self.params, self.bufhistory, self.z)
        return out

    def buffer(x, n, p=0, opt=None):
        if opt not in ('nodelay', None):
            raise ValueError('{} not implemented'.format(opt))

        i = 0
        if opt == 'nodelay':
            # No zeros at array start
            result = x[:n]
            i = n
        else:
            # Start with `p` zeros
            result = np.hstack([np.zeros(p), x[:n - p]])
            i = n - p
        # Make 2D array, cast to list for .append()
        result = list(np.expand_dims(result, axis=0))

        while i < len(x):
            # Create next column, add `p` results from last col if given
            col = x[i:i + (n - p)]
            if p != 0:
                col = np.hstack([result[-1][-p:], col])

            # Append zeros if last row and not length `n`
            if len(col):
                col = np.hstack([col, np.zeros(n - len(col))])

            # Combine result with next row
            result.append(np.array(col))
            i += (n - p)

        return np.vstack(result).T

    def run_ace(self, input, userMap, params, bufhistory,z):

        #divide audio into time shifted chunks

        [u, z, bufhistory] = buffer( np.vstack(z,input), self.framesize, self.params.overlap, bufhistory)
        nFrames = u.shape(2)

        #apply window
        u = np.matmul(u, np.matlib.repmat(self.window, 1, nFrames))

        #perform FFT to get freq-time matrix and discard symmetric bins
        #not sure if this is done right, this may not be the same operation as;
            #u((numbins+1):end,:) =[];
        u = fft(u, self.fftsize)

        for i in range(self.numbins, np.ma.size(u,1)):
            for j in range(0,np.ma.size(u,1)):
                u[i][j] = []


        #calculate envelope using weighted sum of bin powers
        u = np.sqrt(params.weights * (np.matmul(u, np.conj(u))))

        #apply channel gains
        u = np.matmul(u, np.matlib.repmat(userMap.GainScale, 1, nFrames))

        #pick N highets values
        x0 = size(u,1) * (np.arange(0,nFrames-1))
        [_,index] = np.sort(u,1)
        #alternative to matlab list like indexing of u. that doesnt exist in python
        #divide value of offset by 22 (Number of Maxima).
        offset = np.matlib.repmat(x0, userMap.NMaximaReject,1)
        for i in range(0, userMap.NMaximaReject):
                u[i][temp[i]/22] = np.nan


        #apply compression
        u = compress(u, userMap.BaseLevel, userMap.SaturationLevel, userMap.LGF_Alpha, -1.0E-10)

        #reverse order of rows to match map channel order
        u = np.flip(u,1)

        #missing stuff for vector output

        #electrodes vector, which electrode isbeing fired
        out.electrodes = (np.matlib.repmat(userMap.ChannelOrder,1, nFrames))

        #output vector
        u = np.nan_to_num(u, nan = -1.0E-10)
        u[u<0] = 0
        out.levels = u

        out.periods = repmat(np.divide(np.ones(u.shape(1), 1), (np.multiply(userMap.AnalysisRate, userMap.NMaxima))),1, nFrames)

###helper functions
def calculate_params(m, self):
    params.shiftsize = m.Shift
    params.overlap = self.framesize - m.Shift

    #create weights matrix
    [params.weights, band_bins] = calculate_weights(m.NumberOfBands, self.numbins)

    #frequency response equalisation
    params.weights = freq_response_equalization(params.weights, self.window, self.framesize, m.NumberOfBands, band_bins)

    return params

def set_window(type,blocksize):
    if lower(type) == "hanning":
        a = [0.5, 0.5, 0.0, 0.0]
    elif lower(type) == "hamming":
        a = [0.54, 0.46, 0.0, 0.0]
    elif lower(type) == "blackman":
        a = [0.42, 0.5, 0.08, 0]
    else:
        raise Exception("unknown window type")

def calculate_weights(numbands, numbins):
    band_bins = np.array(FFT_band_bins(numbands))
    band_bins = band_bins.reshape(-1,1)
    w = np.zeros(numbands, numbins)
    bin = 2 #ignore bins 0 and 1
    for i in range(0,numbands):
        width = band_bins[i]
        for j in range(bin, (bin + width - 1)):
            w[i][j] = 1
            bin = bin + width
    return [w, band_bins]

def freq_response_equalization(w, window, blocksize, numbands, band_bins):
    freq_response =  scipy.signal.freqz(np.divide(window,2), 1, blocksize)
    power_response = np.matmul(freq_response, np.conj(freq_response))

    P1 = power_response[0]
    P2 = np.multiply(2, power_response[1])
    P3 = power_response[0], (np.multiply(2, power_response[2]))

    power_gains = np.zeros(numbands, 1)
    for i in range(0, numbands):
        width = band_bins(i)
        if width == 1:
            power_gains[i] = P1
        elif width == 2:
            power_gains[i] = P2
        else:
            power_gains[i] = P3

    for i in range(0, numbands - 1):
        for j in range(0, w.shape(2)):
            w[i][j] = np.divide(w[i][j], power_gains[i])
    return w

def FFT_band_bins(num_bands):
    if num_bands == 22:
        widths = [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8 ]# 7+15 = 22
    elif num_bands == 21:
        widths = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 5, 6, 6, 7, 8] # 7 + 14 = 21
    elif num_bands == 20:
        widths = [ 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 8 ] # 7 + 13 = 20
    elif num_bands == 19:
        widths = [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9] # 7 + 12 = 19
    elif num_bands == 18:
        widths = [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9] # 6+ 12 = 18
    elif num_bands == 17:
        widths = [1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9] # 5+12 = 17
    elif num_bands == 16:
        widths = [1, 1, 1, 2, 2, 2, 2, 2, 3, 4, 4, 5, 6, 7, 9, 11] #5+11 = 16
    elif num_bands == 15:
        widths = [1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 5, 6, 8, 9, 13] #5+10 = 15
    elif num_bands == 14:
        widths = [1, 2, 2, 2, 2, 2, 3, 3, 4, 5, 6, 8, 9, 13] # 4+10 = 14
    elif num_bands == 13:
        widths = [1, 2, 2, 2, 2, 3, 3, 4, 5, 7, 8, 10, 13] # 4 + 9 = 13
    elif num_bands == 12:
        widths = [1, 2, 2, 2, 2, 3, 4, 5, 7, 9, 11, 14] # 4 + 8 = 12
    elif num_bands == 11:
        widths = [1, 2, 2, 2, 3, 4, 5, 7, 9, 12, 15] # 4+7 = 11
    elif num_bands == 10:
        widths = [2, 2, 3, 3, 4, 5, 7, 9, 12, 15] # 3+7 = 10
    elif num_bands == 9:
        widths = [2, 2, 3, 3, 5, 7, 9, 13, 18] # 3 + 6 = 9
    elif num_bands == 8:
        widths = [2, 2, 3, 4, 6, 9, 14, 22] # 3 + 5 = 8
    elif num_bands == 7:
        widths = [3, 4, 4, 6, 9, 14, 22] #2 + 5 = 7
    elif num_bands == 6:
        widths = [3, 4, 6, 9, 15, 25] #2+4 = 6
    elif num_bands == 5:
        widths = [3, 4, 8, 16, 31] #2+3= 5
    elif num_bands == 4:
        widths = [7, 8, 16, 31] # 1 + 3 = 4
    elif num_bands == 3:
        widths = [7, 15, 40] # 1 + 2 = 3
    elif num_bands == 2:
        widths =[7, 55] # 1+1 = 2
    elif num_bands == 1:
        widths = 62 # 1
    else:
        raise Exception("illegal number of bands")




def compress(u, base_level, saturation_level, lgf_alpha, sub_mag):
    r = (np.subtract(u,base_level))/(saturation_level - base_level)
    sat = np.logical(r > 1)
    for i in range(0,len(r)):
        if sat[i]:
            r[i] = 1

    sub = np.logical(r < 0)
    for i in range(0,len(r)):
        if sub[i]:
            r[i] = 0;

    v = log(1 + lgf_alpha * r) / log(1 + lgf_alpha);

    for i in range(0,len(v)):
        if sub[i]:
            v[i] = sub_mag

    return [v, sub, sat]
