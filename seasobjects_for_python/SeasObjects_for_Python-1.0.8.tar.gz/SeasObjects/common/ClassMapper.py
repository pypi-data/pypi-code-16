
class ClassMapper(object):

	def __init__(self):
		from SeasObjects.common.RESOURCE import RESOURCE
		from SeasObjects.model.Ability import Ability
		from SeasObjects.model.AbstractEntity import AbstractEntity
		from SeasObjects.model.Activity import Activity
		from SeasObjects.model.Address import Address
		from SeasObjects.model.AliveRequest import AliveRequest
		from SeasObjects.model.AliveResponse import AliveResponse
		from SeasObjects.model.Capacity import Capacity
		from SeasObjects.model.Condition import Condition
		from SeasObjects.model.Controllability import Controllability
		from SeasObjects.model.Coordinates import Coordinates
		from SeasObjects.model.Device import Device
		from SeasObjects.model.Direction import Direction
		from SeasObjects.model.Entity import Entity
		from SeasObjects.model.Error import Error
		from SeasObjects.model.Evaluation import Evaluation
		from SeasObjects.model.Input import Input
		from SeasObjects.model.InterfaceAddress import InterfaceAddress
		from SeasObjects.model.Map import Map
		from SeasObjects.model.Message import Message
		from SeasObjects.model.Notification import Notification
		from SeasObjects.model.Obj import Obj
		from SeasObjects.model.Organization import Organization
		from SeasObjects.model.Orientation import Orientation
		from SeasObjects.model.Output import Output
		from SeasObjects.model.Parameter import Parameter
		from SeasObjects.model.Person import Person
		from SeasObjects.model.PhysicalEntity import PhysicalEntity
		from SeasObjects.model.Provenance import Provenance
		from SeasObjects.model.Request import Request
		from SeasObjects.model.Response import Response
		from SeasObjects.model.Ring import Ring
		from SeasObjects.model.Route import Route
		from SeasObjects.model.Service import Service
		from SeasObjects.model.ServiceProvider import ServiceProvider
		from SeasObjects.model.Size import Size
		from SeasObjects.model.Status import Status
		from SeasObjects.model.SystemOfInterest import SystemOfInterest
		from SeasObjects.model.TemporalContext import TemporalContext
		from SeasObjects.model.TimeSeries import TimeSeries
		from SeasObjects.model.ValueObject import ValueObject
		from SeasObjects.model.Velocity import Velocity
		from SeasObjects.model.Waypoint import Waypoint
		from SeasObjects.model.Waypoints import Waypoints
		from SeasObjects.model.Zone import Zone
		from SeasObjects.model.UnitPriceSpecification import UnitPriceSpecification
		from SeasObjects.model.Enumeration import Enumeration
		from SeasObjects.model.Transaction import Transaction
		from SeasObjects.model.SomeItems import SomeItems
		from SeasObjects.model.Offering import Offering

		
		self.class_map = {
			RESOURCE.GEO_POINT: Coordinates,
			RESOURCE.ABILITY: Ability,
			RESOURCE.ABSTRACTENTITY: AbstractEntity,
			RESOURCE.ACTIVITY: Activity,
			RESOURCE.ADDRESS: Address,
			RESOURCE.ALIVEREQUEST: AliveRequest,
			RESOURCE.ALIVERESPONSE: AliveResponse,
			RESOURCE.CAPACITY: Capacity,
			RESOURCE.CONDITION: Condition,
			RESOURCE.CONTROLLABILITY: Controllability,
			RESOURCE.DEVICE: Device,
			RESOURCE.DIRECTION: Direction,
			RESOURCE.ENTITY: Entity,
			RESOURCE.ERROR: Error,
			RESOURCE.EVALUATION: Evaluation,
			RESOURCE.ENUMERATION: Enumeration,			
			RESOURCE.INPUT: Input,
			RESOURCE.INTERFACEADDRESS: InterfaceAddress,
			RESOURCE.MAP: Map,
			RESOURCE.MESSAGE: Message,
			RESOURCE.NOTIFICATION: Notification,
			RESOURCE.OBJECT: Obj,
			RESOURCE.OFFERING: Offering,
			RESOURCE.ORGANIZATION: Organization,
			RESOURCE.ORIENTATION: Orientation,
			RESOURCE.OUTPUT: Output,
			RESOURCE.PARAMETER: Parameter,
			RESOURCE.PHYSICALENTITY: PhysicalEntity,
			RESOURCE.PERSON: Person,
			RESOURCE.PROVENANCE: Provenance,
			RESOURCE.REQUEST: Request,
			RESOURCE.RESPONSE: Response,
			RESOURCE.RING: Ring,
			RESOURCE.ROUTE: Route,
			RESOURCE.SERVICE: Service,
			RESOURCE.SERVICEPROVIDER: ServiceProvider,
			RESOURCE.SIZE: Size,
			RESOURCE.SOMEITEMS: SomeItems,				
			RESOURCE.STATUS: Status,
			RESOURCE.SYSTEMOFINTEREST: SystemOfInterest,
			RESOURCE.TEMPORALCONTEXT: TemporalContext,
			RESOURCE.TIMESERIES: TimeSeries,
			RESOURCE.TRANSACTION: Transaction,
			RESOURCE.UNITPRICESPECIFICATION: UnitPriceSpecification,
			RESOURCE.VALUEOBJECT: ValueObject,
			RESOURCE.VELOCITY: Velocity,					
	#		RESOURCE.VARIANT: Variant,
			RESOURCE.WAYPOINT: Waypoint,
			RESOURCE.WAYPOINTS: Waypoints,
			RESOURCE.ZONE: Zone
		}	
			
	def getClass(self, typelist, default = None):
		for t in typelist:
			if self.class_map.has_key(t):
				return self.class_map[t]
		
		# No match, return default
		return default
