import socketserver
import http.server
import threading


# as shown in python docs https://docs.python.org/3/library/http.server.html#http.server.SimpleHTTPRequestHandler
class httpServer:
    def __init__(self, port):
        self.PORT = port
        self.Handler = http.server.SimpleHTTPRequestHandler

    def start(self):
        threading.Thread(target=self.serve).start()

    def serve(self):
        with socketserver.TCPServer(("", self.PORT), self.Handler) as httpd:
            print("http_server serving at port", self.PORT)
            httpd.serve_forever()
