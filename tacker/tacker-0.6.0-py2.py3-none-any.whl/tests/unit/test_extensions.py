# Copyright (c) 2011 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc

import mock
from oslo_log import log as logging
from oslo_serialization import jsonutils
import routes
import webob
import webtest

from tacker.api import extensions
from tacker.common import config
from tacker.common import exceptions
from tacker.plugins.common import constants
from tacker.tests import base
from tacker.tests.unit import extension_stubs as ext_stubs
import tacker.tests.unit.extensions
from tacker.tests.unit import testlib_api
from tacker import wsgi


LOG = logging.getLogger(__name__)
extensions_path = ':'.join(tacker.tests.unit.extensions.__path__)


class ExtensionsTestApp(wsgi.Router):

    def __init__(self, options={}):
        mapper = routes.Mapper()
        controller = ext_stubs.StubBaseAppController()
        mapper.resource("dummy_resource", "/dummy_resources",
                        controller=controller)
        super(ExtensionsTestApp, self).__init__(mapper)


class PluginInterfaceTest(base.BaseTestCase):
    def test_issubclass_hook(self):
        class A(object):
            def f(self):
                pass

        class B(extensions.PluginInterface):
            @abc.abstractmethod
            def f(self):
                pass

        self.assertTrue(issubclass(A, B))

    def test_issubclass_hook_class_without_abstract_methods(self):
        class A(object):
            def f(self):
                pass

        class B(extensions.PluginInterface):
            def f(self):
                pass

        self.assertFalse(issubclass(A, B))

    def test_issubclass_hook_not_all_methods_implemented(self):
        class A(object):
            def f(self):
                pass

        class B(extensions.PluginInterface):
            @abc.abstractmethod
            def f(self):
                pass

            @abc.abstractmethod
            def g(self):
                pass

        self.assertFalse(issubclass(A, B))


