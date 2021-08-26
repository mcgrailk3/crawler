import logging, sys
from tcpsocket import TCPsocket
from tcprequest import Request
from queue import Queue
from urllib.parse import urlparse

def main(): # function, method are the same
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    urlqueue = Queue()

    if len(sys.argv) != 3:
        sys.exit("Invalid amount of args, exiting...")
    elif int(sys.argv[1]) != 1:
        sys.exit("Can't run more than one thread currently, exiting...")

    try:
        urlfile = open(sys.argv[2], 'r')
    except FileNotFoundError:
        log.error("File Not Found")
        sys.exit("File not found, exiting...")
    try:
        for line in urlfile:
            urlqueue.put(line)
    except IOError:
        log.error("File read error")
        sys.exit("File read error, exiting...")


    
    while not urlqueue.empty():
        mysocket = TCPsocket() # create an object of TCP socket
        mysocket.createSocket()
        url = urlqueue.get()
        print("URL: {}".format(url))
        parsedurl = urlparse(url)
        ip = mysocket.getIP(parsedurl.netloc)
        port  = 80
        mysocket.connect(ip, port)

        # build our request
        myrequest = Request()
        msg = myrequest.getRequest(parsedurl.netloc, parsedurl.path, parsedurl.query)

        # send out request
        mysocket.send(msg)
        data = mysocket.receive() # receive a reply from the server
        print("data received: ", data)

        mysocket.close()

# call main() method:
if __name__ == "__main__":
   main()
