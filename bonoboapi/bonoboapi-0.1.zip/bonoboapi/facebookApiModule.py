from .generalApiModule import *

class FacebookAPI(GeneralAPI):
    # Sending Facebook chats to bonobo

    __faceToken = None # for QS value
    def __init__(self, bonoboToken, faceToken = ""):
        super(FacebookAPI, self).__init__(SUPPORTEDPLATFORMS["facebook"], bonoboToken)
        self.__faceToken = faceToken

    def updateFaceToken(self, newToken):
        self.__faceToken = newToken

    def __sendUserToBonobo(self, jsonData, timeDate=None, intentsList=None):
        dataToSend = super(FacebookAPI, self).getBasicJson(jsonData, timeDate, intentsList)
        content = super(FacebookAPI, self).sendToBonoboWithPOSTRequest(dataToSend)
        return content

    def __sendBotToBonobo(self, jsonData, timeDate=None, intentsList=None):
        dataToSend = super(FacebookAPI, self).getBasicJson(jsonData, timeDate, intentsList)
        if "json" not in dataToSend[FULL_JSON]:
            dataToSend[FULL_JSON] = {
                "json": jsonData
            }
            dataToSend = super(FacebookAPI, self).addOptionalParams(dataToSend, timeDate, intentsList)
        #add facebook token to json
        if "qs" not in dataToSend[FULL_JSON]:
            dataToSend[FULL_JSON]["qs"] = {
                "access_token": self.__faceToken
            }
        elif ACCESSTOKEN in dataToSend[FULL_JSON][QS] and \
             dataToSend[FULL_JSON][QS][ACCESSTOKEN] != self.__faceToken and\
             dataToSend[FULL_JSON][QS][ACCESSTOKEN] != "":
            self.__faceToken = dataToSend[FULL_JSON][QS][ACCESSTOKEN]

        content = super(FacebookAPI, self).sendToBonoboWithPOSTRequest(dataToSend)
        return content

    def sendDataToBonobo(self, jsonData, timeDate = None, intentsList = None):
        super(FacebookAPI, self).assertDictInput(jsonData)
        if "entry" in jsonData:# 'entry' key implies that the json comes from facebook and json can be sent directly
            return self.__sendUserToBonobo(jsonData, timeDate, intentsList)
        else:
            return self.__sendBotToBonobo(jsonData, timeDate, intentsList)