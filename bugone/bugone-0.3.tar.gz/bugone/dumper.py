
from __future__ import print_function

import sys
import getopt
import time
import connector,bugnet


def usage():
    print("bugone-dumper:")
    print(" usage : bugone-dumper [-c host] [-s serial port] [-d hex|log|print]")
    print(" Diplay packet bugNet received in an human readable format")

    
def log(pkt):
    now = time.asctime()
    print("%s => Message [%d] from %d to %d" % (now,pkt.counter,pkt.src,pkt.dst))
    for (s_id,d_id,val) in pkt.values:
        print("- (%d.%d) -> (%d.%d) = %d" % (pkt.src,s_id,pkt.dst,d_id,val))
    

def hexdump(pkt):
    print(pkt)
    cnt = 1
    for k in pkt.bin:
        print("0x%02x" % ord(k),end=' ')
        if (cnt % 16) == 0 : print()
        cnt = cnt + 1
    print()
        
    
def run(con,display_func):
    while 1:
        data = con.receive()
        if data:
            pkt = bugnet.Packet(data)
            display_func(pkt)
            sys.stdout.flush()

def main():            
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:s:d:",)
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)

    cn = None
    display_func= hexdump
    for o, a in opts:
        if o == "-h":
            usage()
            sys.exit()
        elif o=='-c':
            cn = connector.TCPMux(a)
        elif o=='-s':
            cn = connector.Serial(a)
        elif o=='-d':
            if a=='print':
                display_func=print
            if a=='hex':
                display_func=hexdump
            if a=='log':
                display_func=log
        else:
            assert False, "unknow option"

    if cn:
        run(cn,display_func)
            
            
if __name__ == '__main__':
    main()
    
