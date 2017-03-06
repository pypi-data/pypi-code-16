#import traceback

class Task():
    def __init__(self):
        self.id = 0
        self.name = ""
        self.pid = 0
        self.done = False
        self.ts_done = -1
        self.ts_added = -1
        self.meta_data = None

    def __repr__(self):
        return "[Task](" + self.name.encode('utf-8') + ")"

class Project():
    def __init__(self):
        self.id = 0
        self.name = ""
        self.tasks = []
        self.priority = 0

    def __repr__(self):
        return "[Project](" + self.name.encode('utf-8') + ")"

def dlog(msg):
    try:
        #traceback.print_stack()
        print(msg)
    except UnicodeDecodeError:
        print(msg.encode('utf-8'))
