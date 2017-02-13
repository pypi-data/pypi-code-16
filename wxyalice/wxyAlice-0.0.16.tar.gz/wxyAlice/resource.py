import falcon


def OK(func):
    def wrapper(self, ids, req, res):
        req.context['ret'] = func(self, ids, req, res)
        res.status = falcon.HTTP_OK

    return wrapper


class Resource(object):
    def __init__(self):
        pass

    def Doc(self, req):
        return req.context['doc']

    def Qry(self, req):
        return req.params

    @OK
    def C(self, ids, req, res):
        return self.mod.C(ids, self.Doc(req))

    @OK
    def Q(self, ids, req, res):
        return self.mod.Q(ids, self.Qry(req))

    @OK
    def R(self, ids, req, res):
        return self.mod.R(ids)

    @OK
    def U(self, ids, req, res):
        return self.mod.U(ids, self.Doc(req))

    @OK
    def D(self, ids, req, res):
        return self.mod.D(ids)
