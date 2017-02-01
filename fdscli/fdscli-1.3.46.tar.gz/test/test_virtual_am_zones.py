'''
Created on Oct 13, 2016

@author: chaithra, Neil
'''
import mock_functions
from fdscli.plugins.abstract_plugin import AbstractPlugin
from fdscli.plugins.zone_plugin import ZonePlugin
from mock import patch
from test.base_cli_test import BaseCliTest


class ZoneTest(BaseCliTest):
    '''
    This test class handles listing zones and creating/deleting zones
    '''

    @patch( "fdscli.services.zone_service.ZoneService.list_zones", side_effect=mock_functions.listZones)
    def test_listZones(self, mockService):

        args = ["zone", "list", "-format=json"]

        print("Making call: zone list -format=json")

        self.cli.run(args)

        self.callMessageFormatter(args)

        assert mockService.call_count == 1

        print("test_listZones passed.\n\n")

    @patch( "fdscli.services.zone_service.ZoneService.list_zones", side_effect=mock_functions.listNoZones)
    def test_listZones_none(self, mockList):
        '''
        Test if there are no zones to list
        '''

        args = ["zone", "list"]

        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockList.call_count == 1

    @patch("fdscli.services.zone_service.ZoneService.list_zones", side_effect=mock_functions.errorGen)
    def test_listzonesError(self, mockList):
        '''
        Test what happens when list zones gets an error
        '''

        args = ["zone", "list"]

        self.callMessageFormatter(args)

        exception = None

        try:
            self.cli.run(args)
        except SystemExit as se:
            exception = se

        assert exception != None, "Expected to get an exception but got none."


    @patch("fdscli.services.node_service.NodeService.list_nodes", side_effect=mock_functions.listNodesForZone)
    @ patch("fdscli.plugins.zone_plugin.ZonePlugin.list_zones", side_effect=mock_functions.listPluginZones)
    @ patch("fdscli.services.zone_service.ZoneService.list_zones", side_effect=mock_functions.listZones)
    @ patch("fdscli.services.zone_service.ZoneService.create_zone", side_effect=mock_functions.createZone)
    def test_create(self, zoneCreate, listCall, listPluginZone, listNodes):
        '''
        testing zone create
        '''

        args = ["zone", "create", "-iface=eth0", "-name=zone1", "-id=1", "-vip=10.0.1.1", "-service_ids=2,3"]

        self.callMessageFormatter(args)
        self.cli.run(args)

        zone = zoneCreate.call_args[0][0]

        assert zoneCreate.call_count == 1
        assert zone.name == "zone1"
        print(zone.zid)
        assert zone.zid == 1

        print("test_create passed.\n\n")

    @patch("fdscli.plugins.zone_plugin.ZonePlugin.get_node_list", side_effect=mock_functions.listNodesForZone)
    def test_create_parser_positive(self, listNodes):
        '''
        testing parser - positive test case:
        zone create -name test -vip 192.168.0.1 -service_ids 2,3
        '''
        args = {}
        args[AbstractPlugin.zone_id] = None
        args[AbstractPlugin.zone_name] = "tempName"
        args[AbstractPlugin.zone_type] = "vamg"
        args[AbstractPlugin.zone_iface] = "eth0"
        args[AbstractPlugin.zone_vip] = "192.168.0.1"
        args[AbstractPlugin.zone_service_ids] = "2,3"
        zonePlugin = ZonePlugin()
        zoneObj = zonePlugin.generate_zone_obj(args)
        assert zoneObj is not None
        assert zonePlugin.validate_zone_input(zoneObj, zone_service_ids=args[AbstractPlugin.zone_service_ids]) is True
        return

    @patch("fdscli.plugins.zone_plugin.ZonePlugin.get_node_list", side_effect=mock_functions.listNodesForZone)
    def test_create_parser_invalid_vip(self, listNodes):
        '''
        testing parser - negative test case:
        zone create -name test -vip 192.168.0.0 -service_ids 2,3
        '''
        args = {}
        args[AbstractPlugin.zone_id] = None
        args[AbstractPlugin.zone_name] = "tempName"
        args[AbstractPlugin.zone_type] = "vamg"
        args[AbstractPlugin.zone_iface] = "eth0"
        args[AbstractPlugin.zone_vip] = "192.168.0.0"
        args[AbstractPlugin.zone_service_ids] = "2,3"
        zonePlugin = ZonePlugin()
        zoneObj = zonePlugin.generate_zone_obj(args)
        assert zoneObj is not None
        assert zonePlugin.validate_zone_input(zoneObj, zone_service_ids=args[AbstractPlugin.zone_service_ids]) is False
        return

    @patch("fdscli.plugins.zone_plugin.ZonePlugin.get_node_list", side_effect=mock_functions.listNodesForZone)
    def test_create_parser_invalid_vip2(self, listNodes):
        '''
        testing parser - negative test case:
        zone create -name test -vip 192.168.0.255 -service_ids 2,3
        '''
        args = {}
        args[AbstractPlugin.zone_id] = None
        args[AbstractPlugin.zone_name] = "tempName"
        args[AbstractPlugin.zone_type] = "vamg"
        args[AbstractPlugin.zone_iface] = "eth0"
        args[AbstractPlugin.zone_vip] = "192.168.0.255"
        args[AbstractPlugin.zone_service_ids] = "2,3"
        zonePlugin = ZonePlugin()
        zoneObj = zonePlugin.generate_zone_obj(args)
        assert zoneObj is not None
        assert zonePlugin.validate_zone_input(zoneObj, zone_service_ids=args[AbstractPlugin.zone_service_ids]) is False
        return

    @patch("fdscli.services.zone_service.ZoneService.get_zone", side_effect=mock_functions.getZone)
    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.prep_zone_for_table", side_effect=mock_functions.empty_two)
    @patch("fdscli.plugins.zone_plugin.ZonePlugin.list_zones", side_effect=mock_functions.listZones)
    def test_get_zone(self, mockService, mockPrep, mockTabular, listCall):

        args = ["zone", "list", "-id=1"]

        print("Making call: zone list -id 1")

        self.cli.run(args)

        self.callMessageFormatter(args)

        print("test_get_zone passed.\n\n")


    @patch("fdscli.services.response_writer.ResponseWriter.writeTabularData", side_effect=mock_functions.empty_one)
    @patch("fdscli.services.response_writer.ResponseWriter.prep_zone_for_table", side_effect=mock_functions.empty_two)
    @patch("fdscli.services.zone_service.ZoneService.get_zone", side_effect=mock_functions.getZone)
    def test_get_zone_failure(self, mockService, mockPrep, mockTabular):

        # the side effect method here will only be successful for a 3
        args = ["zone", "list", "-id", "2"]

        print("Making call: zone list -id 2")

        exception = None

        try:
            self.cli.run(args)
        except SystemExit as se:
            exception = se;

        self.callMessageFormatter(args)

        assert exception != None, "Expected a SystemExit to be raised but it didn't happen"
        assert mockService.call_count == 1
        assert mockPrep.call_count == 0, "Expected the zone preparation method not to be called."
        assert mockTabular.call_count == 0, "Expected the zone write table method not to be called."

        print("test_get_zone_failure passed.\n\n")

    @patch("fdscli.services.zone_service.ZoneService.list_zones", side_effect=mock_functions.listZones)
    @patch("fdscli.services.zone_service.ZoneService.delete_zone", side_effect=mock_functions.deleteZone)
    def test_deletezone_by_id(self, mockDelete, listCall):

        args = ["zone", "delete", "-id=3"]

        self.callMessageFormatter(args)

        self.cli.run(args)

        assert mockDelete.call_count == 1

        id = mockDelete.call_args[0][0]

        print("Making sure we call the find method with the ID and get a certain name to the delete call.")

        assert id == "3"
