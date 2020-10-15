import numpy as np
import numpy.matlib
from scipy.fftpack import fft
import scipy.signal
import MAP



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


    def initialise(self, userMap, fs, framesize = 0):
        self.userMap = userMap
        self.fs = fs
        if framesize == 0:
            print("fft", self.fftsize)
            self.framesize = self.fftsize
        else:
            self.framesize = framesize
            print("gg", self.framesize)

        #precalc params
        self.numbins = self.fftsize/2 + 1

        self.window = set_window(self.windowtype, self.framesize)
        #hardcoded
        #self.userMap.set_stim_orer(self.stimorder)
        self.params = calculate_params(self.userMap, self)

        #preallocate memory buffers
        self.bufhistory = np.zeros(1, self.params.overlap)
        self.z = []

    def set_output_mode(self, mode):
        if mode.lower() == 'vector':
            self.outputmode = mode.lower()
        elif mode.lower() == 'matrix':
            self.outputmode = mode.lower()
        else:
            raise Exception("Supported output modes are vector or matrix")

    def process(self, input):
    #https://stackoverflow.com/questions/38453249/is-there-a-matlabs-buffer-equivalent-in-numpy

        [out, self.z, self.bufhistory] = self.run_ace(
            input, self.userMap, self.params, self.bufhistory, self.z)
        return out



    def run_ace(self, input, userMap, params, bufhistory,z):

        #divide audio into time shifted chunks
        ##matlab signature buffer(x,n,p,opt) signal vector x, over/underlap by p,segments of length n,
        #  opt vector of samples to precede
        #[z;input] is the same as input as far as i can tell as z is null.

        #this version has no buffer history!!!! will need to implement

        #[u, z, bufhistory] = buffer( input, self.framesize, p=self.params.overlap, opt = bufhistory)
        print(self.framesize, "framesize")
        print(input.shape, "input size")
        u = buffer( input, self.framesize, p=int(self.params.overlap))
        #for i in range(0, u.shape(1)):
        shape = u.shape
        u = u[0:shape[0]][0:shape[1]-1]
        print(u.shape, "XXXX")

        u = np.delete(u, 2798,1)



        print(u.shape, "XXXX")
        u = np.array(u)

        _,nFrames = u.shape
        nFrames = nFrames


        #apply window
        #print(u[0], u[127], "UUUUU")
        window = np.matlib.repmat(self.window, 1, nFrames)


        u = np.multiply(u, window)

        #perform FFT to get freq-time matrix and discard symmetric bins
        #not sure if this is done right, this may not be the same operation as;
            #u((numbins+1):end,:) =[];

        u = fft(u, self.fftsize,0)

        delete = range(int(self.numbins), np.ma.size(u,0))
        u = np.delete(u,delete,0)
        print(u.shape)
        '''for i in range(int(self.numbins), np.ma.size(u,0)):

            for j in range(0,y):

                indexshift = x * y
                delete.append(indexshift+j)
                #np.delete(u,(i,j))
                #u[i][j] = np.nan
            x = x + 1
            print(x)
        print(len(delete))
        print(u.shape,"U")
        u = np.delete(u,delete)
        print(u.shape, "u")
        '''
        #calculate envelope using weighted sum of bin powers
        u = np.sqrt(np.matmul(params.weights  ,(np.multiply(u, np.conj(u)))))

        #apply channel gains
        u = np.multiply(u, np.matlib.repmat(userMap.GainScale, 1, nFrames))

        #pick N highets values
        print(np.ma.size(u,0), np.arange(0,nFrames))
        x0 = np.multiply(np.ma.size(u,0) , (np.arange(0,nFrames)))
        print(x0)
        index = np.argsort(u,1)

        #alternative to matlab list like indexing of u. that doesnt exist in python
        #divide value of offset by 22 (Number of Maxima).
        x0NMaxima = np.matlib.repmat(x0, int(userMap.NMaximaReject),1)

        shape = u.shape
        print(x0, len(x0), " here")
        print(np.add(index[0:int(userMap.NMaximaReject)], x0NMaxima).shape, " SHAPE")
        for i in (np.add(index[0:int(userMap.NMaximaReject)], x0NMaxima)):
                #print(i, shape[1], shape[0])

                for j in i:
                    offset = np.floor(j/shape[1]/22)

                    #u[int(offset)][j%shape[1]] = np.nan

        #apply compression
        u = compress(u, userMap.BaseLevel, userMap.SaturationLevel, userMap.LGF_alpha, -1.0E-10)

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
    params = type('param', (object,), {'shiftsize': m.Shift, 'overlap': self.framesize- m.Shift, 'weights': []})
    params.shiftsize = m.Shift
    params.overlap = self.framesize - m.Shift

    #create weights matrix
    [params.weights, band_bins] = calculate_weights(m.NumberOfBands, self.numbins)

    #frequency response equalisation
    params.weights = freq_response_equalization(params.weights, self.window, self.framesize, m.NumberOfBands, band_bins)

    return params

