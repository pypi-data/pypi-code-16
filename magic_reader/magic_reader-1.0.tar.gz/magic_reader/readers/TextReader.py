class TextReader(object):
    def __init__(self, source_path):
        self.source_path = source_path

    def read(self):
        reader = open(self.source_path, "rb")
        for r in reader:
            yield r
        reader.close()
