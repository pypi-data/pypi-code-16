# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#
from fdscli.model.admin.tenant import Tenant
from fdscli.model.admin.user import User
from fdscli.model.common.named_credential import NamedCredential
from fdscli.model.common.s3credentials import S3Credentials
from fdscli.model.common.size import Size
from fdscli.model.fds_error import FdsError
from fdscli.model.health.health_category import HealthCategory
from fdscli.model.health.health_record import HealthRecord
from fdscli.model.health.health_state import HealthState
from fdscli.model.health.system_health import SystemHealth
from fdscli.model.platform.address import Address
from fdscli.model.platform.domain import Domain
from fdscli.model.platform.node import Node
from fdscli.model.platform.service import Service
from fdscli.model.statistics.calculated import Calculated
from fdscli.model.statistics.datapoint import Datapoint
from fdscli.model.statistics.series import Series
from fdscli.model.statistics.statistics import Statistics
from fdscli.model.virtualzones.zone import Zone
from fdscli.model.volume.data_protection_policy_preset import DataProtectionPolicyPreset
from fdscli.model.volume.exported_volume import ExportedVolume
from fdscli.model.volume.qos_preset import QosPreset
from fdscli.model.volume.safeguard_preset import SafeGuardPreset
from fdscli.model.volume.settings.nfs_settings import NfsSettings
from fdscli.model.volume.snapshot import Snapshot
from fdscli.model.volume.snapshot_policy import SnapshotPolicy
from fdscli.model.volume.volume import Volume
from fdscli.utils.converters.platform.node_converter import NodeConverter

'''
Created on Apr 22, 2015

@author: nate
'''

responseOk = dict()
responseOk["status"] = "OK"

response200 = dict()
response200["status"] = 200

def empty_one(one):
    return

def empty_two(one, two):
    return

def empty():
    return

def errorGen( *args ):
    error = FdsError( error="NOOO!" )
    return error

def passwordGetter(prompt):
    return "password"

def writeJson( data ):
    return

def listVolumes():
    volume = Volume(name="FakeVol",an_id=1)
    vols = []

    vols.append( volume )
    
    return vols

def listNoVolumes():
    return []

def getVolume( vid ):
    
    if int(vid) == 3:
        volume = Volume(name="FakeVol", an_id=3)
        return volume
    else:
        return FdsError( "No Volume" )

def getNamedCredentialByKey(key):
    if key == 'fakef1' or key == 'ABCDEF':
        credential = NamedCredential(digest="ABCDEF", user_id=1, name="fakef1")
        credential.url = "https://hannah.reid:secret@localhost:7777"
        credential.protocol = "https"
        credential.username = "hannah.reid"
        credential.password = "secret"
        credential.hostname = "localhost"
        credential.port = 7777
        return credential
    elif key == 'fakes3' or key == '333333':
        credential = NamedCredential(digest="333333", user_id=1, name="fakes3")
        credential.url = "http://localhost"
        credential.s3credentials.access_key_id = 'hr1'
        credential.s3credentials.secret_key = 'secret'
        credential.bucketname = 'tinpail'
        return credential

def getNfsVolume( vid ):
    volume = Volume(name="FakeVol", an_id=3)
    settings = NfsSettings(use_acls=False, use_root_squash=False, synchronous=False, clients="*", max_object_size=None, capacity=Size( 1, "TB" ) )
    volume.settings = settings
    return volume
    
def createVolume(volume):
    return volume

def editVolume(volume):
    return volume

def exportVolume(volume, repository, snapshot_id, credential_digest, safeguard_policy, from_last_export):
    return "{code: 202, description: \'accepted\'}"

def importVolume(volume_name, repository, credential_digest=None):
    volume = Volume(name=volume_name, an_id=3260)
    settings = NfsSettings(use_acls=False, use_root_squash=False, synchronous=False, clients="*", max_object_size=None, capacity=Size( 1, "TB" ) )
    volume.settings = settings
    return volume

def cloneFromTimelineTime( volume, a_time ):
    
    volume.id = 354
    volume.timeline_time = a_time
    return volume

def cloneFromSnapshotId( volume, snapshot_id ):
    volume.id = 789
    return volume

def cloneRemote( remote_volume, snapshot_id, credential_digest, from_last_clone_remote ):
    return "{code: 202, description: \'accepted\'}"

def deleteVolume(name):
    return responseOk

