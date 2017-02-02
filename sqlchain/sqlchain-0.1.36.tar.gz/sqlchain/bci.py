#
#  Blockchain.info compatible API module
#  
import urlparse, cgi, json

from bitcoinrpc.authproxy import AuthServiceProxy
from string import hexdigits

from util import *
from insight import apiHeader, apiTx
from rpc import do_RPC
from encodings import hex_codec

def do_BCI(env, send_resp):
    args = env['PATH_INFO'].split('/')[2:]
    if args[0] == 'q':
        env['PATH_INFO'] = '/rpc/'+args[1]
        return do_RPC(env, send_resp)
        
    get,cur = urlparse.parse_qs(env['QUERY_STRING']), sqc.dbpool.get().cursor()
    send_resp('200 OK', [('Content-Type', 'application/json')])
    if args[0] == "block-height":
        return json.dumps(apiHeader(cur, args[1], 'bci'))
    if args[0] == "rawblock":
        if all(c in hexdigits for c in args[1]):
            return json.dumps(bciBlock(cur, args[1]))
    if args[0] == "rawtx":
        if all(c in hexdigits for c in args[1]):
            return json.dumps(apiTx(cur, args[1], ['raw']) if 'format' in get and get['format'][0] =='hex' else bciTx(cur, args[1]))
    if args[0] in ["address","unspent"]:
        addrs = get['active'][0].split('|') if 'active' in get else args[1].split(',')
        return json.dumps(bciAddr(cur, addrs, args[0] == "unspent", get))
    return []
    
def bciBlockWS(cur, block): # inconsistent websocket sub has different labels
    data = { 'height': int(block), 'tx':[], 'txIndexes':[] }
    cur.execute("select hash from blocks where id=%s limit 1;", (block,))
    for data['hash'], in cur:
        data['hash'] = data['hash'][::-1].encode('hex')
        hdr = gethdr(data['height'], None, sqc.cfg['path'])
        data['blockIndex'] = data['height']
        data['version'] = hdr['version']
        data['time'] = hdr['time']
        data['prevBlockIndex'] = data['height']-1
        data['mrklRoot'] = hdr['merkleroot'][::-1].encode('hex')
        data['nonce'] = hdr['nonce']
        data['bits'] = hdr['bits']        
        cur.execute("select hash from trxs where block_id>=%s and block_id<%s;", (block*MAX_TX_BLK, block*MAX_TX_BLK+MAX_TX_BLK))
        for txhash, in cur:
            data['tx'].append(bciTx(cur, txhash[::-1].encode('hex')))
            data['txIndexes'].append(txhash[::-1].encode('hex'))
        data['nTx'] = len(data['tx'])
        data['reward'] = 0
        for out in data['tx'][0]['out']:
            data['reward'] += out['value']
        data['totalBTCSent'] = 0
        for tx in data['tx']:
            for out in tx['out']:
                data['totalBTCSent'] += out['value']
        del data['tx']
        return data
    return None
    
def bciBlock(cur, blkhash):
    data = { 'hash':blkhash, 'tx':[] }
    cur.execute("select id from blocks where hash=%s limit 1;", (blkhash.decode('hex')[::-1],))
    for blkid, in cur:
        data['height'] = data['block_index'] = int(blkid)
        hdr = gethdr(data['height'], None, sqc.cfg['path'])
        data['ver'] = hdr['version']
        data['time'] = hdr['time']
        data['prev_block'] = hdr['previousblockhash'][::-1].encode('hex')
        data['mrkl_root'] = hdr['merkleroot'][::-1].encode('hex')
        data['nonce'] = hdr['nonce']
        data['bits'] = hdr['bits']
        data['main_chain'] = True
        cur.execute("select hash from trxs where block_id>=%s and block_id<%s;", (blkid*MAX_TX_BLK, blkid*MAX_TX_BLK+MAX_TX_BLK))
        for txhash, in cur:
            data['tx'].append(bciTx(cur, txhash[::-1].encode('hex')))
        data['n_tx'] = len(data['tx'])
        data['fee'] = -(5000000000 >> (data['height'] / 210000))
        for out in data['tx'][0]['out']:
            data['fee'] += out['value']
        return data
    return None

