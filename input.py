# Student Names: Garrett Fitzgerald, Kevin McGrail
# ID num:  1016818720, 1013412930

from re import S
from fileio import FileIO
import logging, sys

class Input:
    def __init__(self):
        self.__cmdlinemode = "single"
        self.__txtinputmode = "textfile"
        self.__filename = ""
        self.log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)

    def process(self, queue, args, mode):
        if mode is self.__cmdlinemode:
            self.singleurl(queue, args)
            return 1
        elif mode is self.__txtinputmode:
            amtthreads, sizeoffile = self.urltext(queue, args)
            return amtthreads, sizeoffile, self.__filename

    def singleurl(self, queue, args):
        if len(args) != 2:
            sys.exit("Invalid amount of args, exiting...")
        queue.put(args[1])

    def urltext(self, queue, args):
        if len(args) != 3:
            sys.exit("Invalid amount of args, exiting...")
        # open file for read only
        fileop = FileIO()
        urlfile = fileop.openro(args[2])
        self.__filename = args[2]
        numthreads = int(args[1])
        # read file line by line, put into queue
        try:
            for line in urlfile:
                queue.put(line)
            sizeoffile = fileop.getsize()
            fileop.close()
            return numthreads, sizeoffile
        except IOError:
            self.log.error("File read error")
            sys.exit("File read error, exiting...")
