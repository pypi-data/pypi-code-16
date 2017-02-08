#-*- coding:utf-8 -*-
import datetime, logging, re, time, string
import pytesseract
from random import random
from cStringIO import StringIO
from lxml import etree
from lxml.cssselect import CSSSelector
from lxml.etree import XMLSyntaxError
from PIL import Image
from betcore.exception import DownlineExcpetion
from betcore.horse.LW import LW_Resource
from betcore.horse.config import COUNTRY_MAP, RACE_TYPE_MAP
from betcore.util import moneyStrToNumber, relogin_when_except

logger = logging.getLogger(__name__)
def get_admin_code(imgbuf):
    im=Image.open(StringIO(imgbuf),'r')
    im = im.convert("L")
    im = im.point(lambda i:i > (255 - 80) and 255)
    w,h = im.size
    pt_left,pt_right = [],[]
    # 找出左右两端画线像素点
    for y in xrange(0, h):
        if not im.getpixel((0,y)):
            pt_left.append(y)
        if not im.getpixel((w-1,y)):
            pt_right.append(y)
    pt_start,pt_end = pt_left[0]-1,pt_right[0]-1
    for i in xrange(0, w):
        for t in range(5):
            x = i
            y = pt_start + int((i+1)*float(pt_end-pt_start)/w + 0.5) + t
            y=(h if y>h else y) if y>0 else 0
            try:
                im.putpixel((x,y), 255)
            except:
                logger.info("去除噪音线坐标错误:%s",(x,y))
    return pytesseract.image_to_string(im,config="-psm 7 digits").strip().replace(".","").replace("-","")

