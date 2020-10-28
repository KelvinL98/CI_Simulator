from cfFromCSV import cfFromCSV
from mm2hz import mm2hz
import numpy as np



def freqsFromCSV(file, initialDepth):
    cf = cfFromCSV(file)
    freqs = [0] * 22
    depth = initialDepth
    for i in range(0, len(freqs)):
        depth += np.double(cf[i])
        freqs[i] = mm2hz(depth)
    return freqs


