import shutil
import threading
import os
import hashlib
import json
import socket
from pathlib import Path

class Manager:
    def __init__(self, node):
        self.node = node
        self.meta = {}
        self.meta_lock = threading.Lock()
        self.image_formats = [".apng",".avif",".gif",".jpg", ".jpeg", ".jfif", ".pjpeg", ".pjp",".png", ".svg", ".webp"]

    def clear(self):
        self.meta_lock.acquire(blocking=True)
        self.meta = {}
        self.meta_lock.release()


    def add(self, path):
        self.meta_lock.acquire(blocking=True)
        data = b''
        try:
            f = open(path, "rb")
            data = f.read()
            f.close()
        except PermissionError:
            self.meta_lock.release()
            raise PermissionError

        md5 = hashlib.md5(data).hexdigest()
        print("Added: ", md5)
        if md5 in self.meta:
            self.meta[md5].append(path)
        else:
            self.meta[md5] = [path]
        self.meta_lock.release()
        content = ''
        for format in self.image_formats:
            if format in path:
                content = '<style>html{height: 100%;margin: 0;}.bg {background-image: url("' + path + '");height: 100%; background-position: center;background-repeat: no-repeat;background-size: cover;}</style><div class="bg"></div>'
                break

        if ".mp4" in path:
            content = '<style>video {object-fit: fill;}</style><meta name="viewport" content="width=device-width, initial-scale=1"><video autoplay><source src="' + path + '" type="video/mp4"></video>'
        if content != '':
            f = open("html" + os.sep + md5 + ".html", "w")
            f.write(content)
            f.close()


    def remove_path(self, path):
        self.meta_lock.acquire(blocking=True)
        for md5 in self.meta:
            if path in self.meta[md5]:
                self.meta[md5].remove(path)
                if len(self.meta[md5]) == 0:
                    self.remove_md5(md5)
                    os.remove("html" + os.sep + md5 + ".html")
                break
        self.meta_lock.release()


    def remove_md5(self, md5):
        if md5 in self.meta:
            del self.meta[md5]

    def get_paths(self, md5):
        self.meta_lock.acquire(blocking=True)
        data = []
        if md5 in self.meta:
            data = self.meta[md5]
        self.meta_lock.release()
        return data

    def get_md5(self, path):
        data = ""
        self.meta_lock.acquire(blocking=True)
        for md5 in self.meta:
            if path in self.meta[md5]:
                data = md5
                break

        self.meta_lock.release()
        return data

    def send_file(self, c, md5):
        self.meta_lock.acquire(blocking=True)
        data = b''
        if md5 in self.meta:
            try:
                f = open(self.meta[md5][0], "rb")
                c.sendall(str(os.path.getsize(self.meta[md5][0])).encode())
                if "ready" in c.recv(1024).decode():
                    print("sending data")
                    c.sendall(f.read())
                    print("sent data")
                    f.close()
            except:
                c.sendall("fail".encode())
        self.meta_lock.release()
        return data

    def contains_md5(self, md5):
        return self.get_paths(md5) != []

    def contains_path(self, path):
        return self.get_md5(path) != ""

    def get_json(self):
        self.meta_lock.acquire(blocking=True)
        data = json.dumps(self.meta)
        self.meta_lock.release()
        return data

    def acquire(self, host, port, md5, path):
        self.meta_lock.acquire(blocking=True)
        if md5 not in self.meta:
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_sock.settimeout(5)
            msg = ""
            try:
                temp_sock.connect((host, port))
                temp_sock.sendall(md5.encode())
                msg = temp_sock.recv(1024).decode()

                if 'fail' not in msg:
                    size = int(msg)
                    f = open(md5 + ".tmp", "wb")
                    temp_sock.sendall("ready".encode())
                    data = temp_sock.recv(size)
                    while data:
                        f.write(data)
                        data = temp_sock.recv(size)

                    f.close()
                    self.create_dir(path)
                    shutil.move(md5 + ".tmp", path)
                temp_sock.close()
            except:
                temp_sock.close()
                print("busy file requests")
        else:
            if path not in self.meta[md5]:
                self.create_dir(path)
                shutil.copy(self.meta[md5][0], path)

        self.meta_lock.release()

    def create_dir(self, path):
        while path[-1] != "/":
            path = path[:len(path)-1]

        Path(path).mkdir(parents=True, exist_ok=True)

    def get_all_md5(self):
        self.meta_lock.acquire(blocking=True)
        md5_list = []
        for md5 in self.meta:
            md5_list.append(md5)
        self.meta_lock.release()
        return md5_list