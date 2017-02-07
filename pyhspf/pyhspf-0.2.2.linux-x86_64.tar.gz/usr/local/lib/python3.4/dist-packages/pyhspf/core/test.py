
import datetime

from wdmutil_anaconda import WDMUtil

filename = 'test.wdm'
number      = 1003
start       = datetime.datetime(2000,1,1)
    
attributes = {
    'TSTYPE': 'EXAM',
    'TCODE ': 4,
    'TSSTEP': 1,
    'STAID ': '',
    'IDSCEN': 'OBSERVED',
    'IDLOCN': 'EXAMPLE',
    'STANAM': '',
    'IDCONS': '',
    'TSFILL': 0
    }
    
data = [34.2, 35.0, 36.9, 38.2, 40.2 , 20.1, 18.4, 23.6]
 
wdm = WDMUtil(verbose = True)
wdm.open(filename, 'w')
wdm.create_dataset(filename, number, attributes)
wdm.add_data(filename, number, data, start)
wdm.close(filename)
