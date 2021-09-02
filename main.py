from io import FileIO
import logging, sys, time, re
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

    if len(sys.argv) != 3:
        sys.exit("Invalid amount of args, exiting...")
    elif int(sys.argv[1]) != 1:
        sys.exit("Can't run more than one thread currently, exiting...")

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

    # main loop creating sockets for each website
    while not urlqueue.empty():
        # get url from queue, print, parse
        url = urlqueue.get()
        print("URL: {}".format(url.strip()))
        parsedurl = urlparse(url)
        
        # checking for duplicate hosts, if set length is different, not a dup
        hostslen = len(hosts)
        hosts.add(parsedurl.hostname)
        if hostslen == len(hosts):
            log.debug("Duplicate Host... skipping")
            continue

        mysocket = TCPsocket() # create an object of TCP socket
        mysocket.createSocket()

        # if no port specified, specify port 80 
        print("Doing DNS... ", end='')
        start = time.time()
        ip = mysocket.getIP(parsedurl.hostname)
        end = time.time()
        print("done in {} ms, found {} ".format((end-start)*1000, ip))
        # checking for duplicate ips, if length is different, not a dup
        ipslen = len(ips)
        ips.add(ip)
        if ipslen == len(ips):
            log.debug("Duplicate IPs... skipping")
            continue

        if not parsedurl.port:
            port  = 80
        else:
            port = parsedurl.port

        print("Connecting on page... ", end='')
        start = time.time()
        mysocket.connect(ip, port)
        end = time.time()
        print("done in {} ms ".format((end-start)*1000))

        # build our request
        headrequest = Request()
        head = headrequest.headRequest(parsedurl.hostname)
        # send out request
        mysocket.send(head)
        data = mysocket.receive() # receive a reply from the server
        print("data received: ", data)
        if not data:
            continue
        response = data.splitlines()
        mysocket.close()
        code4xx = re.compile(r'4[0-9][0-9]')
        code2xx = re.compile(r'2[0-9][0-9]')
        code3xx = re.compile(r'3[0-9][0-9]')
        # build our request
        if code4xx.search(response[0]):
            print('{}'.format(response[0]))
        elif code2xx.search(response[0]):
            print('200 request shown')
            continue
        elif code3xx.search(response[0]):
            print('300 request shown')
            continue
        else:
            print('**********Unhandled status code*********')
            continue
        
        getrequest = Request()
        get = getrequest.getRequest(parsedurl.hostname, parsedurl.path, parsedurl.query)

        mysocket.createSocket()
        mysocket.connect(ip, port)

        # send out request
        mysocket.send(get)
        data = mysocket.receive() # receive a reply from the server
        print("data received: ", data)

        mysocket.close()


# call main() method:
if __name__ == "__main__":
   main()
