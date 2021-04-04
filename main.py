import hashlib
import os
import time

import threading
import server
#import client

def put_meta():
    hash_table = {}

    for subdir, dirs, files in os.walk("files"):
        for filename in files:
            filepath = subdir + os.sep + filename

            # filter only file types we want (TODO)
            if filepath.endswith(".jpg") or filepath.endswith(".png") or filepath.endswith(".txt"):
                # get md5 of file
                f = open(filepath, "rb")
                data = f.read(1024)
                md5 = hashlib.md5(data).hexdigest()

                # create key for new file based on md5 + path
                if md5 in hash_table:
                    hash_table[md5].append(filepath)
                else:
                    hash_table[md5] = [filepath]

    hash_table["timestamp"] = time.time()
    return hash_table


def serverThread(meta_data):
    s = server.Server(meta_data)


def clientThread(meta_data):
    client.Client(meta_data)


meta_data = put_meta()
# scan all files in tree

#print(meta_data)

t1 = threading.Thread(target=serverThread, args=(meta_data,))
t1.start()

#client = threading.Thread(target=clientThread, args=(meta_data,))
#client.start()
