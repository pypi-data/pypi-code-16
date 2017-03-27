import os
from queue import Queue

class GarbageLogCollections:
    # url ga
    # info ga
    # payload ga
    # result ga
    def gc(n, msg):
        m = n + ' ' + msg
        os.system("echo {} >> {}/{}.log".format(m, GA_DIR, n))


class Collections:
    q = Queue()
    url = set()

    def __init__(self, dir='.'):
        self.f = dir

    def add(self,type, content):
        getattr(Collections, type).add(content)

    def save(self, type,f):
        with open(os.path.join(self.f,f), 'w') as fp:
            for c in getattr(Collections, type):
                print(c, file=fp)

    def load(self, type, f):
        try:
            t = getattr(Collections, type)
        except AttributeError as e:
            setattr(Collections, type, set())
            t = getattr(Collections, type)
        with open(os.path.join(self.f,f), 'r') as fp:
            for l in fp:
                t.add(l)

    def ready(self, type):
        t = getattr(Collections, type)
        for c in t:
            Collections.put(c)

    @staticmethod
    def put(content):
        Collections.q.put(content)

    @staticmethod
    def get(timeout=6, block=True):
        return Collections.q.get(timeout, block)

