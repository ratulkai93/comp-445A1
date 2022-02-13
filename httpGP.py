import socket
import argparse
import sys
import json
from urllib.parse import urlsplit, parse_qs
#todo: parse the url from cmd, shove into the method to send request

def run_httpcClient():
    line= input('type your request: ')
    parsedLine= line.split(" ")
    if(parsedLine[2]=="-v"):
        parsedUrl= "".join(map(str,parsedLine[3]))#checks for verbose  and converts the following list item to string
    else:
        parsedUrl= "".join(map(str,parsedLine[2]))#converts the list item to string
            
    httpc_get(parsedUrl)
        
        
#parses and sends get request w/ provided url (has additional info for verbose)
def httpc_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()
    
def httpc_post(url):
    print('sending post')
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    #s.send(bytes('POST /%s HTTP/1.0\r\n Host: %s\r\nContent-Type: application/json\r\nContent-Length: 47\r\n\r\n{"capabilities": {}, "desiredCapabilities": {}}'  % (path, host), 'utf8'))
    s.send(bytes('POST /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()

run_httpcClient() 
#paste this on the terminal when running the file---> httpc get http://httpbin.org/get?course=networking&assignment=1

#to test GET request only   
#httpc_get('http://httpbin.org/get?course=networking&assignment=1')

#to test POST request only ----> not functional atm!
#httpc_post('http://httpbin.org/get?course=networking&assignment=1')