import threading


# uses a set for the queue. Duplicates are therefore discarded, and results popped() at random
class SetQueue:
    def __init__(self):
        self.items = set()

    def push(self, item):
        self.items |= set([item])

    def push_group(self, items):
        self.items |= set(items)

    def pop(self):
        return self.items.pop()

    def pop_group(self, amount):
        return [self.items.pop() for i in range(amount)]

    def __len__(self):
        return len(self.items)


# provides a thread-safe way to push/pop
class PubSub:
    tid = lambda self: threading.current_thread()

    # queue is dependency injected
    def __init__(self, queue):
        self.cv = threading.Condition()
        self.queue = queue
        self.pushed = 0
        self.popped = 0

    # thread-safe push onto queue. takes a single item
    def push(self, item):
        self.cv.acquire()
        self.queue.push(item)
        self.pushed += 1
        self.cv.notify()  # 1 item added, only need to notify 1 waiter
        self.cv.release()

    # thread-safe push onto queue. takes a list of items
    def push_group(self, items):
        self.cv.acquire()
        self.queue.push_group(items)
        self.pushed += len(items)
        self.cv.notify_all()  # notify all. Docs say notify(len(items)) is not garuenteed in future impls, so we dont rely on it
        self.cv.release()

    # thread-safe pop. returns a single item if amount is 1, otherwiser returns a list
    # this is a blocking call
    def pop(self, amount=1):
        self.cv.acquire()

        while (len(self.queue) < amount):
            self.cv.wait()

        if amount == 1:
            result = self.queue.pop()
            self.popped += 1
        else:
            result = self.queue.pop_group(amount)
            self.popped += amount

        self.cv.release()

        return result

    # returns a string of some stats
    def print_info(self):
        print('PubSub: pushed=%s, popped=%s, current_size=%s' % (self.pushed, self.popped, len(self.queue)))
