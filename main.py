import os
import socket
import json
from pandas import array
from sympy import false, isprime, true

class TCPServer:

    fileName = b""
    content = b""
    endpointCheck = true
    fileCheck = true


    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print("Listening at", server.getsockname())
        while True:
            conn, addr = server.accept()
            print("Connected by", addr)
            data = conn.recv(1024)
            request = HTTPRequest(data) 
            try:
                if (request.method == "GET" or request.method == "PUT" or request.method == "DELETE"):
                    pass
                elif (request.method == "POST"):
                    indexB = data.index(b"boundary")
                    indexC = data.index(b"Content-Length")
                    indexB += 35
                    boundary = data[indexB:indexC]
                    boundary = boundary.replace(b"\r\n",b"")
                    i = data.index(b"filename")
                    s = data[i:len(data)]
                    i = s.index(b"filename")
                    i += 10
                    i2 = s.index(b"Content-Type: ") - 3
                    global fileName 
                    fileName = s[i:i2]
                    while True:
                        tmp = conn.recv(1024)
                        data += tmp
                        if (boundary in tmp):
                            break
                    i3 = data.rindex(b"Content-Type: ")
                    i3 += 14
                    s2 = data[i3:]
                    i4 = s2.index(b"\r\n\r") + 4
                    s2 = s2[i4:]
                    i5 = s2.index(boundary)
                    s2 = s2[:i5]
                    i5 = s2.rindex(b"\r\n")
                    s2 = s2[:i5]
                    global content
                    content = s2
            except ValueError:
                path = request.uri.strip('/')
                global endpointCheck
                endpointCheck = true
                global fileCheck
                fileCheck = true
                if (path == "upload"):
                    fileCheck = false
                else:
                    endpointCheck = false
            request = HTTPRequest(data) 
            try:
                handler = getattr(self, 'handle_%s' % request.method)
            except AttributeError:
                pass
            response = handler(request)
            conn.sendall(response)
            conn.close()
            

