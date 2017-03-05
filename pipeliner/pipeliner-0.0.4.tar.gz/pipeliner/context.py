class Context(dict):
    """
    Pipeline execution context
    """
    def __init__(self, current_pipeline, *args, **kwargs):
        self.current_pipeline = current_pipeline
        super(Context, self).__init__(*args, **kwargs)
