
import time

def format_time(time_string):  #这个函数确保所有时间均采用'HH:MM:SS'格式
    tlen = len(time_string)
    if tlen < 3:
        original_format = '%S'       
    elif tlen < 6:
        original_format = '%M:%S'
    else:
        original_format = '%H:%M:%S'
    time_string = time.strftime('%H:%M:%S', time.strptime(time_string, original_format))
    ####################################################
    #time.strptime() 函数根据指定的格式把一个时间字符串解析为时间元组
    
    return(time_string)

def time2secs(time_string):
    time_string = format_time(time_string)
    (hours, mins, secs) = time_string.split(':')
    seconds = int(secs) + (int(mins)*60) + (int(hours)*60*60)
    return(seconds)

def secs2time(seconds):
    return(time.strftime('%H:%M:%S', time.gmtime(seconds)))
