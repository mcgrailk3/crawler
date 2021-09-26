class SharedStats:
    def __init__(self):
        self.lock = None
        self.dnslookup = 0
        self.robots = 0
        self.links = 0
        self.crawled = 0
        self.amtthreads = 0
        self.bytes = 0
        self.extracted = 0
        self.responses = [0,0,0,0,0]