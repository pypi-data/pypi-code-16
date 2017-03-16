class Loop(object):
    def __init__(self, state):
        self.state = state

    def run(self):
        self.handle_events()
        self.handle_state()
        self.paint()

    def handle_events(self):
        pass

    def handle_state(self):
        pass

    def paint(self):
        pass

    def trigger_event(self, event):
        self.state['events'].append(event)