def set_window(type,blocksize):

    if type.lower() == "hanning":
        a = [0.5, 0.5, 0.0, 0.0]
    elif type.lower() == "hamming":
        a = [0.54, 0.46, 0.0, 0.0]
    elif type.lower() == "blackman":
        a = [0.42, 0.5, 0.08, 0]
    else:
        raise Exception("unknown window type")
    n = np.vstack(np.array(range(0,int(blocksize))))
    r = np.divide(np.multiply((2 * np.pi), n), blocksize)
    # w = a(1) - a(2)*cos(r) + a(3)*cos(2*r) - a(4)*cos(3*r);
    w1 = np.subtract(a[0], np.multiply(a[1], np.cos(r)))
    w2 = np.multiply(a[2], np.cos(np.multiply(2, r)) )
    w3 = np.multiply(a[3], np.cos(np.multiply(3,r)))
    w = np.add(w1,w2)
    w = np.subtract(w,w3)
    return w

def calculate_weights(numbands, numbins):
    band_bins = np.array(FFT_band_bins(numbands))

    band_bins = band_bins.reshape(-1,1)
    band_bins = np.insert(band_bins,0,0) #add zero att the front of array so indexing matches matlab code

    w = np.zeros((numbands, int(numbins)))
    bin = 3 #ignore bins 0 and 1

    for i in range(1,numbands+1):
        width = band_bins[i]
        setToOne(w, i, width, bin)

        bin = bin + width
    return [w, band_bins]

def setToOne(w, i, width, bin):
    r = bin + int(width) - 1
    j = bin
    while j < r:
        #-1 offset to match array to matlab array which starts at 1 rather than 0.
        w[i-1][j-1] = 1
        j+=1




def freq_response_equalization(w, window, blocksize, numbands, band_bins):
    [freq_response, _] =  scipy.signal.freqz(np.divide(window,2), 1, blocksize)
    conj = np.conj(freq_response)
    power_response = np.multiply(np.asarray(freq_response), np.asarray(conj))

    P1 = power_response[0]
    P2 = np.multiply(2, power_response[1])
    P3 = np.add(power_response[0], (np.multiply(2, power_response[2])))

    power_gains = np.zeros((numbands, 1))
    for i in range(0, numbands):
        width = band_bins[i]
        if width == 1:
            power_gains[i] = P1
        elif width == 2:
            power_gains[i] = P2
        else:
            power_gains[i] = P3

    for i in range(0, numbands - 1):
        r = np.asarray(w).shape
        for j in range(0, r[1]):
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
    return widths




def compress(u, base_level, saturation_level, lgf_alpha, sub_mag):
    r = (np.subtract(u,base_level))/(saturation_level - base_level)
    print(r)
    sat = np.greater(r, 1)
    print(sat)


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


def buffer(x, n, p=0, opt=None):
    if opt not in ('nodelay', None):
        raise ValueError('{} not implemented'.format(opt))

    n = int(n)
    p = int(p)
    i = 0
    if opt == 'nodelay':
        # No zeros at array start
        result = x[:n]
        i = n
    else:
        # Start with `p` zeros
        result = np.hstack([np.zeros(p), x[:n-p]])
        i = n-p
        print(i, "n-p")
    # Make 2D array, cast to list for .append()
    result = list(np.expand_dims(result, axis=0))

    while i < len(x):
        # Create next column, add `p` results from last col if given
        col = x[i:i+(n-p)]

        if p != 0:
            col = np.hstack([result[-1][-p:], col])

        # Append zeros if last row and not length `n`
        if len(col):
            col = np.hstack([col, np.zeros(n - len(col))])

        # Combine result with next row
        result.append(np.array(col))
        i += (n - p)
    print(np.ma.size(result))
    res = np.vstack(result).T
    print(res[0][0], res[127][2798])
    print(res.shape)
    return np.vstack(result).T