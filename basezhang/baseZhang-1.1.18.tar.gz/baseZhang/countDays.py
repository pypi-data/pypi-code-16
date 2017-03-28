# !usr/bin/env python
# coding=gbk
def is_R_or_N(user_in_date=2017):  # 判断是否闰年
    # user_in_date = int(input('请输入四位数年份：'))
    # print user_in_date
    value_r_n = user_in_date % 4 == 0 and user_in_date % 100 != 0
    if value_r_n:
        result = str(user_in_date) + '是闰年'
        # print result
    else:
        result = str(user_in_date) + '不是闰年'
        # print result
    return value_r_n


def get_mEnd_days(mEnd=12, is_R_N=True):
    totaldays = 0
    if is_R_N:
        if mEnd == 12:
            totaldays = 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 11:
            totaldays = 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 10:
            totaldays = 30 + 31 + 31 + 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 9:
            totaldays = 31 + 31 + 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 8:
            totaldays = 31 + 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 7:
            totaldays = 30 + 31 + 30 + 31 + 29 + 31
        elif mEnd == 6:
            totaldays = 31 + 30 + 31 + 29 + 31
        elif mEnd == 5:
            totaldays = 30 + 31 + 29 + 31
        elif mEnd == 4:
            totaldays = 31 + 29 + 31
        elif mEnd == 3:
            totaldays = 29 + 31
        elif mEnd == 2:
            totaldays = 31
        elif mEnd == 1:
            totaldays = 0
    else:
        if mEnd == 12:
            totaldays = 30 + 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 11:
            totaldays = 31 + 30 + 31 + 31 + 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 10:
            totaldays = 30 + 31 + 31 + 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 9:
            totaldays = 31 + 31 + 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 8:
            totaldays = 31 + 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 7:
            totaldays = 30 + 31 + 30 + 31 + 28 + 31
        elif mEnd == 6:
            totaldays = 31 + 30 + 31 + 28 + 31
        elif mEnd == 5:
            totaldays = 30 + 31 + 28 + 31
        elif mEnd == 4:
            totaldays = 31 + 28 + 31
        elif mEnd == 3:
            totaldays = 28 + 31
        elif mEnd == 2:
            totaldays = 31
        elif mEnd == 1:
            totaldays = 0

    return totaldays


def get_year_toatal_days(year=2017):
    if is_R_or_N(year):
        total = 366
    else:
        total = 365
    return total


def get_yEnd_yStart_days(yEnd=2017, yStart=1949):
    totaday = 0
    years = range(yStart + 1, yEnd)
    for year_every in years:
        if is_R_or_N(year_every):
            totaday += 366
        else:
            totaday += 365
    return totaday


def countDaysBettweenTwo(dayStart='20150101', dayEnd='20170102'):
    yStart, mStart, dStart = int(dayStart[:4]), int(dayStart[4:6]), int(dayStart[6:8])
    yEnd, mEnd, dEnd = int(dayEnd[:4]), int(dayEnd[4:6]), int(dayEnd[6:8])
    print 'dayStart:', yStart, mStart, dStart
    print 'dayEnd:', yEnd, mEnd, dEnd

    dayPast = dEnd + get_mEnd_days(mEnd, is_R_or_N(yEnd))

    dayLeft = get_year_toatal_days(yStart) - dStart - get_mEnd_days(mStart, is_R_or_N(yStart))

    if yEnd - yStart == 1:
        FinalanswerDay = dayPast + dayLeft
    elif yEnd - yStart < 1:
        FinalanswerDay = dayPast - dStart - get_mEnd_days(mStart, is_R_or_N(yStart))
    else:
        FinalanswerDay = dayPast + dayLeft + get_yEnd_yStart_days(yEnd, yStart)
    return FinalanswerDay
