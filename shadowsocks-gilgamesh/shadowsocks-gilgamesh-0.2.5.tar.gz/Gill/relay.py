import os
import sys
import time
import errno
import struct
import socket
import select
import traceback
import random, hashlib, logging
from termcolor import cprint,colored
from Gill import loop
from Gill.protocols.ea_protocol import  Enuma,Elish,Chain_of_Heaven, Enuma_len
from Gill.protocols.auth import get_hash, get_config, Encryptor
from Gill.protocols.socks5 import socks5_payload
from Gill.protocols.dns import DNSearcher
from Gill.utils import L

BUF_SIZE = 8096
BUF_MAX = 65535 / 2


test_config = {
    'server_port':13007,
    'method':'aes-256-cfb',
    'hash':'md5',
    'auth':"hello world",
    'password':'passw',
    'port_password':{
        13007:'passw',
        13008:'passw1'
    },
    'local_port':10800,
    'server':'127.0.0.1',
    'dns_local':False
}


tlog = lambda x, y: print("[{}]: {}".format(colored(x, "grey", attrs=['bold']), y))
err = lambda x: print("[{}]: {}".format(colored("failed", "red"), x))
sus = lambda x: print("[{}]: {}".format(colored("ok", "green"), x))
wrn = lambda x: print("[{}]: {}".format(colored("warn", "yellow"), x))



def sus(*args):
    print("[{}]: ".format(colored("ok", "green")) ,*args)
# as sslocal:
# stage 0 SOCKS hello received from local, send hello to local
# stage 1 addr received from local, query DNS for remote
# stage 2 UDP assoc
# stage 3 DNS resolved, connect to remote
# stage 4 still connecting, more data from local received
# stage 5 remote connected, piping local and remote

# as ssserver:
# stage 0 just jump to stage 1
# stage 1 addr received from local, query DNS for remote
# stage 3 DNS resolved, connect to remote
# stage 4 still connecting, more data from local received
# stage 5 remote connected, piping local and remote

STAGE_INIT = 0
STAGE_ADDR = 1
STAGE_UDP_ASSOC = 2
STAGE_DNS = 3
STAGE_CONNECTING = 4
STAGE_STREAM = 5
STAGE_DESTROYED = -1
MSG_FASTOPEN = 0x20000000
STREAM_UP = 0
STREAM_DOWN = 1

# for each stream, it's waiting for reading, or writing, or both
WAIT_STATUS_INIT = 0
WAIT_STATUS_READING = 1
WAIT_STATUS_WRITING = 2
WAIT_STATUS_READWRITING = WAIT_STATUS_READING | WAIT_STATUS_WRITING

BUF_SIZE = 64 * 1024 - 1

# data how to deal with. include EN /DE
# 
EN = 0
DE = 1

GEN_INIT_SEQ = 0
GEN_CHALLENGE = 1
GEN_PASS_IV = 2
GEN_HMAC = 3
GEN_PASS_HASH = 4

VERBOSE_LEVEL = 5

verbose = 1

STAGE_A_INIT = 4
STAGE_A_SEQ = 3
STAGE_A_HMAC = 5
STAGE_A_HASH_I = 6
STAGE_A_FINISH = 7
STAGE_A_LOAD = 8

ERROR_MAX_TIMES = 1

def print_exception(e):
    global verbose
    logging.error(e)
    if verbose > 0:
        import traceback
        traceback.print_exc()


