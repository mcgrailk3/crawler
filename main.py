# Student Names: Garrett Fitzgerald, Kevin McGrail
# ID num:  1016818720, 1013412930

import logging, sys, time, re
from printthread import PrintThread
import threading
from urlparser import URLParser

from fileio import FileIO
from tcpsocket import TCPsocket
from tcprequest import Request
from queue import Queue
from urllib.parse import urlparse
from input import Input
from duplicatecheck import DuplicateCheck
from sharedparameters import SharedParameters
from crawlthread import CrawlThread
from printthread import PrintThread

def main(): # function, method are the same
    startMainTime = time.time()
    # loglevel setup info allows most, debug for general debug messages, critical to supress errors
    # loglevel = "INFO"
    # loglevel = "DEBUG"
    loglevel = "CRITICAL"
    cmdlinemode = "single"
    txtinputmode = "textfile"

    # set mode, either cmd line input or txt file, for part 1 we want cmdlinemode, for all others, we want txtinputmode
    # mode = cmdlinemode
    mode = txtinputmode
    # set default number of threads to 1
    numthreads = 1
    log = logging.getLogger(__name__)
    log.setLevel(loglevel)

    urlqueue = Queue()
    threads = []

    shared = SharedParameters()
    shared.lock = threading.Lock()
    shared.hostTable = set()
    shared.ipTable = set()
    shared.Q = urlqueue
    qsize = urlqueue.qsize()

    inpobj = Input(shared, sys.argv, mode)
    inpobj.process()
    dup = DuplicateCheck()
    dup.setlogging(loglevel)
    
    inpobj.start()

    print(f"Opened {inpobj.filename} with size {inpobj.sizeoffile} bytes")
    print(f"{shared.amtthreads} threads starting...")


    start = time.time()
    
    for i in range(0, shared.amtthreads, 1):
        t = CrawlThread(i, "crawler", shared, loglevel)
        t.start()
        threads.append(t)
    p = PrintThread(0, threads, shared, qsize, loglevel)
    p.start()
    for t in threads:
        t.join()
    

    end = time.time()
    totaltime = end - start
    """
    print(f"Extracted {} URLs @ {}/s")
    print(f"Looked up {} DNS names @ {}/s")
    print(f"Downloaded {} robots @ {}/s")
    print(f"Crawled {} pages @ {}/s")
    print(f"Parsed {} links @ {}/s")
    print(f"HTTP codes: 2xx = , 3xx = , 4xx = , 5xx = , other = ")
    """
    """

    # main loop creating sockets for each website
    while not urlqueue.empty():
        # get url from queue, print, parse
        url = urlqueue.get()

        print(f"URL: {url.strip()}")
        urlparseobj = URLParser()
        hostname, port, path, query, pathquery, scheme = urlparseobj.parse(url)

        #print(f"\tParsing URL... host {hostname}, port {port}, request {pathquery}")
        print(f"\tParsing URL... host {hostname}, port {port}")
    
        # checking for duplicate hosts, if set length is different, not a dup
        print(f"\t\033[1mChecking host uniqueness... ", end='')
        hostunique = dup.unique(hosts, hostname)
        if not hostunique:
            print(f"failed\033[0m")
            continue
        print(f"passed\033[0m")

        mysocket = TCPsocket() # create an object of TCP socket
        mysocket.setlogging(loglevel)
        mysocket.createSocket()

        print("\tDoing DNS... ", end='')
        # start measuring time, set start to current time
        start = time.time()
        # get the ip of hostname, dns lookup
        ip = mysocket.getIP(hostname)
        # get the end time, set end to current time
        end = time.time()
        # print how long it took, end - start time * 1000 to get in milliseconds
        print(f"done in {int((end-start)*1000)} ms, found {ip} ")
        if ip is None:
            continue
        # checking for duplicate ips, if length is different, not a dup
        print(f"\t\033[1mChecking IP uniqueness... ", end='')
        ipunique = dup.unique(ips, ip)
        if not ipunique:
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
        head = headrequest.headRequest(hostname)
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
        get = getrequest.getRequest(hostname, path, query)


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
    """

# call main() method:
if __name__ == "__main__":
   main()
