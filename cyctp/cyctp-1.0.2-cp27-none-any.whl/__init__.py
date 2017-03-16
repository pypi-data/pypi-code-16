# -*- coding: utf-8 -*-

import os, sys
import logging, logging.config
#import ctp library
PKG_PATH = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(PKG_PATH, 'lib') #find ctp dll
if sys.platform == 'win32': os.environ['PATH'] = LIB_PATH + (os.pathsep + os.environ['PATH'] if os.environ['PATH'] else "")
elif sys.platform == 'darwin': os.environ['DYLD_LIBRARY_PATH'] = LIB_PATH + (os.pathsep + os.environ['DYLD_LIBRARY_PATH'] if os.environ.has_key('DYLD_LIBRARY_PATH') else "")
else: 
    os.environ['LD_LIBRARY_PATH'] = LIB_PATH + (os.pathsep + os.environ['LD_LIBRARY_PATH'] if os.environ.has_key('LD_LIBRARY_PATH') else "")  #no effect, should: export LD_LIBRARY_PATH=./lib
    #os.execve(os.path.realpath(__file__), sys.argv, os.environ)

logger = logging.getLogger()#__name__)

from cyctp.ctp_market import CtpMarket
from cyctp.ctp_trader import CtpTrader
from cyctp.ctp_handler import MdHandler, TdHandler
from cyctp.ctp_trader import THOST_TE_RESUME_TYPE

INSTRUMENT_STATUS_BEFORE_TRADING = '0'
INSTRUMENT_STATUS_NO_TRADING = '1'
INSTRUMENT_STATUS_CONTINOUS = '2'
INSTRUMENT_STATUS_AUCTION_ORDERING = '3'
INSTRUMENT_STATUS_AUCTION_BALANCE = '4'
INSTRUMENT_STATUS_AUCTION_MATCH = '5'
INSTRUMENT_STATUS_CLOSED = '6'

HEDGE_FLAG_SPECULATION = '1'
HEDGE_FLAG_ARBITRAGE = '2'
HEDGE_FLAG_HEDGE = '3'
HEDGE_FLAG_MARKETMAKER = '5'

ORDER_PRICE_TYPE_ANY = '1'
ORDER_PRICE_TYPE_LIMIT = '2'
ORDER_PRICE_TYPE_BEST = '3'
ORDER_PRICE_TYPE_LAST = '4'
ORDER_PRICE_TYPE_LAST_PLUS_ONE = '5'
ORDER_PRICE_TYPE_LAST_PLUS_TWO = '6'
ORDER_PRICE_TYPE_LAST_PLUS_THREE = '7'
ORDER_PRICE_TYPE_SELL1 = '8'
ORDER_PRICE_TYPE_SELL1_PLUS_ONE = '9'
ORDER_PRICE_TYPE_SELL1_PLUS_TWO = 'A'
ORDER_PRICE_TYPE_SELL1_PLUS_THREE = 'B'
ORDER_PRICE_TYPE_BUY1 = 'C'
ORDER_PRICE_TYPE_BUY1_PLUS_ONE = 'D'
ORDER_PRICE_TYPE_BUY1_PLUS_TWO = 'E'
ORDER_PRICE_TYPE_BUY1_PLUS_THREE = 'F'
ORDER_PRICE_TYPE_FIVE_LEVEL = 'G'

ORDER_DIRECTION_BUY = '0'
ORDER_DIRECTION_SELL = '1'

ORDER_SUBMIT_STATUS_INSERT = '0'
ORDER_SUBMIT_STATUS_CANCEL = '1'
ORDER_SUBMIT_STATUS_MODIFY = '2'
ORDER_SUBMIT_STATUS_ACCEPT = '3'
ORDER_SUBMIT_STATUS_INSERT_REJECT = '4'
ORDER_SUBMIT_STATUS_CANCEL_REJECT = '5'
ORDER_SUBMIT_STATUS_MODIFY_REJECT = '6'

ORDER_STATUS_ALL = '0'
ORDER_STATUS_PART_QUEUE = '1'
ORDER_STATUS_PART_NOT_QUEUE = '2'
ORDER_STATUS_QUEUE = '3'
ORDER_STATUS_NOT_QUEUE = '4'
ORDER_STATUS_CANCEL = '5'
ORDER_STATUS_UNKNOWN = 'a'
ORDER_STATUS_NOT_TOUCH = 'b'
ORDER_STATUS_TOUCH = 'c'

OFFSET_FLAG_OPEN = '0'
OFFSET_FLAG_CLOSE = '1'
OFFSET_FLAG_FORCE_CLOSE = '2'
OFFSET_FLAG_CLOSE_TODAY = '3'
OFFSET_FLAG_CLOSE_YESTERDAY = '4'
OFFSET_FLAG_FORCE_OFF = '5'
OFFSET_FLAG_LOCAL_FORCE_CLOSE = '6'

