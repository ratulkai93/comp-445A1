import socket
import sys
from urllib.parse import urlparse
import httpcHelper
import re
from httpFS import FileServer


def run_httpc(userInput):
    url = None
    verbose = False
    headers = None
    body_content = None
    file_name = None
    port = 80

    # command parsing
    # -v
    if "-v" in userInput:
        verbose = True
    # -h [key:value]
    if "-h" in userInput:
        pairs = re.findall("-h (.+?:.+?) ", userInput)
        headers = "\r\n".join(pairs)
    # url
    urlString = userInput.split(" ")[-1]
    if "'" in urlString:
        url = urlString[1:-1]
    else:
        url = urlString

    if userInput.startswith("httpc get") or userInput.startswith("httpc post"):
        o = urlparse(url)
        host = o.hostname
        if o.port is None:
            port = port
        else:
            port = o.port
        while True:
            # create socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))

                # GET
                if userInput.startswith("httpc get"):
                    request = httpcHelper.HttpRequest(host, o.path, o.query, headers)
                    s.sendall(request.get_info())

                # POST
                elif userInput.startswith("httpc post"):
                    # -d
                    if "-d" in userInput and "-f" not in userInput:
                        infos = userInput.split(" -d ")[1].split(" ")
                        body_content = (infos[0] + infos[1])[1:-1]
                    # -f
                    if "-f" in userInput and "-d" not in userInput:
                        readFileName = userInput.split(" -f ")[1].split(" ")[0]
                        with open(readFileName, 'r') as f:
                            body_content = f.read()
                    request = httpcHelper.HttpRequest(host, o.path, body_content, headers)
                    s.sendall(request.post_info())
                # print(request.get_info().decode('utf-8'))
                # print(request.post_info().decode('utf-8'))

                data = recvall(s)
            response = httpcHelper.HttpResponse(data)

            if response.code == "301":
                host = response.location
            else:
                break
        display(verbose, response, file_name)

        # Invalid: Either post or get
    else:
        print("Invalid command, please try again")


# display the data from socket, includes verbose info if needed
def display(verbose, response, file_name):
    if verbose:
        print(response.text)
        if file_name is not None:
            with open(file_name, 'w') as f:
                f.write(response.text)
            print("Writing to the file: " + file_name)
    else:
        print(response.body)
        if file_name is not None:
            with open(file_name, 'w') as f:
                f.write(response.text)
            print("Writing to the file: " + file_name)


# show help instructions
def showHelp(command):
    if "get" in command:
        print('\nusage: httpc get [-v] [-h key:value] URL\n\nGet executes a HTTP GET request for a given URL.\n\t-v' \
              '\t\tPrints the detail of the response such as protocol, status, and headers.\n\t-h key:value\t' \
              'Associates headers to HTTP Request with the format "key:value".\n')

    if "post" in command:
        print('\nusage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL\n\nPost executes a HTTP ' \
              'POST request for a given URL with inline data or from file.\n\t-v\t\tPrints the detail of the ' \
              'response such as protocol, status, and headers.\n\t-h key:value\tAssociates headers to HTTP Request ' \
              'with the format "key:value".\n\t-d string\tAssociates an inline data to the body HTTP POST request.' \
              '\n\t-f file\t\tAssociates the content of a file to the body HTTP POST request.\n\nEither [-d] or [-f] ' \
              'can be used but not both.')

    if "help" in command:
        print('\nhttpc is a curl-like application but supports HTTP protocol only.\nUsage:\n\thttpc.py command ' \
              '[arguments]\nThe commands are:\n\tget\t\texecutes a HTTP GET request and prints the response.\n\tpost\t' \
              'executes a HTTP POST request and prints the response.\n\thelp\tprints this screen.\n\n' \
              'Use "httpc help [command]" for more information about a command.\n')


# receive all
def recvall(sock):
    BUFF_SIZE = 1024
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            break
    return data


# Program starts:
while True:
    user_Input = input("\nplease enter your request, or: "
                     "enter \"help\" for instructions, "
                     "enter \"quit\" to exit the program\n")
    try:
        if "help" in user_Input:
            showHelp(user_Input)
        if "quit" in user_Input:
            sys.exit(0)
        run_httpc(user_Input)
    except AttributeError:
        print("Invalid command, please check your option arguments")
    except FileNotFoundError:
        print("File not found, please check your file name or directory")
    except:
        print("Invalid command")
    print("------------------------request ends------------------------")

'''
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
    
FILE SYSTEM:
    httpc get 'http://localhost:8080/'
    httpc get -v 'http://localhost:8080/'
    httpc get -h Content-Type:application/json 'http://localhost:8080/'
    httpc get -h Content-Type:text/xml 'http://localhost:8080/'

    httpc get -v 'http://localhost:8080/foo'
    httpc get -v -h 'http://localhost:8080/../foo'
    httpc get -h Content-Disposition:inline 'http://localhost:8080/foo'
    httpc get -h Content-Disposition:inline 'http://localhost:8080/filename'
    httpc post -h Content-Type:application/json -d '{"": "helloworld"}' http://localhost:8080/foo
    httpc post -h Content-Type:text/txt -d 'helloworld' http://localhost:8080/foo.txt
'''