class Connection:

    
    pass_hash_v = None

    # def __init__(self):
    def __init__(self, server, mapper, local_sock, eventloop, config ,is_local = False, dns_resolve= None, dns_local = False,seq='',stat_callback=None):
        self.config = config
        self._server = server
        self.err = err
        self.sus = sus
        self.wrn = wrn
        self.tlog = tlog
        self._downstream_status = WAIT_STATUS_INIT
        self._upstream_status = WAIT_STATUS_READING
        self._data_to_write_to_local = []
        self._data_to_write_to_remote = []
        self._data_cached_from_read = b''
        self._data_to_write_to_remote2 = []
        self.received_len = 0
        self._remote_sock = None
        self._local_sock = local_sock
        self._is_local = is_local
        self._socks5_init = False
        self._dns_local = dns_local
        self._auth = False
        self._loop = eventloop
        self._dns_resolver = dns_resolve
        self._fd_to_handlers = mapper
        self.sec_handler = None
        self._data_check_len = None
        self._stat_callback = stat_callback
        self.last_activity = 0
        self._timeouts = []
        self._connected = False
        self._stage = STAGE_INIT
        #! 
        self.last_auth = None
        self.p_hash = None
        self._tp = None
        self._raddr = None
        self._rport = None
        self._target = None
        self._auth_stage = STAGE_A_INIT 
        self._hash = lambda x: getattr(hashlib,"md5")(x).hexdigest()

        self._error_times = 0
        self._error_len = 0
        self.load_auth = False

        # self._stage = AUTH_INIT
        ok_socks5 = None
        mapper[local_sock.fileno()] = self
        local_sock.setblocking(False)
        local_sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        eventloop.add(local_sock, loop.POLL_OUT | loop.POLL_ERR,
                 self._server)

        if is_local:
            # suthenticate
            self._chosen_server = self.server_config

            
            ## init socks5 and get real data's meta data.
            self._tp, self._raddr, self._rport,ok_socks5 = socks5_payload(local_sock)
            print(self._raddr,self._rport)
            if not ok_socks5:
                self.destroy()

            #! authenticate init . craete remote.
            # print("ds")
            self.authenticate(is_local=True)
            print("Init")

        # if not self._auth:
        #     self.err("auth failed . close connection.")
        #     local_sock.close()
        #     return

        

        

        if ok_socks5:
                self._data_to_write_to_local.append(ok_socks5)

                # self.waiting(STREAM_UP, WAIT_STATUS_WRITING)
                # print("back")
                self.on_continue_write(local_sock)
                
                # local_sock.send(ok_socks5)
                # d = local_sock.recv(4096)
                # sus(self._raddr, ok_socks5, eventloop._impl._fds)
                print(colored("socks5.............. [ok]", "red"))
                self._socks5_init = True
                # sus("D",d)
                # data = local_sock.recv(4096)
                # sus("D:",data)
        
        if self._dns_resolver is None:
            self._dns_resolver = DNSearcher()
                

        if self._dns_local and is_local:
            self._raddr = self._dns_resolver[self._raddr]

        #! init update acitivity
        self.alive()


    def __hash__(self):
        # default __hash__ is id / 16
        # we want to eliminate collisions
        return id(self)

    @staticmethod
    def create(ip, port, server=False, handler=None):
        addrs = socket.getaddrinfo(
            ip, 
            port,
            0,
            socket.SOCK_STREAM,
            socket.SOL_TCP)

        if len(addrs) == 0:
            raise Exception("getaddrinfo failed for %s:%d" % (ip, port))
        af, socktype, proto, canonname, sa = addrs[0]

        remote_sock = socket.socket(af, socktype, proto)
        try:
            # inf(ip)
            # inf(sa)
            if handler:
                # handler._remote_sock = remote_sock
                handler._fd_to_handlers[remote_sock.fileno()] = handler
                

            if not server:
                # remote_sock.connect((ip))
                remote_sock.setblocking(False)
                remote_sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

                
            else:
                remote_sock.setblocking(False)
                remote_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                remote_sock.bind(sa)
                remote_sock.listen(1024)
                
                # self._eventloop.put(remote_sock, IN, self.on_read)
            
            

        except  (OSError, IOError) as e:
            L(e, ip, port,c="red")
            remote_sock.close()
            raise Exception("conneciton build failed")

        # if not server and handler:

        #     try:
        #         remote_sock.connect((ip, port))
        #     except (OSError, IOError) as e:
        #         err("can not connect to." + ip)
        #         err(e)
        #         err(errno_from_exception(e))


        return remote_sock

    @property
    def server_config(self):
        server = self.config['server']
        server_port = self.config['server_port']
        if type(server_port) == list:
            server_port = random.choice(server_port)
        if type(server) == list:
            server = random.choice(server)
        logging.debug('chosen server: %s:%d', server, server_port)
        return server, server_port

    def authenticate(self, is_local=False):
        # exchange and auth. use hmac and hash
        # init encryptor.
        
            
        config = self.config
        hash_f = getattr(hashlib, config['hash'])
        passwd = config['password']
        pass_hash = None
        challenge = None
        pass_iv = None
        

        # if Connection.pass_hash_v is not None and not self._auth:

        #     pass_iv = Connection.pass_hash_v
        #     pass_hash = Chain_of_Heaven(pass_iv, GEN_PASS_HASH, hash_f, config)
        #     if self._is_local:
        #         self._auth_stage = STAGE_A_FINISH
        #         self.sec_handler = Encryptor(pass_hash, config['method'])
        #         self.p_hash = pass_hash[:4]
        #         # self.last_auth = time.time()
        #         self.sus("load authenticate")
        #     else:
        #         self._auth_stage = STAGE_A_LOAD
        #     self.load_auth = True

        # print(is_local)
        if is_local:
            if not self._remote_sock:
                s, p = self._get_server_config
                L("create remote :", s,p, c='green')
                self._remote_sock = Connection.create(s, p, server=False, handler=self)
                try:
                    self._remote_sock.connect((s, p))
                except (IOError ,OSError) as e:
                    if loop.errno_from_exception(e) == \
                                    errno.EINPROGRESS:
                                pass
                else:
                    self._connected = True
                self._loop.add(self._remote_sock,  loop.POLL_ERR | loop.POLL_OUT, self._server)
                # self.waiting(STREAM_UP, WAIT_STATUS_WRITING)
                self.waiting(STREAM_UP, WAIT_STATUS_READWRITING)
                self.waiting(STREAM_DOWN, WAIT_STATUS_READING)
                
                if self.load_auth:
                    L("se")
                    # data = self._local_sock.recv()
                    # self._data_to_write_to_remote = []
                    # L("hehe")
                    self._data_to_write_to_remote = [pass_iv]    
                    self.load_auth = False
                    return


            if self._auth_stage == STAGE_A_INIT:
                # sus("C -- init")
                start_q = Chain_of_Heaven(None, GEN_INIT_SEQ, hash_f, config)
                self._data_to_write_to_remote = [start_q]
                

                #! out this handler waiting from loop to deal with next stage.
                #! waiting connect to server is ok.
                return


            if self._auth_stage == STAGE_A_HMAC:
                # sus("C -- mac")
                try:
                    challenge = self._remote_sock.recv(64)
                except (IOError, OSError) as e:
                    print("auth:",e)
                    return False

                if not challenge:
                        self.destroy()
                        return

                hmac = Chain_of_Heaven(challenge, GEN_HMAC, hash_f, config)
                self.to_sock(self._remote_sock, hmac)
                self._auth_stage = STAGE_A_HASH_I
                return

            if self._auth_stage == STAGE_A_HASH_I:
                # sus("C -- fini")
                try:
                    pass_iv = self._remote_sock.recv(64)
                except (IOError, OSError) as e:
                    print("auth:", e)
                    return False

                if not pass_iv:
                        self.destroy()
                        return
                pass_hash = Chain_of_Heaven(pass_iv, GEN_PASS_HASH, hash_f, config)
                self._auth_stage = STAGE_A_FINISH


            ## 
            #  before finished authenticated, must ensure syn.
            # self._remote_sock.setblocking(True)


            # try:
                # self._remote_sock.send(start_q)

                # challenge = self._remote_sock.recv(64)
                # print("c",end='')
                # hmac = Chain_of_Heaven(challenge, GEN_HMAC, hash_f, config)
                # self._remote_sock.send(hmac)
                # pass_iv = self._remote_sock.recv(64)
                # print("i",end='')
                # pass_hash = Chain_of_Heaven(pass_iv, GEN_PASS_HASH, hash_f, config)

            # except (OSError, IOError) as e:
                # self.err("[local] auth:  IO error")
                # return False
            # except Exception as e:
                # self.err("[local] auth: Chain_of_heaven error")
                # return False

            # self._remote_sock.setblocking(False)
            
        else:

            #  before finished authenticated, must ensure syn.
            # self._local_sock.setblocking(True)
            print("Server ... ")
            try:
                if self._auth_stage == STAGE_A_INIT:
                    sus("[R] C -- init")
                    try:
                        start_q = self._local_sock.recv(64)
                    except (IOError, OSError) as e:
                        print("auth:l:",e)
                        return False
                    
                    if not start_q:
                        self.destroy()
                        return

                    challenge = Chain_of_Heaven(start_q, GEN_CHALLENGE, hash_f,config)
                    self.to_sock(self._local_sock, challenge)
                    self._auth_stage = STAGE_A_HASH_I
                    self._challenge = challenge
                    return
                
                if self._auth_stage == STAGE_A_HASH_I:
                    sus("[R] C -- fini")
                    try:
                        hmac = self._local_sock.recv(64)
                        print("h",end='')
                    except (IOError, OSError) as e:
                        print("auth:l:",e)
                        return False

                    if not hmac:
                        self.destroy()
                        return

                    pass_iv = Chain_of_Heaven(hmac, GEN_PASS_IV, hash_f, config, self._challenge)
                    self.to_sock(self._local_sock, pass_iv)
                    pass_hash = Chain_of_Heaven(pass_iv, GEN_PASS_HASH, hash_f, config)

                    self._auth_stage = STAGE_A_FINISH


                if self._auth_stage == STAGE_A_LOAD:
                    try:
                        pass_hash = self._local_sock.recv(64)
                        print("h",end='')
                    except (IOError, OSError) as e:
                        print("auth:l:",e)
                        return False

                    self.load_auth = False
                    self._auth_stage = STAGE_A_FINISH


            except Exception as e:
                self.err("[remote] auth: Chain_of_heaven error : ")
                print_exception(e)
                return False


        if pass_hash is not None and self._auth_stage == STAGE_A_FINISH  and not self._auth:
            Connection.pass_hash_v = pass_hash
            self.p_hash = pass_hash[:4]
            if not self.sec_handler:
                self.sec_handler = Encryptor(pass_hash, config['method'])
            self.sus("authenticate ok")
            self._auth = True

            if not self._is_local:
                self.waiting(STREAM_DOWN, WAIT_STATUS_READING)
            return True

        return False

    def to_sock(self, sock, data):
        # sus("data out ",len(data), sock == self._remote_sock)
        # write data to sock
        if not data or not sock:
            return False
        uncomplete = False
        try:
            l = len(data)
            s = sock.send(data)
            if s < l:
                data = data[s:]
                uncomplete = True
        except (OSError, IOError) as e:
            err_no = loop.errno_from_exception(e)
            if err_no in (errno.EAGAIN, errno.EINPROGRESS,
                            errno.EWOULDBLOCK):
                uncomplete = True
            else:
                logging.error("to sock %s",e)
                self.err(e)
                self.destroy()
                return False

        if self._remote_sock == sock:
            L("[%d]:" % len(data),"to server" ,c= "yellow")
        elif self._local_sock == sock:
            L("[%d]:" % len(data), "to con",c='yellow', a=['bold'])
            # print( "remote from  local:", sock==self._local_sock, " remote:", sock==self._remote_sock)
        


        if uncomplete:
            err("Go On .....")
            if sock == self._local_sock:
                self._data_to_write_to_local.append(data)
                if self._upstream_status == WAIT_STATUS_INIT:
                    # print("to socket point")
                    self.waiting(STREAM_UP, WAIT_STATUS_READING)
                else: 
                    # print("d wr")   
                    self.waiting(STREAM_DOWN, WAIT_STATUS_WRITING)
            elif sock == self._remote_sock:
                self._data_to_write_to_remote.append(data)
                # print("to socket point wr")
                self.waiting(STREAM_UP, WAIT_STATUS_WRITING)
            else:
                logging.error('write_all_to_sock:unknown socket')
        else:
            if sock == self._local_sock:
                # sus("from write", self._downstream_status == WAIT_STATUS_READING, self._downstream_status == WAIT_STATUS_WRITING)
                self.waiting(STREAM_DOWN, WAIT_STATUS_READING)
                # sus("To Donw read")
            elif sock == self._remote_sock:
                # sus("F waiting read")

                # if self._auth_stage == STAGE_A_INIT:
                    # self.waiting(STREAM_UP, WAIT_STATUS_WRITING)
                self.waiting(STREAM_UP, WAIT_STATUS_READING)
            else:
                logging.error('waiting:error unknown sock.')
        return True


    def from_sock(self, sock, is_remote=False):
        #! this hanppend before authed           !#
        #! ----- authenticate area ----------------
        #! first need to authenticate.
        ilocal = not is_remote
        if not self._auth:
            if sock == self._remote_sock and not is_remote:
                m = self.authenticate(is_local=ilocal)
                # print("m",m)
                    
            elif sock == self._local_sock and is_remote:
                m = self.authenticate(is_local=ilocal)
                
            else:
                m = None

            # print("m",m)
            if m is None:
                return

        #! ------- authenticate  ------------------

        data = None
        real_data = None
        uncomplete = False

            # print( "local from  local:", sock==self._local_sock, " remote:", sock==self._remote_sock)
        try:
            data = sock.recv(BUF_SIZE)
            # if len(data) > 0:
                # print("\nRECV",len(data), colored,"red"))    
            # sus("Got socks' payload")
            
        except (OSError, IOError) as e:
            if loop.errno_from_exception(e) in (errno.ETIMEDOUT, errno.EAGAIN, errno.EWOULDBLOCK):
                
                return




        if not data:
            # if sock == self._remote_sock:
                # sus("close remote reading sock")
            # sus("no data --- destroy this connection.")
            # if self._error_times == 0:
                # self._error_times = time.time()
                # L("[E]:", self._error_times,c='red')
                
            # if time.time() - self._error_times > ERROR_MAX_TIMES:
            L("[destroy]:",time.time(), c='red')
            self.destroy()

            return

        
        if self._remote_sock == sock:
            L("[%d]R:" % len(data),"from ",self._target ,c= "blue")
        elif self._local_sock == sock:
            if not data:
                l = 0
                L("[%d]L:" % l, "from con no data",time.time() - self._error_times, c='blue', a=['bold'], end="\n")
            else:
                l = len(data)
                L("[%d]L:" % l, "from con ",c='blue', a=['bold'])
            # print( "remote from  local:", sock==self._local_sock, " remote:", sock==self._remote_sock)
        


        #! if data recived init the eror values.

        self._error_times = 0

        self.alive(len(data))
        if self._is_local and not self._socks5_init:
            # print("socks5 init. .......")
            ## socks5 init 
            # print(data)
            self._socks5_init = socks5_payload(sock)
            # print("ok")




        if not is_remote:
            ##! deal with  local's read.

            #! deal with data:
            #! if sock is local_sock:
            #!    (hmac (encrypt  data))
            #! elif  sock is server sock:
            #!    (decrypt (checksum (concate data cached_data)))

            if sock == self._local_sock:
                
                #! after authenticate . deal with normal data.
                # print("data",data)
                real_data = self.deal_data(data, EN) # encrypted -> hmac
                if self._stage == STAGE_CONNECTING:
                    self._data_to_write_to_remote.append(real_data)
                elif self._stage == STAGE_STREAM:
                    self.to_sock(self._remote_sock, real_data) # write to remtoe server's remote sock

            elif sock == self._remote_sock:

                answer_data = self.deal_data(data, DE) #  checksum -> decrypt
                if answer_data is not None:
                    tp, info, seq, payload_answer = answer_data
                    self.to_sock(self._local_sock, payload_answer)

                    #! if the data remain bigger than data should be.
                    if self._data_check_len is not None:
                        while self.received_len > self._data_check_len:
                            L("[warrning]","deal with remain data", c="yellow")
                            tp, info, seq, payload_answer = self.deal_data(b'', DE)
                            self.to_sock(self._local_sock, payload_answer)
                return
            else:
                self.err("[local] reading data: unkown socket")

        else:
            ##! deal with remote's read.
            #! 
            # sus("remote from sock")
            if sock == self._local_sock:
                tp, addr, port, payload = self.deal_data(data, DE) # checksum -> decrypt
                # print(addr,port, colored(payload,'red'))
                L("[%d]:" % len(payload), "extract from con",addr, port,c='magenta',a=['bold'])
                # print(self._raddr, addr)
                if payload:
                    if self._remote_sock:# and self._raddr == addr:
                        # sus("write to ")
                        #! check if a remote sock existed then to ensure target sock's addr info is corrupt.
                        self.to_sock(self._remote_sock, payload)
                    else:
                        #! craete a remote's connection to get real tcp data from remote's Network.
                        #! if dns_resolve.local == local:
                        #!      will search host in local point. not in here
                        if not self._dns_local:
                            addr = self._dns_resolver[addr]
                        #! this is real catch data from remote .
                        #! append payload in data_buf ready to send to remote
                        self._data_to_write_to_remote.append(payload)
                        #! create remote sock
                        remote_sock = Connection.create(addr, port, server=False, handler=self)
                        self._target = (addr, port)
                        self._remote_sock = remote_sock
                        #! register sock to loop waiting to deal with.

                        self._loop.add(remote_sock, loop.POLL_OUT | loop.POLL_ERR, self._server)
                        try:
                            remote_sock.connect((addr, port))
                        except (IOError, OSError) as e:
                            if loop.errno_from_exception(e) == errno.EINPROGRESS:
                                sus("--- waiting connect ---")
                        else:
                            sus("--- ready ---")
                        
                        # self._connected = True
                        self._loop.add(self._remote_sock,  loop.POLL_ERR | loop.POLL_OUT, self._server)
                        # self.waiting(STREAM_UP, WAIT_STATUS_WRITING)
                        self.waiting(STREAM_UP, WAIT_STATUS_READWRITING)
                        self.waiting(STREAM_DOWN, WAIT_STATUS_READING)
                        return
                        #! add handler to do 
                        # if not self._is_local:
                        #     #! this is add handler to deal with data in remote server.
                        #     #! if in local server . will add hanlder while create connection.
                        #     self._fd_to_handlers[remote_sock.fileno()] = self
                        
                        #! set action -> reading or writing

            elif sock == self._remote_sock:

                #! got answer from network.
                #! package this data ,then pass it to local.
                real_data = self.deal_data(data, EN)
                L("[%d]:" % len(real_data), "package to con", c='grey',a=['bold'] )
                # print("TO L",len(real_data),colored(self._hash(real_data),'red'))
                self.to_sock(self._local_sock, real_data)
            else:
                self.err("[remote] reading data: unkown socket")




    def deal_data(self, data, data_direction=EN):
        
        if data_direction == DE:
        ##! Decrypt direction .
        #! 1. check data is complate
        #! 2. checksum(data).
        #! 3. decrypt(data). 
            length_complte = False
            now_data = self._data_cached_from_read + data
            cached_data_len = len(now_data)
            de_data = b''
            #! get data's length in this time.
            l = len(data)

            if self._data_check_len is None:
                #! get this package's length.
                self._data_check_len = Enuma_len(now_data)
                # print("\nS: ",colored("%s" %self._data_check_len,"yellow") )
            
            
            
            if cached_data_len >= self._data_check_len:
                de_data = now_data[:self._data_check_len]
                self._data_cached_from_read = now_data[self._data_check_len:]
                self.received_len = cached_data_len - self._data_check_len
                
                #! the remain cached data's length must more than 6 bit.
                #! this is header's length. 
                if len(self._data_cached_from_read) > 6:
                    self._data_check_len = Enuma_len(self._data_cached_from_read)
                else:
                    self._data_check_len = None

                length_complte = True
            else:
                self._data_cached_from_read = now_data
                self.received_len += l


            #! combine all data. may be the size would bigger expectly. 
            print('recv_len',self.received_len, self._data_check_len)
            
            if length_complte:
                ## checksum
                # if checksum()
                tp, raddr, rport, payload = Enuma(de_data,self.p_hash, self.sec_handler.decrypt)
                return tuple([tp, raddr, rport, payload])
            else:
                return None



        else:
        ## Encrypt direction is simple.
        # 1. hmac(data)
        # 2. encrypt(data)
        # 3. combine hmac + en_data
            if self._tp is None:
                self._tp = 1
            if self._raddr is None:
                self._raddr = b"back.back"
                self._rport = 666

            # cprint(self._tp, 'magenta')
            en_data = Elish(self._tp, self._raddr, self._rport, data, self.p_hash, self.sec_handler.encrypt)
            return en_data

    def alive(self, data_len=0):
        self._server.alive(self, data_len)

    def waiting(self, direction, status):
        ## waiting sock to handle
        # deal with break point when data direct break.
        databreak = False
        if direction == STREAM_DOWN:
            if self._downstream_status != status:
                self._downstream_status = status
                databreak = True
        elif direction == STREAM_UP:
            if self._upstream_status != status:
                self._upstream_status = status
                databreak = True


        if databreak:
        # change sock's event status in loop.
            if self._local_sock:
                event = loop.POLL_ERR
                if self._downstream_status & WAIT_STATUS_WRITING:
                # need to: data  > sock
                    # tlog("wating", "l to out")
                    event |= loop.POLL_OUT
                if self._upstream_status & WAIT_STATUS_READING:
                # need to: buf  < sock
                    # tlog("waiting", "l to in")
                    event |= loop.POLL_IN
                self._loop.modify(self._local_sock, event)
            if self._remote_sock:
                event = loop.POLL_ERR
                if self._downstream_status & WAIT_STATUS_READING:
                    # need to: buf  < sock
                    # tlog("waiting", "r to in")
                    event |= loop.POLL_IN
                if self._upstream_status & WAIT_STATUS_WRITING:
                    # need to: data  > sock
                    # tlog("waiting", "r to out")
                    event |= loop.POLL_OUT
                # print(event)
                if self._remote_sock in self._loop._fdmap:
                    self._loop.modify(self._remote_sock, event)
                else:

                    self._loop.add(self._remote_sock, event, self._server)
                    # if self._is_local:
                        #! add hanler to deal with data while reading from remote server .
                        # self._fd_to_handlers[self._remote_sock.fileno()] = self


    def on_error(self, sock):
        if sock == self._remote_sock:
            logging.debug('got remote error')
        else:
            logging.debug('got local error')
        # err("on remote error")
        self.destroy()

    def on_continue_write(self, sock):
        self._stage = STAGE_STREAM
        if sock == self._local_sock:
            if self._data_to_write_to_local:
                data = b''.join(self._data_to_write_to_local)
                self._data_to_write_to_local = []
                self.to_sock(self._local_sock, data)
            else:
                self.waiting(STREAM_DOWN, WAIT_STATUS_READING)
        elif sock == self._remote_sock:
            self._stage = STAGE_STREAM
            if self._data_to_write_to_remote:
                
                # if self._connected or not self._is_local:
                if self._data_to_write_to_remote:
                    data = b''.join(self._data_to_write_to_remote)
                    self._data_to_write_to_remote = []
                    self.to_sock(self._remote_sock, data)
                    
                    #!! this is mean the local conn to serv' chanel connected.
                    if self._auth_stage == STAGE_A_INIT:
                        self._auth_stage = STAGE_A_HMAC
                else:
                    L("ogg")
                # else:
                #     try:
                #         data = b''.join(self._data_to_write_to_remote)
                #         l = len(data)
                #         if self._target and not self._is_local:
                #             s = self._remote_sock.sendto(data, MSG_FASTOPEN, self._target)
                #         else:    
                #             s = self._remote_sock.sendto(data, MSG_FASTOPEN, self._chosen_server)
                #         if s < l:
                #             data = data[s:]
                #             self._data_to_write_to_remote = [data]
                #         else:
                #             self._data_to_write_to_remote = []
                #         self._connected =True
                #     except (OSError, IOError) as e:
                #         if loop.errno_from_exception(e) == errno.EINPROGRESS:
                #             print('send to . connect one time')
                #             self.waiting(STREAM_UP, WAIT_STATUS_READWRITING)
                #         elif eventloop.errno_from_exception(e) == errno.ENOTCONN:
                #             logging.error('fast open not supported on this OS')
                #             L("not connect .",c='red')
                #             self.destroy()
                #         else:
                #             # cprint("Sendto Error","red")
                #             L("[%d]:"% loop.errno_from_exception(e), e, c='red',a=['bold'])
                #             self.destroy()


            else:
                # print("w - rr",)
                self.waiting(STREAM_UP, WAIT_STATUS_READING)
        else:
            err("continue write error: uknow sock.")
            self._loop.remove(sock)
            # self._server._fd_to_handlers[]
            self._server.remove_handler(self)
            if sock.fileno() != -1:
                del self._fd_to_handlers[sock.fileno()]
            sock.close()


    def handle_event(self, sock, event):
        # sus("handle", sock)
        # cprint("handle","green",end='\r')
        remote = not self._is_local
        if sock == self._remote_sock:
            # sus("R")
            if event & (loop.POLL_ERR):
                self.on_error()

            if event & (loop.POLL_IN| loop.POLL_HUP):
                # sus("remote reading\r")
                self.from_sock(sock, is_remote=remote)
                if self._stage == STAGE_DESTROYED:
                    return

            if event & loop.POLL_OUT:
                # sus("remote write\r")
                self.on_continue_write(sock)
                # self.to_sock(sock,)

        elif sock == self._local_sock:
            # sus("L")
            if event & (loop.POLL_ERR):
                self.on_error()
            if event & (loop.POLL_IN | loop.POLL_HUP):
                # sus("local_sock reading\r")
                self.from_sock(sock, is_remote=remote)
                if self._stage == STAGE_DESTROYED:
                    return

            if event & loop.POLL_OUT:
                # sus("local_sock write\r")
                # self.to_sock(sock,)
                self.on_continue_write(sock)


        else:
            self.clear_dirty_sock(sock)
        
    @property
    def _get_server_config(self):
        server = self.config['server']
        server_port = self.config['server_port']
        if type(server_port) == list:
            server_port = random.choice(server_port)
        if type(server) == list:
            server = random.choice(server)
        logging.debug('chosen server: %s:%d', server, server_port)
        return server, server_port


    @property
    def _get_local_config(self):
        server = '127.0.0.1'
        server_port = self.config['local_port']
        return server, server_port

    
    def clear_dirty_sock(self, sock):
        cprint("Clear dirty sock","red")
        self._loop.remove(sock)
        self._server.remove_handler(self)
        if sock.fileno() != -1:
            del self._fd_to_handlers[sock.fileno()]
        sock.close()



    def destroy(self ):
        err("destroy")
        pass
        # if self._stage == STAGE_DESTROYED:
        #     # this couldn't happen
        #     logging.debug('already destroyed')
        #     return
        self._stage = STAGE_DESTROYED
        if self._raddr:
            logging.debug('destroy: %s:%d',
                          self._raddr, self._rport)
        else:
            logging.debug('destroy')
        if self._remote_sock:
            logging.debug('destroying remote')
            self._loop.remove(self._remote_sock)
            del self._fd_to_handlers[self._remote_sock.fileno()]
            self._remote_sock.close()
            self._remote_sock = None
        if self._local_sock:
            logging.debug('destroying local')
            self._loop.remove(self._local_sock)
            del self._fd_to_handlers[self._local_sock.fileno()]
            self._local_sock.close()
            self._local_sock = None
        # self._dns_resolver.remove_callback(self._handle_dns_resolved)
        self._server.remove_handler(self)

