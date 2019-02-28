# General game info
# Team names, cities, records, etc.

import asyncio
import objectpath

from game_events_parser import GameEventsParser
from linescore_parser import LinescoreParser

class Game:
    def __init__(self, data):
        self.data = data
        self.gameEventsParser = GameEventsParser()
        self.linescoreParser = LinescoreParser()

    def getAbbreviation(self, flag):
        return self.data['teams'][flag]['team']['abbreviation']

    def hasStarted(self):
        return False

    async def update(self):
        live_feed_url = "https://statsapi.mlb.com/api/v1.1/game/{}/feed/live".format(self.data['gamePk'])
        self.live_feed = await self.linescoreParser.getJSONFromURL(live_feed_url)
