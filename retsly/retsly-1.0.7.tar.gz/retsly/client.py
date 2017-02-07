from request import Request
from listingRequest import ListingRequest
from officeRequest import OfficeRequest
from agentRequest import AgentRequest
from openHouseRequest import OpenHouseRequest
from assessmentRequest import AssessmentRequest
from transactionRequest import TransactionRequest
from parcelRequest import ParcelRequest
from vendorRequest import VendorRequest

BASE_URL = 'https://rets.io/api/v1'

class Client:
  def __init__(self, token, vendor='test'):
    """
    Construct Retsly client

    Args:
      token (string):         access token
      vendor (string):        vendor ID

    """
    self.token = token
    self.vendor = vendor

  def setVendor(self, vendor):
    """Set the vendor"""
    self.vendor = vendor
    return self

  def listings(self, query=None):
    """Get a listings request"""
    return ListingRequest(self, query)

  def agents(self, query=None):
    """Get an agents request"""
    return AgentRequest(self, query)

  def offices(self, query=None):
    """Get an offices request"""
    return OfficeRequest(self, query)

  def openHouses(self, query=None):
    """Get an openhouses request"""
    return OpenHouseRequest(self, query)

  def assessments(self, query=None):
    """Get an assessments request"""
    return AssessmentRequest(self, query)

  def transactions(self, query=None):
    """Get a transactions request"""
    return TransactionRequest(self, query)

  def parcels(self, query=None):
    """Get a parcels request"""
    return ParcelRequest(self, query)

  def vendors(self, query=None):
    """Get a vendors request"""
    return VendorRequest(self, query)

  def getRequest(self, method, url, query):
    return Request(self, method, url, query)

  def getURL(self, resource):
    if resource == 'vendors':
      return '/'.join([BASE_URL, resource, self.vendor])
    else:
      return '/'.join([BASE_URL, self.vendor, resource])
