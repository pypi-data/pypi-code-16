#-*- coding:utf-8 -*-
import json,logging,re,socket,time
from random import random
from urllib import urlencode
from betcore.exception import UnknownTradeException, DownlineExcpetion
from betcore.browser import BaseBrowser
from betcore.horse.config import COMMENT_CHARS, LANG_MAP, COUNTRY_MAP, TOTE_MAP
from betcore.util import logging_timing, record_trade, getReqBuyNiceTickets,timimng_func,relogin_when_except,getLastWeekDate,get_attr_byres

logger = logging.getLogger(__name__)
class AA_Resource(BaseBrowser):
    def __init__(self,account,db=None,host="",login_host="",proxy_enabled=0,proxy_setting="",source_ip=None,loc_map={},cookies={}):
        BaseBrowser.__init__(self,"aa",source_ip=source_ip,cookies=cookies)
        self.account=account
        self.host,self.login_host=host,login_host
        self.trans_hosts,self.rc_hosts = [],[]
        self.is_first_time_scrap=1
        self.timeout=0.2
        if db is not None: self.db,self.cursor=db,db.connect()
        self.member_profile={}

    def do_login(self):
        logger.info("开始登陆AA网站%s",self.account)
        self.session.headers.pop('Host',None);self.session.headers.pop('Referer',None)
        self.get_res_content('http://%s' %self.host)
        logger.info("提交登陆信息")
        self.session.headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
        rs=self.get_res_by_json('http://%s/web-login/sv/login/' %self.host, {'un':self.account[0],'pw':self.account[1],'cap':'*V_S-DK-l#9LF','':''})
        if rs['login']==True:
            logger.info("pin码登陆")
            rs = self.get_res_by_json('http://%s/web-login/sv/pin/' % self.host, {'pn':self.account[2]})
            logger.info(rs)
            if rs.get('error',None)=='LOGIN_REQUIRED':
                raise DownlineExcpetion(self)
            if rs.get("url").find("reset-password")>0:
                result=0,"require reset passwd"
            else:
                self.get_res_content('http://%s%s' % (self.host,rs.get("url")))
                #取得账号信息.验证是否登录成功
                token=self.load_userid()
                if token:
                    result=1,"login successful"
                else:
                    result=0,"login failed"
        else:
            raise DownlineExcpetion(self)
        return result

    def reset_passwd(self,old_sec_code,new_sec_code):
        "重置密码"
        if old_sec_code==new_sec_code:
            result=self.get_res_by_json("http://%s/web-login/sv/extend-password?tocPlusUrl=null" %self.host)
            logger.info("延长密码:%s",result)
        else:
            result=self.init_login(new_sec_code)
        return result

    def init_login(self,new_sec_code):
        logger.info("开始登陆AA网站%s",self.account)
        self.session.headers.pop('Host',None);self.session.headers.pop('Referer',None)
        self.get_res_content('http://%s' %self.host)
        logger.info("提交登陆信息")
        self.session.headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
        rs=self.get_res_by_json('http://%s/web-login/sv/login/' %self.host, {'un':self.account[0],'pw':self.account[1],'cap':'*V_S-DK-l#9LF','':''})
        if rs['login']==True:
            logger.info("pin码登陆")
            url='http://%s/web-login/sv/pin/' % self.host
            rs=self.get_res_by_json(url, {'pn':self.account[2]})
            logger.info(rs)
            if rs.get('error',None)=='LOGIN_REQUIRED':
                raise DownlineExcpetion(self)
            if rs.get("url").find("reset-password")>0:
                url = 'http://%s/web-login/sv/reset-password-service' %self.host
                rs=self.get_res_by_json(url,{'npi':new_sec_code[1], 'npw':new_sec_code[0], 'cpw':new_sec_code[0], 'tocPlusUrl':'null'})
                logger.info(rs)
        else:
            raise DownlineExcpetion(self)
        logger.info("%s初始化成功" %self.account[0])
        return 1


    def get_member_profile(self):
        host=self.rc_hosts[0] if self.rc_hosts else self.login_host
        url = 'http://%s/player-tote-backend/s/member/profile' %host
        self.session.headers.update({'Host':host,'Referer':'http://%s/web-login/tote/activate' %host})
        profile = self.get_res_by_json(url)
        if not profile.get("error",None)=='LOGIN_REQUIRED':
            self.member_profile={'credit':profile['availableBalance'],'profit':profile['accountProfitLoss'], 'login_token':profile['loginTokenValid'],'user_id':profile["userId"]}
        return self.member_profile

    @relogin_when_except("重登AA...")
    def load_userid(self):
        try:
            profile=self.get_member_profile()
            self.userId = profile["user_id"]
            logger.info("登陆AA成功,userid:%s",self.userId)
            return profile['login_token']
        except:
            raise DownlineExcpetion(self)

    def check_last_week_win(self):
        user_code=self.get_res_by_json("http://%s/partner-server/s/getCurrentUser" %self.rc_hosts[0])['user']['userCode']
        monday,sunday=getLastWeekDate()
        st,end=monday.strftime("%d-%m-%Y"),sunday.strftime("%d-%m-%Y")
        rt=self.get_res_by_json("http://%s/report-server/s/shTaxPayment/publicSHReport?userCode=%s&fromDate=%s&untilDate=%s&viewMode=dollar" %(self.rc_hosts[0],user_code,st,end))
        return round(rt['result']['uplineTote'][0]['balance'],2)

    def get_race_msg(self,pid):
        "获取当前赛事消息"
        url="http://%s/horseracing-server/s/getRaceMessages?pCardId=%s&viewMode=dollar" %(self.rc_hosts[0],pid)
        rt=self.get_res_content(url)
        return rt

    def testServerSpeech(self,servers):
        "检查各个地址抓数据的速度"
        race_list = self.getSummaryRaceList(host=self.rc_hosts[0])
        speech_map = {}
        race_id = None
        for l in race_list:
            if l['timeout'] >= 2:
                card_id = l['card_list'][0][0]
                race_id = race_id if race_id is not None else self.get_race_info( card_id )[0]
                for i in range(10):
                    for s in servers:
                        start = time.time()
                        try:
                            url = 'http://%s/player-tote-backend/s/race/orderlist/wp?raceId=%s&currency=RMB&mode=DOLLAR&h=%s' %(s, race_id, time.time())
                            self.get_res_content(url)
                            elapsed = abs((time.time() - start)*1000)
                        except:
                            elapsed = 10000
                        elapsed_list = speech_map.get(s,[])
                        elapsed_list.append(int(elapsed))
                        speech_map.update({s:elapsed_list})
                break
        for k,v in speech_map.items():
            speech_map.update({k:(socket.getaddrinfo(k, 80)[0][4][0],sum(v)/len(v))})
        return sorted(speech_map.iteritems(), key=lambda x:x[1][1])

    @relogin_when_except("重登AA...")
    def getSummaryRaceList(self, content=None,host=None):
        logger.info("开始从AA网站上获取赛事列表")
        try:
            url = 'http://%s/player-tote-backend/s/card/list?lang=%s' %(self.rc_hosts[0] if self.rc_hosts else host,self.lang)
            if content is None:
                if self.is_first_time_scrap:
                    rt=self.get_res(url)
                    if rt is None:
                        raise DownlineExcpetion(self)
                    self.is_first_time_scrap=0
                else:
                    rt=self.get_res(url,retry=0,timeout=self.timeout)
                rt=rt.json() if rt is not None else []
            else:
                rt=json.loads(content)
            race_list = []
            for e in rt:
                race= {"timeout":"", "country":"", "location":"", "race_date":"","card_list":[],"tote_list":[],"race_type":""}
                card_list,_,timeout, country_and_type,_,date,_,_,location,_,_ = e
                country_and_type = country_and_type.strip()
                country, race_type = re.findall( r'([\w ]+)-?([\w ]*)', country_and_type)[0]
                country, race_type = country.strip(), race_type.strip()
                race_type = "Horse" if len(race_type)==0 else race_type
                race["country"] = COUNTRY_MAP.get(country,country)
                race["timeout"] = timeout
                race["location"] = re.findall( r'([-\w/.() ]+)', location)[0].strip()
                race["card_list"] = card_list
                tl = []
                for c in card_list:
                    toteName = "FC" if c[3]=="Q"  else TOTE_MAP.get(c[3],c[3])
                    tl.append("%s_%s" %(TOTE_MAP.get(c[1],c[1]), toteName))

                race["tote_list"] = tl
                race["race_date"] = time.strftime( "%d-%m-%Y", time.strptime(time.ctime(date/1000)))
                race["race_type"] = race_type
                race_list.append( race )
            #logger.info("已成功从AA上获取赛事条数：%s" % len(race_list))
            return race_list
        except:
            logger.exception(rt)
            if rt.content.find("internal error")>0:
                logger.info("AA无赛事")
                return []
            else:
                logger.info(rt)
                logger.info(rt.content)
                raise DownlineExcpetion(self)

    def saveSummaryRaceList(self, race_list):
        if race_list:
            self.cursor.execute( "delete from races where belong='%s'" %self.site )
            insertSql =  '''insert into races( belong, timeout, country, location, race_date, card_list, tote_list, race_type ) values("%s", %d, "%s", "%s", "%s", "%s", "%s","%s")'''
            for r in race_list:
                self.cursor.execute( insertSql %(self.site, int(r["timeout"]),r["country"],r["location"],r["race_date"],r["card_list"],r["tote_list"],r["race_type"]))
            logger.info("已成功更新保存AA赛事信息")
            return 1
        else:
            logger.info("抓取AA赛事信息失败")
            return 0


    def process_wp_data(self,key,race_info,chance_volume_floor,fake_tickets):
        insertSql =  '''insert into wp_eatbet( key, race_num, horse_num, win, place, discount, lwin, lplace, bet_type, location, tote_code,belong )
                       values( "%s", %d, %d, %d, %d, %s, %s, %s, "%s" , "%s", "%s", "%s")'''
        loc,tc,rn=race_info
        @logging_timing("完成保存AA彩池赌票吃票数据到数据库")
        def save_wp(content):
            belist = content.split("#TOTE_WIN_PLACE.EAT#")
            bet_data = []
            eat_data = []
            if len(belist) == 2:
                cursor = self.db.connect()
                for l in belist[0].split("\r\n"):
                    if len(l) > 0 and not l.isspace() and not l[0] in COMMENT_CHARS:
                        bet_data.append( [float(n) for n in l.split()])
                for l in belist[1].split("\r\n"):
                    if len(l) > 0 and not l.isspace() and not l[0] in COMMENT_CHARS:
                        eat_data.append( [float(n) for n in l.split()])
                wpNiceTickets,wNiceTickets,pNiceTickets = getReqBuyNiceTickets( bet_data,"RQB",chance_volume_floor,fake_tickets)
                for bd in wpNiceTickets+wNiceTickets+pNiceTickets:
                    cursor.execute( insertSql %('%s' %str(key),rn,bd[0],bd[1],bd[2],bd[3],bd[4],bd[5],"EAT",loc,tc,self.site))

                wpNiceTickets,wNiceTickets,pNiceTickets = getReqBuyNiceTickets( eat_data,"RQE",chance_volume_floor,fake_tickets)
                for ed in wpNiceTickets+wNiceTickets+pNiceTickets:
                    cursor.execute( insertSql %('%s' %str(key),rn,ed[0],ed[1],ed[2],ed[3],ed[4],ed[5],"BET" ,loc,tc,self.site))
                return 1
        return save_wp

    @logging_timing("全部完成从AA抓取独赢位置挂单数据")
    @relogin_when_except("重登AA...")
    def collect_wp(self,key,race_info,chance_volume_floor,fake_tickets):
        content = timimng_func("完成抓取AA上的数据",self.get_res_content,'http://%s/player-tote-backend/s/race/orderlist2/wp?raceId=%s&cardId=%s&currency=RMB&mode=DOLLAR&version=0&_=%s' %(self.rc_hosts[0], key[1],key[0],random()))
        self.process_wp_data(key,race_info,chance_volume_floor,fake_tickets)(content)
        return 1



    @record_trade("AA交易")
    @relogin_when_except("重登AA...")
    def buyWP(self,key,race_num,ticket):
        "赌或吃独赢/位置"
        horse_num, win, place, discount, lwin, lplace, type=ticket
        if key is not None:
            cardId = key[0]
            data = '''{"list":[{"selNum":"%s","win":%s,"place":%s,"price":%s,"lwin":%s,"lplace":%s}],"type":"%s","cardId":%s,"raceNum":"%s","saveOnMatch":%s}''' %( horse_num ,win,place,discount/100.0,lwin/10.0,lplace/10.0,type,cardId ,race_num,"true")
            url = 'http://%s/player-tote-backend/s/order/placeOrderWP?%s&_=%s' %(self.trans_hosts[0],urlencode({'data':data}),time.time())
            rt = self.get_res_content(url,timeout=5)
            if rt.find("login")>0:
                logger.info(rt)
                raise DownlineExcpetion(self)
            if rt.find("errors")>0:
                logger.info(rt)
                return "REJECTED",0
            try:
                rs = json.loads(rt)['result'][0]
            except KeyError:
                logger.exception(rt)
                raise
            status = rs['status']
            volume = max(win, place)
            if status == "FULL":
                logger.info("%s在AA上%s票,  场次:%s,马:%s, 独赢:%s, 位置:%s, 折扣:%s, 极限:%s/%s" %(self.account[0],LANG_MAP[type], race_num, horse_num, win, place, discount, lwin, lplace))
            elif status == "PARTIAL":
                logger.info( rs )
                etc=rs.get('etc',None)
                if etc is not None:
                    exec(etc.replace('null','0'))
                    volume = matched_amt
                    logger.info("%s在AA%s票只能部分成交，票数:%s" %(self.account[0],LANG_MAP[type],volume))
                else:
                    volume = int(volume/2)
                    logger.info("%S在AA%s票只能部分成交，估计票数:%s" %(self.account[0],LANG_MAP[type],volume))
            elif status== "REJECTED":
                volume=0
                logger.info("%s在AA%s票失败:%s" %(self.account[0],LANG_MAP[type],rt))
                if rt.find("INVALID_USER_STATUS") > 0:
                    logger.info("用户状态无效:%s" %rt)
                    raise UnknownTradeException()
            else:
                logger.info("未知错误:%s" %rt)
                raise UnknownTradeException()
            return status,volume
        else:
            return "REJECTED",0

    def peddingWP(self, key, bet_type,race_num, pedding_seq):
        result=[]
        try:
            if key is not None:
                for psub_seq in [ pedding_seq[i:i+25] for i in range(0,len(pedding_seq),25)]:
                    ps=[]
                    for p in psub_seq:
                        hn,w,p,dis,lw,lp=p
                        ps.append('{"selNum":"%s","win":%s,"place":%s,"price":%s,"lwin":%s,"lplace":%s,"row":2}' %(hn,w,p,dis/100.0,lw/10.0,lp/10.0))
                    cardId = key[0]
                    data = '''{"list":[%s],"type":"%s","cardId":%s,"raceNum":%s,"isWin":false,"isPlace":false,"isAll":false}''' %(",".join(ps) ,bet_type,cardId ,race_num)
                    url = 'http://%s/player-tote-backend/s/order/placeOrderWP?%s&_=%s' %(self.trans_hosts[0],urlencode({'data':data}),random())
                    res=self.get_res_by_json(url,timeout=5)
                    sub_res=res['result']
                    for r in sub_res:
                        exec(r.get("etc")).replace('null', '0')
                        result.append((r['status'],order_id))
        except NameError:
            logger.info(sub_res)
        except KeyError:
            logger.info(res)
        return result

    def cancel_pedding_wp(self,order_id_list):
        url = 'http://%s/player-tote-backend/s/order/cancelOrder' %self.trans_hosts[0]
        id_seq=",".join([str(e) for e in order_id_list])
        logger.info("AA撤单id:%s" %id_seq)
        rt = self.get_res(url,{'idSequence':id_seq}).text
        if rt.find("OK") >0:
            return 1
        elif rt.find("ORDER_NOT_EXIST") >0:
            logger.info("order_id:%s,%s" %(id_seq,rt))
            return 0
        else:
            logger.info(rt)
            return -1

    def get_tote_price(self,key,race_num):
        "根据cardId获取最近的一场比赛的赔率"
        url = "http://%s/player-tote-backend/s/race/getTotePrices?raceId=%s" %(self.rc_hosts[0],key[1])
        rt=self.get_res_content(url)
        try:
            rt=json.loads(rt)["totes"]
        except ValueError:
            logger.info(rt)
            return {}
        else:
            tote_prices={int(k):(0 if float(v['winPrice'])==199.8 else float(v['winPrice']),0 if float(v['placePriceMax'])==199.8 else float(v['placePriceMax']))for k,v in rt.items() if not v['scratched']}
            return  tote_prices

    def get_race_info(self, cardId, race_num=None):
        "根据cardId获取最近将要举行的一场比赛的raceId"
        try:
            url='http://%s/player-tote-backend/s/combo/main?cardId=%s' %(self.rc_hosts[0] if self.rc_hosts else self.rc_hosts[0], cardId)
            rt=self.get_res_content(url)
            rt=rt.split("_preload_")
            race_list_by_card = json.loads(rt[1][1:-2].replace("'","\""))
            race_id,race_num=-1,-1
            for r in race_list_by_card["/race/listByCard"]["raceList"]:
                if r['status']=='OPEN':
                    race_id,race_num=r['id'],r['number']
                    break
            pid=get_attr_byres(rt[2],'"pid":',",")
            return race_id,race_num,pid
        except DownlineExcpetion:
            raise DownlineExcpetion(self)
        except:
            logger.info(rt)
            logger.exception( "carid:%s,race_num:%s" %(cardId,race_num))
            raise DownlineExcpetion(self)

    def getAllRaceIdByCard(self,cardId):
        "获取一个cardId对应的所有计划举行赛事的raceId列表"
        url = "http://%s/player-tote-backend/s/card/listScratchContenderByCard?cardId=%s" %(self.rc_hosts[0], cardId)
        raceId, race_num, pid = self.get_race_info(cardId)
        raceList = json.loads(self.get_res_content(url))["raceList"]
        rl = []
        for r in raceList:
            if r["raceNumber"] >= race_num:
                rl.append( r )
        logger.debug("cardId为%s对应的所有计划举行赛事的raceId列表为%s"  %(cardId, raceList))
        return rl

    def getWPTrans(self,key,race_num):
        "查询一场比赛的交易情况"
        cardId,raceId,pid = eval(key) if isinstance(key, basestring) else key
        rt = self.get_res_by_json("http://%s/report-server/s/trans/mine?raceId=%s&cardId=%s&physicalRaceId=%s&quinellaOnly=false" %(self.rc_hosts[0], raceId, cardId, pid))
        matchlist = rt["groups"]["matchedList"]
        match= []
        for e in matchlist:
            if "marketAbbr" in e and e["market"] == "TOTE_WIN_PLACE":
                bet_type,horse,win,place,discount,lwin,lplace = e["betType"],e["selectionNumber"],e["volume"] if e["winLimit"] else 0, e["volume"] if e["placeLimit"] else 0,e["discount"],e["winLimit"],e["placeLimit"]
                match.append((horse,bet_type.upper(),win,place,discount,lwin,lplace))
        unmatchlist = rt["groups"]["unmatchedList"]
        unmatch=[]
        for e in unmatchlist:
            if "marketAbbr" in e and e["market"] == "TOTE_WIN_PLACE":
                order_id,bet_type,horse,win,place,discount,lwin,lplace = e["id"],e["betType"],e["selectionNumber"],e["volume"] if e["winLimit"] else 0, e["volume"] if e["placeLimit"] else 0,e["discount"],e["winLimit"],e["placeLimit"]
                unmatch.append((horse,order_id,bet_type.upper(),win,place,discount,lwin,lplace))

        return match,unmatch
    def getWPSummaryTransHistByDate(self, date):
        "根据日期获取该天的交易总账"
        rt=json.loads(self.get_res_content("http://%s/player-tote-backend/s/transHist/main?userId=%s" %(self.rc_hosts[0], self.userId)))["past"]["TOTE_WINPLACE"]
        trans=[]
        for th in rt:
            logger.info(th)
            d=time.strftime("%d-%m-%Y", time.strptime(time.ctime(th['date']/1000)))
            if d == date:
                country, race_type, location =  re.findall(r'(?:([\w]+) - )?([\w ]+), ([\w ]+)',th["cardName"])[0]
                cty = race_type if country=="" else country
                rt = "Horse" if country=="" else race_type
                trans.append({"country":COUNTRY_MAP.get(cty,cty),"location":location.strip(), "race_type":rt, "toteName":"AU" if th["tote_code"]=="TB" else th["tote_code"], "volume":th["volume"], "tax":th["tax"], "profit":th["profit"],"key":(th["cardId"],d), "belong":"AA"})
        return trans

    def getWPTransHistByKey(self, key):
        "根据CardId查询每场比赛的明细账目"
        detail=json.loads(self.get_res_content("http://%s/player-tote-backend/s/transHist/detail?userId=%s&cardId=%s&marketTypeGroup=TOTE_WINPLACE" %(self.rc_hosts[0], self.userId, key)))
        transDetail=[{"race_num" :e["raceNumber"],"horse_num":int(e["selectionNumber"]),"bet_type":e["betType"], "volume":e["volume"],"discount":e["discount"],"lwin":e["winLimit"],"lplace":e["placeLimit"],"profit":e["balance"],"position":int(e["position"]),"winDividend":e["winDividend"], "placeDividend":e["placeDividend"] } for e in detail["transactionDetails"]]
        return transDetail
if __name__ == '__main__':
    pass
