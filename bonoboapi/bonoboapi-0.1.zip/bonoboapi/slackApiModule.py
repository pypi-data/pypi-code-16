from .generalApiModule import *

class SlackAPI(GeneralAPI):

    __slackToken = None # for token value
    def __init__(self, bonoboToken, slackToken = ""):
        super(SlackAPI, self).__init__(SUPPORTEDPLATFORMS["slack"], bonoboToken)
        self.__slackToken = slackToken

    def updateSlackToken(self, newToken):
        self.__slackToken = newToken

    def sendUserToBonobo(self, jsonData, timeDate=None, intentsList=None):
        super(SlackAPI, self).assertDictInput(jsonData)
        dataToSend = super(SlackAPI, self).getBasicJson(jsonData, timeDate, intentsList)
        content = super(SlackAPI, self).sendToBonoboWithPOSTRequest(dataToSend)
        return content

    def sendBotToBonobo(self, jsonData, timeDate=None, intentsList=None):
        super(SlackAPI, self).assertDictInput(jsonData)

        if "message" not in jsonData:
            jsonData = {
                "message": jsonData
            }
        dataToSend = super(SlackAPI, self).getBasicJson(jsonData, timeDate, intentsList)

        if TOKEN not in dataToSend[FULL_JSON]:
            dataToSend[FULL_JSON][TOKEN] = self.__slackToken
        elif dataToSend[FULL_JSON][TOKEN] != "":
            self.__slackToken = dataToSend[FULL_JSON][TOKEN]

        content = super(SlackAPI, self).sendToBonoboWithPOSTRequest(dataToSend)
        return content