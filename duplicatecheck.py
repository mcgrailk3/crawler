import logging, sys

class DuplicateCheck:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)


    def setlogging(self, level):
        self.log.setLevel(level)
        
    def unique(self, set, input):
        setlen = len(set)
        set.add(input)
        if setlen == len(set):
            self.log.debug("Duplicate... skipping")
            return False
        else: 
            self.log.debug("Not a duplicate")
            return True