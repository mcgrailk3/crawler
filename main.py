from io import FileIO
import logging, sys
from urllib import parse

from fileio import FileIO
from tcpsocket import TCPsocket
from tcprequest import Request
from queue import Queue
from urllib.parse import urlparse

def main(): # function, method are the same
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    urlqueue = Queue()

    if len(sys.argv) != 2:
        sys.exit("Invalid amount of args, exiting...")
    """
    elif int(sys.argv[1]) != 1:
        sys.exit("Can't run more than one thread currently, exiting...")
    """
    """
    # open file for read only
    fileop = FileIO()
    urlfile = fileop.openro(sys.argv[2])

    # read file line by line, put into queue
    try:
        for line in urlfile:
            urlqueue.put(line)
    except IOError:
        log.error("File read error")
        sys.exit("File read error, exiting...")
    
    hosts = set()
    ips = set()
    """
    urlqueue.put(sys.argv[1])
    # main loop creating sockets for each website
    while not urlqueue.empty():
        # get url from queue, print, parse
        url = urlqueue.get()
        print("URL: {}".format(url.strip()))
        parsedurl = urlparse(url)
        print(parsedurl)

        """
        # checking for duplicate hosts, if set length is different, not a dup
        hostslen = len(hosts)
        hosts.add(parsedurl.netloc)
        if hostslen == len(hosts):
            log.debug("Duplicate Host... skipping")
            continue
        """
        mysocket = TCPsocket() # create an object of TCP socket
        mysocket.createSocket()

        # if no port specified, specify port 80 
        ip = mysocket.getIP(parsedurl.netloc)

        """
        # checking for duplicate ips, if length is different, not a dup
        ipslen = len(ips)
        ips.add(ip)
        if ipslen == len(ips):
            log.debug("Duplicate IPs... skipping")
            continue
        """

        if not parsedurl.port:
            port  = 80
        else:
            port = parsedurl.port

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
