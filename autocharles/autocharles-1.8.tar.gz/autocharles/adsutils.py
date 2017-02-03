import re

gdomains = [
        'tpc.googlesyndication.com', 
        'googleads.g.doubleclick.net',
        'pubads.g.doubleclick.net',
        'pagead2.googlesyndication.com', 
        'cm.g.doubleclick.net',
        'securepubads.g.doubleclick.net',
        'static.doubleclick.net',
        'googleads4.g.doubleclick.net',
        'ad.doubleclick.net'
        ]


def isGoogleAds(transaction):
    domain = transaction.attrib['host']
    if domain in gdomains:
	return True
    else:
        return False

def getType(transaction):
    
    # config file
    if re.search(r'/mads/static[.]*', transaction.attrib['path']) and transaction.attrib['host'] == 'googleads.g.doubleclick.net':
        return 'config'

    # activeview ping
    elif transaction.attrib['host'] == 'pagead2.googlesyndication.com' and transaction.attrib['path'] ==  '/activeview':
        return 'activeview'

    # display or video ads
    query = transaction.get('query')
    if re.search(r'pubads.g.doubleclick.net', transaction.attrib['host']) is not None and transaction.attrib['path'] ==  '/gampad/ads':
       return 'ad'

    # other
    return transaction.findall('response')[0].get('mime-type')

def getAdType(transaction):
    for header in transaction.iter('header'):
        for name in header.findall('name'):
            if name.text == 'X-Afma-Ad-Format' and header.find('value').text == 'native':
                return 'native'
    query = transaction.get('query')
    if re.search(r'env=vp', query) is not None:
        return 'videoad'
    else:
        return 'display'

def formatSec(x):
    return '{:.1f} sec'.format(float(x)/1000)

def formatSize(x):
    return '{:.2f} MB'.format(float(x)/(1024*1024))

def formatSizeKB(x):
    try:
        int(x)
        return '{:.1f}'.format(float(x)/(1024))
    except ValueError:
        return 'n/a'

def formatSpeedTtl(size, duration):
    return '{:.1f} KB/s'.format((float(size)/1024)/(float(duration)/1000))

def formatSpeed(size):
    try:
        int(size)
        return '{:.1f}'.format(float(size)/1024)
    except ValueError:
        return 'n/a'




