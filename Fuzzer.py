import os
import shutil
from datetime import datetime
from random import choice, uniform, sample, randrange
from CrashChecker import CrashChecker
from Dumb import Dumb
from Ole import Ole
import warnings
warnings.filterwarnings("ignore")

class Fuzzer():
    def __init__(self):
        self.target_file = ""
        if not os.path.exists("seed"): os.makedirs("seed")
        if not os.path.exists("tmp"): os.makedirs("tmp")
        self.seedDir = os.getcwd()+os.sep+"seed"+os.sep
        self.tmpDir = os.getcwd()+os.sep+"tmp"+os.sep
        #self.crashChecker = CrashChecker(r"C:\Program Files (x86)\Hnc\Office NEO\HOffice96\Bin\HCell.exe")
        self.crashChecker = CrashChecker(r"C:\Program Files (x86)\Hnc\Office NEO\HOffice96\Bin\Hwp.exe")
        self.fuzzList = [Ole()]

    def pick(self, seedDir):
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
            self.target_file = self.pick(self.seedDir)
            fuzzer = choice(self.fuzzList)
            fuzzer.runMutation(self.target_file)
            if self.crashChecker.runCrash(self.target_file, False):
                print "found new crash. start minimizing"
                while not fuzzer.isMinimizeFinished():
                    fuzzer.runMinimize()
                    fuzzer.updateMinimizeCrash(self.crashChecker.runCrash(self.target_file, True))
                break
            self.remove()

if __name__ == '__main__' :
    Fuzzer().start()
