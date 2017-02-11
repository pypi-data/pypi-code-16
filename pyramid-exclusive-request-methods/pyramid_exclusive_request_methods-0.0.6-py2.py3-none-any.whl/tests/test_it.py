import unittest
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_defaults
from webtest import TestApp
        
from .. import exclusive_view_config


@exclusive_view_config(route_name='test1', request_method=['GET'])
def test_view0(context, request):
    return Response(text=u'HEY')


@view_defaults(route_name='test2')
class test_view_class(object):
    def __init__(self, context, request):
        pass

    @exclusive_view_config(request_method=['POST'])
    def post(self):
        return Response(text=u'HEY')


class BasicTest(unittest.TestCase):

    def test_it(self):
        def test_view1(context, request):
            return Response(text=u'HEY')


        def test_view2(context, request):
            return Response(text=u'HEY')

        c = Configurator(package=__name__)
        c.include('pyramid_exclusive_request_methods')
        c.add_route('test1', '/1')
        c.add_route('test2', '/2')
        c.add_exclusive_view(test_view1, route_name='test1', request_method=['GET', 'POST'])
        c.add_view(test_view2, route_name='test2', request_method=['GET', 'POST'])

        t = TestApp(c.make_wsgi_app())
        resp = t.get('/1')
        self.assertEquals(resp.status_int, 200)
        resp = t.post('/1')
        self.assertEquals(resp.status_int, 200)
        resp = t.put('/1', status=405)
        self.assertEquals(resp.status_int, 405)

        resp = t.get('/2')
        self.assertEquals(resp.status_int, 200)
        resp = t.post('/2')
        self.assertEquals(resp.status_int, 200)
        resp = t.put('/2', status=404)
        self.assertEquals(resp.status_int, 404)


    def test_it_with_non_exclusives(self):
        def test_view1(context, request):
            return Response(text=u'FOO')


        def test_view2(context, request):
            return Response(text=u'BAR')

        c = Configurator(package=__name__)
        c.include('pyramid_exclusive_request_methods')
        c.add_route('test1', '/1')
        c.add_route('test2', '/2')

        c.scan(__name__)
        c.add_exclusive_view(test_view1, route_name='test1', request_method=['POST'])
        c.add_view(test_view2, route_name='test1', request_method=['PUT'])

        t = TestApp(c.make_wsgi_app())
        resp = t.get('/1')
        self.assertEquals(resp.status_int, 200)
        self.assertEquals(resp.text, u'HEY')
        resp = t.post('/1')
        self.assertEquals(resp.status_int, 200)
        self.assertEquals(resp.text, u'FOO')
        resp = t.put('/1')
        self.assertEquals(resp.status_int, 200)
        self.assertEquals(resp.text, u'BAR')
        resp = t.options('/1', status=405)
        self.assertEquals(resp.status_int, 405)

        resp = t.post('/2')
        self.assertEquals(resp.text, u'HEY')
        resp = t.get('/2', status=405)
        self.assertEquals(resp.status_int, 405)
