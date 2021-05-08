import socket
import threading
import hashlib
import os


class FileServer:
    def __init__(self, hostname, port, node):
        self.node = node
        self.hostname = hostname
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((hostname, port))

    def client_thread(self, c, addr):
        md5 = c.recv(1024).decode()
        print(md5,"requested")
        data = self.node.meta_manager.send_file(c, md5)
        c.close()

    def start(self):
        threading.Thread(target=self.listener).start()

    def listener(self):
        self.sock.listen()
        print("file server started")
        while True:
            c, addr = self.sock.accept()
            threading.Thread(target=self.client_thread, args=(c, addr,)).start()
