#  coding: utf-8 
import socketserver, os, urllib.parse
from email.utils import formatdate
from pathlib import Path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Ismaeel Bin Mohiuddin
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(4096).strip()
        root = os.path.abspath("./www")
        # print ("Got a request of: %s\n" % self.data)
        data = self.data.split(b'\r\n')
        get_value = b''
        for request in data:
            # print(request)
            if request.startswith(b'GET'):
                get_value = request.split()[1]

        header = ""
        status = ""
        date = ""
        content_type = ""
        content_length = ""
        allow = ""
        message = ""
        file = b'./www' + get_value
        file = urllib.parse.unquote(file.decode()).encode()
        handled = False

        if not data[0].startswith(b'GET'):
            status = "HTTP/1.1 405 Method Not Allowed\r\n"
            content_type = "Content-type:text/html\r\n"
            allow = "Allow: GET\r\n"
            message = "<h1>405 Method Not Allowed</h1>"

        else:

            abs_path = os.path.abspath(file.decode())

            if root in abs_path:
                # Path is inside root
                if os.path.isdir(file):
                    # is a directory
                    if not file.endswith(b'/'):
                        # Needs to be redirected
                        file += b'/'
                        newpath = file.decode()[5:]
                        status = 'HTTP/1.1 301 Moved Permanently\r\nLocation: ' + newpath + '\r\n'
                        handled = True
                    else:
                        file += b'index.html'

                if os.path.isfile(file) and not handled:

                    if status == "":
                        status = "HTTP/1.1 200 OK\r\n"

                    if (file.endswith(b'.html')):
                        # HTML
                        content_type = "Content-type:text/html\r\n"
                        message = open(file, 'r').read()

                    elif (file.endswith(b'.css')):
                        # CSS
                        content_type = "Content-type:text/css\r\n"
                        message = open(file, 'r').read()

                    else:
                        # Others
                        content_type = "Content-type:application/octet-stream\r\n"
                        message = open(file, 'rb').read()

                elif not handled:
                    # Does not exist
                    status = "HTTP/1.1 404 Not Found\r\n"
                    content_type = "Content-type:text/html\r\n"
                    message = "<h1>404 Not Found</h1>"
            else:
                # When path is outside root
                status = "HTTP/1.1 404 Not Found\r\n"
                content_type = "Content-type:text/html\r\n"
                message = "<h1>404 Not Found</h1>"

        if len(message) > 0:
            # When there is a body
            content_length = "Content-Length: " + str(len(message)) + "\r\n"

        date = "Date: " + str(formatdate(timeval=None, localtime=False, usegmt=True)) + "\r\n"
        header = status + date + content_length + "Connection: close\r\n" + content_type + allow + "\r\n"
        # print(header)
        header = bytearray(header, 'utf-8')
        if type(message) == str:
            message = bytearray(message, 'utf-8')
        self.request.sendall(header + message)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
