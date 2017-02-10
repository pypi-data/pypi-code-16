# Copyright (c) 2015, Formation Data Systems, Inc. All Rights Reserved.
#
from test.base_cli_test import BaseCliTest
from fdscli.model.admin.tenant import Tenant
from fdscli.model.admin.user import User
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.common.repository import Repository
from fdscli.model.common.s3credentials import S3Credentials
from fdscli.model.common.size import Size
from fdscli.model.platform.address import Address
from fdscli.model.platform.domain import Domain
from fdscli.model.platform.node import Node
from fdscli.model.platform.service import Service
from fdscli.model.platform.service_status import ServiceStatus
from fdscli.model.task.completion_status import CompletionStatus
from fdscli.model.task.safeguard_task_status import SafeGuardTaskStatus, SafeGuardTaskType
from fdscli.model.volume.data_protection_policy import DataProtectionPolicy
from fdscli.model.volume.exported_volume import ExportedVolume
from fdscli.model.volume.qos_policy import QosPolicy
from fdscli.model.volume.recurrence_rule import RecurrenceRule
from fdscli.model.volume.remote_volume import RemoteVolume
from fdscli.model.volume.safeguard_preset import SafeGuardPreset
from fdscli.model.volume.settings.nfs_settings import NfsSettings
from fdscli.model.volume.settings.object_settings import ObjectSettings
from fdscli.model.volume.snapshot_policy import SnapshotPolicy
from fdscli.model.volume.subscription import Subscription
from fdscli.model.volume.volume import Volume
from fdscli.model.volume.volume_status import VolumeStatus
from fdscli.utils.converters.admin.tenant_converter import TenantConverter
from fdscli.utils.converters.admin.user_converter import UserConverter
from fdscli.utils.converters.common.named_credential_converter import NamedCredentialConverter
from fdscli.utils.converters.common.repository_converter import RepositoryConverter
from fdscli.utils.converters.platform.domain_converter import DomainConverter
from fdscli.utils.converters.platform.node_converter import NodeConverter
from fdscli.utils.converters.platform.service_converter import ServiceConverter
from fdscli.utils.converters.task.safeguard_task_converter import SafeGuardTaskConverter
from fdscli.utils.converters.volume.exported_volume_converter import ExportedVolumeConverter
from fdscli.utils.converters.volume.preset_converter import PresetConverter
from fdscli.utils.converters.volume.remote_volume_converter import RemoteVolumeConverter
from fdscli.utils.converters.volume.subscription_converter import SubscriptionConverter
from fdscli.utils.converters.volume.volume_converter import VolumeConverter

from fdscli.model.event.event import Event, EventContent
from fdscli.model.event.event_descriptor import EventDescriptor
from fdscli.utils.converters.event.event_converter import EventConverter

from fdscli.model.event.event_source_info import EventSourceInfo
from fdscli.model.volume.safeguard_settings import SafeGuardSettings

from fdscli.utils.converters.event.event_source_info_converter import EventSourceInfoConverter


