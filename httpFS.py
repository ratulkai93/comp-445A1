from audioop import add
from os import stat
import socket
import threading
import re
import json

from matplotlib.font_manager import json_dump
from httpFileHandler import FileHandler

class FileServer:
    def __init__(self, port=8080,dir="."):
        self.port= port
        self.directory= dir

    def run_fileServer(self):
        print("starting custom file server: \n")
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            listener.bind(('', self.port))
            listener.listen(5)
            print('file server is listening at', self.port)
            while True:
                (conn, addr) = listener.accept()
                threading.Thread(target=request_handler, args=(conn, addr, self.directory)).start()
        finally:
            print("Closing server. Thank you!")
            listener.close()
            print("server is now shut down...")
            
    #read data content from clients request
    def rcv_data(self,conn):
        data= b''
        while True:
            dt= conn.recv(1024)
            data+=dt
            if len(dt)<1024:
                break
        return data

    def request_handler(self, conn, addr, dirPath):
        try:
            data=rcv_data(conn).decode("utf-8")
            print("showing received data: \r\n{0}".format(data))
            parsedReq= ParsingHttpRequests(data)
            print("received request is: {0}",format(parsedReq.method))
            response_Message=self.respGenerator(parsedReq, dirPath)
            print("retrieving response: {0}".format(response_Message))
            conn.send(response_Message)
        finally:
            conn.close()    
            print("disconnecting from the address: {0}".format(addr))

    def respGenerator(self, parsedReq, dirPath):
        fh= FileHandler()
        
        if parsedReq.method=="GET":
            if parsedReq.operation== FileOp.DL:
                status= 200
                parsedReq.contentType= "text/html"
                content= "DL file for testing!"
                
            elif parsedReq.operation==FileOp.GetRes:
                status=200
                content="{\"args\": \""+parsedReq.getParams +"\"}"
            
            elif parsedReq.operation==FileOp.GetFList:
               fh.getAllFiles(dirPath, parsedReq.contentType)
               status= fh.stat
               content= fh.content 
            
            elif parsedReq.operation==FileOp.GetFContent:
                fh.content_GET(dirPath, parsedReq.fileName, parsedReq.contentType)
                status= fh.stat
                content= fh.content
        
        elif parsedReq.method =="POST":
            if parsedReq.operation== FileOp.PostRes:
                print("making post response: \n")
                status=200
                content="{\"args\": {}, \"data\": \""+parsedReq.fileContent +"\"}"
            else:
                fh.content_POST(dirPath, parsedReq.fileName, parsedReq.fileContent, parsedReq.contentType)
                status= fh.stat
                content= fh.content
                
        #generating response and encoding        
        resp_msg= 'HTTP/1.1 ' + str(status) + ' ' + self.status_msg(status) + '\r\n'+'Connection: close\r\n' + 'Content-Length: ' + str(len(content)) + '\r\n'
        if parsedReq.operation==FileOp.DL:
            resp_msg+= 'Content-Disposition: attachment; filename="download.txt"\r\n'
        resp_msg+= 'Content-Type: ' + parsedReq.contentType + '\r\n\r\n' + content
        
        return resp_msg.encode("utf-8")
        
    def status_msg(self, status):
        msg= ''
        if status==200:
            msg= 'OK!'
        if status==301:
            msg= 'Permanently moved'
        if status==400:
            msg= 'Bad Request!'
        if status==404:
            msg= 'Not found'
        if status==505:
            msg= 'HTTP version not supported'
        return msg                 
                
class ParsingHttpRequests:
    def __init__(self,data):
        self.contentType="application/json"
        self.getParams=""
        
        (http_header, http_body)= data.split('\r\n\r\n')
        headerLines= http_header.split('\r\n')
        (method, resource, version)= headerLines[0].split(' ')
        
        for line in headerLines:
            if("Content-Type" in line):
                self.contentType= line.split(':')[1]
            
        if(resource.endswith("?")):
            resource=resource[:-1]
            
        #parsing GET    
        if(method=="GET"):
            self.method= "GET"
            
            if(resource.startswith("/get")):
                self.operation=FileOp.GetRes
                if(resource== "/get"):
                    self.getParams=""
                else:
                    l, r= resource.split('?')
                    out={}
                    for kv in r.split('&'):
                        key, value= kv.split('=')
                        out[key]=value
                    self.getParams=json_dumps(out)
                    
            elif(resource.startswith("/download")):
                self.operation= FileOp.DL  
            elif(resource.startswith("/")):
                self.operation= FileOp.GetFList
            else:
                m= re.match(r"/(.+)",resource) #matching regex
                if(m):
                    self.operation=FileOp.GetFContent
                    self.fileName= m.group(1)
                else:
                    self.operation=FileOp.Invalid
        #parsing POST            
        elif(method=="POST"):
            self.method="POST"
            m= re.match(r"/(.+)",resource)
            if(m):
                self.fileContent= http_body
                if(m.group(1)=="post"):
                    self.operation=FileOp.PostRes
                else:
                    self.operation= FileOp.WriteFContent
                    self.fileName= m.group(1)
            else:
                self.operation= FileOp.Invalid
        else:
            self.method="Invalid"
            
        self.version= version
            
            
                 

class FileOp:
    Invalid=0
    GetFList=1
    GetFContent=2
    WriteFContent=3
    GetRes=4
    PostRes=5
    DL= 6            
        
        
        
        
# parser = argparse.ArgumentParser()
# parser.add_argument("--port", help="file server port", type=int, default=8080)
# args = parser.parse_args()
# run_fileServer('', args.port)