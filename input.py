# Student Names: Garrett Fitzgerald, Kevin McGrail
# ID num:  1016818720, 1013412930

from fileio import FileIO
import logging, sys, threading, time

class Input (threading.Thread):
    def __init__(self, shared, args, mode):
        threading.Thread.__init__(self)
        self.__cmdlinemode = "single"
        self.__txtinputmode = "textfile"
        self.totaltime = 0
        self.filename = ""
        self.numthreads = 0
        self.sizeoffile = 0
        self.mode = mode
        self.shared = shared
        self.args = args
        self.fileop = FileIO()
        self.urlfile = None
        self.totaltime = None
        self.log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)

    def process(self):
        if self.mode is self.__cmdlinemode:
            self.singleurl()
        elif self.mode is self.__txtinputmode:
            self.urltext()
        return

    def singleurl(self):
        if len(self.args) != 2:
            sys.exit("Invalid amount of args, exiting...")
        self.shared.Q.put(self.args[1])
        return

    def urltext(self):
        if len(self.args) != 3:
            sys.exit("Invalid amount of args, exiting...")
        # open file for read only
        self.filename = self.args[2]
        
        self.urlfile = self.fileop.openro(self.filename)
        self.sizeoffile = self.fileop.getsize()
        self.shared.amtthreads = int(self.args[1])
        # read file line by line, put into queue
        return

    def run(self):
        start = time.time()
        try:
            for line in self.urlfile:
                self.shared.Q.put(line)
                self.shared.lock.acquire()
                self.shared.extracted += 1
                self.shared.lock.release()
            self.fileop.close()
        except IOError:
            self.log.error("File read error")
            sys.exit("File read error, exiting...")
        end = time.time()
        self.totaltime = end - start
        if self.totaltime < 1:
            self.totaltime = 1
        return

