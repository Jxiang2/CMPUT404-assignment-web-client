#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self, url):
        [host, port] = [None, None]
        #get host
        if urllib.parse.urlparse(url).hostname != None:
            #print(urllib.parse.urlparse(url).hostname)
            host = urllib.parse.urlparse(url).hostname
        else:
            host = "http://127.0.0.1"

        #get port
        if urllib.parse.urlparse(url).port != None:
            #print(urllib.parse.urlparse(url).port)
            port = urllib.parse.urlparse(url).port
        else:
            port = 80
        return [host, port]

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')    


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        status_code = data.split(" ")[1]
        return int(status_code)

    def get_headers(self,data):
        header = data.split("\r\n\r\n")[0]
        return header

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body

    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def interact(self, host, port, payload):
        self.connect(host, port)
        self.sendall(payload)
        data = self.recvall(self.socket)
        status_code = self.get_code(data)
        print("code: ", status_code)
        body = self.get_body(data)
        self.close()

        return status_code, body


    def GET(self, url, args=None):
        try:
            path = urllib.parse.urlparse(url).path if urllib.parse.urlparse(url).path != "" else "/"
            #print("path: " ,path)
            [host, port] = self.get_host_port(url)
            connection = "Connection: close\r\n\r\n"
            payload = "GET" + " " + path + " " + "HTTP/1.1\r\n" + "Host:" + host + "\r\n" + connection
            status_code, body = self.interact(host, port, payload)

        except ConnectionRefusedError:
            response = HTTPResponse(code=404, body= {" "})
            return response
        return HTTPResponse(status_code, body)

    def POST(self, url, args=None):
        try:
            path = urllib.parse.urlparse(url).path if urllib.parse.urlparse(url).path != "" else "/"
            [host, port] = self.get_host_port(url)
            connection = "Conntection: close \r\n"
            payload = ""

            if args != None:
                message = urllib.parse.urlencode(args)
                content_length = "Content-length: " + str(len(message)) + "\r\n"
                payload = "POST" + " " + path + " " + "HTTP/1.1\r\n" + "Host:" + \
                    host + "\r\n" + content_length + connection + "\r\n" + urllib.parse.urlencode(args)
            else:
                content_length = "Content-length: " + str(0) + "\r\n"
                payload = "POST" + " " + path + " " + "HTTP/1.1\r\n" + "Host:" + \
                    host + "\r\n" + content_length + connection + "\r\n"
                #print out payload
            status_code, body = self.interact(host, port, payload)
            
        except ConnectionRefusedError:
            response = HTTPResponse(code=404, body= {" "})
            return response
        return HTTPResponse(status_code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
