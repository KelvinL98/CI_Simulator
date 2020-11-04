from cfFromCSV import cfFromCSV
from mm2hz import mm2hz
import numpy as np



def freqsFromCSV(file, initialDepth):
    # use cfFromCSV to read in spacings.
    cf = cfFromCSV(file)
    freqs = [0] * 22
    depth = initialDepth
    for i in range(0, len(freqs)):
        depth += np.double(cf[i])
        freqs[i] = mm2hz(depth)
    #cf file is in descending order, flip to match channel order.
    return freqs[::-1]


