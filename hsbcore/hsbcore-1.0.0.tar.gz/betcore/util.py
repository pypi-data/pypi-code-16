#-*- coding=utf-8 -*-#
import os,sys,inspect,socket,math,threading
import logging,paramiko
import calendar,datetime
from string import translate,maketrans
from time import time,sleep
from cStringIO import StringIO
from betcore.exception import  ChanceOverException
def current_file_directory():
    """get directory of current script, if script is built
    into an executable file, get directory of the excutable file"""
    path = os.path.realpath(sys.path[0])        # interpreter starter's path
    if os.path.isfile(path):                    # starter is excutable file
        path = os.path.dirname(path)
        return os.path.abspath(path)            # return excutable file's directory
    else:                                       # starter is python script
        caller_file = inspect.stack()[1][1]     # function caller's filename
        return os.path.abspath(os.path.dirname(caller_file))# return function caller's file's directory

def get_attr_byres(res,st_char,end_char=None):
    st_idx=res.find(st_char)+len(st_char)
    if end_char is None:
        return res[st_idx:]
    else:
        return res[st_idx:res.find(end_char,st_idx)]


def logging_timing(msg=""):
    def _logging_timing(func):
        "计算并记录一个函数的执行时间到日志文件"
        def wrapper(*args, **kwargs):
            start = time()
            result = func(*args, **kwargs)
            elapsed = abs((time() - start)*1000)
            logging.getLogger(__name__).info("%s执行时间:[%d毫秒]" % (msg, elapsed))
            return result
        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        return wrapper
    return _logging_timing

def timimng_func(msg,func,*args,**kwargs):
    start = time()
    result = func(*args, **kwargs)
    elapsed = abs((time() - start)*1000)
    logging.getLogger(__name__).info("%s执行时间:[%d毫秒]" % (msg, elapsed))
    return result

def record_trade(msg=""):
    def _record_trade(func):
        "计算并记录一个函数的执行时间到日志文件"
        def wrapper(*args, **kwargs):
            start = time()
            bookTime = datetime.datetime.now()
            result,volume = func(*args, **kwargs)
            elapsed = abs((time() - start)*1000)
            logging.getLogger(__name__).info("%s执行时间:[%d毫秒]" % (msg, elapsed))
            return result,volume,bookTime,elapsed
        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        return wrapper
    return _record_trade
