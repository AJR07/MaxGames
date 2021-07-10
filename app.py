import json
import discord
from discord.ext import commands
import os
from client import Client

import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

client = Client(command_prefix=["m!"], help_command=None)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('m!help'))
    print("We have logged in as {0.user}".format(client))

with open('config.json', 'r') as file:
    data = json.load(file)
    client.run(data["tokenId"])
    