# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 13:44:42 2021

@author: josh
"""

import os
import sys
import threading
import socket
from cryptography.fernet import Fernet

import file_io
import server
import file_grabber


class Main:

    def __init__(self):
        self.port = 10000
        self.meta_data = {}

        server_list = file_io.read_data("server_list")
        if server_list is None:
            server_list = []
        else:
            server_list = server_list.split(",")

        self.server_list = server_list
        self.key = file_io.read_bytes("key")
        self.s = socket.socket()
        self.password = ""

    def metaDelete(self, a):
        delete_list = []
        for key in self.meta_data:
            if key not in a:
                delete_list.append(key)

        return delete_list

    def run(self):
        if self.key is None:
            self.key = Fernet.generate_key()
            file_io.write_bytes(["key"], self.key)
        else:
            if self.server_list == []:
                sys.exit("you should have a server in the server_list!")

        # store auth variable
        f = Fernet(self.key)
        self.password = f.encrypt("join".encode())

        # scan all files in tree
        for subdir, dirs, files in os.walk("files"):
            for filename in files:
                filepath = subdir + os.sep + filename

                # filter only file types we want (TODO)
                if filepath.endswith(".jpg") or filepath.endswith(".png"):
                    # get md5 of file
                    md5 = file_io.to_md5(filepath)

                    # create key for new file based on md5 + path
                    if md5 in self.meta_data:
                        self.meta_data[md5].append(filepath)
                    else:
                        self.meta_data[md5] = [filepath]

        print(self.meta_data)
        #todo
        # display thread

        # file grabber thread
        fg = threading.Thread(target=file_grabber.start, args=(self,))

        # server thread
        s = threading.Thread(target=server.start, args=(self,))
        fg.start()
        s.start()
        #fg.join()
        #s.join()



if __name__ == '__main__':
    run = Main()
    run.run()