import glob
import json
import shutil
import socket
import threading
import os
import time

import FileServer
import Q
import Meta_Manager
import DirScanner
import httpServer


class Node:
    def __init__(self, hostname, port, cycle_time):
        self.hostname = hostname
        self.cycle_time = cycle_time
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.file_server = FileServer.FileServer(hostname, port + 1, self)
        self.order_lock = threading.Lock()
        self.meta_manager = Meta_Manager.Manager(self)
        self.dir_scanner = DirScanner.DirScanner(self, "files")
        self.http_server = httpServer.httpServer(port + 2)

        self.sock.bind((hostname, port))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def start(self):
        for subdir, dirs, files in os.walk("."):
            if "files" in subdir or "html" in subdir:
                for filename in files:
                    os.remove(subdir + os.sep + filename)

        self.file_server.start()
        threading.Thread(target=self.listener).start()
        self.sock.sendto("join".encode(), ('255.255.255.255', self.port))
        print("sent join request")
        #time.sleep(10)
        self.dir_scanner.start()
        self.http_server.start()
        threading.Thread(target=self.html_displayer).start()
        while False:
            self.sock.sendto("join".encode(), ('255.255.255.255', self.port))
            print("sent join request")
            time.sleep(30)

    def html_displayer(self):
        print("cycling htmls")
        content = '<style>html{height: 100%;margin: 0;}.bg {background-image: url("default.jpg");height: 100%; background-position: center;background-repeat: no-repeat;background-size: cover;}</style><div class="bg"></div>'
        while True:
            try:
                files = []
                for file in os.listdir("html"):
                    files.append(file)
                    if ".html" in file:
                        print("new display item")
                        shutil.copy("html" + os.sep + file, "content.html")
                        time.sleep(self.cycle_time)
                if len(files) == 0:
                    f = open("content.html", "r")
                    if content != f.read():
                        f = open ("content.html", "w")
                        f.write(content)
                        f.close()

            except FileNotFoundError:
                f = open("content.html", "w")
                f.write(content)
                f.close()



    def listener(self):
        print("listener started")
        while True:
            data, addr = self.sock.recvfrom(2048)
            if addr[0] != self.hostname:
                threading.Thread(target=self.client_thread, args=(data, addr,)).start()

    def client_thread(self, data, addr):
        q = Q.Q()
        q.push(data.decode().split('|'))

        while not q.empty():
            command = q.pop()
            print(command)

            if 'join' in command:
                self.sock.sendto(("meta_data|" + self.meta_manager.get_json()).encode(), addr)

            elif 'add' in command:
                self.meta_manager.acquire(addr[0], self.port + 1, q.pop(), q.pop())

            elif 'del' in command:
                path = q.pop()
                try:
                    os.remove(path)
                except:
                    print("already removed",path)

            elif 'meta_data' in command:
                new_meta = json.loads(q.pop())

                for md5 in new_meta:
                    if not self.meta_manager.contains_md5(md5):
                        for path in new_meta[md5]:
                            self.meta_manager.acquire(addr[0], self.port + 1, md5, path)
        #print(self.meta_manager.meta)