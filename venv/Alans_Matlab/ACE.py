import numpy as np
import numpy.matlib
from scipy.fftpack import fft
class ACE(object):

    userMap #map
    framesize #no. samples in one frame
    fs #sampling rate of audio
    fftsize #size of fft
    stimorder #order of electrode stim
    windowtype #type of window to apply
    outputmode #determines output after process step

    #precalculated values for speed
    numbins
    window
    params

    #memory
    bufhistory
    z

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
        self.params = calc_params(self.userMap, self)

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
        nFrames = np.size(u, axis = 2)

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
        temp = np.matlib.repmat(x0, userMap.NMaximaReject,1)

        for i in range(1,userMap.NMaximaReject):
            for j in range(0,np.ma.size(u,1)):
                u[i][j]= np.NAN
        

