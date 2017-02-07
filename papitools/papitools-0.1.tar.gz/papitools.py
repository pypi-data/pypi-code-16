import json

class PAPIWrapper(object):
    """All basic operations that can be performed using PAPI """

    final_response = "NULL" #This variable holds the SUCCESS or FAILURE reason
    headers = {
        "Content-Type": "application/json"
    }
    access_hostname = "yetToFind"
    property_name = "yetToFind"
    version = "yetToFind"
    notes = "yetToFind"
    emails = "yetToFind"
    groupId = "yetToFind"
    contractId = "yetToFind"
    propertyId = "yetToFind"

    def __init__(self, access_hostname, property_name = "yetToFind", \
                version = "yetToFind",notes = "yetToFind", emails = "yetToFind", \
                groupId = "yetToFind", contractId = "yetToFind", propertyId = "yetToFind"):
        self.access_hostname = access_hostname
        self.property_name = property_name
        self.version = version
        self.notes = notes
        self.emails = emails
        self.groupId = groupId
        self.contractId = contractId
        self.propertyId = propertyId


    def getPropertyInfo(self,session,property_name):
        """
        Function to fetch property ID and update the proerty object with corresponding values

        Parameters
        ----------
        session : session
            An akamai session object
        property_name: property_name
            Property or configuration name

        Returns
        -------
        self : self
            (PAPIWrapper) Object with propertyId, contractId and groupId as attributes
        """

        groupsInfo = self.getGroups(session)
        for eachDataGroup in groupsInfo.json()['groups']['items']:
            try:
                contractId = [eachDataGroup['contractIds'][0]]
                groupId = [eachDataGroup['groupId']]
                url = 'https://' + self.access_hostname + '/papi/v0/properties/?contractId=' + contractId[0] +'&groupId=' + groupId[0]
                propertiesResponse = session.get(url)
                if propertiesResponse.status_code == 200:
                    propertiesResponseJson = propertiesResponse.json()
                    propertiesList = propertiesResponseJson['properties']['items']
                    for propertyInfo in propertiesList:
                        propertyName = propertyInfo['propertyName']
                        propertyId = propertyInfo['propertyId']
                        propertyContractId = propertyInfo['contractId']
                        propertyGroupId = propertyInfo['groupId']
                        if propertyName == property_name or propertyName == property_name + ".xml":
                            #Update the self attributes with correct values
                            self.groupId = propertyGroupId
                            self.contractId = propertyContractId
                            self.propertyId = propertyId
                            self.final_response = "SUCCESS"
                            return self
            except KeyError:
                pass
        #Return the self as it is without updated information
        self.final_response = "FAILURE"
        return self


    def getGroups(self,session):
        """
        Function to fetch all the groups under the contract

        Parameters
        ----------
        session : session
            An akamai session object

        Returns
        -------
        groupResponse : groupResponse
            (groupResponse) Object with all response details.
        """

        groupUrl = 'https://' + self.access_hostname + '/papi/v0/groups/'
        groupResponse = session.get(groupUrl)
        if groupResponse.status_code == 200:
            self.final_response = "SUCCESS"
            return groupResponse
        else:
            self.final_response = "FAILURE"

    def getPropertyRules(self,session,property_name,version):
        """
        Function to download rules from a property

        Parameters
        ----------
        session : session
            An akamai session object
        property_name: property_name
            Property or configuration name
        version : version
            Property orconfiguration version number

        Returns
        -------
        rulesResponse : rulesResponse
            (rulesResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        rulesUrl = 'https://' + self.access_hostname  + '/papi/v0/properties/' + self.propertyId +'/versions/'+str(version)+'/rules/?contractId='+ self.contractId +'&groupId='+ self.groupId
        rulesResponse = session.get(rulesUrl)
        print(json.dumps(rulesResponse.json()))
        if rulesResponse.status_code == 200:
            self.final_response = "SUCCESS"
        else:
            self.final_response = rulesResponse.json()['detail']
        return rulesResponse

    def createVersion(self,session,baseVersion,property_name):
        """
        Function to create or checkout a version of property

        Parameters
        ----------
        session : session
            An akamai session object
        baseVersion : baseVersion
            Property or configuration version number to checkout from
        property_name: property_name
            Property or configuration name

        Returns
        -------
        createVersionResponse : createVersionResponse
            (createVersionResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        newVersionData = """
        {
            "createFromVersion": %s
        }
        """ % (baseVersion)
        createVersionUrl = 'https://' + self.access_hostname + '/papi/v0/properties/' + self.propertyId + '/versions/?contractId=' + self.contractId + '&groupId=' + self.groupId
        createVersionResponse = session.post(createVersionUrl, data=newVersionData,headers=self.headers)
        if createVersionResponse.status_code == 201:
            self.final_response = "SUCCESS"
        return createVersionResponse

    def getVersion(self,session,property_name,activeOn="LATEST"):
        """
        Function to get the latest or staging or production version

        Parameters
        ----------
        session : session
            An akamai session object
        activeOn : activeOn
            Network Type (STAGING OR PRODUCTION) or the LATEST Version
        property_name: property_name
            Property or configuration name

        Returns
        -------
        VersionResponse : VersionResponse
            (VersionResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        if activeOn == "LATEST":
            VersionUrl = 'https://' + self.access_hostname + '/papi/v0/properties/' + self.propertyId + '/versions/latest?contractId=' + self.contractId +'&groupId=' + self.groupId
        elif activeOn == "STAGING":
            VersionUrl = 'https://' + self.access_hostname + '/papi/v0/properties/' + self.propertyId + '/versions/latest?contractId=' + self.contractId +'&groupId=' + self.groupId + '&activatedOn=STAGING'
        elif activeOn == "PRODUCTION":
            VersionUrl = 'https://' + self.access_hostname + '/papi/v0/properties/' + self.propertyId + '/versions/latest?contractId=' + self.contractId +'&groupId=' + self.groupId + '&activatedOn=PRODUCTION'
        VersionResponse = session.get(VersionUrl)
        return VersionResponse

    def uploadRules(self,session,updatedData,property_name,version):
        """
        Function to upload rules to a property

        Parameters
        ----------
        session : session
            An akamai session object
        updatedData : updatedData
            Complete JSON rules dataset to be uploaded
        property_name: property_name
            Property or configuration name

        Returns
        -------
        updateResponse : updateResponse
            (updateResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        updateurl = 'https://' + self.access_hostname  + '/papi/v0/properties/'+ self.propertyId + "/versions/" + str(version) + '/rules/' + '?contractId=' + self.contractId +'&groupId=' + self.groupId
        updatedData = json.dumps(updatedData)
        updateResponse = session.put(updateurl,data=updatedData,headers=self.headers)
        if updateResponse.status_code == 403:
            print("Property cannot be updated due to reasons\n")
            print(updateResponse.json()['detail'])
        elif updateResponse.status_code == 404:
            print("The requested property version is not available")
        elif updateResponse.status_code == 200:
            self.final_response == "SUCCESS"
            print("Bingo.... Property is updated")
        return updateResponse

    def activateConfiguration(self,session,property_name,version,network,emailList,notes):
        """
        Function to activate a configuration or property

        Parameters
        ----------
        session : session
            An akamai session object
        property_name: property_name
            Property or configuration name
        version : version
            version number to be activated
        network : network
            network type on which configuration has to be activated on
        emailList : emailList
            List of emailIds separated by comma to be notified
        notes : notes
            Notes that describes the activation reason

        Returns
        -------
        activationResponse : activationResponse
            (activationResponse) Object with all response details.
        """

        self.getPropertyInfo(session, property_name)
        emails = []
        emails.append(emailList)
        emails = json.dumps(emails)
        activationDetails = """
             {
                "propertyVersion": %s,
                "network": "%s",
                "note": "%s",
                "notifyEmails": %s
            } """ % (version,network,notes,emails)
        
        actUrl  = 'https://' + self.access_hostname + '/papi/v0/properties/'+ self.propertyId + '/activations/?contractId=' + self.contractId +'&groupId=' + self.groupId
        activationResponse = session.post(actUrl, data=activationDetails, headers=self.headers)
        try:
            if activationResponse.status_code == 400 and activationResponse.json()['detail'].find('following activation warnings must be acknowledged'):
                acknowledgeWarnings = []
                print("Following are the WARNINGS...\n")
                for eachWarning in activationResponse.json()['warnings']:
                    print("WARNING: " + eachWarning['detail'])
                    acknowledgeWarnings.append(eachWarning['messageId'])
                    acknowledgeWarningsJson = json.dumps(acknowledgeWarnings)
                print("\nAutomatically acknowledging the warnings.\n")
                #acknowledgeWarnings = json.dumps(acknowledgeWarnings)
                #The details has to be within the three double quote or comment format
                updatedactivationDetails = """
                     {
                        "propertyVersion": %s,
                        "network": "%s",
                        "note": "%s",
                        "notifyEmails": %s,
                        "acknowledgeWarnings": %s
                    } """ % (version,network,notes,emails,acknowledgeWarningsJson)
                print("Please wait while we activate the config for you.. Hold on... \n")
                updatedactivationResponse = session.post(actUrl,data=updatedactivationDetails,headers=self.headers)
                if updatedactivationResponse.status_code == 201:
                    print("Here is the activation link, that can be used to track\n")
                    print(updatedactivationResponse.json()['activationLink'])
                    self.final_response = "SUCCESS"
                else:
                    self.final_response = "FAILURE"
                    print(updatedactivationResponse.json())
                return updatedactivationResponse
            elif activationResponse.status_code == 422 and activationResponse.json()['detail'].find('version already activated'):
                print("Property version already activated")
                self.final_response = "SUCCESS"
            elif activationResponse.status_code == 404 and activationResponse.json()['detail'].find('unable to locate'):
                print("The system was unable to locate the requested version of configuration")
                self.final_response = "FAILURE"
            return activationResponse
        except KeyError:
            self.final_response = "FAILURE"
            print("Looks like there is some error in configuration. Unable to activate configuration at this moment\n")
            return activationResponse
