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
        while (self.shared.amtthreads) > 0:
            self.shared.lock.acquire()
            print(f"[{self.count:>4}] {self.shared.amtthreads:>5}  \
Q {self.shared.Q.qsize():>6}  \
E {self.qsize-self.count:>6}  \
H {len(self.shared.hostTable):>6}  \
D {self.shared.dnslookup:>6}  \
I {len(self.shared.ipTable):>6}  \
R {self.shared.robots:>6}  \
C {self.shared.crawled:>6}  \
L {self.shared.links:>10}")
            #print(f"\t *** crawling {} pps @ {.1f} Mbps")
            self.shared.lock.release()
            time.sleep(2)
            self.count += 2
        return
