# General game info
# Team names, cities, records, etc.

from game_events_parser import GameEventsParser
from linescore_parser import LinescoreParser
import asyncio

class Game:
    def __init__(self, data):
        self.data = data
        self.gameEventsParser = GameEventsParser()
        self.linescoreParser = LinescoreParser()

    def getAbbreviation(self, flag):
        #need to retrieve team abbrev here
        return

    def hasStarted(self):
        return false

    async def update(self):
        linescore_url = "https://statsapi.mlb.com/api/v1/game/{}/linescore".format(gamePk)
        self.linescore = await self.linescoreParser.getJSONFromURL(linescore_url)

    
