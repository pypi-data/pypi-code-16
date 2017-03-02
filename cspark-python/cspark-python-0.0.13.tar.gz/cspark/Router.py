
class Router:

    def handle_update(self, update):
        handler = self.get_handler_class()()
        handler.handle_update(update)
