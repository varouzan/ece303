
def itofx(n):
    l=[]
    for i in range(7,0,-2):
        a=n//16**i
        n=n-a*(16**i)
        b=n//16**(i-1)
        n=n-b*16**(i-1)
        l.append(a*16+b)
    return l

def fxtoi(l):
    s=0
    for i in range(0,4):
        s=s+(l[i]<<(8*(3-i)))
    return s


class segment(object):

    N=0
    N_ack=0 #find a way to ack the fucking things
    def __init__(self,data,seq=None,check=None,is_ack=False):
        if is_ack==True:
            self.ack=True
            self.msg=data
        else:
            self.ack=False
            self.msg=unicode(data)
            if seq is None:
                segment.N+=1 
                self.sequence_num=segment.N
            else:
                self.sequence_num=seq
        
        if check is None:    
            self.checksum=self.get_checksum_ack()
        else:
            self.checksum=check
        


    def get_checksum(self):

        s=0    
        for i in range(0, len(self.msg), 2):
            if (i+1) < len(self.msg):
                a = ord(self.msg[i]) 
                b = ord(self.msg[i+1])
                s = s + (a+(b << 8))
            elif (i+1)==len(self.msg):
                s += ord(self.msg[i])
            else:
                raise "Something Wrong here"

        # One's Complement
        s = s + (s >> 16)
        s = ~s & 0xffff
        return s

    def get_checksum_ack(self):    
        if self.ack==True:
            l=str(self.msg).decode("ascii")
        else:
            l=self.msg

        s=0
        for i in range(0, len(l), 2):
            if (i+1) < len(l):
                a = ord(l[i]) 
                b = ord(l[i+1])
                s = s + (a+(b << 8))
            elif (i+1)==len(l):
                s += ord(l[i])
            else:
                raise "Something Wrong here"

        # One's Complement
        s = s + (s >> 16)
        s = ~s & 0xffff
        return s        

    def is_corrupt(self):
        if self.get_checksum_ack() == self.checksum:
            return False
        else:
            return True

    def pack(self,pad=512):
        p= bytearray(self.msg,encoding="ascii")+bytearray(itofx(self.checksum))+bytearray(itofx(self.sequence_num))
        p=bytearray([0])*pad+p
        return p


    def pack_ack(self,pad=1016):
        p= bytearray(itofx(self.msg))+bytearray(itofx(self.checksum))
        p=bytearray([0])*pad+p
        return p

def unpack(byte_arr,START=512):
    N=len(byte_arr)
    return segment(byte_arr[START:N-8].decode("ascii"),fxtoi(byte_arr[N-4:N]),fxtoi(byte_arr[N-8:N-4]))

def unpack_ack(byte_arr,START=1016):
    N=len(byte_arr)
    return segment(fxtoi(byte_arr[START:N-4]),None,fxtoi(byte_arr[N-4:N]),True)



def get_ack(byte_arr): ####make a seperate packa and unpack for ack
    ack=unpack_ack(byte_arr)
    # print ack.ack
    if ack.is_corrupt():
        return -1
    else:
        return ack.msg


def check127(l,START=512):
    for i in range(START,len(l)-8):
        if l[i]>127:
            return True
    return False
