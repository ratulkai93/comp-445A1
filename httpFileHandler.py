import os
import json
import threading
import logging

from matplotlib.font_manager import json_dump

class FileHandler:
    tdLock= threading.Lock() #to prevent race conditions
    
    def __init__(self):
        self.stat= 400
        self.content= ''
    
    def getAllFiles(self, url_dir, contType):
        out={}
        fList=[]
        files= FileHandler.fileList_dir(url_dir)
        for file in files:
            fList.append(file)
        self.stat=200
        self.content=FileHandler.generate_file_content(contType,fList)
    
    def content_GET(self, url_dir, fName, contentType):
        #wrong case 1
        if fName.find('../') != -1:
            out= {}
            out['warning']=400
            out['message']='Bad request!'
            self.stat=400
            self.content= json_dump(out)
        else:
            files= FileHandler.fileList_dir(url_dir)
            #wrong case 2
            if fName not in files:
                out= {}
                out['warning']=404
                out['message']='Not found!'
                self.stat=404
                self.content= json_dump(out) 
            else:
                FileHandler.tdLock.acquire()
                try:
                    with open(url_dir + '/' + fName, 'r', errors="ignore") as fObject:
                        content= fObject.read()
                finally:
                    FileHandler.tdLock.release()
                self.stat=200
                self.content=content 
    
    def content_POST(self,url_dir, fName, content, contType):
        if contType=='application/json':
            parsedJson= json.loads(content)
            for key,value in parsedJson.items():
                content= v #stored parsed data into content
        FileHandler.tdLock.acquire()
        try:
            with open(url_dir + '/'+ fName, 'w') as f:
                f.write(content)
        finally:
            FileHandler.tdLock.release()
        self.stat=200
        self.content= json_dumps("") #convert content to json string
        
    #----------------helper static methods-----------------------
    #returns list of files in the directory
    @staticmethod
    def fileList_dir(url_dir): 
        fileList=[]
        for root, dirs, files in os.walk(url_dir): #walk through os directories & generate file names
            for file in files:
                temp= root + '/' + file
                fileList.append(temp[(len(url_dir)+1):])
        return fileList
    
    #to generate the content of the file with given type
    @staticmethod
    def generate_file_content(content_type, content_list):
        if content_type=='application/json':
            out={}
            out[""]=content_list
            return json_dump(out)
        elif content_type=='text/xml':
            return FileHandler.gen_xml(content_list)
    
    #generate xml content
    @staticmethod
    def gen_xml(fileList):
        xml= "<root>"
        for f in fileList:
            xml+=("<file>"+ f +"</file>")
        xml+="</root>"
        return xml
    
    #returns given files content type
    @staticmethod
    def getContentType(fName):
        content_type= 'text/plain'
        extn= os.path.splitext(fName)[-1]        
        if extn=='.json':
            content_type='application/json'
        if extn=='.html':
            content_type='text/html'
        if extn=='.xml':
            content_type='text/xml'
        
        return content_type