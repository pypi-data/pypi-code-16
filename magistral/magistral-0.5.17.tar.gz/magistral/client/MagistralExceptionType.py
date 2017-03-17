'''
Created on 10 Aug 2016

@author: rizarse
'''
from enum import Enum

class MagistralExceptionType(Enum):
    
    GeneralError = "MagistralException"
    
    ConnectionPointsError = "Error while receiving connection points"    
    MqttConnectionError = "Error connecting to MQTT"
    RestError = "REST service execution error"
    
    ConversionError = "Conversion error"
    
    HistoryInvocationError = ""
    FetchTopicsError = "Error when fetching topic information"
    
    PermissionFetchError = "Error when fetching user permissions"
    PermissionGrantError = "Error when granting user permissions"
    PermissionRevokationError = "Error when revoking user permissions"
    
    InvalidPubKey = "Invalid publish key"
    InvalidSubKey = "Invalid subscription key"
    InvalidSecretKey = "Invalid secret key"