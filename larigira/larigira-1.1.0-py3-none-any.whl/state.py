'''
This module provides a simple to use way for method (de)serialization focused on
keeping state across restarts. Its simple API will allow you to have internal state kept on filesystem and
recovered.
'''

# TODO: make it a singleton
class StateKeeper:
    @classmethod
    def register(cls, instance_name, obj):
        # TODO: deserialize (if you can)
        # TODO: run sth that will dump it every X
        # TODO: attach a handler to dump upon exit
        pass

