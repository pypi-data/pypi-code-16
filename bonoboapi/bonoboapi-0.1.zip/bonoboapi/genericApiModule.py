from .generalApiModule import *

class GenericAPI(object):
    __bonoboToken = None
    __platform = None

    def __init__(self, bonoboToken):
        self.__platform = SUPPORTEDPLATFORMS["generic"]
        self.__bonoboToken = bonoboToken

    def updateBonoboToken(self, newToken):
        self.__bonoboToken = newToken

    # analyzing optional input of intents list (either list or string)
    def __getIntentsList(self, intentsList):
        if type(intentsList) is list:
            return intentsList
        elif intentsList:
            return [intentsList]
        #else:
        #    raise TypeError('intentsList needs to be a List / String')

    def sendDataToBonobo(self, text, channel_id, user_id, platform, who_speaks, date_time=None, intents_list=None):
        # input validation
        if who_speaks != "bot" and who_speaks != "user":
            raise ValueError("'who_speaks' parameter error: ('bot'/'user') MESSAGE WAS NOT SENT")
        # json structure to send
        dataToSend = {
            "id_channel": channel_id,
            "text": text,
            "platform": platform,
            "token": self.__bonoboToken,
            "who_speaks": who_speaks,
            "user_id": user_id
        }
        if intents_list is not None:
            intents_list = self.__getIntentsList(intents_list)
            dataToSend[INTENTS_LIST] = intents_list
        if date_time is not None:
            dataToSend[DATE_TIME] = date_time

        self.sendToBonoboWithPOSTRequest(dataToSend)

    def sendToBonoboWithPOSTRequest(self, dataToSend):
        resp = requests.post(BONOBOAPIADRESS, data=json.dumps(dataToSend), headers={"content-type": "application/json"})
        return resp
