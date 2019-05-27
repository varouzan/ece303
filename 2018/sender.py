# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket
import random

import channelsimulator
import utils
from struct import *

from packaging import *

class Sender(object):


    def __init__(self,inbound_port=50006, outbound_port=50005, timeout=1, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)
        
        

        #OMG!!!!!!!!!! don't overcomlicate man
        #get all the segments in one output buffer which will be sent to the socket
        #one buffer sent out from the socket but multiple sockets


    def send(self, data):
        #data into field struct with data, checksum, seqno ... 
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class MySender(Sender):
    
    TEST_DATA = bytearray([68, 65, 84, 65])  # some bytes representing ASCII characters: 'D', 'A', 'T', 'A'
    msg_size=504 #rember you designed for 512 
    W=5



    def __init__(self,input_file):
        super(MySender, self).__init__()
        
        self.pos_s=0
        self.pos_e=MySender.msg_size
        
        self.buff=input_file
        self.data_to_send=bytearray([0])*1024
        # self.base=None 
        # self.acked=[False]*W

    def get_data_to_snd(object,data):
        pass


    def out(self):
        if(len(self.buff)<self.pos_e):
            self.pos_e=len(self.buff)
            obj=segment(self.buff[self.pos_s:len(self.buff)],self.pos_s)
            return obj.pack()
        else:
            obj=segment(self.buff[self.pos_s:self.pos_e],self.pos_e)
            return obj.pack()


    # def wait_for_ack(self):            
    #         while(True):
    #             ack_b = self.simulator.u_receive()  # receive ACK
    #             ack=get_ack(ack_b)
    #             if ack==self.pos_s:
    #                 self.logger.info(ack)# note that ASCII will only decode bytes in the range 0-127
    #                 break 
    #         return

    def wait_for_ack(self):            
            while(True):
                try:
                    # print "inside wait for ack"
                    ack_b = self.simulator.u_receive()  # receive ACK
                    ack=get_ack(ack_b)
                    if ack==self.pos_e:
                        # print "RECEIVED ACK:", ack
                        self.logger.info("Received ACK {}".format(ack))# note that ASCII will only decode bytes in the range 0-127
                        break
                    else:
                        # print "Received NACK and Resend:"
                        s=unpack(self.data_to_send)
                        # print s.msg
                        # print "sent sequence is: " ,s.sequence_num
                        # print "sent checksum is: " ,s.checksum
                        self.simulator.u_send(self.data_to_send)
                        self.wait_for_ack() 
                        break
                except socket.timeout:
                    self.simulator.u_send(self.data_to_send)
                    self.wait_for_ack()  
                    break   
            # print "pos_e is ", self.pos_e
            self.pos_s+=MySender.msg_size
            self.pos_e+=MySender.msg_size

            return


    def send(self):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        L=len(self.buff)
        # print L
        while (self.pos_e<=L):
            # print "start"
            self.logger.info("inside main while loop")
            self.data_to_send=self.out()
            # print "data to send", self.data_to_send
            self.simulator.u_send(self.data_to_send)  # send data      
            # print "wait for ack"      
            self.wait_for_ack()

    # def send(self):
    #     self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
    #     L=len(self.buff)
    #     while (self.pos_e<L):
    #         data_to_send=self.out()
    #         self.simulator.u_send(data_to_send)  # send data            
    #         while(True):
    #             try:
    #                 ack_b = self.simulator.u_receive()  # receive ACK
    #                 ack=get_ack(ack_b)
    #                 if ack==self.pos_s
    #                     self.logger.info(ack)# note that ASCII will only decode bytes in the range 0-127
    #                     break
    #             except socket.timeout:
    #                 pass



    """def reset(self):
        flag=False
        for i in range(0,W):
            if self.acked[i]=False:
                breaker=i
                self.pos_s+=self.pos_s+i*self.msg_size
                self.pos_e+=self.pos_e+i*self.msg_size
                flag=True
                break
        if flag==False
            self.acked=[False]*W
            return
        else:
            for i in range(W-1,breaker,-1):
                self.acked[W-1-i]=self.acked[i]
            for i in range(breaker,-1,-1):
                self.acked[W-1-i]=False
        return"""




"""        self.logger.info("Sending on port: {} and waiting for ACK from port: {}".format(self.outbound_port.self.inbound_port))
        while(self.pos_s< len(self.buff)-1):
            self.reset()
            try:
                self.simulator.u_send(self.out)
                while(True):
                    ack=unpack(self.simulator.u_receive)
                    if ack.is_corrupt():
                        pass
                    else
                        acks=ack.sequence
                        if acks>= pos_s and acks<=pos_e and acks%msg_size==0: #valid sequence number
                            self.acked[(acks-pos_s)/msg_size]=True
                            if ((acks-pos_s)/msg_size)==0:
                                break
"""



class BogoSender(Sender):
    TEST_DATA = bytearray([68, 65, 84, 65])  # some bytes representing ASCII characters: 'D', 'A', 'T', 'A'

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.get_from_socket()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass


if __name__ == "__main__":
    # test out MySender
    f=open('readfile.txt','r')
    data_f=f.read()
    sndr = MySender(data_f)
    sndr.send()


