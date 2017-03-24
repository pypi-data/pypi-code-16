# coding: utf8

import datetime
from datetime import date
import logging
from project.agency_confs import a_pair_of_a_agency_id_list
from libs.exception import HzfException
from libs.subrent_pay_date_amend import amend_subrent_pay_date
from libs.time_utils import add_months
from project.error_code import ERR_LAST_SUBRENT_GT_THIRTY

try:
    from huizhaofang.models import SubPay, SubRent, Pay, User, ContractSnapshot, ContractNo
except:
    from db_models.tables.subpay import SubPay
    from db_models.tables.subrent import SubRent
    from db_models.tables.pay import Pay
    from db_models.tables.user import User
    from db_models.tables.contract_snapshot import ContractSnapshot
    from db_models.tables.contract_no import ContractNo

try:
   from libs.log_tool import write_debug_log
except:
   def write_debug_log(string):
       print string


#### 合同日期相关转换函数

def get_date(year, month, day, plus=False):
    """ 某个理论日期不存在时，需要根据场景向前/向后推移，找到一个有效日期"""
    #printLog("get_date: [%s/%s/%s]" % (year, month, day))
    if day <= 0:
        raise Exception('无效的day %s' % day)
    invalid = False
    while True:
        try:
            ret = datetime.date(year, month, day)
            break #已经找到有效日期
        except: #无效日期，需要循环继续寻找
            #printLog("[%s/%s/%s]" % (year, month, day))
            invalid = True
            day -= 1
            if day == 0:
                raise
            continue
    if plus and invalid:
        ret += datetime.timedelta(days=1)
    return ret

def get_delta_date(month, date, plus=False):
    #printLog("delta: [%s/%s]" % (str(date), month))
    if date.month <= month:
        year = date.year - (month - date.month + 12) / 12
        month = (12 + date.month - month) % 12
        if month == 0:
            month = 12
        day = date.day
    else:
        year = date.year
        month = date.month - month
        day = date.day
    return get_date(year, month, day, plus=plus)

def get_future_date(date, month, plus=False):
    #printLog("future: [%s/%s]" % (str(date), month))
    if date.month + month > 12:
        year = date.year + (date.month + month) / 12
        month = (date.month + month) % 12
        if month == 0:
            month = 12
            year -= 1
        day = date.day
    else:
        year = date.year
        month = date.month + month
        day = date.day
    #printLog("future 0-[%s/%s/%s]" % (year, month, day))
    return get_date(year, month, day, plus=plus)


def get_contract_cycle(start, end, fix_mode=True):
    if type(start) in [str, unicode]:
        start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    if type(end) in [str, unicode]:
        end = datetime.datetime.strptime(end, '%Y-%m-%d').date()

    m = 1
    d = 0
    nextend = start - datetime.timedelta(days=1)
    while True:
        if fix_mode:
            cur_start = get_future_date(start, m - 1 , plus=True)
            nextend = get_future_date(start, m, plus=True) - datetime.timedelta(days=1)
        else:
            cur_start = nextend + datetime.timedelta(days=1)
            nextend = get_future_date(cur_start, 1, plus=True) - datetime.timedelta(days=1)
        logging.info("akpm %s" % nextend)
        if nextend == end:
            break
        if nextend > end:
            if end.day >= start.day:
                d = end.day - cur_start.day + 1
            elif not fix_mode:
                d = (end - cur_start).days + 1
            else:
                d = end.day + 30 - start.day + 1
            m -= 1
            break
        m += 1
    if d == 30 and fix_mode:
        d = 0
        m += 1

    return m,d

