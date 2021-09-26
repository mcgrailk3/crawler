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

    print(f"Extracted {shared.extracted} URLs @ {int(shared.extracted/inpobj.totaltime):d}/s")
    print(f"Looked up {shared.dnslookup} DNS names @ {int(shared.dnslookup/totaltime):d}/s")
    print(f"Downloaded {shared.robots} robots @ {int(shared.robots/totaltime):d}/s")
    print(f"Crawled {shared.crawled} pages @ {int(shared.crawled/totaltime):d}/s")
    print(f"Parsed {shared.links} links @ {int(shared.links/totaltime):d}/s")
    print(f"HTTP codes: 2xx = {shared.responses[0]}, 3xx = {shared.responses[1]}, 4xx = {shared.responses[2]}, 5xx = {shared.responses[3]}, other = {shared.responses[4]}")
    
    
# call main() method:
if __name__ == "__main__":
   main()
