import logging

from wof import WOF

from ..LCM_dao import LCMDao

#import private_config
import wof.models as wof_base
import datetime

logging.basicConfig(level=logging.DEBUG)
config='LCM_config.cfg'
connection='sqlite:///LCM_Data/LCM.db'

dao = LCMDao(connection,config)
#LCM_wof = WOF(dao)
#LCM_wof.config_from_file('LCM_config.cfg')

r = dao.get_datavalues("7","Temp")
#print r
#dir(r)
#len(r)

dt_format = '%m/%d/%Y %H:%M'
for i in range(len(r)):
    DateTimeString = r[i].DateString + ' '+r[i].TimeString
    r[i].DateTimeUTC = datetime.datetime.strptime(DateTimeString, dt_format)
    print r[i].DateTimeUTC
    

