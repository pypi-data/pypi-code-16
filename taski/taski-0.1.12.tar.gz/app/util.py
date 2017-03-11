import pytz
from tzlocal import get_localzone

def same_date(utc_dt1, utc_dt2, timezone=None):
    #print(utc_dt1, utc_dt2)
    dt1 = pytz.utc.localize(utc_dt1)
    dt2 = pytz.utc.localize(utc_dt2)

    if timezone is None:
        local_tz = get_localzone()
    else:
        local_tz = pytz.timezone(timezone)

    local_dt1 = dt1.astimezone(local_tz)
    local_dt2 = dt2.astimezone(local_tz)

    #print(local_dt1.date(), local_dt2.date())
    return local_dt1.date() == local_dt2.date()

def dlog(msg):
    try:
        #traceback.print_stack()
        print(msg)
    except UnicodeDecodeError:
        print(msg.encode('utf-8'))
