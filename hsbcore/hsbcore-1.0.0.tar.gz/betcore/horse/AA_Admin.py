#-*- coding:utf-8 -*-
import logging,re,time
from betcore.horse.AA import AA_Resource
from betcore.horse.config import COUNTRY_MAP
from betcore.util import relogin_when_except
from betcore.exception import DownlineExcpetion

logger = logging.getLogger(__name__)
class ResourceCollector(AA_Resource):

    @relogin_when_except("重登AA...")
    def get_member_tree(self):
        try:
            content = self.get_res_by_json( "http://%s/player-tote-backend/s/member/getDownlinesByPartnerId?uplineId=%s" %(self.rc_hosts[0],self.userId))
        except AttributeError:raise DownlineExcpetion()
        mt=content['result']
        self.memberTree = {m['fullName']:(m['userId'], m['cashBalance']) for m in mt}
        return self.memberTree

    def getWPSummaryTransHistByDate(self, userName, date):
        self.memberTree = self.get_member_tree()
        "根据日期获取该天的交易总账"
        url = "http://%s/player-tote-backend/s/transHist/main?userId=%s" %(self.rc_hosts[0], self.memberTree[userName][0])
        logger.info( url )
        rt = self.get_res_by_json(url)["past"]["TOTE_WINPLACE"]
        trans = []
        for th in rt:
            logger.debug( th )
            d = time.strftime( "%d-%m-%Y", time.strptime(time.ctime(th['date']/1000)))
            if d == date:
                country, raceType, location =  re.findall(r'(?:([\w]+) - )?([\w ]+), ([\w ]+)',th["cardName"])[0]
                cty = raceType if country=="" else country
                rt = "Horse" if country=="" else raceType
                trans.append({"country":COUNTRY_MAP.get(cty,cty),"location":location.strip(), "race_type":rt, "tote_name":"AU" if th["toteCode"]=="TB" else th["toteCode"], "volume":th["volume"], "tax":th["tax"], "profit":th["profit"],"key":(userName,th["cardId"]), "belong":"aa"})
        return trans
    def getWPTransHistByKey(self, keystr):
        self.memberTree = self.get_member_tree()
        "根据CardId查询每场比赛的明细账目"
        key=eval(keystr)
        url="http://%s/player-tote-backend/s/transHist/detail?userId=%s&cardId=%s&marketTypeGroup=TOTE_WINPLACE" %(self.rc_hosts[0], self.memberTree[key[0]][0], key[1])
        detail = self.get_res_by_json(url)
        transDetail = []
        logger.info("抓取用户%s,key:%s的明细账" %key)
        for e in detail["transactionDetails"]:
            transDetail.append({"race_num" :e["raceNumber"],"horse_num":int(e["selectionNumber"]),"bet_type":e["betType"], "volume":e["volume"],"discount":e["discount"],"lwin":e["winLimit"],"lplace":e["placeLimit"],"profit":e["balance"],"position":int(e["position"]),"win_dividend":e["winDividend"], "place_dividend":e["placeDividend"] })
        return transDetail

    def add_user(self,name,credit="600000",sec_code=("!1qaz2wsx","24680"),currency="RMB",level='PLAYER'):
        url = "http://%s/partner-server/s/createMember" %self.rc_hosts[0]
        data ={'loginId':name.upper(), 'currency':currency, 'level':level, 'status':'ACTIVE', 'name':name, 'password':sec_code[0], 'pin':sec_code[1],
                'creditLimit':credit, 'lineLossLimit':credit,
                'tax':'%s,TOTE_WINPLACE,0.003,0.006;%s,INPLAY_WINPLACE,0.004,0.01;%s,FORECAST,0,0.015;%s,QUINELLA,0.003,0.009' %(currency,currency,currency,currency),
                'minorTax':'%s,TOTE_WINPLACE,0.003,0.006;%s,FORECAST,0,0.015;%s,QUINELLA,0.003,0.009' %(currency,currency,currency),
                'taxRebate':'0',
                'ticketLimit':'TOTE_WINPLACE,50000,50000;INPLAY_WINPLACE,50000,50000;QUINELLA,50000,50000',
                'minorTicketLimit':'TOTE_WINPLACE,6000,6000;QUINELLA,2400,2400',
                'fightLimit':'0,0,0,0'}
        rt=self.session.post(url, data,timeout=30).json()
        if rt.get("userId",0)>0:
            logger.info("创建账号:%s成功" %name)
            return 1
        else:
            logger.info("创建账号：%s失败:%s" %(name,rt))
            return 0

    def del_user(self,username):
        url = "http://%s/partner-server/s/deleteUser" %self.rc_hosts[0]
        data={'userId':self.memberTree[username][0]}
        rt=self.session.post(url, data,timeout=30).json()
        if rt.find("ok")>0:
            logger.info("delete user %s 成功", username)
            return True
        else:
            logger.info(rt)
            return False


    def add_users(self,st_idx,end_idx,player_prefix,endfix_set=[''],credit_set=["600000"],sec_code=("!1qaz2wsx","24680"),currency="RMB",level='PLAYER'):
        users=[]
        for i in range(st_idx,end_idx):
            for idx,end in enumerate(endfix_set):
                name = "%s%s%s" %(player_prefix,i,end)
                self.add_user(name=name,credit=credit_set[idx],sec_code=sec_code,currency=currency,level=level)
                users.append(name)
                time.sleep(1)
        return users

    def add_users2(self,player_prefix,endfix_set=[''],credit_set=["600000"],sec_code=("!1qaz2wsx","24680"),currency="RMB",level='PLAYER'):
        users=[]
        for idx,end in enumerate(endfix_set):
            name = "%s%s" %(player_prefix,end)
            self.add_user(name=name,credit=credit_set[idx],sec_code=sec_code,currency=currency,level=level)
            users.append(name)
            time.sleep(1)
        return users

    def update_user_credit(self,user_name,credit="150000"):
        "更新信用额并激活账号"
        update_profile={ "userId":self.memberTree[user_name][0], "loginId":user_name.upper(), "status":"ACTIVE",
                        "name":user_name, "mobileNo":"+15555555555|", "password":"", "pin":"",
                        "creditLimit":credit, "lineLossLimit":credit,
                        "tax":"RMB,TOTE_WINPLACE,0.003,0.006;RMB,INPLAY_WINPLACE,0.002,0.01;RMB,FORECAST,0,0.004;RMB,QUINELLA,0.0035,0.009",
                        'minorTax':'RMB,TOTE_WINPLACE,0.003,0.006;RMB,FORECAST,0,0.004;RMB,QUINELLA,0.003,0.009',
                        "taxRebate":"RMB,TOTE_WINPLACE,0,0;RMB,INPLAY_WINPLACE,0,0;RMB,FORECAST,0,0;RMB,QUINELLA,0,0",
                        "ticketLimit":"TOTE_WINPLACE,50000,50000;INPLAY_WINPLACE,50000,50000;QUINELLA,50000,50000",
                        'minorTicketLimit':'TOTE_WINPLACE,50000,50000;QUINELLA,50000,50000',
                        "fightLimit":"0,0,0,0" }
        rt=self.session.post("http://%s/partner-server/s/editMember" %self.rc_hosts[0],update_profile).json()
        if rt.get("error",None) is not None:
            logger.info(rt["error"])
            return 0
        return rt['status']=='ok'
if __name__ == '__main__':
    pass