def get_subrent_list(lease_begin, lease_end, hzf_pay_type, amount,
                     prepay_days, down_payment_month, agency_id, hzf_final_payment=1,
                     lease_type=2, fix_mode=True, service_fee_payer=6):
    ret = []
    hzf_pay_rate = [3, 6, 12]
    rate = hzf_pay_rate[hzf_pay_type - 1]

    if lease_type == 3:
        down_payment_month = 0

    months, days = get_contract_cycle(lease_begin, lease_end, fix_mode=fix_mode)
    tm = months
    if days > 0:
        tm += 1
    stages = tm / rate
    if tm % rate > 0:
        stages += 1
    last_end_date = lease_begin - datetime.timedelta(days=1)
    for i in range(stages):
        s = SubRent()
        s.index = i + 1
        diff = 0
        if i == 0:
            diff = down_payment_month
        print '................'
        print str(lease_begin)
        print str(diff)
        print str(down_payment_month)

        if not fix_mode:
            for j in range(diff):
                cur_start = last_end_date + datetime.timedelta(days=1)
                if j == 0:
                    s.pay_date = cur_start
                last_end_date = get_future_date(cur_start, 1, plus=True) - datetime.timedelta(days=1)
            for j in range(rate-diff):
                cur_start = last_end_date + datetime.timedelta(days=1)
                if j == 0:
                    s.start_date = cur_start
                if diff == 0 and j == 0:
                    s.pay_date = cur_start
                last_end_date = get_future_date(cur_start, 1, plus=True) - datetime.timedelta(days=1)
            s.end_date = last_end_date
        else:
            s.start_date = get_future_date(lease_begin,
                                           i * rate + diff)
            s.end_date = get_future_date(lease_begin - datetime.timedelta(days=1),
                                         (i + 1) * rate)
            s.pay_date =  get_future_date(lease_begin,
                                           i * rate)  # - datetime.timedelta(days=1)

        if service_fee_payer and service_fee_payer == 6 and i == 0:
            if hzf_pay_type == 3:
                d_rate = 0.92
                r_rate = 0.94
            elif hzf_pay_type == 2:
                d_rate = 0.95

            #s.price = int(round(amount * (rate - diff + (1-d_rate)/d_rate * 3)))
            s.price = int(round(amount * (rate - diff)))
        elif service_fee_payer == 7 and i == 0:
            if hzf_pay_type == 3:
                d_rate = (1 * 2 + 0.92 * 9) / 11
                amount = amount / 0.92 * d_rate
            s.price = int(round(amount * (rate - diff)))
        else:
            s.price = int(round(amount * (rate - diff)))
        if stages == 1:
            ret.append(s)
        elif i < stages - 1:
            ret.append(s)
        elif ret and hzf_final_payment == 2:
            s.end_date = lease_end
            if agency_id in [10630]:
                check_hzf_payment(s, agency_id)
            ret[0].price += s.price
        elif ret and hzf_final_payment == 3:
            s.end_date = lease_end
            if agency_id in [10630]:
                check_hzf_payment(s, agency_id)
            ret[-1].end_date = lease_end
            ret[-1].price += s.price
        else:
            ret.append(s)

    #payrate = float((lease_end - s.start_date).days + 1) / 30
    ret[-1].end_date = lease_end
    #ret[-1].price = int(round(ret[-1].price * payrate))
    amend_subrent_pay_date(ret[0], agency_id)
    return ret

def check_hzf_payment(subrent, agency_id):
    if agency_id in [1969, 1717, 10465]: # 如果是有家置地和天地昊、同程 不检查尾款同上期合并和尾款首付
        return
    last_subrent_days = (subrent.end_date - subrent.start_date).days
    if last_subrent_days > 30:
        raise HzfException(ERR_LAST_SUBRENT_GT_THIRTY[0], ERR_LAST_SUBRENT_GT_THIRTY[1])

payment_params = [
  { 'rate': 1, },
  { 'rate': 2, },
  { 'rate': 3, },
  { 'rate': 4, },
  { 'rate': 5, },
  { 'rate': 6, },
  { 'rate': 7, },
  { 'rate': 8, },
  { 'rate': 9, },
  { 'rate': 10, },
  { 'rate': 11, },
  { 'rate': 12, },
]

def yuan2fen(amount):
    s = "%s00" % (int(amount))
    return int(s)

def fen2yuan(amount):
    str_fen = str(amount)
    str_yuan = "%s.%s" % (str_fen[:-2], str_fen[-2:])
    return str_yuan

def get_month_days(date):
    for day in [28, 29, 30, 31]:
        try:
            datetime.date(date.year, date.month, day)
            ret = day
        except:
            pass
        
    return ret


