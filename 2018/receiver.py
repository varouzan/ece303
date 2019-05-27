# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils

from packaging import *


class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10000, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")



class MyReceiver(Receiver):
    ACK_DATA = bytes(1)
    nack=segment(0,None,None,True)
    nack_b=nack.pack_ack()

    def __init__(self):
        super(MyReceiver, self).__init__()

    def receive(self):
        f=open("outfile.txt", 'w')
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            # print"you receive"
            data = self.simulator.u_receive()  # receive data

            if check127(data):
                # print "CORRUPT by check127"
                self.logger.info("Got CORRUPT data from socket")
                self.simulator.u_send(MyReceiver.nack_b)
            else:
                # print "unpack"
                seg=unpack(data)
                # print "sequrnce numner is: ", seg.sequence_num
                if seg.checksum!=seg.get_checksum():
                    # print "IS CORRUPT: ", seg.is_corrupt()
                    # print "CORRUPT by checksum:", seg.checksum
                    # print "COMPUTEd checksum: ", seg.get_checksum()
                    # print "CORRUPTED data is: ", seg.msg 
                    self.logger.info("Got CORRUPT data from socket")
                    self.simulator.u_send(MyReceiver.nack_b)
                else:
                    # print " GOOD checksum:", seg.checksum
                    # print "COMPUTEd checksum: ", seg.get_checksum()
                    self.logger.info("Got data from socket: {}".format(
                        seg.msg))  # note that ASCII will only decode bytes in the range 0-127
                    # print seg.msg
                    f.write(seg.msg)
                    ack=segment(seg.sequence_num,None,None,True)
                    # print "message in ack", ack.msg
                    data_to_send=ack.pack_ack()
                    # print ack.msg , ack.checksum
                    # print "ACK PACKET", data_to_send
                    # print len(data_to_send)
                    self.simulator.u_send(data_to_send)

class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            data = self.simulator.get_from_socket()  # receive data
            self.logger.info("Got data from socket: {}".format(
                data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
            self.simulator.put_to_socket(BogoReceiver.ACK_DATA)  # send ACK


if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = MyReceiver()
    rcvr.receive()
