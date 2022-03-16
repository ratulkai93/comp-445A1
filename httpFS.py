import socket
import threading
import re
import json

from matplotlib.font_manager import json_dump
from httpFileHandler import FileHandler

class FileServer:
    def __init__(self, port) -> None:
        pass

    def run_fileServer(host, port):
        print("starting custom file server: \n")
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            listener.bind((host, port))
            listener.listen(5)
            print('file server is listening at', port)
            while True:
                conn, addr = listener.accept()
                threading.Thread(target=request_handler, args=(conn, addr)).start()
        finally:
            listener.close()
            
    #read data content from clients request
    def rcv_data(conn):
        data= b''
        while True:
            dt= conn.recv(1024)
            data+=dt
            if len(dt)<1024:
                break
        return data

    def request_handler(conn, addr, dirPath):
        try:
            data=rcv_data(conn).decode("utf-8")
            print("showing received data: \r\n{0}".format(data))
            parsedReq= reqParse(data)
        finally:
            conn.close()    

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
                if(resource== "/get")
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