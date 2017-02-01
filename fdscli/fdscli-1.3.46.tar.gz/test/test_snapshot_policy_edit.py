# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#

from test.base_cli_test import BaseCliTest
import mock_functions
from mock import patch
from fdscli.model.volume.recurrence_rule import Frequency

class TestSnapshotPolicyEdit(BaseCliTest):
    '''
    Created on Apr 30, 2015
    
    @author: nate
    '''
    
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.get_snapshot_policy", side_effect=mock_functions.getSnapshotPolicy)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.list_snapshot_policies", side_effect=mock_functions.listSnapshotPolicies)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.edit_snapshot_policy", side_effect=mock_functions.editSnapshotPolicy)
    def test_policy_edit_defaults(self, mockEdit, mockList, mockGet):
        '''
        Test that a snapshot policy edited with the minimal set of data fills in the correct defaults
        '''
        
        args = ["snapshot_policy", "edit", "-volume_id=3", "-name=MyPolicy", "-policy_id=1"]
        
        self.callMessageFormatter(args)
        self.cli.run( args )
        
        assert mockEdit.call_count == 1
        assert mockList.call_count == 1
        
        policy = mockEdit.call_args[0][1]
        
        assert policy.name == "MyPolicy"
        assert policy.id == "1"
        assert hasattr( policy, "retention" ) == False
        
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.get_snapshot_policy", side_effect=mock_functions.getSnapshotPolicy)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.list_snapshot_policies", side_effect=mock_functions.listSnapshotPolicies)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.edit_snapshot_policy", side_effect=mock_functions.editSnapshotPolicy)
    def test_policy_edit(self, mockEdit, mockList, mockGet):
        '''
        Test policy edit with command line arguments
        '''
        
        args = ["snapshot_policy", "edit", "-volume_id=3", "-policy_id=1", "-name=MyPolicy", "-frequency=WEEKLY", "-hour", "3", "12", "-day_of_week", "SU", "WE", "-minute", "15", "30", "45"]
        
        self.callMessageFormatter(args)
        self.cli.run(args)        
        
        assert mockEdit.call_count == 1
        assert mockList.call_count == 1
        
        policy = mockEdit.call_args[0][1]
        
        assert policy.name == "MyPolicy"
        assert policy.recurrence_rule.frequency.name == "WEEKLY"
        assert policy.recurrence_rule.byhour == [3, 12]
        assert policy.recurrence_rule.byminute == [15,30,45]
        assert policy.recurrence_rule.byday == ["SU", "WE" ]
        
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.get_snapshot_policy", side_effect=mock_functions.getSnapshotPolicy)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.list_snapshot_policies", side_effect=mock_functions.listSnapshotPolicies)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.edit_snapshot_policy", side_effect=mock_functions.editSnapshotPolicy)
    def test_policy_edit_hourly(self, mockEdit, mockList, mockGet):
        '''
        Test policy edit with command line arguments
        '''
        
        args = ["snapshot_policy", "edit", "-volume_id=3", "-policy_id=1", "-name=MyPolicy", "-frequency=HOURLY", "-retention=360"]
        
        self.callMessageFormatter(args)
        self.cli.run(args)        
        
        assert mockEdit.call_count == 1
        assert mockList.call_count == 1
        
        policy = mockEdit.call_args[0][1]
        
        assert policy.name == "MyPolicy"
        assert policy.recurrence_rule.frequency.name == "HOURLY", "Expected HOURLY but got {}".format( policy.recurrence_rule.frequency.name)
        assert policy.recurrence_rule.byhour == None, "Expected None but got {}".format( policy.recurrence_rule.byhour)
        assert policy.recurrence_rule.byminute == [15, 30, 45], "Expected [15, 30, 45] but got {}".format( policy.recurrence_rule.byminute)
        assert policy.recurrence_rule.byday == None, "Expected None but got {}".format( policy.recurrence_rule.byday)
        assert policy.retention_time_in_seconds == 360, "Expected 360 but got {}".format( policy.retention_time_in_seconds)
        
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.get_snapshot_policy", side_effect=mock_functions.getSnapshotPolicy)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.list_snapshot_policies", side_effect=mock_functions.listSnapshotPolicies)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.edit_snapshot_policy", side_effect=mock_functions.editSnapshotPolicy)
    def test_policy_edit_restrictions(self, mockEdit, mockList, mockGet):  
        '''
        test policy edit and check the restrictions are being enforced
        '''
        #no id
        args = [ "snapshot_policy", "edit", "-volume_id=3", "-frequency=DAILY", "-day_of_week", "SU", "MO", "-name=MyPolicy" ]
        
        self.callMessageFormatter(args)
        self.cli.run( args )
        
        assert mockEdit.call_count == 0
        assert mockList.call_count == 0
        
        # make sure days don't make it in if its daily
        args.append( "-policy_id=1" )
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        assert mockEdit.call_count == 1
        assert mockList.call_count == 1
        
        policy = mockEdit.call_args[0][1]
        
        assert policy.recurrence_rule.byday is None
        
        #make sure month, day of month and day of year don't make it in a weekly
        args = ["snapshot_policy", "edit", "-volume_id=3", "-policy_id=1", "-name=MyPolicy", "-frequency=WEEKLY", "-day_of_month", "15", "-day_of_year", "255", "-month", "2", "5", "-day_of_week", "TH"]
        
        self.callMessageFormatter(args)
        self.cli.run(args)

        assert mockEdit.call_count == 2
        assert mockList.call_count == 2
        
        policy = mockEdit.call_args[0][1]
        
        assert policy.recurrence_rule.bymonth is None
        assert policy.recurrence_rule.byyearday is None
        assert policy.recurrence_rule.bymonthday is None
        assert policy.recurrence_rule.byday == ["TH"]
        
        #make sure month and day of the year dont' make it in the monthly
        args[5] = "-frequency=MONTHLY"
        
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        assert mockEdit.call_count == 3
        assert mockList.call_count == 3
        
        policy = mockEdit.call_args[0][1]
        
        assert policy.recurrence_rule.bymonth is None
        assert policy.recurrence_rule.byyearday is None
        assert policy.recurrence_rule.bymonthday == [15]
        assert policy.recurrence_rule.byday == ["TH"]
        
        #make sure everything gets in if its yearly
        args[5] = "-frequency=YEARLY"
        
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        assert mockEdit.call_count == 4
        assert mockList.call_count == 4
        
        policy = mockEdit.call_args[0][1]
        
        assert policy.recurrence_rule.bymonth == [2,5]
        assert policy.recurrence_rule.byyearday == [255]
        assert policy.recurrence_rule.bymonthday == [15]
        assert policy.recurrence_rule.byday == ["TH"]  
        
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.get_snapshot_policy", side_effect=mock_functions.getSnapshotPolicy)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.list_snapshot_policies", side_effect=mock_functions.listSnapshotPolicies)
    @patch( "fdscli.services.snapshot_policy_service.SnapshotPolicyService.edit_snapshot_policy", side_effect=mock_functions.editSnapshotPolicy)
    def test_policy_edit_data(self, mockEdit, mockList, mockGet):
        '''
        Try to create a snapshot policy using a JSON string instead of arguments
        '''
        
        jString = "{\"uid\":1,\"name\":\"MyPolicy\",\"retentionTime\": {\"seconds\":86400, \"nanos\":0},\"timelineTime\":0,\"recurrenceRule\":{\"FREQ\":\"WEEKLY\",\"BYDAY\":[\"SU\"]}}"
        
        args = ["snapshot_policy", "edit", "-volume_id=3", "-data=" + jString]
        self.callMessageFormatter(args)
        self.cli.run(args)
        
        assert mockEdit.call_count == 1
        assert mockList.call_count == 1
        
        policy = mockEdit.call_args[0][1]
        
        assert policy.name == "MyPolicy"
        assert policy.id == 1
        assert policy.recurrence_rule.frequency.name == "WEEKLY"
        assert policy.retention_time_in_seconds == 86400
        assert policy.timeline_time == 0
        assert policy.recurrence_rule.byday == ["SU"]        
        
