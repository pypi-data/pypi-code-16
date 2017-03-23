import requests, json
from abc import ABCMeta, abstractmethod

### Constants
SUPPORTEDPLATFORMS = {"generic": "generic", "viber": "viber", "slack": "slack", "facebook": "facebook"}
BONOBOAPIADRESS = "http://api.bonobo.ai/apiv1/addmessage/"
FULL_JSON = "full_json"
PLATFORM = "platform"
TOKEN = "token"
INTENTS_LIST = "intents_list"
DATE_TIME = "date_time"
QS = "qs"
ACCESSTOKEN = "access_token"


class GeneralAPI(ABCMeta('ABC',(object,),{})):
    # General API with standard functions for all the different subclasses

    __bonoboToken = None
    __platform = None

    @abstractmethod
    def __init__(self, platform, bonoboToken):
        self.__platform = platform
        self.__bonoboToken = bonoboToken

    def updateBonoboToken(self, newToken):
        self.__bonoboToken = newToken

    # returns a dictionary with the basic structure needed for bonobo web app
    def getBasicJson(self, dataJson, timeDate, intentsList):
        dataNew = {
            PLATFORM: self.__platform,
            TOKEN: self.__bonoboToken,
            FULL_JSON: dataJson
        }

        dataNew = self.addOptionalParams(dataNew, timeDate, intentsList)
        return dataNew

    # analyzing optional input of intents list (either list or string)
    def __getIntentsList(self, intentsList):
        if type(intentsList) is list:
            return intentsList
        elif intentsList:
            return [intentsList]
        #else:
        #    raise TypeError('intentsList needs to be a List / String')

    def sendToBonoboWithPOSTRequest(self, dataToSend):
        resp = requests.post(BONOBOAPIADRESS,
                             data=json.dumps(dataToSend),
                             headers={"content-type": "application/json"})
        return resp

    def addOptionalParams(self, dataToSend, timeDate, intentsList):
        # adding attributes to the constructed json
        if intentsList is not None:
            intentsList = self.__getIntentsList(intentsList)
            dataToSend[INTENTS_LIST] = intentsList
        if timeDate is not None:
            dataToSend[DATE_TIME] = timeDate
        return dataToSend

    def assertDictInput(self, input):
        if type(input) != type(dict()):
            raise ValueError("The value of the json should be as dictionary type")
        return True

    # getters and setters
    def getPlatform(self):
        return self.__platform

    def getbonoboToken(self):
        return self.__bonoboToken

    def getSendTo(self):
        return BONOBOAPIADRESS

    def setBonoboToken(self, newToken):
        self.__bonoboToken = newToken

    def setbonoboAddress(self, newAddress):
        BONOBOAPIADRESS = newAddress