def relogin_when_except(msg=""):
    "当函数出现异常时，自动重登"
    def do_func(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except ChanceOverException:
                raise ChanceOverException()
            except:
                logging.getLogger(__name__).exception(msg)
                args[0].do_login()
                result = func(*args, **kwargs)
            return result
        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        return wrapper
    return do_func


def lvol_decider(st_time,org_volume, hedge_sentinel, delay_section,volume_section,mult_vol_section,mult_chance_section):
    """根据由收集数据到发现机会再到对冲的时间间隔来决定对冲的数量,根据机会的票量决定放大的倍数"""
    delay = (time() - st_time)*1000
    logging.getLogger(__name__).info( "总延迟:%sms" %delay)
    lvol = 0
    for idx, d in enumerate(delay_section):
        if delay <= d:
            lvol = volume_section[idx]
            if idx==0:
                for i,cv in enumerate(mult_chance_section):
                    if org_volume>=cv:
                        lvol=lvol*mult_vol_section[i]
                        break
            break
    lvol = 5 if hedge_sentinel and lvol>0 else lvol
    logging.getLogger(__name__).info( "此次对冲极限额度为:%s" %lvol)
    return lvol


def divParam( paramSeq, divLen ):
    "将数组分成几个元祖,例如 ：list = [1,2,3,4,5,6,7,8,9] ,divParam[list,3] =========>(1,2,3)、(4,5,6)、(7,8,9)"
    totalTp = len(paramSeq)/divLen
    for i in range(totalTp):
        yield paramSeq[i*divLen:(i+1)*divLen]


def getReqBuyNiceTickets(raw_data,req_bet_type,vol_lmt=20,fake_tickets={},fake_time_delay=0.5):
    "获取要求吃或者要求赌的票的最优票集合"
    wpnt,wnt,pnt=[],[],[]
    bet_type="BET" if req_bet_type=="RQE" else "EAT"
    for d in raw_data:
        if d[1]>=vol_lmt and d[2]>=vol_lmt:
            nt=wpnt
        elif d[1]>=vol_lmt and d[2]==0:
            nt=wnt
        elif d[1]==0 and d[2]>=vol_lmt:
            nt=pnt
        else:continue
        is_fake=0
        for ftk,ftv in fake_tickets.setdefault(bet_type,{}).items():
            fvol,ftime=ftv
            if ftk==(d[0],d[3],d[4],d[5]) and fvol>=max(d[1],d[2]) and time()-ftime<=fake_time_delay:
                logging.getLogger(__name__).info( "排除假单:%s" %str(d))
                fake_tickets[bet_type][ftk]=(max(d[1],d[2]),time())
                is_fake=1
                break
        if is_fake:continue
        lnt = nt[-1] if nt else None
        if lnt is None or lnt[0] != d[0]:
            nt.append(d)
        else:
            if req_bet_type=="RQE":
                if lnt[3] <= d[3] and ( lnt[4] < d[4] or lnt[5] < d[5]):
                    nt.append(d)
            elif req_bet_type=="RQB":
                if lnt[3] >= d[3] and ( lnt[4] > d[4] or lnt[5] > d[5]):
                    nt.append(d)
    return wpnt, wnt, pnt
def lw_wp_content_parser1(rt,prefix="<pre id=BET_DATA>",endfix="</pre>"):
    "用于转换抓取回来的独赢位置彩池数据"
    is_success=1
    try:
        rt = rt[rt.index(prefix) + len(prefix): rt.rindex(endfix)]
    except ValueError:
        logging.getLogger(__name__).info("查询不到独赢位置彩池数据%s" %rt)
        is_success=-1 if rt.find("logout")>0 else 0
        rt=""
    data=[]
    for l in StringIO(translate(rt,maketrans('!/', '  '))).readlines():
        if len(l) > 0 and not l.isspace() and not l[0]=='#' :
            e=[float(n) for n in l.split()[1:]]
            if e: data.append(e)
    return data,is_success


def lw_wp_content_parser2(rt,prefix='"pendingData":"',endfix='"}'):
    "用于转换抓取回来的独赢位置彩池数据"
    logger=logging.getLogger(__name__)
    is_success=1
    if rt.find("rateLimit")>=0:
        logger.info("查询不到独赢位置彩池数据%s" %rt)
        is_success=0
        data=[]
    else:
        try:
            rt=rt[rt.find(prefix)+len(prefix):rt.find(endfix)]
        except ValueError:
            logger.info("查询不到独赢位置彩池数据%s" %rt)
            is_success=-1 if rt.find("logout")>0 else 0
            rt=""
        data=[[float(e) for e in l.split()[1:]] for l in StringIO(rt.replace("!","").replace("/"," ").decode('string_escape')).readlines() if len(l) > 0 and not l.isspace() and not l[0]=='#']
    return data,is_success

def lw_wp_content_parser(rt,prefix="<pre id=BET_DATA>",endfix="</pre>"):
    return lw_wp_content_parser2(rt) if rt.find('"pendingData":"')>0 else lw_wp_content_parser1(rt,prefix,endfix)

class RSCollectThread(threading.Thread):
    def __init__(self,contentParserCallback, browser, url,name="rs-thread" ):
        super(RSCollectThread,self).__init__(name=name)
        self.data = []
        self.url = url
        self.broser = browser
        self.callback = contentParserCallback

    def run(self):
        rt = self.broser.get_res_content(self.url)
        self.data = self.callback(rt)


def isServerOnline(ip, port):
    "检查一个服务器是否在线,需提供服务器的ip和用作检测开放的端口"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout( 1 )
    try:s.connect((ip, port));return 1
    except:return 0
    finally:s.close()


def moneyStrToNumber(moneyStr):
    '将类似于 $50,385.45 ($8,378.50) 的字符串转换成数字'
    if moneyStr.find("(") > -1 :
        return float(moneyStr.replace("$","").replace(",","").replace("(","").replace(")",""))*-1
    else:
        return float(moneyStr.replace("$","").replace(",",""))

def today():
    return datetime.datetime.today().strftime("%d-%m-%Y")

def getMondayDate():
    "获取当前日期的上一个星期一的日期，如果今天是星期一，则日期是今天"
    lastMonday = datetime.datetime.today()
    oneday = datetime.timedelta(days=1)
    while lastMonday.weekday() != calendar.MONDAY:
        lastMonday -= oneday
    return lastMonday

def getLastWeekDate():
    "获取当前日期的上一个星期的星期一和星期日的日期"
    lastMonday = datetime.datetime.today() - datetime.timedelta(days=7)
    oneday = datetime.timedelta(days=1)
    while lastMonday.weekday() != calendar.MONDAY:
        lastMonday -= oneday
    return lastMonday,lastMonday + datetime.timedelta(days=6)


def getDays(startDate,endDate):
    "获取两个日期之间的所有日期"
    sd=datetime.datetime.strptime(startDate,"%Y-%m-%d")
    ed=datetime.datetime.strptime(endDate,"%Y-%m-%d")
    oneday=datetime.timedelta(days=1)
    li=[]
    while ed >= sd:
        li.append(sd)
        sd += oneday
    return li

def wpmakeup(rc,key,rn,hn,win,place,lw,lp):
    "补单"
    bt,v=("BET",max(win,place)) if (win>0 or place>0) else ("EAT",min(win,place))
    logmsg="独赢+位置" if (lw>0 and lp>0) else "独赢" if lp==0 else "位置"
    site="lw" if isinstance(key[0], basestring) else "aa"
    if  v>0:
        vol=math.ceil(float(v)/5)*5 if site=="lw" else (v if v > 5 else 5)
        logging.getLogger(__name__).info("在%s补单赌%s票%s" %(site,vol,logmsg))
        st,tn_vol= rc.buyWP(rn, hn, key, vol if lw>0 else 0, vol if lp>0 else 0,  100, lw, lp, bt)[0:2]
    if v<=-5:
        vol=(abs(int(v))/5)*5 if site=="lw" else abs(int(v))
        logging.getLogger(__name__).info( "在%s补单吃%s票%s" %(site,vol,logmsg))
        st,tn_vol= rc.buyWP(rn, hn, key, vol if lw>0 else 0, vol if lp>0 else 0,  76, lw, lp, bt)[0:2]
    win= tn_vol if lw>0 else 0
    place= tn_vol if lp>0 else 0
    return site,bt,win,place

def patch_single(rc,key,rn,hn,w,p,lw,lp):
        "当对冲时，出现吃不到货或者赌不到货时需要补单"
        assert w >0 or p >0 or w <= -5 or p <=-5
        win,place = w,p
        trans_seq=[]
        if win>0 and place>0:
            "首先尝试用独赢+位置补"
            v=min(win,place)
            logging.getLogger(__name__).info("马匹%s,有单边:(%s,%s),尝试独赢+位置补单%s票" %(hn,win,place,v))
            site,bt,wv,pv = wpmakeup(rc,key,rn,hn,v,v,lw,lp)
            if wv>0:trans_seq.append((site,hn,bt,wv,pv,lw,lp))
            win=win-wv;place=place-pv
        if win>0:
            logging.getLogger(__name__).info("马匹%s,有单边:(%s,%s),尝试独赢补单%s票" %(hn,win,place,win))
            site,bt,wv,pv = wpmakeup(rc,key,rn,hn,win,0,lw,0)
            if wv>0:trans_seq.append((site,hn,bt,wv,0,lw,0))
            win=win-wv;place=place-pv
        if place>0:
            logging.getLogger(__name__).info("马匹%s,有单边:(%s,%s),尝试位置补单%s票" %(hn,win,place,place))
            site,bt,wv,pv = wpmakeup(rc,key,rn,hn,0,place,0,lp)
            if pv>0:trans_seq.append((site,hn,bt,0,pv,0,lp))
            win=win-wv;place=place-pv
        if win<=-5 and place <= -5:
            v=max(win,place)
            logging.getLogger(__name__).info("马匹%s,有单边:(%s,%s),尝试独赢+位置补单%s票" %(hn,win,place,v))
            site,bt,wv,pv = wpmakeup(rc,key,rn,hn,v,v,lw,lp)
            if wv>0:trans_seq.append((site,hn,bt,wv,pv,lw,lp))
            win=win+wv;place=place+pv
        if win<=-5:
            logging.getLogger(__name__).info("马匹%s,有单边:(%s,%s),尝试独赢补单%s票" %(hn,win,place,win))
            site,bt,wv,pv = wpmakeup(rc,key,rn,hn,win,0,lw,0)
            if wv>0:trans_seq.append((site,hn,bt,wv,0,lw,0))
            win=win+wv;place=place+pv
        if place<=-5:
            logging.getLogger(__name__).info("马匹%s,有单边:(%s,%s),尝试位置补单%s票" %(hn,win,place,place))
            site,bt,wv,pv = wpmakeup(rc,key,rn,hn,0,place,0,lp)
            if pv>0:trans_seq.append((site,hn,bt,0,pv,0,lp))
            win=win+wv;place=place+pv
        return (win,place),trans_seq


class SSH2:
    "用于连接linux主机的SSH"
    def __init__(self, host, username="root", passwd="",port=22 ):
        self.client= paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ip=host
        try:self.client.connect(host,port,username,passwd,timeout=5)
        except:
            print "SSH服务尚未开启"
            raise

    def __enter__(self):return self

    def cmd(self, cmd):
        "一般命令"
        try:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            return stdout.readlines()
        except : print "在%s执行远程命令%s失败" %(self.ip,cmd)

    def long_cmd(self,cmd):
        "长命令"
        chan = self.client.invoke_shell()
        if(chan.send_ready()):chan.send(cmd);sleep(1);
        chan.close()

    def put(self,local_file, remote_path):
        "上传文件"
        try:
            sftp=paramiko.SFTPClient.from_transport(self.client.get_transport())
            sftp.put(local_file,remote_path)
        except Exception: raise

    def __exit__(self, type, value, traceback):self.client.close()

class EatBetDataCollectThread(threading.Thread):
    def __init__(self,name="EatBetDataCollectThread",args=()):
        threading.Thread.__init__(self, name=name)
        self.data = []
        self.rc,self.key, self.race_num, self.location, self.tote_code,self.min_hedge_volume = args

    def run(self):
        self.data = self.rc.getWPEatBegData(self.key,self.race_num)
        self.rc.saveWPEatBegData(self.data, self.location, self.tote_code,self.min_hedge_volume)


if __name__ == '__main__':
    pass
