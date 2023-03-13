# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import threading

hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>Pygmu 4Ever!</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

def start_server():
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")


# Import the required libraries
from tkinter import *
import webview

# Create an instance of tkinter frame or window
win = Tk()

# Set the size of the window
win.geometry("700x350")

# Create a GUI window to view the HTML content
webview.create_window('pygmu', 'http://localhost:8080')

def start_webview():
    webview.start()
    print('started...')



if __name__ == "__main__":
    # Start the webserver in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    webview_thread = threading.Thread(target=start_webview)
    webview_thread.start()

