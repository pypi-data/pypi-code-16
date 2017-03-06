import os

def generateRandomData(length):
    return os.urandom(length)

def readFile(path):
    f = open(path)
    s = f.read()
    f.close()
    return s
