#!/usr/bin/env python

"""
testing out this discord.py thing
"""

import discord
import time
import asyncio
from discord.ext.commands import Bot

TOKEN = "NDM0MDkxNTI4Mjg2MjQwNzY4.DbFb_w.Jj6Cjm6mgDVIcaz-p6cvt3MuA64"
CLIENT_ID = "434091528286240768"
CLIENT_SECRET = "tnYjVQSOKGSQS8M4WMNJrQ9HJ-ewU61m"
GAME_THREAD_CHANNEL_ID = "434122846646829057"

import discord
import asyncio

client = discord.Client()

async def my_background_task():
    await client.wait_until_ready()
    counter = 0
    channel = discord.Object(id=GAME_THREAD_CHANNEL_ID)
    while not client.is_closed:
        cv = "fuck u <@225731078369837056>"
        counter += 1
        await client.send_message(channel, cv)
        await asyncio.sleep(300) # task runs every 5 minutes

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.loop.create_task(my_background_task())
client.run(TOKEN)
