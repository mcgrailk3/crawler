import logging, sys

class FileIO:
    def __init__(self):
        self.filename = ''    # a string
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
        return urlfile  

    # open write only
    def openwo(self, file):
        self.filename = file
        try:
            urlfile = open(self.filename, 'w')
        except FileNotFoundError:
            self.log.error("File Not Found")
            sys.exit("File not found, exiting...")
        return urlfile

    # open read write
    def openrw(self, file):
        self.filename = file
        try:
            urlfile = open(self.filename, 'w+')
        except FileNotFoundError:
            self.log.error("File Not Found")
            sys.exit("File not found, exiting...")
        return urlfile

    # close
    def close(self, file):
        try:
            file.close()
        except IOError as e:
            self.log.error("FileIO Error {}".format(e))
            sys.exit("FileIO Error, exiting...")
