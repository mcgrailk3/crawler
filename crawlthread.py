import threading, logging, sys, time, re
from fileio import FileIO
from tcpsocket import TCPsocket
from tcprequest import Request
from queue import Queue
from urllib.parse import urlparse
from input import Input
from duplicatecheck import DuplicateCheck
from sharedparameters import SharedParameters
from urlparser import URLParser

class CrawlThread (threading.Thread):
    def __init__(self, ID, name, shared, loglevel):
        threading.Thread.__init__(self)
        self.threadID = ID
        self.name = name
        self.shared = shared
        self.log = logging.getLogger(__name__)
        self.log.setLevel(loglevel)
        
    def run(self):
        dup = DuplicateCheck()
        dup.setlogging(self.log.level)
        
        while not self.shared.Q.empty():
            # get url from queue, print, parse
            url = self.shared.Q.get()
            urlparseobj = URLParser()
            # print(f"URL: {url.strip()}, {self.threadID}")

            hostname, port, path, query = urlparseobj.parse(url)
        
            # checking for duplicate hosts, if set length is different, not a dup
            self.shared.lock.acquire()
            hostunique = dup.unique(self.shared.hostTable, hostname)
            self.shared.lock.release()
            if not hostunique:
                continue

            mysocket = TCPsocket() # create an object of TCP socket
            mysocket.setlogging(self.log.level)
            mysocket.createSocket()

            # print(f"\tDoing DNS... {self.threadID}", end='')
            # get the ip of hostname, dns lookup
            ip = mysocket.getIP(hostname)
            self.shared.lock.acquire()
            self.shared.dnslookup += 1
            self.shared.lock.release()
 
            if not ip:
                continue
            # checking for duplicate ips, if length is different, not a dup
            self.shared.lock.acquire()
            ipunique = dup.unique(self.shared.ipTable, ip)
            self.shared.lock.release()
            if not ipunique:
                continue
            
            if mysocket.connect(ip, port) == -1:
                continue

            # build our request
            headrequest = Request()
            head = headrequest.headRequest(hostname)
            # send out request
            mysocket.send(head)
            data, amtbytes = mysocket.receive() # receive a reply from the server

            if not data.strip():
                continue
            # split data into lines to parse through
            response = data.splitlines()
            # split first line to get status code, easier than using regexs
            responsecode = response[0].split(" ")
            
            mysocket.close()

            # if response is 200, then break out of loop, else keep going to build get request
            if responsecode[1] == "200":
                self.shared.lock.acquire()
                self.shared.robots += 1
                self.shared.lock.release()
                continue
            
            mysocket = TCPsocket() # create an object of TCP socket
            mysocket.setlogging(self.log.level)
            mysocket.createSocket()

            if mysocket.connect(ip, port) == -1:
                continue

            # build our request
            getrequest = Request()
            get = getrequest.getRequest(hostname, path, query)

            # print(f"\tLoading... {self.threadID}", end='')
            mysocket.send(get)
            data, amtbytes = mysocket.receive() # receive a reply from the server

            if not data:
                continue
            # split data into lines to parse through
            response = data.splitlines()
            # split first line to get status code, easier than using regexs
            responsecode = response[0].split(" ")
            # print(f"\tVerifying header... status code {responsecode[1]} {self.threadID}")
            #print("      + Parsing page... ", end='')
            
            if responsecode[1][0] == "2":
                self.shared.lock.acquire()
                self.shared.responses[0] += 1
                self.shared.crawled += 1
                self.shared.lock.release()
            elif responsecode[1][0] == "3":
                self.shared.lock.acquire()
                self.shared.responses[1] += 1
                self.shared.crawled += 1
                self.shared.lock.release()
            elif responsecode[1][0] == "4":
                self.shared.lock.acquire()
                self.shared.responses[2] += 1
                self.shared.lock.release()
                continue
            elif responsecode[1][0] == "5":
                self.shared.lock.acquire()
                self.shared.responses[3] += 1
                self.shared.lock.release()
                continue
            else:
                self.shared.lock.acquire()
                self.shared.responses[4] += 1
                self.shared.lock.release()
                continue

            links = data.count('href')
            self.shared.lock.acquire()
            self.shared.bytes += amtbytes
            self.shared.links += links
            self.shared.lock.release()
            mysocket.close()
        self.shared.lock.acquire()
        self.shared.amtthreads -= 1
        self.shared.lock.release()
        return