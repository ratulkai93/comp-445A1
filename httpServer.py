import json
import socket
import threading
import logging
import re
from urllib.parse import urlparse
from pprint import pprint
from httpFS import *
from httpFileHandler import FileHandler
from UDPctrlr import *

# class Operation: 
#     Invalid=0
#     GetFL=1
#     GetFC=2
#     WriteFC=3
#     GetRs=4
#     PostRs=5
#     Dl=6
class MockServer:
    BUFFER_SIZE= 1024
    
    def __init__(self, port=8080, d="."):
        self.port = port
        self.dataDir = d
    
    def startServer(self):
        print("Starting mock Server: \n")
        self.udpServe()
		# while(True):
        #     try:
        #         self.__conn.settimeout(LISTENER)
        #         response, sender = self.__conn.recvfrom(PACKET_SIZE)
        #         p = Packet.from_bytes(response)
        #         p.peer_ip_addr = peer_ip_addr
        #         p.peer_port = int(peer_port)
        #         logging.debug('[Transport] Received response: {}: {}'.format(p, p.payload.decode("utf-8")))
        #         self.serving()
        #     except socket.timeout:
        #         pass


    def udpServe(self):
        server= UDPctrlr()
        if not server.connectToClient():
            sys.exit(0)
        data= server.receiveMessage()
        if data is None:
            sys.exit(0)
        data.decode('utf-8')
        print("Received the data: \r\n"+data)
        reqParser= ParsingHttpRequests(data)
        print("received: "+ reqParser.method)
        resp_message= genResponse(reqParser, self.dataDir)
        print("response message: "+resp_message)
        server.sendMsg(resp_message)
        server.dis_connect()
    
    def status_phrase(self, status):
        phrase = ''
        if status == 200:
            phrase = 'OK'
        if status == 301:
            phrase = 'Moved Permanently'
        if status == 400:
            phrase = 'Bad Request'
        if status == 404:
            phrase = 'Not Found'
        if status == 505:
            phrase = 'HTTP Version Not Supported'
        
        return phrase
    
    def genResponse(self, requestParser, pathDir):
        fileapp= FileHandler()
        if requestParser.method =="GET":
            if requestParser.operation == FileOp.Dl:
                status = 200
                requestParser.contentType = "text/html"
                content = "this is a download file for testig purpose."     
            elif requestParser.operation == FileOp.GetRes:
                status = 200
                content = "{\"args\": \"" + requestParser.getParameter +"\"}"
            elif requestParser.operation == FileOp.GetFList:
                fileapp.get_all_files(dirPath, requestParser.contentType)
                status = fileapp.status
                content = fileapp.content
            elif requestParser.operation == FileOp.GetFContent:
                fileapp.get_content(dirPath, requestParser.fileName, requestParser.contentType)
                status = fileapp.status
                content = fileapp.content		
        elif requestParser.method == "POST":
            if requestParser.operation == FileOp.PostRes:
                logging.debug("Regular post.")
                status = 200
                content = "{\"args\": {},\"data\": \"" + requestParser.fileContent + "\"}"
            else:
                fileapp.post_content(dirPath, requestParser.fileName, requestParser.fileContent, requestParser.contentType)
                status = fileapp.status
                content = fileapp.content
        # response
        response_msg = 'HTTP/1.1 ' + str(status) + ' ' + self.status_phrase(status) + '\r\n'
        response_msg = response_msg + 'Connection: close\r\n' + 'Content-Length: ' + str(len(content)) + '\r\n'
        if requestParser.operation == Operation.Download:
            response_msg = response_msg + 'Content-Disposition: attachment; filename="download.txt"\r\n'
        response_msg = response_msg + 'Content-Type: ' + requestParser.contentType + '\r\n\r\n'
        response_msg = response_msg + content
        return response_msg.encode("utf-8")       