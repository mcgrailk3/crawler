# Student Names: Garrett Fitzgerald, Kevin McGrail
# ID num:  1016818720, 1013412930

# resources: https://docs.python.org/3/howto/sockets.html

import socket, select, logging

TIMEOUT = 5 # unit is seconds
BUF_SIZE = 1024 # unit is bytes

class TCPsocket:
    # list our instance variables
    # Constructor: create an object
    def __init__(self):
        self.sock = None  # each object's instance variables
        self.host = ""  # remote host name
        self.log = logging.getLogger(__name__)
        
        # logging.basicConfig(level=logging.DEBUG)
        #self.log.debug("create an object of TCPsocket")

    def setlogging(self, level):
        self.log.setLevel(level)

    def createSocket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # self.sock is an instance variable
            self.sock.settimeout(TIMEOUT)
            self.log.debug("created a tcp socket!")
        except socket.error as e:
            self.log.error("Failed to create a TCP socket {}".format(e))
            self.sock = None

    # www.google.com -> host name
    # given a host name, how to get its ip address
    # Return the ip of input hostname. Both ip and hostname in string
    def getIP(self, hostname):
        self.log.debug("Getting IP....")
        self.host = hostname
        if len(hostname) > 64:
            return None
        try:
            ip = socket.gethostbyname(hostname)   # ip is a local variable to getIP(hostname), ip is of string type
        except socket.gaierror:
            self.log.error("Failed to gethostbyname")
            return None
        return ip


    # connect to a remote server: IP address, port
    def connect(self, ip, port):
        self.log.debug("Connecting....")
        if self.sock is None or ip is None:
            self.sock = None
            return
        try:
            self.sock.connect((ip, port))   # server address is defined by (ip, port)
            self.log.debug("Successfully connect to host: {}".format(ip))
        except socket.error as e:
            self.log.error("Failed to connect: {}".format(e))
            self.sock.close()
            self.sock = None
            return -1

    # return the number of bytes sent
    def send(self, request):
        self.log.debug("Sending....")
        bytesSent = 0       # bytesSent is a local variable
        if self.sock is None:
            return 0
        try:
            bytesSent = self.sock.sendall(request.encode())   # encode(): convert string to bytes
        except socket.error as e:
            self.log.error("socket error in send: {}".format(e))
            self.sock.close()
            self.sock = None
        return bytesSent

    # Receive the reply from the server. Return the reply as string
    def receive(self):
        self.log.debug("Receiving....")
        if self.sock is None:
            return ""
        reply = bytearray()    # b'', local variable, bytearray is mutable
        bytesRecd = 0   # local integer
        self.sock.settimeout(TIMEOUT)
        """
        self.sock.setblocking(1)    # flag 0 to set non-blocking mode of the socket
        ready = select.select([self.sock], [], [], TIMEOUT) # https://docs.python.org/3/library/select.html
        if ready[0] == []:     # timeout
            self.log.debug("Time out on", self.host)
            return ""
        # else reader has data to read
        """
        try:
            while bytesRecd < 96000000:         # use a loop to receive data until we receive all data, up to 96 MB
                data = self.sock.recv(BUF_SIZE)  # returned chunk of data with max length BUF_SIZE. data is in bytes
                if data == b'':  # if empty bytes
                   break
                else:
                   reply += data  # append to reply
                   bytesRecd += len(data)
        except socket.error as e:
            self.log.error("socket error in receive: {}".format(e))
            self.sock.close()
            self.sock = None
        return reply.decode('utf-8', 'ignore'), bytesRecd

    def receivehead(self):
            self.log.debug("Receiving....")
            if self.sock is None:
                return ""
            reply = bytearray()    # b'', local variable, bytearray is mutable
            bytesRecd = 0   # local integer
            self.sock.settimeout(TIMEOUT)
            """
            self.sock.setblocking(1)    # flag 0 to set non-blocking mode of the socket
            ready = select.select([self.sock], [], [], TIMEOUT) # https://docs.python.org/3/library/select.html
            if ready[0] == []:     # timeout
                self.log.debug("Time out on", self.host)
                return ""
            # else reader has data to read
            """
            try:
                data = self.sock.recv(BUF_SIZE)  # returned chunk of data with max length BUF_SIZE. data is in bytes
                #print(f"Receiving..... {data}")
                reply += data  # append to reply
                bytesRecd += len(data)
            except socket.error as e:
                self.log.error("socket error in receive: {}".format(e))
                #self.sock.close()
                #self.sock = None
            return reply.decode('utf-8', 'ignore'), bytesRecd

    # Close socket
    def close(self):
        if not (self.sock is None):
            self.sock.close()