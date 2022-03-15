# By Rahimuz Zaman, 27771789
# By Mingyang Chen, 40026335

import socket
import json
import sys
from urllib.parse import urlsplit, parse_qs, urlparse

from numpy import byte

# todo: httpc_get needs to be able to return header

def run_httpcClient():
    line = input('type your request or quit: ')
    if line == "quit":
        sys.exit(0)
    parsedLine = line.split(" ")

    needVerbose = False
    needHeader = False
    needData = False
        
    if(parsedLine[1]=="help")and(parsedLine[2]=="get"):
        print('\nusage: httpc get [-v] [-h key:value] URL\n\nGet executes a HTTP GET request for a given URL.\n\t-v' \
             '\t\tPrints the detail of the response such as protocol, status, and headers.\n\t-h key:value\t' \
             'Associates headers to HTTP Request with the format "key:value".\n')
        
    if(parsedLine[1]=="help")and(parsedLine[2]=="post"):
        print('\nusage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL\n\nPost executes a HTTP ' \
             'POST request for a given URL with inline data or from file.\n\t-v\t\tPrints the detail of the ' \
             'response such as protocol, status, and headers.\n\t-h key:value\tAssociates headers to HTTP Request ' \
             'with the format "key:value".\n\t-d string\tAssociates an inline data to the body HTTP POST request.' \
             '\n\t-f file\t\tAssociates the content of a file to the body HTTP POST request.\n\nEither [-d] or [-f] ' \
             'can be used but not both.')
        
    if(parsedLine[1]=="help"):
        print('\nhttpc is a curl-like application but supports HTTP protocol only.\nUsage:\n\thttpc.py command ' \
             '[arguments]\nThe commands are:\n\tget\texecutes a HTTP GET request and prints the response.\n\tpost\t' \
             'executes a HTTP POST request and prints the response.\n\thelp\tprints this screen.\n\n' \
             'Use "httpc help [command]" for more information about a command.\n')

    # todo:
    # GET
    if parsedLine[1] == "get":
        print("getting: ", end="")

        # httpc get -v URL
        if (parsedLine[2] == "-v") and (parsedLine[3] != "-h"):
            needVerbose = True
            parsedStuff = "".join(map(str, parsedLine[3]))
            print("v")

        # httpc get -h "k:v" URL
        elif parsedLine[2] == "-h":
            needHeader = True
            parsedHeader = "".join(map(str, parsedLine[3]))
            parsedUrl = "".join(map(str, parsedLine[4]))
            parsedStuff = parsedHeader + " " + parsedUrl
            print("h")

        # httpc get -v -h "k:v" URL
        elif (parsedLine[2] == "-v") and (parsedLine[3] == "-h"):
            needVerbose = True
            needHeader = True
            parsedHeader = "".join(map(str, parsedLine[4]))
            parsedUrl = "".join(map(str, parsedLine[5]))
            parsedStuff = parsedHeader + " " + parsedUrl
            print("v h")

        # httpc get URL
        else:
            parsedStuff = "".join(map(str, parsedLine[2]))
            print("null")

        httpc_get(parsedStuff, needVerbose, needHeader)
        # httpc_get(parsedUrl, needVerbose)

    # POST
    if parsedLine[1] == "post":
        print("posting: ", end="")

        # httpc post -v -h "k:v" -d inline-data URL
        if (parsedLine[2] == "-v") and (parsedLine[3] == "-h") and (parsedLine[5] == "-d"):  # works fine --> httpc post -v -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
            print("v h d")
            needVerbose = True
            needHeader = True
            needData = True
            parsedHeader = "".join(map(str, parsedLine[4]))
            parsedData = "".join(parsedLine[6])
            parsedUrl = "".join(map(str, parsedLine[7]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("v h d successes")

        # httpc post -h "k:v" -d inline-data URL
        elif (parsedLine[2] == "-h") and (parsedLine[4] == "-d"):  # works atm--> httpc post -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
            print("h d")
            needHeader = True
            needData = True
            parsedHeader = "".join(map(str, parsedLine[3]))
            parsedData = "".join(parsedLine[5])
            parsedUrl = "".join(map(str, parsedLine[6]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("h d successes")

        # httpc post -v -h"k:v" -f file URL
        elif (parsedLine[2] == "-v") and (parsedLine[3] == "-h") and (parsedLine[5] == "-f"):  # works fine --> httpc post -v -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
            print("v h f")
            needVerbose = True
            needHeader = True
            needData = True
            parsedHeader = "".join(map(str, parsedLine[4]))
            parsedFileName = "".join(parsedLine[6])
            try:
                print(parsedFileName)
                with open(parsedFileName, 'r') as f:
                    parsedData = f.read()
                print(parsedData)
            except IOError:
                print("File is not found.")
                quit()
            else:
                print("File is successfully read.")
            parsedUrl = "".join(map(str, parsedLine[7]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("v h f successes")

        # httpc post -h"k:v" -f file URL
        elif (parsedLine[2] == "-h") and (parsedLine[4] == "-f"):
            print("h f")
            needHeader = True
            needData = True
            parsedHeader = "".join(map(str, parsedLine[3]))
            parsedFileName = "".join(parsedLine[5])
            try:
                print("loading " + parsedFileName)
                with open(parsedFileName, 'r') as f:
                    parsedData = f.read()
                print(parsedData)
            except IOError:
                print("File is not found.")
                quit()
            else:
                print("File is successfully read.")
            parsedUrl = "".join(map(str, parsedLine[6]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("h f successes")

        # httpc post -v URL
        elif parsedLine[2] == "-v":  # causes bad request when input---> httpc post -v http://httpbin.org/post
            print("Need more parameters! Just -v is not enough")
            quit()
            needVerbose = True
            parsedStuff = "".join(map(str, parsedLine[3]))  # list goes out of bounds

        # httpc post -h"k:v" URL
        elif parsedLine[2] == "-h":  # doesnt work anymore--> httpc post -h Content-Type:application/json http://httpbin.org/post
            print("Need more parameters! Just -h is not enough")  # list goes out of bounds
            quit()
            needHeader = True
            parsedHeader = "".join(map(str, parsedLine[3]))
            parsedUrl = "".join(map(str, parsedLine[4]))
            parsedStuff = parsedHeader + " " + parsedUrl
            print("yoooo")

        # -d and -f cannot be used at the same time
        elif ("-d" in parsedLine) and ("-f" in parsedLine):
            print("-d and -f cannot be used at the same time, program is quiting...")
            quit()

        # httpc post URL
        else:
            parsedStuff = "".join(map(str, parsedLine[2]))
            print("Need more parameters! Try again!")  # list goes out of bounds
            quit()
        httpc_post(parsedStuff, needVerbose, needHeader, needData)

    # Get /
    if parsedLine[0] == "GET":
        if parsedLine[1] == "/":
            print("GET /:")
            # get_list()
        elif parsedLine[1] == "/foo":
            print("GET /foo:")
            # get_foo()
        else:
            print("Wrong input!")

    if parsedLine[0] == "POST":
        if parsedLine[1] == "/bar":
            print("POST /bar:")
            # post_bar()
        else:
            print("Wrong input!")


# parses and sends get request w/ provided url (has additional info for verbose)

def httpc_get(urlstuff, needVerbose, needHeader):
    if needHeader:
        parsedHeaderStuff = urlstuff.split(" ")
        print(urlstuff)
        print(parsedHeaderStuff)
        parsedHeader = "".join(map(str, parsedHeaderStuff[0]))
        url = "".join(map(str, parsedHeaderStuff[1]))
    else:
        parsedHeader = " "
        url = urlstuff
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    get_req="GET /"+path+" HTTP/1.0\r\n"+ parsedHeader +"\r\nHost: "+host+"\r\n\r\n"
    s.sendall(bytes(get_req,'utf-8'))
    display(s, needVerbose)
    s.close()

# httpc post -h Content-Type:application/json --d '{"Assignment": 1}' http://httpbin.org/post
def httpc_post(urlstuff, needVerbose, needHeader, needData):
    print('sending post')
    if needHeader and needData:
        parsedHeaderStuff = urlstuff.split(" ")
        parsedHeader = "".join(map(str, parsedHeaderStuff[0]))
        parsedData = "".join(map(str, parsedHeaderStuff[1]))
        url = "".join(map(str, parsedHeaderStuff[2]))
    else:
        parsedHeader = " "
        parsedData = " "
        url = urlstuff
    print(urlstuff)
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    post_req = "POST /" + path + " HTTP/1.0\r\nHost: " + host + "\r\n" + parsedHeader + "\r\nContent-Length: 17\r\n\r\n" + parsedData + "\r\n"
    s.sendall(bytes(post_req, 'utf8'))
    display(s, needVerbose)
    s.close()

# display the data from socket, includes verbose info if needed
def display(s, needVerbose):
    strRecv = ""
    while True:
        data = s.recv(100)
        if data:
            strRecv = strRecv + (str(data, 'utf8'))
        else:
            break
    if needVerbose:
        print(strRecv)  # Print w/ verbose info
    else:
        print(strRecv.split("\r\n\r", 1)[1])  # Print w/o verbose info

        
# to read and print a file
def read(file_dir):
    try:
        f = open(file_dir, 'r', encoding="utf-8")
        print(f.read)
    except IOError:
        print("HTTP ERROR 404: File not found.")
    f.close()


# to write new content to a file, a new file will be created at the dir if not exists
def write(file_dir, new_content):
    f = open(file_dir, 'a+', encoding="utf-8")
    f.write(new_content)
    f = open(file_dir, 'a+', encoding="utf-8")
    print(f.read)
    f.close()
    
    
# todo:
# def get_list():
# def get_foo():
# def post_bar():

while True:
    run_httpcClient()
    print("----------------request ends----------------")




# paste this on the terminal when running the file---> httpc get http://httpbin.org/get?course=networking&assignment=1

# to test GET request only
# httpc_get('http://httpbin.org/get?course=networking&assignment=1')

# to test POST request only ----> not functional atm!
# httpc_post('http://httpbin.org/get?course=networking&assignment=1')

"""
Test cases:
GET:
    httpc get http://httpbin.org/get?course=networking&assignment=1
    httpc get -v http://httpbin.org/get?course=networking&assignment=1
    httpc get -h Content-Type:text/html http://httpbin.org/get?course=networking&assignment=1
    httpc get -v -h Content-Type:text/html http://httpbin.org/get?course=networking&assignment=1
POST:
    httpc post -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
    httpc post -h Content-Type:application/json -f valid.txt http://httpbin.org/post
    httpc post -v -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
    httpc post -v -h Content-Type:application/json -f valid.txt http://httpbin.org/post
    
    httpc post -h http://httpbin.org/post
    httpc post -v http://httpbin.org/post
    httpc post -h Content-Type:application/json -f non-valid.txt http://httpbin.org/post
"""
