from ipaddress import ip_address
import time
import socket
from tkinter import W
from Packet import *
from Window import *
import sys

#helper constants    
SERVER_IP="localhost"
SERVER_PORT = 8007
ROUTER_IP = "localhost"
ROUTER_PORT = 3000
ALIVE= 10
TIME_OUT=2
WINDOW_SIZE=5
TIME_OUT_FOR_RECEIVE = 30

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
    
    def getPacket(self,tOut):
        self.__conn.settimeout(tOut)
        try:
            pData, address= self.__conn.recvfrom(PACKET_SIZE)
            pkt= Packet.from_bytes(pData)
            print("Receved:"+ pkt + pkt.payload )
            self.__routerAddr=address
            
            if self.__pcktBuilder is None:
                self.__pcktBuilder=Packetbuilder(pkt.peer_ip_addr, pkt.peer_port)
            
            return pkt 
        except socket.timeout:
            print("Timeout bc of recvfrom msg..")
            return None
    
    #client ---> server
    def connectToServer(self):
        #for 3-way handshake
        print("connecting to :"+SERVER_IP+ " : "+SERVER_PORT)
        self.__routerAddr=(ROUTER_IP,ROUTER_PORT)
        peer_ip = ip_address(socket.gethostbyname(SERVER_IP))
        self.__pcktBuilder = Packetbuilder(peer_ip, SERVER_PORT)
        self.__conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#udp 
        try:
            #syn sent from client
            p1= self.__pcktBuilder.pcktBuild(PACKET_TYPE_SYN)
            self.__conn.sendto(p1.to_bytes(),self.__routerAddr)
            self.__conn.settimeout(ALIVE)
            print("Waiting for server response...\n")
            resp, sender= self.__conn.recvfrom(PACKET_SIZE)# expecting syn/ack from server
            p1=Packet.from_bytes(resp)         
            print("Server connection is ON!")
        except socket.timeout:
            print("Connection has timed out!")
            self.__conn.close()
            sys.exit(0)
            
        if p1.packet_type==PACKET_TYPE_SYN_AK:
            p1=self.__pcktBuilder.pcktBuild(PACKET_TYPE_AK) #sending AK to server
            self.__conn.sendto(p1.to_bytes(), self.__routerAddr)
            return True #Servers ready, no need to timeout
        else:
            print("Unexpected packet as follows: "+ p1) 
            self.__conn.close()
            sys.exit(0)    
                   
    #server--->client
    def connectToClient(self):
        self.__conn=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__conn.bind('',SERVER_PORT)
        print("Server is listening at "+ SERVER_IP+" : "+SERVER_PORT)
        
        pk= self.getPacket(ALIVE)
        
        if pk is None:
            print("Connection timeout...")
            return False
        
        if pk.packet_type == PACKET_TYPE_SYN: #if server already received SYN, send back ACK/SYN
            pk.packet_type = PACKET_TYPE_SYN_AK
            self.__conn.sendto(pk.to_bytes(), self.__routerAddr) #We can ignore the incoming ACK bc client wont have to deal with this case 
            print("Client connection established.")
            return True
        
        return False
    
    def sendMsg(self, msg):
        wd= Window()
        wd.createSenderWindow(msg)        
        threading.Thread(target=self.senderListener, args=(wd,)).start()
        while wd.hasPendingPacket():  # Not all packets have been sent
            #if theres any window, get the packets that can be sent
            for frame in wd.getFrames():
                p = self.__pcktBuilder.pcktBuild(PACKET_TYPE_DATA, frame.seq_num, frame.payload)
                self.__conn.sendto(p.to_bytes(), self.__routerAddr)
                print("sending message: "+ p.payload)
                frame.timer = time.time()
                frame.send = True
    
    #Listening response from server 
    def senderListener(self, window):        
        while window.hasPendingPacket():
            # Find sent packets that haven't been ACKed & check the timers
            try:
                self.__conn.settimeout(TIME_OUT)
                response, sender = self.__conn.recvfrom(PACKET_SIZE)
                p = Packet.from_bytes(response)
                #logging.debug('[Transport] Received response: {}: {}'.format(p, p.payload.decode("utf-8")))
                if p.packet_type == PACKET_TYPE_AK:
                    window.updateWindow(p.seq_num)
            except socket.timeout:
                #logging.debug("[Transport] Timeout when wait ACK.")
                for i in range(window.pointer, window.pointer + WINDOW_SIZE):
                    if i >= len(window.frames):
                        break
                    f = window.frames[i]
                    if f.send and not f.ACK:
                        # reset send status, so it can be re-sent
                        f.send = False

        #logging.debug('[Transport] Listener reaches the end!')
    
    def receiveMessage(self):
        window = Window()
        window.createReceiverWindow()
        while not window.finished():
            # TODO if None, raise error
            p = self.getPacket(TIME_OUT_FOR_RECEIVE)
            if p is None:
                #logging.debug("[Transport] No message received in timeout time")
                return None
            # discard possible packet from handshake
            if p.packet_type == PACKET_TYPE_AK and p.seq_num == 0:
                continue
            window.process(p)
            # send ACK
            p.packet_type = PACKET_TYPE_AK
            self.__conn.sendto(p.to_bytes(), self.__routerAddr)

        data = self.retrieveData(window)
        return data
    
    # return data (bytes)
    def retrieveData(self, window):
        data = b''
        for f in window.frames:
            data = data + f.payload
        return data   
     
    def dis_connect(self):
        #Disconnecting: FIN, ACK, FIN, ACK
        #logging.info("Disconnecting.")
        print("Disconnecting server. Thank you!")
        self.__conn.close()    