import logging, sys, os

class FileIO:
    def __init__(self):
        self.filename = ''    # a string
        self.__size = 0
        self.__file = None
        self.log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)

    # open read only
    def openro(self, file):
        self.filename = file
        try:
            urlfile = open(self.filename, 'r')
        except FileNotFoundError:
            self.log.error("File Not Found")
            sys.exit("File not found, exiting...")
        self.__file = urlfile
        return urlfile  

    # open write only
    def openwo(self, file):
        self.filename = file
        try:
            urlfile = open(self.filename, 'w')
        except FileNotFoundError:
            self.log.error("File Not Found")
            sys.exit("File not found, exiting...")
        self.__file = urlfile
        return urlfile

    # open read write
    def openrw(self, file):
        self.filename = file
        try:
            urlfile = open(self.filename, 'w+')
        except FileNotFoundError:
            self.log.error("File Not Found")
            sys.exit("File not found, exiting...")
        self.__file = urlfile
        return urlfile

    # close
    def close(self):
        try:
            self.__file.close()
        except IOError as e:
            self.log.error("FileIO Error {}".format(e))
            sys.exit("FileIO Error, exiting...")

    def getsize(self):
        try:
            self.__file.seek(0, os.SEEK_END)
            self.__size = self.__file.tell()
            return self.__size
        except IOError as e:
            self.log.error("FileIO Error {}".format(e))
            sys.exit("FileIO Error, exiting...")