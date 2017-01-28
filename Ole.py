import OleFileIO_PL as OLE
from random import choice, uniform, sample, randrange

class Ole():
    def __init__(self):
        self.mutationList = []
        self.targetFile = ''
        self.data = ''
        self.mData = ''
        self.minimizeIdx = 0
        self.minimizeInfo = []

    def makeMutationList_(self):
        fuzz_offset = []
        fuzzing_list = []
        mutate_position = []
        ole = OLE.OleFileIO(self.targetFile)
        ole_list = ole.listdir()
        for entry in ole_list:
            if "BodyText" in entry:
                sections = entry[1:]
                for sec in  sections:
                    stream = entry[0]+"/"+sec
                    size = ole.get_size(stream)
                    fuzzing_list.append( (ole.openstream(stream).read(16), size) )
            if "BinData" in entry:
                sections = entry[1:]
                for sec in  sections:
                    stream = entry[0]+"/"+sec
                    size = ole.get_size(stream)
                    fuzzing_list.append( (ole.openstream(stream).read(16), size) )

        ole.close()
        for magic, size in fuzzing_list:
            if self.data.find(magic) != -1:
                offset = self.data.find(magic)
                mutate_position.append((offset, size))  
        for offset, size in mutate_position:
            fuzz_offset += sample(xrange(offset, offset+size), int(size*uniform(0.001, 0.003))) # 0.1% ~ 0.3%
        for index in fuzz_offset:
            self.mutationList.append([index])
            self.mutationList[-1].append(chr(randrange(256)))

    def mutate_(self):
        self.mData = bytearray(self.data)
        for mutation in self.mutationList:
            self.mData[mutation[0]] = mutation[-1]

    def runMutation(self, targetFile):
        self.targetFile = targetFile
        self.data = open(self.targetFile, 'rb').read()
        self.mutationList = []
        self.minimizeIdx = 0
        self.minimizeInfo = []
        self.makeMutationList_()
        self.mutate_()
        open(self.targetFile, 'wb').write(self.mData)

    def isMinimizeFinished(self):
        if self.minimizeIdx == len(self.mutationList):
            return True
        return False

    def runMinimize(self):
        self.minimizeInfo = self.mutationList[self.minimizeIdx]
        del self.mutationList[self.minimizeIdx]
        self.mutate_()
        open(self.targetFile, 'wb').write(self.mData)

    def updateMinimizeCrash(self, result):
        if result == False:
            self.mutationList.insert(self.minimizeIdx, self.minimizeInfo)
            self.minimizeIdx += 1