class Strategy(object):
    lmap = None
    rmap = None
    framesize = None
    fs = None


    def __init__(self, lmap, rmap, framesize, fs):
        self.lmap = lmap
        self.rmap = rmap
        self.framesize = framesize
        self.fs = fs

    def process(self, in_l, in_r):
        return [in_l,in_r]

