# Helpers for implementing anvil.server on a threaded Real Python process.
# Used in uplink and downlink, but not in pypy-sandbox.

import threading, random, string, json

from . import  _serialise, _server
from ._server import LazyMedia


def _gen_id():
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(10))


# Overwrite with functions from context
send_reqresp = None
on_register = None # optional


class LocalCallInfo(threading.local):
    def __init__(self):
        self.stack_id = None
        self.session = None

    def __getitem__(self, item):
        return self.session.__getitem__(item)

    def __setitem__(self, key, value):
        return self.session.__setitem__(key, value)

    def __delitem__(self, key):
        del self.session[key]

    def get(self, key, default=None):
        return self.session.get(key, default)

    def __iter__(self):
        return self.session.__iter__()


call_info = LocalCallInfo()
call_responses = {}
waiting_for_calls = threading.Condition()

registrations = {}
backends = {}


class IncomingRequest(_serialise.IncomingReqResp):
    def execute(self):
        def make_call():
            call_info.stack_id = self.json.get('call-stack-id', None)
            call_info.session = self.json.get('sessionData', None)
            try:
                if 'liveObjectCall' in self.json:
                    loc = self.json['liveObjectCall']
                    spec = dict(loc)

                    if self.json["id"].startswith("server-"):
                        spec["source"] = "server"
                    elif self.json["id"].startswith("client-"):
                        spec["source"] = "client"
                    else:
                        spec["source"] = "UNKNOWN"

                    del spec["method"]
                    backend = loc['backend']
                    if backend not in backends:
                        raise Exception("No such LiveObject backend: " + repr(backend))
                    inst = backends[backend](spec)
                    method = getattr(inst, loc['method'])
                    r = method(*self.json['args'], **self.json['kwargs'])
                else:
                    command = self.json['command']
                    if command not in registrations:
                        raise Exception('No server function named %s has been registered' % command)
                    r = registrations[command](*self.json["args"], **self.json["kwargs"])

                try:
                    json.dumps(call_info.session)
                except:
                    raise Exception("anvil.server.session may only contain strings, numbers, lists and dicts")

                try:
                    send_reqresp({"id": self.json["id"], "response": r, "sessionData": call_info.session})
                except _server.AnvilSerializationError as e:
                    raise _server.AnvilSerializationError("Cannot serialize return value from function. " + e.message)
            except:
                send_reqresp(_server._report_exception(self.json["id"]))
            finally:
                self.complete()

        threading.Thread(target=make_call).start()

    def complete(self):
        pass


class IncomingResponse(_serialise.IncomingReqResp):
    def execute(self):
        id = self.json['id']
        if id in call_responses:
            call_responses[id] = self.json
            with waiting_for_calls:
                waiting_for_calls.notifyAll()
        else:
            print("Got a response for an unknown ID: " + repr(self.json))


def kill_outstanding_requests(msg):
    for k in call_responses.keys():
        if call_responses[k] is None:
            call_responses[k] = {'error': msg}

    with waiting_for_calls:
        waiting_for_calls.notifyAll()


# can be used as a decorator too
def register(fn, name=None):
    if isinstance(fn, str):
        # Someone's using the old syntax. Our bad.
        (fn, name) = (name, fn)

    if name is None:
        name = fn.__name__

    registrations[name] = fn

    if on_register is not None:
        on_register(name, False)

    return fn


callable = register


def register_live_object_backend(cls):

    name = "uplink." + cls.__name__
    backends[name] = cls

    if on_register is not None:
        on_register(name, True)

    return cls


live_object_backend = register_live_object_backend


# A parameterised decorator
def callable_as(name):
    return lambda f: register(f, name)


def do_call(args, kwargs, fn_name=None, lo_call=None): # Yes, I do mean args and kwargs without *s
    id = _gen_id()

    call_responses[id] = None

    with waiting_for_calls:
        #print("Call stack ID = " + repr(_call_info.stack_id))
        req = {'type': 'CALL', 'id': id, 'args': args, 'kwargs': kwargs,
               'call-stack-id': call_info.stack_id}

        if fn_name:
            req["command"] = fn_name
        elif lo_call:
            req["liveObjectCall"] = lo_call
        else:
            raise Exception("Expected one of fn_name or lo_call")

        try:
            send_reqresp(req)
        except _server.AnvilSerializationError as e:
            raise _server.AnvilSerializationError("Cannot serialize arguments to function. " + e.message)

        while call_responses[id] is None:
            waiting_for_calls.wait()

    r = call_responses.pop(id)

    if 'response' in r:
        return r['response']
    if 'error' in r:
        raise _server.AnvilWrappedError(r["error"])
    else:
        raise Exception("Bogus response from server: " + repr(r))
