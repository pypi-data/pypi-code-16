# Imports

## parser_core - core parser class
from parser_core import *

## requests - to handle HTTP requests
import requests

# Main clan parser class
class ClanParser(WLParser):
    """
    parser for a clan page

    @PARAMS:
    'clanID' (string or int): ID of targeted clan
    """

    def __init__(self, clanID):
        baseURL = "https://www.warlight.net/Clans/?"
        self.ID = clanID
        self.URL = self.makeURL(baseURL, ID=clanID)

    @property
    @getPageData
    def exists(self):
        """True if the clan exists"""
        nonexistentMarker = ("-->\n\nOops!  That item could not be found.  "
                             "It may have been deleted.")
        return (nonexistentMarker not in self.pageData)

    @property
    @getPageData
    @checkNonexistent
    def name(self):
        """clan name"""
        page = self.pageData
        return self.getValueFromBetween(page, "<title>", " -")

    @property
    @getPageData
    @checkNonexistent
    def size(self):
        """clan member count"""
        page = self.pageData
        marker = "Number of members:</font> "
        return self.getIntegerValue(page, marker)

    @property
    @getPageData
    @checkNonexistent
    def link(self):
        """URL string for clan's designated link"""
        page = self.pageData
        marker = 'Link:</font> <a rel="nofollow" href="'
        end = '">'
        link = self.getValueFromBetween(page, marker, end)
        if link == "http://": return ""
        return link

    @property
    @getPageData
    @checkNonexistent
    def tagline(self):
        """clan tagline"""
        page = self.pageData
        marker = 'Tagline:</font> '
        end = '<br />'
        return self.getValueFromBetween(page, marker, end)

    @property
    @getPageData
    @checkNonexistent
    def createdDate(self):
        """dateteime object representing clan creation date"""
        page = self.pageData
        marker = "Created:</font> "
        end = "<br"
        dateString = self.getValueFromBetween(page, marker, end)
        return self.getDate(dateString)

    @property
    @getPageData
    @checkNonexistent
    def bio(self):
        """clan bio from clan page"""
        page = self.pageData
        marker = "Bio:</font>  "
        end = "<br />"
        return self.getValueFromBetween(page, marker, end)

    @property
    @getPageData
    @checkNonexistent
    def members(self):
        """
        members of the clan in a list of dictionaries
        {'ID' (int), 'name' (string), 'title' (string), 'isMember' (bool)}
        isMember refers to Warlight membership
        """
        page = self.pageData
        marker = '<table class="dataTable">'
        end = '</table>'
        data = list()
        dataRange = self.getValueFromBetween(page, marker, end)
        dataSet = dataRange.split('<tr>')[2:]
        for dataPoint in dataSet:
            isMember = ('/Images/SmallMemberIcon.png"' in dataPoint)
            playerID = self.getIntegerValue(dataPoint, "/Profile?p=")
            playerName = self.getValueFromBetween(dataPoint,
                         '">', '</a>')
            titleRange = dataPoint.split("<td>")[-1]
            playerTitle = self.getValueFromBetween(titleRange, "",
                          "</td")
            data.append({'ID': playerID, 'name': playerName,
                         'title': playerTitle, 'isMember': isMember})
        return data

def getClans():
    """returns a set containing all active clan IDs"""
    URL = "https://www.warlight.net/Clans/List"
    r = requests.get(URL)
    clanSet = set()
    clanData = r.text.split("/Clans/?ID=")[1:]
    for clan in clanData:
        clanID = ""
        while clan[0] in string.digits:
            clanID += clan[0]
            clan = clan[1:]
        clanSet.add(int(clanID))
    return clanSet