def findVolumeById( an_id ):
    volume = Volume()
    volume.name = "VolumeName"
    volume.id = an_id
    
    return volume

def findVolumeByName( name ):
    volume = Volume()
    volume.name = name
    volume.id = 100
    
    return volume

def findVolumeBySnapId( an_id ):
    volume = Volume()
    volume.name = "SnapVol"
    volume.id = 300
    
    return volume

def createSnapshot( snapshot ):
    
    return snapshot

def listSnapshots( volumeName ):
    snapshot = Snapshot()
    snaps = []
    snaps.append( snapshot )
    return snaps

def listExports( repository, credential_digest=None ):
    '''
    Mock function for listing exported volumes in a bucket.

    Parameters
    ----------
    repository (Repository): Specifies credentials and storage endpoint
    '''
    exports = []

    # A few examples using object prefix key version 0
    exports.append( ExportedVolume(obj_prefix_key="1/2/prefix",
        source_volume_name="sourceVol1",
        blob_count=5) )
    exports.append( ExportedVolume(obj_prefix_key="1/3/prefix",
        source_volume_name="sourceVol2",
        blob_count=26) )
    exports.append( ExportedVolume(obj_prefix_key="1/4/prefix",
        source_volume_name="sourceVol2",
        source_volume_type="ISCSI",
        creation_time=456789013,
        blob_count=26) )

    # An example using object prefix key version 2 (there is no version 1)
    exports.append( ExportedVolume(obj_prefix_key="2/1/4/216/prefix",
        source_volume_name="sourceVol2",
        source_volume_type="ISCSI",
        creation_time=456789013,
        blob_count=26) )

    return exports

def listServices(nodeId):

    services = []
    services.append( Service(a_type="AM",name="AM") )
    services.append( Service(a_type="DM",name="DM") )
    services.append( Service(a_type="PM",name="PM") )
    services.append( Service(a_type="SM",name="SM") )
    
    return services  

def listNodes():
    node = Node()
    node.name = "FakeNode"
    address = Address()
    address.ipv4address = "10.12.14.15"
    address.ipv6address = "Ihavenoidea" 
    node.address = address
    node.id = "21ABC"
    node.state = "UP"
    
    node.services["AM"]  = [Service(a_type="AM",name="AM")]
    node.services["DM"]  = [Service(a_type="DM",name="DM")]
    node.services["PM"]  = [Service(a_type="PM",name="PM")]
    node.services["SM"]  = [Service(a_type="SM",name="SM")]                
 
    nodes = [node]
    return nodes

def listDiscoveredNodes():
    node = Node()
    node.name = "FakeNode"
    address = Address()
    address.ipv4address = "10.12.14.15"
    address.ipv6address = "Ihavenoidea" 
    node.address = address
    node.id = "21ABC"
    node.state = "DISCOVERED"
    
    node.services["AM"]  = [Service(a_type="AM",name="AM")]
    node.services["DM"]  = [Service(a_type="DM",name="DM")]
    node.services["PM"]  = [Service(a_type="PM",name="PM")]
    node.services["SM"]  = [Service(a_type="SM",name="SM")]                
 
    nodes = [node]
    return nodes

def addNode( node_id, state ):
    return response200
    
def removeNode( node_id ):
    return response200

def stopNode( node_id ):
    return response200

def startNode( node_id ):
    return response200

def startService(node_id, service_id):
    return response200

def stopService(node_id, service_id):
    return response200

def removeService(node_id, service_id):
    return response200

def addService(node_id, service):
    return response200

def shutdownDomain( domain_name ):
    return responseOk

def startDomain( domain_name ):
    return responseOk

def listLocalDomains():
    
    domain = Domain()
    domains = []
    domains.append(domain)
    
    return domains

def findDomainById(an_id):
    domain = Domain()
    domain.id = an_id
    domain.name = "MyDomain"
    domain.site = "MySite"
    
    return domain

def createSnapshotPolicy( volume_id, policy ):
    policy.id = 100
    return policy

def editSnapshotPolicy( volume_id, policy ):
    return policy

def listSnapshotPolicies( volume_id=None ):
    policies = []
    policy = SnapshotPolicy()
    policy.id = 900
    policies.append( policy )
    return policies

def getSnapshotPolicy( volumeId, policyId ):
    policy = SnapshotPolicy()
    policy.name = "11_0"
    policy.id = policyId
    policy.volume_id = volumeId
    return policy

def attachPolicy( policy_id, volume_id ):
    return responseOk

