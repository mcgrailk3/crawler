import logging, threading, time
from queue import Queue

class PrintThread (threading.Thread):
    def __init__(self, id, threads, shared, stats, qsize, loglevel):
        threading.Thread.__init__(self)
        self.threadid = id
        self.pages = None
        self.oldcrawled = None
        self.threads = threads
        self.shared = shared
        self.stats = stats
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
        while (self.stats.amtthreads) > 0:
            self.stats.lock.acquire()
            self.pages = self.stats.crawled -self.oldcrawled
            #print(f"pages: {self.pages}")
            print(f"[{self.count:>4}] {self.stats.amtthreads:>5}  \
Q {self.shared.Q.qsize():>6}  \
E {self.stats.extracted:>6}  \
H {len(self.shared.hostTable):>6}  \
D {self.stats.dnslookup:>6}  \
I {len(self.shared.ipTable):>6}  \
R {self.stats.robots:>6}  \
C {self.stats.crawled:>5}  \
L {int((self.stats.links)/1000):>6d}K")
            print(f"\t *** crawling {(self.pages/2):.1f} pps @ {((self.stats.bytes/2)*8)/1000:.1f} Mbps")
            self.oldcrawled = self.stats.crawled
            self.stats.bytes = 0
            self.stats.lock.release()
            time.sleep(2)
            self.count += 2
        return