def get_subpay_list(lease_begin, lease_end, user_pay_type, prepay_day,
                    service_fee, amount, down_payment_month, agency_id,
                    prepay_days=15, final_payment=1, final_price=-1,
                    final_service_fee=-1, lease_type=1, service_fee_payer=1, fix_mode=True):
    ret = []
    if lease_type == 3:
        down_payment_month = 0
    params = payment_params[user_pay_type - 1]
    rate = params['rate']
    down_payment_stage = down_payment_month / rate

    logging.info("akpm %s - %s" % (lease_begin, lease_end))
    total_months, total_days = get_contract_cycle(lease_begin, lease_end, fix_mode)
    logging.info("akpm %s - %s" % (total_months, total_days))
    i = 0
    orig_service_fee = service_fee

    start = lease_begin
    end = lease_end
    nextend = start - datetime.timedelta(days=1)
    last_end_date = start - datetime.timedelta(days=1)

    for i in range(down_payment_stage):
        cur_start = last_end_date + datetime.timedelta(days=1)  #get_future_date(start, m - 1 , plus=True)
        last_end_date = get_future_date(cur_start, 1, plus=True) - datetime.timedelta(days=1)

    i = 0
    m = 1
    while True:
        #if fix_mode:
        #    cur_start = get_future_date(start, m - 1 , plus=True)
        #    last_end_date = get_future_date(cur_start, m, plus=True) - datetime.timedelta(days=1)
        #else:
        #    cur_start = last_end_date + datetime.timedelta(days=1)  #get_future_date(start, m - 1 , plus=True)
        #    last_end_date= get_future_date(cur_start, 1, plus=True) - datetime.timedelta(days=1)

        if service_fee_payer in [4] and i < 3:
            service_fee = 0
        else:
            service_fee = orig_service_fee

        s = SubPay()
        s.price = int(round((amount + service_fee) * rate))
        s.base_price = int(round(amount * rate))
        s.unpay_price = int(round((amount + service_fee) * rate))
        s.service_fee = int(round(service_fee * rate))
        s.index = i+1

        if not fix_mode:
            cur_start = last_end_date + datetime.timedelta(days=1)  #get_future_date(start, m - 1 , plus=True)
            s.end_date = get_future_date(cur_start, 1, plus=True) - datetime.timedelta(days=1)
        elif lease_begin.day == 1:
            s.end_date = get_future_date(lease_begin,
                                         (i + down_payment_stage + 1) *
                                         rate) - datetime.timedelta(days=1) 
        else:
            s.end_date = get_future_date(lease_begin - datetime.timedelta(days=1), 
                                         (i + down_payment_stage + 1) *
                                         rate) 

        m += 1
        s.start_date = last_end_date + datetime.timedelta(days=1)
        last_end_date = s.end_date

        pay_date = s.start_date

        if lease_type == 3 or lease_type == 4: #C端 公寓目前只支持5天后还款
            prepay_days = -4

        for j in range(0, 32):
            date1 = pay_date - datetime.timedelta(days=prepay_days + j)
            write_debug_log("date1: " + str(date1))
            if date1.day == prepay_day:
                pay_date2 = date1
                break
            date2 = pay_date - datetime.timedelta(days=prepay_days - j)
            write_debug_log("date2: " + str(date2))
            if date2.day == prepay_day:
                pay_date2 = date2
                break
            if date1.day == prepay_day or date1 == get_date(date1.year, date1.month, prepay_day):
                pay_date2 = date1
                break
            if date2.day == prepay_day or date2 == get_date(date2.year, date2.month, prepay_day):
                pay_date2 = date2
                break
            
        write_debug_log("pay_date2: " + str(pay_date2))
        orig = pay_date2

        s.pay_date = get_date(orig.year, orig.month, prepay_day)

        if s.end_date == lease_end:
            ret.append(s)
            break

        if s.end_date > lease_end:
            orig_end = s.end_date
            s.end_date = lease_end

            if fix_mode:
                month_days = 30
            else:
                month_days = get_month_days(s.start_date)
            write_debug_log('%s month_days: %d' % (s.start_date, month_days))

            if total_days > 0 and total_days < month_days:
                payrate = total_days / (month_days * 1.0)
            else:
                payrate = 1

            s.price = int(round((amount + service_fee) * rate * payrate))

            if final_price != -1:
                s.price = final_price + final_service_fee
            s.service_fee = int(round(service_fee * rate * payrate))
            s.base_price = int(round(amount * rate * payrate))
            s.unpay_price = s.price

            #if final_service_fee != -1:
            #    s.service_fee = final_service_fee
            #    s.base_price = final_price

            if final_payment == 1:
                ret.append(s)
            elif final_payment == 2:
                pass
            elif final_payment == 3:
                ret[-1].price += s.price
                ret[-1].end_date = s.end_date
                ret[-1].base_price += s.base_price
                ret[-1].unpay_price += s.unpay_price
                ret[-1].service_fee += s.service_fee
            break

        ret.append(s)
        i += 1

    if final_price != -1:
        ret[-1].price = final_price
        ret[-1].unpay_price = final_price
        ret[-1].service_fee = int(round(final_price *  service_fee / (service_fee + amount)))
        ret[-1].base_price = final_price - s.service_fee

    if lease_type == 4:
        count = 0
        pay_date = lease_begin - datetime.timedelta(days=5)
        # 为了快速实现 新公寓算法，对生成的数据进行修改，之后会对按照整理的算法进行重构
        for subpay in ret:
            if count > 0:
                subpay.pay_date = add_months(pay_date, count)
            if agency_id in a_pair_of_a_agency_id_list:  # 如果是押一付一，付款日期加一个月
                subpay.pay_date = add_months(pay_date, count + 1)
            ret[count] = subpay
            count += 1

    return ret

