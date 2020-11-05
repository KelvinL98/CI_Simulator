# function pos = hz2mm(cf,k)
#
# This function relates frequency to position on basilar membrane based on
#   data given in Greenwood (1990).
#
# Input parameter:
#   cf is the frequency corresponding to pos.
#
# Output parameter:
#   pos is the position relative to the length of the basilar membrane in mm.
#
# Optional parameter:
#   k is an integration constant. Typical values are between 0.8-0.9. [0.88]
#
# Reference: Greenwood D. "A cochlear frequency-position for several
#   species - 29 years later", J. Acoust. Soc Am. 1990(87) pp2592-2605.
#
import numpy as np

def hzTomm(cf, k = 0.88):

    bmLength = 35
    a = 2.1
    A = 165.4
    cfA = np.divide(cf,A)
    cfAk = np.add(cfA, k)
  #  bmLengthA = np.divide(bmLength, A)
    bmLengthA = bmLength / A
  #  pos = np.log10(np.multiply(cfAk, bmLengthA))
    pos = np.log10((cf/A) + k) * bmLength/a

    return pos



