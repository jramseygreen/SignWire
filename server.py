import socket
import threading
import json


class Server:
    def __init__(self, meta_data, server_list):
        self.host = '0.0.0.0'
        self.port = 10000
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.meta_data = meta_data
        self.server_list = server_list
        self.driver()


    def driver(self):
        print(self.meta_data)
        self.s.bind((self.host, self.port))
        self.s.listen()
        print("listening")

        while True:
            c, addr = self.s.accept()
            if addr[0] not in self.server_list:
                self.server_list.append(addr[0])

            print("accepted", c, addr)
            x = threading.Thread(target=clientThread, args=(c, addr, self.meta_data))
            x.start()



def clientThread(c, addr, meta_data):
    message = ""
    while message != "quit":
        message = c.recv(1024).decode()
        print("message recieved is: ",message)
        if message == "ping":
            c.sendall(("pong").encode())

        elif message == "meta_rq":
            send_meta(c, meta_data)

        elif message == "file_rq":
            send_file(c)
        #default
        else:
            c.sendall(("error").encode())

    print("closed client", c, addr)
    c.close()


def send_meta(c, meta_data):
    c.sendall((meta_data["timestamp"]))
    if (c.recv(1024).decode() == "ready"):
        payload = json.dumps(meta_data)
        c.sendall(payload.encode())

def send_file(c):
    c.sendall(("sending file").encode())
    if (c.recv(1024).decode() == "ready"):
        f = open("test.txt", "rb")
        c.sendall(f.read())
        f.close()