class TestConverters(BaseCliTest):
    '''
    Created on Jun 1, 2015
    
    @author: nate
    '''

    def test_object_volume_conversion(self):

        volume = Volume()
        volume.id = 34
        volume.name = "TestVolume"
        volume.media_policy = "SSD"

        status = VolumeStatus()
        status.last_capacity_firebreak = 0
        status.last_performance_firebreak = 10000
        status.state = "AVAILABLE"
        status.current_usage = Size( 12, "TB" )
        volume.status = status
        volume.application = "MS Access"

        tenant = Tenant()
        tenant.id = 9
        tenant.name = "UNC"
        volume.tenant = tenant

        settings = ObjectSettings()
        settings.max_object_size = Size( 1, "GB" )
        settings.encryption = "true"
        settings.compression = "true"
        settings.allow_mount = "false"
        settings.replica = "true"
        volume.settings = settings

        qos_policy = QosPolicy()
        qos_policy.priority = 6
        qos_policy.iops_max = 5000
        qos_policy.iops_min = 3000
        volume.qos_policy = qos_policy

        p_policy = DataProtectionPolicy()
        p_policy.commit_log_retention = 86400
        p_policy.preset_id = None

        s_policy = SnapshotPolicy()
        s_policy.retention_time_in_seconds = 86400
        s_policy.preset_id = None

        rule = RecurrenceRule()
        rule.byday = "MO"
        rule.frequency = "WEEKLY"
        rule.byhour = 14
        rule.byminute = 45
        s_policy.recurrence_rule = rule

        p_policy.snapshot_policies = [s_policy]
        volume.data_protection_policy = p_policy
        
        sg = SafeGuardSettings( safeguard_type="CDM")
        volume.safeguard_settings = sg

        j_str = VolumeConverter.to_json(volume)

        newVolume = VolumeConverter.build_volume_from_json(j_str)

        print j_str

        assert newVolume.name == "TestVolume"
        assert newVolume.id == 34
        assert newVolume.media_policy == "SSD"
        assert newVolume.status.state == "AVAILABLE"
        assert newVolume.status.last_capacity_firebreak == 0
        assert newVolume.status.last_performance_firebreak == 10000
        assert newVolume.status.current_usage.size == 12
        assert newVolume.status.current_usage.unit == "TB"
        assert newVolume.application == "MS Access"
        assert newVolume.qos_policy.priority == 6
        assert newVolume.qos_policy.iops_max == 5000
        assert newVolume.qos_policy.iops_min == 3000
        assert newVolume.data_protection_policy.commit_log_retention == 86400
        assert len(newVolume.data_protection_policy.snapshot_policies) == 1
        assert newVolume.tenant.id == 9
        assert newVolume.tenant.name == "UNC"
        assert newVolume.settings.compression == True
        assert newVolume.settings.encryption == True
        assert newVolume.settings.allow_mount == False
        assert newVolume.settings.replica == True

        new_s_policy = newVolume.data_protection_policy.snapshot_policies[0]

        assert new_s_policy.retention_time_in_seconds == 86400
        assert new_s_policy.recurrence_rule.frequency.name == "WEEKLY"
        assert new_s_policy.recurrence_rule.byday == "MO"
        assert new_s_policy.recurrence_rule.byhour == 14
        assert new_s_policy.recurrence_rule.byminute == 45
        
        new_sg = newVolume.safeguard_settings
        assert new_sg.safeguard_type == 'CDM'

    def test_nfs_volume_conversion(self):
        volume = Volume()
        volume.id = 1234
        volume.name = "TestNFSVolume"
        volume.media_policy = "HDD"
        # set NFS settings different than defaults.
        settings = NfsSettings()
        settings.max_object_size = Size(3, "MB")
        settings.use_acls = True
        settings.use_root_squash = True
        settings.synchronous = True
        settings.capacity = Size(2, "TB")
        volume.settings = settings

        j_str = VolumeConverter.to_json(volume)

        newVolume = VolumeConverter.build_volume_from_json(j_str)

        assert newVolume.settings.max_object_size.size == 3
        assert newVolume.settings.max_object_size.unit == "MB"
        assert newVolume.settings.clients == "*"
        assert newVolume.settings.use_acls is True
        assert newVolume.settings.use_root_squash is True
        assert newVolume.settings.synchronous  is True
        assert newVolume.settings.capacity.size == 2
        assert newVolume.settings.capacity.unit == "TB"
        assert newVolume.name == "TestNFSVolume"
        assert newVolume.id == 1234
        assert newVolume.media_policy == "HDD"
        
        new_sg = newVolume.safeguard_settings
        assert new_sg.safeguard_type is None

    def test_user_conversion(self):

        user = User()
        role = "USER"

        tenant = Tenant()
        tenant.name = "TheWorst"
        tenant.id = 2


        user.id = "5abc34"
        user.name = "jdoe"
        user.tenant = tenant
        user.role = role

        j_user = UserConverter.to_json(user)
        print j_user

        new_user = UserConverter.build_user_from_json(j_user)

        assert new_user.id == "5abc34"
        assert new_user.name == "jdoe"
        assert new_user.role == "USER"
        assert new_user.tenant.name == "TheWorst"
        assert new_user.tenant.id == 2

    def test_tenant_conversion(self):

        tenant = Tenant()

        tenant.id = 320
        tenant.name = "HisTenant"

        j_tenant = TenantConverter.to_json(tenant)
        print j_tenant

        new_tenant = TenantConverter.build_tenant_from_json(j_tenant)

        assert new_tenant.name == "HisTenant"
        assert new_tenant.id == 320

    def test_domain_conversion(self):

        domain = Domain()
        domain.site = "boulder"

        domain.id = 5102
        domain.name = "terrible.domain"

        j_domain = DomainConverter.to_json(domain)
        print j_domain

        new_domain = DomainConverter.build_domain_from_json(j_domain)

        assert new_domain.site == "boulder"
        assert new_domain.name == "terrible.domain"
        assert new_domain.id == 5102
        assert new_domain.state == Domain.STATE_UNKNOWN

    def test_service_conversion(self):

        service = Service()

        service.id = "qwerty"
        service.name = "AM"

        service.port = 7004
        service.type = "AM"

        status = ServiceStatus()
        status.state = "LIMITED"
        status.description = "Some fake description"
        status.error_code = 4001

        service.status = status

        j_service = ServiceConverter.to_json(service)
        print j_service

        new_service = ServiceConverter.build_service_from_json(j_service)

        assert new_service.id == "qwerty"
        assert new_service.name == "AM"
        assert new_service.type == "AM"

        new_status = new_service.status

        assert new_status.state == "LIMITED"
        assert new_status.description == "Some fake description"
        assert new_status.error_code == 4001

    def test_named_credential_conversion(self):

        # Mutual exclusion: s3 bucket versus remote volume.
        # First, try s3 bucket.
        s3credentials = S3Credentials()

        s3credentials.access_key_id = "AnAccessIdKey"
        s3credentials.secret_key = "ASecretKey"

        named_credential = NamedCredential()
        named_credential.digest = "aaaabbbb"
        named_credential.name = "goodcredential"
        named_credential.s3credentials = s3credentials
        named_credential.user_id = 42
        named_credential.url = "a/url"
        named_credential.bucketname = "tinpail"

        j_str = NamedCredentialConverter.to_json(named_credential)
        print j_str

        deserialized = NamedCredentialConverter.build_from_json(j_str)
        assert deserialized.digest == "aaaabbbb"
        assert deserialized.name == "goodcredential"
        assert deserialized.user_id == 42
        assert deserialized.url == "a/url"

    def test_node_conversion(self):

        node  = Node()

        address = Address()

        address.ipv4address = "10.12.13.14"
        address.ipv6address = "someweirdaddress"
        node.address = address

        node.id = 928
        node.name = "CoolNode"

        node.state = "DOWN"

        service = Service()

        service.id = 21
        service.name = "DM"

        service.type = "DM"

        s_status = ServiceStatus()
        s_status.description = "Doing very medium"
        s_status.error_code = 201
        s_status.state = "DEGRADED"

        service.status = s_status

        node.services["DM"].append( service )

        j_node = NodeConverter.to_json(node)
        print j_node

        new_node = NodeConverter.build_node_from_json(j_node)

        assert new_node.address.ipv4address == "10.12.13.14"
        assert new_node.address.ipv6address == "someweirdaddress"
        assert new_node.id == 928
        assert new_node.name == "CoolNode"
        assert new_node.state == "DOWN"
        assert len(new_node.services["DM"]) == 1

        new_service = new_node.services["DM"][0]

        assert new_service.status.state == "DEGRADED"
        assert new_service.status.description == "Doing very medium"
        assert new_service.status.error_code == 201
        assert new_service.type == "DM"
        assert new_service.id == 21
        assert new_service.name == "DM"

    def test_repository_conversion(self):

        # Mutual exclusion: s3 bucket versus remote volume.
        # First, try s3 bucket.
        credentials = S3Credentials()

        credentials.access_key_id = "AnAccessIdKey"
        credentials.secret_key = "ASecretKey"

        repository = Repository()
        repository.uuid = "aaaabbbb"
        repository.credentials = credentials
        repository.volume_id = 42
        repository.url = "a/url"
        repository.bucket_name = "tinpail"
        repository.obj_prefix_key = "1/1/name"
        repository.new_volume_name = "newVolumeName"

        # These won't survive the round trip because s3 bucket is present
        repository.remote_om = "https://me:password@hostname:1234"
        repository.remote_volume_name = "volumeName"

        j_repo = RepositoryConverter.to_json(repository)
        print j_repo

        roundtrip_repo = RepositoryConverter.build_repository_from_json(j_repo)

        assert roundtrip_repo.uuid == "aaaabbbb"
        assert roundtrip_repo.credentials.access_key_id == "AnAccessIdKey"
        assert roundtrip_repo.credentials.secret_key == "ASecretKey"
        assert roundtrip_repo.volume_id == 42
        assert roundtrip_repo.url == "a/url"
        assert roundtrip_repo.bucket_name == "tinpail"
        assert roundtrip_repo.remote_om == None
        assert roundtrip_repo.remote_volume_name == None

        # Second, try remote volume
        repository.credentials = None
        repository.bucket_name = None
        repository.remote_om = "https://me:password@hostname:1234"
        repository.remote_volume_name = "volumeName"

        j_repo = RepositoryConverter.to_json(repository)
        print j_repo

        roundtrip_repo = RepositoryConverter.build_repository_from_json(j_repo)
        assert roundtrip_repo.uuid == "aaaabbbb"
        assert roundtrip_repo.volume_id == 42
        assert roundtrip_repo.url == "a/url"
        assert roundtrip_repo.bucket_name == None
        assert roundtrip_repo.remote_om == "https://me:password@hostname:1234"
        assert roundtrip_repo.remote_volume_name == "volumeName"

    def test_safeguard_task_status(self):

        task_status = SafeGuardTaskStatus(uuid=5150, description="task_1", volume_id=42, bucket_name='tinpail', percent_complete=20, endpoint="http://localhost")
        task_status.status = CompletionStatus.running
        task_status.task_type = SafeGuardTaskType.export

        j_str = SafeGuardTaskConverter.to_json_string(task_status)
        print "SafeGuard Task Status"
        print j_str + "\n"

        deserialized = SafeGuardTaskConverter.build_from_json(j_str)
        assert task_status.uuid == 5150
        assert task_status.bucket_name == 'tinpail'
        assert task_status.percent_complete == 20
        assert task_status.endpoint == 'http://localhost'

    def test_subscription_conversion(self):

        subscription = Subscription()
        subscription.digest = "abcdef01"
        subscription.name = "vogue"
        subscription.volume_id = 11
        subscription.creation_time = 149000267
        subscription.remote_volume = "popular_mechanics"
        subscription.named_credential = NamedCredential(digest="fffff02", name="goodcredential")

        j_sub = SubscriptionConverter.to_json(subscription)
        print j_sub

        deserialized = SubscriptionConverter.build_from_json(j_sub)
        assert deserialized.digest == "abcdef01"
        assert deserialized.name == "vogue"
        assert deserialized.volume_id == 11
        assert deserialized.creation_time == 149000267
        assert deserialized.remote_volume == "popular_mechanics"
        assert deserialized.named_credential.digest == "fffff02"

    def test_remote_volume_conversion(self):

        remote_volume = RemoteVolume()

        remote_volume.remote_om_url = "https://me:password@hostname:1234"
        remote_volume.source_volume_name = "sourceVol"
        volume = Volume()
        volume.id = 34
        volume.name = "TestVolume"
        volume.media_policy = "SSD"
        remote_volume.volume = volume

        j_remote_volume = RemoteVolumeConverter.to_json(remote_volume)
        print j_remote_volume

        roundtrip_remote_volume = RemoteVolumeConverter.build_remote_volume_from_json(j_remote_volume)
        assert roundtrip_remote_volume.remote_om_url == "https://me:password@hostname:1234"
        assert roundtrip_remote_volume.source_volume_name == "sourceVol"
        assert roundtrip_remote_volume.volume.id == 34

    def test_exported_volume_conversion(self):

        # Tests object prefix key version 0
        exported_volume = ExportedVolume("7/42/2016-08-03T01:41:14",
            "source_vol",
            "ISCSI",
            4800235841,
            16)

        j_exported_volume = ExportedVolumeConverter.to_json(exported_volume)
        print j_exported_volume

        roundtrip = ExportedVolumeConverter.build_exported_volume_from_json(j_exported_volume)
        assert roundtrip.obj_prefix_key == "7/42/2016-08-03T01:41:14"
        assert roundtrip.source_volume_name == "source_vol"
        assert roundtrip.source_volume_type == "ISCSI"
        assert roundtrip.creation_time == 4800235841
        assert roundtrip.blob_count == 16
        assert roundtrip.source_volume_id == 42
        assert roundtrip.source_snapshot_id == 0
        assert roundtrip.source_domain_id == 7

        # Tests object prefix key version 2 (there is no version 1)
        exported_volume2 = ExportedVolume("2/7/42/216/2016-08-03T01:41:14",
            "source_vol",
            "ISCSI",
            4800235841,
            16)

        j_exported_volume2 = ExportedVolumeConverter.to_json(exported_volume2)
        print j_exported_volume2

        roundtrip2 = ExportedVolumeConverter.build_exported_volume_from_json(j_exported_volume2)
        assert roundtrip2.obj_prefix_key == "2/7/42/216/2016-08-03T01:41:14"
        assert roundtrip2.source_volume_name == "source_vol"
        assert roundtrip2.source_volume_type == "ISCSI"
        assert roundtrip2.creation_time == 4800235841
        assert roundtrip2.blob_count == 16
        assert roundtrip2.source_volume_id == 42
        assert roundtrip2.source_snapshot_id == 216 
        assert roundtrip2.source_domain_id == 7

    def test_safeguard_preset_conversion(self):
        '''Round-trip conversion for ``model.volume.SafeGuardPreset`` object
        '''
        safeguard_preset = SafeGuardPreset(an_id=3, name="safeguard_preset_test")
        safeguard_preset.recurrence_rule.byday = "MO"
        safeguard_preset.recurrence_rule.frequency = "WEEKLY"
        safeguard_preset.recurrence_rule.byhour = 14
        safeguard_preset.recurrence_rule.byminute = 45

        j_str = PresetConverter.safeguard_to_json_string(safeguard_preset)
        print j_str

        # Produces ``model.volume.SafeGuardPreset`` object
        deserialized = PresetConverter.build_safeguard_preset_from_json(j_str)
        assert deserialized.name == "safeguard_preset_test"
        assert deserialized.id == 3
        assert deserialized.recurrence_rule.byday == "MO"
        assert deserialized.recurrence_rule.frequency.name == "WEEKLY"
        assert deserialized.recurrence_rule.byhour == 14
        assert deserialized.recurrence_rule.byminute == 45
        assert deserialized.recurrence_rule.bymonthday == None
        assert deserialized.recurrence_rule.bymonth == None
        assert deserialized.recurrence_rule.byyearday == None

        # The value 'MINUTELY' was added as an allowed frequency in 1.3.2.
        safeguard_preset2 = SafeGuardPreset(an_id=0, name="safeguard_preset_test2")
        safeguard_preset2.recurrence_rule.frequency = "MINUTELY"
        # Test as list
        safeguard_preset2.recurrence_rule.byhour = [0]
        safeguard_preset2.recurrence_rule.byminute = [5]

        j_str2 = PresetConverter.safeguard_to_json_string(safeguard_preset2)
        print j_str2

        # Produces ``model.volume.SafeGuardPreset`` object
        deserialized2 = PresetConverter.build_safeguard_preset_from_json(j_str2)
        assert deserialized2.name == "safeguard_preset_test2"
        assert deserialized2.id == 0
        assert deserialized2.recurrence_rule.frequency.name == "MINUTELY"
        assert deserialized2.recurrence_rule.byday == None
        assert deserialized2.recurrence_rule.byhour == [0]
        assert deserialized2.recurrence_rule.byminute == [5]
        assert deserialized2.recurrence_rule.bymonthday == None
        assert deserialized2.recurrence_rule.bymonth == None
        assert deserialized2.recurrence_rule.byyearday == None

    def test_event_converter_and_source_info(self):
        """
        Roundtrip conversion from ``model.event.event.Event``
        which includes testing of  ``model.event.event.EventContent``, ``model.event.event_source_info.EventSourceInfo``
        and ``model.event.event_descriptor.EventDescriptor``
        """

        s = EventSourceInfo("101", 1, "192.168.1.1", 555, "StorMgr", 103, "SM", "v1", 1, "local", None)
        desc = EventDescriptor("com.formationds.events.model.EventDescriptor",
                               "sm.SOME_KEY", "CRITICAL", ["SYSTEM"], "SOME FORMAT")
        ec = EventContent("com.formationds.events.model.Event", {'seconds': 100, 'nanos': 1000}, desc, s, None)
        e = Event(123, "test.Key", 0, "Event message", "NORMAL", ["CAT1", "CAT2"], ["101"])
        alt_e = Event(e_type="com.formationds.events.model.FormattedEvent", event_content=ec, locale="en_US",
                      event_message="THERE WAS AN EVENT!" )

        # Convert to dict representing the object
        e_d = EventConverter.to_json(e)

        assert 123 == e_d["uuid"]
        assert "test.Key" == e_d["messageKey"]
        assert 0 == e_d["initialTimestamp"]
        assert "Event message" == e_d["defaultMessage"]
        assert "NORMAL" == e_d["severity"]
        assert "CAT1" in e_d["categories"]
        assert "CAT2" in e_d["categories"]
        assert "listArgs" in e_d["messageArgs"]
        assert "101" in e_d["messageArgs"]["listArgs"]

        alt_e_d = EventConverter.to_json(alt_e)
        assert "com.formationds.events.model.FormattedEvent" == alt_e_d["type"]
        assert "en_US" == alt_e_d["locale"]
        assert "THERE WAS AN EVENT!" == alt_e_d["eventMessage"]
        assert ec.e_type == alt_e_d["event"]["type"]
        assert ec.timestamp == alt_e_d["event"]["timestamp"]
        assert ec.attributes == alt_e_d["event"]["attributes"]

        # Also test the sourceInfo stuff
        s_d = EventSourceInfoConverter.to_json(s)
        assert s_d["sourceId"] == "101"
        assert s_d["nodeId"] == 1
        assert s_d["nodeAddress"] == "192.168.1.1"
        assert s_d["pid"] == 555
        assert s_d["processName"] == "StorMgr"
        assert s_d["serviceId"] == 103
        assert s_d["serviceType"] == "SM"
        assert s_d["serviceVersion"] == "v1"
        assert s_d["domainId"] == 1
        assert s_d["domainName"] == "local"
        assert s_d["attributes"] == {}

        # Convert to JSON string
        e_js = EventConverter.to_json_string(e)
        alt_e_js = EventConverter.to_json_string(alt_e)

        # Now convert the string back to an object and make sure they're equal
        e2 = EventConverter.build_from_json(e_js)
        assert e.uuid == e2.uuid
        assert e.message_key == e2.message_key
        assert e.creation_time == e2.creation_time
        assert e.default_message == e2.default_message
        assert e.severity == e2.severity
        assert e.categories == e2.categories
        assert e.message_args == e2.message_args

        alt_e2 = EventConverter.build_from_json(alt_e_js)
        assert alt_e.e_type == alt_e2.e_type
        assert alt_e.event_content.e_type == alt_e2.event_content.e_type
        assert alt_e.event_content.timestamp == alt_e2.event_content.timestamp
        assert alt_e.event_content.descriptor.e_type == alt_e2.event_content.descriptor.e_type
        assert alt_e.event_content.descriptor.severity == alt_e2.event_content.descriptor.severity
        assert alt_e.event_content.descriptor.key == alt_e2.event_content.descriptor.key
        assert alt_e.event_content.descriptor.message_format == alt_e2.event_content.descriptor.message_format
        assert alt_e.event_content.attributes == alt_e2.event_content.attributes

        # Test the sourceInfo stuff too
        assert alt_e.event_content.source_info.source_id == alt_e2.event_content.source_info.source_id
        assert alt_e.event_content.source_info.node_id == alt_e2.event_content.source_info.node_id
        assert alt_e.event_content.source_info.node_address == alt_e2.event_content.source_info.node_address
        assert alt_e.event_content.source_info.pid == alt_e2.event_content.source_info.pid
        assert alt_e.event_content.source_info.process_name == alt_e2.event_content.source_info.process_name
        assert alt_e.event_content.source_info.service_id == alt_e2.event_content.source_info.service_id
        assert alt_e.event_content.source_info.service_type == alt_e2.event_content.source_info.service_type
        assert alt_e.event_content.source_info.service_version == alt_e2.event_content.source_info.service_version
        assert alt_e.event_content.source_info.domain_id == alt_e2.event_content.source_info.domain_id
        assert alt_e.event_content.source_info.domain_name == alt_e2.event_content.source_info.domain_name
        assert alt_e.event_content.source_info.attributes == alt_e2.event_content.source_info.attributes
