import datetime
import calendar

utz = lambda x: calendar.timegm(x.timetuple()) * 1000
inverse_utz = lambda x: time.gmtime(x / 1000)
tuple_str = lambda x: time.strftime('%Y-%m-%d', x)
str_dt = lambda x: datetime.strptime(x, "%Y-%m-%d")
dt_str = lambda x: x.strftime("%Y-%m-%d")
month_increment = lambda x, y: datetime.strptime(x, '%Y-%m-%d') + relativedelta(months=y)
increment_date = lambda x, n: x + timedelta(n)