class ResourceExtensionTest(base.BaseTestCase):

    class ResourceExtensionController(wsgi.Controller):

        def index(self, request):
            return "resource index"

        def show(self, request, id):
            return {'data': {'id': id}}

        def notimplemented_function(self, request, id):
            return webob.exc.HTTPNotImplemented()

        def custom_member_action(self, request, id):
            return {'member_action': 'value'}

        def custom_collection_action(self, request, **kwargs):
            return {'collection': 'value'}

    class DummySvcPlugin(wsgi.Controller):
            def get_plugin_type(self):
                return constants.DUMMY

            def index(self, request, **kwargs):
                return "resource index"

            def custom_member_action(self, request, **kwargs):
                return {'member_action': 'value'}

            def collection_action(self, request, **kwargs):
                return {'collection': 'value'}

            def show(self, request, id):
                return {'data': {'id': id}}

    def test_exceptions_notimplemented(self):
        controller = self.ResourceExtensionController()
        member = {'notimplemented_function': "GET"}
        res_ext = extensions.ResourceExtension('tweedles', controller,
                                               member_actions=member)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        # Ideally we would check for a 501 code here but webtest doesn't take
        # anything that is below 200 or above 400 so we can't actually check
        # it.  It throws webtest.AppError instead.
        try:
            test_app.get("/tweedles/some_id/notimplemented_function")
            # Shouldn't be reached
            self.assertTrue(False)
        except webtest.AppError as e:
            self.assertIn('501', e.message)

    def test_resource_can_be_added_as_extension(self):
        res_ext = extensions.ResourceExtension(
            'tweedles', self.ResourceExtensionController())
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))
        index_response = test_app.get("/tweedles")
        self.assertEqual(200, index_response.status_int)
        self.assertEqual("resource index", index_response.body)

        show_response = test_app.get("/tweedles/25266")
        self.assertEqual({'data': {'id': "25266"}}, show_response.json)

    def test_resource_gets_prefix_of_plugin(self):
        class DummySvcPlugin(wsgi.Controller):
            def index(self, request):
                return ""

            def get_plugin_type(self):
                return constants.DUMMY

        res_ext = extensions.ResourceExtension(
            'tweedles', DummySvcPlugin(), path_prefix="/dummy_svc")
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))
        index_response = test_app.get("/dummy_svc/tweedles")
        self.assertEqual(200, index_response.status_int)

    def test_resource_extension_with_custom_member_action(self):
        controller = self.ResourceExtensionController()
        member = {'custom_member_action': "GET"}
        res_ext = extensions.ResourceExtension('tweedles', controller,
                                               member_actions=member)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        response = test_app.get("/tweedles/some_id/custom_member_action")
        self.assertEqual(200, response.status_int)
        self.assertEqual("value",
                         jsonutils.loads(response.body)['member_action'])

    def test_resource_ext_with_custom_member_action_gets_plugin_prefix(self):
        controller = self.DummySvcPlugin()
        member = {'custom_member_action': "GET"}
        collections = {'collection_action': "GET"}
        res_ext = extensions.ResourceExtension('tweedles', controller,
                                               path_prefix="/dummy_svc",
                                               member_actions=member,
                                               collection_actions=collections)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        response = test_app.get("/dummy_svc/tweedles/1/custom_member_action")
        self.assertEqual(200, response.status_int)
        self.assertEqual("value",
                         jsonutils.loads(response.body)['member_action'])

        response = test_app.get("/dummy_svc/tweedles/collection_action")
        self.assertEqual(200, response.status_int)
        self.assertEqual("value",
                         jsonutils.loads(response.body)['collection'])

    def test_plugin_prefix_with_parent_resource(self):
        controller = self.DummySvcPlugin()
        parent = dict(member_name="tenant",
                      collection_name="tenants")
        member = {'custom_member_action': "GET"}
        collections = {'collection_action': "GET"}
        res_ext = extensions.ResourceExtension('tweedles', controller, parent,
                                               path_prefix="/dummy_svc",
                                               member_actions=member,
                                               collection_actions=collections)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        index_response = test_app.get("/dummy_svc/tenants/1/tweedles")
        self.assertEqual(200, index_response.status_int)

        response = test_app.get("/dummy_svc/tenants/1/"
                                "tweedles/1/custom_member_action")
        self.assertEqual(200, response.status_int)
        self.assertEqual(jsonutils.loads(response.body)['member_action'],
                         "value")

        response = test_app.get("/dummy_svc/tenants/2/"
                                "tweedles/collection_action")
        self.assertEqual(200, response.status_int)
        self.assertEqual("value",
                         jsonutils.loads(response.body)['collection'])

    def test_resource_extension_for_get_custom_collection_action(self):
        controller = self.ResourceExtensionController()
        collections = {'custom_collection_action': "GET"}
        res_ext = extensions.ResourceExtension('tweedles', controller,
                                               collection_actions=collections)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        response = test_app.get("/tweedles/custom_collection_action")
        self.assertEqual(200, response.status_int)
        LOG.debug(jsonutils.loads(response.body))
        self.assertEqual("value", jsonutils.loads(response.body)['collection'])

    def test_resource_extension_for_put_custom_collection_action(self):
        controller = self.ResourceExtensionController()
        collections = {'custom_collection_action': "PUT"}
        res_ext = extensions.ResourceExtension('tweedles', controller,
                                               collection_actions=collections)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        response = test_app.put("/tweedles/custom_collection_action")

        self.assertEqual(200, response.status_int)
        self.assertEqual('value', jsonutils.loads(response.body)['collection'])

    def test_resource_extension_for_post_custom_collection_action(self):
        controller = self.ResourceExtensionController()
        collections = {'custom_collection_action': "POST"}
        res_ext = extensions.ResourceExtension('tweedles', controller,
                                               collection_actions=collections)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        response = test_app.post("/tweedles/custom_collection_action")

        self.assertEqual(200, response.status_int)
        self.assertEqual('value', jsonutils.loads(response.body)['collection'])

    def test_resource_extension_for_delete_custom_collection_action(self):
        controller = self.ResourceExtensionController()
        collections = {'custom_collection_action': "DELETE"}
        res_ext = extensions.ResourceExtension('tweedles', controller,
                                               collection_actions=collections)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        response = test_app.delete("/tweedles/custom_collection_action")

        self.assertEqual(200, response.status_int)
        self.assertEqual('value', jsonutils.loads(response.body)['collection'])

    def test_resource_ext_for_formatted_req_on_custom_collection_action(self):
        controller = self.ResourceExtensionController()
        collections = {'custom_collection_action': "GET"}
        res_ext = extensions.ResourceExtension('tweedles', controller,
                                               collection_actions=collections)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        response = test_app.get("/tweedles/custom_collection_action.json")

        self.assertEqual(200, response.status_int)
        self.assertEqual('value', jsonutils.loads(response.body)['collection'])

    def test_resource_ext_for_nested_resource_custom_collection_action(self):
        controller = self.ResourceExtensionController()
        collections = {'custom_collection_action': "GET"}
        parent = dict(collection_name='beetles', member_name='beetle')
        res_ext = extensions.ResourceExtension('tweedles', controller,
                                               collection_actions=collections,
                                               parent=parent)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        response = test_app.get("/beetles/beetle_id"
                                "/tweedles/custom_collection_action")

        self.assertEqual(200, response.status_int)
        self.assertEqual('value', jsonutils.loads(response.body)['collection'])

    def test_resource_extension_with_custom_member_action_and_attr_map(self):
        controller = self.ResourceExtensionController()
        member = {'custom_member_action': "GET"}
        params = {
            'tweedles': {
                'id': {'allow_post': False, 'allow_put': False,
                       'validate': {'type:uuid': None},
                       'is_visible': True},
                'name': {'allow_post': True, 'allow_put': True,
                         'validate': {'type:string': None},
                         'default': '', 'is_visible': True},
            }
        }
        res_ext = extensions.ResourceExtension('tweedles', controller,
                                               member_actions=member,
                                               attr_map=params)
        test_app = _setup_extensions_test_app(SimpleExtensionManager(res_ext))

        response = test_app.get("/tweedles/some_id/custom_member_action")
        self.assertEqual(200, response.status_int)
        self.assertEqual('value',
                         jsonutils.loads(response.body)['member_action'])

    def test_returns_404_for_non_existent_extension(self):
        test_app = _setup_extensions_test_app(SimpleExtensionManager(None))

        response = test_app.get("/non_extistant_extension", status='*')

        self.assertEqual(404, response.status_int)


