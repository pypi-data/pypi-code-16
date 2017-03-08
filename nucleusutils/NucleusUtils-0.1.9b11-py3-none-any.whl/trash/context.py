class Context:
    def __init__(self, obj):
        self.object = obj

    def __enter__(self):
        return self.object

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __aenter__(self):
        return self.object

    def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
