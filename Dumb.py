from random import choice, uniform, sample, randrange

class Dumb():
    def __init__(self):
        self.mutationList = []
        self.targetFile = ''
        self.data = ''
        self.mData = ''
        self.minimizeIdx = 0
        self.minimizeInfo = []

    def makeMutationList_(self):
        mutation_idx_list = []
        dataLen = len(self.data)

        for i in range(randrange(100)):
            mutation_idx_list.append(randrange(dataLen))

        for idx in sorted(mutation_idx_list)[::-1]: # descending order
            self.mutationList.append([idx])
            self.mutationList[-1].append(randrange(3)) # cutting, byteMutate, adding
            #self.mutationList[-1].append(1)

            if self.mutationList[-1][1] == 0:
                self.mutationList[-1].append(randrange(2))
            elif self.mutationList[-1][1] == 1:
                #self.mutationList[-1].append(randrange(1, 5))
                self.mutationList[-1].append(1)
                self.mutationList[-1].append(''.join([chr(randrange(256)) for i in range(randrange(1, self.mutationList[-1][2] + 1))]))
            elif self.mutationList[-1][1] == 2:
                self.mutationList[-1].append(''.join([chr(randrange(256)) for i in range(randrange(2))]))

    def mutate_(self):
        self.mData = bytearray(self.data)
        for mutation in self.mutationList: # descending order
            mIdx = mutation[0]
            mType = mutation[1]
            mSize = mutation[2]

            if mType == 0: # cutting
                self.mData = self.mData[:mIdx] + self.mData[mIdx + mSize:]
            elif mType == 1: # byteMutate
                for i in range(mSize):
                    self.mData[mIdx + i] = mutation[-1][i]

                #self.mData = self.mData[:mIdx] + mutation[-1] + self.mData[mIdx + mSize:]
            elif mType == 2: # adding
                self.mData = self.mData[:mIdx] + mutation[-1] + self.mData[mIdx + 1:]

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