class ActionExtensionTest(base.BaseTestCase):

    def setUp(self):
        super(ActionExtensionTest, self).setUp()
        self.extension_app = _setup_extensions_test_app()

    def test_extended_action_for_adding_extra_data(self):
        action_name = 'FOXNSOX:add_tweedle'
        action_params = dict(name='Beetle')
        req_body = jsonutils.dumps({action_name: action_params})
        response = self.extension_app.post('/dummy_resources/1/action',
                                           req_body,
                                           content_type='application/json')
        self.assertEqual("Tweedle Beetle Added.", response.body)

    def test_extended_action_for_deleting_extra_data(self):
        action_name = 'FOXNSOX:delete_tweedle'
        action_params = dict(name='Bailey')
        req_body = jsonutils.dumps({action_name: action_params})
        response = self.extension_app.post("/dummy_resources/1/action",
                                           req_body,
                                           content_type='application/json')
        self.assertEqual("Tweedle Bailey Deleted.", response.body)

    def test_returns_404_for_non_existent_action(self):
        non_existent_action = 'blah_action'
        action_params = dict(name="test")
        req_body = jsonutils.dumps({non_existent_action: action_params})

        response = self.extension_app.post("/dummy_resources/1/action",
                                           req_body,
                                           content_type='application/json',
                                           status='*')

        self.assertEqual(404, response.status_int)

    def test_returns_404_for_non_existent_resource(self):
        action_name = 'add_tweedle'
        action_params = dict(name='Beetle')
        req_body = jsonutils.dumps({action_name: action_params})

        response = self.extension_app.post("/asdf/1/action", req_body,
                                           content_type='application/json',
                                           status='*')
        self.assertEqual(404, response.status_int)


