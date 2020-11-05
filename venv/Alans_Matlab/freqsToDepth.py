import numpy as np
from hzTomm import hzTomm
#returns insertion depth and mm spacing of each electrode
def freqsToDepth(freqs):
    #get the the frequency of the deepest electrode
    print(freqs, 'freqs')
    insertionDepth = hzTomm(freqs[np.size(freqs) -1])
    print(insertionDepth, "depth")
    #insertionDepth = hzTomm(freqs[0])
    spacing = []
    lastPos = 0
    for i in range(0, np.size(freqs)):
        if (i == 0):
            dist = 0
        else:
            dist = lastPos - hzTomm(freqs[i])
        print(freqs[i], hzTomm(freqs[i]), "curr, mm")
        lastPos = hzTomm(freqs[i])
        spacing.append(dist)
    return insertionDepth, spacing
