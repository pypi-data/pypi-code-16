class Plugin:
    def on_message(self, msg):
        """ Called on each message, to process it and handle it

        msg -- the message dictionnary, as got by redskyAPI
        
        Can be overriden """
        pass

    def execute(self, cmd, *args):
        """ Called when the corresponding command has been called in the client

        args -- optionnal args passed in the client

        Can be overriden """
        pass

class PluginThreaded(Thread):
    def __init__(self):
        Thread.__init__(self)

    def _exceute(self, cmd, args):
