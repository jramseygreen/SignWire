import socket
import json



class Client:
    def __init__(self, meta_data, server_list):
        self.meta_data = meta_data
        self.server_list = server_list
        self.port = 10000


    def driver(self):
        while True:
            print(self.meta_data)
            if len(self.server_list) > 0:
                self.update()


    def update(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for server in self.server_list:
            s.connect((server, self.port))
            s.sendall("meta_rq".encode())
            if (s.recv(1024).decode() > self.meta_data["timestamp"]):
                #update
                s.sendall("ready".encode())
                data=s.recv(1024).decode()
                self.meta_data=json.loads(data)
                s.sendall("quit".encode())
            else:
                s.sendall("nvm".encode())
                s.sendall("quit".encode())
            #meta request





# port = 10000
# ip = '192.168.0.31'
# msg = "ping"
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((ip,port))
#
# def pingpong() :
#     msg=""
#     while (msg!="quit"):
#         msg = input("Message: ")
#         s.sendall(msg.encode())
#         r = s.recv(1024).decode()
#         print(r)
#         if (r=="sending file"):
#             f=open("test.txt","x")
#             f=open("test.txt","wb")
#             s.sendall(("ready").encode())
#             f.write(s.recv(1024))
#             f.close()
#
#         if (r=="sending meta"):
#             s.sendall(("ready").encode())
#             data=s.recv(1024).decode()
#             #metaprint(data)
#             meta_data=json.loads(data)
#             #meta_data["test"]=4
#             print(meta_data)
#
# meta_data={}
# pingpong()
