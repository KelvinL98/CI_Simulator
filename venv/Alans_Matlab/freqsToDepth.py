import numpy as np
from hzTomm import hzTomm
#returns insertion depth and mm spacing of each electrode
def freqsToDepth(freqs):
    #get the the frequency of the deepest electrode
    print("freqs", freqs)
    insertionDepth = hzTomm(freqs[np.size(freqs) -1])
   # insertionDepth = hzTomm(freqs[0])
    spacing = []
    curr = insertionDepth
    for i in range(0, np.size(freqs)):
        dist = curr - hzTomm(freqs[i])
        spacing.append(dist)
    return insertionDepth, spacing
