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
from multiprocessing import process
import multiprocessing

class CrawlThread_mp (multiprocessing.process.BaseProcess):
    def __init__(self, ID, name, shared, stats, loglevel):
        process.BaseProcess.__init__(self)
        self.threadID = ID
        self.name = name
        self.shared = shared
        self.stats = stats
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

            mysocket = TCPsocket()  # create an object of TCP socket
            mysocket.setlogging(self.log.level)
            mysocket.createSocket()

            # print(f"\tDoing DNS... {self.threadID}", end='')
            # get the ip of hostname, dns lookup
            ip = mysocket.getIP(hostname)
            self.stats.lock.acquire()
            self.stats.dnslookup += 1
            self.stats.lock.release()

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
            head = headrequest.headRequest11(hostname)
            # send out request
            mysocket.send(head)
            data, amtbytes = mysocket.receivehead()  # receive a reply from the server

            if not data.strip():
                continue
            # split data into lines to parse through
            response = data.splitlines()
            # split first line to get status code, easier than using regexs
            responsecode = response[0].split(" ")
            # print(f"Response: {response}")
            # mysocket.close()

            # if response is 200, then break out of loop, else keep going to build get request
            if responsecode[1] == "200":
                mysocket.close()
                self.stats.lock.acquire()
                self.stats.robots += 1
                self.stats.lock.release()
                continue

            # mysocket = TCPsocket() # create an object of TCP socket
            # mysocket.setlogging(self.log.level)
            # mysocket.createSocket()

            # if mysocket.connect(ip, port) == -1:
            #    continue

            # build our request
            getrequest = Request()
            get = getrequest.getRequest11(hostname, path, query)

            # print(f"\tLoading... {self.threadID}", end='')
            mysocket.send(get)
            data, amtbytes = mysocket.receive()  # receive a reply from the server
            mysocket.close()
            if not data:
                continue
            # split data into lines to parse through
            response = data.splitlines()
            # split first line to get status code, easier than using regexs
            responsecode = response[0].split(" ")
            # print(f"Response code: {responsecode}")
            # print(f"Response: {response}")
            # print(f"\tVerifying header... status code {responsecode[1]} {self.threadID}")
            # print("      + Parsing page... ", end='')
            if 'HTTP' not in responsecode[0]:
                self.stats.lock.acquire()
                self.stats.responses[4] += 1
                self.stats.lock.release()
                continue
            if responsecode[1][0] == "2":
                pass
            elif responsecode[1][0] == "3":
                pass
            elif responsecode[1][0] == "4":
                self.stats.lock.acquire()
                self.stats.responses[2] += 1
                self.stats.lock.release()
                continue
            elif responsecode[1][0] == "5":
                self.stats.lock.acquire()
                self.stats.responses[3] += 1
                self.stats.lock.release()
                continue
            else:
                self.stats.lock.acquire()
                self.stats.responses[4] += 1
                self.stats.lock.release()
                continue

            links = data.count('href')
            self.stats.lock.acquire()
            if responsecode[1][0] == "2":
                self.stats.responses[0] += 1
            elif responsecode[1][0] == "3":
                self.stats.responses[1] += 1
            self.stats.crawled += 1
            self.stats.bytes += amtbytes
            self.stats.links += links
            self.stats.lock.release()
        self.stats.lock.acquire()
        self.stats.amtthreads -= 1
        self.stats.lock.release()
        return