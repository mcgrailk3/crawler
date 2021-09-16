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
        urlparseobj = URLParser()
        while not self.shared.Q.empty():
            # get url from queue, print, parse
            self.shared.lock.acquire()
            url = self.shared.Q.get()
            self.shared.count -= 1
            print(f"URLs left: {self.shared.count}")
            self.shared.lock.release()

            print(f"URL: {url.strip()}")

            hostname, port, path, query, pathquery, scheme = urlparseobj.parse(url)

            #print(f"\tParsing URL... host {hostname}, port {port}, request {pathquery}")
            #print(f"\tParsing URL... host {hostname}, port {port}")
        
            # checking for duplicate hosts, if set length is different, not a dup
            #print(f"\t\033[1mChecking host uniqueness... ", end='')
            self.shared.lock.acquire()
            hostunique = dup.unique(self.shared.hostTable, hostname)
            if not hostunique:
                #print(f"failed\033[0m")
                self.shared.lock.release()
                continue
            #print(f"passed\033[0m")
            self.shared.lock.release()

            mysocket = TCPsocket() # create an object of TCP socket
            mysocket.setlogging(self.log.level)
            mysocket.createSocket()

            #print("\tDoing DNS... ", end='')
            # start measuring time, set start to current time
            start = time.time()
            # get the ip of hostname, dns lookup
            ip = mysocket.getIP(hostname)
            self.shared.lock.acquire()
            self.shared.dnslookup += 1
            self.shared.lock.release()
            # get the end time, set end to current time
            end = time.time()
            # print how long it took, end - start time * 1000 to get in milliseconds
            #print(f"done in {int((end-start)*1000)} ms, found {ip} ")
            if not ip:
                continue
            # checking for duplicate ips, if length is different, not a dup
            self.shared.lock.acquire()
            #print(f"\t\033[1mChecking IP uniqueness... ", end='')
            ipunique = dup.unique(self.shared.ipTable, ip)
            if not ipunique:
                #print(f"failed\033[0m")
                self.shared.lock.release()
                continue
            #print(f"passed\033[0m")
            self.shared.lock.release()

            #print(f"\t\033[1mConnecting on robots... ", end='')
            start = time.time()
            
            if mysocket.connect(ip, port) == -1:
                #print("failed\033[0m")
                continue
            end = time.time()
            #print(f"done in {int((end-start)*1000)} ms \033[0m")

            # build our request
            headrequest = Request()
            head = headrequest.headRequest(hostname)
            # send out request
            #print("\t\033[1mLoading... ", end='')
            start = time.time()
            mysocket.send(head)
            data, amtbytes = mysocket.receive() # receive a reply from the server
            end = time.time()
            #print(f"done in {int((end-start)*1000)} ms with {amtbytes} bytes\033[0m")
            if not data.strip():
                continue
            # split data into lines to parse through
            response = data.splitlines()
            # split first line to get status code, easier than using regexs
            responsecode = response[0].split(" ")
            #print(f"\t\033[1mVerifying header... status code {responsecode[1]}\033[0m")
            #print("\n---------------------------------------")
            #print(data.strip())
            
            mysocket.close()

            # if response is 200, then break out of loop, else keep going to build get request
            if responsecode[1] == "200":
                self.shared.lock.acquire()
                self.shared.robots += 1
                self.shared.lock.release()
                continue
            
            mysocket.createSocket()

            #print(f"      * Connecting on page... ", end='')
            start = time.time()
            
            if mysocket.connect(ip, port) == -1:
                #print("failed")
                continue
            end = time.time()
            #print(f"done in {int((end-start)*1000)} ms ")

            # build our request
            getrequest = Request()
            get = getrequest.getRequest(hostname, path, query)

            #print("\tLoading... ", end='')
            start = time.time()
            mysocket.send(get)
            data, amtbytes = mysocket.receive() # receive a reply from the server
            end = time.time()
            #print(f"done in {int((end-start)*1000)} ms with {amtbytes} bytes")
            if not data:
                continue
            # split data into lines to parse through
            response = data.splitlines()
            # split first line to get status code, easier than using regexs
            responsecode = response[0].split(" ")
            #print(f"\tVerifying header... status code {responsecode[1]}")
            #print("      + Parsing page... ", end='')
            start = time.time()
            links = data.count('href')
            end = time.time()
            #print(f"done in {int((end-start)*1000)} ms with {links} links")
            mysocket.close()
        print("thread out of loop")
