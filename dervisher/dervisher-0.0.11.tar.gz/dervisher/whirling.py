#!/bin/bash
__author__ = 'lsamaha'

import sys, signal, time, random, uuid
from threading import Timer
from dervisher.dervisher import Dervisher
from dervisher.words import Words
from dervisher.event import Event
from dervisher.post import Post
from dervisher.stream import Stream
from boto.kinesis.layer1 import KinesisConnection

class Whirling(Dervisher):

    dance = ['back','forth']
    max_events_per_uow = 10

    def __init__(self):
        self.whirling = False
        self.timer = None
        self.count = 0
        self.words = Words()

    def start(self, rpm):
        Dervisher.start(self, rpm)
        self.timer = WhirlTimer(rpm, self.whirl)
        self.timer.start()
        self.whirling = True

    def stop(self):
        self.timer.stop()
        Dervisher.stop(self)

    def whirl(self):
        step = Whirling.dance[self.count % len(Whirling.dance)]
        uow_uid = str(uuid.uuid4())
        self.post.event(Event(event_class='start', event_type='whirl',
                              subtype=step, env='dev', product=self.product, uow_uid=uow_uid))
        for _ in range(random.randrange(0, Whirling.max_events_per_uow)):
            self.post.event(Event(event_class=self.words.any_verb(), event_type=self.words.any_noun(),
                              subtype=self.words.any_adverb(), env='dev', product=self.product, uow_uid=uow_uid))
        self.post.event(Event(event_class='complete', event_type='whirl',
                              subtype=step, env='dev', product=self.product, uow_uid=uow_uid))
        self.count += 1

    def sig(self, signal, frame):
        print("received signal %s" % signal)
        self.stop()

class WhirlTimer():

    def __init__(self, rpm, callback):
        self.timer = None
        self.wait_time = 60 / rpm
        self.callback = callback
        self.stopped = True
        self.start()

    def run(self):
        self.stopped = True
        self.start()
        self.callback()

    def start(self):
        if self.stopped:
            self.timer = Timer(self.wait_time, self.run)
            self.timer.start()
            self.stopped = False

    def stop(self):
        self.timer.cancel()
        self.stopped = True

def main():
    if len(sys.argv) < 2:
        print("usage: whirl rpm shards")
    else:
        rpm = int(sys.argv[1])
        shards = int(sys.argv[2])
        print("a dervisher starts whirling at %d rpm" % rpm)
        dervisher = Whirling(product = 'mimi', post=Post(stream=Stream(KinesisConnection(), shard_count=shards)))
        dervisher.start(rpm)
        signal.signal(signal.SIGINT, dervisher.sig)
        while(dervisher.whirling):
            time.sleep(1)

if __name__ == "__main__":
    main()