def detachPolicy( policy_id, volume_id ):
    return responseOk

def deleteSnapshotPolicy( volume_id, policy_id ):
    return responseOk 

def listTimelinePresets(preset_id=None):
    p = DataProtectionPolicyPreset()
    p.id = 1
    p.policies = [SnapshotPolicy()]
    presets = [p]
    return presets

def listSafeGuardPresets(preset_id=None):
    p = SafeGuardPreset()
    p.id = 1
    presets = [p]
    return presets

def listQosPresets(preset_id=None):
    p = QosPreset()
    p.id = 1
    p.priority = 1
    p.iops_guarantee = 1
    p.iops_limit = 1
    presets = [p]
    return presets

def listUsers(tenant_id=1):
    user = User()
    user.username = "jdoe"
    user.id = 23
    
    return [user]

def createUser(user):
    return user

def listTenants():
    tenant = Tenant()
    tenant.name = "coolness"
    tenant.id = 1
    tenant.users = listUsers()
    return [tenant]

def createTenant(tenant):
    tenant.id = 2
    return tenant

def assignUser(tenant_id, user_id):
    return responseOk

def removeUser(tenant_id, user_id):
    return responseOk

def changePassword(user_id, password):
    return responseOk

def reissueToken(user_id):
    return responseOk

def get_token(user_id):
    d = dict()
    d["token"] = "totallyfaketoken"
    return d

def whoami():
    user = User()
    user.username = "me"
    user.id = 100
    return user

def getSystemHealth():
    health = SystemHealth()
    cap = HealthRecord(state=HealthState.BAD,category=HealthCategory.CAPACITY,message="l_capacity_bad_rate")
    serv = HealthRecord(state=HealthState.GOOD,category=HealthCategory.SERVICES,message="l_services_good")
    fb = HealthRecord(state=HealthState.GOOD,category=HealthCategory.FIREBREAK,message="l_firebreak_good")
    
    health.health_records.append( cap )
    health.health_records.append( serv )
    health.health_records.append( fb )
    
    health.overall_health = HealthState.MARGINAL
    
    return health

def fakeStats( query ):
    
    stats = Statistics()
    series = Series()
    
    series.context = Volume( an_id=1,name="TestVol" )
    series.type = "GETS"
    series.datapoints.append( Datapoint(x=0, y=1) )
    series.datapoints.append( Datapoint(x=20, y=100) )
    
    stats.series_list.append( series )
    
    stats.calculated_values.append( Calculated(key="total", value=3000 ) )
    
    return stats

def mockPostNode( session, url, data=None, callback=None, callback2=None ):
    nodes = listNodes()
    
    if len(nodes) > 0:
        return NodeConverter.to_json(nodes[0])
    
    return ""

def checkVolume( volumeId, fix_flag=None ):
    return

def checkTokens( domainId ):
    return

def fixTokens( domainId ):
    return


def listZones():
    zone = Zone(name="zone1", zid=1)
    zones = []

    zones.append(zone)

    return zones

def listPluginZones(args):
    zone = Zone(name="zone1", zid=1)
    zones = []

    zones.append(zone)

    return zones

def listNoZones():
    return []

def createZone(args):
    zone = Zone(name="zone1", id="1")
    print zone.zid
    print zone.name
    return zone

def getZone(id):
    if int(id) == 1:
        zone = Zone(name="zone1", id=1)
        return zone
    else:
        return FdsError("No zone")

def deleteZone(id):
    return responseOk

def CreateZoneService():
    return responseOk

def listNodesForZone():
    node = Node()
    node.name = "FakeNode"
    node.id = "2"
    node.state = "UP"

    node.services["AM"] = [Service(a_type="AM", name="AM", an_id="2")]
    node.services["DM"] = [Service(a_type="DM", name="DM")]
    node.services["PM"] = [Service(a_type="PM", name="PM")]
    node.services["SM"] = [Service(a_type="SM", name="SM")]

    node2 = Node()
    node2.name = "FakeNode2"
    node2.id = "3"
    node2.state = "UP"

    node2.services["AM"] = [Service(a_type="AM", name="AM", an_id="3")]
    node2.services["DM"] = [Service(a_type="DM", name="DM")]
    node2.services["PM"] = [Service(a_type="PM", name="PM")]
    node2.services["SM"] = [Service(a_type="SM", name="SM")]

    nodes = [node, node2]
    return nodes
