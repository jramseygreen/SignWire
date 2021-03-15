# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 15:25:17 2021

@author: josh
"""
import socket
import random

import file_io


def start(main):
    s = socket.socket()
    meta_data = main.meta_data.copy()
    server_list = main.server_list.copy()
    random.shuffle(server_list)
    while meta_data == main.meta_data: # kill thread if hash table updated
        for item in meta_data:
            if not file_io.file_exists(meta_data[item][0]):
                for server in server_list:
                    try:
                        s.connect((server, main.port))
                    except:
                        continue
                    if 'accepted' in s.recv(1024).decode():
                        s.sendall(('rc_file_rq,' + item + ',msgend').encode())
                        data = s.recv(1024)
                        if "fail" not in data.decode():
                            for path in meta_data[item]:
                                file_io.write_bytes(path, data)
                            break

    s.close()
