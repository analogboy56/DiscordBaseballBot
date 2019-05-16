#!/usr/bin/env python

"""
testing out this discord.py thing
"""

import discord
import time
import asyncio
from discord.ext.commands import Bot
from random import randint
from datetime import datetime

TOKEN = 
CLIENT_ID = 
CLIENT_SECRET = 
GAME_THREAD_CHANNEL_ID = 
POLITICS_CHANNEL_ID = 

import discord
import asyncio

client = discord.Client()

def getTime():
    today = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
    return today
    
async def my_background_task():
    await client.wait_until_ready()
    counter = 0
    channel = discord.Object(id=GAME_THREAD_CHANNEL_ID)
    other_channel = discord.Object(id=POLITICS_CHANNEL_ID)
    while not client.is_closed:
        cv = "fuck u <@225731078369837056>"
        #measure = "GO BERNIE!!!!!! <@424300998425575434>"
        num=(randint(900,21600))
        print("[{}] Next callout in {} minutes".format(getTime(), num/60))
        if num > 17000:
            cv1 = "<@225731078369837056> might actually be alright."
            await client.send_message(channel, cv1)
        else:
            await client.send_message(channel, cv)
        await asyncio.sleep(num) # task randomizes between 15 min - 6 hours

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.loop.create_task(my_background_task())
client.run(TOKEN)