def get_service_rate(hzf_pay_type, lease_type=None):
    if lease_type == 4:
        return 100 * 8 / 92.0
    rate_list = [4, 5, 8]
    if hzf_pay_type <= 0 or hzf_pay_type > len(rate_list):
        raise Exception('invalid hzf_pay_type')
    return rate_list[hzf_pay_type - 1]

def get_down_payment_month(prepay_days):
    if prepay_days == 3:
        down_payment_month = 0
    elif prepay_days in [2, 30]:
        down_payment_month = 2
    else:  #15/1
        down_payment_month = 1
    return down_payment_month

def get_prepay_day(lease_begin, prepay_days, down_payment_month, lease_type=2):
    if lease_begin.day == 1:
        if prepay_days == 15: 
            prepay_day = 16
        elif prepay_days == 30:
            prepay_day = 1 
        else:
            prepay_day = 5
    else:
        lastday = (get_future_date(lease_begin-datetime.timedelta(days=1),
                                      down_payment_month)).day
        prepay_day = lastday - (prepay_days - 1)
        if prepay_day <= 0:
            prepay_day += 30
        if prepay_day > 30:
            prepay_day -= 30
    return prepay_day

def obj_waper(obj):
    """
    """
    ret = {}

    for k,v in vars(obj).items():
        if k == '_state':
            continue
        hump_key = k
        ret[hump_key] = v

    return ret

