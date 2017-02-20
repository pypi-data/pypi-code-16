class StreamBuffer:
    def __init__(self):
        self.buffer = []

    def insert(self, data):
        self.buffer.append(data)

    def get(self):
        return self.buffer
