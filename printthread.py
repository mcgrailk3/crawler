import logging, threading, time
from queue import Queue

class PrintThread (threading.Thread):
    def __init__(self, id, threads, shared, qsize, loglevel):
        threading.Thread.__init__(self)
        self.threadid = id
        self.pages = None
        self.oldcrawled = None
        self.threads = threads
        self.shared = shared
        self.qsize = qsize
        self.count = None
        self.log = logging.getLogger(__name__)
        self.log.setLevel(loglevel)
        
    def run(self):
        self.count = 0
        self.pages = 0
        self.oldcrawled = 0
        time.sleep(2)
        self.count += 2
        while (self.shared.amtthreads) > 0:
            self.shared.lock.acquire()
            self.pages = self.shared.crawled -self.oldcrawled
            print(f"[{self.count:>4}] {self.shared.amtthreads:>5}  \
Q {self.shared.Q.qsize():>6}  \
E {self.shared.extracted:>6}  \
H {len(self.shared.hostTable):>6}  \
D {self.shared.dnslookup:>6}  \
I {len(self.shared.ipTable):>6}  \
R {self.shared.robots:>6}  \
C {self.shared.crawled:>5}  \
L {int((self.shared.links)/1000):>6d}K")
            print(f"\t *** crawling {(self.pages/2):.1f} pps @ {((self.shared.bytes/2)*8)/1000:.1f} Mbps")
            self.oldcrawled = self.shared.crawled
            self.shared.bytes = 0
            self.shared.lock.release()
            time.sleep(2)
            self.count += 2
        return
