import socket
import argparse
import sys
import json
from urllib.parse import urlsplit, parse_qs
#parsing lib used below!
#https://www.cs.unb.ca/~bremner/teaching/cs2613/books/python3-doc/library/urllib.parse.html

#this file only prints out whatever we type on the command line 
def run_client(host, port):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((host, port))
        print("Type any thing then ENTER. Press Ctrl+C to terminate")
        while True:
            line = sys.stdin.readline(1024)
            
            # parses the url from this line---> httpc get http://httpbin.org/get?course=networking&assignment=1
            parsedLine= line.split(" ") #splits the input line to list items 
            
            if(parsedLine[2]=="-v"):
                parsedUrl= "".join(map(str,parsedLine[3]))#checks for verbose  and converts the following list item to string
            else:
                parsedUrl= "".join(map(str,parsedLine[2]))#converts the list item to string
            
            request = parsedUrl.encode("utf-8")
            conn.sendall(request)
            # MSG_WAITALL waits for full request or error
            response = conn.recv(len(request), socket.MSG_WAITALL)
            sys.stdout.write(response.decode("utf-8"))
            
            dcURL= response.decode("utf-8")
            query= urlsplit(dcURL).query
            params=json.dumps(parse_qs(query)) 
            print("{ \n",
                  "args: { \n \t",
                        params, "\n",
                    "},\n",
                    "headers: { \n",
                        "\tHost: "+urlsplit(dcURL).netloc ,"\n",
                        "\tUser-agent: Concordia-HTTP/1.0 \n", #need to figure out how to parse this part
                    "}, \n",
                    "url: ", dcURL,
                    "\n}"
                )
            #print(params)#-->prints courses name and assignment number 
            #print(urlsplit(dcURL).netloc) #--> prints host
            #print(urlsplit(dcURL).scheme)
            #print("url: ", dcURL)
           
    finally:
        conn.close()

#python echoclient.py --host localhost --port 8007
# Usage: python echoclient.py --host host --port port
parser = argparse.ArgumentParser()
parser.add_argument("--host", help="server host", default="localhost")
parser.add_argument("--port", help="server port", type=int, default=8007)
args = parser.parse_args()
run_client(args.host, args.port)
