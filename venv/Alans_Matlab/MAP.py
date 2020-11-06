import constant
import re
import csv
import scipy
import numpy as np
import math

class MAP(object):
    #properties
    Filename = None
    SubjectID = None
    ImplantType = None
    Side = None
    NMaxima = None
    StimulationMode = None
    PhaseWidth = None
    IPG = None
    Q = None
    TSPL = None
    CSPL = None

    #electrode properties (vectors)
    Active = None
    EL = None
    F_Low = None
    F_High = None
    THR = None
    MCL = None
    Gain = None
    PulseRate = None

    #predefined values
    BaseLevel = 0.0156
    SaturationLevel = 0.5859

    #derived properties
    AnalysisRate = None
    Shift = None
    GainScale = None
    Range = None
    NumberOfBands = None
    NMaximaReject = None
    ImplantGeneration = None
    StimulationModeCode = None
    ChannelOrder = None
    LGF_alpha = None

    def __init__(self, side = None, file = None, sampleRate = None):
        hardcode(self)
        if sampleRate == None:
            raise Exception("Specify sampleRate")

        return
        if side == None:
            raise Exception("Specify side, 'left' or 'right'")
        if file == None:
            raise Exception("Specify file location")

    def load(self, side, file):
        f = open(file, "r")
        headerlines = 0

        for x in f:
            line = f.readline()
            line = re.split(':', line)
            headerlines = headerlines + 1

            if line[0] == 'Filename' or 'SubjectID' or 'ImplantType' or 'Side' or 'Strategy' or 'StimulationMode':
                self.line[0] = strip(line[1])
            if line[0] == 'NMaxima' or 'PhaseWidth' or 'IPG' or 'Q' or 'TSPL' or 'CSPL':
                self.line[0] = float(line[1])
        if self.Side != side:
            raise Exception("specified map does not correspond to the correct side")
        #read CSV portion of map, discard header lines
        f.close()
        f = open(f)
        for i in range(0,headerlines):
            next(f)

        csv_reader = csv.Dictreader(f)
        headers = csv_reader.next()

        for row in csv_reader:
            rows.append(row)

def LGF_proc(p, u):

#        r = (np.subtract(u, p.base_level))/(p.sat_level - p.base_level)
#       sat = 0
#      if r > 1:
#          sat = 1
#         r = 1
##      if r < 0:
#          sub = p.sub_mag
#         r = 0

#      v = np.log(1 + p.lgf_alpha * r) / np.log(1 + p.lgf_alpha)
#      return [v,sub, sat]

    r = (np.subtract(u, p.base_level)) / (p.sat_level - p.base_level)
    sat = r > 1

    sat.astype(np.int)
    if sat:
        r = 1

    sub = r < 0
    sub.astype(np.int)
    if sub:
        r = 0;

    v = np.log(1 + p.lgf_alpha * r) / np.log(1 + p.lgf_alpha);

    if sub:
        v = sub_mag

    return [v, sub, sat]

def LGF_Q_diff(log_alpha, Q, BaseLevel, SaturationLevel):

    if type(log_alpha) is int:
        alpha = np.exp(np.float(log_alpha))
    else:
        alpha = np.exp(np.float(log_alpha[0]))
    return (np.subtract(LGF_Q(alpha, BaseLevel, SaturationLevel), Q))



def LGF_Q(alpha, base_level, sat_level):
    p = type('params', (object,), {'lgf_alpha': alpha, 'base_level': base_level, 'sat_level':sat_level, 'sub_mag': 0},)
    p.lgf_alpha = alpha
    p.base_level = base_level
    p.sat_level = sat_level
    p.sub_mag = 0
    input_level = sat_level/(np.sqrt(10))
    p = LGF_proc(p, input_level)
    q = np.multiply(100,(np.subtract(1,p)))

    return q

def calc_LGF_alpha(Q, BaseLevel, SaturationLevel):
    log_alpha = 0
    while True:
        log_alpha = log_alpha + 1
        Q_diff = LGF_Q_diff(log_alpha,Q,BaseLevel,SaturationLevel)

        if Q_diff[0] < 0:
            break
            #third interval value 0 is a bogus value to align input/output sizes. may effect result
    interval =  np.array([(log_alpha - 1), log_alpha, 0])
#    opt.Display = 'off';
#    opt.TolX = [];
#    log_alpha = fzero('LGF_Q_diff', interval, opt, Q, BaseLevel, SaturationLevel);
    log_alpha = scipy.optimize.fsolve(LGF_Q_diff, interval, xtol = 0, args = (Q, BaseLevel, SaturationLevel))

    alpha = np.exp(log_alpha)
    return alpha




def hardcode(self):
    #hardcode in "CI1_ACE_LEFT.txt"
    self.Filename = "CI1_ACE_left.txt"
    self.SubjectID = "CI1"
    self.ImplantType = "CI24RE"
    self.Side = "Left"
    self.NMaxima = 8.0
    self.StimulationMode = "MP1+2"
    self.PhaseWidth = 25.0
    self.IPG = 8.0
    self.Q = 20.0
    self.TSPL = 25.0
    self.CSPL = 65.0
    self.EL = [22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1]
    self.EL = np.array(self.EL)
    self.F_Low = [188,313,438,563,688,813,938,1063,1188,1313,1563,
                  1813,2063,2313,2688,3063,3563,4063,4688,5313,6063,6938]
    self.F_low = np.array(self.F_Low)
    self.F_High = [313,438,563,688,813,938,1063,1188,1313,1563,1813,2063,
                   2313,2688,3063,3563,4063,4688,5313,6063,6938,7938]
    self.THR = np.full((22,1), 100)
    self.MCL = [250,200,200,200,200,200,200,200,200,200,200,200,200,200,200,
                200,200,200,200,200,200,200]
    self.MCL = np.array(self.MCL)
    self.Gain = np.full((22,1),0.0)
    self.PulseRate = np.full((22,1),900)
    self.Active = np.full((22,1), True)
    #derive paramaters
    self.GainScale = np.power(10, (self.Gain/20))
    self.Range = np.subtract(self.MCL,self.THR)
    self.NumberOfBands = 22
    self.NMaximaReject = self.NumberOfBands - self.NMaxima
    self.ImplantGeneration = "CIC4"
    self.StimulationModeCode = 28
    #base to apex
    chanOrder = range(self.NumberOfBands - 1, -1, -1)
    chanOrder = np.vstack(chanOrder)
    self.ChannelOrder = chanOrder
    self.Shift = np.ceil(16000/900)
    self.AnalysisRate = np.round(16000/self.Shift)
    self.LGF_alpha = calc_LGF_alpha(self.Q, self.BaseLevel, self.SaturationLevel)










