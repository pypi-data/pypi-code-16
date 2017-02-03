import sys

def getAlerts(trans):
    alerts = ''
    try:
        if trans['status'].lower() <> 'complete':
            return 'not complete'
        if int(trans['totalSize']) > 70000:
            alerts += 'large size, '
        if int(trans['latency']) > 800:
            alerts += 'high latency, '
        if trans['connectDuration'] <> '' and int(trans['connectDuration']) > 600:
            alerts += 'long connect time, '
        if trans['dnsDuration'] <> '' and int(trans['dnsDuration']) > 600:
            alerts += 'long DNS connect,'
        if trans['type'] == 'googleads/ad':
            if trans['av_request'] == '':
                alerts += 'ad not viewed, '
            if trans['creatives'] == '':
                alerts += 'no fill, '
        if trans['protocol'] <> 'https':
            alerts += 'not secure, '
    except:
        return alerts
    return alerts



