import logging, re
from sys import path
from urllib.parse import urlparse

class URLParser:
    def __init__(self):
        self.input = ''    # a string
        self.url = ''
        self.scheme = ''
        self.hostname = ''
        self.path = ''
        self.query = ''
        self.pathquery = ''
        self.port = 0
        self.log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)


    def parse(self, input):
        self.input = input
        # check if scheme is in url, if not add // for urlparsing 
        if not re.match('(?:http|ftp|https)://', self.input):
            self.input = "//" + self.input
        
        parsedurl = urlparse(self.input)
        
        # if no port present, make port default 80
        if not parsedurl.port:
            self.port  = 80
        else:
            self.port = parsedurl.port
        pathquery = ""
        if parsedurl.path:
            pathquery = parsedurl.path
        else:
            pathquery = "/"
        if parsedurl.query:
            pathquery = pathquery + "?"+parsedurl.query
        
        self.scheme = parsedurl.scheme
        self.pathquery = pathquery
        self.path = parsedurl.path
        self.query = parsedurl.query
        self.hostname = parsedurl.hostname
        return self.hostname, self.port, self.path, self.query, self.pathquery, self.scheme