
import socket
import threading
from   threading import Thread

class TelloLink():
    """
    // ----------------------------------------------------------------------------------------------------------------------------
    This module provides an alternative communications layer for the DJI Tello drone
    -------------------------------------------------------------------------------------------------------------------------------
    Back End:
    
        downlink_com(port)                 Thread: Handles downlink data transmissions from the drone (OK responses + errors).
        downlink_telemetry(port)           Thread: Receives telemetry data from the drone.
        uplink(DATA, hold_ping: bool)      Sends data uplink to the drone.
                                            - When streaming from the ground station, the ping must be held to maintain mode and connection.
                                            - Otherwise, ping takes priority over data streaming.
        connection_()                      Connection state machine (external rate limiting recommended).
        telem_buffer()                     Buffers telemetry data from the socket (external rate limiting recommended).
    
    Utility (Front End):
    
        uplink(DATA, hold_ping: bool)      Sends data uplink to the drone.
                                            - Usually, you want hold_ping enabled while sending/streaming.
                                            - DATA should be a "command" (see DJI Tello protocol documentation).
        disconnect()                       Disconnect toggle.
        connect()                          Connect toggle (enabled by default at runtime).
        get_telem(search_id)               Retrieve a telemetry state from the buffer.
    
    -------------------------------------------------------------------------------------------------------------------------------
    Written by:      Steven Andrews II
    // ----------------------------------------------------------------------------------------------------------------------------
    """




    '''Buffer:     Telemetry parsing buffer  : TELEMETRY__ -> defaults to empty if not reciving   '''
    def telem_buffer(self):
        self.TELEMETRY__    =   {} 
        for _ in  self.telemetry_keys:
            for i in self.raw_telemetry :
                k_          =   i.split(":")
                key_        =   k_[0]
                if key_ == _ :       
                    self.TELEMETRY__[key_] = k_[1]   
            


    '''Utility:    Get telemetry from the buffer    '''
    def get_telem(self,search):  
         for k,v in self.TELEMETRY__.items():
             if k == search:
                 return v                           
         return False           
        
   
   
    '''Socket:      UDP Respons Receive Thread   ( receives responses from commands )   '''
    def downlink_com(self_,port):
        while True:
            if self_.connection_data["connection_toggle"] == True and self_.downlink_hold == False:
                try: 
                        DATA    ,  ADDRESS      = self_.client_socket.recvfrom(   port   ) 
                        self_.incoming          = True
                except socket.error as error_ :
                    print("Error: in downlink_com")                                        



    '''Socket:      Receives telemetry information from the drone      '''
    def downlink_telemetry(self_,port):
        while True:
            if self_.connection_data["connection_toggle"] == True and self_.downlink_hold == False :
                try:
                        DATA    ,  ADDRESS      =  self_.client_state_socket.recvfrom(   port   ) 
                        DATA                    =  DATA.decode(  'ASCII'  )
                        self_.raw_telemetry     =  DATA.split(";")
                        if self_.hold           == True:     
                           self_.incoming       =  True
                           self_.hold           =  False
                except socket.error as error_ :
                        print("Error: downlink_telemetry") 
               


    '''Socket:      Outgoing packet handler    '''
    def uplink(self,DATA,*arg):
        if  self.connection_data["connection_toggle"] == True:
            self.hold             = False or bool(  arg  )   #  ping command hold 
            try:
               PACKET             = str.encode(   DATA   )
               self.client_socket.sendto(  PACKET , self.DRONE_address  )  
            except socket.error:
                print("outgoing: socket error")
    


    '''Utility:      Quick toggle comunications off   '''
    def disconnect(self):
        if  self.connection_data["connection_toggle"]           != False:
            self.connection_data["connection_state"]            = False
            socket.socket .close(self.client_socket )                    
            socket.socket .close(self.client_state_socket )
            self.connection_data["connection_toggle"]           = False
            return  True
        else:
            return  True
        
        
     '''Utility:      Quick toggle comunications on  ( default is on ) '''
    def connect(self):
        if  self.connection_data["connection_toggle"]           != True:
            self.connection_data["connection_toggle"]           = True
            return  True
        else:
            return  True


    '''Handler:      Establish Connection and track state    '''
    def connection_(self):      
       if  self.connection_data["connection_toggle"]  == True:      
           self.connection_data["ping_clk"]                                 =  self.connection_data["ping_clk"]    +   1
           #     disconnection detection 
           if self.connection_data["connection_state"] == True and self.connection_data["conCheck_index"] > self.connection_data["conCheck_Mindex"]:
              self.connection_data["conCheck_index"]                        = 0
              self.connection_data["connection_state"]                      = False
           
           #     AUto bind to local host 
           if self.connection_data["connection_state"] == False and self.connection_data["conCheck_index"] > self.connection_data["conCheck_Mindex"]:
              self.downlink_hold                                            = True
              socket.socket .close(self.client_socket )                     # clear socket objects 
              socket.socket .close(self.client_state_socket )
              self.host_name              = socket. gethostname()                                                          
              self.local_ip               = socket. gethostbyname( self.host_name )
              self.CMDsoc                 = socket. socket(  socket.AF_INET , socket.SOCK_DGRAM  )                         
              self.telemetry              = socket. socket(  socket.AF_INET , socket.SOCK_DGRAM  )                         
              self.CMDsoc          .bind(  (   self.local_ip ,  self.UDP_control_port         )  )
              self.telemetry       .bind(  (   ""            , self.UDP_state_port            )  )
              self.client_socket                                            = self.CMDsoc                                    
              self.client_state_socket                                      = self.telemetry                               
              self.connection_data["conCheck_index"]                        = 0
              self.downlink_hold                                            = False

           #    connection ping 
           if self.connection_data["ping_clk"] >= (self.connection_data["ping_MClk"]/2):
               if self.connection_data["connection_sub_state"] == False:
                  # Hold: holds the command uplink if streaming data ( telemetry downlink keeps the connection state open )
                  if self.hold  != True:
                        print       (   "Ping..."   ) 
                        self.uplink (   "command"   )

                  self.connection_data["conCheck_index"]                    = self.connection_data["conCheck_index"]   +  1
                  self.connection_data["connection_sub_state"]              = True    
                  
           # time out 
           if self.connection_data["ping_clk"] >= (self.connection_data["ping_MClk"]) :
                  self.hold                                                 = False
                  self.connection_data["connection_sub_state"]              = False
                  self.connection_data["ping_clk"]                          = 0

           # incoming data // reset state machine        
           if self.incoming == True: 
                self.connection_data["connection_state"]                    = True    
                self.connection_data["ping_clk"]                            = 0
                self.connection_data["connection_sub_state"]                = False
                self.connection_data["conCheck_index"]                      = 0
                self.incoming                                               = False

                


    '''      Iitial set up for Comunications lib        '''
    def __init__(self):

        #   Telemetry 
        self.raw_telemetry          = []                # raw telemetry data ( backend )
        self.TELEMETRY__            = {}                # parsed telemetry data from the buffer 
        # look up table 
        self.telemetry_keys = (                         # A list of every possible telemetry data index/key
                'mid', 'x', 'y', 'z',
                'pitch', 'roll', 'yaw',
                'vgx', 'vgy', 'vgz',
                'templ', 'temph',
                'tof', 'h', 'bat', 'time','baro',
                'agx', 'agy', 'agz'
            )


        #   connection state toggles 
        self.incoming               = False             # incoming data state 
        self.hold                   = False             # sending data / hold ping rquest 
        self.downlink_hold          = False             # hold threads while changing sockets ( ussed durring a loss of connection )
        self.UPLINK_PORT            = 1024              # Client ports 
        
        #   Connection Link State Data
        self.connection_data = {
            "connection_state"      : False,            # state of connection ckeck  ( the actual state of connection: client side connection momitoring )
            "connection_sub_state"  : False,            # state of connection ckeck ( spam reduction )
            "ping_clk"              : 0,                # internal clock
            "ping_MClk"             : 4*60,             # frame time ( *60 ~ convert to seconds )
            "conCheck_index"        : 0,                # connection time out clk
            "conCheck_Mindex"       : 2,                # connection time out 
            "connection_toggle"     : True,             # on / off state for drone connection
            }

        #   Users IP and port 
        self.host_name              = socket. gethostname()                                                           # pull ip from socket host 
        self.local_ip               = socket. gethostbyname( self.host_name )
        self.CMDsoc                 = socket. socket(  socket.AF_INET , socket.SOCK_DGRAM  )                          # command    socket object  ( AFINET = IPV4 protocalll // DGRM = datagram )
        self.telemetry              = socket. socket(  socket.AF_INET , socket.SOCK_DGRAM  )                          # telemetry  socket object

       #    Drone coms_ data :
        self.drone_ip               = '192.168.10.1'
        self.droneVideo_ip          = '0.0.0.0'         
        self.UDP_control_port       = 8889
        self.UDP_state_port         = 8890
        self.UDP_video_port         = 1111 # beta 2.0
        self.DRONE_address          = (self.drone_ip , self.UDP_control_port)

        #   open sockets 
        self. CMDsoc        .bind(  (   self.local_ip ,  self.UDP_control_port         )  )
        self. telemetry     .bind(  (   ""            ,  self.UDP_state_port           )  )

        # wrap sockets 
        self.client_socket                           = self.CMDsoc          
        self.client_state_socket                     = self.telemetry        

        
        # create threads 
        self.threads_init                     = False
        if not self.threads_init:
            # command responsed thread
            self.receive_thread                      = threading.Thread( target = TombStone.downlink_com         , args = (  self,   self.UPLINK_PORT) )
            self.receive_thread.daemon               = True                                                               # force thred to run in parallel 
            self.receive_thread.start()
            # status responsed thread
            self.status_thread                       = threading.Thread( target = TombStone.downlink_telemetry   , args = (  self,   self.UPLINK_PORT) )
            self.status_thread.daemon                = True                                                               # force thred to run in parallel 
            self.status_thread.start()
            # <>>> end stop
            self.threads_init                 = True
