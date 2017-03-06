# Imports

## parser core - mainly the core parser class
from parser_core import *

# LadderParser class
class LadderParser(WLParser):

    """
    class to parse ladders
    @PARAMS:
    'ladderID': integer ID for ladder to parse
    """
    def __init__(self, ladderID):
        baseURL = "https://www.warlight.net/LadderSeason?"
        self.ID = ladderID
        self.URL = self.makeURL(baseURL, ID=ladderID)

    ## existence check
    @property
    @getPageData
    def exists(self):
        """
        error page is result if a ladder doesn't exist
        """
        page = self.pageData
        errorMarker = '<h1>Whoops, an error has occurred</h1>'
        return (errorMarker not in page)

    ## size
    @property
    @checkNonexistent
    @getPageData
    def size(self):
        """
        returns integer amount of teams on ladder
        """
        page = self.pageData
        marker = "<td>There are currently "
        if marker not in page:
            return None
        return self.getIntegerValue(page, marker)

    ## trimUnranked
    @staticmethod
    def trimUnranked(teams):
        """
        given a list of teams, removes unranked teams
        """
        trimmedTeams = [team for team in teams if
                        (len(team) > 0 and team['rank'] != None)]
        return trimmedTeams

    ## getTeams
    @checkNonexistent
    def getTeams(self, rankedOnly=False):
        """
        returns teams from the ladder as a list of dictionaries:
        {'ID', 'rank', 'rank shift', 'rating', 'players'}
        where players is a list of dictionaries:
        {'name', 'clan'}
        where clan is a dictionary:
        {'ID', 'name'} - {None, ""} if no clan

        PARAMS:
        rankedOnly (default False): whether to only return ranked teams
        """
        offset = 0
        stop = False
        allTeams = list()
        while(not stop):
            rankParser = LadderRankingParser(self.ID, offset)
            allTeams += rankParser.getLadderTeams()
            if ((rankParser.isEmpty) or
                (rankedOnly and rankParser.hasUnranked)):
                stop = True
            offset += 50
        if rankedOnly:
            allTeams = self.trimUnranked(allTeams)
        self.allTeams = allTeams
        return allTeams

    ## getHistory
    @checkNonexistent
    def getHistory(self, cutoff=None, returnExpired=False):
        """
        returns game history of a ladder as list of dicts:
        {"ID", 'end date', 'teams', 'finished', 'end date', 'expired'}
        endDate is None if finished is False
        'teams' is a list of dicts of 'ID' and 'won' (bool)

        PARAMS:
        cutoff (datetime object): earliest date cutoff; default None
        returnExpired (bool, default False): whether to return expired games
        """
        offset = 0
        stop = False
        allGames = list()
        while(not stop):
            histParser = LadderHistoryParser(self.ID, offset)
            allGames += histParser.getGameHistory(returnExpired, cutoff)
            if (histParser.isEmpty or
                (cutoff != None and histParser.earliestDate < cutoff) or
                (returnExpired and histParser.hasExpired)):
                stop = True
            offset += 50
        return allGames

    ## getTeamHistory
    @checkNonexistent
    def getTeamHistory(self, teamID, cutoff=None, returnExpired=False):
        """
        returns game history of a ladder team as list of dicts:
        {"ID", 'end date', 'teams', 'finished', 'end date', 'expired'}
        endDate is None if finished is False
        'teams' is a list of dicts of 'ID' and 'won' (bool)

        PARAMS:
        teamID (int): ID of team to examine
        cutoff (datetime object): earliest date cutoff; default None
        returnExpired (bool, default False): whether to return expired games
        """
        offset = 0
        stop = False
        allGames = list()
        while(not stop):
            histParser = LadderTeamHistoryParser(self.ID, teamID, offset)
            allGames += histParser.getGameHistory(returnExpired, cutoff)
            if (histParser.isEmpty or
                (cutoff != None and histParser.earliestDate < cutoff) or
                (returnExpired and histParser.hasExpired)):
                stop = True
            offset += 50
        return allGames

