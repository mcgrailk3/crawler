import logging, threading, time
from queue import Queue

class PrintThread (threading.Thread):
    def __init__(self, id, threads, shared, qsize, loglevel):
        threading.Thread.__init__(self)
        self.threadid = id
        self.threads = threads
        self.shared = shared
        self.qsize = qsize
        self.count = None
        self.log = logging.getLogger(__name__)
        self.log.setLevel(loglevel)
        
    def run(self):
        self.count = 0
        while len(self.threads):
            self.shared.lock.acquire()
            print(f"[{self.count:>4}] {len(self.threads):>5}  \
                Q {self.shared.Q.qsize():>3}  \
                E {self.qsize-self.count:>3}  \
                H {len(self.shared.hostTable):>3}  \
                D {self.shared.dnslookup:>3}  \
                I {len(self.shared.ipTable):>}  \
                R {self.shared.robots:>3}  \
                C {self.shared.crawled:>3}  \
                L {self.shared.links:>3}")
            #print(f"\t *** crawling {} pps @ {.1f} Mbps")
            self.shared.lock.release()
            time.sleep(2)
            self.count += 2