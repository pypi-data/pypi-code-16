#-*- coding:utf-8 -*-
import datetime,time,logging,re,socket,string
import execjs,pytesseract
from cStringIO import StringIO
from random import random
from PIL import Image
from lxml import etree
from lxml.cssselect import CSSSelector
from lxml.etree import XMLSyntaxError
from betcore.exception import DownlineExcpetion, UnknownTradeException, UserBlockedExcpetion, SysMaintenanceExcpetion
from betcore.browser import BaseBrowser
from betcore.horse.config import LANG_MAP, RACE_TYPE_MAP, COUNTRY_MAP
from betcore.util import logging_timing, record_trade, getReqBuyNiceTickets, relogin_when_except, lw_wp_content_parser, current_file_directory, getLastWeekDate, get_attr_byres

logger = logging.getLogger(__name__)
def switch2png(imgbuf):
    im=Image.open(StringIO(imgbuf),'r')
    im = im.convert("L")
    im = im.point(lambda i:i > (255 - 80) and 255)
    output = StringIO()
    im.save(output,"PNG")
    output.seek(0)
    return Image.open(output)

class LW_Resource(BaseBrowser):
    def __init__(self, account, db=None,host='',login_host="",proxy_enabled=0,proxy_setting="",source_ip=None,loc_map={},cookies={}):
        BaseBrowser.__init__(self,"lw",source_ip=source_ip,cookies=cookies)
        self.account=account
        self.host,self.login_host=host,login_host
        self.main_domain=".".join(self.host.split(".")[1:])
        self.trans_hosts,self.rc_hosts = [],[]
        self.lm = loc_map
        if db is not None: self.db,self.cursor=db,db.connect()
        self.proxy_enabled,self.proxy_setting=proxy_enabled,proxy_setting
        "记录安全验证服务器的二级域名"
        self.secureList = ["securemx3","securebd2","secure","secure2k6"]
        nodejs=execjs.get("Node")
        self.js=nodejs.compile(open("%s/mask.js" %current_file_directory(),"r").read() + open("%s/text4.js" %current_file_directory(),"r").read())

    def login_step1(self):
        self.session.headers.update({"Referer":"http://%s/" %self.login_host,"Host":self.login_host})
        logger.info("用户%s开始登陆citibet" %self.account[0])
        valid = self.get_valid()
        code = self.get_code()
        secHost = self.secureList[0]
        encode_pwd = self.js.call('mask', "voodoo_people_%s%s" %(self.account[0],self.js.call('mask',self.account[1])))
        postdata = {'uid2': '', 'pass2': '', 'code2': '', 'uid': self.account[0], 'pass': self.js.call('mask','%s%s%s'%(valid,code,encode_pwd)), 'code': code, 'valid': valid,'lang':'EN'}
        rt=self.get_res_content("http://%s.%s/login" %(secHost,self.main_domain), postdata)
        return rt

    def login_step2(self,rt):
        secHost = self.secureList[0]
        try:
            while 1:
                logger.info(rt)
                if rt.find("error")>0:
                    raise UserBlockedExcpetion()
                if rt.find("downtime.jsp")>0:
                    raise SysMaintenanceExcpetion()
                if rt.find("pass.jsp")>0:
                    result=0,"require reset passwd"
                    break
                if rt.find("validate_pin.jsp")>0:
                    logger.info("提交pin码信息")
                    rt = self.get_res_content("http://%s.%s/validate_pin.jsp" %(secHost,self.main_domain))
                if rt.find("Validate PIN")>0:
                    r = re.findall(r'r[12]=\'([\w-]+)\'',rt)
                    pin = self.js.call('mask',"pin_%s%s" %(self.account[0],self.account[2]))
                    encode_pin = self.js.call('mask',"%s%s%s"%(r[0],r[1],pin))
                    rt=self.get_res_content("http://%s.%s/verifypin" %(secHost,self.main_domain), {"code":encode_pin})
                if rt.find("terms.jsp")>0:
                    logger.info("%s登陆长城成功" %self.account[0])
                    result=1,"login successful"
                    break
                if len(rt)==0 or rt.find("location.replace")>0 or rt.find("login.jsp")>0:
                    raise DownlineExcpetion(self)
        except DownlineExcpetion:
            logger.exception("登陆出错，暂停2秒后重新一次登陆")
            time.sleep(2)
            self.do_login()
        except IndexError:
            logger.exception("")
            raise IndexError()
        return result

    def do_login(self):
        rt=self.login_step1()
        return self.login_step2(rt)

    def reset_passwd(self,old_sec_code,new_sec_code):
        if old_sec_code==new_sec_code:
            secHost = self.secureList[0]
            old_pass=self.js.call('encode',self.js.call('mask',self.account[1]))
            change_pass="".join(list(self.account[1])[::-1])
            new_pass=self.js.call('encode',self.js.call('mask',change_pass))
            logger.info("提交登陆信息")
            rt=self.get_res_content("http://%s.%s/pass.jsp" %(secHost,self.main_domain),{'oldPass':old_pass,'pass1':new_pass,'pass2':new_pass})
            if rt.find("validate_pin.jsp")>0:
                #todo还需还重置密码到以前的密码
                logger.info("密码延期成功成功")
        else:
            self.init_login(new_sec_code)
        return 1

    def init_login(self,new_sec_code):
        rt=self.login_step1()
        secHost = self.secureList[0]
        if rt.find("pass.jsp")>0:
            pass_data = {"oldPass":self.js.call('encode',self.js.call('mask',self.account[1])),
            "pass1":self.js.call('encode',self.js.call('mask',new_sec_code[0])),
            "pass2":self.js.call('encode',self.js.call('mask',new_sec_code[0]))}
            self.session.post("http://%s.%s/pass.jsp" %(secHost,self.main_domain), pass_data).text
            pin_data = {"code":new_sec_code[1],"code2":new_sec_code[1]}
            rt=self.session.post("http://%s.%s/verifypin" %(secHost,self.main_domain), pin_data).text
            if rt.find("terms.jsp")>0:
                logger.info("%s初始化成功",self.account[0])
                result=1
            else:
                logger.info("%s初始化失败:%s",self.account[0],rt)
                result=0
        else:
            logger.info("%s初始化失败:%s",self.account[0],rt)
            result=0
        return result


    def get_valid(self):
        "获取登陆所需的valid code"
        if self.proxy_enabled:self.session.proxies = {"http": "http://%s" %self.proxy_setting}
        while 1:
            rt = self.get_res_content("http://%s/" %self.login_host)
            logger.info(rt)
            m = re.findall(r'(\?[\w-]+)', rt)
            rt = self.get_res_content("http://%s/%s" %(self.login_host, m[0]))
            rt = self.get_res_content('http://%s/_index.jsp' %self.login_host)
            if rt.find("Page Not Found!")>0 or rt.find("Try again later")>0:
                time.sleep(1)
                continue
            else:
                break
        try:
            valid = re.findall( r'id="valid" value="([\w-]+)"', rt)[0]
        except IndexError:
            logger.exception(rt)
            raise DownlineExcpetion(self)
        logger.info("获取valid:%s" %valid)
        self.session.proxies={}
        return valid

    def get_code(self):
        "获取并解析验证码"
        while 1:
            r = self.session.get("http://%s/img.jpg?%s" %(self.login_host, random())).content
            code=pytesseract.image_to_string(switch2png(r)).strip()
            if len(code)==5:break
        logger.info("获取验证码:%s" %code)
        return code

    def get_member_profile(self,content=None):
        url = "http://%s/acc_profile_overview.jsp" %self.rc_hosts[0]
        rt = self.get_res_content(url) if content is None else content
        "信用额度"
        try:
            m = re.findall(r'<th>Available Balance</th>.*?<td>.*?\$([\d,.]+)',rt,re.S)
            availableBalance = float(m[0].replace(",",""))
            "输赢"
            m = re.findall(r'<th>Current Profit/Loss</th>.*?<td>(<span)?.*?\$([\d,.]+)\)?.*?</td>',rt,re.S)
            if len(m[0]) == 2:
                currentProfit = float(m[0][1].replace(",",""))
                currentProfit = currentProfit if len(m[0][0])==0 else  currentProfit*-1
            else:
                currentProfit = 0
            return {"credit":availableBalance,"profit":currentProfit}
        except IndexError:
            logger.info(rt)
            raise

    def testServerSpeech(self,servers):
        "检查各个地址抓数据的速度"
        race_list = self.getSummaryRaceList(host=self.rc_hosts[0])
        self.saveSummaryRaceList(race_list)
        self.cursor.execute( "select card_list from races where timeout >=2 and belong='%s'" %self.site )
        nature_key =  eval(self.cursor.fetchone()[0])[0]
        m = re.findall( r'/playerhk\.jsp\?race_type=(\d+\w?)&race_date=([\d-]+)', nature_key)
        key = m[0][1], m[0][0]
        race_num = self.get_race_num(nature_key)
        speech_map = {}
        for i in range(10):
            for s in servers:
                start = time.time()
                try:
                    req_eat_url = "http://%s/eatdata?race_date=%s&race_type=%s&rc=%s&m=HK&c=2&_%s" %(s,key[0], key[1], race_num, random())
                    self.session.get(req_eat_url).content
                    elapsed = abs((time.time() - start)*1000)
                except:
                    elapsed = 10000
                elapsed_list = speech_map.get(s,[])
                elapsed_list.append(int(elapsed))
                speech_map.update({s:elapsed_list})
        for k,v in speech_map.items():
            speech_map.update({k:(socket.getaddrinfo(k, 80)[0][4][0],sum(v)/len(v))})
        return sorted(speech_map.iteritems(), key=lambda x:x[1][1])


    @relogin_when_except("重登长城...")
    def check_last_week_win(self):
        monday,sunday=getLastWeekDate()
        st,end=monday.strftime("%d-%m-%Y"),sunday.strftime("%d-%m-%Y")
        un=self.account[0].replace("sub","")
        rt=self.get_res_content("http://%s/member/report/pay_report_fin_v3.jsp?start=%s&end=%s&uid=%s" %(self.rc_hosts[0],st,end,un))
        rt=get_attr_byres(rt,'<div id="racing_container" style="">','<br/>')
        tree = etree.parse(StringIO(rt), etree.HTMLParser())
        rt=CSSSelector("div")(CSSSelector('td')(CSSSelector('table tr')(tree)[2])[-1])[0]
        profit = float(("-" +rt.xpath("span")[0].text if rt.text==None else rt.text).replace("$","").replace("(","").replace(")","").replace(",",""))
        return profit

    def get_race_timeout(self):
        logger.debug("开始更新保存citibet赛事开赛时间信息")
        url = "http://%s/datastore?getdata=y&cardtimer=y&x=%s" %(self.rc_hosts[0], random())
        rt = self.get_res_content(url)
        try:
            time = rt[rt.index("<pre id=txtTimerAllCard>")+len("<pre id=txtTimerAllCard>"):rt.rindex(";</pre>")]
        except ValueError: raise DownlineExcpetion(self)
        m = re.findall( r'(\d\d_\d\d_\d\d\d\d)_(\d+)=(\d+)', time)
        return {'%s_%s' %(race_id,date.replace("_","-")):int(timeout) for date, race_id, timeout in m}


    @relogin_when_except("重登长城...")
    def getSummaryRaceList(self, content=None,host=None):
        "从长城上获取赛事列表：距离开赛时间,国家，地点，开赛日期，彩池列表,赛事类型"
        logger.info("开始从citibet获取赛事列表")
        rc_host = self.rc_hosts[int(random()*len(self.rc_hosts))] if host is None else host
        url = "http://%s/playerhk.jsp" %rc_host
        if content is None:
            rt=self.get_res_content(url)
        else:rt = content
        if rt.find("No Race")>0:return []
        idxstart = rt.find(r'<div id="oldcarddata" style="display:none">')
        idxend = rt.find(r'<!--end oldcarddata -->')
        doc = rt[idxstart:idxend]
        race_list = []
        try:
            tree = etree.parse(StringIO(doc), etree.HTMLParser())
            sel = CSSSelector('div.cardcontaioner')
            for e in sel(tree):
                cntsel = CSSSelector('dd.country_name')
                country  = COUNTRY_MAP.get(cntsel(e)[0].text,cntsel(e)[0].text)
                rctypesel = CSSSelector('dd.rc_type span')
                race_type = rctypesel(e)[0].text
                expsel = CSSSelector('div.expendline')
                if  len(expsel(e)) == 1:
                    race_list.append(self.parseSummaryRaceInfo(e, country, race_type))
                else:
                    for es in expsel(e):
                        race_list.append(self.parseSummaryRaceInfo(es, country,race_type))
        except XMLSyntaxError:
            logger.info(rt)
            logger.info("抓取赛事信息错误....")
            raise DownlineExcpetion(self)
        race_timeout_map=self.get_race_timeout()
        for r in race_list:
            r['timeout']=race_timeout_map.get('%s_%s' %(r['race_id'],r['race_date']),9999)
        return race_list

    def parseSummaryRaceInfo(self, element, country, race_type):
        "解析赛事列表相关信息"
        locsel = CSSSelector('dd.location_name')
        try:
            location = locsel(element)[0].text.strip()
        except:
            html = etree.tostring(locsel(element)[0])
            location = html[html.index('<span class="InRun_icon"/>')+len('<span class="InRun_icon"/>'):html.index("</dd>")].strip()

        raceidre = r'cati(\d\d_\d\d_\d\d\d\d)_(\d+)[a-z]'
        m = re.findall(raceidre, CSSSelector('dd.rc_time')(element)[0].get("icardd") )
        race_date,raceId=m[0]
        race_date=race_date.replace("_","-")

        card_list = element.findall(".//ul/li/a")
        cardurlre = r'/\w+\.jsp\?race_type=\w+&race_date=[\w-]+'
        cl,tl = [],[]
        for c in card_list:
            cardurl = re.findall( cardurlre, c.get("onclick"))[0]
            tote_name = "AU" if c.text == "TB" else c.text
            tote_name = "FC" if tote_name == "Q" else tote_name
            toteClass = c.getparent().get("class")
            toteClass = toteClass.split("_")[0]
            toteClass = tote_name if toteClass == "on" else toteClass
            cl.append( cardurl )
            tl.append( "%s_%s" %(toteClass, tote_name))
        try:
            location.replace(u'\xa0'," ")
        except KeyError:
            logger.debug("---KeyError---location:--%s" % location)

        return {"timeout":"", "country":country, "location":location.replace(u'\xa0'," "), "race_date":race_date, "card_list":cl, "tote_list":tl, "race_id":raceId, "race_type" :RACE_TYPE_MAP[race_type]}

    def saveSummaryRaceList(self, race_list):
        if race_list:
            self.cursor.execute( "delete from races where belong='%s'" %self.site )
            insertSql =  '''insert into races(belong, timeout, country, location, race_date, card_list, tote_list, race_type ) values("%s", %d, "%s", "%s", "%s", "%s", "%s","%s")'''
            for r in race_list:
                self.cursor.execute( insertSql %(self.site, r["timeout"],r["country"],r["location"],r["race_date"],r["card_list"], r["tote_list"], r["race_type"]))
            logger.info("已成功更新保存LW赛事信息")
            return 1
        else:
            logger.info("抓取LW赛事信息失败")
            return 0


    @relogin_when_except("重登长城...")
    def get_race_num(self, cardurl):
        url = 'http://%s%s' %(self.rc_hosts[0], cardurl)
        rt = self.get_res_content(url)
        if rt.find("rcs")>0:
            try:
                m = re.findall(r'rcs.push\((\d+)', rt)
                return int(m[0])
            except IndexError:
                return 100
        else:
            logger.info("在获取比赛场次时掉线？？")
            logger.info(cardurl)
            raise DownlineExcpetion(self)

    def get_race_msg(self,race_date,race_type,rc):
        "获取当前赛事信息"
        url = 'http://%s/datastore?race_date=%s&race_type=%s&rc=%s&time=%s' % (self.rc_hosts[0],race_date,race_type,rc,time.time())
        rt = self.get_res_content(url)
        return rt

    def process_wp_data(self,req_bet_type,key,race_info,lw_wp_content_parser,chance_volume_floor,fake_tickets):
        insertSql =  '''insert into wp_eatbet( key, race_num, horse_num, win, place, discount, lwin, lplace, bet_type, location, tote_code, belong )
                       values( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

        bet_type="EAT" if req_bet_type=="RQB" else "BET"
        @logging_timing("完成保存长城彩池%s数据到数据库" %("求赌" if req_bet_type=="RQB" else "求吃"))
        def save_wp(content):
            data,is_success=lw_wp_content_parser(content,"<pre id=%s_DATA" %("BET" if req_bet_type=="RQB" else "EAT"))
            wpNiceTickets,wNiceTickets,pNiceTickets=getReqBuyNiceTickets( data,req_bet_type,chance_volume_floor,fake_tickets)
            insert_data = [(self.formatKey(*key), race_info[2], bd[0], bd[1], bd[2], bd[3], bd[4], bd[5], bet_type,race_info[0],race_info[1],"lw" ) for bd in wpNiceTickets+wNiceTickets+pNiceTickets]
            cur=self.db.connect()
            cur.executemany( insertSql,insert_data)
            return is_success
        return save_wp

    @logging_timing("全部完成从长城抓取独赢位置数据")
    @relogin_when_except("重登长城...")
    def collect_wp(self,key,race_info,chance_volume_floor,fake_tickets):
        rc_host = self.rc_hosts[0]
        beturl = "http://%s/betdata?race_date=%s&race_type=%s&rc=%s&m=HK&c=3&lu=0" %(rc_host,key[0],key[1],race_info[2])
        bet_process =self.process_wp_data("RQB",key,race_info,lw_wp_content_parser,chance_volume_floor,fake_tickets)
        eaturl = "http://%s/eatdata?race_date=%s&race_type=%s&rc=%s&m=HK&c=3&lu=0" %(rc_host,key[0],key[1],race_info[2])
        eat_process =self.process_wp_data("RQE",key,race_info,lw_wp_content_parser,chance_volume_floor,fake_tickets)
        urls = [beturl,eaturl];processors=[bet_process,eat_process]
        return self.fetch_and_process_parallel(urls,processors)

    @logging_timing("完成从长城抓取独赢位置数据")
    def collect_wp_by_type(self,key,race_num,bet_type="RQE"):
        race_date,race_type = key
        rc_host = self.rc_hosts[0]
        url = "http://%s/%sdata?race_date=%s&race_type=%s&rc=%s&m=HK&c=2&_%s" %(rc_host,{"RQE":"eat","REB":"bet"}[bet_type],race_date, race_type, race_num, random())
        rt=self.get_res_content(url)
        data,is_success=lw_wp_content_parser(rt,"<pre id=%s_DATA" %{"RQE":"EAT","REB":"BET"}[bet_type])
        return data,is_success


    def formatKey(self, race_date, race_type):
        "转化成符合数据库格式的字符串key"
        return "('%s','%s')" %( race_date, race_type)

    @record_trade("LW交易")
    @relogin_when_except("重登长城...")
    def buyWP(self,key,race_num,ticket):
        "赌或吃独赢/位置"
        horse_num,win,place,discount,lwin,lplace,type=ticket
        if key is not None:
            map1={"BET":"bookings","EAT":"bets"}
            map2={"BET":"book","EAT":"bet"}
            race_date, race_type = key
            url = 'http://%s/%s?t=frm&race=%s&horse=%s&win=%s&place=%s&amount=%s&limit=%s/%s&type=%s&race_type=%s&race_date=%s&show=%s&post=1&rd=%s' %(self.trans_hosts[0],map1.get(type),race_num,horse_num,int(win),int(place),discount,lwin,lplace,map2.get(type),race_type,race_date,race_num,random())
            rt = self.get_res_content(url)
            if rt.find("too fast")>0:
                logger.info("交易过快，睡眠90ms后重试")
                time.sleep(0.09)
                rt = self.get_res_content(url)
            status="REJECTED"
            volume = 0
            if rt.find( "fully transacted" ) > 0:
                logger.info("%s在长城%s票,场次:%s,马:%s, 独赢:%s, 位置:%s, 折扣:%s, 极限:%s/%s" %(self.account[0],LANG_MAP[type], race_num, horse_num, int(win), int(place), discount, lwin, lplace))
                status= "FULL"
                volume = max( win, place)
            elif rt.find("partially transacted")>0:
                w, p = re.findall(r'Win:.*<strong>(\d+)</strong>.*Plc:.*<strong>(\d+)</strong>', rt)[0]
                status= "PARTIAL"
                w, p = int(w), int(p)
                volume = max( w, p)
                logger.info("%s在长城%s票只能部分成交，票数:%s" %(self.account[0],LANG_MAP[type],volume))
            else:
                logger.info("%s在长城%s票失败,原因:%s" %(self.account[0],LANG_MAP[type],rt))
                if rt.find("top.logout")>0:
                    raise DownlineExcpetion(self)
                if rt.find("An error has occurred")>0 or rt.find("Insufficient credit") > 0 or rt.find("Suspended")>0:
                    logger.info("用户%s:%s" %(self.account[0],rt))
                    raise UnknownTradeException()
            return status, volume
        else:
            return "REJECTED",0

    def peddingWP(self, race_num, horse_num, key, win, place, discount, lwin, lplace, type="BET"):
        "赌或吃独赢/位置"
        if key is not None:
            logger.info("开始挂单")
            map1={"EAT":"bookings","BET":"bets"}
            race_date, race_type = key
            url = 'http://%s/%s?t=frm&race=%s&horse=%s&win=%s&place=%s&amount=%s&l_win=%s&l_place=%s&race_type=%s&race_date=%s&wptck=1&show=%s&post=2&rd=%s' \
                %(self.trans_hosts[0],map1.get(type),race_num,horse_num,int(win),int(place),discount,lwin,lplace,race_type,race_date,race_num,random())
            rt = self.get_res_content(url)
            logger.info(rt)

    def getWPTrans(self, key, race_num):
        "查询一场比赛的交易情况"
        race_date, race_type = key
        url = "http://%s/datastore?q=n&l=x&race_date=%s&race_type=%s&rc=%s" %(self.rc_hosts[0], race_date, race_type, race_num)
        rt = self.get_res_content(url)
        try:
            start = rt.index("<pre id=TRANS_DATA>") + len("<pre id=TRANS_DATA>")
            end = rt.index("</pre>", start)
            trans = rt[start:end]
        except ValueError:
            raise DownlineExcpetion(self)
        if trans.find("[") == -1:
            raise DownlineExcpetion(self)
        m = re.findall( r'[WP]+#([BE])#(\d+)#(\d+)#([\d.]+)#([\d.]+)#([\d.]+)#([\d.]+)/([\d.]+)', trans)
        trans = []
        for e in m:
            bet_type,race_num, horse,win,place,discount,lwin,lplace = e
            trans.append((horse,"BET" if bet_type == "B" else "EAT",float(win),float(place),float(discount),float(lwin),float(lplace)))
        return trans,[]

    def getWPSummaryTransHistByDate(self, date):
        "根据日期获取该天的交易总账"
        url = "http://%s/history.jsp?uid=%s" %(self.rc_hosts[0],self.user)
        rt = self.get_res_content(url)
        tree = self._getTransHistByDate(rt, date)
        transhist = []
        if not tree == None:
            sel = CSSSelector( 'table.max_report tr')
            for e in sel(tree)[1:]:
                tds = CSSSelector("td")(e)
                onclick = tds[5].xpath("span/@onclick")[0]
                start = onclick.find("'")
                end = onclick.find("'",start+1)
                detailurl = onclick[start+1:end]
                profit = ("-" +tds[4].xpath("span")[0].text if tds[4].text==None else tds[4].text).replace("$","").replace("(","").replace(")","").replace(",","")
                profit = float( profit )
                country, race_type, location = re.findall(r'([\w ]+)([\(\w\)]*)-([\w. ]+)[\(\w+\)]*', tds[0].text)[0]
                country = COUNTRY_MAP.get(country,country)
                race_type = RACE_TYPE_MAP.get(race_type.replace("(","").replace(")",""),"Horse")
                transhist.append({"country":country, "race_type":race_type, "location":location,"tote_name":tds[1].text, "volume":float(tds[2].text),  "tax":float(tds[3].text.replace("$","")), "profit":profit,"key":detailurl, "belong":"LW" })
        return transhist

    def _getTransHistByDate(self, transHistStr, date, start=0):
        try:
            start = transHistStr.find('<div class="txn_wrapper_settled">', start)
            end = transHistStr.find('<div class="txn_wrapper_settled">', start+1)
            tree = etree.parse(StringIO(transHistStr[start:end]), etree.HTMLParser())
            sel = CSSSelector('div.lca_date h3')
            d= datetime.datetime.strptime(string.capwords(sel(tree)[0].text), "%d %b %Y")
            d= d.strftime("%d-%m-%Y")
            if d == date:
                return tree
            else:
                return self._getTransHistByDate(transHistStr,date,start+1)
        except XMLSyntaxError:
            logger.info("当天暂无交易数据")
            return None

    def getWPTransHistByKey(self, key):
        "根据key查询每场比赛的明细账目"
        url="http://%s/%s" %(self.rc_hosts[0], key)
        logger.info(url)
        rt = self.get_res_content(url)
        m = re.findall( r'<div class="race_infobox">.*?<dt>Race</dt>\s+<dd>(\d+)</dd>.*?(<table class="max_report" name="tbl_detail".*?</table>)', rt, re.S)
        transhist = []
        for rn, trans in m:
            "取出每匹马的赌票吃票数据"
            tdre = '.*?<td>(.*?)</td>'*11
            md = re.findall(r'<tr class="row_(bet|eat)">%s.*?</tr>'%tdre,trans,re.S)
            for e in md:
                profit = re.findall(r'\(?\$([\d.,]+)',e[11])[0].replace(",","")
                profit = -float(profit) if e[11].find("(") > 0 else float(profit)
                limit = re.findall(r'(\d+)/(\d+)', e[5])[0]
                dividend = re.findall(r'(\d+)/(\d+)', e[9].replace(' - ',"0/0"))[0]
                transhist.append({"race_num" :int(rn),"horse_num":int(e[1]),"bet_type":e[0], "volume":max(float(e[2].replace("<sup>","").replace("</sup>","")), float(e[3].replace("<sup>","").replace("</sup>",""))),
                       "discount":float(e[4])/100.0,"lwin":float(limit[0])/10.0,"lplace":float(limit[1])/10.0,"profit":profit,"position":int(e[8].replace(' - ',"0")),
                       "winDividend":float(dividend[0])/10.0, "placeDividend":float(int(dividend[1]))/10.0 })
        return transhist

    def get_tote_price(self,key,race_num):
        race_date,race_type=key
        url="http://%s/totedata?race_date=%s&race_type=%s&rc=%s&currRC=%s" %(self.rc_hosts[0],race_date,race_type,race_num,race_num)
        rt = self.get_res_content(url)
        try:
            indexStart = rt.find("var toteContent='")+17
            indexEnd = rt.find("</table>")+8
            content = rt[indexStart:indexEnd]
            content=content.replace("</td> <td >", "</td><td >")
            content=content.replace("<tr> <td >", "<tr><td >")
            content=content.replace("</td> </tr>", "</td></tr>")
            tree = etree.parse(StringIO(content), etree.HTMLParser())
            rs = tree.xpath('//text()')
            new_rs = [];tote_prices={}
            for r in rs:
                if r not in [u'\xa0',' ']:
                    new_rs.append(r)

            for i in range(len(new_rs)/3):
                tmp = new_rs[3*i:3*i+3]
                if not (tmp[0]=='SCR' or tmp[0]==" "):
                    try:
                        tote_prices[int(tmp[1])]=(float(tmp[0].split("-")[-1]),float(tmp[2].split("-")[-1]))
                    except:
                        logger.exception(tmp)
            return tote_prices

        except XMLSyntaxError:
            logger.info('获取赔率失败')
            return {}

    def get_race_result(self,date):
        url="http://%s/results.jsp?d=%s" %(self.rc_hosts[0],date)
        rt = self.get_res_content(url)
        result_list=rt[rt.find('<div id="result_list">'):rt.find('<!--result_list end here-->')]
        result_window=rt[rt.find('<div id="results_window">'):rt.find('<!--Result container end here-->')]
        result_map,race2id_map={},{}
        tree = etree.parse(StringIO(result_list), etree.HTMLParser())
        for cat_rs_tree in CSSSelector('div.cate_resultslist')(tree):
            for rs_tree in CSSSelector('dl dt')(cat_rs_tree):
                a_elm=CSSSelector("a")(rs_tree)[0]
                cty,loc=rs_tree.get("class").split('_')[0][:2],a_elm.text.split("/")[0].strip()
                if cty=='NZ':cty='AU'
                race2id_map[a_elm.get("href").split("#")[-1].replace('down','')]=cty,self.lm.get((cty,loc),loc)

        tree = etree.parse(StringIO(result_window), etree.HTMLParser())
        for rb in CSSSelector('table.racebox')(tree):
            raceno=CSSSelector('div.raceno')(rb)[0].get('id').split("_")
            race_all_result=result_map.setdefault(race2id_map[raceno[0]],{})
            one_race_result=race_all_result.setdefault(int(raceno[1]),{})
            totes=[]
            for t in CSSSelector('div.result_tote ul li')(rb):
                totes.append(t.get('id').split("_")[0].upper())
            tb_name,tb_idx=['wp','fc','pft'],0
            for rt in CSSSelector('table.result_table')(rb):
                if rt.get('id') not in ['scr_row','resultThead']:
                    for tr in CSSSelector('tr')(rt):
                        tds=CSSSelector('td')(tr)
                        for ti,t in enumerate(totes):
                            tote_rs=one_race_result.setdefault("%s-%s" %(t,tb_name[tb_idx]),{})
                            if tb_idx==0:
                                tote_rs[tds[0].text]=(0 if tds[1+3*ti].text=='-' else float(tds[1+3*ti].text),0 if tds[3+3*ti].text=='-' else float(tds[3+3*ti].text))
                            else:
                                tote_rs[tds[0].text]=0 if tds[1+ti].text=='-' else float(tds[1+ti].text)
                    tb_idx+=1
        return result_map

if __name__ == '__main__':
    pass
