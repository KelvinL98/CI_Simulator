from cfFromCSV import cfFromCSV
from mm2hz import mm2hz
import numpy as np



def freqsFromSpacing(spacing, initialDepth):

    depth = initialDepth
    freqs=[]
    for i in range(0, len(spacing)):
        depth += np.double(spacing[i])
        freqs.append(mm2hz(depth))
    #cf file is in descending order, flip to match channel order.
    return freqs


