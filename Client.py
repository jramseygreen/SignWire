import socket
import json

port = 10000
ip = '192.168.0.31'
msg = "ping"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip,port))

def pingpong() :
    msg=""
    while (msg!="quit"):
        msg = input("Message: ")
        s.sendall(msg.encode())
        r = s.recv(1024).decode()
        print(r)
        if (r=="sending file"):
            f=open("test.txt","x")
            f=open("test.txt","wb")
            s.sendall(("ready").encode())
            f.write(s.recv(1024))
            f.close()

        if (r=="sending meta"):
            s.sendall(("ready").encode())
            data=s.recv(1024).decode()
            #metaprint(data)
            meta_data=json.loads(data)
            #meta_data["test"]=4
            print(meta_data)

meta_data={}
pingpong()
