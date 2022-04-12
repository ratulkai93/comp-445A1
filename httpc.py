import socket
from urllib.parse import urlparse
import re
#from MockHttpClient import *
from UDPctrlr import *
import logging
import sys
import argparse


class Parameter:
    url = None
    verbose = False
    headers = None
    bodyData = None
    writeFileName = None
    port = 80

    @staticmethod
    def reInit():
        Parameter.url = None
        Parameter.verbose = False
        Parameter.headers = None
        Parameter.bodyData = None
        Parameter.writeFileName = None


def writeFile(fileName, content):
    with open(fileName, 'w') as f:
        f.write(content)
    print("Write reponse to the file: " + fileName)


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


def run_httpc(command):
    # command parsing
    # -v
    if "-v" in command:
        Parameter.verbose = True
    # -h [key:value]
    if "-h" in command:
        Parameter.headers = getHeaders(command)
    if "-o" in command:
        Parameter.writeFileName = command.split(" -o ")[1]
        command = command.split(" -o ")[0]

    urlString = command.split(" ")[-1]
    if "'" in urlString:
        Parameter.url = urlString[1:-1]
    else:
        Parameter.url = urlString

    # Get Usage: httpc get [-v] [-h key:value] URL
    # Post Usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL
    if command.startswith("get") or command.startswith("post"):
        o = urlparse(Parameter.url)
        host = o.hostname
        if o.port is None:
            port = Parameter.port
        else:
            port = o.port
        while True:
            udpClient = UdpController()
            udpClient.connectServer()
            if command.startswith("post"):
                if "-d" in command and "-f" not in command:
                    infos = command.split(" -d ")[1].split(" ")
                    Parameter.bodyData = (infos[0] + infos[1])[1:-1]
                if "-f" in command and "-d" not in command:
                    readFileName = command.split(" -f ")[1].split(" ")[0]
                    with open(readFileName, 'r') as f:
                        Parameter.bodyData = f.read()
                request = HttpRequest(host, o.path, Parameter.bodyData, Parameter.headers)
                # print(request.getPost().decode('utf-8'))
                logging.debug("Client sent request: {}".format(request.getPost()))
                udpClient.sendMessage(request.getPost())

            else:
                request = HttpRequest(host, o.path, o.query, Parameter.headers)
                logging.debug("Client sent request: {}".format(request.getGet()))
                udpClient.sendMessage(request.getGet())
            data = udpClient.receiveMessage()
            if data is None:
                logging.debug("Client did not receive response.")
                sys.exit(0)
            logging.debug("Client received response: {}".format(data.decode('utf-8')))

            response = HttpResponse(data)
            if response.code == HttpCode.redirect:
                host = response.location
            else:
                break

        udpClient.dis_connect()

        if Parameter.verbose:
            print(response.text)
            if Parameter.writeFileName is not None:
                writeFile(Parameter.writeFileName, response.text)
        else:
            print(response.body)
            if Parameter.writeFileName is not None:
                writeFile(Parameter.writeFileName, response.text)

    # If invalid
    else:
        print("Invalid command.")


def getHeaders(command):
    pairs = re.findall("-h (.+?:.+?) ", command)
    return "\r\n".join(pairs)
    # return command.split(" -h ")[1].split(" ")[0]


def recvall(sock):
    BUFF_SIZE = 1024  # 1 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data


# program entrance
# parse the input parameters
parser = argparse.ArgumentParser()
parser.add_argument("-v", help="output log", action='store_true')
args = parser.parse_args()

# whether output debug
if (args.v):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
else:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

while True:
    user_input = input("\nplease enter your request, or: "
                       "enter \"help\" for instructions, "
                       "enter \"quit\" to exit the program\n")
    try:
        if "help" in user_input:
            showHelp(user_input)
        if "quit" in user_input:
            sys.exit(0)
        Parameter.reInit()
        run_httpc(user_input)
    except AttributeError:
        print("Invalid command, please check your option arguments")
    except FileNotFoundError:
        print("File not found, please check your file name or directory")
    except:
        print("Invalid command")
    print("------------------------request ends------------------------")
