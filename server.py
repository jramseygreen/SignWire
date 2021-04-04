import socket
import threading


def clientThread(c, addr):
    message = ""
    while message != "quit":
        message = c.recv(1024).decode()
        print("message recieved is: ",message)
        if message == "ping":
            c.sendall(("pong").encode())

        elif message == "file_rq":
            send_file(c)
        #default
        else:
            c.sendall(("error").encode())

    print("closed client", c, addr)
    c.close()


def send_file(c):
    c.sendall(("sending file").encode())
    if (c.recv(1024).decode() == "ready"):
        f = open("test.txt", "rb")
        c.sendall(f.read())
        f.close()

host = '0.0.0.0'
port = 10000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((host, port))

s.listen()
print("listening")

while True:
    c, addr = s.accept()
    print("accepted", c, addr)
    x = threading.Thread(target=clientThread, args=(c, addr,))
    x.start()
