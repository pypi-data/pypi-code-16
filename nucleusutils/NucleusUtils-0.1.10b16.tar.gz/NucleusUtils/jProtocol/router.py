from .exceptions import ProtocolError, INTERNAL_SERVER_ERROR
from .objects import Request, Response


class Router:
    def __init__(self):
        self.methods = {}

    def register(self, method, callback):
        self.methods[method] = callback

    def _call(self, method, req):
        if method in self.methods:
            result = self.methods[method](req)
            if isinstance(result, Response):
                return result
            raise ProtocolError(INTERNAL_SERVER_ERROR,
                                server_exc=RuntimeError(f"Method '{method}' must return Response object"))
        raise ProtocolError('Unknown method!')

    def read(self, server, client, method, data, index):
        req = Request(server, client, method, data, index)
        try:
            result = self._call(method, req)
        except ProtocolError as e:
            if e.server_exc:
                print(e.server_exc)
            return Response(e)
        except Exception as e:
            return Response(ProtocolError(e))
        else:
            return result

    def get_response(self, server, client, obj):
        method = obj.get('method')
        data = obj.get('data')
        index = obj.get('id')

        response = self.read(server, client, method, data, index)
        response.index = index
        return response.to_protocol()


class AsyncRouter(Router):
    async def _call(self, method, req):
        if method in self.methods:
            result = await self.methods[method](req)
            if isinstance(result, Response):
                return result
            raise ProtocolError(INTERNAL_SERVER_ERROR,
                                server_exc=RuntimeError(f"Method '{method}' must return Response object"))
        raise ProtocolError('Unknown method!')

    async def read(self, server, client, method, data, index):
        req = Request(server, client, method, data, index)
        try:
            result = await self._call(method, req)
        except ProtocolError as e:
            if e.server_exc:
                print(e.server_exc)
            return Response(e)
        except Exception as e:
            return Response(ProtocolError(e))
        else:
            return result

    async def get_response(self, server, client, obj):
        method = obj.get('method')
        data = obj.get('data')
        index = obj.get('id')

        response = await self.read(server, client, method, data, index)
        response.index = index
        return response.to_protocol()