class RequestExtensionTest(base.BaseTestCase):

    def test_headers_can_be_extended(self):
        def extend_headers(req, res):
            assert req.headers['X-NEW-REQUEST-HEADER'] == "sox"
            res.headers['X-NEW-RESPONSE-HEADER'] = "response_header_data"
            return res

        app = self._setup_app_with_request_handler(extend_headers, 'GET')
        response = app.get("/dummy_resources/1",
                           headers={'X-NEW-REQUEST-HEADER': "sox"})

        self.assertEqual("response_header_data",
                         response.headers['X-NEW-RESPONSE-HEADER'])

    def test_extend_get_resource_response(self):
        def extend_response_data(req, res):
            data = jsonutils.loads(res.body)
            data['FOXNSOX:extended_key'] = req.GET.get('extended_key')
            res.body = jsonutils.dumps(data)
            return res

        app = self._setup_app_with_request_handler(extend_response_data, 'GET')
        response = app.get("/dummy_resources/1?extended_key=extended_data")

        self.assertEqual(200, response.status_int)
        response_data = jsonutils.loads(response.body)
        self.assertEqual('extended_data',
                         response_data['FOXNSOX:extended_key'])
        self.assertEqual('knox', response_data['fort'])

    def test_get_resources(self):
        app = _setup_extensions_test_app()

        response = app.get("/dummy_resources/1?chewing=newblue")

        response_data = jsonutils.loads(response.body)
        self.assertEqual('newblue', response_data['FOXNSOX:googoose'])
        self.assertEqual("Pig Bands!", response_data['FOXNSOX:big_bands'])

    def test_edit_previously_uneditable_field(self):

        def _update_handler(req, res):
            data = jsonutils.loads(res.body)
            data['uneditable'] = req.params['uneditable']
            res.body = jsonutils.dumps(data)
            return res

        base_app = webtest.TestApp(setup_base_app(self))
        response = base_app.put("/dummy_resources/1",
                                {'uneditable': "new_value"})
        self.assertEqual("original_value", response.json['uneditable'])

        ext_app = self._setup_app_with_request_handler(_update_handler,
                                                       'PUT')
        ext_response = ext_app.put("/dummy_resources/1",
                                   {'uneditable': "new_value"})
        self.assertEqual("new_value", ext_response.json['uneditable'])

    def _setup_app_with_request_handler(self, handler, verb):
        req_ext = extensions.RequestExtension(verb,
                                              '/dummy_resources/:(id)',
                                              handler)
        manager = SimpleExtensionManager(None, None, req_ext)
        return _setup_extensions_test_app(manager)


class ExtensionManagerTest(base.BaseTestCase):

    def test_invalid_extensions_are_not_registered(self):

        class InvalidExtension(object):
            """Invalid extension.

            This Extension doesn't implement extension methods :
            get_name, get_description, get_namespace and get_updated
            """
            def get_alias(self):
                return "invalid_extension"

        ext_mgr = extensions.ExtensionManager('')
        ext_mgr.add_extension(InvalidExtension())
        ext_mgr.add_extension(ext_stubs.StubExtension("valid_extension"))

        self.assertIn('valid_extension', ext_mgr.extensions)
        self.assertNotIn('invalid_extension', ext_mgr.extensions)


