import winappdbg
from winappdbg import *
import os
import subprocess
import shutil
import threading
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

class CrashChecker():
    def __init__(self, program):
        self.program = program
        self.target_file = ""
        self.timer = None
        if not os.path.exists("crash"): os.makedirs("crash")
        self.crashDir = os.getcwd()+os.sep+"crash"+os.sep
        if not os.path.isfile("unique.txt") : open("unique.txt", "w").close()
        self.unique_list = open("unique.txt", "rb").read().split("\r\n")
        self.crash_count = len(self.unique_list) - 1
        self.iter_count = 0
        self.crashResult = False

    def quit_(self, proc):
        self.timer = False
        try:
            proc.kill()
        except:
            subprocess.call("taskkill /f /im %s" % self.program.split("\\")[-1] ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def handle_(self, event):
        if event.get_event_code() == win32.EXCEPTION_DEBUG_EVENT and event.is_last_chance():
            self.timer.cancel()
            self.timer = False

            crash = Crash(event)
            crash.fetch_extra_data(event, takeMemorySnapshot = 0)
            unique = crash.signature[3]
            if not self.isMinimize:
                if unique in self.unique_list:
                    print "[-] Duplicate Crash"
                    self.quit_(event.get_process())
                else:
                    self.crashResult = True
                    self.crash_count += 1
                    self.unique_list.append(unique)
                    try:
                        with open('unique.txt','w') as f:
                            f.write('\n'.join(self.unique_list))
                    except:
                        import traceback
                        print traceback.format_exc()
                        pass
                    try:
                        report = crash.fullReport()
                        prog = self.program.split("\\")[-1]

                        with open(self.crashDir+prog+'_'+datetime.now().strftime("%y-%m-%d-%H-%M-%S")+".log", "w") as f:
                            f.write(report)
                        self.resultFile = self.crashDir+prog+'_'\
                            +datetime.now().strftime("%y-%m-%d-%H-%M-%S")+'_'+self.target_file.split("\\")[-1]
                        shutil.copy(self.target_file, self.resultFile)
                    except:
                        import traceback
                        print traceback.format_exc()
                        pass
                    try:
                        event.get_process().kill()
                    except:
                        subprocess.call("taskkill /f /im %s" % self.program.split("\\")[-1])
            else: # minimize
                if unique == self.unique_list[-1]: # minimize success
                    self.crashResult = True
                    try:
                        prog = self.program.split("\\")[-1]
                        shutil.copy(self.target_file, self.resultFile + ".minimize")
                    except:
                        import traceback
                        print traceback.format_exc()
                        pass
                try:
                    event.get_process().kill()
                except:
                    subprocess.call("taskkill /f /im %s" % self.program.split("\\")[-1])
        else: # not crash
            if not self.timer:
                self.timer = threading.Timer(5, self.quit_, [event.get_process()])
                self.timer.start()

    def runCrash(self, targetFile, isMinimize):
        self.crashResult = False
        self.target_file = targetFile
        self.isMinimize = isMinimize
        dbg = Debug(self.handle_, bKillOnExit = True)
        dbg.execl('"%s" "%s"' % (self.program, self.target_file))
        dbg.loop()
        if not isMinimize:
            self.iter_count += 1
            print "iter : ", self.iter_count, "crash : ", self.crash_count
        return self.crashResult