from ipaddress import ip_address
import logging
import time
import socket
from Packet import *
import sys

#helper constants    
SERVER_IP="localhost"
SERVER_PORT = 8007
ROUTER_IP = "localhost"
ROUTER_PORT = 3000

class Packetbuilder:
    __destAddr=None
    __destPort=None
    
    def __init__(self, destAddr, destPort):
        self.__destAddr=destAddr
        self.__destPort=destPort
    
    def pcktBuild(self, packetType, sequenceNumber = 0, payload = "", islast = False):
        return Packet(packetType, sequenceNumber, self.__destAddr, self.__destPort, islast, payload)

class UDPctrlr:
    __conn=None
    __routerAddr=None
    __pcktBuilder= None
    
    def __init__(self):
        pass
    
    def connectToServer(self):
        #for 3-way handshake
        print("connecting to :"+SERVER_IP+ " : "+SERVER_PORT)
        self.__routerAddr=(ROUTER_IP,ROUTER_PORT)
        peer_ip = ip_address(socket.gethostbyname(SERVER_IP))
        self.__pcktBuilder = Packetbuilder(peer_ip, SERVER_PORT)
        self.__conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#udp 
        try:
            #syn from client to server
            p1= self.__pcktBuilder.pcktBuild(PACKET_TYPE_SYN)#to fix
            self.__conn.sendto(p1.to)
            