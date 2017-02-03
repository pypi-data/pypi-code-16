import re

def extractRegex(exp, string):
    try:
        return re.search(exp, string).group(1)
    except:
        return 'error'