class PluginAwareExtensionManagerTest(base.BaseTestCase):

    def test_unsupported_extensions_are_not_loaded(self):
        stub_plugin = ext_stubs.StubPlugin(supported_extensions=["e1", "e3"])
        plugin_info = {constants.CORE: stub_plugin}
        with mock.patch("tacker.api.extensions.PluginAwareExtensionManager."
                        "check_if_plugin_extensions_loaded"):
            ext_mgr = extensions.PluginAwareExtensionManager('', plugin_info)

            ext_mgr.add_extension(ext_stubs.StubExtension("e1"))
            ext_mgr.add_extension(ext_stubs.StubExtension("e2"))
            ext_mgr.add_extension(ext_stubs.StubExtension("e3"))

            self.assertIn("e1", ext_mgr.extensions)
            self.assertNotIn("e2", ext_mgr.extensions)
            self.assertIn("e3", ext_mgr.extensions)

    def test_extensions_are_not_loaded_for_plugins_unaware_of_extensions(self):
        class ExtensionUnawarePlugin(object):
            """This plugin does not implement supports_extension method.

            Extensions will not be loaded when this plugin is used.
            """
            pass

        plugin_info = {constants.CORE: ExtensionUnawarePlugin()}
        ext_mgr = extensions.PluginAwareExtensionManager('', plugin_info)
        ext_mgr.add_extension(ext_stubs.StubExtension("e1"))

        self.assertNotIn("e1", ext_mgr.extensions)

    def test_extensions_not_loaded_for_plugin_without_expected_interface(self):

        class PluginWithoutExpectedIface(object):
            """Does not implement get_foo method as expected by extension."""
            supported_extension_aliases = ["supported_extension"]

        plugin_info = {constants.CORE: PluginWithoutExpectedIface()}
        with mock.patch("tacker.api.extensions.PluginAwareExtensionManager."
                        "check_if_plugin_extensions_loaded"):
            ext_mgr = extensions.PluginAwareExtensionManager('', plugin_info)
            ext_mgr.add_extension(ext_stubs.ExtensionExpectingPluginInterface(
                "supported_extension"))

            self.assertNotIn("e1", ext_mgr.extensions)

    def test_extensions_are_loaded_for_plugin_with_expected_interface(self):

        class PluginWithExpectedInterface(object):
            """Implements get_foo method as expected by extension."""
            supported_extension_aliases = ["supported_extension"]

            def get_foo(self, bar=None):
                pass

        plugin_info = {constants.CORE: PluginWithExpectedInterface()}
        with mock.patch("tacker.api.extensions.PluginAwareExtensionManager."
                        "check_if_plugin_extensions_loaded"):
            ext_mgr = extensions.PluginAwareExtensionManager('', plugin_info)
            ext_mgr.add_extension(ext_stubs.ExtensionExpectingPluginInterface(
                "supported_extension"))

            self.assertIn("supported_extension", ext_mgr.extensions)

    def test_extensions_expecting_tacker_plugin_interface_are_loaded(self):
        class ExtensionForQuamtumPluginInterface(ext_stubs.StubExtension):
            """This Extension does not implement get_plugin_interface method.

            This will work with any plugin implementing TackerPluginBase
            """
            pass
        stub_plugin = ext_stubs.StubPlugin(supported_extensions=["e1"])
        plugin_info = {constants.CORE: stub_plugin}

        with mock.patch("tacker.api.extensions.PluginAwareExtensionManager."
                        "check_if_plugin_extensions_loaded"):
            ext_mgr = extensions.PluginAwareExtensionManager('', plugin_info)
            ext_mgr.add_extension(ExtensionForQuamtumPluginInterface("e1"))

            self.assertIn("e1", ext_mgr.extensions)

    def test_extensions_without_need_for__plugin_interface_are_loaded(self):
        class ExtensionWithNoNeedForPluginInterface(ext_stubs.StubExtension):
            """This Extension does not need any plugin interface.

            This will work with any plugin implementing TackerPluginBase
            """
            def get_plugin_interface(self):
                return None

        stub_plugin = ext_stubs.StubPlugin(supported_extensions=["e1"])
        plugin_info = {constants.CORE: stub_plugin}
        with mock.patch("tacker.api.extensions.PluginAwareExtensionManager."
                        "check_if_plugin_extensions_loaded"):
            ext_mgr = extensions.PluginAwareExtensionManager('', plugin_info)
            ext_mgr.add_extension(ExtensionWithNoNeedForPluginInterface("e1"))

            self.assertIn("e1", ext_mgr.extensions)

    def test_extension_loaded_for_non_core_plugin(self):
        class NonCorePluginExtenstion(ext_stubs.StubExtension):
            def get_plugin_interface(self):
                return None

        stub_plugin = ext_stubs.StubPlugin(supported_extensions=["e1"])
        plugin_info = {constants.DUMMY: stub_plugin}
        with mock.patch("tacker.api.extensions.PluginAwareExtensionManager."
                        "check_if_plugin_extensions_loaded"):
            ext_mgr = extensions.PluginAwareExtensionManager('', plugin_info)
            ext_mgr.add_extension(NonCorePluginExtenstion("e1"))

            self.assertIn("e1", ext_mgr.extensions)

    def test_unloaded_supported_extensions_raises_exception(self):
        stub_plugin = ext_stubs.StubPlugin(
            supported_extensions=["unloaded_extension"])
        plugin_info = {constants.CORE: stub_plugin}
        self.assertRaises(exceptions.ExtensionsNotFound,
                          extensions.PluginAwareExtensionManager,
                          '', plugin_info)


