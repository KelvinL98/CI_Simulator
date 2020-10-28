# function cf = mm2hz(pos,k)
#
#This function relates position on basilar membrane to freqency based on
#   data given in Greenwood (1990).
#
# Input parameter:
#   pos is the position along the basilar membrane in mm where 0 is at the
#   base and 35 is at the apex
#
# Output parameter:
#   cf is the frequency corresponding to pos.
#
# Optional parameter:
#   k is an integration constant. Typical values are between 0.8-0.9. [0.88]
#
# Reference: Greenwood D. "A cochlear frequency-position for several
#   species - 29 years later", J. Acoust. Soc Am. 1990(87) pp2592-2605.
#
#
import numpy as np

def mm2hz(pos,k = 0.88):
    #i dont check if k and 'var' exist like matlab does, not sur ehow important that is?
    #instead i just set default value of k to 0.88, a low limit freq of 20Hz

    bmLength = 35

    a = 2.1
    A = 165.4
    cf = A*(np.power(10, (np.divide(np.multiply(a,pos)),bmLength))- k)
    return cf

