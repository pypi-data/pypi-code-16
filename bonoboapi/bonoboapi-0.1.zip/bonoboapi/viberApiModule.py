from .generalApiModule import *

class ViberAPI(GeneralAPI):

    __viberToken = None # for QS value
    def __init__(self, bonoboToken, viberToken = ""):
        super(ViberAPI, self).__init__(SUPPORTEDPLATFORMS["viber"], bonoboToken)
        self.__viberToken = viberToken

    def updateViberToken(self, newToken):
        self.__viberToken = newToken

    def addAuthTokenToViberJson(self, dataToSend):
        AT = "auth_token"
        if AT in dataToSend[FULL_JSON] and dataToSend[FULL_JSON][AT] != "":
            self.__viberToken = dataToSend[FULL_JSON][AT]
        dataToSend[FULL_JSON][AT] = self.__viberToken
        return dataToSend

    def sendDataToBonobo(self, jsonData, timeDate=None, intentsList=None):
        super(ViberAPI, self).assertDictInput(jsonData)
        dataToSend = super(ViberAPI, self).getBasicJson(jsonData, timeDate, intentsList)
        dataToSend = self.addAuthTokenToViberJson(dataToSend)
        content = super(ViberAPI, self).sendToBonoboWithPOSTRequest(dataToSend)
        return content
