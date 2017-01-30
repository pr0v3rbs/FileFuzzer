import os
import shutil
from datetime import datetime
from random import choice, uniform, sample, randrange
from CrashChecker import CrashChecker
from Dumb import Dumb
from Ole import Ole
from Xml import Xml
import warnings
warnings.filterwarnings("ignore")

class Fuzzer():
    def __init__(self):
        self.targetFile = ""
        if not os.path.exists("seed"): os.makedirs("seed")
        if not os.path.exists("tmp"): os.makedirs("tmp")
        self.seedDir = os.getcwd()+os.sep+"seed"+os.sep
        self.tmpDir = os.getcwd()+os.sep+"tmp"+os.sep
        #self.crashChecker = CrashChecker(r"C:\Program Files (x86)\Hnc\Office NEO\HOffice96\Bin\HCell.exe")
        self.crashChecker = CrashChecker(r"C:\Program Files (x86)\Hnc\Office NEO\HOffice96\Bin\Hwp.exe")
        self.fuzzMap = {}
        self.fuzzMap["hwp"] = [Dumb(), Ole()]
        self.fuzzMap["hml"] = [Xml()]
        self.fuzzMap["cell"] = [Dumb()]
        self.fuzzMap["xlsx"] = [Dumb()]

    def pick(self, seedDir):
        while not os.listdir(seedDir):
            raw_input("no seedfile found. insert seed file in 'seed' folder and press enter.")
        fname = choice(os.listdir(seedDir))
        shutil.copy(self.seedDir+fname, self.tmpDir+fname)
        return self.tmpDir+fname

    def remove(self):
        while len(os.listdir("tmp")) != 0 :
            for x in os.listdir("tmp"):
                try:
                    os.remove(r"tmp\%s" % x)
                except:
                    pass

    def start(self):
        while True:
            self.targetFile = self.pick(self.seedDir)
            fuzzer = choice(self.fuzzMap.get(self.targetFile.split('.')[-1], Dumb()))
            fuzzer.runMutation(self.targetFile)
            if self.crashChecker.runCrash(self.targetFile, False):
                print "found new crash. start minimizing"
                while not fuzzer.isMinimizeFinished():
                    fuzzer.runMinimize()
                    fuzzer.updateMinimizeCrash(self.crashChecker.runCrash(self.targetFile, True))
            self.remove()

if __name__ == '__main__' :
    Fuzzer().start()