def subpay_waper(subpayList):
    new = []
    for i in subpayList:
        if type(i) == dict:
            if 'base_price' not in i.keys():
                i['base_price'] =  int(i['price']) - int(i['service_fee'])
            if 'unpay_price' not in i.keys():
                i['unpay_price'] =  int(i['price'])
            paid_price = 0
            if 'paid_price' not in i.keys():
                paid_price = int(i['price']) - int(i['unpay_price'])
            if 'pay_time' in i.keys() and i['pay_time']:
                pay_time = str(i['pay_time'])
            else:
                pay_time = ''
            if 'remark_pay_time' in i.keys() and i['remark_pay_time']:
                remark_pay_time = str(i['remark_pay_time'])
            else:
                remark_pay_time = ''
            
            if 'overdue_fine' in i.keys() and i['overdue_fine']:
                overdue_fine =  int(i['overdue_fine'])
            else:
                overdue_fine = 0
                
            new.append({
                'index': i['index'],
                'pay_date': i['pay_date'],
                'price': i['price'],
                'base_price': i['base_price'],
                'unpay_price': i['unpay_price'],
                'overdue_fine': overdue_fine,
                'paid_price': paid_price,
                'pay_time': pay_time,
                'remark_pay_time': remark_pay_time,
                'service_fee': i['service_fee'],
                'start_date': str(i['start_date']),
                'end_date': str(i['end_date']),
                'status': '0',
            })
        else:
            if i.pay_time:
                pay_time = str(i.pay_time)
            else:
                pay_time = ''
            remark_pay_time = i.remark_pay_time
            if i.offline_pay_time:
                remark_pay_time = i.offline_pay_time
            if i.status == 0:
                pay_time = ""
                remark_pay_time = ""
            if hasattr(i, 'overdue_fine'):
                overdue_fine = int(i.overdue_fine_nature - i.overdue_fine_reduce)
            else:
                overdue_fine = 0
            
            new.append({
                'index': i.index,
                'price': i.price,
                'base_price': i.base_price,
                'unpay_price': i.unpay_price,
                'paid_price': (i.price - i.unpay_price),
                'pay_time': pay_time,
                'remark_pay_time': str(remark_pay_time),
                'pay_date': str(i.pay_date),
                'service_fee': i.service_fee,
                'overdue_fine':overdue_fine,
                'start_date': str(i.start_date),
                'end_date': str(i.end_date),
                'status': str(i.status),
            })
    subrentList = new
    return new

def subrent_waper(subrentList):
    new = []
    count_idx = 1
    for i in subrentList:
        if type(i) == dict:
            i['index'] = count_idx
            if 'paid' in i.keys():
                paid = i['paid']
            elif 'status' in i.keys():
                paid = i['status']
            else:
                paid = 0
                i['unpay_price'] = i['price']
            new.append({
                'index': i['index'],
                'pay_date': i['pay_date'],
                'price': i['price'],
                'paid': paid,
                'unpay_price': i['unpay_price'],
                'paid_price': int(i['price']) - int(i['unpay_price']),
            })
        else:
            new.append({
                'index': i.index,
                'pay_date': str(i.pay_date),
                'price': i.price,
                'paid': i.status,
                'paid_price': i.price - i.unpay_price,
                'cashing_time': str(i.cashing_time),
                'unpay_price': i.unpay_price,
                'start_date': str(i.start_date),
                'end_date': str(i.end_date),
                'subrent_id': i.subrent_id,
                'status': i.status,
            })
        count_idx += 1
    subrentList = new
    return subrentList


def fix_final_subrent(subrent_list, subpay_list, service_fee_payer=1, orig_fee_rate=5,
                      hzf_final_payment=1,
                      hzf_pay_type=3):

    if hzf_pay_type == 3:
        d_rate = 0.92
        d_rate = 0.94
    elif hzf_pay_type == 2:
        d_rate = 0.95

    total_rent = 0
    for i in subrent_list:
        total_rent += i.price
    total_base_price = 0
    for i in subpay_list:
        total_base_price += i.base_price
    first_amount = subpay_list[0]['price']
    if hzf_final_payment == 2:
        rent = subrent_list[0]
    else:
        rent = subrent_list[-1]

    if service_fee_payer in [2]:
        rent.price = int(round(rent.price -
                                        (total_rent -
            float(total_base_price) / (orig_fee_rate + 100) * 100.0
                                        )))
        for i in subrent_list:
            i.price = int(i.price / 100)
            i.price = i.price  * 100
    elif service_fee_payer in [5]:
        rent.price = int(round(rent.price -
                                        (total_rent -
            float(total_base_price) *  d_rate
                                        )))
        for i in subrent_list:
            i.price = int(i.price / 100)
            i.price = i.price  * 100
    elif service_fee_payer in [6]:
        rent.price = int(round(rent.price
            #+ float(first_amount) * (1-d_rate) * 3
            - (total_rent -
            float(total_base_price) *  (d_rate)
                                        )))
        for i in subrent_list:
            i.price = int(i.price / 100)
            i.price = i.price  * 100
    else:
        rent.price = int(round(rent.price -
                                        (total_rent - total_base_price)))
        rent = subrent_list[0]
    return subrent_list

