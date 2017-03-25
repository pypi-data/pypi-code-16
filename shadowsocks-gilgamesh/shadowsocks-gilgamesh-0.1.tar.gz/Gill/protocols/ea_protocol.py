import os, random
from struct import unpack, pack
from Gill.utils import err, sus, to_bytes

__all__ = ["Enuma_len", "Enuma", "Elish",'test_config']

"""
typedef struct {
    u_char tp;  // 1 byte
    u_int8_t addr_len; // 1byte
    u_int16_t port; // 2 byte
    u_int16_t payload_len; // 2byte
    u_char * addr;
    u_char * payload;
    u_int32_t checksum; // 4 byte  
    u_int32_t seq; // 4 byte

} EA;

hash(start) -> server 
challent -> local

hash(challent || hash(passwd))  -> server 
server verify
init_password_iv -> local

will set p_hash = hash(init_password_iv || password)


challenge  4 byte
hash(start) 4 byte
init_password_iv  16 byte
"""


def Chain_of_Heaven(data, stage, hash, config, challenge=None):
    if stage == 1:
        k, = unpack("I", data[:4])
        if chr(k) in config['auth']:
            return os.urandom(4)
        else:
            err("start error")
            return False
    elif stage == 2:
        if challenge:
            if data == hash(challenge + hash(to_bytes(config['password'])).digest()).digest():
                return os.urandom(16)
            else:
                err("challenge error")
                return False
        else:
            err("no challenge found")
            return False
    elif stage == 3:
        return hash(data + hash(to_bytes(config['password'])).digest()).digest()
    elif stage == 4:
        return hash(data + to_bytes(config['password'])).digest()
    elif stage == 0:
        start = random.choice(config['auth'])
        return pack("I", ord(start))
    else:
        err("what the fuck")
        raise Exception("no such stage {}".format(stage))



def Enuma_len(data, seq=False):
    tp = data[0]
    if tp != 1 and tp != 9:
        return False
    pay_len,= unpack(">I", data[1:5])
    tp_l = 1
    pl_l = 4
    checksum_l = 4
    if not seq:
        return pay_len + tp_l + checksum_l + pl_l
    return pay_len + tp_l + checksum_l  + pl_l + 2

def Enuma(data, p_hash, decrypt,int_seq=None ):

    """
this is a elish payload . if tp == 1
__________________________________________________________________________________
| tp 1 | addr-payload-len 4 |           encrypted_payload n         | checksum 4 |
----------------------------------------------------------------------------------

the detail of  encrypted_payload .
---------------------------------------------------------------------------------- 
| addr_len 1 | port 2 | payload_l 2 |   addr al   |           payload pl         |
----------------------------------------------------------------------------------


if tp == 9:
__________________________________________________________________________________
| tp 9  | payload-len 2 |           encrypted_payload n             | checksum 4.|
----------------------------------------------------------------------------------

encrypted_payload n
---------------------------------------------------------------------------------- 
| info_len 1 |  seq 2 | payload_l 2  |   info     |           payload            |
----------------------------------------------------------------------------------



the checksum is a simple algo to verify package's complety.
the detail like:

checksum = tp
for var in [al, port, pl, p_hash]:
    checksum ^= var

    """
    sus(".... Enuma : %d ...." % len(data))
    if not data:
        err(data)
        return False

    if len(data) < 16:
        err("len wrong :{}".format(data))
        return False

    tp = data[0]
    check = tp

    apl, = unpack('>I', data[1:5])
    # print(apl)
    addr_payload_en = data[5:5+apl]
    addr_payload = decrypt(addr_payload_en)

    al = addr_payload[0]
    port, = unpack('>H', addr_payload[1:3])

    pl, = unpack('>H',addr_payload[3:5])


    check ^= al    
    check ^= port
    check ^= pl

    addr = addr_payload[5:5+al]
    payload = addr_payload[5+ al:]

    # print(al, pl, addr, payload)
    checksum = data[5+apl: 5 + apl + 4]
    checksum_int, = unpack("I", checksum)
    
    seq_int = None
    if int_seq:
        seq = data[6 + addr_len + payload_len + 4: 6 + addr_len + payload_len + 8]
        seq_int, = unpack("I", seq)
        if int_seq != seq_int:
            err("sequce error, may attack by reply")
            return False
        sus(">>>>>> {} ok ".format(int_seq))
    
    # sus("-- check --> {}".format(list(checksum)))
    if checksum_int == check ^ unpack("I", p_hash)[0]:

        return tp, addr, port, payload
    err("ea decode err")
    return False

def Elish(tp, addr, port, payload, p_hash, encrypt,int_seq=None):
    """
this is a elish payload .
__________________________________________________________________________________
| tp 1 | addr-payload-len 2 |           encrypted_payload n         | checksum 4 |
----------------------------------------------------------------------------------

the detail of  encrypted_payload .
---------------------------------------------------------------------------------- 
| addr_len 1 | port 2 | payload_l 2 |   addr al   |           payload pl         |
----------------------------------------------------------------------------------

the checksum is a simple algo to verify package's complety.
the detail like:

checksum = tp
for var in [al, port, pl, p_hash]:
    checksum ^= var

    """
    sus(".... Elish : %d ...." % len(payload))
    check = tp
    pl = len(payload)
    al = len(addr)
    content = pack("B", tp)
    #1
    addr_payload = pack("B",al)
        #1
    addr_payload += pack(">H",port)
        #3
    addr_payload += pack(">H",pl)
        #5
    addr_payload += addr
    addr_payload += payload
    addr_payload_en = encrypt(addr_payload)

    apl = len(addr_payload_en)

    content += pack(">I", apl)
    #5
    content += addr_payload_en

    check ^= al
    check ^= port
    check ^= pl
    check ^= unpack("I", p_hash)[0]
    # sus(list(checksum))
    # sus("-- uncheck --> {}".format(list(pack("I", check))))

    content += pack("I", check)
    #7 + apl 
    if int_seq:
        content += pack("I", int_seq)
    # int_seq
    # print(content)
    return content