class NetNode:

    def __init__(self, config, is_local=False, _stat_callback=None):
        self.config = config
        self.err = err
        self.sus = sus
        self.wrn = wrn
        self.tlog = tlog
        self._fd_to_handlers = {}
        self._is_local = is_local
        if is_local:
            server, server_port = self._get_local_config
        else:
            server, server_port = self._get_server_config
        self._server_sock = Connection.create(server, server_port, server=True)
        self._loop = None
        self._close = False
        self._fd_to_handlers = {}
        self._handler_to_timeouts = {}
        self._timeouts = []
        self._stat_callback = _stat_callback

    def add_to_loop(self, eventloop):
        if self._loop:
            raise Exception("aleady in loop")
        if self._close:
            raise Exception("already closed")
        self._loop = eventloop

        self._loop.add(self._server_sock, loop.POLL_IN| loop.POLL_ERR, self)
        self._loop.add_periodic(self.periodic_call)

    def periodic_call(self):
        if self._close:
            if self._server_sock:
                self._loop.remove(self._server_sock)
                self._server_sock.close()
                self._server_sock = None

        if not self._fd_to_handlers and self._close:
            # print("close")
            logging.debug('stopping')
            self._loop.stop()

        # self._heart_jump()

    def handle_event(self, sock, fd, event):
        if sock:
            logging.debug("fd %d %s" , fd, loop.EVENT_NAMES.get(event, event))

        if sock == self._server_sock:
            if event & loop.POLL_ERR:
                err("handle server error")
                raise Exception("handle Server error")
            try:
                con,_ = sock.accept()
                node = Connection(self,self._fd_to_handlers ,con, self._loop, self.config, is_local=self._is_local)
            except (OSError, IOError) as e:
                error_no = loop.errno_from_exception(e)
                if error_no in (errno.EAGAIN, errno.EINPROGRESS,
                                errno.EWOULDBLOCK):
                    return
                else:
                    L(e)
                    if self._config['verbose']:
                        traceback.print_exc()

        else:
            if sock:
                # print(self._fd_to_handlers)
                handler = self._fd_to_handlers.get(fd, None)

                if handler:
                    handler.handle_event(sock, event)
                else:
                    logging.warn('poll removed fd %d\r', fd )

    def remove_handler(self, handler):
        index = self._handler_to_timeouts.get(hash(handler), -1)
        if index >= 0:
            # delete is O(n), so we just set it to None
            self._timeouts[index] = None
            del self._handler_to_timeouts[hash(handler)]

    def alive(self,handler, data_len=0):
        # heart move onece.
        if data_len and self._stat_callback:
            self._stat_callback(self._listen_port, data_len)

        now = int(time.time())
        if now - handler.last_activity < loop.TIMEOUT_PRECISION:
            # thus we can lower timeout modification frequency
            return
        handler.last_activity = now
        index = self._handler_to_timeouts.get(hash(handler), -1)
        if index >= 0:
            # delete is O(n), so we just set it to None
            self._timeouts[index] = None
        length = len(self._timeouts)
        self._timeouts.append(handler)
        self._handler_to_timeouts[hash(handler)] = length



    @property
    def _get_server_config(self):
        server = self.config['server']
        server_port = self.config['server_port']
        if type(server_port) == list:
            server_port = random.choice(server_port)
        if type(server) == list:
            server = random.choice(server)
        logging.debug('chosen server: %s:%d', server, server_port)
        return server, server_port


    @property
    def _get_local_config(self):
        server = '127.0.0.1'
        server_port = self.config['local_port']
        return server, server_port

    def dead(self, next_tick=False):
        logging.debug('TCP close')
        self._closed = True
        if not next_tick:
            if self._loop:
                self._loop.remove_periodic(self.handle_periodic)
                self._loop.remove(self._server_sock)
            self._server_sock.close()
            for handler in list(self._fd_to_handlers.values()):
                handler.destroy()