def bciAddr(cur, addrs, utxo, get={}):
    data,tops = [],[]
    single = (len(addrs) == 1)
    for addr in addrs:
        if is_address(addr):
            addr_id = addr2id(addr, cur)
            if addr_id:
                if utxo:
                    from insight import addrUTXOs
                    data.extend(addrUTXOs(cur, addr_id, addr))
                else:
                    hdr,txs = bciAddrTXs(cur, addr_id, addr, get)
                    data.extend(txs)
                    tops.append(hdr)
    if not utxo and single:
        tops[0].update({'txs':data})
    return { 'unspent_outputs':data } if utxo else tops[0] if single else { 'addresses':tops, 'txs':data }

def bciAddrTXs(cur, addr_id, addr, args):
    return {'recd':0},['asasas'] # todo finish this call

def isTxAddrs(tx, addrs):
    for vi in tx['inputs']:
        if 'addr' in vi['prev_out'] and vi['prev_out']['addr'] in addrs:
            return True
    for vo in tx['out']:
        if vo['addr'] in addrs:
            return True
    return False

def bciTxWS(cur, txhash): # reduced data for websocket subs
    data = bciTx(cur, txhash)
    del data['block_height']
    del data['lock_time']
    for vi in data['inputs']:
        if 'prev_out' in vi:
            del vi['prev_out']['tx_index']
            del vi['prev_out']['n']
            del vi['prev_out']['spent']
    for vo in data['out']:
        del vo['tx_index']
        del vo['n']
    return data
        
def bciTx(cur, txhash):
    data = { 'hash':txhash }
    txh = txhash.decode('hex')[::-1]
    cur.execute("select id,txdata,floor(block_id/{0}),ins,txsize from trxs where id>=%s and hash=%s limit 1;".format(MAX_TX_BLK), (txh2id(txh), txh))
    for txid,blob,blkid,ins,txsize in cur:
        hdr = getBlobHdr(int(blob), sqc.cfg['path'])
        data['tx_index'] = int(txid)
        data['block_height'] = int(blkid)
        data['ver'],data['lock_time'] = hdr[4:6]
        data['inputs'],data['vin_sz'] = bciInputs(cur, int(blob), ins)
        data['out'],data['vout_sz'] = bciOutputs(cur, int(txid), int(blob))
        data['time'] = gethdr(data['block_height'], 'time', sqc.cfg['path']) if int(blkid) > -1 else 0
        data['size'] = txsize if txsize < 0xFF00 else (txsize&0xFF)<<16 + hdr[3]
        return data
    return None

def bciInputs(cur, blob, ins):
    data = []
    hdr = getBlobHdr(blob, sqc.cfg['path']) # hdrsz,ins,outs,size,version,locktime,stdSeq,nosigs
    if ins >= 192:
        ins = (ins & 63)*256 + hdr[1] 
    if (ins == 0):  # no inputs
        return [{}],ins # only sequence and script here        
    else:
        buf = readBlob(blob+hdr[0], ins*7, sqc.cfg['path'])
        if len(buf) < ins*7 or buf == '\0'*ins*7: # means missing blob data
            return [{ 'error':'missing data' }],ins
        for n in range(ins):
            in_id, = unpack('<Q', buf[n*7:n*7+7]+'\0')
            cur.execute("select value,addr,addr_id from outputs o, address a where o.id=%s and a.id=o.addr_id limit 1;", (in_id,))
            for value,addr,aid in cur:
                data.append({ 'prev_out':{ 'spent':True, 'type':0, 'n':in_id%MAX_IO_TX, 'value':int(value), 
                              'tx_index':in_id/MAX_IO_TX, 'addr':mkaddr(addr,aid) }})
    return data,ins
    
def bciOutputs(cur, txid, blob):
    data = []
    cur.execute("select o.tx_id,o.id%%{0},value,addr,addr_id from outputs o, address a where o.id>=%s*{0} and o.id<%s*{0} and a.id=o.addr_id;".format(MAX_IO_TX), (txid,txid+1))
    outs = cur.fetchall()
    for in_id,n,value,addr,aid in cur:
        vout = { 'n':int(n), 'value':int(value), 'addr':mkaddr(addr,aid), 'type':0, 'tx_index':txid }
        if in_id:
            vout['spent'] = True
        data.append(vout)
    return data,len(outs)
