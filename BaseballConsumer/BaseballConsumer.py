'''
BASEBALL GAME THREAD BOT
Originally written by:
/u/DetectiveWoofles
/u/avery_crudeman
Edited for Discord by KimbaWLion
Updated 2019 by analogboy56 and fustrate
Please contact us on Reddit or Github if you have any questions.
'''

from datetime import datetime, timedelta
from game import Game
import time
import json
import logging
import aiohttp
import discord
import random

GAME_THREAD_LOG = r'D:\Users\LaMaster\Downloads\DiscordBaseballBot-master\DiscordBaseballBot-master\BaseballConsumer\logs\game_thread.now'
SETTINGS_FILE = '../settings.json'

class BaseballUpdaterBot:

    def __init__(self):
        self.BOT_TIME_ZONE = None
        self.TEAM_TIME_ZONE = None
        self.TEAM_CODE = None

    def read_settings(self):
        with open(SETTINGS_FILE) as data:
            self.settings = json.load(data)

            self.DISCORD_CLIENT_ID = self.settings.get('DISCORD_CLIENT_ID')
            if self.DISCORD_CLIENT_ID == None: return "Missing DISCORD_CLIENT_ID"

            self.DISCORD_CLIENT_SECRET = self.settings.get('DISCORD_CLIENT_SECRET')
            if self.DISCORD_CLIENT_SECRET == None: return "Missing DISCORD_CLIENT_SECRET"

            self.DISCORD_TOKEN = self.settings.get('DISCORD_TOKEN')
            if self.DISCORD_TOKEN == None: return "Missing DISCORD_TOKEN"

            self.DISCORD_GAME_THREAD_CHANNEL_ID = self.settings.get('DISCORD_GAME_THREAD_CHANNEL_ID')
            if self.DISCORD_GAME_THREAD_CHANNEL_ID == None: return "Missing DISCORD_GAME_THREAD_CHANNEL_ID"

            self.BOT_TIME_ZONE = self.settings.get('BOT_TIME_ZONE')
            if self.BOT_TIME_ZONE == None: return "Missing BOT_TIME_ZONE"

            self.TEAM_TIME_ZONE = self.settings.get('TEAM_TIME_ZONE')
            if self.TEAM_TIME_ZONE == None: return "Missing TEAM_TIME_ZONE"

            self.TEAM_CODE = self.settings.get('TEAM_CODE')
            if self.TEAM_CODE == None: return "Missing TEAM_CODE"

            self.TEAM_ABBREV = self.settings.get('TEAM_ABBREV')
            if self.TEAM_ABBREV == None: return "Missing TEAM_ABBREV"

        return 0

    def getTime(self):
        today = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
        return today

    def formatAtBatLineForLog(self, atbat):
        return "{} {} | B:{} S:{} O:{}; Result: {}; Description: {}".format(
            atbat['topOrBot'], atbat['inning'], atbat['balls'], atbat['strikes'],
            atbat['outs'] ,atbat['result'], atbat['description'])

    def hasPlayerQuip(self, gameEvent):
        if "Mike Trout" in gameEvent['description']: return True
        return False

    def formatPlayerQuips(self, description):
        if "Mike Trout" in description:
            playerQuips = [
                "Fuck Mike Trout",
                "uck-Fay ike_Trout-May"
            ]
            return random.choice(playerQuips)
        return ""

    def formatGameEventForDiscord(self, gameEvent, linescore):
        return "```" \
               "{}\n" \
               "{}{}\n" \
               "```\n" \
               "{}" \
               "{}".format(self.formatLinescoreForDiscord(gameEvent, linescore),
                           self.formatPitchCount(gameEvent['gameEvent'], gameEvent['balls'], gameEvent['strikes']),
                           gameEvent['description'],
                           self.playerismsAndEmoji(gameEvent, linescore),
                           self.endOfInning(gameEvent))

    def formatPlayerChangeForDiscord(self, gameEvent, linescore):
        return "```" \
               "{}\n" \
               "```\n" \
               "{}" \
               "{}".format(gameEvent['description'],
                           self.playerismsAndEmoji(gameEvent, linescore),
                           self.endOfInning(gameEvent))

    def formatLinescoreForDiscord(self, gameEvent, linescore):
        return "{}   ┌───┬──┬──┬──┐\n" \
               "   {}     │{:<3}│{:>2}│{:>2}│{:>2}│\n" \
               "  {} {}    ├───┼──┼──┼──┤\n" \
               "{}   │{:<3}│{:>2}│{:>2}│{:>2}│\n" \
               "         └───┴──┴──┴──┘".format(
            self.formatInning(gameEvent),
            self.formatSecondBase(linescore['status']['runner_on_2b']),
            linescore['away_team_name']['team_abbrev'], linescore['away_team_stats']['team_runs'],
            linescore['away_team_stats']['team_hits'], linescore['away_team_stats']['team_errors'],
            self.formatThirdBase(linescore['status']['runner_on_3b']), self.formatFirstBase(linescore['status']['runner_on_1b']),
            self.formatOuts(gameEvent['outs']),
            linescore['home_team_name']['team_abbrev'], linescore['home_team_stats']['team_runs'],
            linescore['home_team_stats']['team_hits'], linescore['home_team_stats']['team_errors']
        )

    def formatInning(self, gameEvent):
        return "{} {:>2}".format(gameEvent['topOrBot'], gameEvent['inning'])

    def formatOuts(self, outs):
        outOrOuts = " Outs"
        if outs is "1": outOrOuts = "  Out"
        return "".join([outs, outOrOuts])

    def formatFirstBase(self, runnerOnBaseStatus):
        return self.formatBase(runnerOnBaseStatus)

    def formatSecondBase(self, runnerOnBaseStatus):
        return self.formatBase(runnerOnBaseStatus)

    def formatThirdBase(self, runnerOnBaseStatus):
        return self.formatBase(runnerOnBaseStatus)

    def formatBase(self, baseOccupied):
        if baseOccupied:
            return "●"
        return "○"

    def formatPitchCount(self, gameEvent, balls, strikes):
        if gameEvent is 'atbat': return "On a {}-{} count, ".format(balls, strikes)
        elif gameEvent is 'action': return ""
        raise Exception("gameEvent not recognized")

    def endOfInning(self, gameEvent):
        if gameEvent['outs'] is "3": return "```------ End of {} ------```".format(self.formatInning(gameEvent))
        return ""

    def playerismsAndEmoji(self, gameEvent, linescore):
        playerism = ""
        event = gameEvent['event']
        if self.favoriteTeamIsBatting(gameEvent, linescore):
            # Favorite team batting
            if "Home Run" in event and gameEvent['rbi'] != "4": playerism = ''.join([playerism, self.settings.get('EMOTE_HOMERUN'), "\n"])
            if "Home Run" in event and gameEvent['rbi'] == "4": playerism = ''.join([playerism, self.settings.get('EMOTE_GRAND_SLAM'), "\n"])
            if gameEvent['rbi'] is not None:
                for i in range(int(gameEvent['rbi'])):
                    playerism = ''.join([playerism, self.settings.get('EMOTE_RBI'), " "])
            if "Strikeout" in event:
                global otherTeamKTrackerTuple
                if "strikes out" in gameEvent['description']:
                    otherTeamKTrackerTuple = ("".join([otherTeamKTrackerTuple[0], self.settings.get('EMOTE_OTHER_TEAM_STRIKEOUT')]), otherTeamKTrackerTuple[1] + 1, otherTeamKTrackerTuple[2])
                if "called out on strike" in gameEvent['description']:
                    otherTeamKTrackerTuple = ("".join([otherTeamKTrackerTuple[0], self.settings.get('EMOTE_OTHER_TEAM_STRIKEOUT_LOOKING')]), otherTeamKTrackerTuple[1], otherTeamKTrackerTuple[2] + 1)

                if otherTeamKTrackerTuple[1] == 3 and otherTeamKTrackerTuple[2] == 0:
                    playerism = "".join(["Strikeout tracker: 3 ", self.settings.get('EMOTE_OTHER_TEAM_STRIKEOUT'), "s"])
                else:
                    playerism = "".join(["Strikeout tracker: ", otherTeamKTrackerTuple[0]])
        else:
            # Favorite team pitching
            if "Strikeout" in event:
                global favTeamKTrackerTuple
                if "strikes out" in gameEvent['description']:
                    favTeamKTrackerTuple = ("".join([favTeamKTrackerTuple[0], self.settings.get('EMOTE_STRIKEOUT')]), favTeamKTrackerTuple[1] + 1, favTeamKTrackerTuple[2])
                if "called out on strike" in gameEvent['description']:
                    favTeamKTrackerTuple = ("".join([favTeamKTrackerTuple[0], self.settings.get('EMOTE_STRIKEOUT_LOOKING')]), favTeamKTrackerTuple[1], favTeamKTrackerTuple[2] + 1)

                if favTeamKTrackerTuple[1] == 3 and favTeamKTrackerTuple[2] == 0:
                    playerism = "".join(["Strikeout tracker: 3 ", self.settings.get('EMOTE_STRIKEOUT'), "s"])
                else:
                    playerism = "".join(["Strikeout tracker: ", favTeamKTrackerTuple[0]])

            # Opponents batting
            if gameEvent['rbi'] is not None:
                for i in range(int(gameEvent['rbi'])):
                    playerism = ''.join([playerism, self.settings.get('EMOTE_OTHER_TEAM_RBI'), " "])

        playerism = ''.join([playerism, "\n"])
        if self.hasPlayerQuip(gameEvent):
            playerism = "".join([playerism, self.formatPlayerQuips(gameEvent['description'])])
        return playerism

    def favoriteTeamIsBatting(self, gameEvent, linescore):
        return (self.favoriteTeamIsHomeTeam(linescore) and gameEvent['topOrBot'] == "BOT" or not self.favoriteTeamIsHomeTeam(linescore) and gameEvent['topOrBot'] == "TOP")

    def getEventIdsFromLog(self):
        idsFromLog = []
        with open(GAME_THREAD_LOG) as log:
            for line in log:
                splitLine = line.split(" ")
                id = splitLine[2][1:-1]
                idsFromLog.append(id)
        log.close()
        return idsFromLog

    def printToLog(self, atbat, linescore):
        with open(GAME_THREAD_LOG, "a") as log:
            id = atbat['id'] if atbat['id'] is not None else "NoIdInJSONFile"
            log.write("[{}] [{}] | {}\n".format(self.getTime(), id, self.formatAtBatLineForLog(atbat)))
        log.close()
        print("[{}] New atBat: {} {}".format(self.getTime(), self.formatAtBatLineForLog(atbat), self.getLinescoreStatus(linescore)))

    def printGameStatusToLog(self, id, gameStatus):
        with open(GAME_THREAD_LOG, "a") as log:
            log.write("[{}] [{}] | Game Status: {}\n".format(self.getTime(), id, gameStatus))
        log.close()
        print("[{}] Game Status: {}".format(self.getTime(), gameStatus))

    def commentOnDiscord(self, gameEvent, linescore):
        if self.gameUpdateIsPlayerChange(gameEvent):
            comment = self.formatPlayerChangeForDiscord(gameEvent, linescore)
        else:
            comment = self.formatGameEventForDiscord(gameEvent, linescore)
        return comment

    def gameUpdateIsPlayerChange(self, gameEvent):
        isPlayerChange = False
        if 'Pitching Substitution' in gameEvent['event']: isPlayerChange = True
        if 'Defensive Sub' in gameEvent['event']: isPlayerChange = True
        if 'Defensive Switch' in gameEvent['event']: isPlayerChange = True
        if 'Offensive Sub' in gameEvent['event']: isPlayerChange = True
        if 'Game Advisory' in gameEvent['event']: isPlayerChange = True
        return isPlayerChange

    async def run(self, client, channel):
        error_msg = self.read_settings()
        if error_msg != 0:
            print(error_msg)
            return

        # timechecker = timecheck.TimeCheck(time_before)
        #gameEventsParser = GameEventsParser()
        #linescoreParser = LinescoreParser()

        # This list will be what is compared against to see if anything new popped up in the game_events feed
        idsOfPrevEvents = self.getEventIdsFromLog()

        # initialize the globalLinescoreStatus variable
        global globalLinescoreStatus
        globalLinescoreStatus = ("0", "0", False, False, False, "0", "0", "0", "0", "0", "0")
        # initialize favTeamKTrackerTuple variable: string, swinging Ks, looking Ks
        global favTeamKTrackerTuple
        favTeamKTrackerTuple = ("", 0, 0)
        global otherTeamKTrackerTuple
        otherTeamKTrackerTuple = ("", 0, 0)

        response = None
        games = []

        todaysGame = datetime.now() - timedelta(hours=5)
        
        while True:
            if todaysGame.day is not (datetime.now()-timedelta(hours=5)).day:
                todaysGame = datetime.now() - timedelta(hours=5)
                favTeamKTrackerTuple = ("", 0, 0)
                otherTeamKTrackerTuple = ("", 0, 0)
                response = None
                games = []
                globalLinescoreStatus = ("0", "0", False, False, False, "0", "0", "0", "0", "0", "0")
                print("[{}] New Day".format(self.getTime()))

            # Loading new API
            url = "https://statsapi.mlb.com/api/v1/schedule/?sportId=1&teamId=136&date="
            url = url + todaysGame.strftime("%m/%d/%Y")

            while not response:
                # If need this here so bot doesn't get stuck on off days
                if todaysGame.day is not (datetime.now() - timedelta(hours=5)).day:
                    break

                print("[{}] Searching for day's URL...".format(self.getTime()))
                try:
                    # If it returns a 404, try again
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as resp:
                            if resp.status == 200:
                                print("[{}] Found day's URL: {}".format(self.getTime(), url))
                                response = await resp.text()

                                # Place retrieved data into an object for parsing
                                data = json.loads(response)

                                # Load the gamePk and store it in games array. Print that the game was found.
                                for game in data['dates'][0]['games']:
                                    obj = Game(game)
                                    games.append(obj)
                                    print(obj)
                                    print("[{}] Found game PK for team {}: {}".format(self.getTime(),
                                                                                                 self.TEAM_CODE,
                                                                                                 game['gamePk']))
                except:
                    print("[{}] Couldn't find URL \"{}\", trying again...".format(self.getTime(), url))
                    time.sleep(20)
            

            try:
                for game in games:
                    
                    if not game.hasStarted():
                        print("[{}] Game has not started yet".format(self.getTime()))
                        continue
                        
                    
                    # Check if new game event
                    for playByPlay in listOfGameEvents:
                        id = (playByplay['id'] if playByPlay['id'] is not None else "NoIdInJSONFile")
                        if id not in idsOfPrevEvents:
                            if not self.linescoreAndGameEventsInSync(linescore, gameEvent):
                                break
                            self.updateGlobalLinescoreStatus(linescore)
                            self.resetOutsGlobalLinescoreStatus()
                            self.printToLog(gameEvent, linescore)
                            await client.send_message(channel, self.commentOnDiscord(playByPlay, linescore))
                            idsOfPrevEvents = self.getEventIdsFromLog()

                    # Check if game status changed
                    gameStatusTuple = self.checkGameStatus(linescore, idsOfPrevEvents)
                    if gameStatusTuple is not None:
                        await client.send_message(channel, embed=gameStatusTuple[0])
                        await client.send_message(channel, gameStatusTuple[1])

                    # Refresh the eventIds
                    idsOfPrevEvents = self.getEventIdsFromLog()
            except Exception as ex:
                logging.exception("Exception occured")
                #await client.send_message(channel, "Bot encountered an error.  Was there a review on the field?")
            
            time.sleep(10)

        print("/*------------- End of Bot.run() -------------*/")

    def linescoreAndGameEventsInSync(self, linescore, gameEvent):
        if int(gameEvent['inning']) < int(linescore['status']['currentInning']): # if bot posting is behind, let it catch up
            return True
        if self.linescoreStatusHasChanged(linescore):
            return True
        if self.baseStatusChangingGameAction(gameEvent):
            return True
        return False

    def baseStatusChangingGameAction(self, gameEvent):
        actionIsBaseStatusChanging = False
        if 'Stolen Base' in gameEvent['event']: actionIsBaseStatusChanging = True
        if 'Balk' in gameEvent['event']: actionIsBaseStatusChanging = True
        if 'Wild Pitch' in gameEvent['event']: actionIsBaseStatusChanging = True
        if 'Defensive Indiff' in gameEvent['event']: actionIsBaseStatusChanging = True
        if 'Pickoff' in gameEvent['event']: actionIsBaseStatusChanging = True
        if 'Passed Ball' in gameEvent['event']: actionIsBaseStatusChanging = True
        if 'Caught Stealing' in gameEvent['event']: actionIsBaseStatusChanging = True
        if 'Picked off stealing' in gameEvent['event']: actionIsBaseStatusChanging = True
        return gameEvent['gameEvent'] == 'action' and not actionIsBaseStatusChanging

    def linescoreStatusHasChanged(self, linescore):
        global globalLinescoreStatus
        newLinescoreStatus = self.getLinescoreStatus(linescore)
        if globalLinescoreStatus != newLinescoreStatus:
            globalLinescoreStatus = newLinescoreStatus
            return True
        return False

    def getLinescoreStatus(self, linescore):
        # Outs, Base status, runner on 1b, runner on 2b, runner on 3b, Home runs, Home hits, Home errors, Away run, Away hits, Away errors
        return (linescore['status']['outs'], linescore['status']['runnerOnBaseStatus'],
                linescore['status']['runner_on_1b'], linescore['status']['runner_on_2b'], linescore['status']['runner_on_3b'],
                linescore['home_team_stats']['team_runs'], linescore['home_team_stats']['team_hits'], linescore['home_team_stats']['team_errors'],
                linescore['away_team_stats']['team_runs'], linescore['away_team_stats']['team_hits'], linescore['away_team_stats']['team_errors'])

    def updateGlobalLinescoreStatus(self, linescore):
        newLinescoreStatus = self.getLinescoreStatus(linescore)
        global globalLinescoreStatus
        globalLinescoreStatus = newLinescoreStatus

    def resetOutsGlobalLinescoreStatus(self):
        global globalLinescoreStatus
        if globalLinescoreStatus[0] == "3": # Make sure to reset outs to 0 if outs = 3 (NOTE: will be out of sync from file's current linescore status)
            globalLinescoreStatus = ("0", globalLinescoreStatus[1], globalLinescoreStatus[2], globalLinescoreStatus[3],
                                     globalLinescoreStatus[4], globalLinescoreStatus[5], globalLinescoreStatus[6], globalLinescoreStatus[7],
                                     globalLinescoreStatus[8], globalLinescoreStatus[9], globalLinescoreStatus[10])

    def checkGameStatus(self, linescore, idsOfPrevEvents): #rain delay?
        id = linescore['status']['game_status_id']
        gameStatus = linescore['status']['game_status']
        if (gameStatus == "Warmup") and (id not in idsOfPrevEvents):
            self.printGameStatusToLog(id, gameStatus)
            em = self.warmupStatus(linescore)
            return em
        if (gameStatus == "In Progress") and (id not in idsOfPrevEvents):
            self.printGameStatusToLog(id, gameStatus)
            em = self.gameStartedStatus()
            return em
        if (gameStatus == "Delayed") and (id not in idsOfPrevEvents):
            self.printGameStatusToLog(id, gameStatus)
            em = self.gameDelayedStatus()
            return em
        if (gameStatus == "Postponed") and (id not in idsOfPrevEvents):
            self.printGameStatusToLog(id, gameStatus)
            em = self.gamePostponedStatus()
            return em
        if (gameStatus == "Completed Early") and (id not in idsOfPrevEvents):
            self.printGameStatusToLog(id, gameStatus)
            em = self.gameCompletedEarlyStatus()
            return em
        if (gameStatus == "Game Over") and (id not in idsOfPrevEvents):
            self.printGameStatusToLog(id, gameStatus)
            em = self.gameEndedStatus(linescore)
            return em
        return None

    def warmupStatus(self, linescore):
        if linescore['probableStartingPitchers'] is None:
            pregamePost = self.settings.get('WARMUP_BODY_ALTERNATIVE')
        else:
            pregamePost = "{:<3}: {} {} ({}-{} {})\n" \
                          "{:<3}: {} {} ({}-{} {})".format(
                linescore['away_team_name']['team_abbrev'], linescore['probableStartingPitchers']['away_pitcher']['throwinghand'],
                linescore['probableStartingPitchers']['away_pitcher']['name'], linescore['probableStartingPitchers']['away_pitcher']['wins'],
                linescore['probableStartingPitchers']['away_pitcher']['losses'], linescore['probableStartingPitchers']['away_pitcher']['era'],
                linescore['home_team_name']['team_abbrev'], linescore['probableStartingPitchers']['home_pitcher']['throwinghand'],
                linescore['probableStartingPitchers']['home_pitcher']['name'], linescore['probableStartingPitchers']['home_pitcher']['wins'],
                linescore['probableStartingPitchers']['home_pitcher']['losses'], linescore['probableStartingPitchers']['home_pitcher']['era'])
        return (discord.Embed(title=self.settings.get('WARMUP_TITLE'), description=self.settings.get('WARMUP_DESCRIPTION')),
                pregamePost)

    def gameStartedStatus(self): # Start of game post
        return (discord.Embed(title=self.settings.get('GAMESTARTED_TITLE'), description=self.settings.get('GAMESTARTED_DESCRIPTION')), self.settings.get('GAMESTARTED_BODY'))

    def gameDelayedStatus(self):
        em = (discord.Embed(title=self.settings.get('RAINDELAY_TITLE'), description=self.settings.get('RAINDELAY_DESCRIPTION')),
              self.settings.get('RAINDELAY_BODY'))
        return em

    def gamePostponedStatus(self):
        em = (discord.Embed(title=self.settings.get('POSTPONED_TITLE'), description=self.settings.get('POSTPONED_DESCRIPTION')),
              self.settings.get('POSTPONED_BODY'))
        return em

    def gameCompletedEarlyStatus(self):
        em = (discord.Embed(title=self.settings.get('COMPLETEDEARLY_TITLE'), description=self.settings.get('COMPLETEDEARLY_DESCRIPTION')),
              self.settings.get('COMPLETEDEARLY_BODY'))
        return em

    def gameEndedStatus(self, linescore):
        favoriteTeamWLRecord = self.getFavoriteTeamWLRecord(linescore)
        otherTeamWLRecord = self.getOtherTeamWLRecord(linescore)
        if self.isFavoriteTeamWinning(linescore):
            # TCB url 'https://www.youtube.com/watch?v=mmwic9kFx2c'
            title = self.settings.get('GAMEENDED_WIN_TITLE')
            description = '{} ({}-{}) beat the {} ({}-{}) by a score of {}-{}!'.format(
                favoriteTeamWLRecord[0], favoriteTeamWLRecord[1], favoriteTeamWLRecord[2],
                otherTeamWLRecord[0], otherTeamWLRecord[1], otherTeamWLRecord[2],
                linescore['away_team_stats']['team_runs'], linescore['home_team_stats']['team_runs']
            )
            em = (discord.Embed(title=title, description=description),
                  self.settings.get('GAMEENDED_WIN_BODY'))
        else:
            title = self.settings.get('GAMEENDED_LOSS_TITLE')
            description = '{} ({}-{}) were defeated by the {} ({}-{}) by a score of {}-{}'.format(
                favoriteTeamWLRecord[0], favoriteTeamWLRecord[1], favoriteTeamWLRecord[2],
                otherTeamWLRecord[0], otherTeamWLRecord[1], otherTeamWLRecord[2],
                linescore['away_team_stats']['team_runs'], linescore['home_team_stats']['team_runs']
            )
            em = (discord.Embed(title=title, description=description),
                  self.settings.get('GAMEENDED_LOSS_BODY'))
        return em

    def isFavoriteTeamWinning(self, linescore):
        homeTeamRuns = linescore['home_team_stats']['team_runs']
        awayTeamRuns = linescore['away_team_stats']['team_runs']
        favoriteTeamIsHomeTeam = self.favoriteTeamIsHomeTeam(linescore)
        return (favoriteTeamIsHomeTeam and (int(homeTeamRuns) > int(awayTeamRuns))) or \
               (not favoriteTeamIsHomeTeam and (int(homeTeamRuns) < int(awayTeamRuns)))

    def getFavoriteTeamWLRecord(self, linescore):
        return self.getWLRecord(linescore, self.favoriteTeamIsHomeTeam(linescore))

    def getOtherTeamWLRecord(self, linescore):
        return self.getWLRecord(linescore, not self.favoriteTeamIsHomeTeam(linescore))

    def getWLRecord(self, linescore, homeOrAway):
        if homeOrAway:
            return (linescore['home_team_name']['team_name'],
                    linescore['home_team_record']['team_wins'], linescore['home_team_record']['team_losses'])
        else:
            return (linescore['away_team_name']['team_name'],
                    linescore['away_team_record']['team_wins'], linescore['away_team_record']['team_losses'])

    def favoriteTeamIsHomeTeam(self, linescore):
        return linescore['home_team_name']['team_abbrev'] == self.TEAM_ABBREV

if __name__ == '__main__':
    baseballUpdaterBot = BaseballUpdaterBot()
    baseballUpdaterBot.run()

