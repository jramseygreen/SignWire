import socket
import server

def main():
    # gets local ip... standard methods returned home address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    hostname = s.getsockname()[0]
    s.close()

    node = server.Node(hostname, 37702, 10)
    node.start()

if __name__ == "__main__":
    main()
