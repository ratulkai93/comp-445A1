import socket
import json
from urllib.parse import urlsplit, parse_qs, urlparse


# todo: parse the url from cmd, shove into the method to send request

def run_httpcClient():
    line = input('type your request: ')
    parsedLine = line.split(" ")

    needVerbose = False
    needHeader = False
    needData = False

    if (parsedLine[2] == "-v"):
        parsedUrl = "".join(
            map(str, parsedLine[3]))  # checks for verbose  and converts the following list item to string
        needVerbose = True
    else:
        parsedUrl = "".join(map(str, parsedLine[2]))  # converts the list item to string

    if (parsedLine[1] == "get"):
        httpc_get(parsedUrl, needVerbose)

    if (parsedLine[1] == "post"):

        if ((parsedLine[2] == "-v") and (parsedLine[3] == "-h") and (parsedLine[5] == "-d")):  # works fine --> httpc post -v -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
            needVerbose = True
            needHeader = True
            needData = True
            parsedHeader = "".join(map(str, parsedLine[4]))
            parsedData = "".join(parsedLine[6])
            parsedUrl = "".join(map(str, parsedLine[7]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("this works!")

        elif ((parsedLine[2] == "-h") and (parsedLine[4] == "-d")):  # works atm--> httpc post -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
            needHeader = True
            needData = True
            parsedHeader = "".join(map(str, parsedLine[3]))
            parsedData = "".join(parsedLine[5])
            parsedUrl = "".join(map(str, parsedLine[6]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("header plus data working!")

        elif ((parsedLine[2] == "-v") and (parsedLine[3] == "-h") and (parsedLine[5] == "-f")):  # works fine --> httpc post -v -h Content-Type:application/json -d {"Assignment":1} http://httpbin.org/post
            needVerbose = True
            needHeader = True
            needData = True
            parsedHeader = "".join(map(str, parsedLine[4]))
            parsedData = "".join(parsedLine[6])
            parsedUrl = "".join(map(str, parsedLine[7]))
            parsedStuff = parsedHeader + " " + parsedData + " " + parsedUrl
            print("this works!")

        elif ((parsedLine[2] == "-h") and (parsedLine[4] == "-f")):
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
            print("header plus file working!")

        elif (parsedLine[2] == "-v"):  # causes bad request when input---> httpc post -v http://httpbin.org/post
            print("need more parameters! just -v is not enough")
            quit()
            needVerbose = True
            parsedStuff = "".join(map(str, parsedLine[3]))  # list goes out of bounds

        elif (parsedLine[2] == "-h"):  # doesnt work anymore--> httpc post -h Content-Type:application/json http://httpbin.org/post
            print("need more parameters! just -h is not enough")  # list goes out of bounds
            quit()
            needHeader = True
            parsedHeader = "".join(map(str, parsedLine[3]))
            parsedUrl = "".join(map(str, parsedLine[4]))
            parsedStuff = parsedHeader + " " + parsedUrl
            print("yoooo")

        else:
            parsedStuff = "".join(map(str, parsedLine[2]))
            print("need more parameters! try again!")  # list goes out of bounds
            quit()
    httpc_post(parsedStuff, needVerbose, needHeader, needData)


# parses and sends get request w/ provided url (has additional info for verbose)
def httpc_get(url, needVerbose):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(addr)
    s.sendall(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    display(s, needVerbose)
    s.close()

# httpc post -h Content-Type:application/json --d '{"Assignment": 1}' http://httpbin.org/post
def httpc_post(urlstuff, needVerbose, needHeader, needData):
    print('sending post')
    if (needHeader and needData):
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
    post_req = "POST /" + path + " HTTP/1.0\r\n" + "Host: " + host + "\r\n" + parsedHeader + "\r\nContent-Length: 17\r\n\r\n" + parsedData + "\r\n"
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


run_httpcClient()
# paste this on the terminal when running the file---> httpc get http://httpbin.org/get?course=networking&assignment=1

# to test GET request only
# httpc_get('http://httpbin.org/get?course=networking&assignment=1')

# to test POST request only ----> not functional atm!
# httpc_post('http://httpbin.org/get?course=networking&assignment=1')
