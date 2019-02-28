import aiohttp
import asyncio
from jsonpatch import JsonPatch

class LiveFeed:
    LIVE_FEED_URL = "https://statsapi.mlb.com/api/v1.1/game/{}/feed/live"
    PATCH_DIFF_URL = "https://statsapi.mlb.com/api/v1.1/game/{}/feed/live/diffPatch?startTimecode={}"

    def __init__(self, gamePk):
        self.gamePk = gamePk
        self.data = {}

    # This will entirely reload the data, if it gets out of date somehow
    async def reload(self):
        url = self.LIVE_FEED_URL.format(self.gamePk)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        self.data = await resp.json()

                    return resp.status == 200
        except:
            return False

    # Perform an update based on the timestamp of the last reload/update
    async def update(self):
        timestamp = self.data['metaData']['timeStamp']
        url = self.PATCH_DIFF_URL.format(self.gamePk, timecode)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        patches = await resp.json()

                        try:
                            self.data = JsonPatch(patches).apply(self.data)
                        except:
                            self.data = {}
                            
                            self.reload()

                    return resp.status == 200
        except:
            return False

    def gameData(self):
        return self.data['gameData']

    def liveData(self):
        return self.data['liveData']
        
    def metaData(self):
        return self.data['metaData']