class ExtensionControllerTest(testlib_api.WebTestCase):

    def setUp(self):
        super(ExtensionControllerTest, self).setUp()
        self.test_app = _setup_extensions_test_app()

    def test_index_gets_all_registerd_extensions(self):
        response = self.test_app.get("/extensions." + self.fmt)
        res_body = self.deserialize(response)
        foxnsox = res_body["extensions"][0]

        self.assertEqual("FOXNSOX", foxnsox["alias"])
        self.assertEqual("http://www.fox.in.socks/api/ext/pie/v1.0",
                         foxnsox["namespace"])

    def test_extension_can_be_accessed_by_alias(self):
        response = self.test_app.get("/extensions/FOXNSOX." + self.fmt)
        foxnsox_extension = self.deserialize(response)
        foxnsox_extension = foxnsox_extension['extension']
        self.assertEqual("FOXNSOX", foxnsox_extension["alias"])
        self.assertEqual("http://www.fox.in.socks/api/ext/pie/v1.0",
                         foxnsox_extension["namespace"])

    def test_show_returns_not_found_for_non_existent_extension(self):
        response = self.test_app.get("/extensions/non_existent" + self.fmt,
                                     status="*")

        self.assertEqual(404, response.status_int)


def app_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)
    return ExtensionsTestApp(conf)


def setup_base_app(test):
    base.BaseTestCase.config_parse()
    app = config.load_paste_app('extensions_test_app')
    return app


def setup_extensions_middleware(extension_manager=None):
    extension_manager = (extension_manager or
                         extensions.ExtensionManager(extensions_path))
    base.BaseTestCase.config_parse()
    app = config.load_paste_app('extensions_test_app')
    return extensions.ExtensionMiddleware(app, ext_mgr=extension_manager)


def _setup_extensions_test_app(extension_manager=None):
    return webtest.TestApp(setup_extensions_middleware(extension_manager))


class SimpleExtensionManager(object):

    def __init__(self, resource_ext=None, action_ext=None, request_ext=None):
        self.resource_ext = resource_ext
        self.action_ext = action_ext
        self.request_ext = request_ext

    def get_resources(self):
        resource_exts = []
        if self.resource_ext:
            resource_exts.append(self.resource_ext)
        return resource_exts

    def get_actions(self):
        action_exts = []
        if self.action_ext:
            action_exts.append(self.action_ext)
        return action_exts

    def get_request_extensions(self):
        request_extensions = []
        if self.request_ext:
            request_extensions.append(self.request_ext)
        return request_extensions
