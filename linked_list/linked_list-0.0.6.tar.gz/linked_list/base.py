class LLBase(object):
    data, nxt = None, None

    def delete(self):
        self.data = None
        self.nxt = None

