import random
import threading

from kidslearn.kidslearn.opera import getOpera


def input_func(context):
    context['data'] = input(context['hint'])


def wait_input(msg, hint, count):
    context = {'data': msg, 'hint': hint, 'count': count}

    t = threading.Thread(target=input_func, args=(context,))
    # t.setDaemon(True)
    t.start()
    t.join(5000)  # 等待10秒
    return context['data']





def processKid(score):
    opera = getOpera(10)
    succnum = score[0]
    failnum = score[1]
    num1 = opera[0]
    num2 = opera[1]
    t = opera[2]
    value = opera[3]

    print("%d %s %d = " % (num1, t, num2))

    str = wait_input('0', '答案是:', num1)
    while not str.isdigit():
        str = wait_input('0', '重新输入答案是:', num1)
    answer = int(str)

    if answer == value:
        print("********对*********")
        succnum += 1
    else:
        print("错,答案是%d" % (value))
        failnum += 1

    print("做对%d题，做错%d题\r\n" % (succnum, failnum))

    if (succnum + failnum) % 10 == 0:
        msg = ''
        curScore = succnum * 100 / (succnum + failnum)
        if curScore > 90:
            msg = '天才宝贝'
        elif curScore > 80:
            msg = '厉害宝宝'
        elif curScore > 60:
            msg = '及格宝宝'
        elif curScore > 50:
            msg = '要加油了'
        else:
            msg = '宝宝太笨了'
        print("%s，一共做了%d题了,得分%d分" % (msg, succnum + failnum, succnum * 100 / (succnum + failnum)))
    return [succnum, failnum]


score = [0, 0]
while (True):
    score = processKid(score)
