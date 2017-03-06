import requests

class APIError(Exception):
    """
    Error class that should simply output errors
    raised by the Warlight API itself
    """
    pass

class ServerGameKeyNotFound(Exception):
    """
    Error class for nonexistent games
    """
    pass

def getAPIToken(email, password):
    """
    Gets API token using email (str) and password (str)
    """
    site = "https://www.warlight.net/API/GetAPIToken"
    data = dict()
    data['Email'] = email
    data['Password'] = password
    r = requests.post(url=site, params=data)
    jsonOutput = r.json()
    if 'error' in jsonOutput:
        raise APIError(jsonOutput['error'])
    return jsonOutput['APIToken']

def makeAPIHandler(email, password):
    """
    Creates an APIHandler object using an
    email (str) and password (str)
    """
    token = getAPIToken(email, password)
    return APIHandler(email, token)

class APIHandler(object):
    """
    Class to handle API calls
    needs an e-mail (str) and token (str);
    can also be created with a password using
    makeAPIHandler
    """

    def __init__(self, email, token):
        self.email = email
        self.token = token

    @staticmethod
    def __canBeTeamless(teams, allowTeamless=True):
        """
        Helper function to determine whether a game can be teamless
        """
        return ((allowTeamless is True) and ([team for team in teams
                if ((isinstance(team, tuple) or isinstance(team, list))
                    and len(team) > 1)] == list()))
        # essentially checks teams for tuples; if no tuples are present,
        # then the game can be played teamlessly

    def __makePlayers(self, teams, allowTeamless=False):
        """
        Given teams, returns a list
        containing player dictionaries

        PARAMETERS:
        teams: list of teams as tuples of player IDs

        OPTIONAL:
        teamless: bool (default False); if set to True,
            a teamless result will be returned if possible
        """
        teamless = self.__canBeTeamless(teams, allowTeamless)
        teamID = 0
        players = list()
        for team in teams:
            if (teamless):
                if (isinstance(team, tuple)):
                    team = team[0]
                player = dict()
                player['token'] = str(team)
                player['team'] = str(None)
                players.append(player)
            elif (isinstance(team, list) or isinstance(team, tuple)):
                for member in team:
                    player = dict()
                    player['token'] = str(member)
                    player['team'] = str(teamID)
                    players.append(player)
            else:
                player = dict()
                player['token'] = str(team)
                player['team'] = str(teamID)
                players.append(player)
            teamID += 1
        return players

    @staticmethod
    def __overrideBonuses(bonuses):
        """
        Given a list containing tuples
        with bonus name and new values,
        generates new list with said data
        in dictionary form
        """
        overridenBonuses = list()
        for bonus in bonuses:
            bonusData = dict()
            bonusData['bonusName'] = bonus[0]
            bonusData['value'] = bonus[1]
            overridenBonuses.append(bonusData)
        return overridenBonuses

    def queryGame(self, gameID, getHistory=False,
                  getSettings=False):
        """
        Queries a game given gameID (str or int)
        using credentials (email+token)
        returns JSON output

        OPTIONAL:
        getHistory (bool, default False):
            whether to retrieve game history

        getSettings (bool, default False):
            whether to retrieve game settings

        OFFICIAL API DOCS:
        https://www.warlight.net/wiki/Query_game_API
        """
        getHistory = str(getHistory).lower()
        getSettings = str(getSettings).lower()
        site = "https://www.warlight.net/API/GameFeed"
        data = dict()
        data['Email'] = self.email
        data['APIToken'] = str(self.token)
        data['GameID'] = str(gameID)
        data['GetHistory'] = getHistory
        data['GetSettings'] = getSettings
        r = requests.post(url=site, params=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            if (isinstance(jsonOutput['error'], str) and
                "ServerGameKeyNotFound" in jsonOutput['error']):
                raise ServerGameKeyNotFound(jsonOutput['error'])
            raise APIError(jsonOutput['error'])
        return jsonOutput

    def createGame(self, template, gameName, teams,
                   settingsDict=None, **settings):
        """
        Creates a game given settings
        using credentials (email+token)
        returns game ID

        PARAMETERS:
        template (int or str): template ID to create game with
        gameName (str): name to give to created game
        teams (list): tuples of player IDs (ints);
            can also just be integers for solo/unteamed players

        OPTIONAL:
        settingsDict: a dictionary for specific game settings
            (similar to settings in queryGame output)
        message: personal message for the game
        teamless (bool, default False): if True, will attempt to
            create the game without any teams
        overridenBonuses (list of tuples): bonuses (name/str) to
            override paired with their new values

        OFFICIAL API DOCS:
        https://www.warlight.net/wiki/Create_game_API
        """
        if settingsDict is None:
            settingsDict = dict()
        site = "https://www.warlight.net/API/CreateGame"
        data = dict()
        data['hostEmail'] = self.email
        data['hostAPIToken'] = str(self.token)
        data['templateID'] = template
        data['gameName'] = gameName
        data['personalMessage'] = settings.get('message', "")
        teamless = settings.get("teamless", False)
        data['players'] = self.__makePlayers(teams, teamless)
        data['settings'] = settingsDict
        if 'overriddenBonuses' in settings:
            data['overriddenBonuses'] = \
            self.__overrideBonuses(settings.get('overriddenBonuses'))
        r = requests.post(url=site, json=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            raise APIError(jsonOutput['error'])
        return jsonOutput['gameID']

    def deleteGame(self, gameID):
        """
        Deletes a game
        using credentials (email+token)
        does not return anything

        PARAMETERS:
        gameID (int or str): game to delete

        OFFICIAL API DOCS:
        https://www.warlight.net/wiki/Delete_game_API
        """
        site = "https://www.warlight.net/API/DeleteLobbyGame"
        data = dict()
        data['Email'] = self.email
        data['APIToken'] = str(self.token)
        data['gameID'] = int(gameID)
        r = requests.post(url=site, json=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            raise APIError(jsonOutput['error'])
        if 'success' not in jsonOutput:
            raise APIError("Unknown error!")

    def getGameIDs(self, *source):
        """
        Gets a list of games for a ladder/tournament
        using credentials (email+token)
        returns list of game IDs

        PARAMETERS:
        *source: source type (str) and ID (int or str)
            e.g. "ladder", 1 or "tournament", 54

        OFFICIAL API DOCS:
        https://www.warlight.net/wiki/Game_ID_feed_API
        """
        site = "https://www.warlight.net/API/GameIDFeed"
        data = dict()
        data['Email'] = self.email
        data['APIToken'] = self.token
        if (len(source) != 2):
            raise TypeError("Need both source type and ID!")
        if ("ladder" in source) or ("Ladder" in source):
            data['LadderID'] = int(source[-1])
        elif ("tournament" in source) or ("Tournament" in source):
            data['TournamentID'] = int(source[-1])
        else:
            raise IOError("Source type must be either ladder or tournament!")
        r = requests.post(url=site, params=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            raise APIError(jsonOutput['error'])
        return jsonOutput['gameIDs']

    def validateToken(self, player, *templates):
        """
        Validates an inviteToken
        using credentials (email+token)
        returns response player object (dictionary)
        containing various data; see API docs for detail

        PARAMETERS
        player (int or str): player token

        OPTIONAL
        *templates (int or str): ID of templates to test
            and determine whether player is able to play on

        OFFICIAL API DOCS:
        https://www.warlight.net/wiki/Validate_invite_token_API
        """
        site = "https://www.warlight.net/API/ValidateInviteToken"
        data = dict()
        data['Email'] = self.email
        data['APIToken'] = self.token
        data['Token'] = player
        if templates is not tuple(): # not empty
            data['TemplateIDs'] = ",".join([str(ID) for ID in templates])
        r = requests.post(url=site, params=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            raise APIError(jsonOutput['error'])
        return jsonOutput

    def setMapDetails(self, mapID, *commands):
        """
        Sets map details
        using credentials (email+token)
        and command setup (commandtype, dict())

        PARAMETERS
        mapID (int or str): ID of map to modify
        *commands (tuples/lists): command-order pairs
            to perform on the map
            orders are dictionaries corresponding to
            attributes relating to the command
            e.g. {'id': 12, 'bonusName': "South America"}
            for an 'addTerritoryToBonus' command

        OFFICIAL API DOCS (for list of commands):
        https://www.warlight.net/wiki/Set_map_details_API
        """
        site = "https://www.warlight.net/API/SetMapDetails"
        data = dict()
        data['email'] = self.email
        data['APIToken'] = self.token
        data['mapID'] = str(mapID)
        commandData = list()
        for command in commands:
            order = dict()
            order['command'] = command[0]
            orders = command[1]
            for item in orders:
                order[item] = orders[item]
            commandData.append(order)
        data['commands'] = commandData
        r = requests.post(url=site, json=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            raise APIError(jsonOutput['error'])