def get_total_rent(subrent_list):
    total_rent = 0
    if not subrent_list:
        return 0
    for i in subrent_list:
        if type(i) == dict:
            total_rent += i['price']
        else:
            total_rent += i.price

    return int(round(total_rent))

def get_total_pay(subpay_list):
    total_base_price = 0
    total_service_fee = 0
    user_amount = 0
    for i in subpay_list:
        if type(i) == dict:
            if 'base_price' not in i.keys():
                i['base_price'] =  int(i['price']) - int(i['service_fee'])
            total_base_price += i['base_price']
            total_service_fee += i['service_fee']
            user_amount += i['price']
        else:
            total_base_price += i.base_price
            total_service_fee += i.service_fee
            user_amount += i.price
    return user_amount, total_base_price

def calculator(lease_begin, lease_end, monthly_amount,
               service_fee_payer=1, prepay_days_type=1,
               hzf_pay_type=2, final_payment=1,
               user_pay_type=1,
               down_payment_month=-1,
               total_months=-1, total_days=-1, final_price=-1, final_service_fee=-1,
               hzf_final_payment=1, lease_type=2, fix_mode=True
              ):
    prepay_days = [15, 30, -4][prepay_days_type - 1]
    if down_payment_month == -1:
        down_payment_month = get_down_payment_month(prepay_days)


    if hzf_pay_type == 3:
        d_rate = 0.92
    elif hzf_pay_type == 2:
        d_rate = 0.95

    service_rate = get_service_rate(hzf_pay_type, lease_type)
    real_monthly_amount = monthly_amount
    if service_fee_payer in [2]:
        real_monthly_amount = float(monthly_amount) / (service_rate +
                                              100) * 100.0
    if service_fee_payer in [5, 6]:
        real_monthly_amount = float(monthly_amount) * d_rate

    orig_service_rate = service_rate
    if service_fee_payer in [2, 3, 5, 6]:
        service_rate = 0

    service_fee = monthly_amount  * service_rate / 100

    prepay_day = get_prepay_day(lease_begin, prepay_days,
                                down_payment_month)

    subrent_list = get_subrent_list(lease_begin, lease_end,
                     hzf_pay_type,
                     real_monthly_amount, prepay_days,
                     down_payment_month, hzf_final_payment,
                     lease_type=lease_type, service_fee_payer=service_fee_payer) 
    subpay_list = get_subpay_list(lease_begin, lease_end,
                   user_pay_type,
                   prepay_day, service_fee,
                   monthly_amount, down_payment_month,
                   prepay_days, final_payment, lease_type=lease_type, service_fee_payer=service_fee_payer)
    total_months,total_days = get_contract_cycle(lease_begin, lease_end, fix_mode)

    subrent_list = fix_final_subrent(subrent_list, subpay_list,
                  service_fee_payer,orig_service_rate, hzf_final_payment, hzf_pay_type=hzf_pay_type)
    total_rent = get_total_rent(subrent_list)

    subrent_list = subrent_waper(subrent_list)

    user_amount,total_base_price = get_total_pay(subpay_list)
    #subpay_list = subpay_waper(subpay_list)

    final_service_fee = subpay_list[-1].service_fee
    #final_amount = subpay_list[-1]['price']
    final_amount = subpay_list[-1].price

    return subrent_list, subpay_list, prepay_day, total_months, total_days, total_rent

def allocate_contract_no(requester, type=1, disable_prefix=True):
    #type: 0租赁(Z) 1会分期(H) 其他未知(U)
    if type == 0:
        prefix = 'Z' 
    elif type == 1:
        prefix = 'H' 
    else:
        prefix = 'U' 

    c = ContractNo(requester=requester, type=type)
    c.save()

    contract_no = datetime.datetime.now().strftime('%Y%m%d')
    numbers = ContractNo.objects.filter(create_time__gte=datetime.date.today()).order_by('create_time')
    index = c.contract_no_id - numbers[0].contract_no_id + 1
    if disable_prefix:
        prefix = ''

    contract_no = "%s%s%.4d" % (prefix, contract_no, index)
    ContractNo.objects.filter(contract_no_id=c.contract_no_id).update(no=contract_no)

    return contract_no

def get_date_from_str(date):
    if type(date) in [str, unicode]:
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    return date
