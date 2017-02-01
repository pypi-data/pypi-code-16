# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#
import time
from test.base_cli_test import BaseCliTest
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.event.event import Event, EventContent
from fdscli.model.platform.domain import Domain
from fdscli.model.platform.node import Node
from fdscli.model.platform.service import Service
from fdscli.model.task.safeguard_task_status import SafeGuardTaskStatus
from fdscli.model.volume.safeguard_preset import SafeGuardPreset
from fdscli.model.volume.snapshot import Snapshot
from fdscli.model.volume.snapshot_policy import SnapshotPolicy
from fdscli.model.volume.subscription import Subscription
from fdscli.model.volume.volume import Volume
from fdscli.services.response_writer import ResponseWriter
from fdscli.model.volume.recurrence_rule import RecurrenceRule
from fdscli.model.platform.address import Address
from fdscli.model.admin.tenant import Tenant
from fdscli.model.platform.service_status import ServiceStatus
from fdscli.model.event.event_source_info import EventSourceInfo
from fdscli.model.event.event_descriptor import EventDescriptor
from fdscli.model.event.event_severity import EventSeverity

class TestResponseWriterPrep(BaseCliTest):
    '''
    Created on May 1, 2015
    
    @author: nate
    '''

    def test_prep_volume(self):
        '''
        Test that the volume table preparation is done properly
        '''
        
        volumes = []
        volume = Volume()
        volume.id = 400
        volume.name = "TestVol"
        volume.data_protection_policy.commit_log_retention = 100000
        volume.qos_policy.iops_min = 0
        volume.qos_policy.iops_max = 100
        volume.qos_policy.priority = 9
        volume.status.current_usage.size = 30
        volume.status.current_usage.unit = "GB"
        volume.media_policy = "SSD"
        volume.status.last_capacity_firebreak = 0
        volume.status.last_performance_firebreak = 0
        volume.state = "ACTIVE"
        tenant = Tenant()
        tenant.id = 12
        tenant.name = "MyTenant"
        volume.tenant = tenant
        volumes.append( volume )
        
        table = ResponseWriter.prep_volume_for_table(self.auth, volumes)
        
        row = table[0]
        
        assert row["ID"] == volume.id
        assert row["Name"] == volume.name
        assert row["State"] == volume.state
        assert row["Media Policy"] == volume.media_policy
        assert row["IOPs Guarantee"] == "None"
        assert row["IOPs Limit"] == volume.qos_policy.iops_max
        assert row["Tenant"] == volume.tenant.name
        assert row["Safeguard Type"] == "None"
        assert row["Usage"] == "30.0 GB"
        
    def test_prep_nodes(self):
        '''
        Test that the node preparation is done properly
        '''
        node = Node()
        node.name = "FakeNode"
        address = Address()
        address.ipv4address = "10.12.14.15"
        address.ipv6address = "noclue"
        node.address = address
        node.id = "21ABC"
        node.state = "UP"
        
        node.services["AM"]  = [Service(a_type="AM",name="AM")]
        node.services["DM"]  = [Service(a_type="DM",name="DM")]
        node.services["PM"]  = [Service(a_type="PM",name="PM")]
        node.services["SM"]  = [Service(a_type="SM",name="SM")]  
        
        nodes = [node]
        
        table = ResponseWriter.prep_node_for_table(self.auth, nodes)              
        row = table[0]
        
        assert row["Name"] == node.name
        assert row["ID"] == node.id
        assert row["State"] == node.state
        assert row["IP V4 Address"] == node.address.ipv4address
        
    def test_prep_services(self):
        '''
        Test that the service preparation is done properly
        '''
        node = Node()
        node.name = "FakeNode"
        address = Address()
        address.ipv4address = "10.12.14.15"
        address.ipv6address = "noclue"
        node.address = address
        node.id = "21ABC"
        node.state = "UP"
        
        node.services["AM"]  = [Service(a_type="AM",name="AM",status=ServiceStatus(state="NOT_RUNNING"),an_id=1,port=7000)]
        node.services["DM"]  = [Service(a_type="DM",name="DM",status=ServiceStatus(state="RUNNING"),an_id=2, port=7001)]
        node.services["PM"]  = [Service(a_type="PM",name="PM",status=ServiceStatus(state="RUNNING"),an_id=3, port=7002)]
        node.services["SM"]  = [Service(a_type="SM",name="SM",an_id=4, port=7003)]  
        
        nodes = [node]
        
        table = ResponseWriter.prep_services_for_table(self.auth, nodes)
        am = None
        pm = None
        sm = None
        dm = None
        
        for row in table:
            s_type = row["Service Type"]
            
            if (s_type == "AM"):
                am = row
                
            if (s_type == "DM"):
                dm = row
            
            if (s_type == "PM"):
                pm = row
            
            if (s_type == "SM"):
                sm = row
        
        assert am["Service Type"] == "AM"
        assert am["Service ID"] == 1
        assert am["Node Name"] == node.name
        assert am["Node ID"] == node.id
        assert am["State"] == "NOT_RUNNING"
        
        assert dm["Service Type"] == "DM"
        assert dm["Service ID"] == 2
        assert dm["Node Name"] == node.name
        assert dm["Node ID"] == node.id
        assert dm["State"] == "RUNNING"
        
        assert pm["Service Type"] == "PM"
        assert pm["Service ID"] == 3
        assert pm["Node Name"] == node.name
        assert pm["Node ID"] == node.id
        assert pm["State"] == "RUNNING"
        
        assert sm["Service Type"] == "SM"
        assert sm["Service ID"] == 4
        assert sm["Node Name"] == node.name
        assert sm["Node ID"] == node.id
        assert sm["State"] == "RUNNING"        
        
    def test_prep_snapshot(self):
        '''
        Test that a snapshot gets prepped for the table properly
        '''
        
        snapshot = Snapshot()
        snapshot.id = 100
        snapshot.name = "FirstSnap"
        snapshot.timeline_time = 30000
        snapshot.retention = 0

        t = time.time()
        
        snapshot.created = t
        snapshots = [snapshot]
        
        table = ResponseWriter.prep_snapshot_for_table(self.auth, snapshots)
        row = table[0]
        
        created = time.localtime( snapshot.created )
        created = time.strftime( "%c", created )
        
        assert row["ID"] == snapshot.id
        assert row["Name"] == snapshot.name
        assert row["Created"] == created
        assert row["Retention"] == "Forever"
        
    def test_prep_snapshot_policy(self):
        '''
        Test that snapshot policies are being prepped for table properly
        '''
        snapshot_policy = SnapshotPolicy()
        snapshot_policy.id = 20
        snapshot_policy.name = "TestPolicy"
        snapshot_policy.retention = 0
        snapshot_policy.timeline_time = 0
        
        rule = RecurrenceRule()
        rule.byhour = [3]
        rule.byminute = [30]
        rule.byday = ["SU", "FR"]
        rule.frequency = "MONTHLY"
        
        snapshot_policy.recurrence_rule = rule
        
        policies = [snapshot_policy]
        
        table = ResponseWriter.prep_snapshot_policy_for_table(self.auth, policies)
        row = table[0]
        
        assert row["ID"] == snapshot_policy.id
        assert row["Name"] == snapshot_policy.name
        assert row["Retention"] == "Forever"
        assert row["Recurrence Rule"] == '{"BYMINUTE": [30], "FREQ": "MONTHLY", "BYHOUR": [3], "BYDAY": ["SU", "FR"]}'
        
    def test_prep_domains(self):
        '''
        Test that the domains get prepped properly for the table
        '''
        domain = Domain()
        
        domain.id = 1
        domain.name = "Fremont"
        domain.site = "US"
        
        domains = [domain]
        
        table = ResponseWriter.prep_domains_for_table(self.auth, domains)
        row = table[0]
        
        assert row["ID"] == domain.id
        assert row["Name"] == domain.name
        assert row["Site"] == domain.site

    def test_prep_events_for_table(self):
        '''Produce tabular data from a list of event objects.
        '''
        
        srcinfo=EventSourceInfo(1, 1, "10.11.12.13", 1234, "TestSVC.exe", 1, "TestSVC", "1.2.3", 1, "local", attributes={})
        desc = EventDescriptor(key="test.KEY1", categories=["SYSTEM","STORAGE"], severity=EventSeverity.info, message_format="Message for event $n$")
        event1 = Event(default_message="Message for event 1", 
                       event_message="Message for event 1",
                       creation_time=0, 
                       event_content=EventContent(descriptor=desc, 
                                                  source_info=srcinfo,
                                                  attributes={"n":1},
                                                  timestamp={"seconds" : 0, "nanos":0}))
        events = [event1]

        event2 = Event(default_message="Message for event 2", 
                       event_message="Message for event 2",
                       creation_time=1, 
                       event_content=EventContent(descriptor=desc, 
                                                  source_info=srcinfo,
                                                  attributes={"n":2},
                                                  timestamp={"seconds" : 1, "nanos":0}))
        events.append(event2)

        table = ResponseWriter.prep_events_for_table(self.auth, events)
        ResponseWriter.writeTabularData(table)

        row1 = table[0]
        assert row1["Message"] == event1.default_message

        row2 = table[1]
        assert row2["Message"] == event2.default_message

    def test_prep_f1credentials_for_table(self):
        '''Produce tabular data from a list of F1 named credential objects.
        '''
        credential1 = NamedCredential(digest="YYZ", user_id=27, name="credential1")
        credential1.url = "https://hannah.reid:secret@localhost:7777"
        named_credentials = [credential1]

        credential2 = NamedCredential(digest="XYZ", user_id=26, name="credential1")
        credential2.protocol = "https"
        credential2.username = "hannah.reid"
        credential2.password = "secret"
        credential2.hostname = "localhost"
        credential2.port = 7777
        credential2.url = "https://hannah.reid:secret@localhost:7777"
        named_credentials.append(credential2)

        table = ResponseWriter.prep_f1credentials_for_table(self.auth, named_credentials)
        ResponseWriter.writeTabularData(table)

        row1 = table[0]
        assert row1["Named Credential ID"] == credential1.digest
        assert row1["User ID"] == credential1.user_id
        assert row1["Name"] == credential1.name
        assert row1["OM Url"] == credential1.url

        row2 = table[1]
        assert row2["Named Credential ID"] == credential2.digest
        assert row2["User ID"] == credential2.user_id

    def test_prep_s3credentials_for_table(self):
        '''Produce tabular data from a list of S3 named credential objects.
        '''
        cred1 = NamedCredential(digest="XZZ", user_id=27, name="s3cred1")
        cred1.bucketname = "tinpail"
        cred1.url = "http://s3.amazon.com"
        cred1.s3credentials.access_key_id = "A18/26"
        cred1.s3credentials.secret_key = "secret1"
        named_credentials = [cred1]

        cred2 = NamedCredential(digest="XWZ", user_id=28, name="s3cred2")
        cred2.bucketname = "tinpail"
        cred2.url = "http://s3.amazon.com"
        cred2.s3credentials.access_key_id = "2G8/96"
        cred2.s3credentials.secret_key = "secret2"
        named_credentials.append(cred2)

        table = ResponseWriter.prep_s3credentials_for_table(self.auth, named_credentials)
        ResponseWriter.writeTabularData(table)

        row1 = table[0]
        assert row1["Named Credential ID"] == cred1.digest
        assert row1["User ID"] == cred1.user_id
        assert row1["Name"] == cred1.name
        assert row1["Url"] == cred1.url
        assert row1["Bucket Name"] == cred1.bucketname
        assert row1["S3 Access Key"] == cred1.s3credentials.access_key_id
        assert row1["S3 Secret Key"] == cred1.s3credentials.secret_key

        row2 = table[1]
        assert row2["Named Credential ID"] == cred2.digest
        assert row2["Name"] == cred2.name

    def test_prep_safeguard_presets(self):
        '''Produce tabular data from a list of SafeGuard preset objects.
        '''
        preset1 = SafeGuardPreset()
        preset1.id = 5
        preset1.name = "Test_SafeGuard_Preset1"
        presets = [preset1]

        rule2 = RecurrenceRule(frequency="HOURLY")
        preset2 = SafeGuardPreset(recurrence_rule=rule2)
        preset2.id = 17
        preset2.name = "Test_SafeGuard_Preset2"
        presets.append(preset2)

        table = ResponseWriter.prep_safeguard_presets(presets)
        ResponseWriter.writeTabularData(table)

        row1 = table[0]
        assert row1["ID"] == preset1.id
        assert row1["Name"] == preset1.name
        assert row1["Recurrence Rule"] == "{}"
        row2 = table[1]
        assert row2["ID"] == preset2.id
        assert row2["Name"] == preset2.name
        assert row2["Recurrence Rule"] == '{"FREQ": "HOURLY"}'

    def test_prep_safeguard_tasks(self):
        '''Produce tabular data from a list of SafeGuard tasks with status.
        '''
        task1 = SafeGuardTaskStatus(uuid='a12345', volume_id=36, endpoint='there', exported_name='replica36', time_started='1483637602')
        tasks = [task1]
        task2 = SafeGuardTaskStatus(uuid='b54321', volume_id=37, endpoint='elsewhere', bucket_name='tinpail', exported_name='0/1/2/3')
        tasks.append(task2)

        table = ResponseWriter.prep_safeguard_tasks_for_table(self.auth, tasks)
        ResponseWriter.writeTabularData(table)

        row1 = table[0]
        assert row1['Volume ID'] == task1.volume_id
        assert row1['Remote Cloud'] == task1.endpoint
        assert row1['Remote Volume/Bucket'] == task1.exported_name
        assert row1['Task ID'] == task1.uuid

        row2 = table[1]
        assert row2['Volume ID'] == task2.volume_id
        assert row2['Remote Cloud'] == task2.endpoint
        assert row2['Remote Volume/Bucket'] == task2.bucket_name
        assert row2['Task ID'] == task2.uuid
        assert row2['Request Time'] == 'unknown'

    def test_prep_subscriptions_for_table(self):
        '''Produce tabular data from a list of subscription objects.
        '''
        sub1 = Subscription(digest="ABC", name="subscription1", volume_id=13)
        subscriptions = [sub1]

        rule2 = RecurrenceRule(frequency="DAILY")
        sub2 = Subscription(digest="ABF", name="subscription2", volume_id=13, recurrence_rule=rule2)
        subscriptions.append(sub2)

        credentials = dict()
        credential3 = NamedCredential(digest="XYZ", user_id=26, name="credential3")
        credential3.bucketname = 'tinpail'
        credentials['XYZ'] = credential3

        rule3 = RecurrenceRule(frequency="MINUTELY")
        sub3 = Subscription(digest="ACA", name="subscription3", volume_id=33,
            recurrence_rule=rule3, named_credential=credential3)
        subscriptions.append(sub3)

        table = ResponseWriter.prep_subscriptions_for_table(subscriptions, credentials)
        ResponseWriter.writeTabularData(table)

        row1 = table[0]
        assert row1["Subscription ID"] == sub1.digest
        assert row1["Volume ID"] == sub1.volume_id
        assert row1["Name"] == sub1.name
        assert row1["Recurrence Rule"] == "All Snapshots"

        row3 = table[2]
        assert row3["Subscription ID"] == sub3.digest
        assert row3["Volume ID"] == sub3.volume_id
        assert row3["SafeGuard Type"] == 'CDM-Snap'
        assert row3["Name"] == sub3.name
        assert row3["Named Credential"] == sub3.named_credential.name
        assert row3["Remote Volume/Bucket"] == sub3.named_credential.bucketname