class HTTPServer(TCPServer):
    """The actual HTTP server class."""
    headers = {
        'Server': 'TCPServer',
    }
    status_codes = {
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found',
    }

    def response_line(self, status_code):
        reason = self.status_codes[status_code]
        response_line = 'HTTP/1.1 %s %s\r\n' % (status_code, reason)
        return response_line.encode()

    def response_headers(self, extra_headers=None):
        headers_copy = self.headers.copy()
        if extra_headers:
            headers_copy.update(extra_headers)
        headers = ''
        for h in headers_copy:
            headers += '%s: %s\r\n' % (h, headers_copy[h])
        return headers.encode() 

    def handle_GET(self, request):
        path = request.uri.strip('/')
        if (path != "isPrime" and path != "download"):
            try:
                endpoint = path[0:path.index("?")]
                parameter = path[path.index("?")+1:path.index("=")]
                value = path[path.index("=")+1:]
                if (endpoint == "isPrime"):
                    if (parameter == "number"):
                        if (value.isdigit()):
                            number = int(value)
                            response_line = self.response_line(200)
                            response_header = self.response_headers()
                            if (isprime(number)):
                                r = {
                                    "number": number,
                                    "isPrime": True,
                                }
                                r_encode = json.dumps(r, indent=2).encode('utf-8')
                            else:
                                r = {
                                    "number": number,
                                    "isPrime": False,
                                }
                                r_encode = json.dumps(r, indent=2).encode('utf-8')
                            response_body = r_encode
                            blank_line = b"\r\n"
                            response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                            return response
                        else:
                            response_line = self.response_line(400)
                            response_header = self.response_headers()
                            blank_line = b"\r\n"
                            r = {
                                "message": "Please give an integer as parameter.",
                            }
                            r_encode = json.dumps(r, indent=2).encode('utf-8')
                            response_body = r_encode
                            response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                            return response
                    else:
                        response_line = self.response_line(400)
                        response_header = self.response_headers()
                        blank_line = b"\r\n"
                        r = {
                            "message": "The parameter name is not named as number",
                        }
                        r_encode = json.dumps(r, indent=2).encode('utf-8')
                        response_body = r_encode
                        response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                        return response
                elif (endpoint == "download"):
                    if (parameter == "fileName"):
                            if os.path.exists(value):
                                file = open(value, "rb")
                                data = file.read(1024)
                                array = bytearray()
                                while data:
                                    array += data
                                    data = file.read(1024)
                                pass
                                response_line = self.response_line(200)
                                response_header = self.response_headers()
                                blank_line = b"\r\n"
                                response_body = b''.join([array])
                                response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                                return response
                            else:
                                response_line = self.response_line(200)
                                response_header = self.response_headers()
                                blank_line = b"\r\n"
                                r = {
                                    "message": "There is no file with that name.",
                                }
                                r_encode = json.dumps(r, indent=2).encode('utf-8')
                                response_body = r_encode
                                response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                                return response
                    else:
                        response_line = self.response_line(400)
                        response_header = self.response_headers()
                        blank_line = b"\r\n"
                        r = {
                            "message": "The parameter name is not named as fileName.",
                        }
                        r_encode = json.dumps(r, indent=2).encode('utf-8')
                        response_body = r_encode
                        response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                        return response 
            except ValueError:
                if (endpoint == "isPrime" or endpoint == "download"):
                    response_line = self.response_line(400)
                    response_header = self.response_headers()
                    blank_line = b"\r\n"
                    response = b''.join([response_line, blank_line, response_header, response_line])
                    return response 
            response_line = self.response_line(404)
            response_header = self.response_headers()
            blank_line = b"\r\n"
            response = b''.join([response_line, blank_line, response_header, response_line])
            return response
        else:
            response_line = self.response_line(400)
            response_header = self.response_headers()
            blank_line = b"\r\n"
            r = {
                "message": "There is no parameter.",
            }
            r_encode = json.dumps(r, indent=2).encode('utf-8')
            response_body = r_encode
            response = b''.join([response_line, blank_line, response_header, response_line, response_body])
            return response

    def handle_POST(self, request):
        if (endpointCheck == false):
            response_line = self.response_line(404)
            response_header = self.response_headers()
            blank_line = b"\r\n"
            response = b''.join([response_line, blank_line, response_header, response_line])
            return response
        if (fileCheck == false):
            response_line = self.response_line(400)
            response_header = self.response_headers()
            r = {
                "message": "There is no file to upload.",
            }
            r_encode = json.dumps(r, indent=2).encode('utf-8')
            response_body = r_encode
            blank_line = b"\r\n"
            response = b''.join([response_line, blank_line, response_header, response_line, response_body])
            return response
        path = request.uri.strip('/')
        name = fileName.decode("utf-8")
        try:
            if (path == "upload"):
                f = open(name, "wb")
                f.write(content)
                response_line = self.response_line(200)
                response_header = self.response_headers()
                response_body = b"Status: 200 OK"
                blank_line = b"\r\n"
                response = b''.join([response_line, blank_line, response_header, response_body])
                return response
        except ValueError:
            pass   
        response_line = self.response_line(404)
        response_header = self.response_headers()
        response_body = b"Status: 404 Not Found"
        blank_line = b"\r\n"
        response = b''.join([response_line, blank_line, response_header, response_body])
        return response

    def handle_PUT(self, request):
        path = request.uri.strip('/')
        try:
            endpoint = path[0:path.index("?")]
            name1 = path[path.index("?")+1:path.index("=")] #oldFileName 
            value1 = path[path.index("=")+1:path.index("&")] 
            name2 = path[path.index("&")+1:path.rindex("=")] #newName
            value2 = path[path.rindex("=")+1:]
            if (endpoint == "rename" and name1 == "oldFileName" and name2 == "newName" and len(value1) != 0 and len(value2) != 0):
                response_line = self.response_line(200)
                response_header = self.response_headers()
                response_body = b""
                blank_line = b"\r\n"
                if not os.path.exists(value1):
                    r = {
                        "message": "We couldn't find a file with that name."
                    }
                    r_encode = json.dumps(r, indent=2).encode('utf-8')
                    response_body = r_encode
                else:
                    os.rename(value1, value2)
                    r = {
                        "message": "We changed the name."
                    }
                    r_encode = json.dumps(r, indent=2).encode('utf-8')
                    response_body = r_encode
                response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                return response
            elif (endpoint == "rename" and ( name1 != "oldFileName" or name2 != "newName" or len(value1) == 0 or len(value2) == 0 )):
                response_line = self.response_line(400)
                response_header = self.response_headers()
                response_body = b""
                blank_line = b"\r\n"
                response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                return response
        except ValueError:
            pass                
        response_line = self.response_line(404)
        response_header = self.response_headers()
        response_body = b"Status: 404 Not Found"
        blank_line = b"\r\n"
        response = b''.join([response_line, blank_line, response_header, response_body])
        return response

    def handle_DELETE(self,request):
        path = request.uri.strip('/')
        try:
            endpoint = path[0:6]
            name = path[path.index("?")+1:path.index("=")]
            value = path[path.index("=")+1:]
            if (endpoint == "remove" and name == "fileName"):
                response_line = self.response_line(200)
                response_header = self.response_headers()
                response_body = b""
                blank_line = b"\r\n"
                if os.path.exists(value):
                    os.remove(value)
                    r = {
                        "message": "We deleted your file."
                    }
                    r_encode = json.dumps(r, indent=2).encode('utf-8')
                    response_body = r_encode
                else:
                    r = {
                        "message": "There is no file in our server with that name."
                    }
                    r_encode = json.dumps(r, indent=2).encode('utf-8')
                    response_body = r_encode
                response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                return response
            elif (endpoint == "remove" and name != "fileName"):
                response_line = self.response_line(400)
                response_header = self.response_headers()
                response_body = b""
                blank_line = b"\r\n"
                response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                return response
            pass
        except ValueError:
            if (endpoint == "remove"):
                response_line = self.response_line(400)
                response_header = self.response_headers()
                response_body = b""
                blank_line = b"\r\n"
                response = b''.join([response_line, blank_line, response_header, response_line, response_body])
                return response
                pass
        response_line = self.response_line(404)
        response_header = self.response_headers()
        response_body = b"Status: 404 Not Found"
        blank_line = b"\r\n"
        response = b''.join([response_line, blank_line, response_header, response_body])
        return response


class HTTPRequest:
    "Parser for HTTP requests"

    def __init__(self, data):
        self.method = None
        self.uri = None
        self.http_version = '1.1' # default to HTTP/1.1 if request doesn't provide a version
        self.parse(data)

    def parse(self, data):
        lines = data.split(b'\r\n')
        request_line = lines[0] 
        words = request_line.split(b' ')
        self.method = words[0].decode() 
        if len(words) > 1:
            self.uri = words[1].decode() 
        if len(words) > 2:
            self.http_version = words[2]

if __name__ == '__main__':
    server = HTTPServer()
    server.start()