VOLUME_CONDITION_ANY = '1'
VOLUME_CONDITION_MIN = '2'
VOLUME_CONDITION_ALL = '3'

FORCE_CLOSE_NOT = '0'
FORCE_CLOSE_LACK_DEPOSIT = '1'
FORCE_CLOSE_CLIENT_OVER_POS_LIMIT = '2'
FORCE_CLOSE_MEMBER_OVER_POS_LIMIT = '3'
FORCE_CLOSE_NOT_INT = '4'
FORCE_CLOSE_VIOLATION = '5'
FORCE_CLOSE_OTHER = '6'
FORCE_CLOSE_PERSON_DELIV = '7'

CONDITION_TRIGGER_IMMEDIATELY = '1'
CONDITION_TRIGGER_TOUCH = '2'
CONDITION_TRIGGER_TOUCH_PROFIT = '3'
CONDITION_TRIGGER_PARKED_ORDER = '4'
CONDITION_TRIGGER_LAST_GT_STOP = '5'
CONDITION_TRIGGER_LAST_GE_STOP = '6'
CONDITION_TRIGGER_LAST_LT_STOP = '7'
CONDITION_TRIGGER_LAST_LE_STOP = '8'
CONDITION_TRIGGER_SELL1_GT_STOP = '9'
CONDITION_TRIGGER_SELL1_GE_STOP = 'A'
CONDITION_TRIGGER_SELL1_LT_STOP = 'B'
CONDITION_TRIGGER_SELL1_LE_STOP = 'C'
CONDITION_TRIGGER_BUY1_GT_STOP = 'D'
CONDITION_TRIGGER_BUY1_GE_STOP = 'E'
CONDITION_TRIGGER_BUY1_LT_STOP = 'F'
CONDITION_TRIGGER_BUY1_LE_STOP = 'H'

TIME_CONDITION_IMMEDIATELY_OR_CANCEL = '1'
TIME_CONDITION_GFOR_SECTION = '2'
TIME_CONDITION_GFOR_DAY = '3'
TIME_CONDITION_GTILL_DAY = '4'
TIME_CONDITION_GTILL_CANCEL = '5'
TIME_CONDITION_GFOR_AUCTION = '6'

class Market(CtpMarket):
    def __new__(cls, *args, **kwargs):
        flowPath = kwargs['flowPath'] if kwargs and kwargs.has_key('flowPath') else (args[0] if len(args)>0 else 'flow'+os.path.sep+'md')
        if not int(os.path.exists(flowPath)):
            os.makedirs(flowPath)
        return CtpMarket.__new__(cls, *args, **kwargs)
    #frontPath="tcp://180.168.146.187:10010", broker="9999", user="083775", pwd="finalpass"
    def __init__(self, flowPath='flow'+os.path.sep+'md', frontPaths=["tcp://180.168.146.187:10031"], broker="9999", user="083775", pwd="finalpass"):  
        self.handler = MdHandler(self)
        self.broker = broker if broker else ""
        self.user = user if user else ""
        self.pwd = pwd if pwd else ""
        logger.info("Connecting to market front server: %s ..."%frontPaths)
        self.connect(frontPaths)

class Trader(CtpTrader):
    def __new__(cls, *args, **kwargs):
        flowPath = kwargs['flowPath'] if kwargs and kwargs.has_key('flowPath') else (args[0] if len(args)>0 else 'flow'+os.path.sep+'td')
        if not int(os.path.exists(flowPath)):
            os.makedirs(flowPath)
        return CtpTrader.__new__(cls, *args, **kwargs)
    #frontPath="tcp://180.168.146.187:10000", broker="9999", user="083775", pwd="finalpass"
    def __init__(self, flowPath='flow'+os.path.sep+'td', frontPaths=["tcp://180.168.146.187:10030"], broker="9999", user="083775", pwd="finalpass", product="", authcode="", privateResume=THOST_TE_RESUME_TYPE.THOST_TERT_RESUME, publicResume=THOST_TE_RESUME_TYPE.THOST_TERT_RESUME, market=None): 
        self.handler = TdHandler(self)
        self.broker = broker if broker else ""
        self.user = user if user else ""
        self.pwd = pwd if pwd else ""
        self.product = product if product else ""
        self.authcode = authcode if authcode else ""
        self.market = market
        self.front_id = -1
        self.session_id = -1
        self.max_order_ref = 0
        self.max_other_ref = 0
        self.all_instruments = []        
        self.all_trade_codes = []
        self.all_bank_accounts = []
        logger.info("Connecting to trader front server: %s ..."%frontPaths)
        self.connect(frontPaths, privateResume, publicResume)
    def set_market(self, market):
        self.market = market
    def get_marekt(self):
        return self.market
    def inc_max_order_ref(self):
        self.max_order_ref += 1
        return '%012d'%self.max_order_ref
    def inc_max_other_ref(self):
        self.max_other_ref += 1
        return '%012d'%self.max_other_ref