class ResourceCollector(LW_Resource):

    def test(self,sec_code):
        print self.js.call('encode',self.js.call('mask',sec_code))

    def add_user(self,name,credit="300,000",sec_code=("!1qaz2wsx","24680"),currency="RMB",level='PLAYER'):
        "level:0会员，1代理"
        currency={"RMB":"RB"}.get(currency,currency)
        level={"AGENT":"1","PLAYER":"0"}.get(level,level)
        url = "http://%s/userscontroller" %self.rc_hosts[0]
        data = {"user":"kin433bag2mab", "pass":"61dc67f2ee9457cb62d75eac773c8f7da2bec02a", "passbak":"!zaq12wsx", "name":"kin433bag2mab",
                "level":0, "credit":"600,000", "currency":"RB",
                "sub_acc_func_checkbox":"history", "sub_acc_func_checkbox":"payreport", "sub_acc_func_checkbox":"ptreport", "sub_acc_func_checkbox":"profile",
                "credit_text":"600,000", "loss":"600,000", "account_type":2, "limit_win":"600,000",
                "bet_tix":"30,000", "bet_tix_minor":"6,000", "eat_tix":"30,000", "eat_tix_minor":"6,000", "eo_tix":0,
                "q_bet_tix":"50,000", "q_bet_tix_minor":"2,400", "q_eat_tix":"50,000", "q_eat_tix_minor":"2,400", "p_bet_tix":0, "p_eat_tix":0,
                "bet_tix_live":"10,000", "eat_tix_live":"10,000", "bet_tax":3, "bet_tax_minor":3, "book_tax":6, "book_tax_minor":6, "fc_bet_tax":0,
                "fc_bet_tax_minor":0, "fc_book_tax":15, "fc_book_tax_minor":15, "q_bet_tax":3, "q_bet_tax_minor":3, "q_book_tax":9, "q_book_tax_minor":9,
                "p_bet_tax":2, "p_book_tax":8, "bet_tax_live":4, "book_tax_live":10, "wp_eat_pt":0, "wp_eat_pt_middle":0,
                "wp_eat_pt_minor":0, "wp_bet_pt":0, "wp_bet_pt_middle":0, "wp_bet_pt_minor":0, "others_eat_pt":0, "others_eat_pt_middle":0,
                "others_eat_pt_minor":0, "others_bet_pt":0, "others_bet_pt_middle":0, "others_bet_pt_minor":0, "parlay_eat_pt":0, "parlay_bet_pt":0, "apply_timing":30,
                "apply_eat_value":0, "apply_bet_value":0, "apply_timing":30, "apply_eat_value":0,
                "apply_bet_value":0, "apply_timing_2":30, "apply_eat_value_2":0, "apply_bet_value_2":0, "apply_timing_2":30, "apply_eat_value_2":0, "apply_bet_value_2":0,
                "apply_timing_3":30, "apply_eat_value_3":0, "apply_bet_value_3":0, "apply_timing_4":9999, "apply_eat_value_4":0, "apply_bet_value_4":0,
                "action":"add", "createAccountType":2, "captchaCode":""}

        data['name'],data['user'],data['credit_text'],data['credit'],data['loss'],data['limit_win'],data['pass'],data['passbak'],data['level']=\
            name,name,credit,credit,credit,credit,self.js.call('mask',sec_code[0]),sec_code[0],level
        while 1:
            r = self.session.get("http://%s/img.jpg?t=2&%s" % (self.rc_hosts[0],random()), timeout=3)
            code=get_admin_code(r.content)
            if len(code)==5:
                logger.info(u"获取验证码:%s" % code)
                data['captchaCode'] = code
                rt=self.get_res_content(url, data)
                break
        if rt.find("User added successfully")>0:
            logger.info("创建账号:%s成功" %name)
            return 1
        if rt.find("User exists")>0:
            logger.info("此前已创建账号:%s成功" %name)
            return 1
        else:
            logger.info("创建账号：%s失败:%s" %(name,rt))
            return 0

    def add_users(self,player_prefix,endfix_set=['','a','b'],credit_set=["300,000","300,000","300,000"],sec_code=("!1qaz2wsx","24680"),currency="RMB",level='PLAYER'):
        users=[]
        for idx,end in enumerate(endfix_set):
            name = "%s%s" %(player_prefix,end)
            while 1:
                if self.add_user(name, credit_set[idx],sec_code,currency,level): break;
            users.append(name)
            time.sleep(1)
        return users

    def reset_passwd(self,name,change_pass):
        url = "http://%s/userscontroller?iam=2" %self.rc_hosts[0]
        new_pass=self.js.call('encode',self.js.call('mask',change_pass))
        data={"processInBackend":"Y", "child":name, "MM_update":"form1", "MM_recordId":name, "pass1":new_pass, "pass2":new_pass }
        self.session.post(url,data)
        logger.info("用户:%s更新密码成功"%name)

    def reset_pin(self,name,change_pin):
        url = "http://%s/userscontroller" %self.rc_hosts[0]
        data={"processInBackend":"Y", "child":name, "MM_update":"form9", "MM_recordId":name, "uid":name, "code1":change_pin, "code2":change_pin}
        self.session.post(url,data)
        logger.info("用户:%s更新pin码成功"%name)


    @relogin_when_except("重登长城..")
    def get_member_tree(self):
        url = "http://%s/member_tree_fin.jsp" %self.rc_hosts[0]
        content = self.get_res_content(url)
        if content.find("logout")>0:raise DownlineExcpetion()
        self.memberTree={}
        prefix='DataBase.user.insert({"citibet" : '
        for line in StringIO(content).readlines():
            idx=line.find(prefix)
            if idx>0:
                m=eval(line[idx+len(prefix):].replace("false","False").replace("true","True"))
                self.memberTree.update({m[0]:(m[0], moneyStrToNumber(m[-1]))})
        return self.memberTree

    @relogin_when_except("重登长城..")
    def getWPSummaryTransHistByDate(self, userName, date):
        "根据日期获取该天的交易总账"
        url = "http://%s/history.jsp?uid=%s" %(self.rc_hosts[0], userName)
        rt = self.get_res_content(url)
        tree = self.getTransHistByDate(rt, date)
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
                transhist.append({"country":country, "race_type":race_type, "location":location,"tote_name":"AU" if tds[1].text=="TB" else tds[1].text , "volume":float(tds[2].text.replace(",","")),  "tax":float(tds[3].text.replace("$","").replace(",","")), "profit":profit,"key":detailurl, "belong":"lw" })
        return transhist

    def getTransHistByDate(self, transHistStr, date, start=0):
        try:
            start = transHistStr.index('<div class="txn_wrapper_settled">', start)
            try:
                end = transHistStr.index('<div class="txn_wrapper_settled">', start+1)
            except ValueError:
                end = transHistStr.rindex('</div></div></body>')
            tree = etree.parse(StringIO(transHistStr[start:end]), etree.HTMLParser())
            sel = CSSSelector('div.lca_date h3')
            d= datetime.datetime.strptime(string.capwords(sel(tree)[0].text), "%d %b %Y")
            d= d.strftime("%d-%m-%Y")
            if d == date:
                return tree
            else:
                return self.getTransHistByDate(transHistStr,date,start+1)
        except XMLSyntaxError:
            logger.exception("当天暂无交易数据")
            return None

        except ValueError:
            if transHistStr.find("<script>location.replace")>=0:
                raise DownlineExcpetion()
            else:
                logger.exception("当天暂无交易数据")
                return None
    def del_user(self,name):
        url="http://%s/users?d=%s" %(self.rc_hosts[0],name)
        rt = self.get_res_content(url)
        if rt.find("closed")>0:
            logger.info("删除用户%s成功" %name)
            return True
        else:
            logger.info("删除用户%s失败" %name)
            return False

    def touch_user(self,name):
        "解锁用户"
        for i in range(1,3):self.get_res_content('http://%s/users?u=%s&l=-%s' %(self.rc_hosts[0],name,i))
        logger.info("用户%s解锁:%s" %name)
        return 1

    @relogin_when_except("重登长城..")
    def getWPTransHistByKey(self, key):
        "根据key查询每场比赛的明细账目"
        url="http://%s/%s" %(self.rc_hosts[0], key)
        logger.info(url)
        rt = self.get_res_content(url)
        try:
            rt = rt[rt.index('<div class="txn_wrapper settled_detail" name="normal_txn_block"'):]
        except:
            rt = rt[rt.index('<div class="txn_wrapper settled_detail" name="live_txn_block"'):]
        m = re.findall( r'<div class="race_infobox">.*?<dt>Race</dt>\s+<dd>(\d+)</dd>.*?(<table class="max_report" name="tbl_detail".*?</table>)', rt, re.S)
        transhist = []
        for rn, trans in m:
            "取出每匹马的赌票吃票数据"
            tdre = '%s%s' %('.*?<td>(.*?)</td>'*11,'.*?<td class="type">.*?</td>')
            md = re.findall(r'<tr class="row_(bet|eat)"\s+name="normal_txn">%s.*?</tr>'%tdre,trans,re.S)
            for e in md:
                profit = re.findall(r'\(?\$([\d.,]+)',e[11])[0].replace(",","")
                profit = -float(profit) if e[11].find("(") > 0 else float(profit)
                limit = re.findall(r'(\d+)/(\d+)', e[5])[0]
                dividend = re.findall(r'(\d+)/(\d+)', e[9].replace(' - ',"0/0"))[0]
                transhist.append({"race_num" :int(rn),"horse_num":int(e[1]),"bet_type":e[0], "volume":max(float(e[2].replace("<sup>","").replace("</sup>","")), float(e[3].replace("<sup>","").replace("</sup>",""))),
                       "discount":float(e[4])/100.0,"lwin":float(limit[0])/10.0,"lplace":float(limit[1])/10.0,"profit":profit,"position":int(e[8].replace(' - ',"0")),
                       "win_dividend":float(dividend[0])/10.0, "place_dividend":float(int(dividend[1]))/10.0 })
        return transhist
    def update_user_credit(self,user_name,credit="600,002"):
        update_profile={"child":user_name, "processInBackend":"Y", "sub_acc_func":"", "eo_tix":"0",
                        "eo_bet":"0.0", "eo_book":"0.0", "auto_submit_formpt":"n", "uid":user_name,
                        "tax_update":"n", "tic_update":"n", "nll_update":"y", "name":user_name, "bet_tix":"0",
                        "eat_tix":"0", "q_bet_tix":"0", "q_eat_tix":"0", "p_bet_tix":"0", "p_eat_tix":"0",
                        "updatephone":"n", "MM_update":"form4", "limit":credit, "loss":"Unlimited", "limit_win":"Unlimited"}
        rt=self.session.post("http://%s/userscontroller" %self.rc_hosts[0],update_profile).text
        return rt.find("Account data updated successfully")>0
if __name__ == '__main__':
    print open("mt.txt","r").read()