class LadderRankingParser(WLParser):
    """
    ladder ranking parser class
    retrieves a list of teams with rankings, one page at a time
    retrieves up to 50 teams at once
    needs a ladder ID and an offset
    """

    def __init__(self, ladderID, offset):
        baseURL = "https://www.warlight.net/LadderTeams?"
        self.URL = self.makeURL(baseURL, ID=ladderID, Offset=offset)
        self.hasUnranked = False
        self.isEmpty = False

    ## __parsePoint
    def __parsePoint(self, dataPoint):
        """
        parses a single datapoint
        for output documentation, see getLadderTeams
        """
        upArrow = 'img src="/Images/UpArrow.png"'
        downArrow = 'img src="/Images/DownArrow.png"'
        if ("<td>Not Ranked </td>" in dataPoint):
            teamRank = None
        else:
            teamRank = self.getIntegerValue(dataPoint, "<td>")
        rankShift = (dataPoint.count(upArrow) -
                     dataPoint.count(downArrow))
        teamMarker = 'LadderTeam?LadderTeamID='
        teamID = self.getIntegerValue(dataPoint, teamMarker)
        teamIDString = teamMarker + str(teamID)
        players, dataList = list(), dataPoint.split("<a ")
        currentClanID, currentClanName, clanIDMarker = None, "", '"/Clans/?ID='
        clanNameMarker, clanNameEnd = '" title="', '">'
        nameMarker, nameEnd = (teamIDString + '">'), '</a'
        for dataUnit in dataList:
            if clanIDMarker in dataUnit and clanNameMarker in dataUnit:
                currentClanID = self.getIntegerValue(dataUnit, clanIDMarker)
                currentClanName = self.getValueFromBetween(dataUnit,
                                  clanNameMarker, clanNameEnd)
            elif nameMarker in dataUnit and nameEnd in dataUnit:
                playerName = self.getValueFromBetween(dataUnit,
                             nameMarker, nameEnd)
                players.append((playerName,
                               (currentClanID, currentClanName)))
                currentClanID = None
                currentClanName = None
            else: continue # useless unit
        ratingRange = dataPoint.split("<td>")[-1]
        if len(ratingRange) < 1 or (ratingRange[0] not in string.digits):
            teamRating = 0
        else:
            teamRating = self.getIntegerValue(ratingRange, "")
        return {'ID': teamID, 'rank': teamRank, 'rank shift': rankShift,
                'rating': teamRating, 'players': players}

    ## getLadderTeams
    @getPageData
    def getLadderTeams(self):
        """
        returns teams given a page of the ladder
        list of dicts:
        {'ID': int, 'rank': int, 'rank shift': int
        'rating': int, 'players': list}
        where players is a list of dicts:
        {'name', 'clan': {'ID', 'name'}}
        clanID and clanName are None if no clan
        """
        page = self.pageData
        teams = list()
        marker, end = '</thead>', '<table class="LadderTeamsPager">'
        if (marker not in page or end not in page):
            self.isEmpty = True
            return teams
        dataRange = self.getValueFromBetween(page, marker, end)
        if ("<tr >" not in dataRange):
            self.isEmpty = True
            return teams
        dataSet = dataRange.split("<tr >")[1:]
        for dataPoint in dataSet:
            data = self.__parsePoint(dataPoint)
            if data['rank'] == None:
                self.hasUnranked = True
            teams.append(data)
        if (len(teams) == 0): self.isEmpty = True
        return teams

# parser class to fetch history of a ladder, 50 games at a time
class LadderHistoryParser(WLParser):

    ## constructor
    def __init__(self, ladderID, offset):
        """takes a ladder ID and an offset (ideally a multiple of 50)"""
        baseURL = "https://www.warlight.net/LadderGames?"
        self.URL = self.makeURL(baseURL, ID=ladderID, Offset=offset)
        self.earliestDate = None
        self.hasExpired = False
        self.gameMarker = '<tr style="background-color: inherit">'

    ## __parsePoint
    def __parsePoint(self, dataPoint):
        """
        parses a single data point
        see getGameHistory for documentation
        """
        expired = False
        if "(expired)</td>" in dataPoint: expired = True
        multiMarker = 'MultiPlayer?GameID='
        gameID = self.getIntegerValue(dataPoint,
                                      multiMarker)
        gameTime = self.getValueFromBetween(dataPoint,
                   'style="white-space: nowrap">',
                   '</td>')
        if gameTime == "": endDate = None
        else: endDate = self.getDateTime(gameTime)
        if "defeated" in dataPoint:
            alphaData, betaData = dataPoint.split("defeated")
            finished = True
        else:
            alphaData, betaData = dataPoint.split(" vs ")
            finished = False
        alphaTeam = self.getIntegerValue(alphaData,
                    '?LadderTeamID=')
        betaTeam = self.getIntegerValue(betaData,
                    '?LadderTeamID=')
        teams = [{'ID': alphaTeam, 'won': finished},
                 {'ID': betaTeam, 'won': False}] # beta never wins
        return {'ID': gameID, 'teams': teams, 'finished': finished,
                'end date': endDate, 'expired': expired}

    ## getGameHistory
    @getPageData
    def getGameHistory(self, returnExpired=True, earliestDate=None):
        """
        returns game history of a ladder as list of tuples:
        {'ID' (int), 'teams': (list), 'finished': (bool),
        'end date' (datetime object), 'expired': (bool)}
        teams is a list of dictionaries:
        {'ID': (int), 'won': (bool)}
        'won' is False if the game is unfinished
        end date is None if finished is False
        """
        page, games = self.pageData, list()
        marker, end = "</thead>", '<div class="LadderGamesPager'
        if (marker not in page or end not in page):
            self.isEmpty = True
            return games
        dataRange = self.getValueFromBetween(page, marker, end)
        gameMarker = self.gameMarker
        if gameMarker not in dataRange:
            self.isEmpty = True
            return games
        dataSet = dataRange.split(gameMarker)[1:]
        for dataPoint in dataSet:
            data = self.__parsePoint(dataPoint)
            if (data['expired']):
                self.hasExpired = True
                if(not returnExpired):
                    continue
            if (data['end date'] != None):
                if (earliestDate != None and data['end date'] < earliestDate):
                    continue
                if self.earliestDate == None:
                    self.earliestDate = data['end date']
                else:
                    self.earliestDate = min(self.earliestDate, data['end date'])
            games.append(data)
        if (len(games) == 0):
            self.isEmpty = True
        return games

class LadderTeamHistoryParser(LadderHistoryParser):
    """
    parser a page of history for a ladder team
    needs ladderID, teamID, and offset
    """

    def __init__(self, ladderID, teamID, offset):
        baseURL = "https://www.warlight.net/LadderGames?"
        self.URL = self.makeURL(baseURL, ID=ladderID,
                                LadderTeamID=teamID, Offset=offset)
        self.gameMarker = '<tr style="background-color: '
        self.hasExpired = False
        self.earliestDate = None
