# Student Names: Garrett Fitzgerald, Kevin McGrail
# ID num:  1016818720, 1013412930

import logging, sys, time, re
from urllib import parse

from fileio import FileIO
from tcpsocket import TCPsocket
from tcprequest import Request
from queue import Queue
from urllib.parse import urlparse


def main(): # function, method are the same
    # loglevel setup
    loglevel = "INFO"
    # loglevel = "DEBUG"

    cmdlinemode = "single"
    txtinputmode = "textfile"

    # set mode, either cmd line input or txt file, for part 1 we want cmdlinemode, for all others, we want txtinputmode
    mode = cmdlinemode
    # mode = txtinputmode
    # set default number of threads to 1
    numthreads = 1
    log = logging.getLogger(__name__)
    log.setLevel(loglevel)

    urlqueue = Queue()
    if mode is txtinputmode:                        # text input mode, check for thread number and file to parse
        if len(sys.argv) != 3:
            sys.exit("Invalid amount of args, exiting...")
        elif int(sys.argv[1]) != 1:
            sys.exit("Can't run more than one thread currently, exiting...")

        # open file for read only
        fileop = FileIO()
        urlfile = fileop.openro(sys.argv[2])
        numthreads = sys.argv[1]
        # read file line by line, put into queue
        try:
            for line in urlfile:
                urlqueue.put(line)
        except IOError:
            log.error("File read error")
            sys.exit("File read error, exiting...")
    elif mode is cmdlinemode:                       # command line mode, check for 1 url
        if len(sys.argv) != 2:
            sys.exit("Invalid amount of args, exiting...")
        urlqueue.put(sys.argv[1])

    hosts = set()
    ips = set()

    # main loop creating sockets for each website
    while not urlqueue.empty():
        # get url from queue, print, parse
        url = urlqueue.get()

        print(f"URL: {url.strip()}")

        # check if scheme is in url, if not add // for urlparsing 
        if not re.match('(?:http|ftp|https)://', url):
            url = "//" + url
        
        parsedurl = urlparse(url)

        # if no port present, make port default 80
        if not parsedurl.port:
            port  = 80
        else:
            port = parsedurl.port
        pathquery = ""
        if parsedurl.path:
            pathquery = parsedurl.path
        else:
            pathquery = "/"
        if parsedurl.query:
            pathquery = pathquery + "?"+parsedurl.query

        #print(f"\tParsing URL... host {parsedurl.hostname}, port {port}, request {pathquery}")
        print(f"\tParsing URL... host {parsedurl.hostname}, port {port}")
    
        # checking for duplicate hosts, if set length is different, not a dup
        print(f"\t\033[1mChecking host uniqueness... ", end='')
        hostslen = len(hosts)
        hosts.add(parsedurl.hostname)
        if hostslen == len(hosts):
            print(f"failed\033[0m")
            log.debug("Duplicate Host... skipping")
            continue
        print(f"passed\033[0m")
        mysocket = TCPsocket() # create an object of TCP socket
        mysocket.setlogging(loglevel)
        mysocket.createSocket()

        print("\tDoing DNS... ", end='')
        # start measuring time, set start to current time
        start = time.time()
        # get the ip of hostname, dns lookup
        ip = mysocket.getIP(parsedurl.hostname)
        # get the end time, set end to current time
        end = time.time()
        # print how long it took, end - start time * 1000 to get in milliseconds
        print(f"done in {int((end-start)*1000)} ms, found {ip} ")
        if ip is None:
            continue
        # checking for duplicate ips, if length is different, not a dup
        print(f"\t\033[1mChecking IP uniqueness... ", end='')
        ipslen = len(ips)
        ips.add(ip)
        if ipslen == len(ips):
            log.debug("Duplicate IPs... skipping")
            print(f"failed\033[0m")
            continue
        print(f"passed\033[0m")


        print(f"\t\033[1mConnecting on robots... ", end='')
        start = time.time()
        
        if mysocket.connect(ip, port) == -1:
            print("failed\033[0m")
            continue
        end = time.time()
        print(f"done in {int((end-start)*1000)} ms \033[0m")

        # build our request
        headrequest = Request()
        head = headrequest.headRequest(parsedurl.hostname)
        # send out request
        print("\t\033[1mLoading... ", end='')
        start = time.time()
        mysocket.send(head)
        data, amtbytes = mysocket.receive() # receive a reply from the server
        end = time.time()
        print(f"done in {int((end-start)*1000)} ms with {amtbytes} bytes\033[0m")
        if not data:
            continue
        # split data into lines to parse through
        response = data.splitlines()
        # split first line to get status code, easier than using regexs
        responsecode = response[0].split(" ")
        print(f"\t\033[1mVerifying header... status code {responsecode[1]}\033[0m")
        #print("\n---------------------------------------")
        #print(data.strip())
        
        mysocket.close()

        # if response is 200, then break out of loop, else keep going to build get request
        if responsecode[1] == "200":
           continue
        
        mysocket.createSocket()

        print(f"      * Connecting on page... ", end='')
        start = time.time()
        
        if mysocket.connect(ip, port) == -1:
            print("failed")
            continue
        end = time.time()
        print(f"done in {int((end-start)*1000)} ms ")

        # build our request
        getrequest = Request()
        get = getrequest.getRequest(parsedurl.hostname, parsedurl.path, parsedurl.query)


        print("\tLoading... ", end='')
        start = time.time()
        mysocket.send(get)
        data, amtbytes = mysocket.receive() # receive a reply from the server
        end = time.time()
        print(f"done in {int((end-start)*1000)} ms with {amtbytes} bytes")
        if not data:
            continue
        # split data into lines to parse through
        response = data.splitlines()
        # split first line to get status code, easier than using regexs
        responsecode = response[0].split(" ")
        print(f"\tVerifying header... status code {responsecode[1]}")
        print("      + Parsing page... ", end='')
        start = time.time()
        links = data.count('href')
        end = time.time()
        print(f"done in {int((end-start)*1000)} ms with {links} links")
        mysocket.close()


# call main() method:
if __name__ == "__main__":
   main()
