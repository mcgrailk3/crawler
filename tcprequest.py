# Student Names: Garrett Fitzgerald, Kevin McGrail
# ID num:  1016818720, 1013412930

class Request:
    def __init__(self):
        self.request = ''    # a string

    def getRequest(self, host, path, query):
        """Build an HTTP GET request """
        self.request = 'GET ' + path + query + ' HTTP/1.0' +  '\nHost: ' + host + '\nConnection: close\n\n'
        #print(f"Request: {self.request}")
        return self.request

    def headRequest(self, host):
        """Build a HEAD request, to check if host has "robots.txt" file """
        self.request = 'HEAD /robots.txt HTTP/1.0\n' + 'Host: ' + host + '\n\n'
        #print(f"Request: {self.request}")
        return self.request

    def getRequest11(self, host, path, query):
        """Build an HTTP GET request """
        self.request = 'GET ' + path + query + ' HTTP/1.1' +  '\r\nHost: ' + host + '\r\nConnection: close\r\n\r\n'
        #print(f"Request: {self.request}")
        return self.request

    def headRequest11(self, host):
        """Build a HEAD request, to check if host has "robots.txt" file """
        self.request = 'HEAD /robots.txt HTTP/1.1\r\n' + 'Host: ' + host + '\r\nConnection: keep-alive\r\n\r\n'
        #print(f"Request: {self.request}")
        return self.request