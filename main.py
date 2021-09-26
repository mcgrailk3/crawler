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
from sharedstats import SharedStats
from crawlthread import CrawlThread
from printthread import PrintThread
from crawlthread_mp import CrawlThread_mp

def main(): # function, method are the same
    startMainTime = time.time()
    # loglevel setup info allows most, debug for general debug messages, critical to supress errors
    #loglevel = "INFO"
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
    stats = SharedStats()
    stats.lock = threading.Lock()
    qsize = urlqueue.qsize()

    inpobj = Input(shared, stats, sys.argv, mode)
    inpobj.process()
    dup = DuplicateCheck()
    dup.setlogging(loglevel)

    if mode == txtinputmode:
        inpobj.start()

    print(f"Opened {inpobj.filename} with size {inpobj.sizeoffile} bytes")
    print(f"{stats.amtthreads} threads starting...")

    start = time.time()

    #Either crawl using multithreading (threading.thread) or with multiprocessing (multiprocessing.process.BaseProcess)


    #Multithreading

    for i in range(0, stats.amtthreads, 1):
        t = CrawlThread(i, "crawler", shared, stats, loglevel)
        t.start()
        threads.append(t)
    p = PrintThread(0, threads, shared, stats, qsize, loglevel)
    p.start()
    for t in threads:
        t.join()

    p.join()


    #Multiprocessing
    '''
    for i in range(0, stats.amtthreads, 1):
        t = CrawlThread_mp(i, "crawler", shared, stats, loglevel)
        #t.start()
        threads.append(t)
    p = PrintThread(0, threads, shared, stats, qsize, loglevel)
    p.start()

    for t in threads:
        #t.join()
        t.run()

    p.join()
    '''



    end = time.time()
    totaltime = end - start
    if mode == txtinputmode:
        print(f"Extracted {stats.extracted} URLs @ {int(stats.extracted/inpobj.totaltime):d}/s")
        print(f"Looked up {stats.dnslookup} DNS names @ {int(stats.dnslookup/totaltime):d}/s")
        print(f"Downloaded {stats.robots} robots @ {int(stats.robots/totaltime):d}/s")
        print(f"Crawled {stats.crawled} pages @ {int(stats.crawled/totaltime):d}/s")
        print(f"Parsed {stats.links} links @ {int(stats.links/totaltime):d}/s")
        print(f"HTTP codes: 2xx = {stats.responses[0]}, 3xx = {stats.responses[1]}, 4xx = {stats.responses[2]}, 5xx = {stats.responses[3]}, other = {stats.responses[4]}")
    
    
# call main() method:
if __name__ == "__main__":
   main()
