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

    # GET
    if parsedLine[1] == "get":

        # httpc get -v URL
        if parsedLine[2] == "-v":
            needVerbose = True
            parsedStuff = "".join(map(str, parsedLine[3]))

        # httpc get -h "k:v" URL
        elif parsedLine[2] == "-h":
            needHeader = True
            parsedHeader = "".join(map(str, parsedLine[3]))
            parsedUrl = "".join(map(str, parsedLine[4]))
            parsedStuff = parsedHeader + " " + parsedUrl

        # httpc get -v -h "k:v" URL
        elif (parsedLine[2] == "-v") and (parsedLine[3] == "-h"):
            needVerbose = True
            needHeader = True
            parsedHeader = "".join(map(str, parsedLine[4]))
            parsedStuff = "".join(map(str, parsedLine[5]))

        # httpc get URL
        else:
            parsedStuff = "".join(map(str, parsedLine[2]))

        httpc_get(parsedStuff, needVerbose, needHeader)
        # httpc_get(parsedUrl, needVerbose)

    # POST
    if parsedLine[1] == "post":

        # httpc post -v -h "k:v" -d inline-data URL
        if (parsedLine[2] == "-v") and (parsedLine[3] == "-h") and (parsedLine[5] == "-d"):  # works fine --> httpc post -v -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
            needVerbose = True
            needHeader = True
            needData = True
            parsedHeader = "".join(map(str, parsedLine[4]))
            parsedData = "".join(parsedLine[6])
            parsedUrl = "".join(map(str, parsedLine[7]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("Header plus data with verbose info is working!")

        # httpc post -h "k:v" -d inline-data URL
        elif (parsedLine[2] == "-h") and (parsedLine[4] == "-d"):  # works atm--> httpc post -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
            needHeader = True
            needData = True
            parsedHeader = "".join(map(str, parsedLine[3]))
            parsedData = "".join(parsedLine[5])
            parsedUrl = "".join(map(str, parsedLine[6]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("Header plus data working!")

        # httpc post -v -h"k:v" -f file URL
        elif (parsedLine[2] == "-v") and (parsedLine[3] == "-h") and (parsedLine[5] == "-f"):  # works fine --> httpc post -v -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
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
            else:
                print("File is successfully read.")
            parsedUrl = "".join(map(str, parsedLine[7]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("Header plus file data with verbose info is working!")

        # httpc post -h"k:v" -f file URL
        elif (parsedLine[2] == "-h") and (parsedLine[4] == "-f"):
            needHeader = True
            needData = True
            parsedHeader = "".join(map(str, parsedLine[3]))
            parsedFileName = "".join(parsedLine[5])
            try:
                print(parsedFileName)
                with open(parsedFileName, 'r') as f:
                    parsedData = f.read()
                print(parsedData)
            except IOError:
                print("File is not found.")
            else:
                print("File is successfully read.")
            parsedUrl = "".join(map(str, parsedLine[6]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("Header plus file data is working!")

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
            sys.exit()

        # httpc post URL
        else:
            parsedStuff = "".join(map(str, parsedLine[2]))
            print("Need more parameters! Try again!")  # list goes out of bounds
            quit()
    httpc_post(parsedStuff, needVerbose, needHeader, needData)

# todo: httpc_get needs to be able to return header
# parses and sends get request w/ provided url (has additional info for verbose)

def httpc_get(urlstuff, needVerbose, needHeader):
    if needHeader:
        parsedHeaderStuff = urlstuff.split(" ")
        parsedHeader = "".join(map(str, parsedHeaderStuff[0]))
        url = "".join(map(str, parsedHeaderStuff[1]))
        #print(url)
    else:
        parsedHeader = " "
        url = urlstuff
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    #s.sendall(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    get_req="GET /"+path+" HTTP/1.0\r\n"+ parsedHeader +"\r\nHost: "+host+"\r\n\r\n"
    s.sendall(bytes(get_req,'utf-8'))
    # concatenated_url_string = "GET " + path + "?" + url.query.replace("%26", "&") + " HTTP/1.1\r\nHost: " \
    #                           + url.netloc + "\r\n" + parsedHeader + "\r\n\r\n"
    # request = concatenated_url_string.encode()
    #s.send(request)
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
        # print(parsedData)
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


while True:
    run_httpcClient()




# paste this on the terminal when running the file---> httpc get http://httpbin.org/get?course=networking&assignment=1

# to test GET request only
# httpc_get('http://httpbin.org/get?course=networking&assignment=1')

# to test POST request only ----> not functional atm!
# httpc_post('http://httpbin.org/get?course=networking&assignment=1')
